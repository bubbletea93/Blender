# Bossa Shot 05 — nine-bottle pinwheel

Manual animation rendering and output naming are documented in [Bossa render settings](bossa_render_settings.md).

Canonical scene: `scenes/gel_polish_bossa_shot05_316_403.blend`.

Updated 2026-10-24 using all 88 source frames, 316–403 at 25 fps (3.52 seconds). The [reference study](../references/bossa_hydraboost_shots/shot05_frames/README.md) contains the extracted frames and measurements. This replaces the eight-bottle first pass, its 0.64 product scales, empty opening and synthetic highlight sweep.

## Motion and composition

Nine original-size bottles form a pinwheel at 40-degree intervals. Caps point obliquely around the opening. The source has a rapid opening pullback followed by a decelerating counterclockwise orbit and a gentle late push-in. Individual bottle axes turn much less than their positions orbit, so the scene animates positions and orientations independently rather than rotating a rigid ring.

The source's nine base centers and cap tips were fitted to a coherent circle and axis model. Smooth anchor curves suppress optical-tracking jitter. Native transform keys cover every source frame, with handles at 315 and 404; the output range remains 316–403. The camera is perspective, 70 mm with a 24 mm vertical sensor. All bottle roots and the array parent remain at scale (1, 1, 1), preserving the original 101.07 mm assembled height.

The reference deliberately overlaps each cap/dropper tip with the neighboring collar or shoulder, forming a connected inner ring. That camera-view layering is now restored. Camera distance and ring placement bring the original-size polish bottles closer to the reference's apparent size. The previous 10.5% opening / 7.8% settled spacing increase, which eliminated projected overlaps and reduced settled bottle axes to about 71–72% of the reference, is superseded.

The current solve matches projected base and axis targets directly. Bases follow the smoothed reference fit; frames 316–319 remain an interpretation of the blurred, cropped opening. Measured individual planar residual turns and independently phased axial swivels of up to ±4 degrees are retained. The inferred nominal cap-toward-camera tilt starts at 25 degrees and eases to 39 degrees by frame 330, allowing the caps to pass in front of adjacent shoulders without physical contact. This replaces the earlier 8-degree tilt and body-center-pivot spacing correction. These depth rotations are an interpretation, not a recovered 3D reconstruction.

The wider, round polish housing differs from the source serum bottle, so the adaptation balances apparent size, opening shape and physical separation. The placement revision measured the following at the 368 × 654 reference size, before the additional local rotations described below:

| Frame | Polish axis / reference axis | Current inner-opening radius | Reference inner-opening radius |
|---|---:|---:|---:|
| 332 | 89.8% | 109.7 px | 100.5 px |
| 350 | 88.0% | 118.8 px | 112.5 px |
| 375 | 91.0% | 133.4 px | 130.0 px |
| 403 | 96.0% | 150.4 px | 149.0 px |

The original-size product remains linked from `assets/products/gel_polish_bossa_animation.blend`. Shared meshes and other shot files are unchanged. Repetitions at the sides are deliberately cropped, as in the reference; this is an array transition, not the final hero composition.

### Local bottle rotations

Each bottle now turns relative to its existing animated orientation: `q_new = q_current @ q_local_delta`. An additional local-Z swivel of up to ±9 degrees and local-X/Y tilts of up to ±0.65 degrees ease in over 18 frames, with independent bottle phases spaced 40 degrees apart. Native keys cover 315–404; output remains 316–403. These authored turns retain the existing cap-over-shoulder layering.

Rotations pivot around the local body center `(0, 0, 0.0247079)`. Position compensation preserves the body-center paths, with maximum measured interpolation drift of 0.001992 mm. The camera and product scales are unchanged. Scene properties `local_rotation_baseline` and `local_rotation_refinement` retain the starting animation and applied local layer.

## Finish, lighting and accents

The approved Shot 06 finish supplies local gold, glass and fine-shimmer lacquer materials. Each bottle has a separate shade, clockwise from `RingBottle_01`: PetrolTeal, RoseCopper, MidnightBlue, Raspberry, Emerald, PearlIvory, Aubergine, GoldenOchre and Lilac. Fine/coarse shimmer densities remain 800/400, gold roughness is 0.06, and lens roughness is 0.002. Lacquer pigment remains opaque. Corrected Bossa object-space shader axes rotate naturally with each bottle.

The three approved Lapohka-derived lights retain Shot 06's powers, dimensions, colors and transforms: WarmWindow 30 W, SoftFill 4 W and CapStrip 7 W. The local studio HDRI has strength 0.16; exposure is -0.65 with AgX Medium High Contrast. The opaque porcelain backdrop remains at Y = 0.30 m. The old moving highlight-sweep light is removed.

`BOSSA05_WindowBlinds` casts real soft bands across the product ring and backdrop. It has 12 slats at 80 mm pitch, 42 mm width and 35 degrees, with 35% transmission for a slightly gentler pattern than Shot 06. Camera/reflection visibility is disabled for the slats, and shadow linking keeps the fill and cap-strip lights unobstructed by them. The window rig stays fixed while the products move through it.

Eight opaque lacquer beads interpret the reference's clear serum accents. They move from the opening field toward the perimeter by frame 325, then drift slowly around the ring. Their paths are authored from reference observations, not exact per-bead tracking or a fluid simulation. Foreground Y positions now range from −0.1225 to −0.15 m; reprojection preserves their baseline apparent trajectories and sizes while separating them from the enlarged bottle arrangement.

## Controls

- `BOSSA05_RadialArray`: identity parent at the composition center.
- `BOSSA05_RingBottle_01` through `_09`: native position/quaternion animation and individual shade assignments.
- `BOSSA05_Camera`: keyed pullback/push-in; `BOSSA05_CameraFocus` preserves fine detail at f/64.
- `BOSSA05_02_LACQUER_ACCENTS`: eight keyed bead objects.
- `BOSSA05_06_WINDOW_SHADE`: physical slat array. Adjust count/spacing in the Array modifier and attenuation in `BOSSA05_WindowShade_Translucency` > `ShadeTransmission`.

The scene's `reference_overlap_refinement` describes the underlying placement, with `local_rotation_baseline` and `local_rotation_refinement` recording the added bottle turns. `reference_overlap_validation` describes the placement before those turns. `motion_model`, `bottle_attitude_refinement`, `attitude_clearance_validation` and `bottle_attitude_baseline` retain earlier fit and correction history; their older clearance figures do not describe the current scene.

## Validation and rendering

The current physical check evaluates all 36 bottle pairs at 355 integer, half-frame and shutter samples across 315–404. Conservative bounds use polygon-containing boxes divided into 4 mm axial slabs. With the local rotations applied, minimum physical separation is 0.227616 mm at frame 393.5 between bottle 8's lens and bottle 9's cap; no tested sample fails. The previous 0.594 mm minimum predates this rotation layer. Camera-view overlaps remain intentional. Product scales remain (1, 1, 1).

The [validation file](../references/bossa_hydraboost_shots/shot05_frames/applied_motion_validation.json), under `local_rotation_revision` and `current_validation`, records the current checks. `reference_overlap_and_size_revision` and earlier sections retain historical placement and clearance measurements.

The current local rotations were inspected successfully in material-preview and solid screenshots at frame 358. The earlier black screenshot capture affected the preceding placement review. Final production lighting has not been rendered for this revision; the material preview does not verify that lighting. No render or export was launched.

Saved sequence settings: **2160 × 3840**, 25 fps, frames **316–403**, Cycles GPU, 1024 maximum samples, adaptive threshold 0.002/minimum 64, high-quality OpenImageDenoise, 16-bit RGB PNG, motion-blur shutter 0.35. Output:

`renders/gel_polish_bossa_shot05_316_403/frames/frame_####.png`

The scene is left at the user's frame 358 for playback. Frame 375 remains a useful manual F12 finish check; Ctrl+F12 renders the 88-frame sequence. The canonical scene is the only working scene; no alternate candidate file, launcher, loose Python script or temporary rendered review was created.
