# Shot 5: Hang Pure collection presentation

The approved scene is `scenes/gel_polish_lapohka_shot5_376_528.blend`. It presents the complete 36-shade collection on a clear acrylic rack beside the branded sample board. Both displays rest directly on a seamless mauve/lavender studio floor. The main teal bottle lands in the rack and remains there through the final frame.

The production sequence and both delivery videos are complete: 153 frames, f376-528, at 3840 x 2160 and 30 fps. See the [production and reference guide](shot5_polish_finale_reference_analysis.md) for deliverables, animation controls and render settings.

## Brand references and composition

The user-supplied photographs establish a coordinated collection: repeated gold bottle rims and caps, ordered shade families, paired nail finishes, a thin transparent stepped rack, and a pearl-bordered sample board. The final shot follows this presentation. The previous tray, glass, brush tools, freestanding fan and raised platform have been retired.

The board has a rounded landscape backing, a four-lobed inner sample panel, and 95 pearls. It holds 36 shades numbered 211-246, each represented by two mounted nail tips:

| Board group | Shade IDs | Arrangement |
| --- | --- | --- |
| Top | 211-219 | Nine paired shades in two aligned rows |
| Left | 220-228 | Nine paired shades in two aligned rows |
| Right | 229-237 | Nine paired shades in two aligned rows |
| Bottom | 238-246 | Nine paired shades in two aligned rows |

The Hang Pure gold monogram, silver star and black wordmark occupy the center, with the collection name below. Their contours are modeled from the supplied logo reference. The outer backing uses pearl-white leather with modeled perimeter stitching; the inner printed panel stays smooth.

The final camera frames both complete displays with substantially less unused space. The collection occupies approximately 86% of image width in the held view. Soft directional illumination preserves contact shadows and readable bottle highlights on the continuous floor and curved background.

## Display dimensions and product layout

The user enlarged the source board and removed its standing foot and rear support. Those edits are preserved in `assets/props/brand_collection_sample_board.blend`. The scene uses a 1.20 instance scale, approximately 347 x 268 mm before tilt, a 12-degree backward lean and 6-degree yaw. Its forward placement is preserved; no stand is reintroduced.

The six-tier rack has six full-size bottles per row. Its complete bounds are approximately 331.7 x 296.8 x 317.3 mm, with 54 mm column spacing, 49 mm row spacing and 42 mm tier rises. The approved bottle is approximately 45.884 x 32.845 x 101.072 mm.

The scene contains 35 supporting bottle instances plus the animated hero, totaling 36 bottles and 36 distinct shades. The hero is PetrolTeal, shade 225, in front-row slot R1/C3. Peach 213 occupies R3/C3. The reusable rack library retains its complete static 36-bottle arrangement; the shot performs this substitution locally.

Rack product variants share the fully evaluated housing and lacquer meshes. This preserves approved geometry detail while avoiding 36 repeated live subdivision/displacement evaluations and unnecessary deformation-motion buffers. Rigid transform motion blur remains enabled.

## Board finish and rebuild sources

The paired nail samples have focused magnetic cat-eye bands and broader velvet bands. Their view-responsive highlight is distinct from the fine UV-locked pigment texture. Pigment spacing is approximately 86 micrometers in the asset; coverage is strongest inside the band and quieter outside it. There is no coarse-glitter layer or emission. Rack bottle materials retain their approved finish.

The leather border has 499 modeled thread segments at approximately 1.95 mm pitch, with small punctures at the thread ends. Rounded leather grain and microscopic pores give the outer cover its texture. The user-sized bounds, original sample transforms, pearl placement and smooth inner panel are preserved.

| File | Role |
| --- | --- |
| `assets/props/brand_collection_sample_board_stitched.blend` | Current linked board; collection `Prop_BrandCollection_SampleBoard_Stitched` |
| `assets/props/brand_collection_sample_board.blend` | Preserved user-sized, stand-free authoring source |
| `assets/props/brand_collection_bottle_rack_36.blend` | Current linked rack and full collection |
| `scripts/brand_collection_palette.py` | Shared 36-shade data in ID order 211-246 |
| `scripts/refine_shot5_sample_board.py` | Adds logo and magnetic materials to the source board |
| `scripts/detail_shot5_sample_board.py` | Runs refinement in memory, then creates stitched leather and fine shimmer |
| `scripts/build_brand_collection_rack36.py` | Rebuilds the rack from the current shot's approved product collection and shared palette |

The stitched-board builder no longer requires a saved cat-eye intermediate. It opens the preserved source, prepares the logo/materials in memory, and writes the final stitched asset. Run asset builders only when intentionally rebuilding; they replace their output assets. The obsolete original board generator is removed because it would recreate the old dimensions and stand.

## Motion and quality checks

The opening is a close, slightly low-angle view of the main bottle above the rack. It descends over its slot, slows just above the shelf around f422-425, contacts at f432, rebounds at f436 and settles by f451. The complete collection holds through f528. The floor and display parents stay grounded; small individual bottle reactions supply delayed follow-through.

The approved geometry audit passed 129 sampled poses, including landing intervals, with no detected inter-assembly intersections, floor/shelf penetrations or final-display cropping. Nominal clearances are 0.12 mm beneath the board, 0.20 mm beneath the rack and 0.25 mm beneath the seated hero's foot. Cleanup preserved the 102 active scene objects and their geometry.

Use `scripts/validate_shot5_gradient_collection.py` for repeatable geometry, layout, dependencies and framing checks. Use `scripts/render_shot5_board_detail.py` for a board close-up under the actual studio lights. Any material or staging change should be checked at the opening, landing, rebound and held collection view before rendering again.

## Repository cleanup

The canonical scene replaces numbered Shot 5 working files. Obsolete migration scripts, the smaller six-bottle rack, the intermediate cat-eye board and unused prop derivatives have been removed from the working tree. Committed historical revisions remain recoverable through Git; old iteration paths are not current runnable dependencies. Original reference media and community source downloads with provenance are preserved. Generated renders and videos remain outside Git.
