# Bossa-inspired portrait polish sequence

**Shot 01 update:** `scenes/gel_polish_bossa_shot01_0_125.blend` is the single retained Shot 01 file. It contains the latest opaque loaded brush, smoothly wetted ferrule, continuous sticky film, and clear threaded neck with lacquer visible inside. The bridge stays attached through frame 125; refined Shot 02 continues the withdrawal and releases the film in its opening frames.

See [Shot 01 controls and review utilities](bossa_shot01_controls.md) and the [126 extracted original frames](../references/bossa_hydraboost_shots/shot01_frames/README.md). Earlier Shot 01 versions and temporary Bossa review renders have been removed. Regenerate reviews from the retained scene when needed.

**Shot 05 update (2026-10-24):** the radial array now uses nine original-size bottles, separate orbit and cap-axis motion, a fast opening pullback and subtle late push-in. Unique lacquer cores, the approved finish, soft window shade and opaque peripheral beads replace the first pass. See [Shot 05 controls and render settings](bossa_shot05_controls.md). Geometry checks pass and the frame-375 rendered viewport was inspected; the full-quality sequence remains to be rendered.

**Shot 06 update (2026-10-24):** the floating array now follows all 22 source frames with two staggered columns, opposing cap angles, slow upward travel and slight perspective enlargement. Bottles retain original scale, unique lacquer cores and the approved Lapohka finish, with soft window-blind shade. See [Shot 06 controls and render settings](bossa_shot06_controls.md). The user approved the rendered viewport appearance; no final sequence render was launched during the update.

**Shot 07 update (2026-10-25):** the closer array view carries Shot 06's unique lacquer cores, finish, lighting and window shade into approximately 1.504× closer framing, upward drift and a gentle push-in. See [Shot 07 controls](bossa_shot07_controls.md). Placement and clearance checks pass; the current composition was inspected in Solid view and still needs a shaded appearance check.

**Shot 02 update:** `scenes/gel_polish_bossa_shot02_126_170.blend` now uses the approved Shot 01 product finish and a macro composition measured from all 45 reference frames. The brush and bottle tilt in opposing directions, the film releases around frames 129-130, and the rounded loaded tip settles above the mouth. See [Shot 02 controls](bossa_shot02_controls.md). Shots 03-04 and 08-09 remain the first pass described below. The cut from Shot 02 into Shot 03 still needs matching.

This authored first-pass sequence adapts the staging and timing of the Bossa
HydraBoost reference to the existing Hang Pure cat-eye polish product. It uses
the tall fluted gold cap, round lacquer face, and bristle applicator. Each shot
is a separate Blender file, following the Lapohka project structure.

**Shot 10 update (2026-10-23):** the trio finale follows all 93 source frames: eased hero landing, outward rear-bottle reveal, then a grounded hold. It now uses the approved Lapohka lacquer finish, original-scale bottles and a perspective camera. See [Shot 10 controls and review status](bossa_shot10_controls.md). Motion and geometry checks pass; the latest perspective revision still needs a shaded animation review.

Shots 01, 02, 05, 06, 07 and 10 are configured for **2160 x 3840, 9:16, 25 fps** high-quality image sequences; see the [shared manual-render guide](bossa_render_settings.md) for settings and output paths. Shots 03-04 and 08-09 retain **1080 x 1920, 9:16, 25 fps** settings. The ten shots
retain the reference's global frame numbers, covering f0–749 without gaps:
750 frames, or 30 seconds. Blender frame ranges below are inclusive. Scene
files contain the initial sequence and the enhancements noted above; this note does not establish
completion of final animation renders. Review images and motion previews may
use lower resolution and sample counts than the saved production settings.

## Shot files and motion

| Shot file in `scenes/` | Frames | Duration | Adaptation |
| --- | --- | --- | --- |
| `gel_polish_bossa_shot01_0_125.blend` | 0–125 | 5.04 s | Hero introduction: a teal bottle floats into portrait composition with restrained rotation and opaque polish droplets. The cap begins lifting toward the next shot. |
| `gel_polish_bossa_shot02_126_170.blend` | 126–170 | 1.80 s | Refined macro withdrawal: quick camera push, opposing brush/bottle tilt, viscous film release, and a rounded wet tip that remains attached through the settle. |
| `gel_polish_bossa_shot03_171_204.blend` | 171–204 | 1.36 s | Polish drop macro: a dense bead stretches beneath the brush, separates, and rounds as it falls toward the opening. |
| `gel_polish_bossa_shot04_205_315.blend` | 205–315 | 4.44 s | Shimmer droplet field: a close droplet transition reveals suspended opaque polish beads, with parallax, gentle deformation, and moving metallic highlights. |
| `gel_polish_bossa_shot05_316_403.blend` | 316–403 | 3.52 s | Refined nine-bottle pinwheel: rapid opening pullback, measured orbit with independent cap angles, gentle late push-in, unique lacquer cores and peripheral polish beads. |
| `gel_polish_bossa_shot06_404_425.blend` | 404–425 | 0.88 s | Refined array A: opposing two-column stagger, original-scale bottles, measured upward drift and subtle perspective enlargement. |
| `gel_polish_bossa_shot07_426_450.blend` | 426–450 | 1.00 s | Refined closer cut of Shot 06: 1.504× framing, upward drift and gentle push-in; approved lacquer finishes and window shade retained. [Controls](bossa_shot07_controls.md). |
| `gel_polish_bossa_shot08_451_496.blend` | 451–496 | 1.84 s | Floating hero: one closed bottle turns and descends among drifting polish droplets. |
| `gel_polish_bossa_shot09_497_656.blend` | 497–656 | 6.40 s | Magnetic finish reveal: a macro polish bead and moving cat-eye highlight lead into a continuous floating-bottle reveal. This replaces the reference's botanical orb. |
| `gel_polish_bossa_shot10_657_749.blend` | 657–749 | 3.72 s | Trio finale: the teal hero settles in front of complementary bottles, then holds a compact portrait arrangement with lower-frame space for website copy. |

The rack and sample board are omitted from this adaptation. The original
Lapohka shot files and reusable product asset remain separate from these shots.

## Materials and small-scale motion

The lacquer and floating polish droplets are opaque, densely pigmented
cat-eye polish. Their material transmission is zero and alpha is one. The
product's protective front lens may remain transparent; its transparency does
not imply clear polish. Teal, plum, and warm complementary shades share the
product's metallic finish direction.

Native Blender object keyframes and shape keys provide controlled bottle
travel, cap withdrawal, bristle flex, bead elongation, pinch-off, and droplet
settling. Small delayed motions should decay rather than oscillate uniformly.
Droplet motion is art-directed for the camera. This sequence has **no LiquiGen
dependency** for its controlled motion. A future shot requiring sustained
pouring or complex fluid collisions would need a separate simulation decision.

Magnetic bands and fine pigment should respond to light and viewing angle,
with texture coordinates attached to the surface. Do not animate noise seeds
to manufacture shimmer. Avoid transparent serum bubbles or a pipette in the
polish close-ups.

## Editing and dependencies

Shot-specific editable controls use the corresponding naming prefix
`BOSSA01_`, `BOSSA02_`, through `BOSSA10_`. Inspect each scene's Outliner and
animation data for the bottle/group roots, brush controls, droplet objects,
camera, and lighting controls. Object transforms control rigid motion;
available shape keys control local deformation. The camera sets portrait
framing and the lights set the moving specular highlights. Local material
controls allow shot-specific color or finish adjustments.

Reusable product content is linked from the existing asset library, with
shot-local controls or overrides where animation and material variation are
needed. Keep linked dependencies relative to the shot file and preserve the
shared asset. Each separate scene can be opened, revised, and rendered on its
own. Render destinations follow the repository convention:
`renders/<shot file stem>/frames/`.

## Review priorities

- Check the full bottle silhouette and readable lacquer face at phone size.
  Hero and final-trio compositions should retain comfortable side margins.
- Keep website copy space clear during the final hold. Cropped repetitions in
  the diagonal arrays are deliberate; cropping the final hero is not.
- Check cap, stem, and bristle alignment and bottle-opening clearance during
  withdrawal. Inspect the drop separation in consecutive frames.
- Keep opaque droplets from covering the product face. Use their differing
  depths and small rotation offsets to establish motion without visual clutter.
- Review adjacent shots for matching shade, motion direction, and transition
  timing. Preserve all 750 frames when assembling the sequence.
- Treat still and motion reviews as first-pass checks. Final render readiness
  requires visual approval of the animation, material response, and framing.

## Reference

Timing and composition were studied from **Victor Bandeira / Bossa Skin Care,
Bossa HydraBoost**, [original film](https://vimeo.com/954255078). The source
clips, exact extraction boundaries, and contact sheet are indexed in
[`references/bossa_hydraboost_shots/README.md`](../references/bossa_hydraboost_shots/README.md).
The polish sequence uses the project's existing product assets and its own
materials and animation; the reference film remains attributed to its creator.
