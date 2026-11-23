# Bossa Shot 01 controls

Manual animation rendering and output naming are documented in [Bossa render settings](bossa_render_settings.md).

The retained scene is `scenes/gel_polish_bossa_shot01_0_125.blend`: 2160 x 3840, 25 fps, frames 0-125. It contains the latest loaded brush, wet ferrule transition, clear threaded neck, and opaque lacquer contents.

Earlier Shot 01 scene versions, Blender backups, and temporary Bossa review renders have been removed. The original Bossa source video and extracted reference frames remain in `references/bossa_hydraboost_shots/`.

## Geometry and motion controls

`BOSSA01_09_LOADED_BRUSH_AND_MENISCUS` contains the continuous brush coating and
bridge. `BOSSA01_10_CLEAR_NECK_AND_CONTENTS` contains the unified glass neck
and opaque interior fill. These objects follow the hero bottle root; the gel's
shape keys bake the cap and brush transforms into its surface positions.

| Object / control | Authored dimensions or behavior |
| --- | --- |
| `BOSSA01_Hero_LoadedBrushAndGelBridge` | Broad, flat brush profile, approximately 6.8 mm wide and 2.8 mm thick through its loaded middle before subdivision; continuous film connects its tip to the mouth. |
| Wet ferrule profile | Extends to brush-local Z = 24 mm, with its top buried in the 1.55 mm-radius stem. The rounded upper collar widens smoothly into the flat brush. |
| `Withdrawal 099` through `Withdrawal 125` shape keys | One sampled gel shape per withdrawal frame, using linear interpolation. The mouth anchor settles at bottle-local Z = 58.45 mm beneath the lacquer meniscus. |
| `BOSSA01_Hero_Bristles` | Static local Z rotation is -100 degrees to show the loaded brush's broad face; existing animation keys are retained. |
| `BOSSA01_Hero_ClearThreadedNeck` | Boolean union of the v004 neck and thread into one optical volume: 9.6 mm bore, 1.19 mm nominal wall, 2.35 mm thread pitch, and 13.46 mm crest diameter. |
| `BOSSA01_Hero_LacquerInsideClearNeck` | Separate opaque fill, with 0.04 mm nominal wall clearance and a gently raised meniscus spanning Z = 58.56–58.75 mm. |

The original opaque gold neck and thread objects remain in the scene but are
hidden from viewport and render. The interim wet-lip torus is also hidden,
because the interior lacquer supplies the visible meniscus. The original
linked product asset remains separate from these shot-local changes.

The bridge stays attached at the end of Shot 01. There is no pinch-off in this
shot; [refined Shot 02](bossa_shot02_controls.md) continues the cap lift from
69 mm and releases the film in its opening frames. Existing cap, bottle, camera, and bristle keyframes are retained,
while the new gel uses baked shape keys. Rebuild the gel animation after changing
the source brush or cap motion. This authored motion has no LiquiGen dependency.

## Surface controls

`BOSSA01_DenseWetCatEyeGel_v006` uses dense teal, blue, and silver pigment facets
with restrained violet flecks beneath a smooth wet coat. Fixed UV coordinates
keep the pigment attached to the deforming surface. The polish has zero
transmission and alpha one; highlights come from its metallic pigment and coat.

`BOSSA01_LoadedGel_WetFerruleBlend_v006` blends the stem's color, metallic weight,
and roughness into the dense gel over UV Y = 0.005–0.055. This smooths the visible
paint boundary while keeping the whole gel surface opaque. The wet coat weight
increases from 0.10 at the upper collar to 0.40 on the loaded brush.

`BOSSA01_ClearThreadedNeck_Glass_v006` uses IOR 1.46, roughness 0.025, and full
transmission. The neck glass transmits light; the contents and brush gel
remain separately opaque. Joining the neck and thread avoids overlapping
internal glass surfaces. The scene allows at least 12 transmission bounces
and 16 total bounces for the thick threaded volume.

## Checking and rendering

Open the retained scene to edit it. Its latest saved state is the working source for this shot.

For the final image sequence, use **Render > Render Animation (Ctrl+F12)**. Saved settings are portrait 4K (2160 x 3840 at 100%), 25 fps, frames 0-125 inclusive (126 images), Cycles GPU rendering on the RTX 4090 via OptiX, up to 1,024 samples, adaptive noise threshold 0.002 with 64 minimum samples, and OpenImageDenoise with accurate albedo/normal guidance. Light paths use 16 total bounces, 8 glossy bounces, and 12 transmission bounces. Existing AgX color, exposure, camera, and 0.35-shutter motion blur are preserved.

Output is **16-bit RGB PNG**, written to `//../renders/gel_polish_bossa_shot01_0_125/frames/frame_` relative to the scene. The images will be `frame_0000.png` through `frame_0125.png`. Overwrite is disabled so rerunning Render Animation skips completed frames; remove any frames you want to replace before rerendering them. Persistent data is enabled for animation rendering.

After rendering the sequence, run `python scripts/package_bossa_shot01_production.py`. It checks all 126 portrait 4K, 16-bit frames and encodes a high-quality H.264 MP4 (CRF 14, slow preset, fast-start playback) plus a ProRes 4444 XQ editing master beside `frames/`. Output names are `bossa_s01_f0-125_hero_4k.mp4`, `bossa_s01_f0-125_hero_4k_master_prores4444xq.mov`, and `bossa_s01_f0-125_hero_4k_manifest.json`. Both videos retain 25 fps, 2160 x 3840 resolution, and the rendered color appearance without creative grading. The utility decodes every output frame before delivering the files and records source/output checksums in the manifest. It uses the existing image sequence without rendering again.

Run `scripts/validate_bossa_shot01_clear_neck.py` in background Blender to check the retained scene. Run `scripts/render_bossa_shot01_clear_neck.py` in background Blender, then `python scripts/package_bossa_shot01_clear_neck.py` to regenerate a portrait review and a slowed close-up when needed. These utilities use `renders/gel_polish_bossa_shot01_0_125/reviews/`, separate from the final `frames/` folder, and do not require older scene versions or working snapshots. Render preview settings are not saved over the scene.

The previous construction helpers remain as source code. Their intermediate working snapshots have been removed; they require a newly prepared baseline if used to rebuild the shot. The general sequence builder produces the initial animation pass and should not be run over the refined scene unless rebuilding deliberately.

Prior verification covered all 26 withdrawal frames: the bristles and coated stem stayed inside the gel, the active gel/neck/fill meshes were closed and consistently oriented, the polish remained opaque, and the threaded neck was transmissive. Refined Shot 02 carries these surfaces into its macro withdrawal.
