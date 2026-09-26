# Shot 3: LiquiGen delivery

Current corrected delivery: [v010 liquid clearance](shot3_liquid_clearance_v010.md).
Open `scenes/gel_polish_lapohka_shot3_199_284_liquigen_v010_clearance.blend`.
New 60 Hz caches and an animated clearance modifier pass the full-shot glass/core
intersection checks. The v009 files described below remain the prior checkpoint.

Open `scenes/gel_polish_lapohka_shot3_199_284_liquigen_v009.blend`.
Frames 199–284, 30 fps, 1920×1080, Cycles, 128 samples.

The scene contains the detailed bottle and the synchronized LiquiGen liquid,
bubbles, foam and spray. Original collider rotations have been restored and the
cache collection is enabled. The earlier gentle timing and camera arc are retained.
The background is black. A forest environment emitter lights
only the bottle; studio lights illuminate the liquid and bubbles. There are
240 additional animated ambient bubbles to fill the sides of the underwater view.

## Source files and dependencies

- `scenes/gel_polish_lapohka_shot3_199_284_liquigen_v009_continuous.liquigen`
  is the editable LiquiGen 1.1.1 simulation.
- `renders/shot3_liquigen_review/inputs/shot3_proxy800_continuous_v009.fbx`
  is the required animated 800-triangle collider. This one source file is
  explicitly tracked despite the generated-output directory being ignored.
- Bottle meshes remain linked to `assets/products/gel_polish_bottle.blend`;
  lighting remains linked/overridden from `assets/lighting/three_point_studio.blend`.
- Bottle objects and their collection are local shot instances with linked mesh
  data. The former collection override was removed so reopening does not restore
  the unused applicator, alternate cap and modeling cutters.
- Shot-specific shaders formerly linked through Shot 2 are now local. Shot 2,
  the studio backdrop and the studio world are no longer dependencies.

Generated Alembic caches are intentionally outside Git. Keep or regenerate these
files in `renders/shot3_liquigen_review/cache_v009_continuous/`:

| File | Bytes |
| --- | ---: |
| `shot3_liquid_0.abc` | 9,054,587,600 |
| `shot3_secondary_0.abc` | 1,259,040 |

Blender uses relative cache paths. LiquiGen stores absolute paths for the FBX
import and the two exporters: on a different checkout location, relink the FBX
and point both exporters at the cache directory above. Export 78 samples with
stride 2, numbering offset 0, and FPS compensation from the 60 Hz simulation.

## Timing and liquid setup

Both archives contain samples 0–77 at 30 fps. A seven-key Bézier curve on
`SHOT03_199_284_Motion["source_seconds"]` drives Travel, Rock, Spin,
LightingFollow and both archive frame overrides. The current [delivery map](shot3_liquigen_timing.json) maps source sample
9 to f199, 14 to f205, 21 to f214, 31 to f225, 47 to f245 and 77 to f284.
After f214, source speed eases from 1× to approximately 0.75–0.8×, removing the
previous early-underwater acceleration to 1.31×. Camera motion, artistic bubbles
and light accents remain on output time.

Synchronization restoration (2026-09-21): the independent Rock and Spin edits
were reverted to the original simulation-source poses. All physical controls now
use the same clock. The gentle descent begins at f214; Camera and Aim retain their
height compensation and sideways arc. This retimes the original simulation without
requiring a new collider or cache. It does not move the source's later physical
turn earlier independently of the liquid.

All 86 output frames match the exported collider within 0.006 mm in position
and the numerical rotation comparison reports zero degrees. Both caches agree
with the shared clock within 0.000004 frames; full-product framing passes.
The live scene was updated and saved with the liquid collection enabled.
Prior live state: `renders/shot3_liquigen_review/shot3_before_sync_restore_20260921.blend`.
Report: `renders/shot3_liquigen_review/sync_restored_validation.json`.
Review: `renders/shot3_liquigen_review/sync_restored_preview.mp4`
(f199-284, 30 fps, 640x360, 16 samples, liquid and simulated bubbles enabled).

The cache parent translates Z by −0.300 m. Cache velocity motion blur remains
disabled until source velocity scaling under retiming is verified. Fractional
archive samples interpolate only where Alembic topology permits. The current
30 Hz caches can still step during slow motion; no denser simulation was exported
as part of the rig revision. The next sampling upgrade is 155 samples at 60 Hz,
exporting every solver step (stride 1) from both exporters with FPS compensation,
then verifying the physical duration and archive time mapping in Blender.

The camera uses the free Add Camera Rigs 1.8.2 Dolly rig, installed from
[the publisher's repository](https://github.com/waylow/add_camera_rigs) at commit
`2fb7b36d52dddc79185de05eb4f87f6aa9e28f7d`. Camera and Aim bones have independent
output-time keys, retaining the established framing drift and adding a shallow
7° arc opposite the bottle's turn. Focus follows the real front lens independently
of the Aim control. Native constraints and drivers render without add-on callbacks.

To adjust the shot:

1. Select `SHOT03_199_284_Motion` and edit `source_seconds` in the Dope Sheet
   or Graph Editor to adjust timing for the bottle, liquid and simulated bubbles
   together. The seven timing keys remain editable.
2. Select `SHOT03_199_284_Dolly_Rig`, enter Pose Mode and edit **Camera** for
   position, **Aim** for composition, or **Camera_Offset** for framing/roll offsets.
   Lens and f-stop are custom properties on the Camera bone.
3. Adjust `SHOT03_199_284_Focus` locally under FrontLens if focus placement needs
   refinement.
4. Rock and Spin use original source rotation driver curves, rather than the
   independent editable actions. Changing their physical angles requires updating
   the collider and simulation; camera adjustments do not.

Native driver response curves retain continuous source motion for Travel, Rock,
Spin and LightingFollow. Driven NLA strip time was tested but produced one
evaluation of lag in Blender 5.1; the delivered rig uses direct drivers instead.
Matching source actions are retained as reference data, with no NLA tracks or
scene scripts required for playback.

Historical editable rotation revisions are preserved in
`shot3_before_earlier_smooth_motion_20260921.blend` and
`shot3_before_sync_restore_20260921.blend` under the review directory. They are
superseded by the synchronized source-driver workflow above.

The previous delivery is preserved at
`renders/shot3_liquigen_review/shot3_before_camera_rig_20260920.blend`, with paths
remapped for that location. Its preview is `continuous_motion_preview.mp4`.
The earlier camera-rig review is `renders/shot3_liquigen_review/camera_rig_preview.mp4`
(f199–284 at 30 fps, 768×432, 24 samples). Production render settings stay at
1920×1080 and 128 samples.

The approved simulation uses a 26 cm deep pool, 2.5 mm voxels, four substeps and
60 Hz solver timing. Its outside drain is disabled. Geometry nodes remove distant
tank walls and floor from the Blender render while retaining the free surface
and bottle cavity. Bubble/foam/spray radii are 0.8/0.35/0.5 mm. Set Material nodes
after the Alembic reader ensure point clouds retain their glass/water materials.

## Cleanup and verification

Removed the Mantaflow domain, emitters, colliders, particle systems, proxy preview
scene, unused backdrop, unused bottle components, obsolete embedded scripts and
unused data. No scripts are required to open or render the delivered scene.
Removed 40 one-off Shot 3 scripts, superseded Blender/LiquiGen projects and proxy
exports, and five obsolete cache directories. Active v009 caches are retained.

At the cleanup checkpoint, reopened the saved file and verified 265 scene objects, one scene, no hidden
objects and no fluid modifiers. Both cache files resolve. Timing checks verified
matching geometry at held frames, resumed motion afterward, finite coordinates
and evaluated particle materials. Cleanup renders at 205, 231 and 284 matched
the prior composition (mean normalized pixel differences below 0.000015).
Review images are in `renders/shot3_liquigen_review/blender_v009/`.
The subsequent camera rig adds its required controls and hidden bone widgets.
The original camera and focus target are replaced, rather than left unused.
The camera-rig report is `renders/shot3_liquigen_review/camera_rig_validation.json`:
all 86 output frames are checked for full-product framing and bottle/proxy
alignment, plus nonsequential subframes and independent camera movement while
physical time is held. The full-quality production animation has not been rendered.

Keyframe simplification (2026-09-20): local action keys were reduced from 544,708
to 26,217 (95.19%, including the Spin Z and shutter refinements below). Dense ambient-bubble curves are fitted within 0.005 mm for
position and 0.0001 for scale, checked at 1/32-frame intervals. Source actions
and physical driver curves only lose redundant collinear samples. The six-key
source clock and twelve camera poses are retained. Camera position and bottle
rotation match the prior version across all 86 frames; two spot renders and a
saved-file reopen check pass. Editors now show selected objects' animation by
default. Reports are `keyframe_simplification.json` and
`keyframe_simplification_reopen.json` in the review directory. A comparison copy
is saved as `shot3_before_key_simplification_20260920.blend` in that directory.

Spin Z refinement: the initial strict reduction rolled back this entire curve
because of floating-point evaluation noise. Its 78 source samples are now six
linear keys at source indices 0, 9, 21, 46, 60 and 77, in both the physical driver
and reference action. These are source indices, not output frames. Maximum
rotation change across all 86 output frames is 0.00000684 degrees. See
`spin_keyframe_reduction.json` for the current count and verification.

The scene-level `Shutter (Render Data)` curve is reduced to three Bézier keys:
f201 = 0.04, f205 = 0.12 and f209 = 0.28, with constant extrapolation outside
the ramp. This is the dense f201–209 channel visible in the user's screenshot;
it is not bottle spin. Quarter-frame samples are replaced by the smooth ramp.
See `shutter_simplification.json` for the numerical difference check. The saved
file is updated; an already-open Blender window must reload it to show the change.
