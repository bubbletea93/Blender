"""Render the Shot 4 motion preview, skipping frames that already exist.

Cycles occasionally faults partway through a long single-process run of this
scene, so the driver in render_lapohka_shot4_all.py restarts Blender in chunks
and this script simply resumes wherever the last process stopped.

    blender -b scenes/gel_polish_lapohka_shot4_285_375.blend \
            --python scripts/render_lapohka_shot4_preview.py -- <first> <last> [pct] [samples]
"""
import bpy
import sys
from pathlib import Path

argv = sys.argv[sys.argv.index('--') + 1:]
first, last = int(argv[0]), int(argv[1])
pct = int(argv[2]) if len(argv) > 2 else 50
samples = int(argv[3]) if len(argv) > 3 else 32

root = Path('C:/Users/danht/Documents/GitHub/Blender')
frames = root / 'renders/shot4_285_375_review/preview_frames'
frames.mkdir(parents=True, exist_ok=True)

scene = bpy.context.scene
scene.render.resolution_percentage = pct
scene.cycles.samples = samples
scene.cycles.use_denoising = True
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'OPTIX'
    prefs.get_devices()
    for device in prefs.devices:
        device.use = device.type == 'OPTIX'
    scene.cycles.device = 'GPU'
except Exception:
    scene.cycles.device = 'CPU'

for frame in range(first, last + 1):
    path = frames / f'shot4_{frame:04d}.png'
    if path.exists():
        print('PREVIEW_FRAME_EXISTS', frame, flush=True)
        continue
    scene.frame_set(frame)
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    print('PREVIEW_FRAME_DONE', frame, flush=True)
print('PREVIEW_COMPLETE', flush=True)
