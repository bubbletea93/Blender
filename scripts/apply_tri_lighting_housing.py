import importlib
from types import SimpleNamespace

import bpy


TARGET_OBJECT = "Housing"
TRI_LIGHT_COLLECTION = "TriLighting_Housing"
LEGACY_LIGHTS = {
    "KeyLight": "TriLamp-Key",
    "FillLight": "TriLamp-Fill",
    "RimLight": "TriLamp-Back",
}


def ensure_collection(name):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def remove_existing_tri_lights():
    for name in ("TriLamp-Key", "TriLamp-Fill", "TriLamp-Back"):
        obj = bpy.data.objects.get(name)
        if obj is not None:
            bpy.data.objects.remove(obj, do_unlink=True)


def hide_legacy_lights():
    for name in LEGACY_LIGHTS:
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        obj.hide_viewport = True
        obj.hide_render = True


def copy_light_colors():
    for source_name, target_name in LEGACY_LIGHTS.items():
        source = bpy.data.objects.get(source_name)
        target = bpy.data.objects.get(target_name)
        if source is None or target is None:
            continue
        target.data.color = source.data.color


def build_runner(settings):
    class Runner:
        def report(self, *_args, **_kwargs):
            pass

    runner = Runner()
    for key, value in settings.items():
        setattr(runner, key, value)
    return runner


def main():
    obj = bpy.data.objects.get(TARGET_OBJECT)
    if obj is None:
        raise RuntimeError(f"Missing object: {TARGET_OBJECT}")
    if bpy.context.scene.camera is None:
        raise RuntimeError("Scene has no active camera")

    tri_lighting = importlib.import_module("bl_ext.blender_org.tri_lighting")

    remove_existing_tri_lights()
    hide_legacy_lights()

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    dims = obj.dimensions.copy()
    max_dim = max(dims)
    diagonal = dims.length

    settings = {
        "height": obj.location.z + (dims.z * 1.55),
        "distance": max(diagonal * 2.6, max_dim * 3.5),
        "energy": 18,
        "contrast": 35,
        "leftangle": 26,
        "rightangle": 45,
        "backangle": 235,
        "primarytype": "AREA",
        "secondarytype": "AREA",
        "key_light_shape": "RECTANGLE",
        "secondary_light_shape": "RECTANGLE",
        "key_light_size": max_dim * 1.5,
        "secondary_light_size": max_dim * 1.2,
        "key_light_size_x": max_dim * 1.5,
        "key_light_size_y": max_dim * 2.1,
        "secondary_light_size_x": max_dim * 1.2,
        "secondary_light_size_y": max_dim * 1.8,
        "shadow_soft_size_key": 0.0,
        "shadow_soft_size_fill": 0.0,
        "spot_size_key": 0.7853982,
        "spot_blend_key": 0.15,
        "spot_size_fill": 0.7853982,
        "spot_blend_fill": 0.15,
    }

    context = SimpleNamespace(
        collection=ensure_collection(TRI_LIGHT_COLLECTION),
        scene=bpy.context.scene,
        space_data=SimpleNamespace(type="OTHER", use_local_camera=False),
    )
    runner = build_runner(settings)
    result = tri_lighting.OBJECT_OT_TriLighting.execute(runner, context)
    if result != {"FINISHED"}:
        raise RuntimeError(f"Tri Lighting failed: {result}")

    copy_light_colors()

    print(f"{TARGET_OBJECT} dimensions: {tuple(round(v, 6) for v in dims)}")
    print(
        "Tri Lighting settings:",
        {
            "height": round(settings["height"], 6),
            "distance": round(settings["distance"], 6),
            "energy": settings["energy"],
            "contrast": settings["contrast"],
            "key_size_x": round(settings["key_light_size_x"], 6),
            "key_size_y": round(settings["key_light_size_y"], 6),
            "secondary_size_x": round(settings["secondary_light_size_x"], 6),
            "secondary_size_y": round(settings["secondary_light_size_y"], 6),
        },
    )

    bpy.ops.wm.save_mainfile()


if __name__ == "__main__":
    main()
