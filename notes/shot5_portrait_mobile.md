# Shot 5 mobile portrait scene

## Selected rack-only revision

The selected mobile version is now
`scenes/gel_polish_lapohka_shot5_portrait_rack_376_528.blend`, scene
`SHOT05_PolishFinale_PortraitRack_376_528`. It retains 1080 × 1920, 30 fps and
the f376–528 timeline. The collection board is hidden for both render and
viewport. The rack now fills approximately 98% of frame width, with 1% side
margins and approximately 18.7% of frame height above and below. This is the
tighter full-rack framing within the retained 9:16 format. The final camera
now looks down at 35 degrees, increased from 28 degrees, with the same 85 mm
lens. This shows more of the bottle tops while keeping the frontal product
silhouette.

`scripts/build_shot5_portrait_rack.py` creates this revision from the prior
portrait scene or a same-directory working snapshot. It checks that the rack,
hero rig, supporting bottle transforms and animation keys are unchanged before
saving. The existing portrait review renderer automatically writes each scene's
review images to its matching render directory.

Rack-only stills are under
`renders/gel_polish_lapohka_shot5_portrait_rack_376_528/review/`.
The latest full-size ending, contact, rebound and reveal stills are under
`review_downward_1080/`. The preceding 28-degree tight framing is retained
under `review_tighter_1080/`, and the earlier framing under `review_1080/`.
`scripts/validate_shot5_portrait_rack.py` passed all 77 held frames and
confirmed the unchanged rig and 193 sampled poses against the previously
audited scene. Results are under
`renders/shot5_portrait_rack_validation/gel_polish_lapohka_shot5_portrait_rack_376_528/`.
For the intentional 1% side margins, run this audit with `--min-margin .005`.
Use the `--reference` argument to select the working snapshot that precedes
the camera revision. The audit still treats any full-rack cropping as a failure.
The earlier two-display composition and its review video remain a comparison
version; the rest of this note describes that earlier composition.

## Earlier two-display version

Scene file: `scenes/gel_polish_lapohka_shot5_portrait_376_528.blend`.
Scene name: `SHOT05_PolishFinale_Portrait_376_528`.

The mobile version renders at 1080 × 1920, 30 fps, over the existing f376–528
timeline. It stages the complete rack farther back and higher in the image, with
the intact landscape sample board closer to the camera and lower in the image.
Both displays rest on the continuous studio floor.

The final camera uses an 85 mm lens, a 55-degree downward view and a vertical
36 mm sensor fit. The board retains its 1.20 scale and uses a 28-degree backward
lean, with its floor clearance recalculated after rotation. Deep f/64 studio
focus keeps both displays sharp in the held view.

The hero and rack move by the same horizontal offset, preserving the front-row
R1/C3 landing, the contact at f432 and the rebound at f436. Bottle and rack
reaction keys retain their original timing. The camera starts with a close,
slightly low view of the hero, cranes and pulls back through the collection
reveal, then holds the complete portrait arrangement from f451 through f528.
All 36 shades and 72 board samples use the existing linked assets.

The landscape scene and shared assets are not rewritten by the portrait builder.
The portrait file opens at f528 in camera view and writes future renders to
`renders/gel_polish_lapohka_shot5_portrait_376_528/frames/`.

## Review tools

Run these scripts with factory startup and automatic script execution disabled.
The builder starts from the canonical landscape scene and saves a separate
portrait file. It replaces only the portrait output when intentionally rerun.

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --factory-startup --disable-autoexec --background 'scenes/gel_polish_lapohka_shot5_376_528.blend' --python 'scripts/build_shot5_portrait.py'

& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --factory-startup --disable-autoexec --background 'scenes/gel_polish_lapohka_shot5_portrait_376_528.blend' --python 'scripts/validate_shot5_portrait.py'

& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --factory-startup --disable-autoexec --background 'scenes/gel_polish_lapohka_shot5_portrait_376_528.blend' --python 'scripts/render_shot5_portrait_review.py' -- --frames 376 404 425 432 436 528
```

Review settings are temporary and are never saved back to the scene. Full-size
review stills are under `renders/gel_polish_lapohka_shot5_portrait_376_528/review_1080/`;
camera-motion review frames are under `motion_review/`. Those renders are review
outputs; the saved scene retains its production render settings.

The portrait audit checks the rack layout, landing clearances, scene dependencies,
floor contact, 9:16 output, and complete collection framing across f452–528.
Its phone-size measurements and center-ray obstruction checks supplement visual
inspection; small shade numbers require a dedicated detail view for legibility.
Reports are under `renders/shot5_portrait_validation/gel_polish_lapohka_shot5_portrait_376_528/`.

The completed audit passed 193 poses, including all 77 held frames, with no
collisions, floor or shelf penetration, missing dependencies, final cropping,
or sampled cross-display obstruction. The held arrangement has at least 8%
frame clearance. The board spans about 834 pixels and the rack 696 pixels of
the 1080-pixel frame width. Detailed audit results accompany the review renders.

The low-resolution `shot5_portrait_motion_review.mp4` preserves the 5.10-second
shot duration and 153-frame, 30 fps delivery timeline. It samples every second
scene frame for camera review at 270 × 480; it is not a production animation
render. Build it from completed motion-review images with
`python scripts/package_shot5_portrait_review.py`.

For supplementary checks after an already successful geometry audit, the
portrait validator accepts `-- --reuse-geometry`. It verifies the saved scene
hash before using the cached geometry report. Rerun the full audit after any
scene or linked-asset change.
