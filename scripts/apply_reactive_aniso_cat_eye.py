import math

import bpy


TARGET_COLLECTION = "Shot_GelPolishBottle"
TARGET_OBJECT = "CatEye_TestSphere"
COMPARE_OBJECT = "Lacquer_CompareSphere"
BASE_MATERIAL = "Lacquer_Glitter02_Copper"
TARGET_MATERIAL = "Lacquer_CatEye_Reference_Test"
EMPTY_NAME = "CatEye_Mapping_Empty"
GLITTER_GROUP = "Glitter_UVFix"
CAT_EYE_ROTATION_DEGREES = 46.98


def clear_node_tree(node_tree):
    for node in list(node_tree.nodes):
        node_tree.nodes.remove(node)


def ensure_target_sphere():
    obj = bpy.data.objects.get(TARGET_OBJECT)
    if obj is not None:
        return obj

    compare = bpy.data.objects.get(COMPARE_OBJECT)
    if compare is None:
        raise RuntimeError(f"Missing compare sphere object: {COMPARE_OBJECT}")

    collection = bpy.data.collections.get(TARGET_COLLECTION)
    if collection is None:
        raise RuntimeError(f"Missing target collection: {TARGET_COLLECTION}")

    obj = compare.copy()
    obj.data = compare.data.copy()
    obj.name = TARGET_OBJECT
    obj.data.name = f"{TARGET_OBJECT}_Mesh"
    collection.objects.link(obj)
    obj.location = compare.location.copy()
    obj.location.x += max(compare.dimensions.x, 0.02) * 1.35
    obj.rotation_euler = compare.rotation_euler.copy()
    obj.scale = compare.scale.copy()
    obj.hide_viewport = False
    obj.hide_render = False
    obj.show_name = True
    return obj


def hide_old_mapping_empty():
    empty = bpy.data.objects.get(EMPTY_NAME)
    if empty is None:
        return
    empty.hide_viewport = True
    empty.hide_render = True
    empty.show_name = False


def ensure_base_material():
    mat = bpy.data.materials.get(BASE_MATERIAL)
    if mat is None:
        raise RuntimeError(f"Missing base material: {BASE_MATERIAL}")
    mat.use_fake_user = True
    return mat


def build_material():
    ensure_base_material()
    material = bpy.data.materials.get(TARGET_MATERIAL)
    if material is None:
        material = bpy.data.materials.new(TARGET_MATERIAL)
    if not material.use_nodes:
        material.use_nodes = True

    node_tree = material.node_tree
    clear_node_tree(node_tree)
    nodes = node_tree.nodes
    links = node_tree.links

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (1260, 120)

    add_shader = nodes.new("ShaderNodeAddShader")
    add_shader.location = (1040, 120)

    glitter = nodes.new("ShaderNodeGroup")
    glitter.name = "Base Glitter"
    glitter.node_tree = bpy.data.node_groups[GLITTER_GROUP]
    glitter.location = (780, 280)
    glitter.inputs["Glitter Scale"].default_value = 2.2
    glitter.inputs["X Aspect Radio"].default_value = 1.0
    glitter.inputs["Y Aspect Radio"].default_value = 1.0
    glitter.inputs["Global Rotation"].default_value = 0.0
    glitter.inputs["Translate X"].default_value = 0.0
    glitter.inputs["Translate Y"].default_value = 0.0
    glitter.inputs["Bump Strength"].default_value = 0.00015
    glitter.inputs["Thin Film Thickness"].default_value = 90.0
    glitter.inputs["Thin Film IOR"].default_value = 1.33

    texcoord = nodes.new("ShaderNodeTexCoord")
    texcoord.location = (-1900, 40)

    rotation_value = nodes.new("ShaderNodeValue")
    rotation_value.name = "Cat Eye Rotation"
    rotation_value.label = "Cat Eye Rotation (deg)"
    rotation_value.location = (-1900, -140)
    rotation_value.outputs[0].default_value = CAT_EYE_ROTATION_DEGREES

    rotation_to_radians = nodes.new("ShaderNodeMath")
    rotation_to_radians.name = "Rotation To Radians"
    rotation_to_radians.operation = "MULTIPLY"
    rotation_to_radians.location = (-1670, -140)
    rotation_to_radians.inputs[1].default_value = math.pi / 180.0

    rotation_vector = nodes.new("ShaderNodeCombineXYZ")
    rotation_vector.name = "Rotation Vector"
    rotation_vector.location = (-1670, 40)

    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-1440, 40)
    mapping.inputs["Scale"].default_value = (2.2, 1.0, 1.0)

    gradient = nodes.new("ShaderNodeTexGradient")
    gradient.gradient_type = "LINEAR"
    gradient.location = (-1430, 160)

    band_ramp = nodes.new("ShaderNodeValToRGB")
    band_ramp.name = "Soft Band Ramp"
    band_ramp.location = (-1180, 160)
    band_ramp.color_ramp.interpolation = "EASE"
    band_ramp.color_ramp.elements[0].position = 0.24
    band_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    band_ramp.color_ramp.elements[1].position = 0.78
    band_ramp.color_ramp.elements[1].color = (0.0, 0.0, 0.0, 1.0)
    shoulder_a = band_ramp.color_ramp.elements.new(0.39)
    shoulder_a.color = (0.24, 0.24, 0.24, 1.0)
    core = band_ramp.color_ramp.elements.new(0.53)
    core.color = (0.74, 0.74, 0.74, 1.0)
    shoulder_b = band_ramp.color_ramp.elements.new(0.67)
    shoulder_b.color = (0.22, 0.22, 0.22, 1.0)

    wave = nodes.new("ShaderNodeTexWave")
    wave.location = (-1430, -120)
    wave.wave_type = "BANDS"
    wave.bands_direction = "X"
    wave.inputs["Scale"].default_value = 32.0
    wave.inputs["Distortion"].default_value = 2.0
    wave.inputs["Detail"].default_value = 5.0
    wave.inputs["Detail Scale"].default_value = 1.2
    wave.inputs["Detail Roughness"].default_value = 0.4

    wave_ramp = nodes.new("ShaderNodeValToRGB")
    wave_ramp.name = "Directional Streaks"
    wave_ramp.location = (-1180, -120)
    wave_ramp.color_ramp.interpolation = "LINEAR"
    wave_ramp.color_ramp.elements[0].position = 0.33
    wave_ramp.color_ramp.elements[0].color = (0.45, 0.45, 0.45, 1.0)
    wave_ramp.color_ramp.elements[1].position = 0.74
    wave_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)

    band_bw = nodes.new("ShaderNodeRGBToBW")
    band_bw.location = (-960, 160)

    wave_bw = nodes.new("ShaderNodeRGBToBW")
    wave_bw.location = (-960, -120)

    band_streaks = nodes.new("ShaderNodeMath")
    band_streaks.operation = "MULTIPLY"
    band_streaks.location = (-720, 40)

    band_soften = nodes.new("ShaderNodeMath")
    band_soften.operation = "MULTIPLY_ADD"
    band_soften.location = (-500, 40)
    band_soften.inputs[1].default_value = 0.60
    band_soften.inputs[2].default_value = 0.06

    band_clamp = nodes.new("ShaderNodeClamp")
    band_clamp.location = (-280, 40)

    tangent_local = nodes.new("ShaderNodeCombineXYZ")
    tangent_local.location = (-1680, -520)
    tangent_local.inputs["X"].default_value = 0.0
    tangent_local.inputs["Y"].default_value = 1.0
    tangent_local.inputs["Z"].default_value = -1.0

    tangent_norm = nodes.new("ShaderNodeVectorMath")
    tangent_norm.operation = "NORMALIZE"
    tangent_norm.location = (-1450, -520)

    tangent_to_world = nodes.new("ShaderNodeVectorTransform")
    tangent_to_world.vector_type = "VECTOR"
    tangent_to_world.convert_from = "OBJECT"
    tangent_to_world.convert_to = "WORLD"
    tangent_to_world.location = (-1220, -520)

    aniso = nodes.new("ShaderNodeBsdfAnisotropic")
    aniso.location = (780, -40)
    aniso.inputs["Color"].default_value = (0.82, 0.40, 0.20, 1.0)
    aniso.inputs["Roughness"].default_value = 0.32
    aniso.inputs["Anisotropy"].default_value = 0.84
    aniso.inputs["Rotation"].default_value = 0.0

    aniso_weight = nodes.new("ShaderNodeMath")
    aniso_weight.operation = "MULTIPLY"
    aniso_weight.location = (0, -220)
    aniso_weight.inputs[1].default_value = 0.08

    color_mix_1 = nodes.new("ShaderNodeMix")
    color_mix_1.data_type = "RGBA"
    color_mix_1.blend_type = "MIX"
    color_mix_1.location = (0, 260)

    color_mix_2 = nodes.new("ShaderNodeMix")
    color_mix_2.data_type = "RGBA"
    color_mix_2.blend_type = "MIX"
    color_mix_2.location = (0, 80)

    color_1_base = nodes.new("ShaderNodeRGB")
    color_1_base.location = (-220, 360)
    color_1_base.outputs[0].default_value = (0.64, 0.19, 0.09, 1.0)

    color_1_band = nodes.new("ShaderNodeRGB")
    color_1_band.location = (-220, 220)
    color_1_band.outputs[0].default_value = (0.82, 0.44, 0.24, 1.0)

    color_2_base = nodes.new("ShaderNodeRGB")
    color_2_base.location = (-220, 160)
    color_2_base.outputs[0].default_value = (0.04, 0.007, 0.005, 1.0)

    color_2_band = nodes.new("ShaderNodeRGB")
    color_2_band.location = (-220, 20)
    color_2_band.outputs[0].default_value = (0.24, 0.07, 0.035, 1.0)

    rough_mix = nodes.new("ShaderNodeMath")
    rough_mix.operation = "MULTIPLY_ADD"
    rough_mix.location = (240, -40)
    rough_mix.inputs[1].default_value = -0.08
    rough_mix.inputs[2].default_value = 0.18

    metallic_mix = nodes.new("ShaderNodeMath")
    metallic_mix.operation = "MULTIPLY_ADD"
    metallic_mix.location = (240, -220)
    metallic_mix.inputs[1].default_value = 0.08
    metallic_mix.inputs[2].default_value = 0.42

    clamp_rough = nodes.new("ShaderNodeClamp")
    clamp_rough.location = (470, -40)

    clamp_metal = nodes.new("ShaderNodeClamp")
    clamp_metal.location = (470, -220)

    links.new(texcoord.outputs["Object"], mapping.inputs["Vector"])
    links.new(rotation_value.outputs["Value"], rotation_to_radians.inputs[0])
    links.new(rotation_to_radians.outputs["Value"], rotation_vector.inputs["Y"])
    links.new(rotation_vector.outputs["Vector"], mapping.inputs["Rotation"])
    links.new(mapping.outputs["Vector"], gradient.inputs["Vector"])
    links.new(mapping.outputs["Vector"], wave.inputs["Vector"])

    links.new(gradient.outputs["Fac"], band_ramp.inputs["Fac"])
    links.new(wave.outputs["Fac"], wave_ramp.inputs["Fac"])

    links.new(band_ramp.outputs["Color"], band_bw.inputs["Color"])
    links.new(wave_ramp.outputs["Color"], wave_bw.inputs["Color"])
    links.new(band_bw.outputs["Val"], band_streaks.inputs[0])
    links.new(wave_bw.outputs["Val"], band_streaks.inputs[1])
    links.new(band_streaks.outputs["Value"], band_soften.inputs[0])
    links.new(band_soften.outputs["Value"], band_clamp.inputs["Value"])

    links.new(color_1_base.outputs["Color"], color_mix_1.inputs[6])
    links.new(color_1_band.outputs["Color"], color_mix_1.inputs[7])
    links.new(band_clamp.outputs["Result"], color_mix_1.inputs[0])

    links.new(color_2_base.outputs["Color"], color_mix_2.inputs[6])
    links.new(color_2_band.outputs["Color"], color_mix_2.inputs[7])
    links.new(band_clamp.outputs["Result"], color_mix_2.inputs[0])

    links.new(color_mix_1.outputs["Result"], glitter.inputs["Glitter Color 1"])
    links.new(color_mix_2.outputs["Result"], glitter.inputs["Glitter Color 2"])
    links.new(band_clamp.outputs["Result"], rough_mix.inputs[0])
    links.new(band_clamp.outputs["Result"], metallic_mix.inputs[0])
    links.new(rough_mix.outputs["Value"], clamp_rough.inputs["Value"])
    links.new(metallic_mix.outputs["Value"], clamp_metal.inputs["Value"])
    links.new(clamp_rough.outputs["Result"], glitter.inputs["Glitter Roughness"])
    links.new(clamp_metal.outputs["Result"], glitter.inputs["Glitter Metallicness"])

    links.new(tangent_local.outputs["Vector"], tangent_norm.inputs[0])
    links.new(tangent_norm.outputs["Vector"], tangent_to_world.inputs["Vector"])
    links.new(tangent_to_world.outputs["Vector"], aniso.inputs["Tangent"])
    links.new(band_clamp.outputs["Result"], aniso_weight.inputs[0])
    links.new(aniso_weight.outputs["Value"], aniso.inputs[6])

    links.new(glitter.outputs["BSDF"], add_shader.inputs[0])
    links.new(aniso.outputs["BSDF"], add_shader.inputs[1])
    links.new(add_shader.outputs["Shader"], output.inputs["Surface"])

    material.use_fake_user = True
    return material


def assign_material(obj, material):
    if not obj.data.materials:
        obj.data.materials.append(material)
        return
    obj.data.materials[0] = material


def main():
    obj = ensure_target_sphere()
    obj.show_name = True
    obj.hide_viewport = False
    obj.hide_render = False

    material = build_material()
    assign_material(obj, material)
    hide_old_mapping_empty()

    bpy.ops.wm.save_mainfile()
    print(f"Assigned {TARGET_MATERIAL} to {TARGET_OBJECT} and saved {bpy.data.filepath}")


if __name__ == "__main__":
    main()
