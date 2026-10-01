"""Render review stills or motion frames of the recreated opening shots.

Blender --background --factory-startup --disable-autoexec --python this.py
-- --shots 1 2 --mode stills (or motion). Never overwrites the saved scenes.
"""
import argparse,bpy,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--shots',nargs='+',type=int,default=[1,2])
p.add_argument('--mode',choices=['stills','motion'],default='stills')
p.add_argument('--frames',nargs='+',type=int)
args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
shots={1:('gel_polish_lapohka_shot1_0_82.blend',[6,18,30,40,53,56,66,76]),
       2:('gel_polish_lapohka_shot2_57_198.blend',[57,61,64,78,117,180])}
for shot in args.shots:
    filename,picks=shots[shot]
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scenes'/filename),load_ui=False)
    s=bpy.context.scene
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='OPTIX';prefs.get_devices()
    for dev in prefs.devices:dev.use=dev.type=='OPTIX'
    s.render.engine='CYCLES';s.cycles.device='GPU'
    s.render.resolution_x=960 if args.mode=='motion' else 1280
    s.render.resolution_y=540 if args.mode=='motion' else 720
    s.render.resolution_percentage=100
    s.cycles.samples=24 if args.mode=='motion' else 64
    s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE'
    s.cycles.denoising_input_passes='RGB_ALBEDO_NORMAL'
    s.cycles.denoising_prefilter='ACCURATE';s.cycles.denoising_quality='HIGH'
    s.cycles.adaptive_min_samples=8;s.cycles.adaptive_threshold=.025
    s.render.use_persistent_data=False;s.render.use_sequencer=False
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8'
    s.render.image_settings.color_mode='RGB';s.render.image_settings.compression=25
    folder=ROOT/'renders'/Path(filename).stem/f'review_{args.mode}'
    folder.mkdir(parents=True,exist_ok=True)
    frames=args.frames or (range(s.frame_start,s.frame_end+1) if args.mode=='motion' else picks)
    for frame in frames:
        s.frame_set(frame)
        s.render.filepath=str(folder/f'frame_{frame:04d}.png')
        start=time.time();bpy.ops.render.render(write_still=True)
        print('REVIEW_FRAME',shot,frame,round(time.time()-start,2),flush=True)
    print('REVIEW_SHOT_COMPLETE',shot,args.mode,flush=True)
print('OPENING_REVIEWS_COMPLETE',flush=True)
