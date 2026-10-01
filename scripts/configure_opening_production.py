"""Save the revised opening shots ready for manual Render Animation.

In background Blender use --python this.py -- --shot 1 (or 2).
The configure() helper also works in the live scene without reloading it.
No render is started. Animation, materials, exposure and shutter are preserved.
"""
import argparse
import bpy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOTS = {
    1: ('gel_polish_lapohka_shot1_0_82.blend', 0, 82),
    2: ('gel_polish_lapohka_shot2_57_198.blend', 57, 198),
}


def render_dir(shot):
    return ROOT / 'renders' / Path(SHOTS[shot][0]).stem


def report(scene, shot):
    return {
        'file': bpy.data.filepath, 'shot': shot,
        'range': [scene.frame_start, scene.frame_end], 'step': scene.frame_step,
        'fps': scene.render.fps / scene.render.fps_base,
        'resolution': [scene.render.resolution_x, scene.render.resolution_y],
        'percentage': scene.render.resolution_percentage,
        'engine': scene.render.engine, 'device': scene.cycles.device,
        'samples': scene.cycles.samples,
        'adaptive': scene.cycles.use_adaptive_sampling,
        'threshold': scene.cycles.adaptive_threshold,
        'minimum_samples': scene.cycles.adaptive_min_samples,
        'denoising': scene.cycles.use_denoising,
        'denoiser': scene.cycles.denoiser,
        'denoising_quality': scene.cycles.denoising_quality,
        'format': scene.render.image_settings.file_format,
        'channels': scene.render.image_settings.color_mode,
        'bit_depth': scene.render.image_settings.color_depth,
        'output': bpy.path.abspath(scene.render.filepath),
        'skip_existing': not scene.render.use_overwrite,
        'persistent_data': scene.render.use_persistent_data,
        'sequencer': scene.render.use_sequencer,
        'motion_blur': scene.render.use_motion_blur,
        'shutter_at_current_frame': scene.render.motion_blur_shutter,
        'view_transform': scene.view_settings.view_transform,
        'look': scene.view_settings.look,
        'exposure': scene.view_settings.exposure,
        'existing_output_frames': len(list((render_dir(shot) / 'frames').glob('frame_*.png'))),
    }


def configure(scene, shot):
    _, start, end = SHOTS[shot]
    assert (scene.frame_start, scene.frame_end) == (start, end)
    assert not bpy.app.is_job_running('RENDER'), 'Wait for the active render to finish.'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'OPTIX'
    prefs.get_devices()
    for device in prefs.devices:
        device.use = device.type == 'OPTIX'
    assert any(d.use for d in prefs.devices), 'No OptiX render device found.'
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    scene.render.resolution_x = 3840
    scene.render.resolution_y = 2160
    scene.render.resolution_percentage = 100
    scene.render.pixel_aspect_x = scene.render.pixel_aspect_y = 1
    scene.render.fps = 30
    scene.render.fps_base = 1
    scene.frame_step = 1
    scene.render.use_border = False
    scene.render.use_crop_to_border = False
    scene.render.use_sequencer = False
    scene.render.use_persistent_data = False
    scene.cycles.samples = 1024
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = .002
    scene.cycles.adaptive_min_samples = 64
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    scene.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    scene.cycles.denoising_prefilter = 'ACCURATE'
    scene.cycles.denoising_quality = 'HIGH'
    scene.cycles.use_animated_seed = False
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.image_settings.color_depth = '16'
    scene.render.image_settings.compression = 25
    scene.render.use_file_extension = True
    scene.render.use_overwrite = False
    scene.render.use_placeholder = False
    (render_dir(shot) / 'frames').mkdir(parents=True, exist_ok=True)
    scene.render.filepath = f'//../renders/{render_dir(shot).name}/frames/frame_'
    return report(scene, shot)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--shot', type=int, choices=[1, 2], required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    path = ROOT / 'scenes' / SHOTS[args.shot][0]
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False)
    configure(bpy.context.scene, args.shot)
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False)
    verified = report(bpy.context.scene, args.shot)
    (render_dir(args.shot) / 'manual_render_settings.json').write_text(json.dumps(verified, indent=2))
    print('MANUAL_RENDER_READY', json.dumps(verified), flush=True)
