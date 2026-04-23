from pathlib import Path

import bpy


OBJECT_NAME = "StudioBackdrop"
MATERIAL_NAME = "StudioBackdrop_Mat"
POLYHAVEN_ASSET = "plaster_grey_04"
TEXTURE_DIR = Path(__file__).resolve().parents[1] / "textures" / "materials" / "polyhaven" / POLYHAVEN_ASSET
TEXTURES = {
    "color": TEXTURE_DIR / "plaster_grey_04_diff_2k.jpg",
    "roughness": TEXTURE_DIR / "plaster_grey_04_rough_2k.jpg",
    "normal": TEXTURE_DIR / "plaster_grey_04_nor_gl_2k.jpg",
}


def require_object(name: str) -> bpy.types.Object:
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise RuntimeError(f"Missing object: {name}")
    return obj


def require_file(path: Path) -> Path:
    if not path.exists():
        raise RuntimeError(f"Missing texture file: {path}")
    return path


def load_image(path: Path, colorspace: str) -> bpy.types.Image:
    image = bpy.data.images.load(str(path), check_existing=True)
    image.filepath = bpy.path.relpath(str(path))
    image.colorspace_settings.name = colorspace
    image.reload()
    return image


def ensure_material(obj: bpy.types.Object) -> bpy.types.Material:
    material = bpy.data.materials.get(MATERIAL_NAME)
    if material is None:
        material = bpy.data.materials.new(MATERIAL_NAME)
    material.use_nodes = True
    material.use_fake_user = True
    if not obj.data.materials:
        obj.data.materials.append(material)
    else:
        obj.data.materials[0] = material
    return material


def set_node_location(node: bpy.types.Node, x: float, y: float) -> None:
    node.location = (x, y)


def build_material(material: bpy.types.Material) -> None:
    color_img = load_image(require_file(TEXTURES["color"]), "sRGB")
    rough_img = load_image(require_file(TEXTURES["roughness"]), "Non-Color")
    normal_img = load_image(require_file(TEXTURES["normal"]), "Non-Color")

    nt = material.node_tree
    nt.nodes.clear()
    nt.links.clear()

    texcoord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    color_tone = nt.nodes.new("ShaderNodeRGB")
    color_mix = nt.nodes.new("ShaderNodeMixRGB")
    color_tex = nt.nodes.new("ShaderNodeTexImage")
    rough_tone = nt.nodes.new("ShaderNodeRGB")
    rough_mix = nt.nodes.new("ShaderNodeMixRGB")
    rough_tex = nt.nodes.new("ShaderNodeTexImage")
    normal_tex = nt.nodes.new("ShaderNodeTexImage")
    normal_map = nt.nodes.new("ShaderNodeNormalMap")
    principled = nt.nodes.new("ShaderNodeBsdfPrincipled")
    output = nt.nodes.new("ShaderNodeOutputMaterial")

    texcoord.name = "BackdropTexCoord"
    mapping.name = "BackdropMapping"
    color_tone.name = "BackdropTone"
    color_mix.name = "BackdropColorMix"
    color_tex.name = "BackdropColor"
    rough_tone.name = "BackdropRoughnessTone"
    rough_mix.name = "BackdropRoughnessMix"
    rough_tex.name = "BackdropRoughness"
    normal_tex.name = "BackdropNormal"
    normal_map.name = "BackdropNormalMap"

    color_tex.image = color_img
    rough_tex.image = rough_img
    normal_tex.image = normal_img

    for image_node in (color_tex, rough_tex, normal_tex):
        image_node.projection = "BOX"
        image_node.projection_blend = 0.2
        image_node.extension = "REPEAT"
        image_node.interpolation = "Cubic"

    mapping.inputs["Scale"].default_value = (0.7, 0.7, 0.7)
    color_tone.outputs["Color"].default_value = (0.18, 0.18, 0.18, 1.0)
    color_mix.blend_type = "MIX"
    color_mix.inputs["Fac"].default_value = 0.14
    rough_tone.outputs["Color"].default_value = (0.85, 0.85, 0.85, 1.0)
    rough_mix.blend_type = "MIX"
    rough_mix.inputs["Fac"].default_value = 0.18
    normal_map.inputs["Strength"].default_value = 0.05

    principled.inputs["Specular IOR Level"].default_value = 0.25

    set_node_location(texcoord, -900, 100)
    set_node_location(mapping, -700, 100)
    set_node_location(color_tone, -650, 350)
    set_node_location(color_tex, -450, 250)
    set_node_location(color_mix, -180, 250)
    set_node_location(rough_tone, -650, 30)
    set_node_location(rough_tex, -450, 30)
    set_node_location(rough_mix, -180, 30)
    set_node_location(normal_tex, -450, -190)
    set_node_location(normal_map, -180, -190)
    set_node_location(principled, 120, 120)
    set_node_location(output, 370, 120)

    links = nt.links
    links.new(texcoord.outputs["Generated"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], color_tex.inputs["Vector"])
    links.new(mapping.outputs["Vector"], rough_tex.inputs["Vector"])
    links.new(mapping.outputs["Vector"], normal_tex.inputs["Vector"])
    links.new(color_tone.outputs["Color"], color_mix.inputs["Color1"])
    links.new(color_tex.outputs["Color"], color_mix.inputs["Color2"])
    links.new(color_mix.outputs["Color"], principled.inputs["Base Color"])
    links.new(rough_tone.outputs["Color"], rough_mix.inputs["Color1"])
    links.new(rough_tex.outputs["Color"], rough_mix.inputs["Color2"])
    links.new(rough_mix.outputs["Color"], principled.inputs["Roughness"])
    links.new(normal_tex.outputs["Color"], normal_map.inputs["Color"])
    links.new(normal_map.outputs["Normal"], principled.inputs["Normal"])
    links.new(principled.outputs["BSDF"], output.inputs["Surface"])


def main() -> None:
    obj = require_object(OBJECT_NAME)
    material = ensure_material(obj)
    build_material(material)

    if bpy.data.filepath:
        bpy.ops.wm.save_mainfile()


if __name__ == "__main__":
    main()
