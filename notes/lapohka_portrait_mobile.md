# Lapohka opening shots: mobile portrait

Four separate portrait scenes adapt the approved Lapohka opening to 9:16.
The landscape source files are unchanged. Each portrait scene preserves its
original frame range and animation at **30 fps**.

| Portrait scene in `scenes/` | Inclusive frames | Framing |
| --- | --- | --- |
| `gel_polish_lapohka_shot1_portrait_0_82.blend` | 0–82 | Double spin and shade cuts, with a clear entrance and exit. |
| `gel_polish_lapohka_shot2_portrait_57_198.blend` | 57–198 | Wider procession framing followed by the final hero orbit. |
| `gel_polish_lapohka_shot3_portrait_199_284.blend` | 199–284 | Complete bottle during the existing liquid entry and descent. |
| `gel_polish_lapohka_shot4_portrait_285_375.blend` | 285–375 | Three dominant columns with the original camera unroll and lane movements; peripheral repetitions may cross the frame edge. |

Each scene retains its original camera as the parent of the new active
`SHOT0N_PortraitCamera`. Portrait adjustments change optical framing through
lens and shift controls. Product motion and materials remain intact. Shot 3
also retains its original Dolly rig, liquid-cache clocks, clearance modifiers
and depth of field. Its saved scene includes the LiquiGen liquid and secondary
cache objects.

## Saved production settings

- **2160 × 3840**, 100%, square pixels; **30 fps**.
- **PNG, RGB, 16-bit** image sequences.
- Cycles: **1024** maximum samples, **0.002** adaptive threshold, **64** minimum
  samples, with OpenImageDenoise.
- Output: `//../renders/<portrait scene filename without .blend>/frames/frame_`.
  For example, Shot 1 writes to
  `renders/gel_polish_lapohka_shot1_portrait_0_82/frames/frame_####.png`.

The scenes retain the source color treatment, lighting and animation. Keep
relative asset paths intact. Shot 3 requires both Alembic files in
`cache/gel_polish_lapohka_shot3_199_284/`; these generated caches are local and
gitignored. They must accompany a project handoff to another machine.

## Verification and review status

The [validation report](lapohka_portrait_validation.json) records unchanged
source files and sampled preservation of original object poses and material
assignments. Half-frame framing checks confirm the complete bottle during
Shot 1's readable holds, after frame 60 in Shot 2 including its handoff, and
throughout Shot 3. Shot 1's intended entrance and exit remain outside the frame.

Geometry and composition diagrams are available at:

- [Shot 1](../renders/lapohka_portrait_framing/shot01_framing.png)
- [Shot 2](../renders/lapohka_portrait_framing/shot02_framing.png)
- [Shot 3](../renders/lapohka_portrait_framing/shot03_framing.png)
- [Shot 4](../renders/lapohka_portrait_framing/shot04_framing.png)

These are **Workbench stills**, so they do not establish final color, gloss or
shimmer. Shot 3's liquid is omitted only from its diagram; it remains enabled
in the saved scene. Final Cycles water edges have not yet been visually
reviewed. See the production
milestones below for current render progress; review the completed production
images before encoding the mobile website hero.

## Website edit timing

These four native shot ranges contain **402 frames** in total. The current
website opening uses an existing retimed **493-frame** edit. Preserve that edit
retiming when assembling the portrait delivery; the scene conversion does not
replace it with a direct concatenation of the native ranges.

## Production queue started 2026-11-01

The authorized production queue was started in Blender using the RTX 4090 (OptiX), in Shot 1 -> 2 -> 3 -> 4 order, for all 402 frames. It uses the saved production settings and each scene's existing motion-blur choice. Shot 3 retains motion blur disabled. The queue skips complete existing frames and stops on cancellation or an error. Keep the Blender session open; Esc cancels the active render and stops the queue.

Event-written progress: [lapohka_portrait_production_queue.json](../renders/lapohka_portrait_production_queue.json). Starting the queue does not establish completed renders or final visual approval. No scene files are overwritten by the queue.

## OSL crash workaround, resumed at frame 61

On 2026-11-03 the latest Blender crash log showed EXCEPTION_ACCESS_VIOLATION in oslexec.dll during OSL shader optimization. Shot 1 had OSL enabled but no Script shader nodes. The queue now disables OSL only when the loaded scene has no Script nodes (including material, world, light and group node trees). This uses the standard Cycles shader compiler while preserving the saved scene, material nodes, lighting, cameras and quality settings. Scenes containing Script nodes retain their saved OSL setting.

Frames 0-60 passed image integrity checks and remain intact. Rendering resumed at Shot 1 frame 61, with 341 frames remaining. The workaround bypasses the crashing component; sustained stability and visual consistency of the shader backend transition still need review after frames are available. No claim of a completed render or a proven permanent crash fix is made.

Evidence: [saved crash log](../renders/gel_polish_lapohka_shot1_portrait_0_82/logs/osl_crash_20261103.txt). The event-written queue JSON records saved/render OSL settings per shot. Blender documents the OSL shader backend in its [manual](https://docs.blender.org/manual/en/latest/render/cycles/osl/index.html).

## Production milestone: Shot 1 complete

On 2026-11-03, Shot 1 frames 0-82 were complete and Shot 2 frames 57-131 were verified. All newly completed PNGs passed header, integrity and full decode checks. Rendering resumed at Shot 2 frame 132 with 244 frames remaining across Shots 2-4. All four scene file hashes still matched the initial queue manifest.

A preview-size visual comparison of Shot 1 frames 60 and 61 found no obvious discontinuity in background, gold, blue lacquer or shimmer across the OSL-to-standard shader transition. This is a visual check, not proof of identical shader output. No newer crash log was found after the earlier oslexec.dll failure; the cause of the later session ending is unknown. The OSL workaround remains active for scenes without Script nodes.

## Production milestone: resume 2026-11-06

The disk audit found Shots 1 and 2 complete, and Shot 3 frames 199-253 complete:
280 of 402 images, with 122 remaining. All newly completed images passed PNG
integrity, full decoding, and 2160x3840 RGB16 checks. All four approved scene
hashes still match. The previous queue status record was stale; actual validated
image files determine the resume point, Shot 3 frame 254.

A separate crash log from November 5 records an access violation in
`nvrtum64.dll` when the queue first entered Shot 3 on OptiX. This identifies the
crashing library, not a proven root cause. The reusable queue now uses the
already discovered RTX 4090 CUDA device for Shot 3, while other shots retain
OptiX. Resolution, sampling, denoising, materials, caches and saved scenes are
unchanged. Continued rendering will establish whether this bypass avoids the
failure; review adjacent frames 253/254 once available for visual continuity.

Evidence: [NVIDIA crash log](../renders/gel_polish_lapohka_shot3_portrait_199_284/logs/optix_crash_20261105.txt).
Queue helper: [render_lapohka_portrait_queue.py](../scripts/render_lapohka_portrait_queue.py).

## Production complete: 2026-11-06

All 402 frames are complete: Shot 1 has 83, Shot 2 has 142, Shot 3 has 86,
and Shot 4 has 91. Every image has the expected 2160x3840 RGB16 PNG header and
end marker. The final 122 images passed CRC verification and full decoding;
earlier images passed the same checks during previous resumes. There are no
missing, corrupt or unexpected frame files. All four scene hashes still match.

Shot 3 frames 253 and 254 show no obvious color or reflection discontinuity at
preview size across the CUDA resume; this is not a pixel-identical comparison.
The liquid and bubbles are present in the production renders. A representative
[contact sheet](../renders/lapohka_portrait_production/portrait_contact_sheet.jpg)
shows the four portrait compositions.

Video packaging uses `package_opening_production.py --portrait --shot N`,
with each native 30 fps sequence delivered next to its frames as a 4K H.264
MP4 and ProRes 4444 XQ MOV. Each delivery manifest records source image hashes
and complete output decode verification. The source PNGs remain the 16-bit
masters. These native clips do not incorporate the website's existing retiming.

Read-only correlation of the landscape delivery clips against the website
video recovered opening cut intervals 0-111, 112-301, 302-384 and 385-492.
Shot 3 maps to source frames 202-284; the other shots include retiming and
holds. A uniform 493/402 time stretch would change the established edit.
Exact reconstruction of that edit remains separate from native shot delivery.

The four 4K MP4s and four ProRes 4444 XQ editing masters are now complete and
fully decoded for verification. A 1080x1920 combined viewing copy contains all
402 frames at native 30 fps, 13.4 seconds, without audio. It converts the
source sRGB transfer to BT.709. See the
[delivery index](../renders/lapohka_portrait_production/README.md) for all files.
The website and existing Bossa-ending preview have not been replaced.
