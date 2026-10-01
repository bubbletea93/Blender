"""Reproduce the approved Shot 5 4K render from an explicitly opened scene.

Run Blender in background with scenes/gel_polish_lapohka_shot5_376_528.blend
and --python scripts/render_shot5_production.py. Existing PNG + JSON pairs are
retained for resume. For a changed scene, use a new output directory with:
-- --output renders/gel_polish_lapohka_shot5_376_528_new_revision
"""
import argparse, bpy, json, sys, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,default=ROOT/'renders/gel_polish_lapohka_shot5_376_528')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
work=args.output.resolve()
out=work/'frames'
out.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene
assert (s.frame_start,s.frame_end)==(376,528)
s.render.resolution_x=3840
s.render.resolution_y=2160
s.render.resolution_percentage=100
s.render.use_sequencer=False
# Shot 5 must rebuild instance transforms each frame: persistent data left a stale podium transform.
s.render.use_persistent_data=False
s.cycles.samples=1024
s.cycles.use_adaptive_sampling=True
s.cycles.adaptive_threshold=.002
s.cycles.adaptive_min_samples=64
s.cycles.use_denoising=True
s.cycles.denoiser='OPENIMAGEDENOISE'
s.cycles.denoising_input_passes='RGB_ALBEDO_NORMAL'
s.cycles.denoising_prefilter='ACCURATE'
s.cycles.denoising_quality='HIGH'
s.cycles.use_animated_seed=False
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='OPTIX'
prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
assert any(d.use for d in prefs.devices)
s.cycles.device='GPU'
s.render.image_settings.file_format='PNG'
s.render.image_settings.color_mode='RGB'
s.render.image_settings.color_depth='16'
s.render.image_settings.compression=25
s.render.filepath=str(out/'frame_')
# Settings apply only to this render process; the opened scene is not overwritten.
for frame in range(376,529):
    dest=out/f'frame_{frame:04d}.png'
    meta=out/f'frame_{frame:04d}.json'
    if dest.exists() and meta.exists():continue
    s.frame_set(frame)
    s.render.filepath=str(dest)
    start=time.time()
    bpy.ops.render.render(write_still=True)
    assert dest.exists() and dest.stat().st_size>100000
    data=dict(frame=frame,seconds=time.time()-start,resolution=[3840,2160],
        samples=1024,noise_threshold=.002,min_samples=64,bit_depth=16,
        denoiser='OpenImageDenoise HIGH / accurate albedo+normal',
        view_transform=s.view_settings.view_transform,look=s.view_settings.look,
        exposure=s.view_settings.exposure,motion_blur=s.render.use_motion_blur,
        source=bpy.data.filepath)
    meta.write_text(json.dumps(data,indent=2))
    print('PRODUCTION_FRAME_COMPLETE',frame,round(data['seconds'],2),flush=True)
print('PRODUCTION_RENDER_DONE',flush=True)
