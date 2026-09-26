# Detailed polish bottle for LiquiGen

Import **gel_polish_bottle_detailed.fbx** into LiquiGen. It contains the original
evaluated housing, embossed lettering, cap grooves and rings, front lens, and
lacquer surface at full detail. This export uses no convex hull, voxel remesh,
or decimation. The canonical bottle asset and existing shots are unchanged.

The housing's ambiguous neck seams are split into closed regions, and its
openings are capped. The lens and lacquer each gain a back closure. The cap
was already closed; microscopic export triangles are cleaned where needed.
All four exported objects have zero open or non-manifold edges. They retain
their material slots and UVs, so LiquiGen's import masks can select each part.

| Object | Detail |
| --- | --- |
| `Bottle_Housing_Gold` | Rounded housing and evaluated HANG PURE embossing |
| `Bottle_Cap_Detailed` | Actual modeled cap, including grooves and ring details |
| `Bottle_FrontLens_Glass` | Original lens shape, with a closed back |
| `Bottle_Lacquer_Pearl` | Original polish surface, with a closed back |

The FBX uses metres, Y-up / -Z-forward, and Housing-local coordinates. The
bottle is approximately 101 mm tall. This is a static assembled bottle export.

## Preserve the approved rendered appearance

**gel_polish_bottle_detailed.blend** is the companion for final rendering.
`Bottle_Original_Render_Surfaces` contains the original evaluated visual
surfaces and original gold, glass and procedural pearl shaders.
`LiquiGen_Detailed_Closed_Geometry` contains the matching FBX meshes, hidden
from beauty renders. Both sets share coordinates; move them together when
animating and exporting the collider motion.

Closing a glass surface changes its refraction and can darken the polish.
Keeping the original optical surfaces for rendering preserves the approved
look while the closed geometry drives the simulation. Bring the LiquiGen
fluid cache back into Blender and render it with the original visual bottle.

FBX does not preserve the complete Blender shader graph. The FBX alone does
not reproduce the exact procedural pearl/glass finish inside LiquiGen.
LiquiGen provides its own Appearance controls; use import masks for gold,
glass and polish if previewing materials there. See the
[Blender shader interchange notes](https://docs.blender.org/manual/en/4.1/addons/import_export/node_shaders_info.html)
and [LiquiGen Appearance and Import documentation](https://docs.jangafx.com/liquigen/pages/references/node_list.html).

## Import checks

Use an Import node and select the FBX, then connect Geometry to Collider Shapes.
Verify that the import lists all four named objects. Smaller import voxels
retain finer modeled details; use the Models/SDF diagnostic view to inspect
the result. The export retains the detail, but voxel spacing limits what the
simulation represents. See the
[JangaFX import guide](https://docs.jangafx.com/liquigen/pages/references/How-To%20Guides/import_animation.html).

`validation.json` records source hashes, closure work, FBX reimport geometry
and UV checks, and render provenance. LiquiGen host import and voxelization
have not yet been verified. `preview_front.png` and `preview_back.png` are
Blender renders of the original optical surfaces in the companion file.

Reproduction scripts, in order: `export_detailed_polish_fbx.py`,
`package_detailed_polish_render.py`, `finish_detailed_polish_fbx.py` under the
project's `scripts/` directory. Use a new output version for a rebuild.
