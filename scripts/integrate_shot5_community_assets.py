"""Integrate the approved community tray into Shot 5, preserving source assets.

Run against the v004 working scene after the official BlenderKit import.
The original tray and its provenance remain under community/organic_ceramic_tray.
The acquired glass cup is integrated separately by integrate_shot5_glass_cup.py.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'renders/shot5_community_v004'
OUT.mkdir(parents=True, exist_ok=True)
LIBRARY = ROOT / 'assets/props/community/manicure_community_props.blend'
SCENE = ROOT / 'scenes/gel_polish_lapohka_shot5_376_528_polish_finale_v004.blend'
s = bpy.context.scene
s.frame_set(480)
bpy.context.view_layer.update()

assert bpy.data.objects.get('SHOT05_CeramicTray') is None, 'Tray already integrated'
staging = bpy.data.collections['SHOT05_COMMUNITY_IMPORT_STAGING']
source = bpy.data.objects['geo_x_organicCeramicTray']
bounds = [Vector(v) for v in source.bound_box]
minimum = Vector(tuple(min(v[a] for v in bounds) for a in range(3)))
maximum = Vector(tuple(max(v[a] for v in bounds) for a in range(3)))
center = Vector(((minimum.x+maximum.x)/2, (minimum.y+maximum.y)/2, minimum.z))

# A reusable derivative has its underside at Z0 and long axis along X.
# Scale remains uniform; the leaf form and raised rim are unaltered.
asset = bpy.data.collections.new('Prop_Community_OrganicCeramicTray')
mesh = source.copy()
mesh.data = source.data.copy()
mesh.name = 'Community_OrganicCeramicTray'
mesh.parent = None
mesh.matrix_world = Matrix.Identity(4)
mesh.data.transform(Matrix.Rotation(math.pi/2, 4, 'Z') @ Matrix.Translation(-center))
asset.objects.link(mesh)
material = source.data.materials[0].copy()
material.name = 'Community_Tray_WarmIvoryGlaze'
mesh.data.materials.clear()
mesh.data.materials.append(material)
nodes, links = material.node_tree.nodes, material.node_tree.links
bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
base = bsdf.inputs['Base Color']
old_socket = base.links[0].from_socket if base.is_linked else None
tint = nodes.new('ShaderNodeMixRGB')
tint.name = 'Shot5 warm ivory glaze'
tint.label = 'Warm ivory; retain source texture variation'
tint.inputs[0].default_value = .82
tint.inputs[2].default_value = (.82, .77, .66, 1)
if old_socket: links.new(old_socket, tint.inputs[1])
else: tint.inputs[1].default_value = base.default_value
links.new(tint.outputs[0], base)
asset['creator'] = 'Santiago Adrio'
asset['source_url'] = 'https://www.blenderkit.com/asset-gallery-detail/ec82565c-f623-4d81-a50a-60fbaf24a075/'
asset['license'] = 'BlenderKit Royalty Free'
asset['adaptation'] = 'Recentered, long axis X; local ivory color mix. Geometry proportions unchanged.'
asset.asset_mark()
bpy.data.libraries.write(str(LIBRARY), {asset}, path_remap='RELATIVE', fake_user=True, compress=True)

# Replace only the temporary import. Other shot assets remain untouched.
for obj in list(staging.objects): bpy.data.objects.remove(obj, do_unlink=True)
bpy.data.collections.remove(staging)
bpy.data.objects.remove(mesh, do_unlink=True)
bpy.data.collections.remove(asset)
with bpy.data.libraries.load(str(LIBRARY), link=True) as (src, dst):
    dst.collections = ['Prop_Community_OrganicCeramicTray']
linked = dst.collections[0]
destination = bpy.data.collections['SHOT05_02_MANICURE_PROPS']
tray = bpy.data.objects.new('SHOT05_CeramicTray', None)
destination.objects.link(tray)
tray.parent = bpy.data.objects['SHOT05_StageReveal']
tray.location = (-.103, -.034, .0502)
tray.rotation_euler.z = math.radians(-18)
tray.empty_display_size = .015
instance = bpy.data.objects.new('SHOT05_CeramicTray_Asset', None)
destination.objects.link(instance)
instance.parent = tray
instance.instance_type = 'COLLECTION'
instance.instance_collection = linked
scale = .080 / (maximum.y-minimum.y)
instance.scale = (scale,)*3
for frame, height in [(376,0),(433,0),(437,.00025),(442,0),(446,.00008),(450,0),(528,0)]:
    tray.location.z = .0502 + height
    tray.keyframe_insert('location', index=2, frame=frame, group='Ceramic tray delayed settle')

def curves(obj):
    ad = obj.animation_data
    if not ad or not ad.action: return []
    return [fc for l in ad.action.layers for st in l.strips for bag in st.channelbags
            if bag.slot_handle == ad.action_slot_handle for fc in bag.fcurves]

def offset_curve(obj, path, axis, delta):
    found = False
    for fc in curves(obj):
        if fc.data_path == path and fc.array_index == axis:
            found = True
            for key in fc.keyframe_points:
                key.co.y += delta; key.handle_left.y += delta; key.handle_right.y += delta
            fc.update()
    if not found: getattr(obj,path)[axis] += delta

for fc in curves(tray):
    for key in fc.keyframe_points:
        key.interpolation='BEZIER'
        key.handle_left_type=key.handle_right_type='AUTO_CLAMPED'

# Reuse the approved animation with local offsets appropriate for the new support.
tip = bpy.data.objects['SHOT05_LooseTip_Teal']
old_z = tip.location.z
old_angles = tip.rotation_euler.copy()
tip.parent = tray
tip.matrix_parent_inverse = Matrix.Identity(4)
tip.location.x, tip.location.y = -.023, .005
floor_z = (.00888812 - minimum.z) * scale
# Seat the tip against the sloping inner wall. Its measured surface normal
# faces the camera; a flat tip on the deep floor disappears behind the rim.
offset_curve(tip, 'location', 2, .012786270924657584 - old_z)
for axis, angle in enumerate((.6607363820075989, -.5232524871826172, 1.3876581192016602)):
    offset_curve(tip, 'rotation_euler', axis, angle-old_angles[axis])
wand = bpy.data.objects['SHOT05_CatEyeMagnet']
wand.location.x, wand.location.y = -.052, -.078
offset_curve(wand, 'rotation_euler', 2, math.radians(-8)-wand.rotation_euler.z)

tray['source_asset'] = linked.name
tray['placement_note'] = '80mm long uniform-scale leaf bowl. Teal tip inside; magnet on podium beside bowl.'
tray['reaction_delay_frames'] = 1
tray['first_hop_mm'] = .25
s['community_assets_status'] = 'Approved tray integrated; glass cup source acquired for separate brush-holder integration.'
s.render.use_persistent_data = False
s.render.filepath = '//../renders/shot5_polish_finale_v004/production/frame_'
s.frame_set(480)
bpy.context.view_layer.update()
for obj in bpy.context.selected_objects: obj.select_set(False)
tray.select_set(True)
bpy.context.view_layer.objects.active = tray
txt = bpy.data.texts.get('SHOT05_README')
if txt:
    txt.write('\nCOMMUNITY v004: approved Santiago Adrio leaf bowl, uniformly scaled to 80 mm. Teal tip leans inside; magnetic wand is beside it. The acquired glass cup is integrated by the separate brush-holder script.\n')
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_as_mainfile(filepath=str(SCENE))
(OUT/'tray_integration.json').write_text(json.dumps({
    'scene':str(SCENE), 'asset_library':str(LIBRARY), 'uniform_scale':scale,
    'tray_location':list(tray.location),'tray_rotation_z_degrees':-18,
    'floor_above_tray_origin_m':floor_z, 'tip_parent':tip.parent.name,
    'glass_imported':False},indent=2))
print('SHOT5_COMMUNITY_TRAY_SAVED',str(SCENE),flush=True)
