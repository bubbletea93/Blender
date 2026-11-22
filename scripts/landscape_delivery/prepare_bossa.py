"""Build 16:9 copies of the six approved Bossa scenes in background Blender.

Run blender -b --factory-startup -P scripts/landscape_delivery/prepare_bossa.py
with -- followed by optional shot numbers. Production scenes keep the original
Cycles settings. Proof images, if requested via BOSSA_WIDE_PROOFS, use a
temporary resolution after saving the production scene.
"""
import os
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
RANGES = {1: (0, 125), 2: (126, 170), 5: (316, 403), 6: (404, 425),
          7: (426, 450), 10: (657, 749)}
PROOF_FRAMES = {1: [52, 124], 2: [155], 5: [316, 390],
                6: [414], 7: [439], 10: [730]}
MAGNIFICATION = {1: 1.15, 2: 1.05, 5: 1.13, 6: 1.13, 7: 1.13, 10: 1.42}
ASPECT = 16 / 9


def compose(scene, shot):
    camera = scene.camera
    optics = camera.data
    if optics.type != 'PERSP' or optics.sensor_fit != 'VERTICAL':
        raise ValueError(f'Check the camera fit on {camera.name}')
    optics.sensor_height /= MAGNIFICATION[shot]
    # A title column and a product column share the first frame. Recenter as
    # the camera moves from the title composition into the brush close-up.
    if shot in (1, 2):
        shifts = ([(0, -.27), (80, -.27), (112, -.16), (125, -.10)]
                  if shot == 1 else [(126, -.10), (149, 0), (170, 0)])
        for frame, shift in shifts:
            optics.shift_x = shift
            optics.keyframe_insert('shift_x', frame=frame, group='Landscape composition')

    titles = {name: y for name, y in [('BOSSA01_Intro', .625),
                                        ('BOSSA01_TitleA', .527),
                                        ('BOSSA01_TitleB', .439)]}
    details = [obj for obj in scene.objects if obj.name in titles or any(
        part in obj.name for part in ('ReferenceDrop_', 'FinaleAccent', 'LacquerAccent_'))]
    offsets = {obj: [] for obj in details}
    for obj in details:
        if obj.delta_location.length > .000001:
            raise ValueError(f'Existing offset on {obj.name}')
        if obj.name in titles:
            obj.data.size *= 1.56
    # Work from unmodified source positions for every sample. The objects
    # retain their original rotation, materials, fade, and focus animation.
    for frame in range(scene.frame_start-1, scene.frame_end+2):
        scene.frame_set(frame)
        basis = camera.matrix_world.to_quaternion()
        for obj in details:
            projected = world_to_camera_view(scene, camera, obj.matrix_world.translation)
            if projected.z <= 0:
                continue
            x, y = projected.x, projected.y
            if obj.name in titles:
                target_x, target_y = .315, titles[obj.name]
            else:
                # Move peripheral lacquer accents into the space opened by
                # the widescreen camera; maintain their distance to the lens.
                spread = 2.0 if shot == 10 else (1.80 if shot == 5 else 2.40)
                target_x = .5 + spread * (x - .5 + optics.shift_x / ASPECT)
                target_y = y
            height = projected.z * optics.sensor_height / optics.lens
            local = Vector(((target_x-x)*height*ASPECT, (target_y-y)*height, 0))
            world_offset = basis @ local
            if obj.parent:
                transform = (obj.parent.matrix_world @ obj.matrix_parent_inverse).to_3x3()
                world_offset = transform.inverted() @ world_offset
            offsets[obj].append((frame, world_offset))
    for obj, samples in offsets.items():
        for frame, offset in samples:
            obj.delta_location = offset
            obj.keyframe_insert('delta_location', frame=frame, group='Landscape composition')
    if shot in (6, 7):
        from array_wings import extend_array
        extend_array(scene, shot)


def build(shot):
    first, last = RANGES[shot]
    name = f'gel_polish_bossa_shot{shot:02}'
    source = ROOT / 'scenes' / f'{name}_{first}_{last}.blend'
    stem = f'{name}_landscape_{first}_{last}'
    destination = source.with_name(stem+'.blend')
    if destination.exists():
        raise FileExistsError(destination)
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
    scene = bpy.context.scene
    if (scene.frame_start, scene.frame_end, scene.render.fps) != (first, last, 25):
        raise ValueError(f'Unexpected timing: {source}')
    scene.render.resolution_x, scene.render.resolution_y = 3840, 2160
    scene.render.resolution_percentage = 100
    scene.render.pixel_aspect_x = scene.render.pixel_aspect_y = 1
    scene.render.use_border = scene.render.use_crop_to_border = False
    scene.render.filepath = f'//../renders/{stem}/frames/frame_'
    scene.render.use_overwrite = scene.render.use_placeholder = False
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_depth = '16'
    scene.render.image_settings.color_mode = 'RGB'
    compose(scene, shot)
    scene.frame_set(PROOF_FRAMES[shot][0])
    scene['landscape_source'] = source.name
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(destination), compress=True)
    print('WIDE SCENE', destination, flush=True)
    if directory := os.environ.get('BOSSA_WIDE_PROOFS'):
        scene.render.resolution_percentage = 20
        scene.render.image_settings.color_depth = '8'
        scene.cycles.samples = 18
        scene.cycles.adaptive_min_samples = 4
        scene.cycles.adaptive_threshold = .05
        for frame in PROOF_FRAMES[shot]:
            scene.frame_set(frame)
            scene.render.filepath = str(Path(directory) / f'shot{shot:02}_{frame:04}.png')
            bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    shots = [int(arg) for arg in args if arg.isdigit()] or list(RANGES)
    for shot in shots:
        build(shot)
