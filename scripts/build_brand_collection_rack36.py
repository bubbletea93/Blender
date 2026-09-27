"""Build the complete 36-shade acrylic collection display.

Run in factory background Blender. Reuses approved, full-size product meshes
and the shared collection palette without changing the board's source geometry.
Front is -Y; bottom is Z0; dimensions are metres.
"""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand_collection_palette import PALETTE

SOURCE = ROOT / 'scenes/gel_polish_lapohka_shot5_376_528.blend'
DEST = ROOT / 'assets/props/brand_collection_bottle_rack_36.blend'
OUT = ROOT / 'renders/shot5_brand_collection_rack36'
OUT.mkdir(parents=True, exist_ok=True)

palette = PALETTE
assert len(palette) == 36 and len({p[0] for p in palette}) == 36

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = 'BrandCollection_ReusableRack36'
scene.unit_settings.system = 'METRIC'
with bpy.data.libraries.load(str(SOURCE), link=False) as (available, requested):
    requested.collections = ['SHOT05_Product_PetrolTeal']
source = requested.collections[0]
assert source is not None
scene.collection.children.link(source)
bpy.context.view_layer.update()
rotation = Matrix.Rotation(math.pi / 2, 4, 'X')
depsgraph = bpy.context.evaluated_depsgraph_get()
points = [rotation @ obj.matrix_world @ Vector(p) for obj in source.all_objects
          if obj.type == 'MESH' for p in obj.evaluated_get(depsgraph).bound_box]
minimum = Vector([min(p[i] for p in points) for i in range(3)])
maximum = Vector([max(p[i] for p in points) for i in range(3)])
normalise = Matrix.Translation((-((minimum.x + maximum.x) / 2),
                               -((minimum.y + maximum.y) / 2), -minimum.z)) @ rotation
original_lacquer = next(slot.material for obj in source.objects
                        if obj.name.endswith('_Lacquer') for slot in obj.material_slots)

# Evaluate the approved rigid product once. Repeating live subdivision and
# displacement modifiers for 36 material variants creates independent dense
# geometry and excessive deformation-motion buffers. Shared finished meshes
# retain the exact approved surface and UVs, while allowing transform blur.
shared_finished_meshes = {}
finished_mesh_report = []
for obj in source.objects:
    if obj.type != 'MESH':
        continue
    if obj.modifiers:
        finished = bpy.data.meshes.new_from_object(
            obj.evaluated_get(depsgraph), preserve_all_data_layers=True, depsgraph=depsgraph)
        finished.name = 'Collection36_SharedFinished_' + obj.name.rsplit('_',1)[-1]
    else:
        finished = obj.data
    shared_finished_meshes[obj.name] = finished
    finished_mesh_report.append({'part':obj.name,'mesh':finished.name,
                                 'vertices':len(finished.vertices),'polygons':len(finished.polygons),
                                 'source_modifiers_evaluated':len(obj.modifiers)})

variants = []
for index, (name, base, band) in enumerate(palette):
    shade_id = 211 + index
    collection = bpy.data.collections.new(f'CollectionBottle36_{shade_id}_{name}')
    collection['shade_id'] = shade_id
    collection['shade_name'] = name
    lacquer = original_lacquer.copy()
    lacquer.name = f'COLLECTION36_Lacquer_{shade_id}_{name}'
    lacquer.animation_data_clear()
    lacquer.node_tree.animation_data_clear()
    for node in lacquer.node_tree.nodes:
        if node.type == 'RGB' and node.name.startswith('Base Color'):
            node.outputs[0].default_value = (*base, 1)
        if node.type == 'RGB' and node.name.startswith('Band Color'):
            node.outputs[0].default_value = (*band, 1)
        if node.type == 'BSDF_GLOSSY':
            node.inputs['Color'].default_value = (*base, 1)
        if node.type == 'TEX_COORD':
            node.object = None
    lacquer['shade_id'] = shade_id
    lacquer['finish_source'] = 'Approved fine-shimmer lacquer; source board palette; no colorimetric catalogue claim'
    for obj in source.objects:
        duplicate = obj.copy()
        duplicate.name = f'CollectionBottle36_{shade_id}_{name}_{obj.name.rsplit("_", 1)[-1]}'
        duplicate.animation_data_clear()
        duplicate.parent = None
        if obj.type == 'MESH':
            duplicate.data = shared_finished_meshes[obj.name]
            duplicate.modifiers.clear()
            duplicate.cycles.use_deform_motion = False
        duplicate.matrix_world = normalise @ obj.matrix_world
        collection.objects.link(duplicate)
        duplicate.light_linking.receiver_collection = None
        duplicate.light_linking.blocker_collection = None
        if obj.name.endswith('_Lacquer'):
            for slot in duplicate.material_slots:
                slot.link = 'OBJECT'
                slot.material = lacquer
    variants.append(collection)
scene.collection.children.unlink(source)

rack = bpy.data.collections.new('Prop_BrandCollection_AcrylicRack36')
scene.collection.children.link(rack)
rack.asset_mark()
rack.asset_data.description = 'Complete 36-shade, six-row by six-column clear acrylic polish display. Full-size product copies; front -Y; bottom Z0.'
rack['reference'] = 'User supplied HANG PURE collection/rack photographs'
rack['product_scale'] = 1.0
rack['rows'] = 6
rack['columns'] = 6
rack['shade_ids'] = list(range(211, 247))
rack['pitch_x_m'] = .054
rack['pitch_y_m'] = .049
rack['rise_m'] = .042
rack['display_note'] = 'All 36 board shades; approximate reference color families, not a color-calibrated catalogue.'

def material(name, color, metal=0, rough=.25, transmission=0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    node = mat.node_tree.nodes.get('Principled BSDF')
    node.inputs['Base Color'].default_value = (*color, 1)
    node.inputs['Metallic'].default_value = metal
    node.inputs['Roughness'].default_value = rough
    node.inputs['Transmission Weight'].default_value = transmission
    node.inputs['IOR'].default_value = 1.49
    return mat

acrylic = material('COLLECTION36_OpticalAcrylic', (.985, .994, 1), rough=.035, transmission=1)
silver = material('COLLECTION36_SilverFasteners', (.60, .65, .69), 1, .2)
ink = material('COLLECTION36_SubtleEngraving', (.16, .12, .075), .35, .32)

def finish(obj, name, mat, bevel=0):
    obj.name = name
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    rack.objects.link(obj)
    obj.data.materials.append(mat)
    if bevel:
        modifier = obj.modifiers.new('Polished manufactured edge', 'BEVEL')
        modifier.width = bevel
        modifier.segments = 3
        modifier.harden_normals = True
        obj.modifiers.new('Flat optical face normals', 'WEIGHTED_NORMAL')
    return obj

def cube(name, location, size, mat=acrylic, bevel=.00045):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, bevel)

row_centres = [(row - 2.5) * .049 for row in range(6)]
shelf_tops = [.006 + row * .042 for row in range(6)]
for row, (y, top) in enumerate(zip(row_centres, shelf_tops)):
    cube(f'CollectionRack36_Shelf_R{row + 1}', (0, y, top - .0015), (.326, .049, .003))
    cube(f'CollectionRack36_RetainingRail_R{row + 1}', (0, y - .0245, top + .005),
         (.326, .002, .010))
    if row:
        cube(f'CollectionRack36_ClearRiser_R{row + 1}',
             (0, y - .0245, top - .021), (.326, .0025, .042))
cube('CollectionRack36_BackPanel', (0, .1475, .116), (.326, .0025, .232))

# Closed sloping panels support the entire underside of every step. The upper
# edge stays above each shelf, leaving most of the product visibly unobstructed.
profile = [(-.148, 0), (.148, 0), (.148, .270), (-.148, .058)]
for side in (-1, 1):
    xs = (side * .163 - .00125, side * .163 + .00125)
    vertices = [(x, y, z) for x in xs for y, z in profile]
    faces = [(3, 2, 1, 0), (4, 5, 6, 7)]
    faces += [(i, (i + 1) % 4, (i + 1) % 4 + 4, i + 4) for i in range(4)]
    mesh = bpy.data.meshes.new(f'CollectionRack36_Side_{side}_MESH')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(f'CollectionRack36_Side_{side}', mesh)
    rack.objects.link(obj)
    finish(obj, obj.name, acrylic, .0006)
    for row, (y, top) in enumerate(zip(row_centres, shelf_tops)):
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=.0026, depth=.0015,
             location=(side * .165, y, top - .0015), rotation=(0, math.pi / 2, 0))
        finish(bpy.context.object, f'CollectionRack36_SilverBolt_{side}_R{row + 1}', silver, .00022)
        cube(f'CollectionRack36_ScrewSlot_{side}_R{row + 1}',
             (side * .1658, y, top - .0015), (.00008, .0028, .00035), ink, .00007)
for x in (-.142, 0, .142):
    for y in (-.123, .123):
        cube('CollectionRack36_ClearFoot', (x, y, .0015), (.016, .016, .003), bevel=.0007)

bottles = []
for row in range(6):
    for column in range(6):
        index = row * 6 + column
        shade_id = 211 + index
        obj = bpy.data.objects.new(f'CollectionRack36_Bottle_R{row + 1}_C{column + 1}_{shade_id}_{palette[index][0]}', None)
        rack.objects.link(obj)
        obj.instance_type = 'COLLECTION'
        obj.instance_collection = variants[index]
        obj.location = ((column - 2.5) * .054, row_centres[row], shelf_tops[row] + .0002)
        obj.empty_display_size = .007
        obj['row'] = row + 1
        obj['column'] = column + 1
        obj['shade'] = palette[index][0]
        obj['shade_id'] = shade_id
        obj['shelf_top_m'] = shelf_tops[row]
        obj['motion_note'] = 'Base at true evaluated product foot; full-size copy.'
        bottles.append(obj)

label = bpy.data.curves.new('CollectionRack36_Label_DATA', 'FONT')
label.body = 'H A N G   P U R E   /   3 6   S H A D E S'
label.align_x = 'CENTER'
label.size = .0026
label.extrude = .000005
obj = bpy.data.objects.new('CollectionRack36_Label', label)
rack.objects.link(obj)
obj.location = (0, -.14808, .008)
obj.rotation_euler.x = math.pi / 2
label.materials.append(ink)

bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
all_points = [instance.matrix_world @ Vector(point) for instance in depsgraph.object_instances
              if instance.object.type == 'MESH' for point in instance.object.bound_box]
bounds = [[min(point[axis] for point in all_points) for axis in range(3)],
          [max(point[axis] for point in all_points) for axis in range(3)]]
dimensions = [bounds[1][axis] - bounds[0][axis] for axis in range(3)]
assert len(bottles) == 36
assert {obj['shade_id'] for obj in bottles} == set(range(211, 247))
assert {(obj['row'], obj['column']) for obj in bottles} == {(r, c) for r in range(1, 7) for c in range(1, 7)}
assert all(abs(obj.location.z - obj['shelf_top_m'] - .0002) < 1e-7 for obj in bottles)
assert .054 > maximum.x - minimum.x and .049 > maximum.y - minimum.y
assert all(tuple(obj.scale) == (1, 1, 1) for obj in bottles)
rack['dimensions_m'] = dimensions
bpy.data.libraries.write(str(DEST), {rack}, path_remap='RELATIVE_ALL', fake_user=True, compress=True)
report = {
    'asset': str(DEST), 'collection': rack.name, 'bounds': bounds,
    'shared_finished_product_meshes': finished_mesh_report,
    'geometry_strategy': 'Approved modifiers evaluated once at their existing levels; all 36 variants share the resulting meshes, with rigid transform motion blur.',
    'dimensions_m': dimensions, 'bottle_dimensions_m': list(maximum - minimum),
    'bottle_count': len(bottles), 'rows': 6, 'columns': 6,
    'pitch_x_m': .054, 'pitch_y_m': .049, 'rise_m': .042,
    'shelf_tops_m': shelf_tops, 'row_centres_y_m': row_centres,
    'shade_ids': list(range(211, 247)),
    'palette': [{'shade_id': 211 + i, 'name': p[0], 'base': p[1], 'band': p[2]} for i, p in enumerate(palette)],
    'bottles': [{'name': ob.name, 'row': ob['row'], 'column': ob['column'],
                 'shade_id': ob['shade_id'], 'location': list(ob.location),
                 'shelf_top_m': ob['shelf_top_m']} for ob in bottles],
    'validation': {'count_36': True, 'all_shades_211_246': True, 'six_rows_six_columns': True,
                   'product_scale_unchanged': True, 'shelf_clearance_m': .0002,
                   'horizontal_gap_m': .054 - (maximum.x - minimum.x),
                   'depth_gap_m': .049 - (maximum.y - minimum.y)},
}
(OUT / 'rack_build.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('RACK36_LIBRARY_READY', str(DEST), flush=True)
