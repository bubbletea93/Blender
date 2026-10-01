"""Cut the LinkedIn work-in-progress teaser from the delivered 4K shot videos.

Hard cuts on motion, in film order, ending on the Shot 5 rack hold with a
title card. Uses existing renders only; does not launch Blender.
Python dependencies: imageio-ffmpeg.
"""
import json
import subprocess
from pathlib import Path

import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[1]
LAP = ROOT / 'renders/lapohka'
OUT = LAP / 'teaser_linkedin'
FPS = 30
W, H = 1920, 1080

# (source video, first local frame, last local frame inclusive, note)
SEGMENTS = [
    ('shot1_f48-180/lapohka_s1_f48-180_spin_closeup_4k.mp4', 6, 100, 'spin + shade swaps'),
    ('shot2_f96-198/lapohka_s2_f96-198_continuation_4k.mp4', 6, 48, 'bottle march'),
    # Stop before f12: a stray lit liquid sheet enters top-left after that.
    ('shot3_f199-284/lapohka_s3_f199-284_liquid_clearance_4k_v009.mp4', 0, 11, 'liquid whip-in'),
    ('shot4_f285-375/lapohka_s4_f285-375_fine_shimmer_4k_v005.mp4', 54, 90, 'array snaps to rows'),
    ('shot5_f376-528/lapohka_s5_f376-528_polish_finale_4k.mp4', 0, 130, 'drop into rack + hold'),
]
INK = '0x3E2544'

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
OUT.mkdir(parents=True, exist_ok=True)
stem = 'lapohka_teaser_linkedin_16x9_v001'
video = OUT / (stem + '.mp4')

# drawtext reads text from files so the middle dot and dash need no escaping.
lines = {
    'kicker.txt': 'WORK IN PROGRESS',
    'title.txt': '3D Product Motion',
    'tools.txt': 'Blender  \u00b7  Cycles  \u00b7  LiquiGen',
}
for name, text in lines.items():
    (OUT / name).write_text(text, encoding='utf-8')

inputs, chains = [], []
for i, (src, a, b, _) in enumerate(SEGMENTS):
    inputs += ['-i', str(LAP / src)]
    chains.append(f'[{i}:v]trim=start_frame={a}:end_frame={b + 1},setpts=PTS-STARTPTS,'
                  f'scale={W}:{H}:flags=lanczos,setsar=1[v{i}]')
total = sum(b - a + 1 for _, a, b, _ in SEGMENTS)
# Title fades in once the Shot 5 rack has landed (~local f40).
t0 = (total - (SEGMENTS[-1][2] - SEGMENTS[-1][1] + 1) + 42) / FPS
fade = f"alpha='if(lt(t,{t0:.3f}),0,min(1,(t-{t0:.3f})/0.5))'"
def text(file, font, size, y, delay=0.0):
    f = fade.replace(f'{t0:.3f}', f'{t0 + delay:.3f}')
    return (f"drawtext=fontfile={font}:textfile='{(OUT / file).as_posix().replace(':', chr(92) + ':')}'"
            f":fontcolor={INK}:fontsize={size}:x=96:y={y}:{f}")
concat = ''.join(f'[v{i}]' for i in range(len(SEGMENTS)))
graph = ';'.join(chains + [
    f'{concat}concat=n={len(SEGMENTS)}:v=1:a=0,'
    + ','.join([text('kicker.txt', 'segoeuisl.ttf', 26, 78),
                text('title.txt', 'segoeuib.ttf', 64, 112, 0.1),
                text('tools.txt', 'segoeuil.ttf', 30, 196, 0.2)])
    + ',format=yuv420p[out]'])

cmd = [ffmpeg, '-hide_banner', '-loglevel', 'warning', '-y', *inputs,
       '-filter_complex', graph, '-map', '[out]', '-an',
       '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-profile:v', 'high',
       '-r', str(FPS), '-movflags', '+faststart',
       '-color_range', 'tv', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
       str(video)]
# Run from the fonts folder so drawtext's fontfile needs no drive-letter escaping.
subprocess.run(cmd, check=True, cwd='C:/Windows/Fonts')

check = subprocess.run([ffmpeg, '-v', 'error', '-i', str(video), '-map', '0:v:0', '-f', 'null', '-',
                        '-progress', 'pipe:1', '-nostats'], capture_output=True, text=True, check=True)
decoded = [int(l.split('=', 1)[1]) for l in check.stdout.splitlines() if l.startswith('frame=')][-1]
if decoded != total:
    raise RuntimeError(f'expected {total} frames, decoded {decoded}')
manifest = {'video': str(video), 'frames': total, 'fps': FPS, 'seconds': round(total / FPS, 2),
            'resolution': [W, H], 'title_fade_in_s': round(t0, 2),
            'segments': [{'source': s, 'local_frames': [a, b], 'note': n} for s, a, b, n in SEGMENTS]}
(OUT / (stem + '_manifest.json')).write_text(json.dumps(manifest, indent=2))
print('TEASER_VERIFIED', json.dumps(manifest))
