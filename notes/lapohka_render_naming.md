# Lapohka render naming and organization

How our 3D animation renders map onto the five original Lapohka reference shots.

The reference clips live in `references/lapohka_3d_motion_shots/` and are all
**3840x2160 @ 30 fps**. They define the frame numbering used everywhere in this
project: shot frame ranges are absolute positions in the full 0-528 timeline, not
per-shot local frames.

| Reference clip | Frames | Count |
| --- | --- | --- |
| `Lapohka 3D Motion - Shot 1 (f0-56).mp4` | 0-56 | 57 |
| `Lapohka 3D Motion - Shot 2 (f57-198).mp4` | 57-198 | 142 |
| `Lapohka 3D Motion - Shot 3 (f199-284).mp4` | 199-284 | 86 |
| `Lapohka 3D Motion - Shot 4 (f285-375).mp4` | 285-375 | 91 |
| `Lapohka 3D Motion - Shot 5 (f376-528).mp4` | 376-528 | 153 |

## Directory layout

Each shot has one scene file and one render folder with the same name,
`gel_polish_lapohka_shot<N>_<start>_<end>`. The range is the frames the scene
actually covers (Shot 1 runs 0-82, past the 0-56 reference, because of the added
blue spin).

```
scenes/
  gel_polish_lapohka_shot1_0_82.blend
  gel_polish_lapohka_shot2_57_198.blend
  gel_polish_lapohka_shot3_199_284.blend          # + .liquigen project and _liquigen_proxy.fbx
  gel_polish_lapohka_shot4_285_375.blend
  gel_polish_lapohka_shot5_376_528.blend
renders/
  gel_polish_lapohka_shot<N>_<start>_<end>/
    frames/frame_####.png                        # 4K 16-bit production sequence (+ per-frame .json where the resumable renderer wrote them)
    lapohka_s<N>_f<start>-<end>_<slug>[_vNNN].mp4 # H.264 playback copy
    ..._master*.mov                              # ProRes 4444 XQ master
    ..._manifest.json                            # encode settings, checksums, source paths
cache/
  gel_polish_lapohka_shot3_199_284/              # LiquiGen v010 Alembic caches loaded by Shot 3
```

Every scene's `render.filepath` is `//../renders/<scene name>/frames/frame_`, so
rendering a scene writes straight into its folder. `renders/*` and `cache/` are
gitignored, so the tree is local only. This file is the tracked copy of the
convention.

## Filename convention

```
lapohka_s<shot>_f<start>-<end>_<slug>_v<NNN>.mp4
```

- `s<shot>` - which reference shot this render is aiming at.
- `f<start>-<end>` - the **actual** frame range encoded in this file, which is
  not always the full reference range. We render parts. A 38-frame slice of
  Shot 3 is `f214-251`, not `f199-284`. The folder names the scene;
  the filename says what is in the file. Keep these honest - a filename that
  overstates its coverage is worse than no name at all.
- `<slug>` - what changed in this pass (`base`, `liquid`, `camera_rig`,
  `sync_restored`). Describe the change, not the quality; `v2`, `final` and
  `fixed` are not slugs.
- `v<NNN>` - monotonic per shot, in render order. Never reuse or renumber a
  version, even after deleting the file. The number is a permanent handle for
  referring to a specific pass in notes and conversation.

Working in parts across multiple sub-ranges of one shot is expected. The
versions still increment across the whole shot rather than per part, so
`v004` being `f214-251` and `v005` being `f199-284` is correct and normal.

## Adding a new render

Render into the scene's own `frames/` folder, encode, and put the videos and
manifest next to `frames/` with the next version number for that shot.
Replace superseded frames and videos rather than keeping review folders around.
