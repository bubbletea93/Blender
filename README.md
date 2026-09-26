# Blender Project Source Control

This repository is set up for Blender project source files.

## Layout

- `scenes/` for shot files. Each shot links the assets it needs.
  - `gel_polish_lapohka_shot5_376_528_polish_finale_v006.blend` — brand collection finale, frames 376–528: low-angle hero opening and three-beat landing, a pearl-bordered 72-tip sample board, and six bottles on a clear two-tier rack. Relative to v005, the board is 20% larger and the complete bottle display is 10% larger, on a 450 mm podium. Camera and hero motion retain v005 framing. Earlier versions are preserved. See [Shot 5 controls and reference analysis](notes/shot5_polish_finale_reference_analysis.md) and [brand collection direction](notes/shot5_brand_collection_direction.md). Composition stills and 306-sample geometry validation have passed; the new image sequence has not been rendered.
  - `gel_polish_macro_closeup_shot.blend` — macro spin (frames 48-180), closeup camera, mid-spin lacquer + backdrop color swap.
  - `gel_polish_bounce_wobble_shot.blend` — tabletop drop with bounce/wobble (frames 1-60), `Camera_TabletopDrop` perspective.
- `assets/` for reusable, linkable `.blend` files. Each top-level collection / world is marked as an asset for the Asset Browser.
  - `assets/props/manicure_finale_props.blend` — five-shade nail-swatch fan, fluted brush holder, cat-eye magnet, loose polished nail tips and ceramic podium.
  - `assets/props/brand_collection_bottle_rack.blend` — clear acrylic rack with two tiers and three columns of full-size polish bottles in six lacquer colors; v006 presents the linked assembly at 110% scale.
  - `assets/props/brand_collection_sample_board.blend` — landscape pearl-bordered sample display with 72 modeled tips, 36 paired shades numbered 211–246, and a clear raised support; v006 presents the linked assembly at 120% scale.
  - `assets/props/community/manicure_community_props.blend` — warm-ivory adaptation of Santiago Adrio's Organic Ceramic Tray (BlenderKit Royalty Free), used as an 80 mm leaf bowl in Shot 5 v004.
  - `assets/props/community/glass_cup_cczero/brush_holder.blend` — unbranded, clear-glass adaptation of cczero's Glass Cup (BlendSwap CC0), sized for the animated manicure brushes. Original source files and provenance records are preserved beside these community assets.
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

The lacquer's pearlescent finish is shared through `Lacquer_RenderGlitter_SHARED`
in the product asset. Edit that core and reload the linked scenes to update their
shimmer while retaining local shade animation. See [finish controls and render
verification](notes/lacquer_shared_pearl_finish.md).

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

