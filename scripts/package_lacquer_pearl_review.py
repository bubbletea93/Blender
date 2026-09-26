"""Package actual rendered pixels into a comparison and short review video."""
from pathlib import Path
import json, subprocess
import cv2, imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'renders/lacquer_pearl_review'
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',15)
sheet=Image.new('RGB',(880,936),(21,23,28))
draw=ImageDraw.Draw(sheet)
draw.text((20,12),'Lacquer core | 1080p denoised render crops at 100%',font=font,fill='white')
for row,(frame,box) in enumerate([(199,(690,490,1110,880)),(231,(650,510,1070,900))]):
    for col,(label,filename) in enumerate([('Previous glitter',f'before_{frame:04d}.png'),('Fine pearl finish',f'final_glitter_{frame:04d}.png')]):
        x,y=20+440*col,54+440*row
        draw.text((x,y),f'{label} / f{frame}',font=font,fill='white')
        source=Image.open(OUT/filename).convert('RGB')
        assert source.size==(1920,1080)
        sheet.paste(source.crop(box),(x,y+32))
draw.text((20,916),'Cycles 128 samples | Denoising on | No added sparkle or sharpening',font=small,fill=(184,190,198))
sheet.save(OUT/'pearl_comparison.png')

frames=OUT/'shimmer_frames'
for frame in range(219,248):assert (frames/f'shot3_{frame:04d}.png').is_file()
video=OUT/'lacquer_pearl_shimmer_219_247.mp4'
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-framerate','30','-start_number','219','-i',str(frames/'shot3_%04d.png'),'-frames:v','29','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
cap=cv2.VideoCapture(str(video));fps=cap.get(cv2.CAP_PROP_FPS);size=[int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))];count=0
decoded={}
while True:
    ok,pixels=cap.read()
    if not ok:break
    if count in (0,12,28):decoded[count]=Image.fromarray(cv2.cvtColor(pixels,cv2.COLOR_BGR2RGB))
    count+=1
cap.release();assert count==29 and fps==30 and size==[1920,1080]
motion=Image.new('RGB',(1450,520),(21,23,28));md=ImageDraw.Draw(motion)
for col,(index,pixels) in enumerate(decoded.items()):
    x=10+480*col
    md.text((x,10),f'Encoded video / f{219+index}',font=font,fill='white')
    motion.paste(pixels.crop((650,470,1120,930)),(x,48))
motion.save(OUT/'encoded_shimmer_samples.png')
(OUT/'package_validation.json').write_text(json.dumps({'video':str(video),'decoded_frames':count,'fps':fps,'size':size,'comparison_crops_unscaled':True},indent=2))
print('PEARL_PACKAGE_COMPLETE',video)
