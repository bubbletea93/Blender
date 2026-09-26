"""Render sparse review frames of Shot 4 at reduced size, for reference comparison.

    blender -b scenes/gel_polish_lapohka_shot4_285_375.blend \
            --python scripts/render_lapohka_shot4_review.py -- <outdir> <pct> <frames csv>
"""
import bpy
import sys
import os

argv = sys.argv[sys.argv.index('--') + 1:]
outdir, pct = argv[0], int(argv[1])
frames = [int(x) for x in argv[2].split(',')]
samples = int(argv[3]) if len(argv) > 3 else 48

os.makedirs(outdir, exist_ok=True)
scene = bpy.context.scene
scene.render.resolution_percentage = pct
scene.cycles.samples = samples
scene.cycles.use_denoising = True
scene.render.image_settings.file_format = 'PNG'

for f in frames:
    scene.frame_set(f)
    scene.render.filepath = os.path.join(outdir, f'shot4_{f:04d}.png')
    bpy.ops.render.render(write_still=True)
    print(f'REVIEW {f}')
print('REVIEW_DONE')
