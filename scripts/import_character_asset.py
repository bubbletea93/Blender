"""Turn a licensed character model into a linkable asset under assets/characters/.

Run headless from the repo root:

    blender -b --factory-startup --python scripts/import_character_asset.py -- \
        --source "path/to/model.glb" --name robot_kid \
        --author "Author Name" --license "Commercial licence #1234" \
        --source-url "https://example.com/model"

Produces:
    assets/characters/<name>.blend              Character_<Name> collection, marked as asset
    assets/characters/<name>/source/<original>  untouched copy of the supplied file
    assets/characters/<name>/provenance.json    author / licence / URL / SHA-256
    textures/characters/<name>/                 unpacked textures, referenced relatively

Supported inputs: .glb .gltf .fbx .obj .blend (all objects appended).
Normalisation: object transforms applied, base at Z=0, centred on X/Y.
Optional --height scales to a target height in metres. Rigs are kept;
armature-parented meshes move with the armature.
"""

import argparse
import datetime
import hashlib
import json
import shutil
import sys
from pathlib import Path

import bpy
from mathutils import Vector

REPO = Path(__file__).resolve().parents[1]


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--name", required=True, help="snake_case file stem, e.g. robot_kid")
    p.add_argument("--author", required=True)
    p.add_argument("--license", required=True)
    p.add_argument("--source-url", default="")
    p.add_argument("--height", type=float, default=0.0, help="target height in metres (0 = keep)")
    return p.parse_args(argv)


def collection_name(stem):
    return "Character_" + "".join(part.capitalize() for part in stem.split("_"))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def clear_file():
    for coll in (bpy.data.objects, bpy.data.meshes, bpy.data.materials,
                 bpy.data.cameras, bpy.data.lights, bpy.data.collections):
        for d in list(coll):
            coll.remove(d)


def import_source(src):
    before = set(bpy.data.objects)
    ext = src.suffix.lower()
    if ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=str(src))
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(src))
    elif ext == ".obj":
        bpy.ops.wm.obj_import(filepath=str(src))
    elif ext == ".blend":
        with bpy.data.libraries.load(str(src), link=False) as (data_from, data_to):
            data_to.objects = list(data_from.objects)
        for ob in data_to.objects:
            if ob is not None and ob.type not in {"CAMERA", "LIGHT"}:
                bpy.context.scene.collection.objects.link(ob)
    else:
        raise SystemExit(f"Unsupported format: {ext}")
    return [ob for ob in bpy.data.objects if ob not in before]


def world_bbox(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for ob in objs:
        if ob.type != "MESH":
            continue
        ev = ob.evaluated_get(dg)
        pts += [ev.matrix_world @ Vector(c) for c in ev.bound_box]
    if not pts:
        raise SystemExit("No mesh geometry imported")
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def normalise(objs, target_height):
    roots = [ob for ob in objs if ob.parent is None]
    lo, hi = world_bbox(objs)
    scale = target_height / (hi.z - lo.z) if target_height > 0 else 1.0
    offset = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    for ob in roots:
        ob.location = (ob.location - offset) * scale
        ob.scale *= scale
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objs:
        if ob.type in {"MESH", "ARMATURE", "EMPTY", "CURVE"}:
            ob.select_set(True)
    bpy.context.view_layer.objects.active = roots[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return hi.z - lo.z, scale


def externalise_images(name, blend_path):
    tex_dir = REPO / "textures" / "characters" / name
    for img in bpy.data.images:
        if img.source != "FILE":
            continue
        tex_dir.mkdir(parents=True, exist_ok=True)
        fname = bpy.path.clean_name(img.name)
        ext = "." + (img.file_format.lower().replace("jpeg", "jpg") if img.file_format else "png")
        if not fname.lower().endswith(ext):
            fname += ext
        dst = tex_dir / fname
        if img.packed_file:
            dst.write_bytes(img.packed_file.data)
            img.unpack(method="REMOVE")
        else:
            srcp = Path(bpy.path.abspath(img.filepath))
            if srcp.exists() and srcp.resolve() != dst.resolve():
                shutil.copy2(srcp, dst)
        img.filepath = bpy.path.relpath(str(dst), start=str(blend_path.parent))


def main():
    a = parse_args()
    src = Path(a.source).resolve()
    if not src.exists():
        raise SystemExit(f"Source not found: {src}")

    out_dir = REPO / "assets" / "characters"
    blend_path = out_dir / f"{a.name}.blend"
    meta_dir = out_dir / a.name
    (meta_dir / "source").mkdir(parents=True, exist_ok=True)
    preserved = meta_dir / "source" / src.name
    if src != preserved:
        shutil.copy2(src, preserved)

    clear_file()
    objs = import_source(src)
    orig_height, scale = normalise(objs, a.height)

    coll_name = collection_name(a.name)
    coll = bpy.data.collections.new(coll_name)
    bpy.context.scene.collection.children.link(coll)
    for ob in objs:
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
        coll.objects.link(ob)
    coll.asset_mark()
    coll.asset_data.description = f"{a.name} character asset ({a.license})"
    coll.asset_data.author = a.author

    bpy.context.scene.name = coll_name
    bpy.context.scene.unit_settings.system = "METRIC"

    blend_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), relative_remap=True)
    externalise_images(a.name, blend_path)
    bpy.ops.wm.save_mainfile(relative_remap=True)

    provenance = {
        "title": a.name,
        "author": a.author,
        "license": a.license,
        "source_url": a.source_url,
        "acquisition": "User supplied licensed file",
        "imported": datetime.datetime.now().isoformat(timespec="seconds"),
        "file": src.name,
        "sha256": sha256(preserved),
        "original_download_preserved": True,
        "asset_file": f"assets/characters/{a.name}.blend",
        "collection": coll_name,
        "original_height_m": round(orig_height, 4),
        "applied_scale": round(scale, 6),
        "objects": sorted(ob.name for ob in objs),
    }
    (meta_dir / "provenance.json").write_text(json.dumps(provenance, indent=2))

    for b in out_dir.glob(f"{a.name}.blend[0-9]*"):
        b.unlink()
    print(json.dumps(provenance, indent=2))


main()
