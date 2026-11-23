# Bossa Shot 10 — measured trio finale

Manual animation rendering and output naming are documented in [Bossa render settings](bossa_render_settings.md).

Scene: `scenes/gel_polish_bossa_shot10_657_749.blend`.

Updated 2026-10-17 from all 93 original frames, **657–749 at 25 fps** (3.72 seconds). Source: Victor Bandeira / Bossa Skin Care, [Bossa HydraBoost](https://vimeo.com/954255078). The [frame study](../references/bossa_hydraboost_shots/shot10_frames/README.md) contains extracted images, measurements, and validation.

## Animation

| Frames | Behavior |
| --- | --- |
| 657–678 | Hero descends quickly, eases into floor contact, and straightens its small initial lean. No rebound. |
| 679–707 | Rear bottles emerge from behind the hero and spread outward, with the left bottle leading slightly. Separate depth paths keep the bottles from intersecting. |
| 707–749 | Products and the highlight sweep hold still; peripheral lacquer accents continue moving. |

Updated 2026-10-23: all three products now retain their original **(1, 1, 1) scale** throughout the shot. A **70 mm perspective camera**, vertical 24 mm sensor and level optical axis replaces the orthographic camera. Its small dolly preserves the hero's measured base/top framing as the shot settles. This is an inferred staging solution, not a recovered original camera.

The three root controls are `BOSSA10_FinaleHero`, `BOSSA10_Finale_Aubergine`, and `BOSSA10_Finale_RoseCopper`. Motion is sampled into native transform keys at each source frame. Boundary keys at 656 and 750 support motion blur; the render range remains 657–749. Linear interpolation between these samples follows smooth, monotone fitted trajectories without Bezier overshoot. No simulation or external motion cache is required.

The rear bottles appear smaller through camera distance, with no animated product scaling. At the hold, the hero is at Y -0.022 m and both rear bottles at Y +0.053371 m, approximately **75.37 mm farther back**. All three have identical physical bounds of approximately **45.884 × 32.845 × 101.072 mm**. The camera sits near (0, -0.812918, 0.049342) m. The right rear bottle retains a deeper opening lane with up to 34.5 mm extra separation, then joins the left bottle's depth for the hold. Lateral paths preserve the reveal timing. The final group occupies about **62.1% of portrait width**, with roughly 19% side margins.

The peripheral accents were remapped along camera rays to preserve their projected centers and sizes after the perspective conversion. The lower-left accent sits closer to the camera to keep its full path above the floor. These accent size adjustments do not affect the product scales.

## Stage and accents

The stage is a neutral pearl surface with a softer floor reflection, replacing the initial mauve stage. Four peripheral accents retain the opaque cat-eye materials at different depths. Camera depth of field is enabled at f/64, matching the approved Lapohka fine-shimmer setup, with the focus target parented to the hero at the lacquer face. Floor clearance is checked throughout the shot.

The level perspective view required a curved backdrop to replace the visible horizon of the original flat plane. `BOSSA10_SeamlessFloor` retains its Z=0 surface under the products, starts a 0.25 m radius sweep at Y=0.25 m, and rises into a wall at Y=0.50 m. Materials and lights are unchanged by the camera conversion.

The finish was revised on 2026-10-17 against the approved Lapohka renders. The local gold uses roughness **0.06**, champagne color (0.78, 0.52, 0.23), metallic 1, anisotropy 0, and coat weight 0.06. All three front lenses use a local glass copy with roughness **0.002**. Local glitter-wrapper/core copies now restore Lapohka's **800/400 fine/coarse densities, 0.80 glint threshold, pearl roughness 0.14, luster minimum 0.03, and coverage offset 0.68**.

Comparison used the existing Shot 10 Render Result at frame 738 and finished Lapohka Shot 1 frame 40, Shot 2 frame 80, and Shot 4 frames 310/348. The prior 200/90 adjustment made facets roughly four times larger and produced coarse white flecks. Normalizing and strengthening the diagonal band also changed the approved finish. Those changes have been reverted: original Object-coordinate mapping, zero mapping offset, reactive values 0.82/0.42/0.10, gain 0.62 and offset 0.01. Fine detail is preserved by rendering a larger image rather than enlarging the material's facets.

The normalized Bossa mesh has the original geometry rotated about Z. UVs retain the original approximately 0–1 span, but Object-space vector constants require conversion: reflection axis (0, 0.86, 0.5) becomes (0.86, 0, 0.5), and anisotropic tangent (0, 1, -1) becomes (1, 0, -1). All three material branches use these directions. PetrolTeal now uses the exact Lapohka base/band colors (0.004, 0.078, 0.068)/(0.025, 0.29, 0.235); Aubergine uses (0.066, 0.008, 0.100)/(0.27, 0.065, 0.34). RoseCopper keeps its existing warm palette because the approved Shot 4 palette has no RoseCopper material.

The focus target sits at hero-local (0, -0.016153, 0.024708), on the lacquer face, rather than behind it at the root's depth. The lacquer shaders remain opaque (alpha 1, transmission 0); the front lenses retain glass transmission. Changes are local to Shot 10.

The existing `textures/hdris/studio_environment.hdr` supplies surface lighting and reflections at strength 0.16. The pale world at 0.35 is now restricted to camera rays; it no longer supplies uniform pale fill to the lacquer. Broad key/fill/rim powers remain 5/2/5 W and the existing sweep is 1.4 W. `BOSSA10_06_REFLECTION_CONTROL` contains two narrow reflection lights and three dark reflection cards adapted from Shot 01. Cards are visible only to glossy rays. The HDRI stays external and is referenced relatively.

An upright Lapohka Shot 2 bottle also has a pale lower floor reflection, so that effect is not by itself a material defect. Shot 10's existing render showed a stronger wash over approximately the lower half of the core. Reflection-ray checks confirm that the lower lens sees the bright floor. A local floor shader branch now uses Lapohka's matte porcelain values (0.27, 0.285, 0.31), roughness 0.72, for glossy rays. The camera-facing pearl floor is retained. Exposure is -0.65, matching the approved Shot 4 render. The appearance of this correction still requires the next manual still.

Light paths allow 16 total, 8 glossy, and 12 transmission bounces. A before/after digest confirmed that the finish update did not alter any existing object animation or camera animation. The material and lighting settings are applied; a manual shaded still remains the appearance check before a full sequence render.

Product meshes remain linked to `assets/products/gel_polish_bossa_animation.blend`. Motion, materials, stage, camera, and lights are local to this shot. Shared product assets are not edited.

Timeline markers preserve the reference's website-overlay timing: title 670–680, tagline 681–692, CTA 699–717. No Bossa branding or button graphics are added to the polish render; the upper and lower areas remain available for the website.

## Validation and manual render

The original orthographic fit and its measurements remain in `applied_motion_validation.json` as historical reference. The current perspective scene passes **189 samples at half-frame intervals from 656 through 750**, including shutter boundary poses: all product scales are 1, products stay in frame, no product bounding boxes intersect, no product or accent penetrates the floor, and the product/camera hold remains stationary. Minimum product separation is approximately **1.65 mm** and minimum accent floor clearance **10.43 mm**. Camera corner rays hit the cyclorama at the checked opening, landing and hold poses. See [perspective validation](../references/bossa_hydraboost_shots/shot10_frames/perspective_validation.json).

Hero base/top landmark drift from the previous composition is below 0.05 pixels at 368 × 654; accent center drift is below 0.001 pixels. Rear landmark positions change with the physical depth conversion, especially during the concealed opening lane, with a maximum sampled change of approximately 11.82 pixels. This is no longer the prior orthographic frame fit, and early blurred/occluded reference frames do not support an exact reconstruction.

The user approved the latest lacquer finish before the perspective conversion. The new camera composition and seamless backdrop have been inspected in Solid view; shader inputs remain unchanged. **The new perspective camera has not yet been rendered.** Its reflections, depth of field and changed rear placement still need a shaded still.

The scene uses **2160 × 3840, 100%, Cycles GPU, 1024 samples, adaptive threshold 0.002 with minimum 64 samples, 16-bit PNG**, frames **657–749**. These are portrait equivalents of the approved Lapohka production sampling settings, with accurate/high-quality OpenImageDenoise and the existing Blackman-Harris 1.5 filter. The rendered viewport uses 256 samples, adaptive threshold 0.03, minimum 16, and denoising. Frames 707–749 show the settled trio. The current frame is **738**. Press **F12** for one still to assess the perspective camera before rendering the sequence. The existing Render Result predates the camera conversion; no new render was started.

Output: `renders/gel_polish_bossa_shot10_657_749/frames/frame_####.png`.

The canonical scene is the only new working scene. Its standard `.blend1` backup preserves the preceding save. No command launcher, loose Python script, temporary render, or alternate candidate scene is created for this iteration.
