"""Encode the Shot 4 preview frames to mp4 using Blender's own ffmpeg.

There is no ffmpeg on PATH on this machine, so the sequence is pushed through a
throwaway VSE scene instead.

    blender -b --factory-startup --python scripts/package_lapohka_shot4_preview.py
"""
import bpy
from pathlib import Path

ROOT = Path('C:/Users/danht/Documents/GitHub/Blender')
FRAMES = ROOT / 'renders/shot4_285_375_review/preview_frames'
OUT = ROOT / 'renders/shot4_285_375_review'
F_START, F_END = 285, 375

files = sorted(FRAMES.glob('shot4_*.png'))
expected = F_END - F_START + 1
assert len(files) == expected, f'Expected {expected} frames, found {len(files)}'

scene = bpy.context.scene
scene.sequence_editor_create()
strip = scene.sequence_editor.strips.new_image(
    'shot4', str(files[0]), channel=1, frame_start=F_START, fit_method='ORIGINAL')
for path in files[1:]:
    strip.elements.append(path.name)

first = bpy.data.images.load(str(files[0]))
width, height = first.size
bpy.data.images.remove(first)

scene.frame_start, scene.frame_end = F_START, F_END
scene.render.fps, scene.render.fps_base = 30, 1
scene.render.resolution_x, scene.render.resolution_y = width, height
scene.render.resolution_percentage = 100
if hasattr(scene.render.image_settings, 'media_type'):
    scene.render.image_settings.media_type = 'VIDEO'   # Blender 5 gates FFMPEG behind this
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'HIGH'
scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
scene.render.ffmpeg.gopsize = 12
scene.render.ffmpeg.audio_codec = 'NONE'
scene.view_settings.view_transform = 'Standard'
scene.render.filepath = str(OUT / 'gel_polish_lapohka_shot4_285_375_preview')

bpy.ops.render.render(animation=True)

# Blender appends the frame range to movie output; fold it back to a stable name.
written = OUT / f'gel_polish_lapohka_shot4_285_375_preview{F_START:04d}-{F_END:04d}.mp4'
final = OUT / 'gel_polish_lapohka_shot4_285_375_preview.mp4'
if written.exists():
    final.unlink(missing_ok=True)
    written.rename(final)
print('PACKAGE_COMPLETE', final, f'{width}x{height}', len(files))
