# Shot 1 and Shot 2: reference motion rebuild

New review scenes reuse the existing linked polish bottle. The original scene
files, shared assets, and previously rendered production videos are unchanged.

| Shot | New scene | Range |
| --- | --- | --- |
| 1 | `scenes/gel_polish_lapohka_shot1_0_56_reference_v002.blend` | 0–56, 30 fps |
| 2 | `scenes/gel_polish_lapohka_shot2_57_198_reference_v002.blend` | 57–198, 30 fps |

## What the original reference actually shows

Sources are the two original shot clips in
`references/lapohka_3d_motion_shots/`. Frame numbers below use the original
continuous timeline, not a separate frame-one start for each clip.

| Frames | Observed reference action | Polish adaptation |
| --- | --- | --- |
| 0–12 | Can enters from below, fully visible about 8–9, reaching its apex about 12 | Bottle rises from completely below frame and eases into a readable hero pose |
| 12–25 | Floating product hold with a slight diagonal lean | Subtle drift and lean; no frozen pose |
| 26–37 | Rapid axial turn; coral/grapefruit changes to green/grape at frame 30 | One continuous, forward spin with the lacquer and backdrop change hidden by the back-facing pose at 30 |
| 38–56 | Reference can remains visible through the cut | Readable green bottle, then the **requested** accelerated exit below frame at 47–56 |
| 57–61 | New product falls in from above and reaches the shelf | Bottle drops from above; contact at 61 |
| 62–78 | Small rebound and settling | Rebound apex 64, second contact 67, tiny recovery 69, settled 78 |
| 79–96 | Stable product hold | Stable pose that meets the existing animation at 96 |
| 99 onward | Camera trucks along the lineup | Existing approved procession and edge-fall ending retained |

The original Shot 1 does **not** show a downward exit before its cut. Its final
ten frames were deliberately adapted to the user's requested exit, rather than
described as a recovered action from the reference.

The former Shot 1 file was set to render 48–180 and the former Shot 2 file began
at 96, despite containing some earlier animation. The new ranges include the
entrance and landing and preserve the original 0–198 overall timing.

## Editable controls

- Shot 1: `SHOT01_Travel` controls the rise/exit; `SHOT01_Tilt` controls the lean;
  `SHOT01_Spin` has the axial Z rotation keys. Spin uses nine keys, with free
  Bezier handles for the acceleration and deceleration. There are no baked
  per-frame rotation keys or hidden rotation drivers on these controls.
- Shot 2: `SHOT02_57_96_Travel`, `SHOT02_57_96_Rock`, and
  `SHOT02_57_96_Spin` control the restored opening. Contact keys have separate
  incoming/outgoing tangents for a crisp impact and progressively smaller arcs.
- Timeline markers identify each action beat.

Shot 1 uses a fixed camera so the entrance and exit cross the actual image edge.
Its new local wall and three correctly aimed local lights replace a source rig
whose tracking targets were missing. Off-camera flags cast broad diagonal
shadows. Coral/olive backdrop colors switch at frame 30. The HDR remains external
and its intensity is adjusted in a local world copy. Shared lighting, bottle,
and environment libraries were not edited.

## Verification and deliverables

- Shot 1's evaluated camera bounds are below frame at 0 and 56 and fully inside
  the image from 9 through 46. The axial spin is monotonic at quarter-frame
  sampling, without reversing through the fast turn.
- Shot 2's evaluated bottle support was checked at 157 quarter-frame samples
  between 57 and 96; the minimum is just above the platform, without penetration.
- Visible transforms and render visibility at 96, 100, 117, 135, 160, 182, and
  198 match the old Shot 2. Matrices of invisible objects were excluded because
  Blender may leave those unevaluated; their visibility was still compared.
- Both new scenes were opened in a fresh Blender process for render checks.
- Motion previews use Cycles, 960 × 540, 24 samples with denoising, 30 fps. They
  demonstrate timing and composition; fine shimmer should be judged from a
  full-resolution production render.

Review frame sequences and individual MP4s live in
`renders/shot1_reference_rebuild/` and `renders/shot2_reference_rebuild/`.
Combined and side-by-side reference videos live in
`renders/opening_reference_review/`. The latter labels original and updated
frames explicitly.

New production output paths are isolated under each shot's
`reference_rebuild/production_4k/` directory. The existing production images and
videos remain the previous versions; no replacement production sequence has
been rendered as part of this animation review.

Builders: `scripts/rebuild_shot1_reference.py` and
`scripts/rebuild_shot2_reference_landing.py`, each run from its original source
scene. Review renderer: `scripts/render_opening_motion_review.py`. Packaging:
`scripts/package_opening_motion_review.py` (regular Python with Pillow and
imageio-ffmpeg).
