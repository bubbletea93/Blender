import math

import bpy
from mathutils import Vector


SOURCE_MATERIAL = "Lacquer_Glitter02_Copper"
TARGET_MATERIAL = "Lacquer_CatEye_Test"
COMPARE_MATERIAL = "Anisotropic Brushed Metal"
LACQUER_OBJECT = "Lacquer"
COMPARE_OBJECT = "Lacquer_CompareSphere"
TARGET_SPHERE_OBJECT = "CatEye_TestSphere"
EMPTY_NAME = "CatEye_Mapping_Empty"
GROUP_NAME = "NG_CatEye_Band"
TARGET_COLLECTION = "Shot_GelPolishBottle"
DEFAULT_STRENGTH = 0.18
DEFAULT_WIDTH = 0.12
DEFAULT_ROTATION = math.pi / 2.0
DEFAULT_BRIGHTNESS_BOOST = 0.08
DEFAULT_ROUGHNESS_DROP = 0.06


def clear_node_tree(node_tree):
    for node in list(node_tree.nodes):
        node_tree.nodes.remove(node)


def ensure_socket(interface, name, in_out, socket_type):
    for item in interface.items_tree:
        if item.item_type != "SOCKET":
            continue
        if item.in_out == in_out and item.name == name:
            return item
    return interface.new_socket(name=name, in_out=in_out, socket_type=socket_type)


def remove_interface_socket(interface, name, in_out):
    for item in list(interface.items_tree):
        if item.item_type != "SOCKET":
            continue
        if item.in_out == in_out and item.name == name:
            interface.remove(item)


def ensure_cat_eye_group():
    group = bpy.data.node_groups.get(GROUP_NAME)
    if group is None:
        group = bpy.data.node_groups.new(GROUP_NAME, "ShaderNodeTree")

    # Reset the interface to the exact contract used by the material.
    for socket_name in ["Vector", "Strength", "Width", "Rotation", "Brightness Boost", "Roughness Drop"]:
        remove_interface_socket(group.interface, socket_name, "INPUT")
    for socket_name in ["Mask", "Color Factor"]:
        remove_interface_socket(group.interface, socket_name, "OUTPUT")

    ensure_socket(group.interface, "Vector", "INPUT", "NodeSocketVector")
    ensure_socket(group.interface, "Strength", "INPUT", "NodeSocketFloat")
    ensure_socket(group.interface, "Width", "INPUT", "NodeSocketFloat")
    ensure_socket(group.interface, "Rotation", "INPUT", "NodeSocketFloat")
    ensure_socket(group.interface, "Brightness Boost", "INPUT", "NodeSocketFloat")
    ensure_socket(group.interface, "Roughness Drop", "INPUT", "NodeSocketFloat")
    ensure_socket(group.interface, "Mask", "OUTPUT", "NodeSocketFloat")
    ensure_socket(group.interface, "Color Factor", "OUTPUT", "NodeSocketFloat")

    clear_node_tree(group)
    nodes = group.nodes
    links = group.links

    group_in = nodes.new("NodeGroupInput")
    group_in.location = (-1800, 0)
    group_out = nodes.new("NodeGroupOutput")
    group_out.location = (850, 0)

    mapping = nodes.new("ShaderNodeMapping")
    mapping.name = "CatEye Mapping"
    mapping.location = (-1500, 50)

    combine_rot = nodes.new("ShaderNodeCombineXYZ")
    combine_rot.location = (-1700, -250)

    clamp_width = nodes.new("ShaderNodeMath")
    clamp_width.name = "Clamp Width"
    clamp_width.operation = "MAXIMUM"
    clamp_width.inputs[1].default_value = 0.0001
    clamp_width.location = (-1700, -500)

    inv_width = nodes.new("ShaderNodeMath")
    inv_width.name = "Inverse Width"
    inv_width.operation = "DIVIDE"
    inv_width.inputs[0].default_value = 1.0
    inv_width.location = (-1500, -500)

    combine_scale = nodes.new("ShaderNodeCombineXYZ")
    combine_scale.location = (-1300, -500)

    gradient = nodes.new("ShaderNodeTexGradient")
    gradient.gradient_type = "LINEAR"
    gradient.location = (-1180, 220)

    band_ramp = nodes.new("ShaderNodeValToRGB")
    band_ramp.name = "Band Shape"
    band_ramp.location = (-920, 220)
    band_ramp.color_ramp.interpolation = "LINEAR"
    band_ramp.color_ramp.elements[0].position = 0.43
    band_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    band_ramp.color_ramp.elements[1].position = 0.49
    band_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    band_ramp.color_ramp.elements.new(0.51)
    band_ramp.color_ramp.elements[2].color = (1.0, 1.0, 1.0, 1.0)
    band_ramp.color_ramp.elements.new(0.57)
    band_ramp.color_ramp.elements[3].color = (0.0, 0.0, 0.0, 1.0)

    linear_light = nodes.new("ShaderNodeMix")
    linear_light.name = "Band Distortion"
    linear_light.blend_type = "LINEAR_LIGHT"
    linear_light.data_type = "RGBA"
    linear_light.inputs[0].default_value = 0.005
    linear_light.location = (-1180, -40)

    noise_a = nodes.new("ShaderNodeTexNoise")
    noise_a.name = "Noise Texture"
    noise_a.noise_dimensions = "3D"
    noise_a.normalize = True
    noise_a.inputs["Scale"].default_value = 1000.0
    noise_a.inputs["Detail"].default_value = 10.0
    noise_a.inputs["Roughness"].default_value = 0.5
    noise_a.inputs["Lacunarity"].default_value = 2.0
    noise_a.inputs["Distortion"].default_value = 2.0
    noise_a.location = (-920, -60)

    separate_xyz = nodes.new("ShaderNodeSeparateXYZ")
    separate_xyz.location = (-1180, -360)

    combine_z = nodes.new("ShaderNodeCombineXYZ")
    combine_z.location = (-920, -360)

    noise_b = nodes.new("ShaderNodeTexNoise")
    noise_b.name = "Noise Texture.001"
    noise_b.noise_dimensions = "3D"
    noise_b.normalize = True
    noise_b.inputs["Scale"].default_value = 1000.0
    noise_b.inputs["Detail"].default_value = 10.0
    noise_b.inputs["Roughness"].default_value = 0.5
    noise_b.inputs["Lacunarity"].default_value = 2.0
    noise_b.inputs["Distortion"].default_value = 2.0
    noise_b.location = (-660, -360)

    ramp_a = nodes.new("ShaderNodeValToRGB")
    ramp_a.name = "Color Ramp.001"
    ramp_a.location = (-660, -20)
    ramp_a.color_ramp.interpolation = "LINEAR"
    ramp_a.color_ramp.elements[0].position = 0.14
    ramp_a.color_ramp.elements[0].color = (0.1, 0.1, 0.1, 1.0)
    ramp_a.color_ramp.elements[1].position = 1.0
    ramp_a.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)

    ramp_b = nodes.new("ShaderNodeValToRGB")
    ramp_b.name = "Color Ramp.002"
    ramp_b.location = (-420, -360)
    ramp_b.color_ramp.interpolation = "LINEAR"
    ramp_b.color_ramp.elements[0].position = 0.14
    ramp_b.color_ramp.elements[0].color = (0.1, 0.1, 0.1, 1.0)
    ramp_b.color_ramp.elements[1].position = 1.0
    ramp_b.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)

    mix_streaks = nodes.new("ShaderNodeMix")
    mix_streaks.name = "Mix.004"
    mix_streaks.blend_type = "MIX"
    mix_streaks.data_type = "RGBA"
    mix_streaks.inputs[0].default_value = 0.5
    mix_streaks.location = (-180, -160)

    band_bw = nodes.new("ShaderNodeRGBToBW")
    band_bw.location = (-420, 80)

    streak_bw = nodes.new("ShaderNodeRGBToBW")
    streak_bw.location = (80, -160)

    multiply_band = nodes.new("ShaderNodeMath")
    multiply_band.name = "Band x Streaks"
    multiply_band.operation = "MULTIPLY"
    multiply_band.location = (80, 80)

    strength_norm = nodes.new("ShaderNodeMath")
    strength_norm.name = "Strength Scale"
    strength_norm.operation = "DIVIDE"
    strength_norm.inputs[1].default_value = DEFAULT_STRENGTH
    strength_norm.location = (-180, 300)

    raw_strength = nodes.new("ShaderNodeMath")
    raw_strength.name = "Apply Strength"
    raw_strength.operation = "MULTIPLY"
    raw_strength.location = (300, 80)

    clamp_raw = nodes.new("ShaderNodeClamp")
    clamp_raw.location = (520, 80)

    rough_mask = nodes.new("ShaderNodeMath")
    rough_mask.name = "Mask Output"
    rough_mask.operation = "MULTIPLY"
    rough_mask.location = (520, -60)

    color_factor = nodes.new("ShaderNodeMath")
    color_factor.name = "Color Output"
    color_factor.operation = "MULTIPLY"
    color_factor.location = (520, -220)

    links.new(group_in.outputs["Vector"], mapping.inputs["Vector"])
    links.new(group_in.outputs["Rotation"], combine_rot.inputs["Z"])
    links.new(combine_rot.outputs["Vector"], mapping.inputs["Rotation"])

    links.new(group_in.outputs["Width"], clamp_width.inputs[0])
    links.new(clamp_width.outputs["Value"], inv_width.inputs[1])
    links.new(inv_width.outputs["Value"], combine_scale.inputs["X"])
    combine_scale.inputs["Y"].default_value = 1.0
    combine_scale.inputs["Z"].default_value = 1.0
    links.new(combine_scale.outputs["Vector"], mapping.inputs["Scale"])

    links.new(mapping.outputs["Vector"], gradient.inputs["Vector"])
    links.new(gradient.outputs["Fac"], band_ramp.inputs["Fac"])
    links.new(gradient.outputs["Color"], linear_light.inputs[6])
    links.new(mapping.outputs["Vector"], linear_light.inputs[7])
    links.new(linear_light.outputs["Result"], noise_a.inputs["Vector"])

    links.new(mapping.outputs["Vector"], separate_xyz.inputs["Vector"])
    links.new(separate_xyz.outputs["Z"], combine_z.inputs["Z"])
    links.new(combine_z.outputs["Vector"], noise_b.inputs["Vector"])

    links.new(noise_a.outputs["Fac"], ramp_a.inputs["Fac"])
    links.new(noise_b.outputs["Fac"], ramp_b.inputs["Fac"])
    links.new(ramp_a.outputs["Color"], mix_streaks.inputs[6])
    links.new(ramp_b.outputs["Color"], mix_streaks.inputs[7])

    # Multiply the narrow band by the compare-sphere-style streak breakup.
    links.new(band_ramp.outputs["Color"], band_bw.inputs["Color"])
    links.new(mix_streaks.outputs["Result"], streak_bw.inputs["Color"])
    links.new(band_bw.outputs["Val"], multiply_band.inputs[0])
    links.new(streak_bw.outputs["Val"], multiply_band.inputs[1])
    links.new(group_in.outputs["Strength"], strength_norm.inputs[0])
    links.new(multiply_band.outputs["Value"], raw_strength.inputs[0])
    links.new(strength_norm.outputs["Value"], raw_strength.inputs[1])
    links.new(raw_strength.outputs["Value"], clamp_raw.inputs["Value"])

    links.new(clamp_raw.outputs["Result"], rough_mask.inputs[0])
    links.new(group_in.outputs["Roughness Drop"], rough_mask.inputs[1])
    links.new(clamp_raw.outputs["Result"], color_factor.inputs[0])
    links.new(group_in.outputs["Brightness Boost"], color_factor.inputs[1])

    links.new(rough_mask.outputs["Value"], group_out.inputs["Mask"])
    links.new(color_factor.outputs["Value"], group_out.inputs["Color Factor"])

    return group


def ensure_target_sphere(lacquer_obj):
    compare_obj = bpy.data.objects.get(COMPARE_OBJECT)
    if compare_obj is None:
        raise RuntimeError(f"Missing compare sphere object: {COMPARE_OBJECT}")
    target_collection = bpy.data.collections.get(TARGET_COLLECTION)
    if target_collection is None:
        raise RuntimeError(f"Missing target collection: {TARGET_COLLECTION}")

    target = bpy.data.objects.get(TARGET_SPHERE_OBJECT)
    if target is None:
        target = compare_obj.copy()
        target.data = compare_obj.data.copy()
        target.name = TARGET_SPHERE_OBJECT
        target_collection.objects.link(target)
    else:
        if target not in target_collection.objects[:]:
            target_collection.objects.link(target)
        for collection in list(target.users_collection):
            if collection != target_collection:
                collection.objects.unlink(target)

    delta = Vector((max(compare_obj.dimensions.x, 0.02) * 1.35, 0.0, 0.0))
    target.location = compare_obj.location + delta
    target.rotation_euler = compare_obj.rotation_euler.copy()
    target.scale = compare_obj.scale.copy()
    target.hide_render = False
    target.hide_viewport = False
    target.show_name = True
    target.data.name = f"{TARGET_SPHERE_OBJECT}_Mesh"
    return target


def ensure_mapping_empty(target_obj):
    target_collection = bpy.data.collections.get(TARGET_COLLECTION)
    if target_collection is None:
        raise RuntimeError(f"Missing target collection: {TARGET_COLLECTION}")
    empty = bpy.data.objects.get(EMPTY_NAME)
    if empty is None:
        empty = bpy.data.objects.new(EMPTY_NAME, None)
        target_collection.objects.link(empty)
    else:
        if empty not in target_collection.objects[:]:
            target_collection.objects.link(empty)
        for collection in list(empty.users_collection):
            if collection != target_collection:
                collection.objects.unlink(empty)
    empty.empty_display_type = "PLAIN_AXES"
    empty.empty_display_size = 0.02
    empty.location = target_obj.location.copy()
    empty.rotation_euler = target_obj.rotation_euler.copy()
    empty.scale = (1.0, 1.0, 1.0)
    if empty.parent != target_obj:
        empty.parent = target_obj
        empty.matrix_parent_inverse = target_obj.matrix_world.inverted()
    return empty


def brightened_color(base_color, amount, warm_shift=(0.0, 0.0, 0.0)):
    return (
        min(1.0, base_color[0] + amount + warm_shift[0]),
        min(1.0, base_color[1] + amount + warm_shift[1]),
        min(1.0, base_color[2] + amount + warm_shift[2]),
        base_color[3],
    )


def create_rgb_node(node_tree, name, color, location):
    node = node_tree.nodes.new("ShaderNodeRGB")
    node.name = name
    node.label = name
    node.outputs[0].default_value = color
    node.location = location
    return node


def create_value_node(node_tree, name, value, location):
    node = node_tree.nodes.new("ShaderNodeValue")
    node.name = name
    node.label = name
    node.outputs[0].default_value = value
    node.location = location
    return node


def ensure_source_material():
    mat = bpy.data.materials.get(SOURCE_MATERIAL)
    if mat is None:
        mat = bpy.data.materials.new(SOURCE_MATERIAL)
        mat.use_nodes = True
        clear_node_tree(mat.node_tree)
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        output = nodes.new("ShaderNodeOutputMaterial")
        output.location = (220, 80)

        glitter = nodes.new("ShaderNodeGroup")
        glitter.name = "Glitter"
        glitter.node_tree = bpy.data.node_groups["Glitter_UVFix"]
        glitter.location = (0, 80)
        glitter.inputs["Glitter Color 1"].default_value = (0.84, 0.28, 0.09, 1.0)
        glitter.inputs["Glitter Color 2"].default_value = (0.06, 0.008, 0.006, 1.0)
        glitter.inputs["Glitter Scale"].default_value = 2.5
        glitter.inputs["X Aspect Radio"].default_value = 1.0
        glitter.inputs["Y Aspect Radio"].default_value = 1.0
        glitter.inputs["Global Rotation"].default_value = 0.0
        glitter.inputs["Translate X"].default_value = 0.0
        glitter.inputs["Translate Y"].default_value = 0.0
        glitter.inputs["Glitter Metallicness"].default_value = 0.47
        glitter.inputs["Glitter Roughness"].default_value = 0.14
        glitter.inputs["Bump Strength"].default_value = 0.0002
        glitter.inputs["Thin Film Thickness"].default_value = 90.0
        glitter.inputs["Thin Film IOR"].default_value = 1.33

        links.new(glitter.outputs["BSDF"], output.inputs["Surface"])

    mat.use_fake_user = True
    return mat


def rebuild_target_material(source_mat, band_group, mapping_empty, target_obj):
    existing = bpy.data.materials.get(TARGET_MATERIAL)
    if existing is None:
        mat = source_mat.copy()
        mat.name = TARGET_MATERIAL
    else:
        mat = existing
        if not mat.use_nodes:
            mat.use_nodes = True

    node_tree = mat.node_tree
    clear_node_tree(node_tree)
    nodes = node_tree.nodes
    links = node_tree.links

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (980, 120)

    glitter = nodes.new("ShaderNodeGroup")
    glitter.name = "Glitter"
    glitter.node_tree = source_mat.node_tree.nodes["Glitter"].node_tree
    glitter.location = (620, 120)

    texcoord = nodes.new("ShaderNodeTexCoord")
    texcoord.name = "Cat Eye Coordinates"
    texcoord.location = (-1200, 200)
    texcoord.object = mapping_empty

    mapping = nodes.new("ShaderNodeMapping")
    mapping.name = "Cat Eye Fallback Mapping"
    mapping.location = (-960, 200)

    max_dim = max(target_obj.dimensions.y, target_obj.dimensions.z, 1e-6)
    scale_value = 1.0 / max_dim
    mapping.inputs["Scale"].default_value = (scale_value, scale_value, scale_value)

    band = nodes.new("ShaderNodeGroup")
    band.name = "Cat Eye Band"
    band.node_tree = band_group
    band.location = (-680, 200)
    band.inputs["Strength"].default_value = DEFAULT_STRENGTH
    band.inputs["Width"].default_value = DEFAULT_WIDTH
    band.inputs["Rotation"].default_value = DEFAULT_ROTATION
    band.inputs["Brightness Boost"].default_value = DEFAULT_BRIGHTNESS_BOOST
    band.inputs["Roughness Drop"].default_value = DEFAULT_ROUGHNESS_DROP

    base_color_1 = (0.84, 0.28, 0.09, 1.0)
    base_color_2 = (0.06, 0.008, 0.006, 1.0)
    bright_color_1 = brightened_color(base_color_1, 0.07, (0.02, 0.03, 0.01))
    bright_color_2 = brightened_color(base_color_2, 0.04, (0.04, 0.02, 0.01))

    color_1_a = create_rgb_node(node_tree, "Base Color 1", base_color_1, (-1220, -120))
    color_1_b = create_rgb_node(node_tree, "Cat Eye Color 1", bright_color_1, (-1220, -280))
    color_2_a = create_rgb_node(node_tree, "Base Color 2", base_color_2, (-1220, -480))
    color_2_b = create_rgb_node(node_tree, "Cat Eye Color 2", bright_color_2, (-1220, -640))

    color_mix_1 = nodes.new("ShaderNodeMix")
    color_mix_1.name = "Mix Color 1"
    color_mix_1.blend_type = "MIX"
    color_mix_1.data_type = "RGBA"
    color_mix_1.location = (-920, -200)

    color_mix_2 = nodes.new("ShaderNodeMix")
    color_mix_2.name = "Mix Color 2"
    color_mix_2.blend_type = "MIX"
    color_mix_2.data_type = "RGBA"
    color_mix_2.location = (-920, -560)

    color_factor_half = nodes.new("ShaderNodeMath")
    color_factor_half.name = "Secondary Color Factor"
    color_factor_half.operation = "MULTIPLY"
    color_factor_half.inputs[1].default_value = 0.6
    color_factor_half.location = (-900, -800)

    rough_base = create_value_node(node_tree, "Base Roughness", 0.14, (-1180, -980))
    rough_subtract = nodes.new("ShaderNodeMath")
    rough_subtract.name = "Band Roughness"
    rough_subtract.operation = "SUBTRACT"
    rough_subtract.location = (-900, -980)

    rough_clamp = nodes.new("ShaderNodeMath")
    rough_clamp.name = "Clamp Roughness"
    rough_clamp.operation = "MAXIMUM"
    rough_clamp.inputs[1].default_value = 0.02
    rough_clamp.location = (-660, -980)

    metallic_base = create_value_node(node_tree, "Base Metallicness", 0.47, (-1180, -1160))
    spec_gain = nodes.new("ShaderNodeMath")
    spec_gain.name = "Specular Gain"
    spec_gain.operation = "MULTIPLY"
    spec_gain.inputs[1].default_value = 0.5
    spec_gain.location = (-900, -1160)

    metallic_add = nodes.new("ShaderNodeMath")
    metallic_add.name = "Band Metallicness"
    metallic_add.operation = "ADD"
    metallic_add.location = (-660, -1160)

    metallic_clamp = nodes.new("ShaderNodeClamp")
    metallic_clamp.location = (-420, -1160)

    links.new(texcoord.outputs["Object"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], band.inputs["Vector"])

    links.new(color_1_a.outputs["Color"], color_mix_1.inputs[6])
    links.new(color_1_b.outputs["Color"], color_mix_1.inputs[7])
    links.new(band.outputs["Color Factor"], color_mix_1.inputs[0])

    links.new(band.outputs["Color Factor"], color_factor_half.inputs[0])
    links.new(color_2_a.outputs["Color"], color_mix_2.inputs[6])
    links.new(color_2_b.outputs["Color"], color_mix_2.inputs[7])
    links.new(color_factor_half.outputs["Value"], color_mix_2.inputs[0])

    links.new(rough_base.outputs["Value"], rough_subtract.inputs[0])
    links.new(band.outputs["Mask"], rough_subtract.inputs[1])
    links.new(rough_subtract.outputs["Value"], rough_clamp.inputs[0])

    links.new(band.outputs["Mask"], spec_gain.inputs[0])
    links.new(metallic_base.outputs["Value"], metallic_add.inputs[0])
    links.new(spec_gain.outputs["Value"], metallic_add.inputs[1])
    links.new(metallic_add.outputs["Value"], metallic_clamp.inputs["Value"])

    links.new(color_mix_1.outputs["Result"], glitter.inputs["Glitter Color 1"])
    links.new(color_mix_2.outputs["Result"], glitter.inputs["Glitter Color 2"])
    glitter.inputs["Glitter Scale"].default_value = 2.5
    glitter.inputs["X Aspect Radio"].default_value = 1.0
    glitter.inputs["Y Aspect Radio"].default_value = 1.0
    glitter.inputs["Global Rotation"].default_value = 0.0
    glitter.inputs["Translate X"].default_value = 0.0
    glitter.inputs["Translate Y"].default_value = 0.0
    links.new(metallic_clamp.outputs["Result"], glitter.inputs["Glitter Metallicness"])
    links.new(rough_clamp.outputs["Value"], glitter.inputs["Glitter Roughness"])
    glitter.inputs["Bump Strength"].default_value = 0.0002
    glitter.inputs["Thin Film Thickness"].default_value = 90.0
    glitter.inputs["Thin Film IOR"].default_value = 1.33

    links.new(glitter.outputs["BSDF"], output.inputs["Surface"])

    return mat


def assign_material(obj, material):
    if not obj.data.materials:
        obj.data.materials.append(material)
        return
    for idx, mat in enumerate(obj.data.materials):
        if mat and mat.name == TARGET_MATERIAL:
            obj.data.materials[idx] = material
            return
    obj.data.materials[0] = material


def restore_lacquer_material(obj, material):
    if not obj.data.materials:
        obj.data.materials.append(material)
        return
    obj.data.materials[0] = material


def main():
    if LACQUER_OBJECT not in bpy.data.objects:
        raise RuntimeError(f"Missing lacquer object: {LACQUER_OBJECT}")
    if COMPARE_MATERIAL not in bpy.data.materials:
        raise RuntimeError(f"Missing compare material: {COMPARE_MATERIAL}")

    source_mat = ensure_source_material()
    lacquer_obj = bpy.data.objects[LACQUER_OBJECT]
    target_sphere = ensure_target_sphere(lacquer_obj)

    band_group = ensure_cat_eye_group()
    mapping_empty = ensure_mapping_empty(target_sphere)
    target_mat = rebuild_target_material(source_mat, band_group, mapping_empty, target_sphere)
    restore_lacquer_material(lacquer_obj, source_mat)
    assign_material(target_sphere, target_mat)

    bpy.ops.wm.save_mainfile()
    print(
        f"Updated {TARGET_MATERIAL}, assigned it to {TARGET_SPHERE_OBJECT}, restored {LACQUER_OBJECT}, "
        f"and saved {bpy.data.filepath}"
    )


if __name__ == "__main__":
    main()
