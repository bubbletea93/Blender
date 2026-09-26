"""Drive the full Shot 4 preview render in restartable chunks.

Run from a connected Blender (or any Python with bpy) - it spawns headless
Blender processes so a Cycles fault only costs the current chunk, and each
restart resumes from the frames already on disk.

    result = run(chunk=8, pct=50, samples=32)
"""
import bpy
import subprocess
from pathlib import Path

ROOT = Path('C:/Users/danht/Documents/GitHub/Blender')
BLEND = ROOT / 'scenes/gel_polish_lapohka_shot4_285_375.blend'
SCRIPT = ROOT / 'scripts/render_lapohka_shot4_preview.py'
FRAMES = ROOT / 'renders/shot4_285_375_review/preview_frames'
F_START, F_END = 285, 375


def missing():
    return [f for f in range(F_START, F_END + 1)
            if not (FRAMES / f'shot4_{f:04d}.png').exists()]


def run(chunk=8, pct=50, samples=32, max_passes=12):
    log = []
    for _ in range(max_passes):
        todo = missing()
        if not todo:
            break
        lo = todo[0]
        hi = min(lo + chunk - 1, F_END)
        proc = subprocess.run(
            [bpy.app.binary_path, '-b', str(BLEND), '--python', str(SCRIPT),
             '--', str(lo), str(hi), str(pct), str(samples)],
            capture_output=True, text=True, timeout=5400)
        done = sum(1 for line in proc.stdout.splitlines() if line.startswith('PREVIEW_FRAME_DONE'))
        log.append({'range': [lo, hi], 'rc': proc.returncode, 'rendered': done})
        if proc.returncode != 0 and done == 0:
            # a chunk that cannot render even one frame would loop forever
            log.append({'range': [lo, hi], 'fatal': proc.stderr[-1200:] or proc.stdout[-1200:]})
            break
    return {'log': log, 'still_missing': missing()}
