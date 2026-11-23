# Bossa Shot 02 controls

Manual animation rendering and output naming are documented in [Bossa render settings](bossa_render_settings.md).

The retained scene is [gel_polish_bossa_shot02_126_170.blend](../scenes/gel_polish_bossa_shot02_126_170.blend): **2160 x 3840, 25 fps, frames 126-170**. The 45-frame shot lasts 1.80 seconds. It carries the approved Shot 01 product finish into a closer view of the coated brush withdrawing from the clear threaded neck.

The [original Shot 02 frame study](../references/bossa_hydraboost_shots/shot02_frames/README.md) includes all 45 source frames, portrait crops, contact sheets, and measured image landmarks. The original is a tall serum bottle with a glass pipette. This adaptation retains the round nail-polish bottle's proportions, flat brush, and opaque glitter lacquer. The background beads are softly defocused, desaturated opaque polish pearls, whereas the source uses clearer serum-like orbs.

## Motion and camera

The camera pushes into the product quickly during frames 126-140, then settles into a slower drift. Bottle and applicator use opposing tilt directions. The bottle's upper end leans right, increasing from 8 to 18 degrees; the applicator's upper end leans left, increasing from 3 to 18 degrees. The long cap moves partly above the portrait frame while the bottle's lower body moves below it. The differing product proportions mean the cap silhouette cannot match the serum reference exactly.

The camera uses an 85 mm perspective lens, vertical sensor fit with a 36 mm sensor height, and depth of field at f/8. Its apparent image height shrinks from 165 mm at frame 126 to approximately 111 mm at frame 140 and 110 mm for the hold. `BOSSA02_CameraFocus` follows a point 65 percent of the way from the bottle neck toward the fitted brush-tip target. The neck and applicator remain readable while foreground and background beads blur at their actual depths.

The cap continues the local lift from Shot 01: approximately **69 mm at frame 126 to 73 mm at frame 170**, with no downward reversal. This preserves withdrawal progress across the cut; the camera and object staging change for the macro view. Shot 03's opening has not yet been matched to the refined Shot 02 ending.

| Timeline marker | Motion |
| --- | --- |
| 126 - Macro cut / continue wet withdrawal | Continue the loaded brush's withdrawal with a short, sticky film still connected to the mouth. |
| 129 - Film necks and releases | The connecting film narrows sharply and separates around frames 129-130. |
| 135 - Attached bead / air gap established | The brush retains its weighted rounded wet end; the lower film has retracted into the mouth by approximately frame 134. |
| 145 - Ease into floating hold | The gap is established, with a gentle diagonal drift and subtle brush settling. |
| 170 - Cut to drop macro | End with the bead still attached. No detached falling droplet is authored in this shot. |

## Objects and editing controls

| Object / collection | Purpose |
| --- | --- |
| `BOSSA02_BrushHero` | Bottle root, with the reference-based bottle placement and tilt. |
| `BOSSA02_BrushHero_CapLift` | Cap, stem, and bristle parent. Its rotation is solved independently from the bottle tilt. |
| `BOSSA02_BrushHero_ApplicatorStem` | The applicator stem beneath the cap. |
| `BOSSA02_BrushHero_Bristles` | The flat bristle bundle, including the `Viscous drag` shape key. Drag rises briefly during release, then relaxes through the hold. |
| `BOSSA02_BrushHero_LoadedBrushAndBead` | Continuous opaque wet coating over the bristles and ferrule, the upper half of the separating film, and the rounded attached bead. |
| `BOSSA02_BrushHero_RecoilingMeniscus` | The lower half of the film, which contracts into the bottle's lacquer after separation. |
| `BOSSA02_BrushHero_ClearThreadedNeck` | Unified clear neck and substantial screw threads inherited from the approved Shot 01 finish. |
| `BOSSA02_BrushHero_LacquerInsideClearNeck` | Separate opaque polish contents visible through the glass neck. |
| `BOSSA02_09_VISCOUS_WITHDRAWAL` | The two animated gel surfaces. |
| `BOSSA02_11_DEFOCUSED_POLISH_BEADS` | Four camera-relative bead tracks: `Left`, `CrossingForeground`, `RightBackground`, and `UpperRight`. |

The foreground bead crosses down and right during the early withdrawal and leaves the frame. The left bead drifts downward and partly outside the left edge. The smaller right and upper-right beads provide soft background motion.

Both gel objects use one sampled shape key per frame, `Withdrawal 126` through `Withdrawal 170`, with linear interpolation. Their geometry is already transformed into bottle-root coordinates. They remain parented to `BOSSA02_BrushHero`, with identity local transforms; parenting them to the cap would apply the applicator motion twice.

**Rebuild the gel samples after changing cap, stem, or bristle motion.** Editing the cap alone moves the bristles without updating their baked coating. The shaping and motion are native Blender geometry and shape keys; there is no LiquiGen simulation or external fluid cache.

The reconstruction source is [refine_bossa_shot02_reference.py](../scripts/refine_bossa_shot02_reference.py). Its `OBS` table controls the reference-based framing, neck/tip targets, and tilt. `PROFILE` controls the loaded brush and ferrule cross-sections; `gel_samples()` controls necking, separation, recoil, and the retained bead. `background_beads()` controls the peripheral bead trajectories. Running the builder rebuilds Shot 02 from the approved Shot 01 file and replaces the saved Shot 02 scene, so incorporate intended scene edits into the builder before using it to reconstruct the shot.

## Surfaces and light

Shot 02 retains Shot 01's polished gold, reflective product lens, opaque teal cat-eye lacquer, wet ferrule blend, and clear neck. The brush coating, returning film, and interior fill use zero transmission and alpha one. The neck glass uses IOR 1.46 and remains a separate optical volume around the opaque contents. Dense pigment and wet highlights supply the lacquer appearance.

The residual lacquer now extends up the shaft to approximately **local Z45 mm**, just below the cap, rather than ending at Z24 mm. A shallow uneven wet edge and gently varying film thickness join continuously into the heavier loaded brush. Only a short area directly below the cap remains dry. This coating is authored geometry, not a fluid simulation. Wet-stem containment is checked from local Z16.3 to43.1 mm throughout the shot.

A separate [LiquiGen withdrawal calibration](bossa_shot02_liquigen_withdrawal.md) uses closed collision inputs to explore viscosity, adhesion, and bridge breakup. Its experimental geometry and caches are independent of this production scene.

The [authored coating review](../references/brush_liquid_motion/authored_coating_review/README.md) builds a separate candidate from this current scene. The completed drainage pass passed 45 integer-frame, 24 half-frame and two shutter-boundary checks, but its rounded tip still had a visible waist. A localized smoother transition is prepared for the next manual review. The production scene has not adopted either candidate. The prior preview and measurements are retained under `authored_coating_review/reviewed_drainage_pass/`.

The scene retains the approved reflection environment and cards. Exposure is -0.20 for the bright macro presentation. `BOSSA02_SoftBackgroundOpaquePearl` reduces background-bead saturation to 0.35 in its hue/saturation node while retaining opaque polish shading.

## Rendering and review

For the final image sequence, use **Render > Render Animation (Ctrl+F12)**. The saved production settings are:

- Portrait 4K: **2160 x 3840 at 100 percent**.
- **25 fps**, frame step 1, frames **126-170 inclusive**.
- Cycles, up to **1,024 samples**, adaptive noise threshold **0.002**, and **64 minimum samples**.
- **16-bit RGB PNG**, with motion blur enabled and shutter **0.35**.
- Output: `//../renders/gel_polish_bossa_shot02_126_170/frames/frame_`, producing `frame_0126.png` through `frame_0170.png`.

The [production frames folder](../renders/gel_polish_bossa_shot02_126_170/frames/) is separate from quick review renders. Overwrite is disabled; remove any completed production frames that you intend to replace before rerendering them.

Review artifacts are in [renders/gel_polish_bossa_shot02_126_170/reviews/](../renders/gel_polish_bossa_shot02_126_170/reviews/):

- [Shot 02 motion review](../renders/gel_polish_bossa_shot02_126_170/reviews/shot02_review.mp4).
- [Reference comparison](../renders/gel_polish_bossa_shot02_126_170/reviews/shot02_reference_comparison.jpg).
- [Build report](../renders/gel_polish_bossa_shot02_126_170/reviews/build_report.json).
- [Validation report](../renders/gel_polish_bossa_shot02_126_170/reviews/validation.json).

The review rendering helper uses 25 percent resolution (540 x 960), 64 samples, and 8-bit PNGs. These temporary render overrides are not saved over production settings. To regenerate the complete review frame sequence without rebuilding the scene, run the builder through background Blender with `-- --render-only --render`.

Then run `python scripts/package_bossa_shot02_review.py` to create the MP4 and labeled comparison sheet. The packager verifies the saved scene matches the validation report and decodes all 45 video frames. Intermediate review PNGs can be removed after packaging; the video, comparison, and reports retain the review results.

[validate_bossa_shot02.py](../scripts/validate_bossa_shot02.py) reopens the production scene without saving it and writes the validation report. The refined scene passed checks at all 45 integer frames: bristle and sampled wet-stem containment, closed outward-oriented gel meshes, clear neck and opaque fill geometry/materials, an established air gap from frame 134, continuous upward cap progress, and existing dependencies. Validation also checks the production frame range, resolution, PNG output, hierarchy, and animation ownership. Its scope does not exhaustively test subframe motion-blur deformation or surface self-intersection; the rendered motion review provides the accompanying visual check.
