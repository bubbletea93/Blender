# Bossa Shot 07 — closer opposing bottle array

Manual animation rendering and output naming are documented in [Bossa render settings](bossa_render_settings.md).

Canonical scene: `scenes/gel_polish_bossa_shot07_426_450.blend`.

Updated 2026-10-25 from the approved [Shot 06](bossa_shot06_controls.md) and all **25 source frames, 426–450**, at 25 fps. The [reference study](../references/bossa_hydraboost_shots/shot07_frames/README.md) contains the extracted frames, cross-cut fit, optical tracks and smoothed motion curves.

## Composition and motion

Shot 07 continues Shot 06's two staggered columns of opposing diagonal bottles, with a hard cut to **1.5039× apparent size**. The source then continues upward while enlarging another **7.99%**; after removing image-centered zoom, its upward drift is **92.70 pixels** in the 368 × 654 reference crop. Most cap tips intentionally extend outside the left/right edges, with further bottles continuing above and below the frame.

All 15 bottle assemblies retain their original unit scale and 101.07 mm assembled height. The 70 mm perspective camera uses a 24 mm vertical sensor. Its location changes from approximately `(0.000079, -0.769985, 0.128180)` at frame 426 to `(-0.000730, -0.713161, 0.093701)` at frame 450. Apparent enlargement comes from camera distance and projected placement, not animated product scaling.

Native transform keys cover frames **425–451**, including motion-blur handles; output remains **426–450**. Visible bottle centers, axes and lengths follow quadratic fits to all 25 reference frames. The increasingly cropped upper-right bottle uses coherent array magnification for its length and an early-14-frame linear angle fit, preventing its late tracking jump from producing false movement. Off-frame continuations follow the aggregate transformation of Shot 06's ending projected endpoints.

The inherited 15-degree cap-away tilt and division between camera and object movement are interpretations of the 2D footage. The round polish housing differs from the serum bottle, and clipped cap tips are inferred. Tracking residuals do not establish an exact 3D reconstruction.

## Approved finish and lighting

The complete approved Shot 06 setup is transferred locally: 15 distinct lacquer shades retain their column positions, along with the same opaque fine-shimmer finish, gold and clear lens. Fine/coarse pigment densities remain 800/400, gold roughness 0.06, and lens roughness 0.002 with IOR 1.45. Shared product assets are unchanged.

The three Lapohka-derived lights retain their exact powers, colors, sizes and transforms: WarmWindow 30 W, SoftFill 4 W and CapStrip 7 W. The studio HDRI remains at strength 0.16, with AgX Medium High Contrast and exposure −0.65. The opaque porcelain backdrop remains at Y = 0.30 m.

The fixed window-blind rig retains 12 slats, 80 mm pitch, 42 mm width, a 35-degree angle, Y = −0.175 m and 25% light transmission. It casts soft bands across products and background; camera/reflection visibility is disabled for the slats, and shadow linking keeps the fill and cap-strip lights unobstructed.

## Validation and review

Conservative full-product bounds pass at **103 integer, intermediate and shutter samples**, checking all **105 bottle pairs**. Minimum physical separation is **13.137 mm**, at frame 451 between Left_01 and Right_02. Minimum clearances are 43.245 mm to the slats, 197.141 mm to the backdrop and 578.872 mm to the camera. Original product scales, all 15 unique lacquer assignments, transferred lighting and external dependencies pass.

For the reliable tracked bottles, raw-reference endpoint RMS error is **0.263 px**, with a maximum of **1.185 px**. Including the deliberately filtered upper-right track gives an aggregate raw-reference RMS of about 1.44 px. These fit residuals are smaller than the underlying landmark uncertainty (approximately 3 px before cross-cut transfer; the cut fit itself has a 1.29 px residual). See [applied validation](../references/bossa_hydraboost_shots/shot07_frames/applied_motion_validation.json).

The solid viewport composition was inspected at frames **438 and 450**. No shaded/final render or export was started, following the user's manual-render workflow. Numerical checks establish placement and clearance, not final lacquer appearance.

## Render settings

Saved settings match Shot 06: **2160 × 3840**, 25 fps, frames **426–450**, Cycles GPU, 1024 maximum samples, adaptive threshold 0.002/minimum 64, OpenImageDenoise high/accurate, 16-bit RGB PNG, f/64 and motion-blur shutter 0.35. Output:

`renders/gel_polish_bossa_shot07_426_450/frames/frame_####.png`

The scene is left at frame **438** for review. F12 renders a still; Ctrl+F12 renders the 25-frame sequence. The canonical file is the only working scene; no alternate candidate file, launcher, loose Python script or temporary review render was created.
