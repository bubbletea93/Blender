# Shot 5 community assets

Status update, 2026-09-25: the user's new brand-collection direction supersedes
this dressing in Shot 5 v005. The tray, glass holder, tools, loose tips and fan
are removed only from the new scene. The completed v004 scene, review and
all source and derivative assets remain preserved. The active composition
uses a pearl sample board and six-bottle acrylic rack; see
`notes/shot5_brand_collection_direction.md`.

Reviewed and approved by the user on 2026-09-24. Both original models have
been acquired and preserved with source, license and SHA-256 records. Their
adaptations are integrated into the separate Shot 5 v004 scene. Full scene
geometry validation, rendered material checks and still-frame reference
comparisons have passed. The complete 153-frame motion preview passed its
decode check and visual impact/recovery review.

## First choice: a small organic ceramic tray

[Organic Ceramic Tray on BlenderKit](https://www.blenderkit.com/get-blenderkit/ec82565c-f623-4d81-a50a-60fbaf24a075/)
is listed as free. The gallery identifies Santiago Adrio and a Royalty Free
license. BlenderKit's [licensing FAQ](https://www.blenderkit.com/docs/licenses/licensing-faq/)
permits commercial rendered images and animation; it does not permit selling
downloaded assets as a new model collection.

The downloaded model is a deep leaf-shaped bowl. It is uniformly scaled to
80 mm long, approximately 44.9 mm wide and 22.7 mm high, retaining its source
proportions. A warm-ivory color mix retains the source texture variation,
roughness and normal detail. The bowl sits in the left foreground, with the
teal loose nail tip leaning against its inner slope so it remains visible
over the rim. The magnetic wand sits alongside the bowl on the podium; the
85 mm wand does not fit naturally inside its smaller interior floor.

## Faceted glass brush holder

[Glass Cup by cczero on BlendSwap](https://blendswap.com/blend/30973)
is a free native Blender/Cycles model under CC0. The listing describes an
eight-sided glass with surface smudges and a branded bump map.

The source is adapted to a 65 mm tall, 51.976 mm diameter manicure-brush
holder. The logo bump branch is removed from the derivative material; the
source glass and separate smudge-roughness texture are preserved in the
original file. The derivative uses roughness `0.008 + source × 0.035` for
clean glass with restrained surface variation, retaining the packed map and
IOR 1.45. Its rendered finish has been checked. This replaces the earlier
rose-colored fluted cup and gold foot.
The existing holder root, three brush-flex controls, nine brush meshes,
their materials and their animation remain intact.

## Composition and motion

Both assets complement the existing five-color nail-swatch fan, magnetic
wand and polish bottle. Generic cosmetics and paintbrush props found in the
search either weakened the manicure theme or had paid/restrictive listings.
The v003 low-angle opening and three-beat landing are retained. The bowl
inherits the stage response and adds a delayed 0.25 mm first hop. The teal
tip is parented to the bowl with its own local response; the wand remains
beside it with its existing delayed movement. The glass vessel inherits the
existing holder motion, and the brushes keep their independent sway.

## Acquired originals and reusable derivatives

The v003 scene is preserved. The working scene is
`scenes/gel_polish_lapohka_shot5_376_528_polish_finale_v004.blend`.

| Asset | Preserved original | Reusable derivative |
| --- | --- | --- |
| Organic Ceramic Tray | `assets/props/community/organic_ceramic_tray/source/organic-ceramic-tray_1K_f62ddb9e-d951-4b54-ad9a-5e9c01cb6cd5.blend` | `assets/props/community/manicure_community_props.blend`, collection `Prop_Community_OrganicCeramicTray` |
| Glass Cup | `assets/props/community/glass_cup_cczero/source/Glass Cup.blend` | `assets/props/community/glass_cup_cczero/brush_holder.blend`, collection `Prop_CommunityGlassBrushHolder` |

The official BlenderKit add-on supplied the free tray and packed 1K textures.
The user supplied `C:\Users\danht\Downloads\Glass Cup.blend`, which was copied
into the project without modifying the original. Each asset directory has
its own `provenance.json` with the source URL, author, license, acquisition
method and SHA-256. Download and sign-in handoffs are resolved; no further
manual acquisition steps are needed.

## Validation status

The glass replacement passed its specific brush/cup geometry check at 306
samples, including quarter-frame sampling during impact and recovery:
zero intersections, at least 2.494 mm brush-to-cup clearance, and at least
47.308 mm radial margin to the podium edge. The report is
`renders/shot5_community_v004/glass_cup_integration.json`.

Full scene geometry validation also passed 306 samples: all 153 integer
frames plus quarter frames through impact and recovery. It found zero
between-assembly or internal intersections, zero containment warnings, and
all props within the podium. The closest podium-edge margin is 5.901 mm at
the tray. This includes checking the animated teal tip against the bowl.
Report: `renders/shot5_community_v004/scene_validation.json`.

Rendered 1920 × 1080 stills and reference comparisons at f376, f400, f460 and
f528 passed camera-framing and material review. The complete 153-frame motion
preview passed its decode check; inspection at f432 and f440 confirmed correct
podium placement and delayed prop reactions. It is a 960 × 540, 64-sample,
30 fps review, not a completed 4K production sequence.

- Video: `renders/lapohka/shot5_f376-528/lapohka_s5_f376-528_polish_finale_v004.mp4`
- Reference comparison: `renders/shot5_polish_finale_v004/reference_comparison.jpg`
- Motion contact sheet: `renders/shot5_polish_finale_v004/motion_contact_sheet.jpg`

## Liquid direction

The user permits LiquiGen if an effect improves the shot. Keep this revision
dry: the landing, stage reaction, swatches and brushes already supply motion,
and another splash would repeat Shot 3. A future optional effect would be a
single viscous teal lacquer bead relaxing in a dedicated palette well; it
would require a suitable palette prop and a separate simulation test.
No new liquid simulation has been started.
