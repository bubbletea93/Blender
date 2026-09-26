# Shot 3 liquid clearance correction

Status: new caches imported, full-range geometry validation passed, and review video completed.
Current Blender delivery: `scenes/gel_polish_lapohka_shot3_199_284_liquigen_v010_clearance.blend`.
The original v009 Blender scene and caches are preserved.

The raw new simulation clears the original lower-right core defect at f246-248,
but still crossed the glass/core on some fast-entry frames. The Blender water
object therefore has a non-destructive `Keep water outside bottle` Geometry
Nodes modifier, after the Alembic reader and before tank-boundary removal.
It projects intruding vertices to the validated collider envelope plus 0.25 mm.
The hidden 1,066-triangle collider follows the detailed bottle rigidly and is a
required modifier dependency. Its geometry does not appear in the render.

All 86 output frames and five nonsequential subframes have zero detected liquid
edge crossings with FrontLens and Lacquer. Framing passes; maximum bottle/source
position error is 0.006 mm. Both archives import as frames 0-154 at 60 fps.
The 256-sample comparison at f246-248 removes the former lower core crescent.
Review video: `renders/shot3_liquigen_review/v010_clearance_preview.mp4`.
All 86 frames are rendered at 960 × 540, 128 Cycles samples, 30 fps. The saved
production scene retains 1920 × 1080 resolution. Blender 5.1 intermittently
crashed during multi-frame background rendering; rendering the remaining frames
in separate processes completed successfully.
Report: `renders/shot3_liquigen_review/v010_clearance_validation.json`.

## Production video delivery

Completed the entire f199-284 shot at native 3840 × 2160, 30 fps (86 frames,
2.867 seconds). Rendered with up to 1,024 Cycles samples, adaptive threshold
0.002, minimum 64 samples, and OpenImageDenoise HIGH with accurate albedo/normal
prefiltering. Original animation, camera, lighting, and liquid timing are retained.

- Master: `renders/lapohka/shot3_f199-284/lapohka_s3_f199-284_liquid_clearance_4k_v009_master.mov`
  (ProRes 4444 XQ, 4:4:4, 10-bit encoder input).
- Playback: `renders/lapohka/shot3_f199-284/lapohka_s3_f199-284_liquid_clearance_4k_v009.mp4`
  (H.264, CRF 12, slow preset).
- Lossless display-referred sources: `renders/shot3_liquigen_review/v010_production_4k/`
  (16-bit RGB PNGs; AgX look baked in).
- Delivery metadata: the matching `_manifest.json` beside the videos.

Render version v009 follows the shot's video numbering; its source scene is
the v010 clearance scene. Both videos decode all 86 frames without errors.
The encoder preserves sRGB transfer metadata and uses BT.709 primaries/YUV
matrix. Opening, entry, underwater, former glare frames f246-248, and closing
images were inspected at production resolution. One Blender crash at f227
was recovered by a successful fresh-process retry. No frame was substituted.
Production overrides are recorded per frame; the editable scene's saved render
resolution remains 1920 × 1080.

Open `scenes/gel_polish_lapohka_shot3_199_284_liquigen_v010_clearance.liquigen`.
The project already references
`renders/shot3_liquigen_review/inputs/shot3_proxy_clearance_v010.fbx`.
No replacement of the detailed render model is required.

The revised collider has 535 vertices and 1,066 triangles, is closed/manifold,
and encloses all 836,878 evaluated vertices of the metal body, front lens,
lacquer and cap. Minimum clearance is 1.5 mm (1.77 mm to the lacquer).
The separate body and cap envelopes are united into one mesh to preserve the
neck shape. All 78 original source poses survive FBX reimport with maximum
vertex error below 0.000065 mm. The current delivery clock and camera stay intact.

The simulation retains 2.5 mm voxels, 60 Hz and four substeps. Imported collider
resolution increases from 200% to 400% (0.625 mm SDF spacing). Global voxel
resolution is retained to avoid an eightfold increase in pool cell count.
Meshing Snap to Colliders is enabled with distance 1.5 voxels, five iterations
and margin 0.1 voxel. This controls mesh placement at collision boundaries;
see [LiquiGen meshing documentation](https://docs.jangafx.com/liquigen/pages/references/node_list.html#snap-to-colliders).

## Regenerating the export

1. Open the v010 project above in LiquiGen.
2. Reset the timeline/simulation to frame 0.
3. Select both `SHOT03 Mesh Alembic` and `SHOT03 Secondary Alembic`, then use
   **Export Selected** in Node Details. Both are configured for 155 samples,
   solver frames 0-154 at 60 Hz, stride 1, with framerate compensation enabled.
4. Wait for both exports to finish. They write to
   `renders/shot3_liquigen_review/cache_v010_clearance/`.

The user completed these exports. During setup, UI Open returned `approval_required`
(trusted action-time confirmation required); native host-command bridge is
unavailable. No denied UI action was retried through another input route.

## Timing and acceptance

Both archives contain the expected 60 Hz range. In Blender, cache.frame
is expressed in scene frames: at scene 30 fps keep `source_seconds * 30`, not
`source_seconds * 60`. Retain the -0.300 m Z cache offset. Import into a separate
review scene/version before replacing the approved v009 delivery. The current
v010 file already references the new caches and retains the original timing.

Check all delivered frames for liquid intersections with FrontLens and Lacquer,
including 246-248 and nonsequential subframes. Render a sequence at sufficient
samples and compare the lower-right core; geometry clearance does not alone
prove that all unwanted optical variation is resolved.

Reports: `renders/shot3_liquigen_review/inputs/shot3_proxy_clearance_v010_validation.json`
and `renders/shot3_liquigen_review/v010_clearance_readback.json`.
