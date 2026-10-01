"""Verify a finished opening-shot PNG sequence and encode master/playback videos.

python scripts/package_opening_production.py --shot 1 (or 2). Same encode as Shot 5.

Uses existing rendered frames; does not launch Blender or modify the sequence.
Python dependencies: Pillow and imageio-ffmpeg.
"""
import argparse
import datetime
import hashlib
import json
import struct
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--shot',type=int,choices=[1,2],required=True)
args=parser.parse_args()
SHOTS={1:(0,82,'scenes/gel_polish_lapohka_shot1_0_82.blend','gel_polish_lapohka_shot1_0_82','lapohka_s1_f0-82_double_spin_4k'),
       2:(57,198,'scenes/gel_polish_lapohka_shot2_57_198.blend','gel_polish_lapohka_shot2_57_198','lapohka_s2_f57-198_reference_landing_4k')}
START,END,SCENE,FOLDER,STEM=SHOTS[args.shot]
FPS=30
args.output=ROOT/'renders'/FOLDER
args.frames=args.output/'frames'
args.output.mkdir(parents=True,exist_ok=True)
manifest_path=args.output/f'{STEM}_manifest.json'

def check_frame(frame):
    path=args.frames/f'frame_{frame:04d}.png'
    data=path.read_bytes()
    if data[:8]!=b'\x89PNG\r\n\x1a\n':raise ValueError(f'Invalid PNG: {path}')
    w,h,depth,color=struct.unpack('>IIBB',data[16:26])
    if (w,h,depth,color)!=(3840,2160,16,2):raise ValueError(f'Unexpected image format: {path}: {(w,h,depth,color)}')
    with Image.open(path) as im:im.verify()
    meta_path=path.with_suffix('.json')
    metadata=json.loads(meta_path.read_text()) if meta_path.exists() else {}
    if metadata and metadata.get('frame')!=frame:raise ValueError(f'Incorrect frame sidecar: {meta_path}')
    return {'frame':frame,'file':path.name,'bytes':len(data),
            'sha256':hashlib.sha256(data).hexdigest(),'render_metadata':metadata}

with ThreadPoolExecutor(max_workers=4) as pool:
    frame_records=list(pool.map(check_frame,range(START,END+1)))
print('SEQUENCE_VERIFIED',len(frame_records),'4K 16-bit RGB frames',flush=True)

ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
stem=STEM
master=args.output/(stem+'_master_prores4444xq.mov')
playback=args.output/(stem+'.mp4')
status={'scene':SCENE,
        'source_sequence':str(args.frames.resolve()),'frame_range':[START,END],
        'frame_count':len(frame_records),'fps':FPS,'duration_seconds':len(frame_records)/FPS,
        'resolution':[3840,2160],'source_bit_depth':16,
        'source_color':'AgX display-referred PNG, sRGB transfer, BT.709/sRGB primaries',
        'encoding_color':'BT.709 YCbCr matrix, limited range, sRGB transfer tag; no creative color adjustment',
        'frames':frame_records,'outputs':[],'status':'encoding'}
manifest_path.write_text(json.dumps(status,indent=2))
source=['-framerate',str(FPS),'-start_number',str(START),'-i',str(args.frames/'frame_%04d.png'),'-frames:v',str(len(frame_records)),'-an']
color_tags=['-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','iec61966-2-1']
matrix='scale=in_range=full:out_range=tv:out_color_matrix=bt709:flags=accurate_rnd+full_chroma_int'

def encode(path,options):
    temporary=path.with_name(path.stem+'.encoding'+path.suffix)
    command=[ffmpeg,'-hide_banner','-loglevel','warning','-y',*source,*options,*color_tags,str(temporary)]
    subprocess.run(command,check=True)
    # Decode every frame: this checks the completed container as well as encoding.
    checked=subprocess.run([ffmpeg,'-v','error','-i',str(temporary),'-map','0:v:0',
                            '-f','null','-','-progress','pipe:1','-nostats'],
                           capture_output=True,text=True,check=True)
    decoded=[int(line.split('=',1)[1]) for line in checked.stdout.splitlines() if line.startswith('frame=')]
    if not decoded or decoded[-1]!=len(frame_records):raise RuntimeError(f'Incomplete encoded video: {path}: {decoded}')
    temporary.replace(path)
    result={'file':str(path.resolve()),'bytes':path.stat().st_size,'decoded_frames':decoded[-1],
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    status['outputs'].append(result)
    manifest_path.write_text(json.dumps(status,indent=2))
    print('VIDEO_VERIFIED',json.dumps(result),flush=True)

try:
    encode(playback,['-vf',matrix+',format=yuv420p','-c:v','libx264','-preset','slow',
                     '-crf','14','-movflags','+faststart'])
    encode(master,['-vf',matrix+',format=yuv444p10le','-c:v','prores_ks','-profile:v','5',
                   '-vendor','apl0','-movflags','+faststart'])
    status['status']='complete'
    status['completed_at']=datetime.datetime.now().astimezone().isoformat()
    manifest_path.write_text(json.dumps(status,indent=2))
    print(f'SHOT{args.shot}_PRODUCTION_DELIVERY_COMPLETE',str(manifest_path),flush=True)
except Exception as error:
    status['status']='failed';status['error']=str(error)
    manifest_path.write_text(json.dumps(status,indent=2))
    raise
