# Blender Project Source Control

This repository is set up for Blender project source files.

## Layout

- `scenes/` for shot files. Each shot links the assets it needs.
  - `gel_polish_macro_closeup_shot.blend` — macro spin (frames 48-180), closeup camera, mid-spin lacquer + backdrop color swap.
  - `gel_polish_bounce_wobble_shot.blend` — tabletop drop with bounce/wobble (frames 1-60), `Camera_TabletopDrop` perspective.
- `assets/` for reusable, linkable `.blend` files. Each top-level collection / world is marked as an asset for the Asset Browser.
  - `assets/products/gel_polish_bottle.blend` — `Product_GelPolishBottle` collection (Housing, Cap, FrontLens, Lacquer, ApplicatorTip, Bristles + cap-indent helpers) and the full lacquer-shade material library.
  - `assets/environments/studio_backdrop.blend` — `Studio_Backdrop` collection (curved cyc with non-destructive depth modifier stack, default + lavender material variants).
  - `assets/environments/studio_environment_world.blend` — `Studio_Environment_HDRI` world that references `textures/hdris/studio_environment.hdr`.
  - `assets/lighting/three_point_studio.blend` — `Lights_ThreePoint_Studio` collection (Key/Fill/Rim area + TriLamp Key/Fill/Back; TriLamp lights have Glossy ray visibility disabled).
- `textures/` for authored textures and HDRI source files.
- `scripts/` for Blender Python tools and automation.
- `references/` for concept art and other versioned input material.

### Linking conventions

- **Bottle and backdrop** are linked into shots and made into Library Overrides so each shot can pose/animate Housing locally and tweak per-shot material slots without modifying the asset.
- **Lighting rig** is linked plain (no override) — share the same rig across shots. Override locally only if a shot needs custom light tweaks.
- **World** is linked plain. The HDR file lives at `textures/hdris/studio_environment.hdr` and is referenced relatively from the world asset.
- **Shot-specific animated materials** (e.g. mid-spin lacquer/backdrop color swaps) are kept local in the shot file and reassigned to the override mesh's material slot via `OBJECT`-link, so the linked asset stays clean.

Generated output such as renders, bake data, and simulation caches should stay out of Git.

## Git and Git LFS

Run `git lfs install` once on each machine before cloning or contributing. The repository tracks these binary source formats through Git LFS:

- `.blend`
- `.fbx`
- `.abc`
- `.usd`
- `.usdc`
- `.exr`
- `.hdr`

## Blender Workflow

- Keep external assets and linked libraries on relative paths.
- Prefer multiple focused `.blend` files over one monolithic project file.
- Use Link/Append to assemble reusable content.
- Do not routinely pack resources during active development.
- Commit at meaningful authoring checkpoints instead of every render iteration.

