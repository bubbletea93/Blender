# Lapohka Shot 2 — hero settle, f115–f198 (motion breakdown)

> **DEVIATION IN OUR SHOT (2026-07-13):** the Blender shot intentionally diverges
> from the reference after f158. Per direction: spin reduced to ~2 revolutions
> (−30°→+680°, settling 40° short of front ~f160), bottle settles halfway OVER the
> plinth end edge — base center ON the edge line, reached as ONE continuous
> decelerating drift from the hop landing (Travel y 0.386 f140 → 0.412 f150 →
> 0.430 f159, ease-out flat). The landing rock dissolves directly into a
> PRECESSING rim wobble at f125 — there is NO upright moment mid-sequence (the
> old reference Beat-1 at f135 is intentionally gone): f126–162 keyed per-frame
> LINEAR via Rock.rotation_x = −A·cosψ, rotation_y = A·sinψ, ψ sweeping ~2.7
> turns (0→960°), amplitude 0.21→0 rad hitting zero only at f161 — it wanders
> onto the edge like a settling coin, even nibbling over it near f154, no
> stop-then-slide. The spin dies at +680°
> (~f160), i.e. 40° SHORT of facing camera — the pre-fall pose is deliberately
> candid, never label-front — then drifts to +700° during the fall. Holds still
> f161–f163, then TIPS from f163 pivoting exactly at the Rock origin (base center =
> edge: no contact-arc compensation needed; −8° f168 → −67° f182 release) into a
> slow-mo fall (z=−0.00023t², +Y kick 0.0019 m/f) reaching ~−130° and ~6cm below
> plinth top by f198. Camera follows from f163 via CameraTrack.y + CameraTarget
> local y/z riding the bottle COM, keeping it centered, PLUS a dutch roll
> (CameraTrack.rotation_x 0 → −24° f163→198, same sign as the tip) that survives
> the Track-To because the constraint's up-vector inherits the rig roll — this
> reproduces the reference's diagonal falling-shot framing.
> Backdrop and plinth were extended downward (backdrop z→−0.5, y→0.78; plinth is
> now a pedestal to z=−0.25) to cover the below-edge framing. Sections below
> describe the ORIGINAL reference for f115–f158; the tail sections (D/E, camera
> lock-off) no longer apply to our shot.

Source: `C:\Users\danht\Downloads\Lapohka_frames` (30 fps, video frames align 1:1 with
shot frames in `scenes/gel_polish_lapohka_shot2_97_198.blend`). Hero = watermelon can
(→ our B06 bottle). Analysis from frames sampled every 2–5 frames across f115–f198.

## One-line read

The hero enters airborne at f115, touches down on its **bottom rim** just left of the
plinth's front corner at ~f117, and spends the rest of the shot doing a **decelerating
pirouette on that rim**: ~3 full revolutions of continuous one-way spin (2 fast, then
one long decelerating final rev) that lands exactly label-front as the lean decays,
ending dead-front, dead-upright, balanced on the plinth corner at f198. The spin
NEVER reverses (confirmed against the clip and the Behance storyboard; a sparse
frame read can alias the tail into looking like an unwind — it isn't one). The camera
trucks right with the hop cadence, stops by ~f150, and is essentially locked for the
final 40 frames so the settle is the only motion.

## Phases

### A — Airborne entry + touchdown (f115–f120)
- f115: hero enters frame-right, mid-air, base ~15% of can-height above the plinth,
  near-vertical with a small (~8°) wobble. Yaw spin already in progress (label ~30°
  off front). Neighbor cans (Christmas deer, silver/yellow) are one hop-beat ahead,
  marching left with heavy motion blur.
- f117: contact — trailing edge of the bottom rim touches first.
- f120: full weight on the rim, leaning **camera-right ~12–14°**. No bounce off the
  surface; energy goes into the rock and the spin.

### B — First rock to upright (f120–f135)
- Lean decays 13° → 0° over ~15 frames with almost no overshoot:
  12° (f125) → 10° (f127) → 6° (f130) → 3° (f132) → 0° (f135).
- Spin continues through the rock (~1 revolution from entry).
- **Beat 1 (f135): perfectly upright AND label dead-front simultaneously.** This
  alignment is deliberate — keyframe it exactly, don't let it fall out of the curves.

### C — Second lean + fast spin (f135–f150)
- The can leans back over camera-right, onto the rim, toward the plinth corner:
  0° (f135) → 6° (f141) → 11° (f150). Reads as the pirouette pose being taken up.
- Spin stays fast through this stretch — roughly constant ~1 rev/16–18 frames
  (label front f135 → back f141 → front again f150 = one full rev in 15 frames).
- **Beat 2 (f150): label front again (cumulative 2 revs), lean ~11°.**

### D — Leaning pirouette, final decelerating revolution (f150–f193)
- Lean holds ~11–12° camera-right through ~f172, then decays: 12° (f175) →
  10° (f180) → 7° (f185) → 3° (f190) → ~1° (f194) → 0° (f198). The base contact
  point is the bottom rim at/over the plinth's front corner — by now the can is
  balanced essentially on the corner point.
- Spin continues in the SAME direction, one more full revolution with a long
  decelerating tail that lands exactly label-front: front f150 (+720°) → back
  ~f161 (+900°) → barcode crosses center ~f169 (+990°) → front art re-enters from
  frame-left and centers → settles at +1080° by ~f193, flat hold to f198.
- Feature tracking (barcode / title) across f160–f190 shows a steady rightward
  sweep across the visible surface — monotonic yaw, no reversal.
- IMPORTANT: the lean direction stays fixed in **screen space** (always camera-right)
  while the can yaws underneath it. Lean and spin are separate transforms — see rig
  notes below.

### E — Settle (f193–f198)
- Final pose: upright, label dead-front, standing exactly on the plinth corner
  (corner reads as a pyramid point under the can, bottom-center of frame).
- Add a ±1–2° micro-settle wiggle on the LEAN dying out f192–f196 so the stop isn't
  dead; the spin itself just eases flat into +1080°.

## Keyframe table (hero transforms)

Positive spin = the direction it turns throughout (label sweeps right-to-left across
the front). Lean pivots at the bottom-rim contact point, axis fixed relative to camera.

| Frame | Spin Z (cumulative) | Lean (camera-right) | Base height | Note |
|-------|--------------------|---------------------|-------------|------|
| 115   | 0° (label ~30° off front) | ~8° wobble | ~0.15 × height | airborne entry |
| 117   | ~+75°              | 12°                 | 0           | rim touchdown |
| 120   | ~+150°             | 13°                 | 0           | full contact |
| 135   | **+360°**          | **0°**              | 0           | Beat 1: upright + front |
| 141   | +540°              | 6°                  | 0           | back panel visible |
| 150   | **+720°**          | 11°                 | 0           | Beat 2: front, 2 revs |
| 161   | +900°              | 12° (holding)       | 0           | back panel centered |
| 170   | +990°              | 12° (holding)       | 0           | barcode side crossing |
| 183   | +1050°             | 8°                  | 0           | front art centering |
| 193   | **+1080°**         | ~0° (+1° micro)     | 0           | spin lands front, flat |
| 198   | +1080°             | 0°                  | 0           | hero lock-off |

Interpolation guidance:
- Spin f115–f150: near-linear (~20°/frame ≈ 1 rev / 17 f), then one continuous
  decelerating final revolution f150→f193 (rates ≈ 16°/f → 10°/f → 4.6°/f → 3°/f),
  easing flat into +1080°. Monotonic — never key a reversal.
- Lean: two slow rocks, not a damped oscillation — down (f120→f135), up (f135→f150),
  long hold (f150→f175), long ease-out to zero (f175→f198). Period is much longer
  than a real can wobble; keep it languid.

## Position

Touchdown lands the base just left of the plinth's front corner. Between f125 and
f150 the base drifts ~half a base-radius toward the corner (sells the rim-walk from
the rocking); from ~f150 it is planted on the corner, slightly overhanging by the end.
Nearly all other perceived travel in the shot is camera, not object.

## Camera

| Frame | Camera |
|-------|--------|
| 115   | trucking right (following the hop march), decelerating; hero in right third; very gentle push-in throughout |
| 150   | truck essentially ends; hero just left of center; neighbor can's edge still at frame-left |
| 163   | slow residual drift only (matches B06 note: "exterior orbit starts f163") |
| 186   | last neighbor (B05 / Christmas can) fully clears frame-left |
| 198   | locked: hero centered (~52% x), plinth corner wedge bottom-center, camera at mid-can height, near-level (slight down-angle early flattens out), no roll |

Can height in frame stays ~63% of frame height for the whole segment — the push-in is
subtle (<5%); the dominant camera move is the lateral truck ending ~f150.

## Environment / lighting

- Backdrop is a lilac wall with soft diagonal light bands (window-gobo look) that
  **drift slowly** throughout — that motion continues even when camera and can are
  still, and keeps the lock-off alive. In our setup this maps to the animated
  `StudioBackdrop_Mat` / a light gobo, not camera movement.
- Plinth top is pale pink with a subtle speckle; front faces fall away bottom-left
  so the corner reads as a pedestal point in the end framing.

## Rig mapping for B06 (gel polish bottle)

The screen-space-fixed lean while yawing requires split transforms:

```
Empty_B06_root      # world location: entry arc + touchdown spot + drift to corner
└─ Empty_B06_lean   # pivot offset to the bottom-rim contact point;
   │                # rotation = lean, axis ≈ camera-right cross world-Z (fixed, does NOT spin)
   └─ Housing (override)  # pure local Z rotation = spin (+1080° net, per table above)
```

- If lean were keyed on the Housing itself, the label would corkscrew — the reference
  clearly keeps the lean plane fixed to camera while the label rotates through it.
- Pivot for the lean must sit on the base rim edge (delta transform or empty offset),
  not the bottle origin, or the base will slide during rocks.
- "Label front" beats (f135 / f150 / f190–198) map to logo-front on the bottle; check
  the override Housing's rest yaw so +360° multiples actually land logo-front.
- The bottle is taller-proportioned than the can; keep the same lean angles (they're
  about silhouette, not physics) but the rim-contact pivot matters even more — verify
  ground contact at f120, f150, f170 with the established contact validations.
