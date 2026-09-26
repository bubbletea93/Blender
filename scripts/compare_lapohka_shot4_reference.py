"""Reference-vs-render contact sheet for Shot 4, and matching reference stills.

Decodes the reference mp4 through Blender's sequencer (no ffmpeg on PATH) and
tiles it beside the rendered preview frames with numpy alone (no PIL either).

    blender -b --factory-startup --python scripts/compare_lapohka_shot4_reference.py
"""
import bpy
import numpy as np
from pathlib import Path

ROOT = Path('C:/Users/danht/Documents/GitHub/Blender')
REF = ROOT / 'references/lapohka_3d_motion_shots/Lapohka 3D Motion - Shot 4 (f285-375).mp4'
OUT = ROOT / 'renders/shot4_285_375_review'
FRAMES = OUT / 'preview_frames'
F_START = 285
PICKS = [285, 292, 300, 322, 336, 342, 348, 356, 363, 368, 371, 375]
TILE_W, TILE_H, GAP = 400, 225, 6


def extract_reference():
    """Render the picked reference frames out of the mp4 as PNG stills."""
    scene = bpy.context.scene
    scene.sequence_editor_create()
    strip = scene.sequence_editor.strips.new_movie(
        'ref', str(REF), channel=1, frame_start=1, fit_method='ORIGINAL')
    width, height = strip.elements[0].orig_width, strip.elements[0].orig_height
    scene.render.resolution_x, scene.render.resolution_y = width // 4, height // 4
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.view_settings.view_transform = 'Standard'
    for frame in PICKS:
        scene.frame_set(frame - F_START + 1)
        scene.render.filepath = str(OUT / f'reference_{frame}.png')
        bpy.ops.render.render(write_still=True)
    scene.sequence_editor_clear()


def load(path):
    img = bpy.data.images.load(str(path), check_existing=False)
    w, h = img.size
    buf = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(buf)
    out = buf.reshape(h, w, 4)[::-1, :, :3].copy()
    bpy.data.images.remove(img)
    return out


def resize(a, tw, th):
    h, w, _ = a.shape
    yi = (np.arange(th) * (h / th)).astype(np.int32)
    xi = (np.arange(tw) * (w / tw)).astype(np.int32)
    return a[yi][:, xi]


def sheet():
    rows = len(PICKS)
    width = 2 * (TILE_W + GAP) + GAP
    height = rows * (TILE_H + GAP) + GAP
    canvas = np.full((height, width, 3), .07, np.float32)
    for row, frame in enumerate(PICKS):
        for col, path in enumerate([OUT / f'reference_{frame}.png',
                                    FRAMES / f'shot4_{frame:04d}.png']):
            if not path.exists():
                continue
            tile = resize(load(path), TILE_W, TILE_H)
            y = GAP + row * (TILE_H + GAP)
            x = GAP + col * (TILE_W + GAP)
            canvas[y:y + TILE_H, x:x + TILE_W] = np.clip(tile, 0, 1)
    img = bpy.data.images.new('cmp', width, height, alpha=False)
    img.pixels.foreach_set(
        np.concatenate([canvas[::-1], np.ones((height, width, 1), np.float32)], 2).ravel())
    img.filepath_raw = str(OUT / 'shot4_reference_comparison.png')
    img.file_format = 'PNG'
    img.save()
    print('COMPARE_COMPLETE', img.filepath_raw)


OUT.mkdir(parents=True, exist_ok=True)
extract_reference()
sheet()
