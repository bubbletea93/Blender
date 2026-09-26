"""Build Shot 4 (frames 285-375) from linked production assets.

Output:    scenes/gel_polish_lapohka_shot4_285_375.blend
Reference: references/lapohka_3d_motion_shots/Lapohka 3D Motion - Shot 4 (f285-375).mp4

Designed to run headless so it never touches a live session:

    blender -b --factory-startup --python scripts/build_lapohka_shot4.py

The reference is an extreme macro on a spinning can that decelerates into a
tilted hero hold, unrolls upright, then drops out of frame while the next
flavour rises in behind it. Every timing below is measured off the extracted
reference frames; see notes/lapohka_shot4_f285-375_motion_breakdown.md.
"""
import bpy
import math
from pathlib import Path
from mathutils import Matrix, Vector, Quaternion

ROOT = Path('C:/Users/danht/Documents/GitHub/Blender')
DEST = ROOT / 'scenes/gel_polish_lapohka_shot4_285_375.blend'
PREFIX = 'SHOT04_285_375'
F_START, F_END = 285, 375

# ---------------------------------------------------------------- clean scene
scene = bpy.data.scenes.new('SHOT04_Macro_285_375')
bpy.context.window.scene = scene
for old in [s for s in bpy.data.scenes if s is not scene]:
    bpy.data.scenes.remove(old)
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for col in list(bpy.data.collections):
    bpy.data.collections.remove(col)
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=False, do_recursive=True)


def collection(suffix, parent=None):
    col = bpy.data.collections.new(PREFIX + '_' + suffix)
    (parent or scene.collection).children.link(col)
    return col


root = collection('MASTER')
product_col = collection('PRODUCT', root)
camera_col = collection('CAMERA', root)
env_col = collection('ENV', root)
light_col = collection('LIGHTS', root)


def empty(suffix, col, parent=None):
    obj = bpy.data.objects.new(PREFIX + '_' + suffix, None)
    col.objects.link(obj)
    obj.parent = parent
    obj.empty_display_size = .015
    return obj


def load_collection(path, name, target, override=False):
    with bpy.data.libraries.load(str(ROOT / path), link=True) as (src, dst):
        dst.collections = [name]
    linked = dst.collections[0]
    target.children.link(linked)
    if not override:
        return linked
    local = linked.override_hierarchy_create(scene, bpy.context.view_layer, do_fully_editable=True)
    if linked.name in target.children:
        target.children.unlink(linked)
    if local.name not in target.children:
        target.children.link(local)
    return local


# ------------------------------------------------------------------- product
# Offsets carried over from Shot 3: they re-centre the linked bottle on its rig.
Z_BODY = .0221898276 - .050536156
CAP_LOC = (.005192914, -.0000177546, .074072212 - .050536156)
VISIBLE = {'Housing', 'Cap', 'FrontLens', 'Lacquer'}
RENAME = {'Housing': 'BottleBody', 'Cap': 'OldCap', 'FrontLens': 'FrontLens', 'Lacquer': 'Lacquer'}


def mount_bottle(tag, spin_empty):
    """Override the linked bottle collection and hang it off *spin_empty*."""
    asset = load_collection('assets/products/gel_polish_bottle.blend',
                            'Product_GelPolishBottle', product_col, True)
    asset.name = f'{PREFIX}_Product_GelPolishBottle_{tag}'
    objects = {o.override_library.reference.name: o for o in asset.all_objects if o.override_library}
    for name, obj in objects.items():
        obj.animation_data_clear()
        visible = name in VISIBLE
        obj.hide_render = not visible
        obj.hide_viewport = not visible
        obj.hide_set(not visible)
        if not visible:
            # An unused alternate cap's exact Boolean can crash dependency evaluation.
            for mod in obj.modifiers:
                mod.show_render = False
                mod.show_viewport = False
            continue
        obj.parent = spin_empty
        obj.matrix_parent_inverse = Matrix.Identity(4)
        obj.rotation_euler = (0, 0, 0)
        obj.scale = (1, 1, 1)
        obj.location = (0, 0, Z_BODY)
        if name in {'FrontLens', 'Lacquer'}:
            # Preserve the linked asset's inverse on save/resync; compensate locally.
            obj.matrix_parent_inverse = obj.override_library.reference.matrix_parent_inverse.copy()
            obj.location = Vector((0, 0, Z_BODY)) - obj.matrix_parent_inverse.translation
        if name == 'Cap':
            obj.location = CAP_LOC
        obj.name = f'{PREFIX}_{tag}_{RENAME[name]}'
    return asset, objects


travel = empty('Travel', product_col)
rock = empty('Rock', product_col, travel)
spin = empty('Spin', product_col, rock)
hero_asset, hero = mount_bottle('HERO', spin)

next_travel = empty('NextTravel', product_col)
next_rock = empty('NextRock', product_col, next_travel)
next_spin = empty('NextSpin', product_col, next_rock)
next_asset, nxt = mount_bottle('NEXT', next_spin)

# ------------------------------------------------------------------ materials
# Champagne metal and front glass stay linked to the approved Shot 2 look; the
# two lacquer shades are local copies so the shot can retint without touching
# the asset, exactly as Shot 3 does.
shot2 = ROOT / 'scenes/gel_polish_lapohka_shot2_97_198.blend'
with bpy.data.libraries.load(str(shot2), link=True) as (src, dst):
    dst.materials = ['SHOT02_57_96_MAT_OldCap_Champagne',
                     'SHOT02_57_96_MAT_FrontLens_Glass',
                     'SHOT02_FUTURE_B06_MAT_Lacquer_GOLDEN_OCHRE',
                     'SHOT02_FUTURE_B01_MAT_Lacquer_CORAL']
gold, glass, ochre_src, coral_src = dst.materials


def retint(source, name, base, band, bsdf_base, roughness):
    """Local copy of a linked lacquer, keeping its procedural cat-eye shader."""
    mat = source.copy()
    mat.name = f'{PREFIX}_MAT_{name}'
    mat.animation_data_clear()
    if mat.node_tree:
        mat.node_tree.animation_data_clear()
        for node in mat.node_tree.nodes:
            if node.type == 'RGB':
                if node.name.startswith('Base Color'):
                    node.outputs[0].default_value = (*base, 1)
                elif node.name.startswith('Band Color'):
                    node.outputs[0].default_value = (*band, 1)
            if node.type == 'BSDF_PRINCIPLED':
                node.inputs['Base Color'].default_value = (*bsdf_base, 1)
                node.inputs['Roughness'].default_value = roughness
    return mat


# Hero reads as the reference's citrus can; the incoming bottle as its melon.
# The shades run dark: the dome is a glossy mirror, so under a high-key surround
# only a deeply saturated base survives the reflected white.
hero_lacquer = retint(ochre_src, 'Lacquer_CitronPeel',
                      (.46, .260, .008), (.95, .70, .075), (.50, .29, .014), .11)
next_lacquer = retint(coral_src, 'Lacquer_MelonFlesh',
                      (.62, .020, .030), (.95, .080, .080), (.66, .028, .036), .13)

for objects, lacquer in ((hero, hero_lacquer), (nxt, next_lacquer)):
    for name, material in [('Housing', gold), ('Cap', gold), ('FrontLens', glass), ('Lacquer', lacquer)]:
        for slot in objects[name].material_slots:
            slot.link = 'OBJECT'
            slot.material = material

# ---------------------------------------------------------------- environment
backdrop = load_collection('assets/environments/studio_backdrop.blend',
                           'Studio_Backdrop', env_col, True)
backdrop.name = PREFIX + '_Studio_Backdrop'

sweep = bpy.data.materials.new(PREFIX + '_MAT_Backdrop_WarmSweep')
sweep.use_nodes = True
nt = sweep.node_tree
nt.nodes.remove(nt.nodes['Principled BSDF'])
# Sampling the reference's background corners gives warm peach across the top
# falling to a mid neutral grey at the lower right, the boundary running
# diagonally. The camera sits on +X, so world +Y is screen-right and +Z is
# screen-up; Generated coordinates normalise the cove to 0-1, and the camera
# sees roughly Y 0.33-0.67 and Z 0-0.26 of it, which is what these coefficients
# are fitted to. Object-space coordinates are deliberately avoided: the gradient
# has to stay locked to the cove so it rolls with the camera, as it does in the
# reference, which rules out screen-space Window coordinates.
tex_co = nt.nodes.new('ShaderNodeTexCoord')
sep = nt.nodes.new('ShaderNodeSeparateXYZ')
mul_y = nt.nodes.new('ShaderNodeMath')
mul_y.operation = 'MULTIPLY'
mul_y.inputs[1].default_value = 1.45
mul_z = nt.nodes.new('ShaderNodeMath')
mul_z.operation = 'MULTIPLY'
mul_z.inputs[1].default_value = -3.53
add = nt.nodes.new('ShaderNodeMath')
add.operation = 'ADD'
fac = nt.nodes.new('ShaderNodeMath')
fac.operation = 'ADD'
fac.inputs[1].default_value = .27
ramp = nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.interpolation = 'B_SPLINE'
ramp.color_ramp.elements[0].position = .02
ramp.color_ramp.elements[0].color = (2.10, 1.22, .68, 1)   # warm peach, top of frame
ramp.color_ramp.elements[1].position = .98
ramp.color_ramp.elements[1].color = (.30, .295, .305, 1)   # mid neutral, lower right
mid = ramp.color_ramp.elements.new(.50)
mid.color = (1.05, .72, .55, 1)
nt.links.new(tex_co.outputs['Generated'], sep.inputs['Vector'])
nt.links.new(sep.outputs['Y'], mul_y.inputs[0])
nt.links.new(sep.outputs['Z'], mul_z.inputs[0])
nt.links.new(mul_y.outputs[0], add.inputs[0])
nt.links.new(mul_z.outputs[0], add.inputs[1])
nt.links.new(add.outputs[0], fac.inputs[0])
nt.links.new(fac.outputs[0], ramp.inputs['Fac'])

# The sweep is 1.3 m off and permanently out of focus, so drive it emissively -
# the gradient then reads exactly as authored instead of falling off with the
# inverse square. It is split by Is Camera Ray: bright to the lens so the
# background is genuinely high-key, but a fraction of that to every other ray.
# Without the split, a 360 degree emissive cove turns the lacquer dome into a
# mirror of white and the shade washes out completely.
cam_emit = nt.nodes.new('ShaderNodeEmission')
cam_emit.inputs['Strength'].default_value = 1.00
env_emit = nt.nodes.new('ShaderNodeEmission')
env_emit.inputs['Strength'].default_value = .14
path = nt.nodes.new('ShaderNodeLightPath')
mix_sweep = nt.nodes.new('ShaderNodeMixShader')
nt.links.new(ramp.outputs['Color'], cam_emit.inputs['Color'])
nt.links.new(ramp.outputs['Color'], env_emit.inputs['Color'])
nt.links.new(path.outputs['Is Camera Ray'], mix_sweep.inputs[0])
nt.links.new(env_emit.outputs[0], mix_sweep.inputs[1])
nt.links.new(cam_emit.outputs[0], mix_sweep.inputs[2])
nt.links.new(mix_sweep.outputs[0], nt.nodes['Material Output'].inputs['Surface'])
for idx, node in enumerate(nt.nodes):
    node.location = ((idx % 5) * 230, -(idx // 5) * 240)

for obj in list(backdrop.all_objects):
    if 'Lavender' in obj.name:
        obj.hide_render = True
        obj.hide_viewport = True
        obj.hide_set(True)
        continue
    obj.name = PREFIX + '_StudioBackdrop'
    # The asset's cove floor sits at z=-0.012, but this rig centres the bottle on
    # the origin, which would leave the product buried under the floor and the
    # camera looking out under the sweep at the bare HDRI. Scale the cove up and
    # drop it well below the product: it then fills frame as pure defocused
    # background, which is all the reference ever shows.
    obj.scale = (1.625, 1.625, 1.625)
    obj.location = (.006, .003, -.110)
    for slot in obj.material_slots:
        slot.link = 'OBJECT'
        slot.material = sweep

# World stays a plain link, per the repo's link-vs-override rule. The HDRI it
# references remains external at textures/hdris/studio_environment.hdr.
with bpy.data.libraries.load(str(ROOT / 'assets/environments/studio_environment_world.blend'), link=True) as (src, dst):
    dst.worlds = ['Studio_Environment_HDRI']
scene.world = dst.worlds[0]

# -------------------------------------------------------------------- lights


def point_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


AIM = (0, 0, -.026)                         # centre of the lacquer disc
lights = load_collection('assets/lighting/three_point_studio.blend',
                         'Lights_ThreePoint_Studio', light_col, True)
lights.name = PREFIX + '_Lights_ThreePoint_Studio'
rig_lights = [o for o in list(lights.all_objects) if o and o.type == 'LIGHT']

# High-key daylight: broad warm key from screen-left (-Y), cool ambient fill from
# screen-right, and narrow strips that draw the gold rim's long speculars.
SPECS = [
    ('KeySoftbox',   (.30, -.34,  .22), 3.20, (1.00, .93, .82), .34, .34, AIM),
    ('AmbientFill',  (.16,  .42,  .10), 0.45, (.84, .89, 1.00), .50, .50, AIM),
    ('EdgeStripL',   (.15, -.13,  .00), 0.70, (1.00, .96, .90), .010, .22, AIM),
    ('EdgeStripR',   (.12,  .15,  .00), 0.34, (.94, .97, 1.00), .010, .22, AIM),
    ('TopKiss',      (.08,  .00,  .17), 0.55, (1.00, .91, .80), .04, .04, AIM),
    ('BackdropWash', (.02, -.30,  .30), 1.10, (1.00, .88, .74), .35, .35, (-.32, .04, .12)),
]
for i, (name, loc, energy, color, sx, sy, aim) in enumerate(SPECS):
    if i < len(rig_lights):
        obj = rig_lights[i]
        obj.data = obj.data.copy()          # local data for shot-specific edits
    else:
        obj = bpy.data.objects.new(PREFIX + '_' + name,
                                   bpy.data.lights.new(PREFIX + '_' + name + '_DATA', 'AREA'))
        light_col.objects.link(obj)
    obj.animation_data_clear()
    obj.parent = None
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.name = PREFIX + '_' + name
    obj.hide_render = False
    obj.hide_viewport = False
    obj.hide_set(False)
    obj.location = loc
    obj.data.name = PREFIX + '_' + name + '_DATA'
    obj.data.type = 'AREA'
    obj.data.energy = energy
    obj.data.color = color
    obj.data.shape = 'RECTANGLE'
    obj.data.size = sx
    obj.data.size_y = sy
    point_at(obj, aim)
for extra in rig_lights[len(SPECS):]:
    extra.hide_render = True
    extra.hide_set(True)

# -------------------------------------------------------------------- camera
focus = empty('FocusTarget', camera_col)
focus.location = (.021, 0, -.026)           # front face of the lacquer disc

cam = bpy.data.objects.new(PREFIX + '_Camera', bpy.data.cameras.new(PREFIX + '_Camera_DATA'))
camera_col.objects.link(cam)
scene.camera = cam
cam.data.lens = 58
cam.data.sensor_width = 36
cam.data.clip_start = .001
cam.data.clip_end = 20
cam.data.dof.use_dof = True
cam.data.dof.focus_object = focus
cam.data.dof.aperture_fstop = 13.0

# The reference can is a slim cylinder that overfills the frame throughout; this
# product is a 44 mm lacquer disc on a 102 mm bottle. To land the same beats the
# macro end is pitched so the disc overfills the frame, and the shot opens up on
# the reference's own unroll beat (f336-348) to the product-legible framing that
# the reference reaches at its upright hold.
D_TIGHT = .120                              # disc slightly over-fills the frame
D_WIDE = .178                               # disc plus rim and cap base in frame


def key_camera(frame, dist, height, roll_deg, aim_z):
    """Place the camera on +X looking at the bottle, rolled about its view axis.

    Roll is applied as an explicit quaternion rather than a Track To constraint:
    a Track To would cancel the roll, which is the whole point of this shot.
    """
    cam.location = (dist, 0, height)
    look = (Vector((0, 0, aim_z)) - cam.location).to_track_quat('-Z', 'Y')
    cam.rotation_mode = 'QUATERNION'
    cam.rotation_quaternion = look @ Quaternion((0, 0, 1), math.radians(roll_deg))
    cam.keyframe_insert('location', frame=frame)
    cam.keyframe_insert('rotation_quaternion', frame=frame)


# Screen roll measured off the reference: a nervous ~56 deg diagonal that holds
# dead still f322-336, then unrolls to level by f348 and stays there.
# Roll is the NEGATED measured tilt (tilt is signed from vertical, roll is
# positive when the subject's top leans right) - the f337-375 values come
# straight from the measurement, so watch that sign when re-deriving them.
def lerp(a, b, t):
    return a + (b - a) * t


CAM_KEYS = [
    (285, D_TIGHT * .985, 41.0, -.026),
    (288, D_TIGHT * .990, 37.0, -.026),
    (292, D_TIGHT * .995, 50.0, -.026),
    (296, D_TIGHT * 1.00, 57.0, -.026),
    (302, D_TIGHT * 1.00, 55.0, -.026),
    (310, D_TIGHT * 1.01, 57.0, -.026),
    (318, D_TIGHT * 1.01, 55.0, -.026),
    (322, D_TIGHT * 1.02, 56.0, -.026),
    (336, D_TIGHT * 1.02, 56.0, -.026),
    (338, lerp(D_TIGHT, D_WIDE, .12), 41.0, -.026),
    (340, lerp(D_TIGHT, D_WIDE, .27), 35.0, -.026),
    (342, lerp(D_TIGHT, D_WIDE, .45), 20.4, -.025),
    (344, lerp(D_TIGHT, D_WIDE, .63), 10.6, -.024),
    (346, lerp(D_TIGHT, D_WIDE, .80), 6.9, -.023),
    (348, lerp(D_TIGHT, D_WIDE, .92), 1.2, -.022),
    (352, D_WIDE * 1.00, 1.8, -.021),
    (357, D_WIDE * 1.01, 0.1, -.021),
    (363, D_WIDE * 1.02, 0.3, -.020),
    (370, D_WIDE * 1.03, 0.0, -.020),
    (375, D_WIDE * 1.03, 0.0, -.020),
]
for frame, dist, roll, aim_z in CAM_KEYS:
    key_camera(frame, dist, aim_z, roll, aim_z)   # level camera: height == aim

# --------------------------------------------------------------- bottle motion
REST = 0.0          # hero spin angle at rest, degrees
SPIN_DIR = -1.0     # label sweeps left-to-right on screen, as in the reference


def spin_deg(frame):
    """Fast decelerating spin -> damped overshoot -> slow hold drift -> exit spin.

    Fitted to the reference beats: the surface smears solid until ~f292, reads
    by f296, overshoots at f302, swings back at f313 and is at rest by f321.
    The reference can hides its silhouette change behind a constant cylinder;
    this disc cannot, so the run-up is held to 2.2 turns and spent almost
    entirely in f285-289, where the 180 deg shutter smears it away. The settle
    amplitude is likewise halved so the disc never turns fully edge-on.
    """
    t = frame - F_START
    remaining = (780.0 * math.exp(-t / 3.5)
                 + 26.0 * math.exp(-t / 16.8) * math.cos(2 * math.pi * t / 22.0 + 1.428))
    drift = 8.0 * min(1.0, max(0.0, (frame - 336) / 30.0))
    exit_spin = 0.0 if frame <= 364 else 3.0 * (frame - 364) ** 1.7
    return REST + SPIN_DIR * (-remaining + drift + exit_spin)


def fcurves_of(obj):
    """Blender 5 keeps F-curves inside slotted action layers, not action.fcurves."""
    action = obj.animation_data.action
    if hasattr(action, 'fcurves'):
        return list(action.fcurves)
    out = []
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                out.extend(bag.fcurves)
    return out


def bake_linear(obj):
    for fcurve in fcurves_of(obj):
        for kp in fcurve.keyframe_points:
            kp.interpolation = 'LINEAR'


for frame in range(F_START, F_END + 1):
    spin.rotation_euler = (0, 0, math.radians(spin_deg(frame)))
    spin.keyframe_insert('rotation_euler', frame=frame)
bake_linear(spin)

# Depth lean: the reference can noses toward the lens during the diagonal hold
# and flattens out as it comes upright.
for frame, lean in [(285, 11.0), (300, 10.0), (336, 9.5), (344, 6.0), (352, 2.5),
                    (363, 2.0), (370, 2.0), (375, 2.0)]:
    rock.rotation_euler = (0, math.radians(lean), 0)
    rock.keyframe_insert('rotation_euler', frame=frame)

# Hero travel: parked through the hold, then it drops and recedes out of frame.
for frame, loc in [(285, (0, 0, .001)), (310, (0, 0, .000)), (336, (0, 0, -.001)),
                   (352, (0, 0, .001)), (364, (0, 0, .000)), (366, (0, 0, -.003)),
                   (368, (-.004, 0, -.012)), (370, (-.026, 0, -.062)),
                   (372, (-.070, 0, -.150)), (375, (-.110, 0, -.260))]:
    travel.location = loc
    travel.keyframe_insert('location', frame=frame)

# Incoming bottle: hidden until the hero clears, then it rises past the lens.
next_rock.rotation_euler = (0, math.radians(3.0), 0)
for frame, loc in [(369, (-.010, .002, -.200)), (371, (.008, .002, -.110)),
                   (373, (.030, .002, -.020)), (375, (.048, .002, .030))]:
    next_travel.location = loc
    next_travel.keyframe_insert('location', frame=frame)
for frame in range(369, F_END + 1):
    # sweeps round to face the lens as the shot cuts, mirroring the reference's
    # incoming can arriving already turned toward camera
    next_spin.rotation_euler = (0, 0, math.radians(170.0 - 28.0 * (frame - 369)))
    next_spin.keyframe_insert('rotation_euler', frame=frame)
bake_linear(next_spin)
for obj in [o for o in next_asset.all_objects if not o.hide_render]:
    for frame, hidden in [(F_START, True), (368, True), (369, False), (F_END, False)]:
        obj.hide_render = hidden
        obj.hide_viewport = hidden
        obj.keyframe_insert('hide_render', frame=frame)
        obj.keyframe_insert('hide_viewport', frame=frame)

# ------------------------------------------------------------------- settings
scene.frame_start, scene.frame_end = F_START, F_END
scene.render.fps, scene.render.fps_base = 30, 1
scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
scene.render.resolution_percentage = 100
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.preview_samples = 16
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 12
scene.cycles.transmission_bounces = 10
scene.cycles.transparent_max_bounces = 10
scene.render.use_motion_blur = True
scene.render.motion_blur_shutter = .62        # the reference smears past 180 deg
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.filepath = '//../renders/gel_polish_lapohka_shot4_285_375/shot4_'
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Base Contrast'   # high-key: keep the pastels
scene.view_settings.exposure = -.15           # high-key, unlike Shot 3's black stage
scene.render.film_transparent = False
scene.unit_settings.system = 'METRIC'
scene.unit_settings.length_unit = 'METERS'
scene['reference'] = '//../references/lapohka_3d_motion_shots/Lapohka 3D Motion - Shot 4 (f285-375).mp4'

for frame, name in [(285, 'CUT - SPINNING MACRO'), (296, 'LABEL RESOLVES'),
                    (302, 'SETTLE OVERSHOOT'), (322, 'DIAGONAL HERO HOLD'),
                    (336, 'UNROLL BEGINS'), (348, 'UPRIGHT HERO'),
                    (365, 'DROP OUT'), (369, 'NEXT SHADE RISES')]:
    scene.timeline_markers.new(name, frame=frame)

notes = bpy.data.texts.new(PREFIX + '_REFERENCE_NOTES')
notes.write(
    'SHOT 4 / FRAMES 285-375 / 30 FPS\n\n'
    'Recreation of the supplied Lapohka macro label shot using the production gel-polish bottle.\n'
    'Product mesh: two linked library overrides of assets/products/gel_polish_bottle.blend\n'
    '  HERO - citron lacquer, on Travel / Rock / Spin\n'
    '  NEXT - melon lacquer, on NextTravel / NextRock / NextSpin, hidden until f369\n'
    'Champagne and glass materials link to Shot 2. Both lacquers are shot-local retints\n'
    'of linked Shot 2 shades, keeping the original procedural cat-eye shader.\n'
    'Backdrop is linked and overridden, with a shot-local warm gradient on OBJECT-linked slots.\n'
    'World is a plain link; the HDRI stays external and is not packed.\n\n'
    'MOTION\n'
    '  285-296  fast spin, decelerating hard; the label smears solid then resolves\n'
    '  296-321  damped settle - overshoot at f302, counter-swing at f313, at rest by f321\n'
    '  322-336  dead hold on the 56 deg diagonal\n'
    '  336-348  camera unrolls 56 -> 0 deg and eases back slightly\n'
    '  348-364  upright hero, slow residual label drift\n'
    '  364-371  hero drops and recedes out of frame, spin accelerating\n'
    '  369-375  next shade rises into frame, still moving as the shot ends\n\n'
    'The screen tilt is CAMERA ROLL, not object tilt - the background rolls with it in the\n'
    'reference. Roll is keyed as an explicit quaternion; a Track To constraint would cancel it.\n'
    'Spin is baked per frame with linear interpolation because the deceleration curve matters.\n\n'
    'Use Camera view. Render range 285-375. Output 1920x1080, Cycles 128 samples, 180 deg shutter.\n')
builder = bpy.data.texts.new('BUILD_LAPOHKA_SHOT4.PY')
builder.write(Path(__file__).read_text(encoding='utf-8'))

for lib in bpy.data.libraries:
    lib.filepath = bpy.path.relpath(lib.filepath, start=str(DEST.parent))

scene.frame_set(322)
bpy.context.view_layer.update()
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'OPTIX'
    prefs.get_devices()
    for dev in prefs.devices:
        dev.use = dev.type == 'OPTIX'
    scene.cycles.device = 'GPU'
except Exception:
    scene.cycles.device = 'CPU'

DEST.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
print('SHOT4_READY', DEST)
