"""Render review images without changing the saved production settings."""
import bpy,sys,json,time,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
version=re.search(r'_v(\d+)\.blend$',bpy.data.filepath).group(1)
work=root/f'renders/shot5_polish_finale_v{version}'
s=bpy.context.scene
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['stills']
preview=args[0]=='preview'
full_resolution=args[0]=='4k'
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU'
# Rebuild instance transforms each frame: persistent Cycles data produced a
# stale podium transform at the first impact frame in sequential rendering.
s.render.use_persistent_data=False
s.cycles.samples=64 if preview else (512 if full_resolution else 256)
s.cycles.adaptive_threshold=.015 if preview else (.003 if full_resolution else .004)
s.render.resolution_x=960 if preview else (3840 if full_resolution else 1920)
s.render.resolution_y=540 if preview else (2160 if full_resolution else 1080)
s.render.resolution_percentage=100
s.render.image_settings.color_depth='8' if preview else '16'
folder=work/'preview_frames' if preview else work
folder.mkdir(parents=True,exist_ok=True)
frames=[int(v) for v in args[1:]] or (range(376,529) if preview else [376,384,400,460,528])
report=[]
for frame in frames:
    s.frame_set(frame)
    suffix='_4k' if full_resolution else ''
    s.render.filepath=str(folder/(f'frame_{frame:04d}.png' if preview else f'review_{frame:04d}{suffix}.png'))
    started=time.time();bpy.ops.render.render(write_still=True)
    report.append({'frame':frame,'seconds':round(time.time()-started,3),'file':s.render.filepath})
    print('SHOT5_REVIEW_FRAME',json.dumps(report[-1]),flush=True)
(work/('preview_render_report.json' if preview else ('stills_4k_render_report.json' if full_resolution else 'stills_render_report.json'))).write_text(json.dumps(report,indent=2))
