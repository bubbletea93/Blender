# Shot 5: polish finale

Current revision: `scenes/gel_polish_lapohka_shot5_376_528_polish_finale_v002.blend`.
Previous scene: `scenes/gel_polish_lapohka_shot5_376_528_polish_finale_v001.blend`.
Reference: `references/lapohka_3d_motion_shots/Lapohka 3D Motion - Shot 5 (f376-528).mp4`.
Range: f376-528 inclusive, 153 frames at 30 fps, 5.10 seconds of output.

Review deliverables: [motion preview](../renders/lapohka/shot5_f376-528/lapohka_s5_f376-528_polish_finale_v002.mp4),
[reference comparisons](../renders/shot5_polish_finale_v002/reference_comparison.jpg),
[f376 comparison](../renders/shot5_polish_finale_v002/comparison_0376.jpg), and
[f460 comparison](../renders/shot5_polish_finale_v002/comparison_0460.jpg).
The 960x540 review video passed a complete 153-frame decode check. No final
4K production image sequence has been rendered for this shot.

Final camera-envelope check: bottle top remains inside the image for all
133 checked frames from 376 through 508. The whole bottle is inside the image
from 392 through 508. At 376 its conservative top bound is 25.2% down from the
upper image edge; the lower body is intentionally cropped. See
`renders/shot5_polish_finale_v002/camera_validation.json`.

The finale reuses the approved fine-shimmer polish bottle and adds manicure
objects created specifically for this shot. It lives in a new Blender file;
the earlier shots and canonical product asset are preserved.

## Reference observations

The original opens close to a suspended beverage can, then pulls back to a
warm tabletop arrangement. A tall pineapple occupies the right side, a ribbed
glass stands to the left, and small fruit sit in the foreground. The group
rests on a round pale plinth against a warm backdrop with broad shadows.
The can settles into a held product view before lifting upward out of the
composition at the end.

| Reference frames | Visible beat | Polish adaptation |
| --- | --- | --- |
| 376-384 | Close view of the can, suspended with small orientation changes. | Close arrival of the upright bottle, with its front lacquer visible and a restrained tilt. |
| 392-424 | Camera pulls back; glass, pineapple and platform enter the composition. | Pullback reveals the left brush holder, right nail-swatch fan, magnetic tool, loose nail tips and ceramic podium. |
| 436-452 | Product group settles into the full tabletop composition. | Bottle completes a small settling motion; supporting props finish their gentle descent. |
| 452-508 | Stable product display with subtle remaining motion. | Readable bottle and manicure display hold, with a quiet camera drift. |
| 520-528 | Can rises quickly and exits toward the top of the picture. | Bottle lifts upward, leaving the supporting manicure objects on the podium. |

These are visual timing observations, not recovered source camera or physics
settings. The decoded contact sheet is
`renders/shot5_polish_finale_v001/reference_contact_sheet.png`; frame selection
is recorded in `reference_frames.json` in the same directory.

### Reference framing and the v002 revision

Measurements below are approximate image-space observations from the decoded
960 x 540 references. Coordinates run from the upper-left corner, normalized
to the frame width and height. They describe visual targets, not recovered
camera settings.

At f376 (`reference_01.png`), the can axis is nearly vertical, with about
0-2 degrees of visible lean. Its center lies around X 0.535; its top is fully
inside the frame around Y 0.27, and its lower body continues below the bottom
edge. The podium and supporting objects are absent from this opening crop.
The visible top rim and right side give a modest elevated, three-quarter
view rather than an overhead or flat frontal view.

The v001 opening instead cuts off the polish cap, shows the complete lacquer
disc, and already reveals the swatch fan and podium. The revision should
keep the cap end inside the frame, crop the lower bottle rather than the top,
and delay the supporting objects' reveal. Preserve the polish identity by
keeping some lacquer visible; the reference can and bottle have different
proportions, so a literal silhouette match would overemphasize the long cap.
The existing opening camera elevation is approximately 14 degrees, already
a useful starting point; changing the aim and crop matters more than making
the viewpoint much higher.

The bottle assembly is turned upright about local X. Consequently,
`SHOT05_Bottle_Tilt` Y primarily controls visible sideways lean, X controls
forward/back tilt, and Z turns the upright bottle about its vertical axis.
Do not treat its Z rotation as image roll. A nearly upright starting axis,
with restrained depth tilt and a small three-quarter turn, follows the
reference while retaining the lacquer face.

At f460 (`reference_10.png`), the central can is centered near X 0.512,
extends from roughly Y 0.25 to 0.82, and occupies about 57% of frame height.
The tall left glass spans approximately X 0.16-0.35 and Y 0.03-0.70. The large
right prop creates a complementary mass behind the hero. The v001 hero
height is already close to this proportion, but its flat magnet on the left
leaves most of the upper-left composition empty. The added brush holder
provides an upright mass around the left quarter of the image; its brushes
can rise toward or above the hero cap without overlapping the central bottle.

### Reference shadows

The reference backdrop carries broad, continuous vertical bands rather than
isolated patches or a triangular shadow ending near the platform. Aim for
two or three readable vertical tonal bands through the visible wall. Extend
the shadow casters beyond that wall's visible bounds and keep the curved
wall-to-floor transition hidden behind the podium where possible. Casters
remain invisible to the camera and glossy/transmission rays while casting
actual shadows.

The tabletop cast shadows point predominantly to screen-right with a modest
downward component, approximately 0-15 degrees below horizontal in the held
view. The tall supporting objects produce shadows extending roughly
10-20% of frame width. These distinct silhouettes and soft penumbras give
the reference its directional light; ambient contact shading alone does not
reproduce it. The v001 review is too uniformly illuminated and has weak
tabletop shadows.

As a relative visual check, the f460 reference's hero-shadow sample has
display-referred luminance around 0.40 against nearby lit podium around
0.73. Broad dark/bright wall samples are approximately 0.50/0.69. These are
encoded image measurements, not linear-light exposure ratios or prescribed
material colors. Preserve readable shadow depth while retaining soft edges
and enough front fill to reveal the flat lacquer face. Tune the main light
direction in the camera view; increasing a side light's power alone will
not correct an incorrectly directed shadow.

## Why these new objects

The fan of five polished nail swatches demonstrates the finish on a nail
shape and supplies a tall color accent on the right. A clear acrylic base
and rear cradle physically support its clear stems and gold pivot ring.
The upright manicure brush holder supplies the tall left-hand mass that the
reference glass provides. The slim cat-eye magnet wand connects to the
magnetic lacquer finish as a lower accessory. Two loose polished tips
provide small foreground accents. A satin ivory ceramic podium carries the
group and its contact shadows.

The revised composition retains the reference's central hero, tall props
on both sides and small foreground accents. The brush holder replaces the
v001 choice of relying on the low magnet alone to balance the right fan. The polish
props communicate application and finish rather than beverage ingredients.

## Reusable assets

New library: `assets/props/manicure_finale_props.blend`.
Builder: `scripts/build_manicure_finale_props.py`.

| Asset collection | Evaluated dimensions | Orientation and use |
| --- | --- | --- |
| `Prop_NailSwatchFan` | 96.47 x 26 x 102 mm | Five swatches; front faces -Y, up +Z; acrylic support rests at Z0. |
| `Prop_CatEyeMagnetWand` | 84.5 x 7.5 x 6.2 mm | Lies along local X; satin charcoal handle, brushed steel head and gold collar. |
| `Prop_ManicureBrushHolder` | 58.72 x 42.90 x 134 mm | Upright holder and brushes; bottom at Z0; supplies the left-side silhouette. |
| `Prop_LooseTip_Teal` | 10.39 x 28 x 2.90 mm | Independent convex teal tip, polished surface faces +Z. |
| `Prop_LooseTip_Raspberry` | 10.39 x 28 x 2.90 mm | Independent convex raspberry tip, polished surface faces +Z. |
| `Stage_CeramicPodium` | 320 mm diameter x 50 mm high | Bottom at Z0, top at Z0.05 m; softly beveled satin ceramic. |

Collections are marked as assets. Their dimensions are authored scene scales,
not measurements of a specific commercial manicure tool. The library is
self-contained: readback found no linked data, external images or shader
object dependencies. All seven nail meshes are closed with outward normals.

The five swatch materials were appended from the approved Shot 4 v004 fine
shimmer scene. They are named `PROP_Lacquer_Aubergine`,
`PROP_Lacquer_PetrolTeal`, `PROP_Lacquer_PearlIvory`,
`PROP_Lacquer_Raspberry` and `PROP_Lacquer_MidnightBlue`. Their UV scale is
14.5 units per metre so the smaller nail tips retain comparable physical
pigment density. They use actual material detail, with no added image noise.

Asset QA and reports:

- `renders/shot5_polish_finale_v001/props_review.png`
- `renders/shot5_polish_finale_v001/props_asset_report.json`
- `renders/shot5_polish_finale_v001/props_mesh_checks.json`
- `renders/shot5_polish_finale_v001/props_dependencies.json`

## Reused scene sources

The hero assembly was appended from
`scenes/gel_polish_lapohka_shot4_285_375_bottle_array_v004_fine_shimmer.blend`,
using its petrol teal shade and corrected fine-shimmer finish. The production
meshes retain their link to `assets/products/gel_polish_bottle.blend`.
The assembly includes body, detailed cap, lacquer and front lens.

The Shot 5 scene links the new prop collections from
`assets/props/manicure_finale_props.blend`. Its studio environment retains
the dependency on `assets/environments/studio_environment_world.blend`.
Library paths are relative to the scene. Lighting and the seamless warm
backdrop are local to this shot.

Scene builder: `scripts/build_lapohka_shot5_polish_finale.py`.
Preserve later manual edits before rebuilding a scene. The v002 revision
reuses the same prop library, now including `Prop_ManicureBrushHolder`.

## Editing the motion

| Control | Editable behavior |
| --- | --- |
| `SHOT05_Bottle_Travel` | Direct XYZ Location keys for arrival, settle, hold and upward exit. |
| `SHOT05_Bottle_Tilt` | Direct XYZ Euler Rotation keys for the restrained orientation changes. |
| `SHOT05_Bottle_Assembly` | Collection instance holding the four-part bottle; child of the tilt control. |
| `SHOT05_Camera` | Direct Location keys control the pullback and quiet drift. |
| `SHOT05_CameraTarget` | Direct Location keys set the composition aim through a Track To constraint. |
| `SHOT05_Camera_DATA` | Sparse focal-length keys coordinate framing with the camera move. |
| `SHOT05_LacquerFocus` | Focus target parented to the bottle at the lacquer front. |
| `SHOT05_StageReveal` | Direct Z Location keys move the podium and every supporting prop together into the opening reveal. |
| `SHOT05_SwatchFan`, `SHOT05_CatEyeMagnet`, `SHOT05_LooseTip_Teal`, `SHOT05_LooseTip_Raspberry` | Direct Z Location keys for a gentle settling motion. |

The animation is authored product choreography. There are no motion drivers
or rigid-body simulations. Keys use Bezier interpolation with Auto Clamped
handles. Timeline markers identify macro arrival, prop reveal, bottle settle,
hero composition, lift preparation, upward exit and the cut.

Focus follows the actual lacquer surface to retain the fine shimmer rather
than focusing on the platform. The depth-of-field setup uses f/64 to keep the
small product group readable.

## v001 production settings and previews

The v001 Blender file was prepared for Cycles rendering at 3840 x 2160, 30 fps,
with a maximum of 512 samples and adaptive sampling threshold 0.003.
OpenImageDenoise uses color, albedo and normal passes with accurate
prefiltering and high quality. The random seed is fixed. Motion blur is
enabled, and the saved image output is 16-bit RGB PNG to
`renders/shot5_polish_finale_v001/production/frame_`.

These saved settings describe the production setup; they do not establish
that a full production sequence has already been rendered. Review stills
and preview videos may use reduced resolution and sample counts to judge
framing, lighting and motion. Their completion must not be reported as a
completed 4K production render.

## v001 placement and animation validation

Read-only validation of v001 checked evaluated instance bounds at all 153 frames.
It used each mesh part's transformed bounds, including depth when comparing
objects. No overlap candidates were found between the hero and supporting
props, or between separate supporting props.

- Hero minimum clearance above the podium: 0.250 mm, at f439.
- Fan and wand minimum clearance: 0.200 mm.
- Loose tip minimum clearance: 0.210 mm.
- Every held object fits within the 160 mm podium radius. The furthest
  conservative corner is on the fan at radius 126.98 mm, leaving about 33 mm.
- No missing linked libraries or animation drivers were found.
- The checked scene contains 21 directly editable animation curves, with
  no more than 12 keys per channel.

These are conservative geometry-envelope checks, not a claim of simulated
contact dynamics. Results are recorded in
`renders/shot5_polish_finale_v001/props_scene_validation.json`. The validation
script does not save or modify the scene.

This v001 report predates the added brush holder and v002 camera/lighting
changes. The separate v002 geometry check is recorded below; image-based
framing and shadow review remains distinct from geometry validation.

## v002 reveal and geometry validation

`SHOT05_StageReveal` parents the podium, swatch fan, brush holder, magnet and
both loose tips. Its vertical offset is -110 mm at f376, -85 mm at f384,
-25 mm at f397 and zero from f414. Moving the complete stage delays the
supporting objects' entrance while preserving their relative placement.
The bottle follows its independent arrival and settling motion.

The final v002 opening uses a 58 mm lens and anchors the cap end around
27% of the image height, with the lower lacquer body partially cropped.
The camera pulls back more quickly between f376 and f400 to keep the cap
inside the frame as the composition is revealed.

The enlarged fan uses a uniform scale of 1.22. The new brush holder retains
its authored scale and sits 0.2 mm above the local tabletop. All supporting
objects share the stage parent, including their existing settling keys.
Consequently their contact clearance must be measured against the moving
tabletop, not against a fixed world Z of 50 mm.

Validation checked every integer frame from f376 through f528 against the
saved v002 scene. The minimum conservative clearances are:

| Assembly | Minimum tabletop clearance | Minimum radial margin to the 160 mm podium edge |
| --- | --- | --- |
| Bottle | 0.250 mm, at f439 | 105.370 mm |
| Swatch fan | 0.200 mm | 24.586 mm |
| Brush holder | 0.200 mm | 45.083 mm |
| Magnet wand | 0.200 mm | 42.553 mm |
| Teal loose tip | 0.210 mm | 17.177 mm |
| Raspberry loose tip | 0.210 mm | 39.642 mm |

The tabletop follows the stage offset plus 50 mm and reaches world Z 50 mm
at f414. Evaluated part boxes produced 144 conservative axis-aligned overlap
candidates; all were separated by the subsequent three-dimensional oriented
box check. No between-assembly intersection candidates remained. Intended
connections inside each assembled prop, such as brush ferrules or the fan
pivot, are outside this clearance check.

No missing libraries, unknown instance parents or animation drivers were
found. The revised scene has 18 active-slot animation curves with at most
12 keys per channel. The validator filters action slots so camera-object
and camera-data channels are not counted twice.

Report: `renders/shot5_polish_finale_v002/scene_validation.json`.
Script: `renders/shot5_polish_finale_v002/validate_scene.py`.
The script changes evaluation frames in memory, writes its report, and never
saves the scene. These geometry checks do not replace visual review of the
macro crop, cast shadows or camera motion.

Saved v002 production settings remain Cycles at 3840 x 2160, 30 fps, up to
512 samples, adaptive threshold 0.003, high-quality OpenImageDenoise with
accurate albedo/normal prefiltering, fixed random seed and 16-bit RGB PNG.
The v002 review stills use 1920 x 1080 at 256 samples; its motion preview
uses 960 x 540 at 64 samples. These review outputs are separate from a
completed 4K production sequence.

### Brush-cup topology correction

The initial revolved cup profile contained repeated zero-radius rings and
an open underside. The reusable asset now has single center vertices for
the inner floor and outer underside, each joined by correctly wound
triangles. Readback verifies 1,346 vertices, 1,536 faces, no zero-area faces,
no boundary or nonmanifold edges, and positive signed volume
0.0000240102 cubic metres. The hollow vessel retains its original exterior
bounds and rose-smoke glass material.

The other 32 mesh objects in the prop library retain identical vertex and
topology hashes, transforms, bounds and material assignments. The correction
is confined to the cup geometry block in the asset builder.
Report: `renders/shot5_polish_finale_v002/cup_topology_validation.json`.
Recovery copy: `renders/shot5_polish_finale_v002/manicure_finale_props_before_cup_fix.blend`.

## v003 low-angle opening and three-beat landing

Scene: `scenes/gel_polish_lapohka_shot5_376_528_polish_finale_v003.blend`.
This revision supersedes the v002 opening camera and settling motion above.
The original live v002 session was preserved in a recovery copy before opening
v003; the shared product and prop libraries are unchanged by this revision.

At f376 the 62 mm camera sits at Z 84 mm, below the raised bottle's foot,
and looks upward about 15 degrees toward Z 166 mm. The cap stays visible
while the lower lacquer face extends beyond the crop. Comparison with the
reference is `renders/shot5_polish_finale_v003/comparison_0376.jpg`.
The camera then pulls back and rises to reveal the manicure arrangement.

| Beat | Frames | Behavior |
| --- | --- | --- |
| Approach and anticipation | 376–425 | Descent eases to a short hover about 12 mm above the settled position. |
| Release and action | 426–432 | The bottle accelerates toward contact; the impact is not eased to a stop. |
| Reaction | 432–451 | A 5.5 mm rebound diminishes through two smaller bounces. The pivot is at the supporting foot. |
| Overlapping recovery | 433–470 | The podium transmits an impulse; heavier props recover sooner and loose tips continue longer. |
| Hold and exit | 470–528 | Arrangement settles, followed by the established upward bottle exit. |

The podium's first compression is 1.4 mm at f434 and rebound is 1 mm at
f438. Prop roots inherit this common movement. Additional local responses
start 1–5 frames after impact: holder 0.45 mm, fan base 0.65 mm, magnetic
wand 2 mm, loose tips 3.5 and 4 mm. Brush and swatch controls add delayed
angular follow-through. This is authored animation representing different
weights, not a rigid-body simulation.

Editable controls:

- `SHOT05_Bottle_Travel`: direct location keys for descent, bounce and exit.
- `SHOT05_Bottle_Tilt`: direct Euler keys about the foot.
- `SHOT05_StageImpact`: common landing impulse.
- `SHOT05_StageReveal`: introductory stage lift.
- Individual prop roots: delayed local bounce and rotation.
- `SHOT05_BrushFlex_01..03` and `SHOT05_SwatchFlex_<shade>`: independent swaying.

Fan and brush-holder object containers were made local to support independent
motion; mesh and material data remain linked. The outer brushes' resting
lean was reduced locally to prevent intersection with the cup rim during
their sway. No motion drivers were added.

Validation covered 306 samples: all 153 integer frames plus quarter-frame
sampling through impact and recovery. The bottle retains at least 0.25 mm
tabletop clearance, props at least 0.20 mm, and loose tips 0.21 mm. No
between-assembly or cup/brush intersections, off-podium props, or missing
libraries were found. Report: `renders/shot5_polish_finale_v003/scene_validation.json`.

Visual sequence inspection caught a stale podium transform in the initial
sequential preview at f432, absent from a fresh single-frame render. Persistent
Cycles render data is now disabled in both the saved scene and review renderer.
Geometry validation alone did not expose that render artifact.

The review sequence is 960x540, 64 samples, 30 fps. The saved production
settings remain 3840x2160 and 512 maximum samples; no v003 production
sequence has been rendered. The community assets recommended during v003
were subsequently approved and integrated in v004; see
`notes/shot5_community_asset_recommendations.md`.

The corrected complete sequence passed its 153-frame decode check. Review:
`renders/lapohka/shot5_f376-528/lapohka_s5_f376-528_polish_finale_v003.mp4`.
The motion contact sheet confirms correct podium placement at impact after
disabling persistent data: `renders/shot5_polish_finale_v003/motion_contact_sheet.jpg`.

## v004 approved community props

The user approved the ceramic tray and faceted glass cup on 2026-09-24.
Both are acquired and adapted in the separate scene
`scenes/gel_polish_lapohka_shot5_376_528_polish_finale_v004.blend`; v003 is
preserved. The low-angle opening, bottle motion and three-beat landing are
retained. Cycles persistent render data remains disabled.

Santiago Adrio's Organic Ceramic Tray (BlenderKit Royalty Free) is uniformly
scaled to 80 mm long and recolored with a warm-ivory glaze while retaining
its source texture detail. The original is a deep leaf-shaped bowl. The
teal nail tip leans against the inner slope, facing the camera above the
rim; the 85 mm magnetic wand rests alongside it on the podium. The tray's
stage-parented control adds a delayed 0.25 mm first hop, and the loose tip
retains independent local follow-through. The raspberry tip remains a
separate compositional counterweight.

cczero's Glass Cup (BlendSwap CC0) replaces the procedural fluted vessel
and gold foot. Its derivative is 65 mm tall and 51.976 mm in diameter,
with the branded bump-map branch removed. The holder root, three brush
controls, nine brush meshes and their materials and actions are preserved.
The source glass and separate smudge-roughness texture are preserved in the
original file. The derivative uses roughness `0.008 + source × 0.035` for a
clean cosmetic display, retaining the original packed map and IOR 1.45.

Both original downloads are preserved with hashes and license records in
`assets/props/community/organic_ceramic_tray/` and
`assets/props/community/glass_cup_cczero/`. Reusable derivatives are
`assets/props/community/manicure_community_props.blend` (tray) and
`assets/props/community/glass_cup_cczero/brush_holder.blend` (glass holder).
See `notes/shot5_community_asset_recommendations.md` for source links.

The glass-specific integration check passed 306 samples with no brush/cup
intersections and a minimum clearance of 2.494 mm. Full v004 scene geometry
validation also passed 306 samples, including quarter frames through impact
and recovery. It found zero external or internal intersections, zero
containment warnings, and all props within the podium; the closest edge
margin is 5.901 mm at the tray. Animated teal-tip/bowl clearance is included.
Report: `renders/shot5_community_v004/scene_validation.json`.
Camera framing and materials passed rendered 1920 × 1080 still/reference
comparisons at f376, f400, f460 and f528. The complete 153-frame motion preview
passed its decode check. Visual inspection at impact f432 and recovery f440
confirmed correct podium placement and delayed prop responses. The preview
uses 960 × 540, 64 Cycles samples and 30 fps. It is a completed review,
not a completed 4K production render.

- Video: `renders/lapohka/shot5_f376-528/lapohka_s5_f376-528_polish_finale_v004.mp4`
- Manifest: `renders/lapohka/shot5_f376-528/lapohka_s5_f376-528_polish_finale_v004_manifest.json`
- Reference comparison: `renders/shot5_polish_finale_v004/reference_comparison.jpg`
- Motion contact sheet: `renders/shot5_polish_finale_v004/motion_contact_sheet.jpg`

The composition stays dry; no new LiquiGen simulation has been started.

## v005 brand collection display

The user's product photographs on 2026-09-25 establish a new collection-display
direction. The active scene is
`scenes/gel_polish_lapohka_shot5_376_528_polish_finale_v005.blend`.
The v004 scene, its completed review and the earlier prop libraries are
preserved. Only the new scene removes the tray, glass cup, brushes, magnet,
loose tips and freestanding swatch fan from its shot collection.

The new linked libraries are purpose-built from those supplied photographs:

| Library | Contents |
| --- | --- |
| `assets/props/brand_collection_bottle_rack.blend` | Six full-size product variants in three columns on two clear acrylic tiers; thin side panels, rails, polished shelf edges and silver fasteners. |
| `assets/props/brand_collection_sample_board.blend` | Landscape 140 × 108 mm sample face, a four-lobed inner panel bordered by 95 pearls, 72 modeled nails in 36 shade pairs numbered 211–246, and a clear stand making the assembly about 148 mm tall. |

The sample board groups nine shade pairs at the top, left, right and bottom
around the HANG PURE / STARRY CAT EYE label. The modeled lacquer surfaces
reuse the approved fine-shimmer finish at a physical UV scale of 14.5 units
per metre. The six rack shades are Pearl Ivory, Blush Rose, Amethyst, Molten
Copper, Sapphire and Emerald. These are an editorial color-family adaptation,
not a color-calibrated reproduction of catalogue shades.

All rack bottles retain the hero's full evaluated size: approximately
45.884 × 32.845 × 101.072 mm. The rack assembly measures approximately
169.680 × 96.335 × 145.272 mm. The sample board's evaluated support-inclusive
bounds are approximately 140.400 × 35.425 × 148.200 mm. The satin-ivory podium
is widened to 410 mm diameter while retaining its 50 mm height.

The board is staged on the left at X −107 / Y +23 mm with +10° yaw; the rack
is on the right at X +98 / Y +29 mm with −8° yaw. Both roots are parented to
`SHOT05_StageReveal`. The low-angle f376 opening and vertical hero choreography
are retained, including anticipation, accelerating drop, rebound and upward
exit. The hero moves forward along Y after the close-up, and the later
camera reveal and hold widen for the larger display arrangement. The existing
directional lighting and continuous vertical background shadow setup remain.

Direct animation controls remain editable:

- `SHOT05_Bottle_Travel` and `SHOT05_Bottle_Tilt`: the hero's motion and pose.
- `SHOT05_CollectionRack`: a small delayed base response.
- `SHOT05_CollectionSampleBoard`: a softer delayed response; mounted tips and
  pearls remain attached.
- Six `SHOT05_CollectionRack_Bottle_R*_C*_<shade>` controls: individually
  delayed, restrained rebounds and rocking at their supporting feet.

Build reports are in `renders/shot5_brand_collection_v005/`:
`scene_build.json`, `rack_build.json` and `board_report.json`. They record
asset construction and placement. Full-scene validation passed all 306 samples,
including quarter frames around impact: zero detected intersections, shelf
penetration, podium-boundary failures or missing libraries/textures. The nearest
rack edge remains 7.138 mm inside the podium, and every bottle retains at least
0.20 mm clearance above its shelf. The f376 camera, lens and hero matrices
match v004 exactly. Report: `validation.json`.

Rendered 1920 ? 1080 / 256-sample composition checks at f376, f400, f432,
f460, f480 and f528 are in `renders/shot5_polish_finale_v005/`. The opening,
display reveal, impact and exit have been visually checked.
No new video or production image sequence has been requested or rendered
for v005. The saved 4K / 512-sample settings remain preparation for a later
production render. No liquid effect is added to this collection presentation.

## v006: larger sample collections

User requested larger sample collections after the v005 review. The sample
board instance is now 120% scale and the complete rack is 110%, with a 450 mm
podium. Board location is X -121 / Y +30 mm; rack location is X +104 / Y +35 mm.
The hero and camera animation are unchanged. The reusable source libraries
keep their original dimensions; these scales are directly editable on
`SHOT05_CollectionSampleBoard` and `SHOT05_CollectionRack`.

Saved scene: `scenes/gel_polish_lapohka_shot5_376_528_polish_finale_v006.blend`.
The live v005 state was copied before editing to
`renders/shot5_brand_collection_v006/source_v005_snapshot.blend`.
Review stills at f400, f432, f480 and f528 passed visual inspection. Geometry
validation passed all 306 samples with zero detected assembly intersections,
shelf penetration, podium-boundary failures or missing libraries/textures.
Rack radial clearance is at least 9.89 mm; board clearance is 19.98 mm.
Report: `renders/shot5_brand_collection_v006/validation.json`.
No v006 production sequence has been rendered.
A 3840 x 2160, 512-sample f480 composition still is available at
`renders/shot5_polish_finale_v006/review_0480_4k.png`.
