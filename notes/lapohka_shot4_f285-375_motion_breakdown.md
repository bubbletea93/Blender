# Lapohka Shot 4 — frames 285–375

Scene: `scenes/gel_polish_lapohka_shot4_285_375.blend`
Reference: `references/lapohka_3d_motion_shots/Lapohka 3D Motion - Shot 4 (f285-375).mp4`
Timing: 91 frames at 30 fps, 3.033 seconds. Reference is 3840 × 2160; scene output is 1920 × 1080.

The supplied reference is an extreme macro on a slim beverage can that spins to
a stop, unrolls upright, then drops out while the next flavour rises in behind
it. This adaptation keeps the production gel-polish bottle, its champagne metal
and glass lens, with a citron lacquer for the hero and a melon lacquer for the
incoming shade.

## Beats

| Frames | Reference beat | Scene controls |
| --- | --- | --- |
| 285–296 | Surface smears solid, then resolves as the spin decelerates hard | `Spin` (baked per frame), camera roll ≈ 41→57° |
| 296–321 | Damped settle: overshoot at f302, counter-swing at f313, at rest by f321 | `Spin` settle term |
| 322–336 | Dead hold on the diagonal | camera roll locked at 56° |
| 336–348 | Camera unrolls 56°→0° and eases back | `Camera` roll + distance |
| 348–364 | Upright hero, slow residual label drift | `Spin` hold drift |
| 364–371 | Hero drops and recedes out of frame, spin accelerating | `Travel` |
| 369–375 | Next shade rises into frame, still moving as the shot cuts | `NextTravel`, `NextSpin` |

## How the reference was measured

Reference frames were decoded through Blender's sequencer (no ffmpeg on this
machine) and analysed numerically rather than by eye:

- **Screen roll** from the dominant edge orientation (structure tensor on an
  8× downsampled frame). It reads a rock-steady 55.6–56.3° across f321–336, then
  a clean ramp to level by f348. The per-frame roll values in `CAM_KEYS` from
  f336 onward are taken straight from that measurement.
- **Spin phase** from the centroid of the label's green (mint) pixels, which is
  the only isolated colour patch on the can. It rises to a maximum at f302,
  troughs at f313 and settles at f321 — a damped oscillation, not a plain
  deceleration, which is why `spin_deg` carries a separate cosine settle term.
- **Camera distance** from the can's silhouette pair after de-rotating each
  frame. Its projected diameter is near constant (424 px at f324–336 vs 405 px
  at f348–363), so the reference barely dollies.
- **Background** from sampling the frame corners: warm peach across the top
  falling to a mid neutral grey at the lower right, boundary running diagonally.
  The cove's gradient coefficients are fitted to those samples.
- Every 5th reference frame is an exact duplicate of its predecessor, so the
  source animation is 24 fps conformed to 30. The scene is authored at 30 fps to
  match the edit and the rest of this repo.

## Verification

The built camera's screen roll was read back from evaluated world matrices
(angle of world +Z in the camera's screen basis) and compared against the roll
measured off the reference, frame by frame:

- **mean absolute error 0.53°** over f321–370, the range where the reference's
  own estimate is trustworthy (settled, little motion blur)
- worst case 2.3°, on in-between frames during the fast unroll where the keys'
  Bézier interpolation differs slightly from the reference's per-frame values
- f285–320 is deliberately *not* fitted frame-by-frame: the reference's roll
  estimate there is corrupted by spin blur (it reads 82° at f296, which the
  frames plainly contradict), so those keys are a smoothed settle instead

Running the same estimator on the rendered frames reads ~11° lower than the
camera's own roll. That is estimator bias, not a scene error — the disc is
rotationally symmetric so it offers no long axis to latch onto, and the
background's diagonal gradient boundary pulls the dominant-edge angle off. The
evaluated-matrix figure above is the authoritative one.

Spin is authored to the reference's measured beat frames (overshoot f302,
counter-swing f313, rest f321) rather than to a per-frame angle: the reference's
spin proxy is the label's green mint patch, which has no analogue on this
product.

## Where this deliberately departs from the reference

The reference product is a slim cylinder: it overfills the frame throughout,
its silhouette never changes as it spins, and the shot never reveals the whole
can. This product is a 44 mm lacquer disc on a 102 mm bottle, so two things had
to be re-pitched:

- **Framing.** The macro end is set so the disc over-fills the frame, and the
  shot opens up on the reference's own unroll beat (f336–348) to the
  product-legible framing the reference reaches at its upright hold. The
  reference holds one distance because a cylinder reads the same at any crop.
- **Spin amplitude.** A disc turns edge-on, which would empty the frame. The
  run-up is held to 2.2 turns and spent almost entirely in f285–289 where the
  shutter smears it away, and the settle amplitude is halved from the measured
  value so the disc never turns fully edge-on.

## Assets and editing

- Two fully editable library overrides of `assets/products/gel_polish_bottle.blend`:
  `HERO` on `Travel` / `Rock` / `Spin`, and `NEXT` on `NextTravel` / `NextRock` /
  `NextSpin`, hidden until f369.
- Champagne and front-glass materials link to Shot 2. Both lacquers are
  shot-local retints of linked Shot 2 shades (`GOLDEN_OCHRE`, `CORAL`), keeping
  the original procedural cat-eye shader.
- The standard backdrop is linked and overridden, scaled up and dropped below
  the product, carrying a shot-local warm gradient on OBJECT-linked slots. It is
  split by Is Camera Ray — bright to the lens, a fraction of that to every other
  ray — because a 360° emissive cove otherwise turns the lacquer dome into a
  mirror of white and the shade washes out.
- The lighting rig is linked and overridden with local light data for this
  shot's high-key daylight.
- The world is a plain link. The HDRI remains external, not packed.
- All new shot objects use the `SHOT04_285_375_` prefix.

The screen tilt is **camera roll**, not object tilt — the background rolls with
it in the reference. Roll is keyed as an explicit quaternion; a Track To
constraint would cancel it. Spin is baked per frame with linear interpolation
because the deceleration curve is the point.

Build script: `scripts/build_lapohka_shot4.py`, also embedded in the .blend as
text. It runs headless (`blender -b --factory-startup --python ...`) and
overwrites the scene file, so preserve manual changes before running it again.

Preview render: `scripts/render_lapohka_shot4_all.py` drives
`scripts/render_lapohka_shot4_preview.py` in restartable chunks. Cycles
intermittently faults partway through a long single-process run of this scene,
so each restart resumes from the frames already on disk. Review renders live
under `renders/shot4_285_375_review/`.
