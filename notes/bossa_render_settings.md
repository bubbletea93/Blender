# Bossa manual animation rendering

Saved and verified on 2026-10-26: all six canonical files were reopened to confirm the settings, first/last output filenames, output directories and external dependencies. Blender was returned to Shot 07 at frame 432. No render was started.

Production settings for the six enhanced shots: **01, 02, 05, 06, 07 and 10**. Open the canonical scene below and use **Render > Render Animation (Ctrl+F12)** when ready. **F12** renders a single frame for an appearance check. This setup does not establish final visual approval; no rendering or encoding is performed by the settings update.

## Scenes and output locations

Paths are relative to the project root. Each output folder matches its scene filename. Frame ranges are inclusive and use the reference's absolute timeline numbers, not a new sequence starting at one.

| Shot | Canonical scene in `scenes/` | Frames | Images | Output in `renders/` |
| --- | --- | --- | --- | --- |
| 01 | [gel_polish_bossa_shot01_0_125.blend](../scenes/gel_polish_bossa_shot01_0_125.blend) | 0–125 | 126 | `gel_polish_bossa_shot01_0_125/frames/frame_####.png` |
| 02 | [gel_polish_bossa_shot02_126_170.blend](../scenes/gel_polish_bossa_shot02_126_170.blend) | 126–170 | 45 | `gel_polish_bossa_shot02_126_170/frames/frame_####.png` |
| 05 | [gel_polish_bossa_shot05_316_403.blend](../scenes/gel_polish_bossa_shot05_316_403.blend) | 316–403 | 88 | `gel_polish_bossa_shot05_316_403/frames/frame_####.png` |
| 06 | [gel_polish_bossa_shot06_404_425.blend](../scenes/gel_polish_bossa_shot06_404_425.blend) | 404–425 | 22 | `gel_polish_bossa_shot06_404_425/frames/frame_####.png` |
| 07 | [gel_polish_bossa_shot07_426_450.blend](../scenes/gel_polish_bossa_shot07_426_450.blend) | 426–450 | 25 | `gel_polish_bossa_shot07_426_450/frames/frame_####.png` |
| 10 | [gel_polish_bossa_shot10_657_749.blend](../scenes/gel_polish_bossa_shot10_657_749.blend) | 657–749 | 93 | `gel_polish_bossa_shot10_657_749/frames/frame_####.png` |

The Blender output path is `//../renders/<scene filename without .blend>/frames/frame_`. Blender automatically appends the four-digit frame number and `.png`, for example `frame_0426.png`. Keep the scene in `scenes/` so this relative path resolves correctly. The six shots contain **399 images** in total.

## Shared production settings

| Setting | Value |
| --- | --- |
| Resolution | 2160 × 3840, 100%, square pixels |
| Timing | 25 fps, frame step 1 |
| Engine | Cycles, GPU Compute |
| Sampling | 1024 maximum samples; adaptive threshold 0.002; minimum 64 samples |
| Denoising | OpenImageDenoise, High quality, accurate prefilter, albedo and normal guidance |
| Image output | PNG, RGB, 16-bit, compression 15%, automatic file extension |
| Render area | Full frame; border/crop disabled; Simplify disabled |
| Motion blur | Enabled, centered shutter, 0.35 |
| Animation memory | Persistent data enabled |
| Existing files | Overwrite disabled; placeholders disabled |

Each shot retains its camera, depth of field, materials, lighting and color-management choices.

## Rendering and resuming

Open a scene and press **Ctrl+F12**. Images are saved into its `frames/` folder as they finish. If interrupted, reopen the same scene and run Render Animation again; existing frame filenames are skipped. Remove any incomplete or corrupt frame before resuming so it is rendered again.

Shot 01 already contains all 126 production frames and its packaged video/master. With Overwrite disabled, rendering it again skips those frames. To deliberately replace the sequence, move the existing frames out of that shot's `frames/` folder yourself first. Preserve the existing video and master until a replacement is complete. If a shot's appearance or render settings change, start a fresh complete sequence rather than mixing old and new frames.

Image sequences are the render deliverable. Video encoding is a separate step after the desired frames finish.

## Completed video deliveries

All six image sequences and their video deliveries are complete. Each video is 2160 × 3840 at 25 fps, with the source frame range preserved. Playback copies use H.264, CRF 14, the slow preset and fast-start playback. Editing masters use ProRes 4444 XQ. The original displayed color is preserved with a BT.709 YCbCr matrix and sRGB transfer tags; no creative grading is applied.

| Shot | Duration | Playback MP4 | ProRes master |
| --- | --- | --- | --- |
| 01 | 5.04 s | [Hero](../renders/gel_polish_bossa_shot01_0_125/bossa_s01_f0-125_hero_4k.mp4) | [Master](../renders/gel_polish_bossa_shot01_0_125/bossa_s01_f0-125_hero_4k_master_prores4444xq.mov) |
| 02 | 1.80 s | [Brush withdrawal](../renders/gel_polish_bossa_shot02_126_170/bossa_s02_f126-170_brush_withdrawal_4k.mp4) | [Master](../renders/gel_polish_bossa_shot02_126_170/bossa_s02_f126-170_brush_withdrawal_4k_master_prores4444xq.mov) |
| 05 | 3.52 s | [Pinwheel](../renders/gel_polish_bossa_shot05_316_403/bossa_s05_f316-403_pinwheel_4k.mp4) | [Master](../renders/gel_polish_bossa_shot05_316_403/bossa_s05_f316-403_pinwheel_4k_master_prores4444xq.mov) |
| 06 | 0.88 s | [Diagonal array](../renders/gel_polish_bossa_shot06_404_425/bossa_s06_f404-425_diagonal_array_4k.mp4) | [Master](../renders/gel_polish_bossa_shot06_404_425/bossa_s06_f404-425_diagonal_array_4k_master_prores4444xq.mov) |
| 07 | 1.00 s | [Array close-up](../renders/gel_polish_bossa_shot07_426_450/bossa_s07_f426-450_array_closeup_4k.mp4) | [Master](../renders/gel_polish_bossa_shot07_426_450/bossa_s07_f426-450_array_closeup_4k_master_prores4444xq.mov) |
| 10 | 3.72 s | [Trio finale](../renders/gel_polish_bossa_shot10_657_749/bossa_s10_f657-749_trio_finale_4k.mp4) | [Master](../renders/gel_polish_bossa_shot10_657_749/bossa_s10_f657-749_trio_finale_4k_master_prores4444xq.mov) |

All 12 videos were decoded completely without errors and checked for frame count, timing, resolution and color tags. Each shot folder contains its source/output checksum manifest beside the videos. Shot 01's existing delivery was reused after its source and output hashes matched the manifest. Source PNGs and Blender scenes were retained; no new Blender renders were needed for packaging.
