# Shot 3: analysis of the original animation

Analyzed 2026-09-10 using the supplied 86-frame video and the artist's Behance project. This documents the original shot, rather than the implementation of our first-pass recreation.

## Evidence and confidence

The [artist's project](https://www.behance.net/gallery/245481455/Lapochka-3D-Motion) lists LiquiGen, Blender, and Cycles. Two process GIFs show a tilted can descending into a rectangular liquid volume. Liquid moves around the entry and settles after submersion. This is strong evidence for a simulated immersion setup. The page does not disclose its complete node graph, cache format, solver settings, camera curves, or retiming factor.

Downloaded evidence is in `references/lapohka_shot3_analysis/`. `03.gif` and `06.gif` are the two simulation views; the associated contact sheets sample their motion. These GIF frame numbers are independent of the 199–284 frame numbering of the supplied video.

## Physical event and screen motion

The strongest interpretation is a descending product entering liquid, viewed in a close underwater-style composition. Its wake contains displaced liquid and entrained air. The bright material above the product is therefore the evolving aftermath of entry, with bubbles moving relative to the descending product.

This differs from our initial model of an isolated upward spray behind a floating bottle. In that first pass, independent droplets follow a prescribed plume shape. The original reads as a product interacting with a continuous surrounding medium.

Direct observations from the supplied clip:

| Delivered frames | Approximate elapsed time | Visible action |
| --- | --- | --- |
| 199 | 0.000 s | Hard cut to black. Can nearly upright. A broad reflective surface is visible below/right. |
| 200–205 | 0.033–0.200 s | The diagonal liquid boundary crosses from the lower can toward its top. The label is visibly distorted/reflected around the boundary. |
| 206–218 | 0.233–0.633 s | Dense bubbles envelop the can as the coherent surface clears upward. Tilt increases and the entry produces an irregular wake. |
| 219–247 | 0.667–1.600 s | The product remains readable in a sustained tilted pose while the bubble field continues evolving around and in front of it. |
| 248–263 | 1.633–2.133 s | The readable front begins transitioning toward the side; the wake continues independently. |
| 264–284 | 2.167–2.833 s | The side/barcode rotates into view and the silhouette leans farther right. Bubbles continue past the product. |

Ranges describe visible beats, not recovered keyframe positions. The clip duration is 86/30 = 2.867 seconds; its last frame starts at 85/30 = 2.833 seconds.

The composition suggests product/camera motion coordinated to retain a hero framing during descent. The rendered images alone do not uniquely distinguish camera tracking, object translation, focal-length changes, or a transformed simulation cache. The renderer's world axes and actual rotation angles cannot be recovered from a single view.

## Likely production workflow

The following is a reconstruction, not an artist-supplied recipe:

1. Author the can's descent, tilt, and axial rotation, possibly with keyframes or baked dynamics. Keep the label facing the camera during the central part of the shot.
2. Transfer that animation to a closed collision proxy in a liquid simulator. Simulate the surface crossing, displacement, cavity/wake, and secondary air particles.
3. Bring the resulting liquid surface and bubble/spray data into the lighting/rendering scene, retaining a shared time mapping with the can.
4. Compose a close view with a black environment, warm edge reflections, readable product illumination, and foreground/background bubble layers.
5. Retime the coordinated result for the long underwater hold, then render/composite with suitable blur and depth of field.

This route is supported by the software's documented capabilities: LiquiGen accepts animated meshes as colliders, supports secondary bubble dynamics, and exports meshes and particles, including velocity data for downstream motion blur. These capabilities establish feasibility, not the creator's specific choices. See [animated mesh import](https://docs.jangafx.com/liquigen/pages/references/How-To%20Guides/import_animation.html) and the [LiquiGen node reference](https://docs.jangafx.com/liquigen/pages/references/node_list.html).

## Why the liquid looks convincing

- **A coherent entry event.** The diagonal reflective surface is visible before the dense wake. The effect develops from contact instead of appearing throughout a column simultaneously.
- **Interaction with the product.** The wake wraps around the body and rim; its silhouette is irregular and changes over time. Bubble motion is related to local flow, drag, and buoyancy.
- **Several scales and depths.** Fine dense bubbles create the wake, larger air pockets remain individually readable, and isolated foreground bubbles introduce parallax and defocus. Particles cross the label rather than staying exclusively behind it.
- **Air inside liquid.** The optical interpretation is submerged air pockets. Merely coloring solid droplets copper does not reproduce the same interfaces or refraction.
- **Selective warm highlights.** Much of the liquid disappears into black. Bright edges describe bubbles, the can rim, and the entry surface. The copper appearance alone does not prove the bulk liquid is brown; light color, absorption, and grading could all contribute.
- **Separation of motion.** The product's readable pose changes more slowly than the surrounding wake, allowing the shot to feel energetic while retaining the label.

## Timing measurement

The supplied MP4 is 30 fps, but it contains near-duplicate adjacent frames at 203, 208, 213, 218, and every fifth frame thereafter through 283. At 480 × 270 analysis resolution, their mean absolute RGB differences are about 0.009–0.033 on a 0–255 scale; other adjacent differences are approximately 5.3–8.9. Compression explains the small nonzero differences.

That is 17 held transitions among 85 transitions, leaving approximately 69 distinct images. The cadence is consistent with 24 fps material converted to 30 fps. It does not establish the simulation step rate or its slow-motion factor. A faithful match should coordinate product, camera, liquid, and blur timing, then reproduce the delivery cadence across the entire result.

## Implications for our Blender recreation

The existing file is a useful asset and composition blockout. Its primary mismatch is the mechanism generating the effect, not simply the number or color of particles.

For a closer reconstruction:

1. Establish a liquid surface and animate the gel-polish bottle crossing it. Use a simplified, closed collider and preserve the detailed linked bottle for rendering.
2. Generate a wake from that collision, with secondary air bubbles driven by the same flow. The bottle's broader body and thin cap will produce different displacement than a can; art-direct the trajectory and emission while respecting its silhouette.
3. Keep the visible entry surface and the bubble wake as distinct components, with a shared simulation/retiming timeline.
4. Match the relative camera/product motion before fine shading. Preserve the readable hold, then the late axial turn.
5. Render a transparent surrounding medium and air bubbles with warm highlights and depth variation. Verify transmission and label visibility in Cycles.
6. Reproduce the 24-to-30 fps cadence only after the continuous motion and retiming are established.

No simulation settings, exact camera values, or original project files were published in the inspected material. A visually similar result will require tests rather than invented source parameters.
