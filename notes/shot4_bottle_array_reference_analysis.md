# Shot 4: bottle-specific adaptation

Reference: `references/lapohka_3d_motion_shots/Lapohka 3D Motion - Shot 4 (f285-375).mp4`.
Current scene: `scenes/gel_polish_lapohka_shot4_285_375_bottle_array_v004_fine_shimmer.blend`.
91 frames at 30 fps; saved output 3840 × 2160.

## What the original actually shows

The full reference is a repeated array of cans, not a solitary macro product.
Several products extend beyond the picture edges. Warm directional light,
soft shadows and selective focus connect the arrangement to a pale stage.
The existing `lapohka_shot4_f285-375_motion_breakdown.md` and original Shot 4
scene describe a tightly cropped earlier study. They are preserved, but that
crop is not the composition used for this new scene.

| Frames | Observation from the full reference | Bottle adaptation |
| --- | --- | --- |
| 285–300 | Labels sweep around the cans, blurred at first, then resolve; products already fill the picture. | Bottles arrive already moving in short staggered glides, with a small rock and planar turn. |
| 300–321 | Remaining rotation damps down. | One small overshoot and counter-settle; faces remain visible. |
| 321–336 | Diagonal arrangement holds so the range reads clearly. | Diagonal palette hold with the aubergine bottle central. |
| 336–348 | The composition rotates toward vertical columns and opens up. | Camera unrolls from 35 degrees to level and pulls back. |
| 348–357 | Upright rows/columns become legible. | Brief front-facing collection display. |
| 357–375 | Products stream vertically in staggered lanes, continuing into the cut. | Alternating columns glide in opposite directions, with staggered release. |

Timing is an editorial interpretation from decoded full frames, not a claim
to recover the original 3D camera or physics. Reference contact sheets are
under `renders/shot4_bottle_adaptation_v002/reference_*.png`.

## Why replace the roll

A can has an almost constant circular cross-section along its length. This
bottle has a wide, shallow body, a narrower long cap, and a distinct lacquer
front. Sustained cylinder-like rolling would change its contact point,
wobble strongly, and repeatedly hide the shade.

The chosen entrance lays the bottle on its back and uses a short glide with
a restrained rocking settle. It carries the reference's fast-to-calm rhythm
while showing the product's recognizable shape and color. This is authored
product choreography, not a rigid-body physics simulation.

## Reused assets and scene controls

- Exact four-part assembly from approved Shot 3 v010: body, cap, front glass,
  and lacquer. Mesh data stays linked to the existing product asset.
- Existing champagne finish, glass, and shared pearlescent shader. Five
  shot-local shades also retint the additive glossy layer, avoiding a red cast
  across the whole palette. Shared source materials are unchanged.
- Existing studio backdrop, HDRI world and lighting collection. Local light
  data and floor material suit the new stage.
- 35 collection instances share five shade assemblies, keeping repeated
  geometry manageable. Each `SHOT04_Bottle_Rxx_Cxx_<shade>` is an editable
  placement/animation control.
- Direct Location and Euler Rotation curves, approximately 5–6 keys per
  channel. Location X controls entrance, Rotation Y the rock, Rotation Z
  planar settle, Location Y the final lane movement. No spin drivers.
- `SHOT04_CameraTilt` removes the initial 14-degree viewing angle, while
  `SHOT04_CameraRoll` unrolls from 35 degrees. Both reach zero at f348;
  Camera_DATA's orthographic scale controls the pullback. Timeline markers
  identify beats.

Builder: `scripts/build_lapohka_shot4_bottle_array.py`. Run in a fresh background
Blender process; it writes only the v003 scene. Preserve later manual edits
before rebuilding. The original Shot 4 study and approved Shot 3 are preserved.

## v004: fine lacquer shimmer and accurate focus

The previous depth-of-field target sat at Z 14 mm, while the front lacquer
surface is approximately Z 33.37 mm at f348. This defocus merged the small
flakes into cloudy patches. Controlled renders with identical materials and
denoising, but DOF disabled, confirmed the focus problem.

The camera now follows a focus target on the hero lacquer front, parented to
the hero bottle at local (0, -0.0283464, 0.0326), with aperture f/64. Ray checks
at f285, 321, 348 and 375 put the target within 0.029 mm of the actual lacquer
surface. Depth of field remains enabled.

The Shot 4 materials use local copies of the glitter wrapper and pearl core:
fine density 800 instead of 220, accent density 400 instead of 90, accent
selection threshold 0.80, pearl roughness 0.14, luster minimum 0.03 and shimmer
coverage offset 0.68. At a 600-pixel core diameter, the fine cells are roughly
1.2-1.3 pixels wide, compared with 4.4-4.8 pixels before. Lens roughness is
0.002. The legacy underlying glitter remains unchanged.

This is UV-attached material detail, not added image noise. All five palette
colors and 39 animated controls/data blocks retain their previous values,
keys, handles and interpolation. The shared product asset remains unchanged.

Patch: `scripts/refine_shot4_lacquer_shimmer.py`.
Review images: `renders/shot4_fine_shimmer_v004/review_0348.png` and
`review_0321.png`. Comparison: `renders/shot4_fine_shimmer_v004/shimmer_comparison.png`.

## v003: framing, alignment, palette and shadow revision

- Reduced column pitch from 76 to 60 mm and row pitch from 133 to 115 mm.
  Shortened the entry glide to retain clearance with the tighter arrangement.
- The f285-336 camera width is now 255 mm. One complete central bottle and two
  large neighboring bottles dominate the diagonal crop; surrounding bottles
  appear as edge fragments, following the supplied reference composition.
- From f348, a 305 mm camera width presents exactly five complete bottles in
  the middle row, with the five bottles above and below partially cropped.
- Removed the source assembly's residual tilt before placement. The camera
  also finishes removing its pitch at f348, so bottle faces are parallel to the
  image plane. This corrects the angled appearance after the camera unroll.
- Five lacquer shades: aubergine, petrol teal, pearl ivory, raspberry and
  midnight blue. Both base color and the additive glossy layer are retinted.
- Lower HDRI fill, a smaller warm key, and two window slats create visible
  cast shadows and soft backdrop bands. The existing backdrop mesh is reused.

All 91 frames pass a separating-axis check on projected oriented bottle
envelopes, with no overlaps. Minimum conservative floor clearance is 0.79 mm.
All bottle front normals align with the camera from f348 onward (zero-degree
error). Linked libraries resolve and the bottle controls have zero drivers.

Preview: `renders/lapohka/shot4_f285-375/lapohka_s4_f285-375_bottle_array_v003.mp4`
(960 x 540, 48 Cycles samples, 30 fps; all 91 encoded frames decoded successfully).
Validation: `renders/shot4_bottle_adaptation_v003/validation.json`.
Production settings remain 3840 x 2160, 256 Cycles samples. The delivered video
is a composition and motion preview, not the final production render.

## Preserved v002 verification and review

All 91 frames pass a conservative transformed-envelope spacing check, with
no intersecting XY envelopes between bottles. Minimum floor clearance is
0.79 mm; the central bottle stays inside the camera during the readable hold.
All linked libraries resolve, and bottle motion has zero drivers.

Preview: `renders/lapohka/shot4_f285-375/lapohka_s4_f285-375_bottle_array_v002.mp4`
(960 × 540, 48 Cycles samples, 30 fps, full 91-frame decode verified).
Validation: `renders/shot4_bottle_adaptation_v002/validation.json`.
Motion contact sheet: `renders/shot4_bottle_adaptation_v002/motion_contact_sheet.png`.
This preview is for the adaptation's composition and motion; a production
render is not part of this scene-building pass.
