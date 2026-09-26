# Lapohka Shot 3 — frames 199–284

Scene: `scenes/gel_polish_lapohka_shot3_199_284.blend`
Reference: `references/lapohka_3d_motion_shots/Lapohka 3D Motion - Shot 3 (f199-284).mp4`
Timing: 86 frames at 30 fps, 2.867 seconds. Scene output: 1920 × 1080, Cycles 128 samples.

The reference uses a beverage can. This adaptation retains the linked gel-polish bottle, champagne metal, glass lens, and a local bordeaux variation of the existing lacquer shader.

## Current implementation: simulated liquid entry

### Entry reflection revision — 2026-09-14

The opening now retains a broad reflecting surface in front of the camera. The previous crop removed the surface needed for the reflection at frames 199–200. Coverage fades back to the established crop by frame 204, before the moving tank boundary can cross the submerged camera.

The pre-entry approach is closer to the water, with the camera and lighting following the adjustment. The opening lens is 61.5 mm, returning to 66.7 mm by frame 205. Opening focus uses f/32 and a 0.04-frame shutter so the reflection and grazing contours remain readable; these return to f/8 and the existing 0.28-frame shutter by 209. Small render-time surface ripples and a dedicated, light-linked grazing strip clarify the water at frame 201. Their contribution also fades out by 209.

The native liquid cache is reused. A comparison against the preserved session verified identical product/camera/light transforms, liquid mesh coordinates, lens, aperture, and shutter at frames 211, 231, and 284. Source libraries remain unchanged.

Current revision outputs are in `renders/shot3_entry_reflection_review/`: the complete preview, full-resolution stills for 199–201, and `entry_reflection_comparison.jpg`. The previous open session is preserved as `shot3_before_entry_fix_20260914_204608.blend` in that folder. `scripts/refine_lapohka_shot3_entry_surface.py` runs on that preserved pre-fix session; it is an incremental revision and should not be reapplied to the already-revised scene. `scripts/finalize_lapohka_shot3_entry.py` verifies and saves the result, and `scripts/package_lapohka_shot3_entry.py` creates the review delivery.

The revised scene replaces the first pass's procedural upward plume with native Mantaflow FLIP immersion. A closed body proxy and cap proxy follow the product into a liquid tank. The surface cavity and secondary bubbles, foam, and spray derive from the same cached flow.

| Frames | Motion |
| --- | --- |
| 199–205 | Rapid downward entry; diagonal refractive surface crosses the bottle. |
| 206–218 | Entry cavity and entrained-air wake develop around the product. |
| 219–247 | Camera follows descent while maintaining the tilted hero framing. |
| 248–284 | Increasing axial turn and tilt expose the bottle's side. The simulated wake continues evolving. |

The camera's 22-degree roll gives a diagonal entry plane. `Travel`, `Rock`, and `Spin` separate descent, world tilt, and axial rotation. Lighting follows the descending product. The delivered preview repeats the previous image at frames 203, 208, …, 283 to match the measured cadence of the reference. Product poses hold on those frames and fluid time nearly pauses; direct Blender renders can retain tiny simulation and sampling differences on held frames.

## Simulation and dependencies

- Bake: frames 190–284, resolution 112, FLIP ratio 0.95, mesh upsampling 2, adaptive stepping up to 12 steps, base time scale 0.35.
- Separate cached air bubbles, foam, and spray; approximately 5,754 live bubbles at frame 231 and 6,531 at frame 284 in this bake.
- Bubble shading uses a relative air/water IOR of `1 / 1.333`, with randomized instance sizes.
- A local Geometry Nodes modifier crops quiet tank boundaries for the camera. The entry surface remains until it clears the product; this avoids distracting reflections of studio light cards in the outer tank walls. The simulation itself retains its full rectangular domain.
- The changing liquid mesh renders without motion blur. Product motion blur remains enabled; the liquid is visually slowed by the simulation time scale.
- **Required cache:** `renders/shot3_199_284_v2_review/liquid_cache/`, approximately 1.09 GB, referenced relatively from the scene. Keep this folder with the Blender file. It is a scene dependency even though `renders/` is gitignored.

The current result is a resolution-112 reconstruction adapted to a different product silhouette, not the artist's original LiquiGen simulation. Individual foreground bubbles and the exact reference turbulence remain areas for further art direction.

## Assets and editing

Product geometry remains linked through editable library overrides. Champagne and front-glass materials remain linked to Shot 2. Lacquer and shot lighting changes are local. Source asset files remain unchanged; the studio HDRI is not packed. New objects use the `SHOT03_199_284_` prefix.

Simulation inputs are in `SHOT03_199_284_SIMULATION_INPUTS`; rendered liquid is in `SHOT03_199_284_LIQUID_ENTRY`. Collision proxies are hidden from render and hidden in the viewport after finalization. Unhide them for inspection or rebaking. The unused alternate cap's Boolean modifier is disabled because it caused a native Blender crash during the original preview renders.

## Reproduction and review

1. Preserve current manual scene changes before rebuilding. `scripts/rebuild_lapohka_shot3_liquid.py` replaces the previous shot-local effect and performs the three native bakes in a separate Blender process.
2. Run `scripts/finish_lapohka_shot3_liquid.py` on `renders/shot3_199_284_v2_review/shot3_liquid_work.blend` to stage the liquid, bubbles, camera, and lighting.
3. Run `scripts/render_lapohka_shot3_liquid_preview.py` on `shot3_liquid_finished.blend` to save the canonical scene, verify linked files and bake flags, and render the complete review sequence plus a full-resolution hero frame.
4. `scripts/package_lapohka_shot3_liquid_preview.py` encodes the review and assembles the reference comparison.

Revised outputs are under `renders/shot3_199_284_v2_review/`. The initial procedural pass and its review remain under `renders/shot3_199_284_review/`. A backup of the open Shot 3 session before the liquid rebuild is retained in the revised review folder as `shot3_before_liquid_rebuild_20260910_185301.blend`.

The old `build_lapohka_shot3.py` / `refine_lapohka_shot3.py` scripts describe the superseded procedural pass; running them would replace the current liquid setup.

## Product assembly alignment (2026-09-15)

The visible cap and front lens now parent to `SHOT03_199_284_BottleBody`;
the lacquer core parents to the front lens. Their relative transforms come
from the linked product's original assembly. This corrects the offset caused
by parenting all parts independently to `Spin` while the housing inherited a
rotation from its source. The housing retains its pose and the shot's animation.

`scripts/realign_lapohka_shot3_product.py` makes the correction with a backup
of the current session. Checks cover frames 199, 200, 205, 231, 247, and 284;
`scripts/render_lapohka_shot3_alignment.py` verifies the saved hierarchy after
reopening and renders frames 199 and 231 at 1080p with 128 samples and denoising.
Outputs and the backup are in `renders/shot3_alignment_review/`.

The shared lacquer shader added subsequently to the original shot work lives
in the product asset; see `notes/lacquer_shared_pearl_finish.md` for its controls.
