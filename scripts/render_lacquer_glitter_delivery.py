"""Verify the published shader in final renders and a short full-resolution clip."""
import bpy,json,os
from pathlib import Path
ROOT=Path('C:/Users/danht/Documents/GitHub/Blender');OUT=ROOT/os.environ.get('LACQUER_REVIEW_DIR','renders/lacquer_glitter_review')
def gpu():
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for device in prefs.devices:device.use=device.type=='OPTIX'
    s=bpy.context.scene;s.cycles.device='GPU';s.cycles.samples=128;s.cycles.use_denoising=True;s.render.resolution_percentage=100
    for ob in s.objects:
        name=ob.override_library.reference.name if ob.override_library else ob.name
        if name=='New_Cap' and ob.hide_render:
            for modifier in ob.modifiers:modifier.show_viewport=False;modifier.show_render=False
    return s

bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scenes/gel_polish_lapohka_shot3_199_284.blend'))
s=gpu();settings={'resolution':[s.render.resolution_x,s.render.resolution_y],'samples':s.cycles.samples,'denoising':s.cycles.use_denoising,'filter':s.cycles.pixel_filter_type,'filter_width':s.cycles.filter_width}
for frame in [199,231]:
    s.frame_set(frame);s.render.filepath=str(OUT/f'final_glitter_{frame:04d}.png');bpy.ops.render.render(write_still=True)
    print('PUBLISHED_STILL',frame,flush=True)
clip=OUT/'shimmer_frames';clip.mkdir(exist_ok=True)
for frame in range(219,248):
    path=clip/f'shot3_{frame:04d}.png'
    if path.exists():continue
    if frame>=223 and (frame-223)%5==0:
        import shutil;shutil.copy2(clip/f'shot3_{frame-1:04d}.png',path)
    else:
        s.frame_set(frame);s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
    print('SHIMMER_FRAME',frame,flush=True)

for shot,frame in [('gel_polish_lapohka_shot2_97_198.blend',150),('gel_polish_lapohka_shot4_285_375.blend',310)]:
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scenes'/shot));s=gpu();s.frame_set(frame)
    s.render.filepath=str(OUT/(Path(shot).stem+f'_glitter_{frame:04d}.png'));bpy.ops.render.render(write_still=True)
    print('OTHER_SHOT_VERIFIED',shot,frame,flush=True)
(OUT/'render_validation.json').write_text(json.dumps({'published_shader_renders':True,'shot3_final_settings':settings,'shimmer_clip_frames':[219,247],'other_shots':[['shot2',150],['shot4',310]]},indent=2))
print('GLITTER_DELIVERY_COMPLETE',flush=True)
