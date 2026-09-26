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

Video renders go under `renders/lapohka/`, one folder per reference shot. The
folder name carries the **reference** range so the tree mirrors
`references/lapohka_3d_motion_shots/` one-to-one:

```
renders/lapohka/
  shot1_f0-56/
  shot2_f57-198/
  shot3_f199-284/
  shot4_f285-375/
  shot5_f376-528/
  _tests/           # material/shader reviews, not shot work
  _legacy_24fps/    # pre-Lapohka clips kept for reference only
  README.md         # live manifest of what is actually on disk
```

Note that `renders/*` is gitignored, so the tree and its manifest are local
only. This file is the tracked copy of the convention.

## Filename convention

```
lapohka_s<shot>_f<start>-<end>_<slug>_v<NNN>.mp4
```

- `s<shot>` - which reference shot this render is aiming at.
- `f<start>-<end>` - the **actual** frame range encoded in this file, which is
  not always the full reference range. We render parts. A 38-frame slice of
  Shot 3 is `f214-251`, not `f199-284`. The folder says what we are matching;
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

The package scripts still write into their own review folders
(`scripts/package_lapohka_shot4_preview.py`,
`renders/shot3_199_284_review/package_preview.py`). Their output paths were
deliberately left alone, so after encoding, move and rename the result into the
right shot folder, take the next version number for that shot, and add a row to
`renders/lapohka/README.md`.
