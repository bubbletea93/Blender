# Shot 3: LiquiGen delivery

Open `scenes/gel_polish_lapohka_shot3_199_284_liquigen_v009.blend`.
Frames 199–284, 30 fps, 1920×1080, Cycles, 128 samples.

The scene uses the detailed bottle with the approved LiquiGen liquid, bubbles,
foam and spray. The background is black. A forest environment emitter lights
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

Both archives contain samples 0–77 at 30 fps. Their frame overrides are already
keyed in Blender using [the shared delivery map](shot3_liquigen_timing.json).
Delivery poses hold at 203, 208, …, 283; the simulation was run continuously and
both caches receive the same holds. Do not substitute a constant frame offset.
The cache parent translates Z by −0.300 m. Native cache velocity motion blur is
disabled because its velocities do not account for delivery holds.

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

Reopened the saved file and verified 265 scene objects, one scene, no hidden
objects and no fluid modifiers. Both cache files resolve. Timing checks verified
matching geometry at held frames, resumed motion afterward, finite coordinates
and evaluated particle materials. Cleanup renders at 205, 231 and 284 matched
the prior composition (mean normalized pixel differences below 0.000015).
Review images are in `renders/shot3_liquigen_review/blender_v009/`.
The full animation has not been rendered.
