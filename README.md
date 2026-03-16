# Blender Project Source Control

This repository is set up for Blender project source files.

## Layout

- `scenes/` for shot files and top-level working scenes
- `assets/` for reusable asset `.blend` files and imported source assets
- `textures/` for authored textures and HDRI source files
- `scripts/` for Blender Python tools and automation
- `references/` for concept art and other versioned input material

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

## Starter Directories

- `scenes/`
- `assets/`
- `textures/`
- `scripts/`
- `references/`
