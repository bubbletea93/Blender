"""Replace only Shot 5's old cup with the approved CC0 community vessel.

Run sequentially after the tray integration, never against the source asset:
  blender --factory-startup --disable-autoexec --background <shot5_v004.blend> \
      --python scripts/integrate_shot5_glass_cup.py

The source .blend is never saved. A self-contained reusable library is written,
then linked into the current shot. Brush and holder controls are preserved.
"""
import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'assets/props/community/glass_cup_cczero/source/Glass Cup.blend'
ASSET = ROOT / 'assets/props/community/glass_cup_cczero/brush_holder.blend'
REPORT = ROOT / 'renders/shot5_community_v004/glass_cup_integration.json'
COLLECTION = 'Prop_CommunityGlassBrushHolder'
INSTANCE = 'SHOT05_CommunityGlassCup'
OLD_PARTS = ('SHOT05_FlexPart_ManicureCup_FlutedGlass',
             'SHOT05_FlexPart_ManicureCup_GoldFoot')
HOLDER = 'SHOT05_ManicureBrushHolder'
TARGET_HEIGHT = .065
MIN_INNER_RADIUS = .0185
MIN_BRUSH_CLEARANCE = .0002


def evaluated_geometry(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        return ([v.co.copy() for v in mesh.vertices],
                [tuple(p.vertices) for p in mesh.polygons])
    finally:
        evaluated.to_mesh_clear()


def radius_at_height(vertices, polygons, height):
    """Minimum radius along polygon/plane intersections, including flat faces."""
    radii = []
    for polygon in polygons:
        points = [vertices[i] for i in polygon]
        crossing = []
        for a, b in zip(points, points[1:] + points[:1]):
            if (a.z - height) * (b.z - height) > 0 or abs(a.z - b.z) < 1e-12:
                continue
            crossing.append(a + (b - a) * ((height - a.z) / (b.z - a.z)))
        if len(crossing) >= 2:
            a, b = crossing[:2]
            d = b - a
            t = max(0, min(1, -a.dot(d) / d.length_squared)) if d.length_squared else 0
            p = a + t * d
            radii.append(math.hypot(p.x, p.y))
    assert radii, f'No cup cross section at {height}'
    return min(radii)


def control_signature(obj):
    ad = obj.animation_data
    return {
        'name': obj.name,
        'parent': obj.parent.name if obj.parent else None,
        'action': ad.action.as_pointer() if ad and ad.action else None,
        'slot': ad.action_slot_handle if ad and ad.action else None,
        'data': obj.data.as_pointer() if obj.data else None,
    }


scene = bpy.context.scene
shot_path = Path(bpy.data.filepath)
assert 'shot5_' in shot_path.name and '_v004' in shot_path.stem, shot_path
assert shot_path.resolve() != SOURCE.resolve()
assert SOURCE.is_file(), SOURCE
assert INSTANCE not in scene.objects, 'Already integrated: inspect the existing instance.'
assert COLLECTION not in bpy.data.collections, 'Existing asset collection: inspect before rerun.'
assert all(name in scene.objects for name in OLD_PARTS), 'Both original cup pieces are required.'
holder = scene.objects[HOLDER]
assert all(scene.objects[name].parent == holder for name in OLD_PARTS)
initial_frame, initial_subframe = scene.frame_current, scene.frame_subframe
protected = [holder] + [obj for obj in scene.objects
                        if obj.name.startswith('SHOT05_BrushFlex_')
                        or obj.name.startswith('SHOT05_FlexPart_NailBrush_')]
before_controls = {obj.name: control_signature(obj) for obj in protected}
source_images_before = set(bpy.data.images)

with bpy.data.libraries.load(str(SOURCE), link=False) as (available, loaded):
    assert 'Glass Cup' in available.objects
    loaded.objects = ['Glass Cup']
cup = loaded.objects[0]
assert cup and cup.type == 'MESH'
asset_collection = bpy.data.collections.new(COLLECTION)
scene.collection.children.link(asset_collection)
asset_collection.objects.link(cup)
cup.parent = None
cup.matrix_world = Matrix.Identity(4)
cup.animation_data_clear()
cup.name = 'CommunityGlassCup_Cczero'
cup.data.name = 'CommunityGlassCup_Cczero_MESH'
dg = bpy.context.evaluated_depsgraph_get()
original_vertices, _ = evaluated_geometry(cup, dg)
minimum = Vector([min(v[i] for v in original_vertices) for i in range(3)])
maximum = Vector([max(v[i] for v in original_vertices) for i in range(3)])
scale = TARGET_HEIGHT / (maximum.z - minimum.z)
center = Vector(((minimum.x + maximum.x) / 2,
                 (minimum.y + maximum.y) / 2, minimum.z))
# Uniform scaling commutes with Catmull-Clark subdivision. Keep the source's
# editable 1,024-vertex topology and level-3 subdivision, normalized to metres.
cup.data.transform(Matrix.Scale(scale, 4) @ Matrix.Translation(-center))
cup.data.update()

material = cup.data.materials[0]
material.name = 'PROP_CommunityGlass_Cczero_Unbranded'
tree = material.node_tree
glass = tree.nodes.get('Glass BSDF')
assert glass and glass.type == 'BSDF_GLASS'
brand_texture = tree.nodes.get('Image Texture')
assert brand_texture and brand_texture.image
assert brand_texture.image.name.startswith('Glass Displacement')
brand_image_name = brand_texture.image.name
bump = tree.nodes.get('Bump')
brand_uv = tree.nodes.get('UV Map')
assert bump and any(link.from_node == bump and link.to_node == glass
                    and link.to_socket == glass.inputs['Normal'] for link in tree.links)
for node in (bump, brand_texture, brand_uv):
    if node:
        tree.nodes.remove(node)
assert not glass.inputs['Normal'].is_linked
assert glass.inputs['Roughness'].is_linked, 'Keep the separate source smudge roughness.'
roughness_source = glass.inputs['Roughness'].links[0].from_socket
clean_roughness = tree.nodes.new('ShaderNodeMath')
clean_roughness.name = 'CleanCosmeticGlass_Roughness'
clean_roughness.label = 'Subtle surface variation: 0.008 + source x 0.035'
clean_roughness.operation = 'MULTIPLY_ADD'
clean_roughness.inputs[1].default_value = .035
clean_roughness.inputs[2].default_value = .008
tree.links.new(roughness_source, clean_roughness.inputs[0])
tree.links.new(clean_roughness.outputs[0], glass.inputs['Roughness'])
for node in tree.nodes:
    if node.type == 'TEX_IMAGE' and node.image:
        assert node.image.packed_file, f'Unpacked source dependency: {node.image.name}'
        node.image.filepath = '//' + Path(node.image.filepath.replace('\\', '/')).name
material['adaptation'] = 'Removed Duralex brand bump; original glass IOR and packed smudge map retained at subtle 0.008 + source x 0.035 roughness.'
cup['creator'] = 'cczero'
cup['license'] = 'CC0'
cup['source_url'] = 'https://blendswap.com/blend/30973'
cup['adaptation'] = 'Uniformly scaled to 65 mm evaluated height; unbranded material.'
asset_collection['creator'] = 'cczero'
asset_collection['license'] = 'CC0'
asset_collection['source_url'] = 'https://blendswap.com/blend/30973'
asset_collection['source_mesh'] = 'Glass Cup / Circle.001'
asset_collection['dimensions_note'] = 'Evaluated at subdivision level 3: 51.976 mm diameter, 65 mm height.'
asset_collection.asset_mark()

dg.update()
vertices, polygons = evaluated_geometry(cup, dg)
cup_tree = BVHTree.FromPolygons(vertices, polygons, epsilon=0)
inner_radius = radius_at_height(vertices, polygons, .063)
assert inner_radius >= MIN_INNER_RADIUS, inner_radius
floor_hit = cup_tree.ray_cast(Vector((0, 0, .07)), Vector((0, 0, -1)), .1)[0]
assert floor_hit is not None
assert abs(min(v.z for v in vertices)) < 1e-7
assert abs(max(v.z for v in vertices) - TARGET_HEIGHT) < 1e-6

# Verify internal brush/cup clearances before replacing anything in the shot.
# Cup geometry is evaluated in the holder's local coordinates, so the existing
# animated holder motion cancels and all individual brush flex remains visible.
samples = sorted(set(range(376, 529)) | {420 + i * .25 for i in range(205)})
handles = [obj for obj in protected if obj.name.startswith('SHOT05_FlexPart_NailBrush_Handle_')]
brush_parts = [obj for obj in protected if obj.type == 'MESH']
minimum_floor_clearance = float('inf')
minimum_surface_clearance = float('inf')
minimum_radial_margin = float('inf')
worst = {}
for sample in samples:
    scene.frame_set(int(sample), subframe=sample - int(sample))
    dg = bpy.context.evaluated_depsgraph_get()
    inverse = holder.matrix_world.inverted()
    stage_inverse = scene.objects['SHOT05_StageReveal'].matrix_world.inverted()
    cup_to_stage = stage_inverse @ holder.matrix_world
    # Evaluated vertices include the true rounded outline rather than the box.
    largest_radius = max(math.hypot(p.x, p.y) for p in (cup_to_stage @ v for v in vertices))
    minimum_radial_margin = min(minimum_radial_margin, .160 - largest_radius)
    for obj in brush_parts:
        local_vertices, faces = evaluated_geometry(obj, dg)
        matrix = inverse @ obj.evaluated_get(dg).matrix_world
        points = [matrix @ v for v in local_vertices]
        tree = BVHTree.FromPolygons(points, faces, epsilon=0)
        assert not cup_tree.overlap(tree), f'Brush intersects cup: {sample}, {obj.name}'
        for point in points:
            # The meshes meet no other solid inside the vessel, so nearest
            # surface distance is meaningful for the separate brush assembly.
            distance = cup_tree.find_nearest(point)[3]
            if distance < minimum_surface_clearance:
                minimum_surface_clearance = distance
                worst = {'sample': sample, 'object': obj.name}
        if obj in handles:
            bottom = min(points, key=lambda p: p.z)
            hit = cup_tree.ray_cast(Vector((bottom.x, bottom.y, .07)), Vector((0, 0, -1)), .1)[0]
            assert hit is not None, f'No interior floor below {obj.name}'
            minimum_floor_clearance = min(minimum_floor_clearance, bottom.z - hit.z)
assert minimum_surface_clearance >= MIN_BRUSH_CLEARANCE, (minimum_surface_clearance, worst)
assert minimum_floor_clearance >= MIN_BRUSH_CLEARANCE, minimum_floor_clearance
assert minimum_radial_margin > .001, minimum_radial_margin

scene.frame_set(initial_frame, subframe=initial_subframe)
assert before_controls == {obj.name: control_signature(obj) for obj in protected}
ASSET.parent.mkdir(parents=True, exist_ok=True)
# libraries.write writes only this collection's dependency closure, with packed
# roughness data. It never saves or modifies the community source .blend.
bpy.data.libraries.write(str(ASSET), {asset_collection}, path_remap='RELATIVE_ALL',
                         fake_user=True, compress=True)
mesh = cup.data
source_material = material
bpy.data.objects.remove(cup, do_unlink=True)
bpy.data.collections.remove(asset_collection, do_unlink=True)
if mesh.users == 0:
    bpy.data.meshes.remove(mesh)
if source_material.users == 0:
    bpy.data.materials.remove(source_material)
for image in list(bpy.data.images):
    if image not in source_images_before and image.users == 0:
        bpy.data.images.remove(image)

with bpy.data.libraries.load(str(ASSET), link=True) as (available, loaded):
    assert COLLECTION in available.collections
    loaded.collections = [COLLECTION]
linked = loaded.collections[0]
assert linked and linked.library
instance = bpy.data.objects.new(INSTANCE, None)
holder.users_collection[0].objects.link(instance)
instance.parent = holder
instance.matrix_parent_inverse = Matrix.Identity(4)
instance.matrix_basis = Matrix.Identity(4)
instance.instance_type = 'COLLECTION'
instance.instance_collection = linked
instance['source_url'] = 'https://blendswap.com/blend/30973'
instance['license'] = 'CC0'
for name in OLD_PARTS:
    bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
assert before_controls == {obj.name: control_signature(obj) for obj in protected}
scene.frame_set(initial_frame, subframe=initial_subframe)
scene['shot5_community_cup'] = 'cczero CC0 faceted glass cup, unbranded, linked reusable asset.'
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_as_mainfile(filepath=str(shot_path))
report = {
    'source': str(SOURCE.relative_to(ROOT)),
    'source_url': 'https://blendswap.com/blend/30973',
    'creator': 'cczero', 'license': 'CC0',
    'asset': str(ASSET.relative_to(ROOT)), 'scene': str(shot_path),
    'collection': COLLECTION, 'instance': INSTANCE,
    'removed_scene_objects': list(OLD_PARTS),
    'removed_brand_texture_branch': brand_image_name,
    'preserved': 'Holder root, three brush controls, nine brush meshes, their materials/actions/parenting.',
    'source_uniform_scale': scale,
    'dimensions_m': [max(v[i] for v in vertices) - min(v[i] for v in vertices) for i in range(3)],
    'interior_floor_m': floor_hit.z,
    'inner_inscribed_radius_at_63mm': inner_radius,
    'samples': len(samples), 'brush_cup_intersections': 0,
    'minimum_brush_surface_clearance_m': minimum_surface_clearance,
    'minimum_brush_floor_clearance_m': minimum_floor_clearance,
    'minimum_cup_podium_radial_margin_m': minimum_radial_margin,
    'worst_brush_clearance': worst,
    'requires_final_review': 'Run full assembly/camera checks and rendered comparison after tray integration.'
}
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
print('SHOT5_COMMUNITY_CUP=' + json.dumps(report))
