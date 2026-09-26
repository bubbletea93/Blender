Research checked 2026-09-19 for the Shot 3 LiquiGen/Blender 5.1 workflow.

Implementation update, 2026-09-20: the accepted Dolly rig and shared source-time
controller are now in the canonical Shot 3 blend. Add Camera Rigs 1.8.2 is installed.
The delivered implementation uses native driver response curves instead of NLA
strip-time drivers: local Blender 5.1 tests found that the latter evaluated the
physical transforms one update late. The balanced ramp stays above 0.5×, while
camera keys remain on output time. Existing 30 Hz Alembic caches are retained;
the denser export below remains a separate sampling upgrade. See
[the current controls and delivery notes](lapohka_shot3_liquigen.md).

**Recommendation:** use Add Camera Rigs' Dolly rig, an editable master simulation
time curve, and independently timed camera movement. Evaluate True Time Remapping
for whole-shot timing experiments; consider Cineflow if its path-editing interface
would save substantial iteration time. The research itself made no scene changes;
the accepted recommendation has since been implemented as described above.

The existing coordinated retime keeps the bottle and caches synchronized, but it
bakes many channels and also retimes the camera. That is a useful delivery result,
not an ideal authoring setup for repeated revisions. Separate spatial motion,
simulation playback time, camera timing, aiming, framing and focus controls.

The reference analysis supports an entry, a readable underwater product view,
and a later side reveal. It does not establish the original artist's camera rig
or speed curve. The following is a proposed adaptation for our bottle.

| Delivery beat | Suggested motion direction |
| --- | --- |
| 199–205: entry | A decisive descent with restrained camera follow. Establish momentum. |
| 206–214: impact/wake | Ease simulation playback slower around the most readable liquid event. Let the camera continue moving. |
| 215–245: underwater hero | Maintain nonzero bottle motion; use a shallow camera arc and gentle framing drift to reveal parallax. Keep the red face readable. |
| 246–270: side reveal | Build the turn and camera arc together without cancelling their relative motion. |
| 271–284: finish | Ease toward the final composition without an unintended full stop before the cut. |

These ranges are blocking guides, not recovered reference settings or a final
speed curve. The available source duration must still fit the 86-frame delivery.

**Timing design.** Store simulation source time in seconds on one shot control.
Map that time to the bottle's original continuous action and both Alembic caches,
using each source's FPS and start offset. Keep the original source actions and
timing map; replace the existing retime rather than stacking another warp on it.
Blender's NLA Animated Strip Time samples an action at a specified action frame,
and the cache Override Frame samples cached geometry at a chosen frame.
[NLA documentation](https://docs.blender.org/manual/en/latest/editors/nla/sidebar.html),
[cache controls](https://docs.blender.org/manual/it/5.1/modeling/modifiers/modify/mesh_sequence_cache.html).

The slope of source time versus output time is playback speed. A horizontal
segment freezes motion. A sudden slope change produces a speed jump. Use a few
deliberate timing keys with continuous slopes and controlled acceleration, and
check that the curve never reverses. Avoid easing to zero velocity at every
intermediate waypoint. Blender's Continuous Acceleration handle smoothing can
help; Auto Clamped handles limit overshoot, but the resulting curve still needs
inspection. [Graph Editor reference](https://docs.blender.org/manual/en/latest/editors/graph_editor/fcurves/properties.html).

Keep camera path progress on output time. Its aim may follow the retimed bottle,
but its position should retain an independent arc/dolly move during slow motion.
Maintain source-time synchronization for physically simulated bubbles. Decide
explicitly whether additional artistic bubbles and animated light effects follow
simulation time or output time; do not indiscriminately warp every channel.

**Camera rig design.** Use Root → Dolly/Orbit → Aim-oriented camera control →
Framing/Roll offset → Camera. Add an independent focus target near the front
lacquer/lens surface. The aim target controls composition; focus controls sharpness.
For this small bottle, use millimeter-scale offsets and restrained orbit/roll.
Keep focal length fixed during initial blocking so lens changes do not obscure
timing problems. A roughly 5–10° camera arc across the underwater hero is a useful
starting experiment, not a prescribed final angle.

Use a smooth target path with deliberate lag or lead instead of locking the
bottle's center to the image center on every frame. Preserve parallax in the
foreground/background bubbles. Check the relative bottle/camera rotation:
matching their angular speed can make a moving product appear stationary.

| Add-on | Evidence and suitability |
| --- | --- |
| [Add Camera Rigs](https://extensions.blender.org/add-ons/add-camera-rigs/) | Free; v1.8.2; listed for Blender 4.2+. Dolly/Crane rigs expose Root, Camera, Camera Offset and Aim controls. Best starting point for our compact product shot. |
| [True Time Remapping, Blender 5.0+ branch](https://github.com/sorecords/true_time_remapping_bl5.0) | Free; keyable Speed/Frames modes and motion-blur stretch. Good whole-scene timing experimentation. Uses its own remapped playback/render operators; verify Alembic, point clouds, output numbering and automated rendering in a copied shot. Not a verified drop-in solution for independently timed camera movement. |
| [Cineflow](https://superhivemarket.com/products/cine-flow) | Listed at $34.99; v1.3.0. Publisher describes arc-length paths, timing grips, speed graph, pass-through waypoints and ordinary Blender keyframe output. Promising paid choice for frequent path revisions. Publisher lists tests on 5.0.1/5.2; our 5.1 scene has not been tested. Existing-camera import and focus-along-path are described as upcoming, so do not assume they ship. |
| [Scene Retimer](https://extensions.blender.org/add-ons/scene-retimer/) | Free; v1.0.0; Blender 4.2+. Useful marker-based scene timing/blocking. Its published mapping is piecewise linear and drivers are untouched. Cache frame-channel coverage is not established; it is not our final smooth-ramp controller without further validation. |
| [Camera Shakify](https://extensions.blender.org/add-ons/camera-shakify/versions/) | Optional finishing tool, not the main motion solution. Use v0.5.1 or later on Blender 5.x; that version fixes a Blender 5.0 driver issue. Keep influence extremely restrained for this polished product shot. |

Also reviewed [Cablecam](https://superhivemarket.com/products/cablecam-cinematic-camera-movement-rig).
Its position/aim/horizon controls are relevant, but the standalone listing still
names versions through 3.6, while a bundle banner claims 5.1.1 compatibility.
Clarify the exact included version before choosing it over the above options.
Prices and compatibility are publisher listings, not local compatibility tests.

**Temporal sampling is the main liquid constraint.** Our archives contain 78
samples at 30 Hz. The current delivery map ranges approximately 0.341×–1.486×
over f214–284; its slowest portion advances only about 10.2 source samples per
output second. This follows directly from `shot3_liquigen_timing.json`.

Blender 5.1's Alembic reader only interpolates mesh vertices when adjacent
samples have matching topology. Our liquid changes vertex/face counts, so a
smooth frame curve cannot guarantee smoothly changing liquid geometry.
[Blender 5.1 source, read_mesh_sample interpolation](https://github.com/blender/blender/blob/v5.1.0/source/blender/io/alembic/intern/abc_reader_mesh.cc#L443-L462).

For 30 fps delivery, a practical minimum unique-sample budget is 60 Hz at 0.5×,
90 Hz at one-third speed, or 120 Hz at 0.25×. These are sampling calculations,
not guarantees of visual smoothness. The current 60 Hz simulation exports every
second step. First test exporting every step (stride 1) for both mesh and
particles, with framerate compensation enabled and the same physical duration.
For deeper slow motion, generate genuinely denser simulation samples; merely
changing the file FPS or increasing internal substeps does not export more
surface states. JangaFX distinguishes full steps from internal substeps and
documents export stride/framerate compensation. [LiquiGen node reference](https://docs.jangafx.com/liquigen/pages/references/node_list.html).

**Motion blur.** Leave cached liquid blur disabled while testing geometry timing.
When enabling it, verify velocity attributes and units and account for playback
speed: for positions sampled at T(t), velocity scales by dT/dt. Confirm actual
renderer behavior before applying a scale to avoid double correction. Blender
provides cache velocity units and a multiplier; JangaFX's Blender convention uses
meters and meters/second. A shutter adjustment alone does not guarantee correct
cache velocities. [Blender cache velocity controls](https://docs.blender.org/manual/it/5.1/modeling/modifiers/modify/mesh_sequence_cache.html),
[JangaFX export conventions](https://docs.jangafx.com/liquigen/pages/references/How-To%20Guides/alembic_convention.html).

**Recommended next experiment:** preserve the current delivery, build one Dolly
rig, block a restrained underwater arc at normal speed, then test two ramp
strengths with the shared source-time control. Review full-frame-rate movies for
label readability, continuous screen motion, cache stepping, focus and framing.
Validate a small rendered range with and without blur before final rendering.
Retiming the already-simulated motion needs no different collision trajectory;
changing the bottle's physical path or orientation requires a matching proxy and
new simulation. Only bake the camera/time evaluation into a delivery copy after
the motion is approved.
