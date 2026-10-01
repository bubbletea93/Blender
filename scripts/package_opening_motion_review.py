"""Package the two revised opening shots and an explicitly labeled comparison.

Uses review frames only; existing production exports are never touched.
Run with regular Python after render_opening_motion_review.py --mode motion.
"""
import json
import subprocess
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'renders/opening_reference_review'
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SHOTS = {1: (0, 56), 2: (57, 198)}
SIZE = (960, 540)
FPS = 30
OUT.mkdir(parents=True, exist_ok=True)


def encode(output, size):
    return subprocess.Popen([
        FFMPEG, '-hide_banner', '-loglevel', 'error', '-y',
        '-f', 'rawvideo', '-pixel_format', 'rgb24', '-video_size',
        f'{size[0]}x{size[1]}', '-framerate', str(FPS), '-i', '-',
        '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17',
        '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(output),
    ], stdin=subprocess.PIPE)


def finish(process):
    process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError('FFmpeg encode failed')


def load(path):
    with Image.open(path) as im:
        return im.convert('RGB').resize(SIZE, Image.Resampling.LANCZOS)


# Fail before opening output videos when a review or reference frame is absent.
for shot, (start, end) in SHOTS.items():
    folder = ROOT / f'renders/shot{shot}_reference_rebuild'
    for frame in range(start, end + 1):
        for path in (folder / 'motion' / f'frame_{frame:04d}.png',
                     folder / 'reference_frames' / f'ref_{frame:03d}.png'):
            if not path.is_file():
                raise FileNotFoundError(path)

font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 20)
combined_path = OUT / 'shots_1_2_updated_motion_review.mp4'
comparison_path = OUT / 'shots_1_2_reference_comparison.mp4'
combined = encode(combined_path, SIZE)
comparison = encode(comparison_path, (1920, 584))
manifest = {'fps': FPS, 'preview_resolution': SIZE, 'shots': []}
for shot, (start, end) in SHOTS.items():
    folder = ROOT / f'renders/shot{shot}_reference_rebuild'
    movie_path = folder / f'shot{shot}_reference_v002_motion_review.mp4'
    movie = encode(movie_path, SIZE)
    picks = ([0, 3, 6, 9, 12, 18, 24, 27, 30, 33, 36, 40, 47, 50, 53, 56]
             if shot == 1 else [57, 59, 61, 64, 67, 69, 72, 78, 96, 100, 117, 135, 160, 175, 190, 198])
    sheet = Image.new('RGB', (1280, 832), '#181818')
    draw = ImageDraw.Draw(sheet)
    for frame in range(start, end + 1):
        updated = load(folder / 'motion' / f'frame_{frame:04d}.png')
        data = updated.tobytes()
        movie.stdin.write(data)
        combined.stdin.write(data)
        original = load(folder / 'reference_frames' / f'ref_{frame:03d}.png')
        pair = Image.new('RGB', (1920, 584), '#181818')
        pair.paste(original, (0, 44))
        pair.paste(updated, (960, 44))
        labels = ImageDraw.Draw(pair)
        labels.text((16, 11), f'ORIGINAL REFERENCE  |  Shot {shot}  |  f{frame}', font=font, fill='white')
        labels.text((976, 11), f'UPDATED POLISH  |  Shot {shot}  |  f{frame}', font=font, fill='white')
        comparison.stdin.write(pair.tobytes())
        if frame in picks:
            index = picks.index(frame)
            x, y = index % 4 * 320, index // 4 * 208
            sheet.paste(updated.resize((320, 180), Image.Resampling.LANCZOS), (x, y + 28))
            draw.text((x + 8, y + 4), f'Shot {shot} / f{frame}', font=font, fill='white')
    finish(movie)
    sheet.save(folder / 'motion_contact.jpg', quality=92)
    manifest['shots'].append({'shot': shot, 'start': start, 'end': end,
                             'frames': end - start + 1, 'video': str(movie_path)})
finish(combined)
finish(comparison)
manifest['combined'] = str(combined_path)
manifest['comparison'] = str(comparison_path)
manifest['total_frames'] = sum(s['frames'] for s in manifest['shots'])
manifest['duration_seconds'] = manifest['total_frames'] / FPS
for path in [combined_path, comparison_path] + [Path(s['video']) for s in manifest['shots']]:
    subprocess.run([FFMPEG, '-v', 'error', '-i', str(path), '-f', 'null', '-'], check=True)
    frames, seconds = imageio_ffmpeg.count_frames_and_secs(str(path))
    expected = next((s['frames'] for s in manifest['shots'] if s['video'] == str(path)), manifest['total_frames'])
    if frames != expected:
        raise RuntimeError(f'{path.name}: expected {expected} frames, got {frames}')
    print('VERIFIED_VIDEO', path, frames, seconds, flush=True)
manifest['decoded_all_videos'] = True
(OUT / 'review_manifest.json').write_text(json.dumps(manifest, indent=2))
print('OPENING_MOTION_VIDEOS_READY', flush=True)
