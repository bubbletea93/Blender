import bpy


LACQUER_OBJECT = "Lacquer"
TARGET_MATERIAL = "Lacquer_CatEye_Mesh"
BASE_MATERIAL = "Lacquer_Glitter02_Copper"
GLITTER_GROUP = "Glitter_UVFix"
REFERENCE_OBJECTS = ["CatEye_TestSphere", "Lacquer_CompareSphere"]


def clear_node_tree(node_tree):
    for node in list(node_tree.nodes):
        node_tree.nodes.remove(node)


def ensure_base_material():
    material = bpy.data.materials.get(BASE_MATERIAL)
    if material is None:
        raise RuntimeError(f"Missing base material: {BASE_MATERIAL}")
    material.use_fake_user = True
    return material


def create_rgb(nodes, name, color, location):
    node = nodes.new("ShaderNodeRGB")
    node.name = name
    node.label = name
    node.outputs[0].default_value = color
    node.location = location
    return node


def create_value(nodes, name, value, location):
    node = nodes.new("ShaderNodeValue")
    node.name = name
    node.label = name
    node.outputs[0].default_value = value
    node.location = location
    return node


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
    output.location = (1520, 180)

    add_shader = nodes.new("ShaderNodeAddShader")
    add_shader.location = (1290, 180)

    glitter = nodes.new("ShaderNodeGroup")
    glitter.name = "Base Glitter"
    glitter.node_tree = bpy.data.node_groups[GLITTER_GROUP]
    glitter.location = (1030, 340)
    glitter.inputs["Glitter Scale"].default_value = 2.35
    glitter.inputs["X Aspect Radio"].default_value = 1.0
    glitter.inputs["Y Aspect Radio"].default_value = 1.0
    glitter.inputs["Global Rotation"].default_value = 0.0
    glitter.inputs["Translate X"].default_value = 0.0
    glitter.inputs["Translate Y"].default_value = 0.0
    glitter.inputs["Bump Strength"].default_value = 0.00018
    glitter.inputs["Thin Film Thickness"].default_value = 90.0
    glitter.inputs["Thin Film IOR"].default_value = 1.33

    texcoord = nodes.new("ShaderNodeTexCoord")
    texcoord.location = (-1950, 40)

    mapping = nodes.new("ShaderNodeMapping")
    mapping.name = "Diagonal Mapping"
    mapping.location = (-1710, 40)
    # Lacquer face is the Y/Z plane. Rotate the mask so the broad band leans
    # upper-left to lower-right like the reference photos.
    mapping.inputs["Rotation"].default_value = (0.0, 0.0, 0.72)
    mapping.inputs["Scale"].default_value = (1.0, 2.4, 1.0)

    gradient = nodes.new("ShaderNodeTexGradient")
    gradient.gradient_type = "LINEAR"
    gradient.location = (-1470, 220)

    band_ramp = nodes.new("ShaderNodeValToRGB")
    band_ramp.name = "Static Band Shape"
    band_ramp.location = (-1220, 220)
    band_ramp.color_ramp.interpolation = "EASE"
    band_ramp.color_ramp.elements[0].position = 0.28
    band_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    band_ramp.color_ramp.elements[1].position = 0.66
    band_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    mid = band_ramp.color_ramp.elements.new(0.46)
    mid.color = (0.74, 0.74, 0.74, 1.0)

    wave = nodes.new("ShaderNodeTexWave")
    wave.location = (-1470, -40)
    wave.wave_type = "BANDS"
    wave.bands_direction = "Y"
    wave.inputs["Scale"].default_value = 40.0
    wave.inputs["Distortion"].default_value = 1.6
    wave.inputs["Detail"].default_value = 4.5
    wave.inputs["Detail Scale"].default_value = 1.0
    wave.inputs["Detail Roughness"].default_value = 0.35

    wave_ramp = nodes.new("ShaderNodeValToRGB")
    wave_ramp.name = "Directional Streaks"
    wave_ramp.location = (-1220, -40)
    wave_ramp.color_ramp.interpolation = "LINEAR"
    wave_ramp.color_ramp.elements[0].position = 0.36
    wave_ramp.color_ramp.elements[0].color = (0.28, 0.28, 0.28, 1.0)
    wave_ramp.color_ramp.elements[1].position = 0.72
    wave_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)

    reflect_to_object = nodes.new("ShaderNodeVectorTransform")
    reflect_to_object.vector_type = "VECTOR"
    reflect_to_object.convert_from = "WORLD"
    reflect_to_object.convert_to = "OBJECT"
    reflect_to_object.location = (-1470, -360)

    view_axis = nodes.new("ShaderNodeCombineXYZ")
    view_axis.location = (-1710, -520)
    view_axis.inputs["X"].default_value = 0.0
    view_axis.inputs["Y"].default_value = 0.86
    view_axis.inputs["Z"].default_value = 0.5

    view_axis_norm = nodes.new("ShaderNodeVectorMath")
    view_axis_norm.operation = "NORMALIZE"
    view_axis_norm.location = (-1470, -520)

    view_dot = nodes.new("ShaderNodeVectorMath")
    view_dot.operation = "DOT_PRODUCT"
    view_dot.location = (-1220, -420)

    view_abs = nodes.new("ShaderNodeMath")
    view_abs.operation = "ABSOLUTE"
    view_abs.location = (-990, -420)

    view_ramp = nodes.new("ShaderNodeValToRGB")
    view_ramp.name = "Reactive Compression"
    view_ramp.location = (-760, -420)
    view_ramp.color_ramp.interpolation = "EASE"
    view_ramp.color_ramp.elements[0].position = 0.0
    view_ramp.color_ramp.elements[0].color = (1.0, 1.0, 1.0, 1.0)
    view_ramp.color_ramp.elements[1].position = 0.22
    view_ramp.color_ramp.elements[1].color = (0.0, 0.0, 0.0, 1.0)

    band_bw = nodes.new("ShaderNodeRGBToBW")
    band_bw.location = (-990, 220)

    streak_bw = nodes.new("ShaderNodeRGBToBW")
    streak_bw.location = (-990, -40)

    view_bw = nodes.new("ShaderNodeRGBToBW")
    view_bw.location = (-520, -420)

    band_streaks = nodes.new("ShaderNodeMath")
    band_streaks.operation = "MULTIPLY"
    band_streaks.location = (-760, 100)

    band_reactive = nodes.new("ShaderNodeMath")
    band_reactive.operation = "MULTIPLY"
    band_reactive.location = (-520, -60)

    band_plus_view = nodes.new("ShaderNodeMath")
    band_plus_view.operation = "MULTIPLY_ADD"
    band_plus_view.location = (-280, -60)
    band_plus_view.inputs[1].default_value = 0.58
    band_plus_view.inputs[2].default_value = 0.04

    band_clamp = nodes.new("ShaderNodeClamp")
    band_clamp.location = (-40, -60)

    tangent_local = nodes.new("ShaderNodeCombineXYZ")
    tangent_local.location = (-1710, -770)
    tangent_local.inputs["X"].default_value = 0.0
    tangent_local.inputs["Y"].default_value = 1.0
    tangent_local.inputs["Z"].default_value = -1.0

    tangent_norm = nodes.new("ShaderNodeVectorMath")
    tangent_norm.operation = "NORMALIZE"
    tangent_norm.location = (-1470, -770)

    tangent_to_world = nodes.new("ShaderNodeVectorTransform")
    tangent_to_world.vector_type = "VECTOR"
    tangent_to_world.convert_from = "OBJECT"
    tangent_to_world.convert_to = "WORLD"
    tangent_to_world.location = (-1220, -770)

    aniso = nodes.new("ShaderNodeBsdfAnisotropic")
    aniso.location = (1030, 40)
    aniso.inputs["Color"].default_value = (0.98, 0.74, 0.64, 1.0)
    aniso.inputs["Roughness"].default_value = 0.16
    aniso.inputs["Anisotropy"].default_value = 0.9
    aniso.inputs["Rotation"].default_value = 0.0

    aniso_weight = nodes.new("ShaderNodeMath")
    aniso_weight.operation = "MULTIPLY"
    aniso_weight.location = (280, -320)
    aniso_weight.inputs[1].default_value = 0.24

    color_mix_1 = nodes.new("ShaderNodeMix")
    color_mix_1.data_type = "RGBA"
    color_mix_1.blend_type = "MIX"
    color_mix_1.location = (260, 360)

    color_mix_2 = nodes.new("ShaderNodeMix")
    color_mix_2.data_type = "RGBA"
    color_mix_2.blend_type = "MIX"
    color_mix_2.location = (260, 180)

    color_1_base = create_rgb(nodes, "Base Color 1", (0.84, 0.28, 0.09, 1.0), (0, 460))
    color_1_band = create_rgb(nodes, "Band Color 1", (0.92, 0.57, 0.46, 1.0), (0, 320))
    color_2_base = create_rgb(nodes, "Base Color 2", (0.06, 0.008, 0.006, 1.0), (0, 280))
    color_2_band = create_rgb(nodes, "Band Color 2", (0.18, 0.05, 0.06, 1.0), (0, 140))

    rough_mix = nodes.new("ShaderNodeMath")
    rough_mix.operation = "MULTIPLY_ADD"
    rough_mix.location = (520, -20)
    rough_mix.inputs[1].default_value = -0.06
    rough_mix.inputs[2].default_value = 0.14

    metallic_mix = nodes.new("ShaderNodeMath")
    metallic_mix.operation = "MULTIPLY_ADD"
    metallic_mix.location = (520, -220)
    metallic_mix.inputs[1].default_value = 0.05
    metallic_mix.inputs[2].default_value = 0.47

    clamp_rough = nodes.new("ShaderNodeClamp")
    clamp_rough.location = (760, -20)

    clamp_metal = nodes.new("ShaderNodeClamp")
    clamp_metal.location = (760, -220)

    links.new(texcoord.outputs["Object"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], gradient.inputs["Vector"])
    links.new(mapping.outputs["Vector"], wave.inputs["Vector"])

    links.new(texcoord.outputs["Reflection"], reflect_to_object.inputs["Vector"])
    links.new(gradient.outputs["Fac"], band_ramp.inputs["Fac"])
    links.new(wave.outputs["Fac"], wave_ramp.inputs["Fac"])

    links.new(view_axis.outputs["Vector"], view_axis_norm.inputs[0])
    links.new(reflect_to_object.outputs["Vector"], view_dot.inputs[0])
    links.new(view_axis_norm.outputs["Vector"], view_dot.inputs[1])
    links.new(view_dot.outputs["Value"], view_abs.inputs[0])
    links.new(view_abs.outputs["Value"], view_ramp.inputs["Fac"])

    links.new(band_ramp.outputs["Color"], band_bw.inputs["Color"])
    links.new(wave_ramp.outputs["Color"], streak_bw.inputs["Color"])
    links.new(view_ramp.outputs["Color"], view_bw.inputs["Color"])

    links.new(band_bw.outputs["Val"], band_streaks.inputs[0])
    links.new(streak_bw.outputs["Val"], band_streaks.inputs[1])
    links.new(band_streaks.outputs["Value"], band_reactive.inputs[0])
    links.new(view_bw.outputs["Val"], band_reactive.inputs[1])
    links.new(band_reactive.outputs["Value"], band_plus_view.inputs[0])
    links.new(band_plus_view.outputs["Value"], band_clamp.inputs["Value"])

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


def hide_reference_objects():
    for name in REFERENCE_OBJECTS:
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        obj.hide_render = True


def main():
    lacquer = bpy.data.objects.get(LACQUER_OBJECT)
    if lacquer is None:
        raise RuntimeError(f"Missing lacquer object: {LACQUER_OBJECT}")

    material = build_material()
    assign_material(lacquer, material)
    hide_reference_objects()

    bpy.ops.wm.save_mainfile()
    print(f"Assigned {TARGET_MATERIAL} to {LACQUER_OBJECT} and saved {bpy.data.filepath}")


if __name__ == "__main__":
    main()
