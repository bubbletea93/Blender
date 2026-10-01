"""Add a second, blue color spin to the Shot 1 reference scene before the drop.

Reads scenes/gel_polish_lapohka_shot1_0_56_reference_v002.blend and saves
scenes/gel_polish_lapohka_shot1_0_82_reference_v003.blend (v002 is untouched).
Blender --background <v002> --python this.py

The rise, first spin, coral-to-green cut (f30) and green hold keep their keys.
The first spin is repeated 26 frames later with a green-to-blue cut at f56,
while the bottle faces away (540 deg), matching the f30 cut at 180 deg.
The original hold-to-drop keys (f45-56) move to f71-82, so the drop is unchanged.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'gel_polish_lapohka_shot1_0_56_reference_v002.blend'
DEST = ROOT / 'scenes/gel_polish_lapohka_shot1_0_82_reference_v003.blend'
OUT = ROOT / 'renders/shot1_reference_rebuild'
SHIFT = 26
END = 56 + SHIFT
TURN = 2 * math.pi
CORAL = (.30, .095, .068, 1)
OLIVE = (.115, .17, .062, 1)
BLUE = (.075, .13, .25, 1)

assert bpy.data.filepath.endswith(SOURCE), bpy.data.filepath
s = bpy.context.scene
assert (s.frame_start, s.frame_end) == (0, 56)


def fcurves(idb):
    return [fc for layer in idb.animation_data.action.layers for strip in layer.strips
            for bag in strip.channelbags for fc in bag.fcurves]


def fcurve(idb, path, index=0):
    return next(fc for fc in fcurves(idb) if fc.data_path == path and fc.array_index == index)


def remap(fc, keep, copies=(), dy=0.0):
    """Rebuild fc from its own keys: keep frames as-is, copy (src, dst) with a value offset."""
    src = {round(k.co.x): dict(y=k.co.y, interp=k.interpolation, left=k.handle_left_type,
                               right=k.handle_right_type,
                               slope_l=(k.co.y - k.handle_left.y) / max(k.co.x - k.handle_left.x, 1e-6),
                               slope_r=(k.handle_right.y - k.co.y) / max(k.handle_right.x - k.co.x, 1e-6))
           for k in fc.keyframe_points}
    plan = [(f, f, 0.0) for f in keep] + [(a, b, dy) for a, b in copies]
    plan.sort(key=lambda p: p[1])
    fc.keyframe_points.clear()
    fc.keyframe_points.add(len(plan))
    frames = [dst for _, dst, _ in plan]
    for i, (a, b, offset) in enumerate(plan):
        k, d = fc.keyframe_points[i], src[a]
        k.co = (b, d['y'] + offset)
        k.interpolation = d['interp']
        k.handle_left_type, k.handle_right_type = d['left'], d['right']
        if d['left'] == 'FREE':
            # Keep the authored slope; handle reach follows the new neighbour spacing.
            left = (b - frames[i - 1]) / 3 if i else 1
            right = (frames[i + 1] - b) / 3 if i < len(frames) - 1 else 1
            k.handle_left = (b - left, k.co.y - left * d['slope_l'])
            k.handle_right = (b + right, k.co.y + right * d['slope_r'])
    fc.update()


def switch(fc, table):
    fc.keyframe_points.clear()
    fc.keyframe_points.add(len(table))
    for k, (f, v) in zip(fc.keyframe_points, table):
        k.co = (f, v)
        k.interpolation = 'CONSTANT'
    fc.update()


spin, tilt, travel = (bpy.data.objects[n] for n in ('SHOT01_Spin', 'SHOT01_Tilt', 'SHOT01_Travel'))
spin_copy = [(f, f + SHIFT) for f in (23, 27, 30, 33, 37, 45, 56)]
remap(fcurve(spin, 'rotation_euler', 2), keep=(0, 12, 23, 27, 30, 33, 37, 45), copies=spin_copy, dy=TURN)
remap(fcurve(tilt, 'rotation_euler', 0), keep=(0, 12, 22, 28, 34, 43),
      copies=[(f, f + SHIFT) for f in (22, 28, 34, 43, 47, 56)])
remap(fcurve(tilt, 'rotation_euler', 1), keep=(0, 12, 25, 33, 44),
      copies=[(f, f + SHIFT) for f in (25, 33, 44, 56)])
remap(fcurve(travel, 'location', 2), keep=(0, 4, 9, 12, 19, 26, 36),
      copies=[(f, f + SHIFT) for f in (26, 36, 45, 47, 50, 53, 56)])
remap(fcurve(travel, 'location', 1), keep=(0, 12, 26, 38),
      copies=[(f, f + SHIFT) for f in (26, 38, 47, 56)])

# Lacquer shades: A coral, B blue, C green. SwapBC=1 shows green; back to 0 reveals SwapMix (blue).
lacquer = bpy.data.materials['SHOT01_Coral_to_Emerald']
lacquer.name = 'SHOT01_Coral_Emerald_Blue'
tree = lacquer.node_tree
switch(fcurve(tree, 'nodes["SwapMix"].inputs[0].default_value'), [(0, 0), (29, 0), (30, 1), (END, 1)])
switch(fcurve(tree, 'nodes["SwapBC"].inputs[0].default_value'),
       [(0, 0), (29, 0), (30, 1), (55, 1), (56, 0), (END, 0)])

wall = bpy.data.materials['SHOT01_Coral_to_Olive_Backdrop']
wall.name = 'SHOT01_Coral_Olive_Blue_Backdrop'
for channel in range(4):
    fc = fcurve(wall.node_tree, 'nodes["Principled BSDF"].inputs[0].default_value', channel)
    switch(fc, [(0, CORAL[channel]), (29, CORAL[channel]), (30, OLIVE[channel]),
                (55, OLIVE[channel]), (56, BLUE[channel]), (END, BLUE[channel])])

s.frame_end = END
s.name = 'SHOT01_ReferenceRiseDoubleSpin_0_82'
for old in list(s.timeline_markers):
    s.timeline_markers.remove(old)
for label, frame in [('RISE FROM BELOW', 0), ('RISE APEX', 12), ('SPIN', 24), ('SHADE SWITCH', 30),
                     ('GREEN HERO', 38), ('BLUE SPIN', 50), ('BLUE SWITCH', 56), ('BLUE HERO', 64),
                     ('DROP OUT', 73), ('CUT TO LANDING', END)]:
    s.timeline_markers.new(label, frame=frame)
note = bpy.data.texts['SHOT01_REFERENCE_README']
note.clear()
note.write('SHOT 1 / 0-82 at 30fps\nRise 1-12; hold; first revolution 23-37 with coral-to-green cut 30; '
           'green hold; second revolution 49-63 with green-to-blue cut 56; blue hold; drop 71-82 '
           '(same keys as the v002 drop at 45-56).\n'
           'Direct editable animation: SHOT01_Travel / SHOT01_Tilt / SHOT01_Spin.\n')

# Validation: spin never reverses, both cuts happen back-facing, shades and framing hold.
spin_fc = fcurve(spin, 'rotation_euler', 2)
samples = [spin_fc.evaluate(f / 10) for f in range(0, END * 10 + 1)]
reversal = min(b - a for a, b in zip(samples, samples[1:]))
assert reversal > -1e-4, f'spin reverses by {math.degrees(reversal):.3f} deg'
cut_angles = {f: math.degrees(spin_fc.evaluate(f)) % 360 for f in (30, 56)}
assert all(abs(a - 180) < 1 for a in cut_angles.values()), cut_angles


def shade(frame):
    mix = fcurve(tree, 'nodes["SwapMix"].inputs[0].default_value').evaluate(frame)
    bc = fcurve(tree, 'nodes["SwapBC"].inputs[0].default_value').evaluate(frame)
    return 'green' if bc > .5 else ('blue' if mix > .5 else 'coral')


shades = {f: shade(f) for f in range(END + 1)}
assert all(shades[f] == 'coral' for f in range(30)) and all(shades[f] == 'green' for f in range(30, 56))
assert all(shades[f] == 'blue' for f in range(56, END + 1))

housing = bpy.data.objects['Housing']
visible = [o for o in [housing] + list(housing.children_recursive) if o.type == 'MESH' and not o.hide_render]
bounds = []
for f in range(END + 1):
    s.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    pts = [world_to_camera_view(s, s.camera, o.evaluated_get(dg).matrix_world @ Vector(p))
           for o in visible for p in o.evaluated_get(dg).bound_box]
    bounds.append({'frame': f, 'xmin': min(p.x for p in pts), 'xmax': max(p.x for p in pts),
                   'ymin': min(p.y for p in pts), 'ymax': max(p.y for p in pts)})
assert bounds[0]['ymax'] < 0 and bounds[END]['ymax'] < 0, (bounds[0], bounds[END])
assert all(0 < b['ymin'] < b['ymax'] < 1 and 0 < b['xmin'] < b['xmax'] < 1 for b in bounds[9:47 + SHIFT])
s.frame_set(18)

bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
report = {'scene': str(DEST), 'range': [0, END], 'fps': s.render.fps,
          'cuts': {'coral_to_green': 30, 'green_to_blue': 56}, 'cut_spin_angles_deg': cut_angles,
          'min_spin_step_deg_per_0.1f': math.degrees(reversal),
          'shade_ranges': {'coral': [0, 29], 'green': [30, 55], 'blue': [56, END]},
          'backdrop_rgba': {'coral': CORAL, 'olive': OLIVE, 'blue': BLUE},
          'drop_frames': [45 + SHIFT, END], 'screen_bounds': bounds}
(OUT / 'animation_validation_v003.json').write_text(json.dumps(report, indent=2))
print('SHOT1_BLUE_SPIN_READY', json.dumps({k: v for k, v in report.items() if k != 'screen_bounds'}), flush=True)
