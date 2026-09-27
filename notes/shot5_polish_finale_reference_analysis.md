# Shot 5: reference direction and production guide

Current scene: `scenes/gel_polish_lapohka_shot5_376_528.blend`.

Original motion reference: `references/lapohka_3d_motion_shots/Lapohka 3D Motion - Shot 5 (f376-528).mp4`.

Range: f376-528 inclusive, 153 frames at 30 fps, 5.10 seconds. The finished scene combines the original reference's close product arrival and pullback with the user's Hang Pure collection presentation. The hero lands in the rack; the board and rack sit on a seamless gradient studio floor.

## Completed production delivery

| Output | Path |
| --- | --- |
| 4K playback video, H.264 CRF 14 | [lapohka_s5_f376-528_polish_finale_4k.mp4](../renders/lapohka/shot5_f376-528/lapohka_s5_f376-528_polish_finale_4k.mp4) |
| 4K master, ProRes 4444 XQ | [lapohka_s5_f376-528_polish_finale_4k_master_prores4444xq.mov](../renders/lapohka/shot5_f376-528/lapohka_s5_f376-528_polish_finale_4k_master_prores4444xq.mov) |
| Verified frame/output manifest | [shot5_production_manifest.json](../renders/lapohka/shot5_f376-528/shot5_production_manifest.json) |
| Source sequence | `renders/shot5_polish_finale_production_4k/production_4k/frame_0376.png` through `frame_0528.png` |

All 153 source images are 3840 x 2160, 16-bit RGB PNGs. The package tool checked image integrity and recorded SHA256 hashes and render metadata. Both encoded videos passed a complete 153-frame decode check. The silent deliveries retain the 30 fps timing and the rendered color treatment.

The production settings are Cycles at 1024 maximum samples, adaptive noise threshold 0.002 and 64 minimum samples; OpenImageDenoise HIGH with accurate albedo and normal inputs; AgX with Medium High Contrast, exposure -0.85; and motion blur enabled. These settings are recorded per frame in the adjacent JSON sidecars and delivery manifest. Persistent render data is disabled to refresh instance transforms between frames.

The PNGs contain the display-referred AgX result. Packaging converts RGB to BT.709 YCbCr for the video codecs, retaining the sRGB transfer tag and making no creative color adjustment. The PNG sequence remains the original 16-bit render source.

## What the original reference contributes

The original opens close to a suspended beverage can, then pulls back to a warm arrangement with a tall pineapple on the right, a ribbed glass on the left and small fruit in the foreground. The group rests on a round pale plinth. The can settles into a held view and lifts out near the end.

The useful visual rhythm is a close product arrival, a gradual reveal of related objects, an impact/settle and a readable final composition. The user-directed polish version uses its own product silhouettes and display arrangement:

| Frames | Reference beat | Current polish adaptation |
| --- | --- | --- |
| 376-384 | Suspended can close-up with restrained orientation changes | Slightly low-angle close-up of the bottle above the collection, looking gently upward |
| 392-424 | Pullback reveals supporting objects and platform | Pullback reveals the sample board and full rack on the studio floor; bottle descends over its front-row slot |
| 422-425 | Lead-in to the settled group | Bottle slows just above the shelf, providing anticipation before contact |
| 426-451 | Arrival and settling | Accelerating drop, f432 contact, f436 rebound, then recovery by f451 |
| 452-528 | Held group followed by an upward exit in the reference | Complete collection remains readable; the hero stays seated in R1/C3 through the ending |

These frame ranges are visual timing observations and authored adaptation choices, not recovered source camera or physics settings. The final held ending deliberately follows the user's rack-landing direction.

### Framing observations retained from the reference study

At reference f376, the can axis is almost vertical, with approximately 0-2 degrees of visible lean. Its center is around normalized X 0.535, its top is around Y 0.27 measured from the upper edge, and its lower body extends below the image. Supporting objects are absent from that crop. The polish bottle has a much longer cap relative to its body, so matching the exact can silhouette would underrepresent the lacquer. The current opening prioritizes the bottle's recognizable face and a close, slightly upward view, as requested by the user.

At reference f460, the can is near X 0.512 and spans roughly Y 0.25-0.82, or 57% of image height. The left glass spans approximately X 0.16-0.35 and Y 0.03-0.70; the large right prop balances it. Those observations explain the earlier aim to balance objects on both sides. The final collection shot instead fits the complete board and rack, with the main bottle completing the rack rather than standing alone in front.

The original's cast shadows point mainly toward screen-right with a modest downward component, approximately 0-15 degrees below horizontal in the held view. Broad soft-edged shadows ground the products. Earlier reference measurements gave display-referred luminance near 0.40 in a hero shadow and 0.73 on neighboring lit surface; these are approximate encoded-image observations, not linear-light ratios or material settings.

The former window-shadow wall and raised platform were replaced at the user's request. The current matte mauve/lavender floor curves continuously into the background, avoiding a visible cutoff, while broad area lights preserve contact shadows and controlled product highlights.

## Current assets and scene controls

The composition contains the complete six-row, six-column rack, the tilted stand-free sample board and the animated hero. There are 35 supporting bottles plus the hero, covering shade IDs 211-246 exactly once. Hero shade 225 occupies front-row slot R1/C3; Peach 213 fills R3/C3. See [collection design and asset authoring](shot5_brand_collection_direction.md) for dimensions, palette, leather stitching and magnetic-shimmer details.

| Control | Purpose |
| --- | --- |
| `SHOT05_Bottle_Travel` | Direct editable translation keys for the descent, hesitation, shelf contact and bounce |
| `SHOT05_Bottle_Tilt` | Direct editable forward/back tilt, sideways lean and vertical-axis turn |
| `SHOT05_Bottle_Assembly` | Main product instance; tagged as row 1, column 3, shade 225 |
| `SHOT05_Camera` and `SHOT05_CameraTarget` | Close opening, pullback and final composition |
| `SHOT05_LacquerFocus` | Focus target on the lacquer surface |
| `SHOT05_CollectionSampleBoard` | User-sized board placement, scale and lean |
| `SHOT05_CollectionRack` | Rack hardware placement |
| `SHOT05_CollectionRack_Bottle_*` | Supporting bottle positions and restrained delayed responses |
| `SHOT05_StageReveal` and `SHOT05_StageImpact` | Static organizational parents; the collection does not rise through or bounce below the floor |
| `SHOT05_GradientStudioSweep` | Continuous floor and curved gradient backdrop |

The product assembly is turned upright about local X. On `SHOT05_Bottle_Tilt`, Y primarily controls visible sideways lean, X controls forward/back tilt, and Z turns the upright bottle around its vertical axis. Z is therefore not image roll.

Linked production dependencies are `assets/props/brand_collection_bottle_rack_36.blend`, `assets/props/brand_collection_sample_board_stitched.blend`, `assets/products/gel_polish_bottle.blend` and `assets/environments/studio_environment_world.blend`, plus their referenced textures. Keep relative library paths intact. The source board `assets/props/brand_collection_sample_board.blend` is preserved for authoring, with the user's dimensions and removed stand.

## Verification and repeatable tools

The approved collection passed 129 sampled poses covering layout, intersections, shelf/floor clearance, opening view, final framing and resource availability. All 36 shade IDs and slots are present. The cleanup audit preserved 102 active scene objects and unchanged scene geometry. Deliberate joins within manufactured assemblies are excluded from inter-assembly collision checks.

| Script | Use |
| --- | --- |
| `scripts/validate_shot5_gradient_collection.py` | Read-only layout, geometry, dependency and framing audit |
| `scripts/render_lapohka_shot5_review.py` | Review stills or a low-resolution motion preview without saving production settings |
| `scripts/render_shot5_board_detail.py` | Close-up of the linked board under the shot's lights, without saving the scene |
| `scripts/render_shot5_production.py` | Repeatable 4K production renderer with the delivered quality settings and resumable PNG/JSON output; does not save the source scene |
| `scripts/package_shot5_production.py` | Verify the existing PNG sequence, encode both delivery formats and verify their decoded frame counts |

Run Blender review/validation tools against the canonical scene with factory startup and automatic script execution disabled. The review renderer accepts `-- stills 376 432 436 480 528`, `-- 4k 480` or `-- preview`. Review settings are intentionally lower than the completed 1024-sample production render. `python scripts/package_shot5_production.py` packages the existing production sequence and does not launch Blender or rerender frames.

For a future approved revision, run Blender with the canonical scene and `--python scripts/render_shot5_production.py`. Its default output is the existing production sequence directory; use `-- --output renders/new_revision` for changed scene content. Existing PNG/JSON pairs are retained when resuming, so use a fresh directory when the source or settings change. The archived production snapshot remains as provenance for the completed render. The current sequence is complete and does not need another render.

## Historical work and cleanup

The final direction supersedes the earlier manicure-tool arrangement, community tray and glass adaptations, freestanding sample fan, smaller six-bottle rack and levitating platform. The board evolved from coarse shimmer to distinct magnetic bands, then gained fine noisy pigment, a leather cover and stitched edging. The rack grew to all 36 shades, and the hero's former upward exit became a seated final hold.

Numbered working scenes and one-time migration scripts are retired. Historical revisions that were committed remain available through Git; their old paths are not instructions for the current production workflow. Original source downloads, provenance and reference media remain preserved. Generated renders, review snapshots and delivery videos are not committed to source control.
