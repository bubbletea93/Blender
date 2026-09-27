# Blender Project Source Control

This repository is set up for Blender project source files.

## Layout

- `scenes/` for shot files. Each shot links the assets it needs.
  - `gel_polish_lapohka_shot5_376_528.blend` — finished brand collection finale, frames 376–528. The hero drops into the front row of the six-by-six, 36-shade rack, beside the user-sized sample board on a seamless mauve/lavender studio floor. The board has the Hang Pure logo, stitched leather, and 72 magnetic cat-eye samples with fine shimmer. The 4K, 30 fps production sequence and MP4/ProRes deliveries are complete. See [Shot 5 controls and reference analysis](notes/shot5_polish_finale_reference_analysis.md) and [brand collection direction](notes/shot5_brand_collection_direction.md).
  - `gel_polish_macro_closeup_shot.blend` — macro spin (frames 48-180), closeup camera, mid-spin lacquer + backdrop color swap.
  - `gel_polish_bounce_wobble_shot.blend` — tabletop drop with bounce/wobble (frames 1-60), `Camera_TabletopDrop` perspective.
- `assets/` for reusable, linkable `.blend` files. Each top-level collection / world is marked as an asset for the Asset Browser.
  - `assets/props/brand_collection_bottle_rack_36.blend` — complete six-tier, six-column display with 36 distinct shades matching the sample board. Shared finished product meshes retain full surface detail while supporting efficient rigid motion blur.
  - `assets/props/brand_collection_sample_board.blend` — original pearl-bordered sample display with 72 tips and 36 paired shades numbered 211–246; contains the user's resized geometry with the stand removed. The current scene uses the separately derived `brand_collection_sample_board_stitched.blend`: sewn pearl-white leather backer, Hang Pure logo, and fine magnetic shimmer. Its linkable collection is `Prop_BrandCollection_SampleBoard_Stitched`.
  - `assets/props/community/` — original community downloads and provenance retained for reference. The unused tray and glass-holder adaptations have been removed from the active project.
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

Shot 5 production frames are in `renders/shot5_polish_finale_production_4k/production_4k/`.
The verified 4K MP4, ProRes 4444 XQ master, and checksum manifest are in
`renders/lapohka/shot5_f376-528/`. Repackage existing frames with
`python scripts/package_shot5_production.py`; this does not render again.

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
