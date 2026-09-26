"""Decode selected original Shot 5 frames and create a visual timing sheet."""
from pathlib import Path
import subprocess,json
import imageio_ffmpeg
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'renders/shot5_polish_finale_v001';OUT.mkdir(parents=True,exist_ok=True)
SOURCE=ROOT/'references/lapohka_3d_motion_shots/Lapohka 3D Motion - Shot 5 (f376-528).mp4'
PICKS=[0,4,8,16,24,36,48,60,72,84,96,108,120,132,144,152]
select='+'.join(f'eq(n,{n})' for n in PICKS)
ff=imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ff,'-hide_banner','-loglevel','error','-y','-i',str(SOURCE),
    '-vf',f'select={select.replace(",", chr(92)+",")},scale=960:540',
    '-fps_mode','vfr',str(OUT/'reference_%02d.png')],check=True)
sheet=Image.new('RGB',(1920,1200),(24,24,24));draw=ImageDraw.Draw(sheet)
for index,local in enumerate(PICKS):
    image=Image.open(OUT/f'reference_{index+1:02d}.png').convert('RGB')
    image.resize((480,270),Image.Resampling.LANCZOS)
    x=(index%4)*480;y=(index//4)*300
    sheet.paste(image.resize((480,270),Image.Resampling.LANCZOS),(x,y+30))
    draw.text((x+12,y+8),f'f{376+local} / {local/30:.2f}s',fill='white')
sheet.save(OUT/'reference_contact_sheet.png')
(OUT/'reference_frames.json').write_text(json.dumps(dict(source=str(SOURCE),frames=[376+n for n in PICKS],fps=30),indent=2))
print(OUT/'reference_contact_sheet.png')
