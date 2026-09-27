"""Read-only geometry, staging, and framing checks for the grounded Shot5 finale.

Run with Blender --factory-startup --disable-autoexec --background SCENE --python
this file. The scene is never saved. Deliberate manufactured joins inside each
bottle, rack, and mounted board are excluded; separate assemblies are tested.
"""
import bpy
import hashlib
import itertools
import json
import math
import re
from pathlib import Path

import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(bpy.data.filepath)
VERSION = SOURCE.stem.rsplit('_', 1)[-1] if re.search(r'_v\d+$',SOURCE.stem) else 'current'
OUT = ROOT / ('renders/shot5_brand_collection_' + VERSION)
OUT.mkdir(parents=True, exist_ok=True)
SOURCE_HASH = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
s = bpy.context.scene
HERO = 'SHOT05_Bottle_Assembly'
RACK = 'SHOT05_CollectionRack'
BOARD = 'SHOT05_CollectionSampleBoard'
EPS = 5e-7
BOTTLES = sorted(o.name for o in s.objects if o.name.startswith('SHOT05_CollectionRack_Bottle_'))
NAMES = [HERO, RACK, BOARD] + BOTTLES
SHELF_BOTTLES = [HERO] + BOTTLES
FINAL_FRAMES = {480., 512., 528.}
CONFIG_FAILURES = []
if (s.frame_start, s.frame_end, s.render.fps) != (376, 528, 30):
    CONFIG_FAILURES.append('Expected frames 376–528 at 30 fps')
if len(BOTTLES) != 35:
    CONFIG_FAILURES.append(f'Expected 35 support bottles; found {len(BOTTLES)}')
for name in [HERO, RACK, BOARD]:
    if name not in s.objects:
        raise RuntimeError('Required assembly missing: ' + name)

LAYOUT = {}
for name in BOTTLES:
    match = re.search(r'_Bottle_R(\d+)_C(\d+)_', name)
    if not match:
        CONFIG_FAILURES.append('Unrecognized rack bottle name: ' + name)
        continue
    LAYOUT[name] = {'row': int(match[1]), 'column': int(match[2]),
                    'shade_id': s.objects[name].get('shade_id')}
LAYOUT[HERO] = {key: s.objects[HERO].get(key) for key in ['row', 'column', 'shade_id']}
if not s.objects[HERO].get('on_rack'):
    CONFIG_FAILURES.append('Hero must be tagged on_rack=True')
if LAYOUT[HERO] != {'row': 1, 'column': 3, 'shade_id': 225}:
    CONFIG_FAILURES.append('Hero must occupy row 1, column 3, shade 225')
if {(v['row'], v['column']) for v in LAYOUT.values()} != set(itertools.product(range(1, 7), repeat=2)):
    CONFIG_FAILURES.append('Rack does not contain exactly the full 6 × 6 layout')
if sorted(v['shade_id'] for v in LAYOUT.values() if v['shade_id'] is not None) != list(range(211, 247)):
    CONFIG_FAILURES.append('Collection must contain each shade ID from 211 through 246 once')

removed_objects_still_visible = [o.name for o in s.objects
    if (o.name == 'SHOT05_CeramicPodium' or o.name.startswith('SHOT05_WindowSlat_')
        or o.name == 'SHOT05_ChampagneCyclorama') and not o.hide_render]
floor_candidates = [o.name for o in s.objects if
    o.get('shot5_studio_floor') or o.name == 'SHOT05_GradientStudioSweep'
    or ('floor' in o.name.lower() and not o.hide_render)]
if not floor_candidates:
    CONFIG_FAILURES.append('No identifiable studio floor object')

SAMPLES = set(float(f) for f in range(376, 453)) | FINAL_FRAMES | {460., 470.}
for name in NAMES + ['SHOT05_Bottle_Travel', 'SHOT05_Bottle_Tilt',
                      'SHOT05_StageReveal', 'SHOT05_StageImpact']:
    obj = s.objects.get(name)
    ad = obj.animation_data if obj else None
    if not ad or not ad.action:
        continue
    for layer in ad.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                if bag.slot_handle == ad.action_slot_handle:
                    SAMPLES.update(float(k.co.x) for fc in bag.fcurves
                                   for k in fc.keyframe_points if 376 <= k.co.x <= 528)
contact = sorted(f for f in SAMPLES if 422 <= f <= 462)
SAMPLES = sorted(SAMPLES | {(a + b) / 2 for a, b in zip(contact, contact[1:])})
GEOMETRY_CACHE = {}
PART_CACHE = {}


def owner(ins):
    obj = ins.parent.original if ins.is_instance and ins.parent else ins.object.original
    while obj:
        if obj.name in NAMES:
            return obj.name
        obj = obj.parent
    return None


def capture_part(ins):
    matrix = ins.matrix_world.copy()
    mesh = ins.object.data
    original = ins.object.original
    geometry_id = ('mesh', original.data.as_pointer()) if not original.modifiers else ('object', original.as_pointer())
    geometry_key = (geometry_id, len(mesh.vertices), len(mesh.polygons))
    if geometry_key not in GEOMETRY_CACHE:
        coords = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
        mesh.vertices.foreach_get('co', coords)
        GEOMETRY_CACHE[geometry_key] = (coords.reshape(-1, 3), [tuple(p.vertices) for p in mesh.polygons])
    # Sharing immutable mesh coordinates is safe for these rigid assets. Matrix
    # changes produce separate instances, retaining static collision trees.
    part_key = (original.as_pointer(), geometry_key, tuple(v for row in matrix for v in row))
    if part_key not in PART_CACHE:
        points = [matrix @ Vector(v) for v in ins.object.bound_box]
        PART_CACHE[part_key] = {
            'name': ins.object.name, 'matrix': matrix,
            'geometry': GEOMETRY_CACHE[geometry_key], 'points': points,
            'lo': np.array([min(p[i] for p in points) for i in range(3)]),
            'hi': np.array([max(p[i] for p in points) for i in range(3)]),
            'axes': [matrix.to_3x3().col[i].normalized() for i in range(3)]}
    return PART_CACHE[part_key]


def exact_points(part, inverse=None):
    matrix = np.asarray(inverse @ part['matrix'] if inverse is not None else part['matrix'])
    return part['geometry'][0] @ matrix[:3, :3].T + matrix[:3, 3]


def exact_bounds(part, inverse=None):
    key = tuple(v for row in inverse for v in row) if inverse is not None else 'world'
    if key not in part.setdefault('bounds_cache', {}):
        points = exact_points(part, inverse)
        part['bounds_cache'][key] = (points.min(axis=0), points.max(axis=0))
    return part['bounds_cache'][key]


def mesh_tree(part):
    if 'tree' not in part:
        part['world_vertices'] = [Vector(v) for v in exact_points(part)]
        part['tree'] = BVHTree.FromPolygons(part['world_vertices'], part['geometry'][1], epsilon=0)
    return part['tree']


def boxes_separate(a, b):
    axes = a['axes'] + b['axes'] + [x.cross(y) for x in a['axes'] for y in b['axes']]
    for axis in axes:
        if axis.length_squared < 1e-16:
            continue
        axis.normalize()
        av = [p.dot(axis) for p in a['points']]
        bv = [p.dot(axis) for p in b['points']]
        if min(max(av), max(bv)) - max(min(av), min(bv)) <= EPS:
            return True
    return False


def inside_surface(point, tree):
    direction = Vector((.812381, .427139, .396713)).normalized()
    origin = point.copy()
    hits = 0
    for _ in range(128):
        position, normal, index, distance = tree.ray_cast(origin, direction)
        if position is None:
            return bool(hits % 2)
        hits += 1
        origin = position + direction * 1e-7
    return None


def projected_bounds(scene, depsgraph, parts):
    if not parts:
        return None
    inverse = scene.camera.matrix_world.normalized().inverted()
    projection = scene.camera.calc_matrix_camera(
        depsgraph, x=scene.render.resolution_x, y=scene.render.resolution_y,
        scale_x=scene.render.pixel_aspect_x, scale_y=scene.render.pixel_aspect_y)
    clip_matrix, inv = np.asarray(projection @ inverse), np.asarray(inverse)
    lo, hi = np.array([math.inf] * 3), np.array([-math.inf] * 3)
    for part in parts:
        world = exact_points(part)
        clip = world @ clip_matrix[:, :3].T + clip_matrix[:, 3]
        w = np.where(np.abs(clip[:, 3]) > 1e-12, clip[:, 3], 1e-12)
        ndc = clip[:, :2] / w[:, None] * .5 + .5
        depth = -(world @ inv[2, :3] + inv[2, 3])
        lo = np.minimum(lo, [ndc[:, 0].min(), ndc[:, 1].min(), depth.min()])
        hi = np.maximum(hi, [ndc[:, 0].max(), ndc[:, 1].max(), depth.max()])
    return {'ndc_xmin_xmax_ymin_ymax': [float(lo[0]), float(hi[0]), float(lo[1]), float(hi[1])],
            'camera_depth_min_max_m': [float(lo[2]), float(hi[2])],
            'width_fraction': float(hi[0] - lo[0]), 'height_fraction': float(hi[1] - lo[1]),
            'within_frame': bool(min(lo[:2]) >= -EPS and max(hi[:2]) <= 1 + EPS and lo[2] > 0)}


floor_checks = {n: {'minimum_floor_clearance_m': math.inf, 'frame': None} for n in NAMES}
shelf_checks = {n: {'shelf_top_in_rack_m': float(s.objects[n].get('shelf_top_m', 0)),
                     'minimum_foot_clearance_m': math.inf, 'frame': None} for n in SHELF_BOTTLES}
board_collection = s.objects[BOARD].instance_collection
board_objects = list(board_collection.all_objects) if board_collection else list(s.objects[BOARD].children_recursive)
board_report = {
    'collection': board_collection.name if board_collection else None,
    'library': bpy.path.abspath(board_collection.library.filepath) if board_collection and board_collection.library else None,
    'root_scale': list(s.objects[BOARD].scale),
    'root_rotation_degrees': [math.degrees(v) for v in s.objects[BOARD].rotation_euler],
    'removed_supports_still_present': [o.name for o in board_objects
        if any(t in o.name for t in ['StandingFoot', 'RearSpine', 'GoldFootAccent'])],
    'logo_objects': [o.name for o in board_objects if any(t in o.name.lower() for t in ['logo', 'monogram', 'hangpure'])],
    'cat_eye_materials': [m.name for m in bpy.data.materials if
        m.name.startswith('BOARD_') and ('cat' in m.name.lower() or
        (m.use_nodes and any('cat' in n.name.lower() for n in m.node_tree.nodes)))]}
unknown, intersections, containment = [], [], []
stage_motion, camera_checks, final_framing, final_clearances, hold_bounds = [], {}, {}, {}, {}
candidate_count = obb_count = 0
pair_names = list(itertools.combinations(NAMES, 2))
# Identical rigid poses need only one exact pair test; report repeated overlap
# occurrences with their current frame when a failed result is reused.
PAIR_CACHE = {}
for frame in SAMPLES:
    if float(frame).is_integer() and int(frame) % 5 == 0:
        print('GRADIENT_VALIDATING_FRAME', frame, flush=True)
    s.frame_set(math.floor(frame), subframe=frame - math.floor(frame))
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    for name in ['SHOT05_StageReveal', 'SHOT05_StageImpact']:
        obj = s.objects.get(name)
        if obj and obj.matrix_world.translation.length > EPS:
            stage_motion.append({'frame': frame, 'object': name,
                                 'translation': list(obj.matrix_world.translation)})
    rack_inverse = s.objects[RACK].matrix_world.inverted()
    parts = {n: [] for n in NAMES}
    for ins in deps.object_instances:
        if ins.object.type == 'MESH':
            name = owner(ins)
            if name is not None:
                parts[name].append(capture_part(ins))
    bounds = {}
    for name in NAMES:
        if not parts[name]:
            unknown.append({'frame': frame, 'assembly': name})
            continue
        exact = [exact_bounds(p) for p in parts[name]]
        bounds[name] = (np.min([p[0] for p in exact], axis=0), np.max([p[1] for p in exact], axis=0))
        clearance = float(bounds[name][0][2])
        if clearance < floor_checks[name]['minimum_floor_clearance_m']:
            floor_checks[name].update(minimum_floor_clearance_m=clearance, frame=frame)
        if name in SHELF_BOTTLES:
            foot = min(float(exact_bounds(p, rack_inverse)[0][2]) for p in parts[name])
            foot -= shelf_checks[name]['shelf_top_in_rack_m']
            # Hero approaches from free space. Shelf-plane clearance is only a
            # support criterion from landing onward, not during its route.
            if name != HERO or frame >= 432:
                if foot < shelf_checks[name]['minimum_foot_clearance_m']:
                    shelf_checks[name].update(minimum_foot_clearance_m=foot, frame=frame)
            if name == HERO and frame in FINAL_FRAMES:
                final_clearances[str(frame)] = foot
        if frame == 480:
            hold_bounds[name] = {'min_m': bounds[name][0].tolist(), 'max_m': bounds[name][1].tolist()}
    if frame in {376, 392, 400, 422, 432, 436, 451, 480, 512, 528}:
        forward = s.camera.matrix_world.to_3x3() @ Vector((0, 0, -1))
        camera_checks[str(frame)] = {
            'position': list(s.camera.matrix_world.translation),
            'forward_z': float(forward.z), 'looks_up': bool(forward.z > 0),
            'hero': projected_bounds(s, deps, parts[HERO])}
    if frame in FINAL_FRAMES:
        final_framing[str(frame)] = {
            'display_union': projected_bounds(s, deps, [p for n in NAMES for p in parts[n]]),
            'assemblies': {n: projected_bounds(s, deps, parts[n]) for n in NAMES}}
        if frame == 480:
            board_report['world_location'] = list(s.objects[BOARD].matrix_world.translation)
            inverse = s.objects[BOARD].matrix_world.inverted()
            lo = np.min([exact_bounds(p, inverse)[0] for p in parts[BOARD]], axis=0)
            hi = np.max([exact_bounds(p, inverse)[1] for p in parts[BOARD]], axis=0)
            board_report['unscaled_asset_min_m'] = lo.tolist()
            board_report['unscaled_asset_max_m'] = hi.tolist()
    for name_a, name_b in pair_names:
        if name_a not in bounds or name_b not in bounds:
            continue
        alo, ahi = bounds[name_a]
        blo, bhi = bounds[name_b]
        if np.min(np.minimum(ahi, bhi) - np.maximum(alo, blo)) <= EPS:
            continue
        for a, b in itertools.product(parts[name_a], parts[name_b]):
            if np.min(np.minimum(a['hi'], b['hi']) - np.maximum(a['lo'], b['lo'])) <= EPS:
                continue
            candidate_count += 1
            pair_key = (id(a), id(b))
            if pair_key not in PAIR_CACHE:
                overlap_count, warnings = 0, []
                if not boxes_separate(a, b):
                    obb_count += 1
                    ta, tb = mesh_tree(a), mesh_tree(b)
                    overlap_count = len(ta.overlap(tb))
                    if not overlap_count:
                        for part, other, label in [(a, tb, 'a_inside_b'), (b, ta, 'b_inside_a')]:
                            vertices = part['world_vertices']
                            for index in sorted({0, len(vertices) // 2, len(vertices) - 1}):
                                if inside_surface(vertices[index], other):
                                    warnings.append(label)
                                    break
                PAIR_CACHE[pair_key] = (overlap_count, warnings)
            overlap_count, warnings = PAIR_CACHE[pair_key]
            pair = {'frame': frame, 'a': name_a + '/' + a['name'], 'b': name_b + '/' + b['name']}
            if overlap_count:
                intersections.append(dict(pair, triangle_pairs=overlap_count))
            if warnings:
                containment.append(dict(pair, warnings=warnings))

missing_libraries = []
for lib in bpy.data.libraries:
    path = bpy.path.abspath(lib.filepath, library=lib.parent)
    if not Path(path).is_file():
        missing_libraries.append({'name': lib.name, 'path': path})
missing_images = []
for image in bpy.data.images:
    if image.source != 'FILE' or image.packed_file or image.packed_files or not image.filepath:
        continue
    path = bpy.path.abspath(image.filepath, library=image.library)
    if not Path(path).is_file():
        missing_images.append({'name': image.name, 'path': path})
floor_failures = [n for n, c in floor_checks.items() if c['minimum_floor_clearance_m'] < -EPS]
shelf_failures = [n for n, c in shelf_checks.items() if c['minimum_foot_clearance_m'] < -EPS]
framing_failures = [{'frame': f, 'assembly': n, 'bounds': b}
                    for f, value in final_framing.items() for n, b in value['assemblies'].items()
                    if b is None or not b['within_frame']]
hero_final_failures = [{'frame': f, 'clearance_m': value} for f, value in final_clearances.items()
                       if not -EPS <= value <= .001]
opening_failures = []
opening = camera_checks.get('376.0', camera_checks.get('376', {}))
if not opening.get('looks_up'):
    opening_failures.append('Opening camera does not look upward')
if opening.get('hero') and opening['hero']['height_fraction'] < .65:
    opening_failures.append('Opening hero occupies less than 65% of the frame height')
passed = not any([CONFIG_FAILURES, removed_objects_still_visible, unknown, intersections,
                  containment, stage_motion, floor_failures, shelf_failures, framing_failures,
                  hero_final_failures, opening_failures, missing_images, missing_libraries,
                  board_report['removed_supports_still_present']])
report = {
    'scene': str(SOURCE), 'scene_sha256': SOURCE_HASH, 'passed': passed,
    'frame_count': 153, 'sample_count': len(SAMPLES), 'sampled_frames': SAMPLES,
    'method': 'Every integer frame through settling, all authored physical poses, and contact interval midpoints. '
              'Exact evaluated mesh coordinates establish floor and shelf clearances. Assembly AABB, per-part '
              'AABB and oriented envelope rejection precede exact mesh BVH surface tests and sampled solid '
              'containment checks. Manufactured joins within an assembly and font geometry are excluded. '
              'Read-only; the source scene is not saved.',
    'configuration_failures': CONFIG_FAILURES,
    'removed_objects_still_visible': removed_objects_still_visible,
    'floor_objects': floor_candidates, 'floor_clearances': floor_checks,
    'floor_clearance_failures': floor_failures, 'rack_bottle_shelf_clearance': shelf_checks,
    'shelf_clearance_failures': shelf_failures, 'rack_layout': LAYOUT,
    'support_bottle_count': len(BOTTLES), 'collection_bottle_count': len(LAYOUT),
    'hero_final_shelf_clearance_m': final_clearances, 'hero_final_shelf_failures': hero_final_failures,
    'board': board_report, 'hold_bounds': hold_bounds, 'camera_checks': camera_checks,
    'opening_failures': opening_failures, 'final_display_framing': final_framing,
    'final_display_framing_failures': framing_failures, 'unexpected_stage_motion': stage_motion,
    'surface_intersections': intersections, 'containment_warnings': containment,
    'unknown_instances': unknown, 'missing_images': missing_images, 'missing_libraries': missing_libraries,
    'aabb_candidates': candidate_count, 'unique_obb_candidates': obb_count}
(OUT / 'gradient_validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
summary = {k: report[k] for k in [
    'scene', 'passed', 'sample_count', 'configuration_failures', 'collection_bottle_count',
    'removed_objects_still_visible', 'floor_clearance_failures', 'shelf_clearance_failures',
    'hero_final_shelf_clearance_m', 'hero_final_shelf_failures', 'opening_failures',
    'final_display_framing_failures', 'unexpected_stage_motion', 'missing_images', 'missing_libraries']}
summary.update(surface_intersections=len(intersections), containment_warnings=len(containment),
               unknown_instances=len(unknown),
               board_floor_clearance=floor_checks[BOARD], rack_floor_clearance=floor_checks[RACK],
               final_display_framing={f: v['display_union'] for f, v in final_framing.items()})
(OUT / 'gradient_validation_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
print('SHOT5_GRADIENT_COLLECTION_VALIDATION', json.dumps(summary), flush=True)
