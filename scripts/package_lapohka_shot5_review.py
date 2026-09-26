"""Create reference comparisons and encode/verify the Shot 5 motion review."""
from pathlib import Path
import argparse,json,subprocess,datetime
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--version',default='v003')
version=parser.parse_args().version
if len(version)!=4 or not version.startswith('v') or not version[1:].isdigit():
    parser.error('--version must use vNNN format')
work=root/f'renders/shot5_polish_finale_{version}'
reference=root/'renders/shot5_polish_finale_v001'
delivery=root/'renders/lapohka/shot5_f376-528';delivery.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
pairs=[]
for frame,index in [(376,1),(400,5),(460,10),(528,16)]:
    pair=Image.new('RGB',(1920,580),(24,24,24));draw=ImageDraw.Draw(pair)
    for x,label,path in [(0,'REFERENCE',reference/f'reference_{index:02d}.png'),(960,'POLISH ADAPTATION',work/f'review_{frame:04d}.png')]:
        with Image.open(path) as im:pair.paste(im.convert('RGB').resize((960,540),Image.Resampling.LANCZOS),(x,40))
        draw.text((x+18,10),f'{label} / f{frame}',font=font,fill='white')
    pair.save(work/f'comparison_{frame:04d}.jpg',quality=95)
    pairs.append(pair)
contact=Image.new('RGB',(1920,580*len(pairs)),(24,24,24))
for i,im in enumerate(pairs):contact.paste(im,(0,i*580))
contact.save(work/'reference_comparison.jpg',quality=95)

frames=[work/'preview_frames'/f'frame_{f:04d}.png' for f in range(376,529)]
if not all(p.exists() for p in frames):
    print('COMPARISONS_READY; preview not complete yet')
    raise SystemExit(0)

# Show the anticipation, contact and overlapping recovery in one review image.
motion_frames=[376,400,422,426,432,436,440,446,470]
motion=Image.new('RGB',(1440,930),(24,24,24))
draw=ImageDraw.Draw(motion)
for i,frame in enumerate(motion_frames):
    x=(i%3)*480;y=(i//3)*310
    with Image.open(work/'preview_frames'/f'frame_{frame:04d}.png') as im:
        motion.paste(im.convert('RGB').resize((480,270),Image.Resampling.LANCZOS),(x,y+40))
    draw.text((x+12,y+9),f'f{frame}',font=font,fill='white')
motion.save(work/'motion_contact_sheet.jpg',quality=95)

ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
video=delivery/f'lapohka_s5_f376-528_polish_finale_{version}.mp4'
cmd=[ffmpeg,'-hide_banner','-loglevel','error','-y','-framerate','30','-start_number','376','-i',str(work/'preview_frames/frame_%04d.png'),'-frames:v','153','-c:v','libx264','-preset','slow','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(video)]
subprocess.run(cmd,check=True)
result=subprocess.run([ffmpeg,'-hide_banner','-v','error','-i',str(video),'-map','0:v:0','-f','null','-','-progress','pipe:1','-nostats'],capture_output=True,text=True,check=True)
decoded=[int(x.split('=')[1]) for x in result.stdout.splitlines() if x.startswith('frame=')][-1]
assert decoded==153,(decoded,result.stdout)
manifest={'scene':f'scenes/gel_polish_lapohka_shot5_376_528_polish_finale_{version}.blend','video':str(video.relative_to(root)),
 'frames':[376,528],'decoded_frames':decoded,'fps':30,'resolution':[960,540],'samples':64,'purpose':'Camera, lighting and animation review; not a production render',
 'reference_comparison':str((work/'reference_comparison.jpg').relative_to(root)),'completed':datetime.datetime.now().isoformat()}
(delivery/f'lapohka_s5_f376-528_polish_finale_{version}_manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
