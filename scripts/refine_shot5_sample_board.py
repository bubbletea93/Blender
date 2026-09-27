"""Derive the user-sized, stand-free board with brand mark and magnetic samples.

The stitched-board builder calls this with BUILD_FOR_STITCHED=True to prepare
the logo and magnetic materials in memory, without writing an intermediate
asset or review. Standalone execution writes an optional review asset under
renders/. The source geometry and original material palette are preserved.
Background Blender: --factory-startup --disable-autoexec
--background --python scripts/refine_shot5_sample_board.py
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand_collection_palette import PALETTE

BUILD_FOR_STITCHED = bool(globals().get("BUILD_FOR_STITCHED", False))
SOURCE = ROOT / "assets/props/brand_collection_sample_board.blend"
QA = ROOT / "renders/shot5_sample_board_cat_eye"
DEST = QA / "brand_collection_sample_board_cat_eye.blend"
if not BUILD_FOR_STITCHED:
    QA.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene = bpy.context.scene
col = bpy.data.collections["Prop_BrandCollection_SampleBoard"]
col.name = "Prop_BrandCollection_SampleBoard_CatEye"
source_objects = set(col.objects)

def bounds(objects):
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    pts = [ob.evaluated_get(deps).matrix_world @ Vector(p)
           for ob in objects for p in ob.evaluated_get(deps).bound_box]
    return [[min(p[i] for p in pts) for i in range(3)],
            [max(p[i] for p in pts) for i in range(3)]]

original_bounds = bounds(source_objects)
source_nail_transforms = {o.name: [list(row) for row in o.matrix_world]
                          for o in source_objects if "shade_pair_variant" in o}
palette = {name: (base, band) for name, base, band in PALETTE}

def simple_material(name, color, metallic, roughness):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    p = mat.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = roughness
    return mat

gold = simple_material("BOARD_HangPure_GoldMonogram", (.508, .324, .071), .45, .30)
silver = simple_material("BOARD_HangPure_SilverStar", (.53, .55, .55), .30, .35)
black = simple_material("BOARD_HangPure_BlackWordmark", (.008, .007, .007), 0, .55)

def bezier(a, b, c, d, n=18):
    return [tuple((1-t)**3*a[i]+3*(1-t)**2*t*b[i]+3*(1-t)*t*t*c[i]+t**3*d[i]
                  for i in range(2)) for t in [k/n for k in range(1, n+1)]]

def brand_piece(name, coords, material):
    # Reference drawing coordinates are traced as vector contours, not a raster.
    factor = .0188 / 215
    verts = [Vector(((x-341.5)*factor, -.00717, .157+(644-y)*factor)) for x,y in coords]
    lookup = {tuple(v): i for i, v in enumerate(verts)}
    faces = [[v if isinstance(v, int) else lookup[tuple(v)] for v in tri]
             for tri in tessellate_polygon([verts])]
    mesh = bpy.data.meshes.new(name + "_VectorMesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    mesh.materials.append(material)
    obj["source"] = "User-supplied Hang Pure brand mark; clean vector contour geometry"
    return obj

# The gold mark has three separate shapes; the silver star is deliberately separate.
left = [(234,415),(283,415),(283,488)]
left += bezier((283,488),(264,496),(249,508),(234,520))
brand_piece("SampleBoard_HangPure_Monogram_UpperLeft", left, gold)
right = [(400,415)]
right += bezier((400,415),(427,415),(449,437),(449,463))
right += [(449,488),(400,488)]
brand_piece("SampleBoard_HangPure_Monogram_UpperRight", right, gold)
lower = [(234,644),(234,598)]
lower += bezier((234,598),(234,547),(271,505),(318,505))
lower += [(449,505),(449,644),(400,644),(400,554),(309,554)]
lower += bezier((309,554),(294,554),(283,568),(283,590))
lower += [(283,601),(309,601),(283,644)]
brand_piece("SampleBoard_HangPure_Monogram_Base", lower, gold)
star = [(468,343)]
star += bezier((468,343),(471,374),(490,390),(520,396))
star += bezier((520,396),(487,402),(474,420),(468,447))
star += bezier((468,447),(462,418),(445,402),(416,396))
star += bezier((416,396),(446,390),(462,374),(468,343))
brand_piece("SampleBoard_HangPure_SilverStar", star[:-1], silver)

# Keep the original center typography but match the supplied black wordmark.
brand = bpy.data.objects["SampleBoard_Brand"]
brand.location.z = .1465
brand.data.materials.clear()
brand.data.materials.append(black)
bpy.data.objects["SampleBoard_Collection"].location.z = .1378
bpy.data.objects.remove(bpy.data.objects["SampleBoard_CentreHairline"], do_unlink=True)

def magnetic_material(label, base, band, velvet):
    mat = bpy.data.materials.new("BOARD_Magnetic_" + label + ("_Velvet" if velvet else "_CatEye"))
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    n, link = nt.nodes.new, nt.links.new
    def math_node(operation, name, *values):
        node = n("ShaderNodeMath"); node.operation = operation; node.name = name
        for i,value in enumerate(values):
            if isinstance(value, (int,float)): node.inputs[i].default_value = value
            else: link(value, node.inputs[i])
        return node.outputs[0]
    tc = n("ShaderNodeTexCoord"); tc.name = "Object-locked nail coordinates"
    sep = n("ShaderNodeSeparateXYZ"); link(tc.outputs["Generated"], sep.inputs[0])
    x,z = sep.outputs["X"],sep.outputs["Z"]
    # A gently curved magnetic stripe, with opposing slopes in the paired finish.
    diagonal = math_node("MULTIPLY", "Band diagonal", math_node("SUBTRACT", "Centered length", z,.5), -.28 if velvet else .34)
    curve = math_node("MULTIPLY", "Band curvature", math_node("SINE", "Curvature sine", math_node("MULTIPLY", "Curve frequency", z,math.pi*1.55)), .045)
    center = math_node("ADD", "Magnetic center", math_node("ADD", "Offset center", diagonal,.47),curve)
    geo = n("ShaderNodeNewGeometry")
    vt = n("ShaderNodeVectorTransform"); vt.vector_type = "VECTOR"; vt.convert_from = "WORLD"; vt.convert_to = "OBJECT"
    link(geo.outputs["Incoming"], vt.inputs[0])
    view_sep = n("ShaderNodeSeparateXYZ"); link(vt.outputs[0],view_sep.inputs[0])
    shift = math_node("MULTIPLY", "Magnetic parallax", view_sep.outputs["X"], .21)
    center = math_node("ADD", "View-responsive band center", center,shift)
    distance = math_node("SUBTRACT", "Distance to magnetic band",x,center)
    def gaussian(name,width):
        normalized = math_node("DIVIDE",name+" width",distance,width)
        return math_node("EXPONENT",name,math_node("MULTIPLY",name+" exponent",math_node("MULTIPLY",name+" squared",normalized,normalized),-1))
    narrow = gaussian("Focused magnetic line", .125 if velvet else .056)
    halo = gaussian("Magnetic halo", .255 if velvet else .185)
    band_mask = math_node("ADD", "Magnetic band plus halo", math_node("MULTIPLY","Focused line weight",narrow,.67),math_node("MULTIPLY","Soft halo weight",halo,.36))
    # Fine pearlescent pigment is deliberately low contrast and never a bump field
    # of chunky flakes. The cat-eye band remains readable at the final wide framing.
    noise = n("ShaderNodeTexNoise"); noise.name = "Quiet microscopic pigment"
    link(tc.outputs["Generated"],noise.inputs["Vector"])
    noise.inputs["Scale"].default_value=245
    noise.inputs["Detail"].default_value=2
    pigment = math_node("ADD", "Fine pigment modulation", math_node("MULTIPLY","Micro contrast",noise.outputs["Fac"],.14),.91)
    mask = math_node("MULTIPLY","Magnetic pigment response",band_mask,pigment)
    mix=n("ShaderNodeMixRGB");mix.name="Pigment aligned by magnetic field";mix.blend_type="MIX";mix.use_clamp=True
    link(mask,mix.inputs[0])
    mix.inputs[1].default_value=(*(max(.0015,c*.44) for c in base),1)
    # Brightness is reflected metallic pigment, not emission.
    lum=max(band)
    bright=tuple(min(.95,c*1.65+.105*lum+.04) for c in band)
    mix.inputs[2].default_value=(*bright,1)
    p=n("ShaderNodeBsdfPrincipled");p.name="Magnetic lacquer under clear topcoat"
    link(mix.outputs[0],p.inputs["Base Color"])
    p.inputs["Metallic"].default_value=.66
    p.inputs["Roughness"].default_value=.265 if velvet else .225
    p.inputs["Coat Weight"].default_value=.45
    p.inputs["Coat Roughness"].default_value=.13
    p.inputs["Anisotropic"].default_value=.48
    p.inputs["IOR"].default_value=1.49
    bump=n("ShaderNodeBump");bump.name="Subtle pigment relief";bump.inputs["Strength"].default_value=.04;bump.inputs["Distance"].default_value=.00000035
    link(noise.outputs["Fac"],bump.inputs["Height"]);link(bump.outputs["Normal"],p.inputs["Normal"])
    output=n("ShaderNodeOutputMaterial");link(p.outputs["BSDF"],output.inputs["Surface"])
    mat["finish"]="View-responsive magnetic cat-eye band with quiet microscopic pigment"
    mat["base_palette_preserved"]=label
    mat["pair_variant"]="soft velvet" if velvet else "focused cat-eye"
    mat["uses_emission"]=False
    return mat

materials={}
for obj in col.objects:
    if "shade_pair_variant" not in obj: continue
    old_mat=obj.active_material
    label=old_mat.name.removeprefix("BOARD_Lacquer_")
    base,band=palette[label]
    variant=int(obj["shade_pair_variant"])
    key=(label,variant)
    if key not in materials: materials[key]=magnetic_material(label,base,band,bool(variant))
    obj.data.materials.clear();obj.data.materials.append(materials[key])
    obj["magnetic_finish"]="soft velvet" if variant else "focused cat-eye"

col["object_count"]=len(col.objects)
col["branding"]="Hang Pure gold monogram, silver star and black wordmark from user reference"
col["finish_revision"]="Focused magnetic bands and quieter pigment; preserves 36 paired colors"
col["source_user_dimensions_preserved"]=True
col.asset_data.description="User-sized stand-free pearl sample board: 36 paired magnetic cat-eye shades and Hang Pure brand mark. Front -Y."
scene.name="BrandCollection_SampleBoard_CatEye"
final_bounds=bounds(col.objects)
assert max(abs(a-b) for rows in zip(original_bounds,final_bounds) for a,b in zip(*rows)) < .000001
assert len([o for o in col.objects if "shade_pair_variant" in o])==72
assert not any("StandingFoot" in o.name or "RearSpine" in o.name for o in col.objects)
for name,matrix in source_nail_transforms.items():
    assert max(abs(a-b) for rows in zip(matrix,bpy.data.objects[name].matrix_world) for a,b in zip(*rows)) < 1e-8
if not BUILD_FOR_STITCHED:
    report={"source":str(SOURCE),"asset":str(DEST),"collection":col.name,
            "source_objects":len(source_objects),"objects":len(col.objects),"nail_tips":72,"shade_count":36,
            "magnetic_materials":len(materials),"original_bounds":original_bounds,"final_bounds":final_bounds,
            "nail_transforms_unchanged":True,"source_board_geometry_unchanged":True,
            "added_logo_objects":4,"removed_derived_hairline":True,"stand_present":False}
    (QA/"asset_report.json").write_text(json.dumps(report,indent=2))
    bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
    print("CAT_EYE_BOARD_READY",json.dumps(report),flush=True)

    # Review scene is not saved into the reusable asset.
    for obj in list(scene.objects):
        if obj.name not in col.all_objects: bpy.data.objects.remove(obj,do_unlink=True)
    world=bpy.data.worlds.new("CatEyeReviewWorld");world.use_nodes=True
    world.node_tree.nodes["Background"].inputs[0].default_value=(.55,.57,.60,1)
    world.node_tree.nodes["Background"].inputs[1].default_value=.35
    scene.world=world
    bpy.ops.object.camera_add(location=(0,-.65,.151))
    cam=bpy.context.object;cam.name="ReviewCamera";cam.rotation_euler=(Vector((0,0,.151))-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='ORTHO';cam.data.ortho_scale=.32;scene.camera=cam
    for i,(pos,energy,size) in enumerate([((-.20,-.23,.37),13,.18),((.22,-.11,.23),4,.16),((0,.12,.35),7,.12)]):
        bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.name="ReviewLight%d"%i;o.data.energy=energy;o.data.shape='DISK';o.data.size=size
        o.rotation_euler=(Vector((0,0,.151))-o.location).to_track_quat('-Z','Y').to_euler()
    scene.render.engine='CYCLES';scene.cycles.samples=128;scene.cycles.use_denoising=True
    try:
        prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
        for device in prefs.devices:device.use=device.type=='OPTIX'
        scene.cycles.device='GPU'
    except Exception: pass
    scene.view_settings.view_transform='AgX'
    scene.render.resolution_x=1800;scene.render.resolution_y=1500;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.filepath=str(QA/'board_review.png')
    bpy.ops.render.render(write_still=True)
    cam.location=(0,-.65,.161);cam.rotation_euler=(Vector((0,0,.161))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.1
    scene.render.resolution_x=1800;scene.render.resolution_y=1400;scene.render.filepath=str(QA/'logo_and_nails_closeup.png')
    bpy.ops.render.render(write_still=True)
    print('CAT_EYE_BOARD_REVIEW_COMPLETE',flush=True)
