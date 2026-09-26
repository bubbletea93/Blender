"""Validate saved Shot5 v005 without changing or saving either scene.

Run with factory startup and --disable-autoexec against the saved v005 file.
Reports all integer frames and quarter frames around the impact. Manufactured
joins within a bottle, acrylic rack, or mounted sample board are intentional.
"""
import bpy
import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(bpy.data.filepath)
VERSION = SOURCE.stem.rsplit('_', 1)[-1]
OUT = ROOT / ('renders/shot5_brand_collection_' + VERSION)
OUT.mkdir(parents=True, exist_ok=True)
SOURCE_HASH = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
BASELINE = ROOT / 'scenes/gel_polish_lapohka_shot5_376_528_polish_finale_v004.blend'
s = bpy.context.scene
assert VERSION in {'v005', 'v006'}, SOURCE
assert (s.frame_start, s.frame_end, s.render.fps) == (376, 528, 30)

HERO = 'SHOT05_Bottle_Assembly'
RACK = 'SHOT05_CollectionRack'
BOARD = 'SHOT05_CollectionSampleBoard'
PODIUM = 'SHOT05_CeramicPodium'
STAGE = 'SHOT05_StageReveal'
PODIUM_RADIUS = float(s.objects[PODIUM]['diameter_mm']) / 2000
EPS = 1e-7
SAMPLES = sorted(set(range(376, 529)) | {420 + i * .25 for i in range(205)})
BOTTLES = sorted(o.name for o in s.objects if o.name.startswith('SHOT05_CollectionRack_Bottle_'))
assert len(BOTTLES) == 6, BOTTLES
NAMES = [HERO, RACK, BOARD] + BOTTLES
assert all(n in s.objects for n in NAMES + [PODIUM, STAGE, 'SHOT05_StageImpact'])
CACHE = {}


def owner(ins):
    obj = ins.parent.original if ins.is_instance and ins.parent else ins.object.original
    while obj:
        if obj.name in NAMES:
            return obj.name
        obj = obj.parent
    return None


def capture_part(ins):
    matrix = ins.matrix_world.copy()
    points = [matrix @ Vector(v) for v in ins.object.bound_box]
    mesh = ins.object.data
    key = (ins.object.original.as_pointer(), len(mesh.vertices), len(mesh.polygons))
    if key not in CACHE:
        coords = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
        mesh.vertices.foreach_get('co', coords)
        CACHE[key] = (coords.reshape(-1, 3), [tuple(p.vertices) for p in mesh.polygons])
    return {'name': ins.object.name, 'matrix': matrix, 'geometry': CACHE[key],
            'points': points,
            'lo': np.array([min(p[i] for p in points) for i in range(3)]),
            'hi': np.array([max(p[i] for p in points) for i in range(3)]),
            'axes': [matrix.to_3x3().col[i].normalized() for i in range(3)]}


def exact_points(part, inverse=None):
    matrix = np.asarray(inverse @ part['matrix'] if inverse is not None else part['matrix'])
    return part['geometry'][0] @ matrix[:3, :3].T + matrix[:3, 3]


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


def camera_state(scene):
    scene.frame_set(376)
    bpy.context.view_layer.update()
    return {'camera_matrix': [list(row) for row in scene.camera.matrix_world],
            'lens_mm': scene.camera.data.lens,
            'hero_matrix': [list(row) for row in scene.objects[HERO].matrix_world],
            'camera_position': list(scene.camera.matrix_world.translation),
            'forward_z': float((scene.camera.matrix_world.to_3x3() @ Vector((0, 0, -1))).z)}


opening = camera_state(s)
checks = {n: {'minimum_tabletop_clearance_m': 100, 'clearance_frame': None,
              'minimum_radial_margin_m': 100, 'radial_margin_frame': None} for n in NAMES}
shelf_checks = {n: {'shelf_top_in_rack_m': float(s.objects[n]['shelf_top_m']),
                    'minimum_foot_clearance_m': 100, 'clearance_frame': None} for n in BOTTLES}
unknown, intersections, containment, parent_errors, stage_errors = [], [], [], [], []
fallbacks, camera_checks, hold_bounds = [], {}, {}
candidate_count = 0
obb_count = 0
pair_names = list(itertools.combinations(NAMES, 2))
for n in [RACK, BOARD, PODIUM]:
    if s.objects[n].parent != s.objects[STAGE]:
        parent_errors.append(n)
for n in BOTTLES:
    if s.objects[n].parent != s.objects[RACK]:
        parent_errors.append(n)

for frame in SAMPLES:
    if frame % 10 == 0:
        print('BRAND_VALIDATING_FRAME', frame, flush=True)
    s.frame_set(math.floor(frame), subframe=frame - math.floor(frame))
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    # Stage coordinates preserve metres; the podium object itself has enlarged
    # XY scale, so using its inverse would distort physical radial margins.
    stage_inverse = s.objects[STAGE].matrix_world.inverted()
    rack_inverse = s.objects[RACK].matrix_world.inverted()
    podium_top = (s.objects[PODIUM].matrix_world @ Vector((0, 0, .05))).z
    expected_top = (s.objects[STAGE].matrix_world @ Vector((0, 0, .05))).z
    if abs(podium_top - expected_top) > EPS:
        stage_errors.append({'frame': frame, 'actual_top_m': podium_top, 'expected_top_m': expected_top})
    parts = {n: [] for n in NAMES}
    for ins in deps.object_instances:
        if ins.object.type == 'MESH':
            name = owner(ins)
            if name is not None:
                parts[name].append(capture_part(ins))
    bounds = {}
    for name in NAMES:
        if not parts[name]:
            unknown.append([frame, name])
            continue
        bounds[name] = (np.min([p['lo'] for p in parts[name]], axis=0),
                        np.max([p['hi'] for p in parts[name]], axis=0))
        # Exact evaluated vertices avoid tilted bound-box corners reporting
        # false foot penetration, and give true podium-edge support margins.
        local = np.concatenate([exact_points(p, stage_inverse) for p in parts[name]])
        clearance = float(local[:, 2].min()) - .05
        radial_margin = PODIUM_RADIUS - float(np.hypot(local[:, 0], local[:, 1]).max())
        c = checks[name]
        if clearance < c['minimum_tabletop_clearance_m']:
            c.update(minimum_tabletop_clearance_m=clearance, clearance_frame=frame)
        if radial_margin < c['minimum_radial_margin_m']:
            c.update(minimum_radial_margin_m=radial_margin, radial_margin_frame=frame)
        if name in BOTTLES:
            points = np.concatenate([exact_points(p, rack_inverse) for p in parts[name]])
            foot = float(points[:, 2].min()) - shelf_checks[name]['shelf_top_in_rack_m']
            if foot < shelf_checks[name]['minimum_foot_clearance_m']:
                shelf_checks[name].update(minimum_foot_clearance_m=foot, clearance_frame=frame)
        if frame == 480:
            hold_bounds[name] = {'stage_local_min': local.min(axis=0).tolist(),
                                 'stage_local_max': local.max(axis=0).tolist()}
    if frame in [376, 392, 400, 422, 432, 438, 451, 480, 508, 528]:
        points = [p for part in parts[HERO] for p in part['points']]
        ndc = [world_to_camera_view(s, s.camera, p) for p in points]
        camera_checks[str(frame)] = {'hero_ndc_xmin_xmax_ymin_ymax': [min(p.x for p in ndc), max(p.x for p in ndc),
                                                                             min(p.y for p in ndc), max(p.y for p in ndc)],
                                     'looks_up': (s.camera.matrix_world.to_3x3() @ Vector((0, 0, -1))).z > 0}
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
            if boxes_separate(a, b):
                continue
            obb_count += 1
            ta, tb = mesh_tree(a), mesh_tree(b)
            overlaps = ta.overlap(tb)
            pair = {'frame': frame, 'a': name_a + '/' + a['name'], 'b': name_b + '/' + b['name']}
            if overlaps:
                intersections.append(dict(pair, triangle_pairs=len(overlaps)))
            else:
                warnings = []
                for part, other, label in [(a, tb, 'a_inside_b'), (b, ta, 'b_inside_a')]:
                    vertices = part['world_vertices']
                    for index in sorted(set([0, len(vertices) // 2, len(vertices) - 1])):
                        if inside_surface(vertices[index], other):
                            warnings.append(label)
                            break
                if warnings:
                    containment.append(dict(pair, warnings=warnings))

missing_libraries = []
for lib in bpy.data.libraries:
    path = bpy.path.abspath(lib.filepath, library=lib.parent)
    if not Path(path).is_file():
        missing_libraries.append({'name': lib.name, 'path': path})
missing_images = []
for im in bpy.data.images:
    if im.source != 'FILE' or im.packed_file or im.packed_files or not im.filepath:
        continue
    path = bpy.path.abspath(im.filepath, library=im.library)
    if not Path(path).is_file():
        missing_images.append({'name': im.name, 'path': path})

opening_comparison = {'baseline': str(BASELINE), 'checked': False}
if BASELINE.is_file():
    bpy.ops.wm.open_mainfile(filepath=str(BASELINE), load_ui=False, use_scripts=False)
    baseline = camera_state(bpy.context.scene)
    errors = {k: float(np.max(np.abs(np.asarray(opening[k]) - np.asarray(baseline[k]))))
              for k in ['camera_matrix', 'lens_mm', 'hero_matrix']}
    opening_comparison.update(checked=True, maximum_absolute_errors=errors,
                              passed=all(v <= 1e-7 for v in errors.values()),
                              current=opening, baseline_state=baseline)

clearance_failures = [n for n, c in checks.items() if c['minimum_tabletop_clearance_m'] < -EPS]
radial_failures = [n for n, c in checks.items() if c['minimum_radial_margin_m'] < -EPS]
shelf_failures = [n for n, c in shelf_checks.items() if c['minimum_foot_clearance_m'] < -EPS]
failed = any([unknown, intersections, containment, parent_errors, stage_errors,
              clearance_failures, radial_failures, shelf_failures, missing_libraries, missing_images])
if opening_comparison.get('checked') and not opening_comparison.get('passed'):
    failed = True
report = {'scene': str(SOURCE), 'scene_sha256': SOURCE_HASH, 'passed': not failed,
          'frame_count': 153, 'sample_count': len(SAMPLES), 'frames': [376, 528],
          'subframe_sampling': 'All integer frames plus quarter frames from 420 through 471',
          'assemblies': NAMES, 'stage_clearance_and_support': checks,
          'rack_bottle_shelf_clearance': shelf_checks, 'hold_bounds': hold_bounds,
          'camera_checks': camera_checks, 'opening_comparison': opening_comparison,
          'unknown_instance_parents': unknown, 'incorrect_parents': parent_errors,
          'stage_top_errors': stage_errors, 'tabletop_clearance_failures': clearance_failures,
          'radial_support_failures': radial_failures, 'shelf_clearance_failures': shelf_failures,
          'surface_intersections': intersections, 'containment_warnings': containment,
          'missing_libraries': missing_libraries, 'missing_images': missing_images,
          'aabb_candidates': candidate_count, 'obb_candidates': obb_count,
          'method': 'Exact evaluated mesh vertices in animated stage/rack coordinates establish tabletop, shelf, and '
                    f'{PODIUM_RADIUS * 1000:g} mm radial clearances. Complete assembly AABB, per-part AABB, and oriented envelope rejection '
                    'precede exact mesh BVH surface tests. Remaining intersecting envelopes receive sampled solid '
                    'containment checks. Manufactured joins within each bottle, rack, and mounted board are excluded; '
                    'between those assemblies, including every neighboring bottle pair, are checked. Font geometry '
                    'is excluded. Source scene and v004 are read only and neither file is saved.'}
(OUT / 'validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
summary = {k: report[k] for k in ['passed', 'frame_count', 'sample_count', 'stage_clearance_and_support',
           'rack_bottle_shelf_clearance', 'tabletop_clearance_failures', 'radial_support_failures',
           'shelf_clearance_failures', 'missing_libraries', 'missing_images', 'opening_comparison']}
summary.update(surface_intersections=len(intersections), containment_warnings=len(containment),
               unknown_instances=len(unknown), aabb_candidates=candidate_count, obb_candidates=obb_count)
(OUT / 'validation_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
print('SHOT5_BRAND_COLLECTION_VALIDATION', json.dumps(summary), flush=True)
