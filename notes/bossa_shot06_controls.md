# Bossa Shot 06 - opposing bottle array

Manual animation rendering and output naming are documented in [Bossa render settings](bossa_render_settings.md).

Canonical scene: `scenes/gel_polish_bossa_shot06_404_425.blend`.

Updated 2026-10-23 from all 22 extracted reference frames, 404-425, at 25 fps (0.88 seconds). See the [frame study](../references/bossa_hydraboost_shots/shot06_frames/README.md), [tracked measurements](../references/bossa_hydraboost_shots/shot06_frames/reference_motion.json), and [applied validation](../references/bossa_hydraboost_shots/shot06_frames/applied_motion_validation.json).

## Composition and animation

Two staggered columns replace the first pass's three equally tilted columns. Left caps lean upper-left; right caps lean upper-right. Five complete products and cropped top/bottom continuations follow the reference. The repeated products deliberately extend outside the portrait frame.

The reference array moves upward about 50 pixels and enlarges 3.74% over the 368 x 654 study crop. The scene uses a 70 mm perspective camera, a 24 mm vertical sensor, forward/downward camera travel, and small individual transform corrections. Every bottle and the array parent retain scale (1, 1, 1) and the original 101.07 mm assembled height. Apparent size differences come from perspective distance.

Bottle centers, cap tips, and base centers were tracked in every reference frame. Smooth fits remove tracking jitter before solving the original-size bottle's position and orientation. The left-middle bottle has unstable late-frame tracked lengths; its center and angle are retained while its length follows the coherent array enlargement, avoiding a false depth pulse. Native per-frame keys cover 404-425, with handles at 403 and 426 for motion blur. There is no added bounce, settling pause, or synthetic highlight sweep.

The 15-degree cap-away tilt and the division between camera and object movement are interpretations of the 2D footage. The round polish body has different proportions from Bossa's serum bottle; this matches projected axes, spacing and motion without deforming the product to copy that silhouette.

## Controls

- `BOSSA06_DiagonalArray`: identity parent for all 15 bottle assemblies.
- `BOSSA06_Left_01` through `Left_07`, and `BOSSA06_Right_01` through `Right_08`: ordered from top to bottom. Each root has `reference_track` and `shade` custom properties.
- Main visible tracks: `Left_03` upper, `Left_04` middle, `Left_05` lower; `Right_04` upper and `Right_05` middle.
- `BOSSA06_Camera`: keyed perspective camera. `BOSSA06_CameraFocus` follows the middle-left lacquer face; f/64 preserves fine pigment detail.
- Each root contains housing, cap-lift/cap, front-lens and lacquer objects. The original linked product mesh is preserved.

## Approved bottle finish

The approved Shot 10 bottle materials provide the local finish. The original PetrolTeal, Aubergine and RoseCopper shaders now each appear on one bottle. Twelve additional local lacquer materials give every bottle a distinct shade, including off-frame continuations. All 15 retain the same approved fine-shimmer wrapper/core; gold and the front lens retain `BOSSA06_ChampagneGold` and `BOSSA06_ClearProductLens`.

The lacquer uses the shared fine-shimmer wrapper/core at 800 fine and 400 coarse density, corrected Bossa object-space directions, original band response, opaque pigment and the approved palettes. Gold has roughness 0.06; the clear lens has roughness 0.002 and IOR 1.45. Product shaders and linked source meshes have no changes in the shared asset files.

### Unique lacquer cores, 2026-10-23

Each core has a separate `BOSSA06_BottleLacquer_<Shade>` material assigned through its object material slot. New variants change the base/band colors and matching colored glossy contribution, while preserving the finish graph, cat-eye response, fine pigment density and opacity. Raspberry, MidnightBlue, PearlIvory, Emerald and GoldenOchre use existing Lapohka palette values. Additional working shade names are scene-local color variations, not product catalog identifiers.

| Position | Left column | Right column |
| --- | --- | --- |
| 01 | SlateSilver | Chocolate |
| 02 | Lilac | OliveGold |
| 03 | Aubergine | PearlIvory |
| 04 | PetrolTeal | RoseCopper |
| 05 | Raspberry | MidnightBlue |
| 06 | GoldenOchre | Emerald |
| 07 | BurnishedBronze | Sapphire |
| 08 | - | Burgundy |

The main visible arrangement alternates aubergine, teal and raspberry down the left, with pearl ivory, rose copper, midnight blue and emerald on the right. The scene's `unique_lacquer_palette` custom property records all assignments and linear colors. Validation confirms 15 distinct materials and base colors, unchanged finish structure for the new copies, and unchanged animation, transforms, lighting and color management during assignment.

The lighting now follows the actual active Lapohka Shot 4 scene at frame 348. Its studio HDRI world is copied locally at strength 0.16, with the environment mapping rotated -90 degrees around X to match the lighting transfer from an overhead camera to Shot 6's front-facing camera. The original image dependency is reused. The backdrop uses a local copy of the active `SHOT04_MAT_WarmPorcelain` material: base color (0.27, 0.285, 0.31), roughness 0.72, metallic 0. The floating composition retains its existing vertical backdrop geometry.

### Lapohka lighting match, 2026-10-23

The earlier six-light arrangement produced bright, pale reflections that differed from the approved Lapohka render. The replacement uses the three active source lights, transferring both their positions and orientations through the camera-basis rotation Rx(+90 degrees). The source reference point is (0, 0, 0.0008); the target array reference point is (0, 0, 0.145). Lights stay fixed in world space throughout the animation.

| Shot 6 light | Source | Power | Rectangle dimensions | Position |
| --- | --- | --- | --- | --- |
| `BOSSA06_WarmWindow` | `SHOT04_WarmWindow` | 30 W | 0.065 x 0.14 m | (-0.36, -0.5492, -0.105) |
| `BOSSA06_SoftFill` | `SHOT04_SoftFill` | 4 W | 0.5 x 0.5 m | (0.28, -0.6492, 0.245) |
| `BOSSA06_CapStrip` | `SHOT04_CapStrip` | 7 W | 0.045 x 0.5 m | (0.02, -0.4492, 0.595) |

Power, dimensions and colors match their source lights. The three additional reflection/sweep lights and two dark cards have been removed. AgX Medium High Contrast and exposure -0.65 match the source scene; reducing that color-management setting alone did not address the different reflection environment.

Correction to the preliminary source inspection: the reflection-transparent material belongs to an unused backdrop variant. The active Lapohka backdrop has an object-linked opaque porcelain override. Shot 6 copies that assigned material and does not add a reflection-bypass branch.

Before/after digests confirm unchanged product shader inputs, color ramps and connections, object transforms and animation curves. Source settings, transfer matrices and digests are retained in the scene's `lapohka_lighting_transfer` custom property. The rendered viewport was inspected at frame 423: the lacquer colors are deeper and the previous broad pale reflection bands are reduced. A full-quality manual still remains pending.

### Window-blind shade, 2026-10-24

The user requested window shade across both the products and background. The backdrop is restored to Y = 0.30 m, replacing the closer Y = 0.15 m product-shadow experiment. A physical slat array, `BOSSA06_WindowBlinds`, now interrupts the warm key light, casting broad diagonal bands through the composition. Existing product shadows remain physically enabled but are no longer the intended background pattern.

The array has 12 slats at 80 mm pitch and 42 mm width, angled 35 degrees across the image, on a constant-Y plane at -0.175 m. The existing area light feathers the shadows naturally, with softer edges on the more distant backdrop. The slat material transmits 25% of incident light. The slats are invisible to the camera and reflection rays; shadow linking keeps the existing fill and cap-strip lights unobstructed by them. All three light powers, sizes and transforms, the HDRI, product materials, camera and animation remain unchanged.

Adjust spacing/count in the slat object's Array modifier and attenuation in `BOSSA06_WindowShade_Translucency` > `ShadeTransmission`. The rig is fixed in world space so the animated products move through the shade. The setup is contained in `BOSSA06_06_WINDOW_SHADE`; there are no external textures, new scripts or review renders.

Validation across 89 integer, intermediate and shutter samples gives at least 32.45 mm between the slat plane and product bounds, and 187.74 mm between product bounds and backdrop. The rendered viewport at frame 413 was inspected for visible feathered bands and retained lacquer detail. A full-quality render has not been run for this lighting change.

## Render settings and review

Saved production settings: **2160 x 3840**, 25 fps, frames **404-425**, Cycles GPU, 1024 maximum samples, adaptive threshold 0.002, minimum 64 samples, OpenImageDenoise high/accurate, 16-bit RGB PNG. AgX Medium High Contrast, exposure -0.65; motion-blur shutter 0.35. Output:

`renders/gel_polish_bossa_shot06_404_425/frames/frame_####.png`

The scene preserves the user's selected frame. Frames **415** and **423** are representative views for a still. Use **F12** for a full-quality still, and **Ctrl+F12** for the 22-frame sequence after approving that appearance. No final render or waiting job was started during this edit, per the user's workflow preference.

Validation passed at 89 integer, intermediate and shutter samples: unit product scales, no conservative full-product bounding-box intersections, at least 21.44 mm separating distance, camera clearance, backdrop clearance and present external dependencies. Against the tracked reference, center RMS error is 0.11 pixels and endpoint RMS is 0.67 pixels. The largest endpoint difference, 4.00 pixels, is in the deliberately filtered noisy middle-left track.

Solid viewport composition and the revised rendered viewport were inspected. A full-quality still and animation remain the final visual checks; numerical validation does not establish final lacquer appearance. Adjacent Shots 05 and 07 have since been refined separately; see the [Shot 05 controls](bossa_shot05_controls.md) and [Shot 07 controls](bossa_shot07_controls.md).
