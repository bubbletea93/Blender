# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Blender art-production repo for gel-polish-bottle product shots. There is no application, no test suite, no build step — work happens inside Blender. The "code" here is `.blend` files, Python automation, and the linked-asset graph between shot files and asset files.

## Working with Blender via MCP

`.mcp.json` configures the `blender-mcp` server. When you need to inspect or modify Blender state, **prefer the MCP tools over running `blender -b ... --python` yourself** — the MCP server connects to a live Blender instance and round-trips much faster:

- `mcp__blender__get_objects_summary` / `get_blendfile_summary_*` — inspect the current file
- `mcp__blender__execute_blender_code` — run `bpy` code in the connected Blender (last resort; prefer dedicated tools when one fits)
- `mcp__blender__get_screenshot_of_*`, `render_thumbnail_to_path`, `render_viewport_to_path` — visual verification

For destructive bulk operations on files that are not currently loaded (e.g. rebuilding both shot files), spawning headless Blender via `subprocess.run([bpy.app.binary_path, "-b", path, "--python", script])` from inside an `execute_blender_code` call is the established pattern — the MCP-connected Blender stays clean while the work happens in subprocesses.

When `execute_blender_code` returns a value, **`result` must be a dict** (not a list) — wrap raw lists as `result = {"key": value}`.

## Asset architecture

The repo follows a strict link-and-override discipline. Reading [README.md](README.md) gives the directory map; the rules below are the parts that bite if you forget them:

**Shot files (`scenes/*.blend`) link assets, never own them.** Each shot links four asset libraries:

- `assets/products/gel_polish_bottle.blend` — bottle as a `Product_GelPolishBottle` collection
- `assets/environments/studio_backdrop.blend` — `Studio_Backdrop` collection
- `assets/environments/studio_environment_world.blend` — `Studio_Environment_HDRI` world (references `textures/hdris/studio_environment.hdr` relatively)
- `assets/lighting/three_point_studio.blend` — `Lights_ThreePoint_Studio` collection

**Override vs. plain link is intentional, not a default:**

- **Bottle and backdrop**: Library Override (`collection.override_hierarchy_create(... do_fully_editable=True)`). Shot-local pose, animation, and material-slot tweaks live on the override.
- **Lighting and world**: plain Link. No per-shot variation expected; if a shot needs to deviate, override locally rather than editing the asset.

**Shot-local animated materials (e.g. `LacquerShade_Swap_AB`, animated `StudioBackdrop_Mat`) stay LOCAL to the shot file.** They are not part of any asset. The pattern for assigning them to an overridden mesh:

```python
slot.link = "OBJECT"           # switch the override's slot to OBJECT-link
slot.material = local_material # then assign the local material
```

This avoids touching the linked mesh's material list while still letting the shot's animation drive the swap. If you forget the `link = "OBJECT"` step, slot assignment fails with `attribute "material" from "MaterialSlot" is read-only` because the slot is `DATA`-linked from the read-only linked mesh.

**Do not pack the studio HDRI into shot files.** The HDR lives on disk at `textures/hdris/studio_environment.hdr` and is referenced relatively from `studio_environment_world.blend`. The shot files were previously bloated by ~21 MB each from a packed temp HDR; this is the canonical fix.

**The `tmpx1vtg4wf.hdr` name is historical** — if you see it referenced in any file, it's the same studio HDR before extraction. Replace with `studio_environment.hdr`.

## File-cleanup pitfalls (asset authoring)

When carving an asset file out of a larger source `.blend` (the original abstraction pattern: open source → delete what you don't want → save-as), `bpy.ops.outliner.orphans_purge` alone is **not enough** — materials with `use_fake_user = True` and node groups with no users but a fake-user flag will survive. The reliable sequence:

1. For every datablock you want to drop: set `use_fake_user = False`, then `user_clear()`, then `db.remove(d)`.
2. Run `bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)` two or three times.
3. The `lib.id | ERROR ID user decrement error: ... 0 <= 0` warnings during save are harmless when they appear after explicit `user_clear()` + `remove()`.

For the bottle asset, the lacquer-shade material library (84 `LacquerShade_*` and `Lacquer_*` materials) is intentionally kept with `use_fake_user = True` so the variants stay shippable even though no mesh references them by default.

## Repo conventions

- **Git LFS tracks `.blend`, `.fbx`, `.abc`, `.usd`, `.usdc`, `.exr`, `.hdr`** (see `.gitattributes`). Run `git lfs install` once per machine before cloning or committing.
- `.blend1` backup files are gitignored. Don't commit them; do clean them up after destructive subprocess saves (they accumulate as `*.blend1`, `*.blend2`, …).
- The `*_blenderkit.blend` files at the repo root and `blenderkit_asset.json` are imported third-party assets (Anisotropic Metal, Glitter02). Treat them as vendored — don't edit; reference their materials/node groups by linking.
- Renders are gitignored except for whitelisted PNGs under `renders/gel_polish_angles/` (see `.gitignore`).

## Shot inventory

- `scenes/gel_polish_macro_closeup_shot.blend` — scene `GelPolishBottle_Shot`, frames 48–180 @ 30 fps, camera `Camera_Gel_macro_closeup` parented to `Target_Gel_macro_closeup`. Animations: `HousingAction.005` (spin), `Target_Gel_macro_closeupAction.006` (camera-target follow), `LacquerShade_Swap_ABAction` + `StudioBackdrop_MatAction` (mid-spin color swaps).
- `scenes/gel_polish_bounce_wobble_shot.blend` — scene `GelPolishBottle_TabletopDrop`, frames 1–60 @ 30 fps, camera `Camera_TabletopDrop`. Animation: `Housing_TabletopDrop_BounceWobble` on the override Housing.
