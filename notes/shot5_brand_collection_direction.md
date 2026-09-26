# Shot 5 — brand collection staging

Design audit, 2026-09-25. Based on the three product photographs supplied in the conversation; no external asset download is needed for this direction.

## What defines the references

The presentation is a coordinated colour collection rather than a manicure workstation. Repetition, ordered shade families, and paired finish samples carry the identity. Gold bottle rims and caps repeat across a transparent stepped rack. The rack has thin clear side panels, low retaining rails, visible shelf edges, and small silver fasteners. It does not look like a thick glass block.

The first reference uses a landscape warm-white sample board, approximately 1.30:1, with a softly rounded outer backing, a four-lobed inner panel, and a pearl border. It displays 36 shades, numbered 211–246, with two nail samples per shade. The top block contains 211–219, the left block 220–228, the right block 229–237, and the bottom block 238–246. Each nine-shade block has two aligned rows. The upper examples emphasize a curved magnetic highlight; the corresponding lower examples spread the shimmer into a broader luminous area. The central label occupies the empty intersection of the four groups.

The second and third photographs show a much larger store display. Its full 24-bottle density would compete with the animated hero in this short finale. A six-bottle, two-tier adaptation retains the same display vocabulary and makes each colour legible.

## Scene scale and proposed composition

The existing evaluated hero is 45.884 mm wide, 32.845 mm deep, and 101.072 mm tall. The current podium is 320 mm in diameter and 50 mm high. These dimensions are recorded in `renders/shot5_polish_finale_v002/build_report.json` and the Shot 5 reference analysis.

Preserve the full-sized hero and supporting bottle geometry. Use six collection bottles in a three-column, two-tier rack; no miniature duplicates. Retain a clear foreground area for the hero's descent and bounce. A 410 mm podium allows the two displays to occupy the left and right rear of the stage without crowding the central product.

| Assembly | Suggested dimensions / placement | Composition role |
| --- | --- | --- |
| Acrylic rack | 164 mm wide × 90 mm deep; 42 mm tier rise; about 146 mm assembly height | Right rear, centre around X +103 mm / Y +30 mm, yaw −8°. Six orderly full-sized colour variants. |
| Pearl sample board | Approximately 140 × 108 mm landscape face, raised on a restrained stand so the assembly reaches about 148 mm | Left rear, centre around X −110 mm / Y +30 mm, yaw +10°. Full paired sample collection, front aimed toward camera. |
| Hero bottle | Original size and controls; foreground centre | Around Y −52 mm rather than −45 mm if rack lip clearance requires it. Unobstructed core and recognizable cap silhouette. |
| Podium | 410 mm diameter × existing 50 mm height | Supports both displays and the landing area; retain the satin ivory surface. |

The planned 140 × 148 mm board assembly should not become a portrait sample face: use stand height to balance it against the rack while keeping the landscape board proportions. The full 72 tips may be physically small but still read as a deliberate collection. If a lower sample count is needed, reduce complete paired groups instead of distributing unrelated individual tips.

With the planned rack placement, a conservative rotated corner reaches roughly 201 mm from the podium centre, leaving only about 4 mm to a 205 mm radius. Measure evaluated geometry before finalizing; moving the rack a few millimetres inward can increase support margin. At hero Y −45 mm, its rear edge is around Y −28.6 mm while the rack front is near Y −26 mm. That is only about 2.6 mm separation before rail thickness and reactions. Hero Y −52 mm gives more room. Check the exact shapes throughout the landing, rather than relying on static bounding boxes alone.

## Camera and visual hierarchy

Keep f376's approved close, slightly low-angle hero shot. The new collection should emerge during the existing camera pullback and stage reveal. Reframe only the later reveal and hold as needed. A final camera distance around 730 mm at 62 mm focal length gives an approximate 424 mm horizontal field, suitable for the enlarged stage. Retain comfortable top clearance for both displays and preserve the hero's clear silhouette against the gap between them.

The rear rack will naturally be taller than the standalone hero because it has a raised second tier. Use depth and separation to keep the foreground bottle dominant: each supporting bottle remains the same real-world size but projects smaller. Avoid tangent overlaps where a rear cap appears to grow out of the hero body or neck. The board's overall colour pattern should support the hero, while its fine typography can become a detail visible in 4K.

## Surface, light, and motion treatment

Retain the warm directional light and continuous vertical background shadow structure already approved. Keep the board backing neutral ivory so the shade differences remain credible. Use clear acrylic with restrained roughness, beveled cut edges, and thin practical supports. Slightly off-white pearls provide a small repeating highlight without becoming oversized jewelry. Reuse the approved fine-shimmer lacquer material at a consistent physical pigment scale across bottles and tips.

The three-beat hero landing still leads the animation. Both display roots inherit the podium response. The heavier rack should recover quickly; individual bottles can show tiny delayed rocking around their feet, while the board can show a softer delayed return. Mounted samples and pearls remain attached. Avoid a large simultaneous hop that makes the organized collection feel unsecured. Retain direct editable animation controls.

The tray, brush cup, loose tool, and freestanding fan are superseded for this version. Keep prior scene files and source assets intact for revision history, but remove those assemblies from the new shot collection. No additional liquid effect is needed in this collection presentation.

## Review criteria

- f376 retains the existing close-up crop, upward view, and product emphasis.
- The reveal presents a recognizable paired sample board and clear stepped bottle rack.
- The hero has a clean silhouette and its core is not hidden by rails or other bottles.
- All physical supports remain inside the podium throughout the reaction.
- Rack bottles remain seated and board samples remain attached during settling.
- Warm object shadows maintain the existing direction and strength without a horizontal backdrop cutoff.
- Supporting variants reuse the sharp fine-shimmer material and the same bottle geometry.
- Review stills and a motion preview are checked before a new production sequence.

## v005 build status

The separate v005 scene and both linked display libraries have been created.
The implemented rack uses six full-size bottles in two tiers and three
columns; its complete evaluated bounds are approximately 169.680 × 96.335 ×
145.272 mm. The board has all 72 modeled tips, 36 paired shades numbered
211–246 and 95 pearls. Its landscape face is nominally 140 × 108 mm, raised
on a support to about 148 mm total height.

The rack root is at X +98 / Y +29 mm with −8° yaw; the board root is at
X −107 / Y +23 mm with +10° yaw, on the 410 mm podium. The hero's vertical
motion and low-angle opening are retained. The hero shifts forward after
the opening, and only the later camera reveal and held composition widen.
The earlier tool-and-community-prop arrangement is absent from v005 and
remains available in the preserved v004 scene.

Geometry validation passed 306 samples, including quarter-frame impact checks.
There are no detected intersections, shelf penetrations, off-podium parts, or
missing libraries/textures. The f376 camera and hero transforms match v004.
1920 ? 1080 composition stills at f376, f400, f432, f460, f480 and f528 have
been visually reviewed. See `renders/shot5_polish_finale_v005/` and
`renders/shot5_brand_collection_v005/validation.json`. No new video or
production sequence has been rendered for this revision.

## v006: enlarged collections

The sample board and all mounted swatches are enlarged by 20%; the complete
acrylic rack and its six bottles are enlarged by 10%. These are scene instance
scales, so the reusable asset libraries keep their original dimensions. The
camera and hero animation are unchanged from v005, making the collections
larger on screen. The podium is widened to 450 mm to support their footprints.

`SHOT05_CollectionSampleBoard` uses scale 1.20 and X -121 / Y +30 mm;
`SHOT05_CollectionRack` uses scale 1.10 and X +104 / Y +35 mm.
Their existing delayed impact responses remain editable on the same controls.

Review stills at f400, f432, f480 and f528 passed visual inspection. Geometry
validation passed all 306 samples with no intersections or support failures.
The nearest rack edge remains 9.89 mm inside the podium; the sample board
has 19.98 mm radial margin. See
`renders/shot5_brand_collection_v006/validation.json`.
This is a composition revision; no v006 production sequence has been rendered.
The final 3840 x 2160, 512-sample composition still is
`renders/shot5_polish_finale_v006/review_0480_4k.png`.
