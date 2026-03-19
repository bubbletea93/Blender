# Beginner Blender Tutorial (2026) — Timestamped Reference Guide

**Video:** [Beginner Blender Tutorial (2026)](https://youtu.be/z-Xl9tGqH14)
**Creator:** Blender Guru
**Blender Version:** 5.0
**Duration:** ~4h 19m

---

## Section 1: Introduction & Interface Basics (00:00:00 – 00:12:00)

| Timestamp | Concept / Tool | Context |
|-----------|---------------|---------|
| 00:01:07 | Default Cube | Starting point in the default scene |
| 00:01:20 | 3D Viewport | Main working area for 3D modeling |
| 00:01:30 | Outliner | Panel listing all scene objects (top-right) |
| 00:01:35 | Properties Panel | Right-side panel with object/scene settings |
| 00:01:40 | Timeline | Bottom panel for animation keyframes |
| 00:02:00 | Middle Mouse Button | Orbit/rotate viewport |
| 00:02:10 | Shift+MMB | Pan viewport |
| 00:02:15 | Scroll Wheel | Zoom in/out |
| 00:02:30 | Numpad 1/3/7 | Front/Right/Top orthographic views |
| 00:02:45 | Numpad 5 | Toggle perspective/orthographic |
| 00:03:00 | X key (Delete) | Delete selected objects |
| 00:03:30 | Shift+A (Add Menu) | Add new objects/meshes |
| 00:03:45 | Mesh Primitives | Cube, Sphere, Cylinder, Torus, Plane, etc. |

## Section 2: Creating the Donut Base — Torus (00:03:45 – 00:15:00)

| Timestamp | Concept / Tool | Context |
|-----------|---------------|---------|
| 00:03:50 | Torus | Mesh primitive used as donut base |
| 00:04:00 | Operator Panel (F9) | Adjust-last-operation panel for torus parameters |
| 00:04:10 | Major/Minor Segments | Ring and cross-section segment counts |
| 00:04:20 | Major/Minor Radius | Ring radius and tube radius |
| 00:05:00 | Object Mode | Default mode for whole-object transforms |
| 00:05:15 | G key (Grab/Move) | Translate selected object/vertices |
| 00:05:20 | R key (Rotate) | Rotate selection |
| 00:05:25 | S key (Scale) | Scale selection |
| 00:05:30 | Axis Constraint (X/Y/Z) | Constrain transform to an axis |
| 00:05:50 | Right-click cancel | Cancel current transformation |
| 00:06:00 | Ctrl+Z (Undo) | Undo last action |

## Section 3: Edit Mode & Shaping the Donut (00:12:00 – 00:30:00)

| Timestamp | Concept / Tool | Context |
|-----------|---------------|---------|
| 00:12:00 | Tab key | Toggle Object/Edit Mode |
| 00:12:10 | Edit Mode | Edit mesh geometry (verts, edges, faces) |
| 00:12:30 | Vertex/Edge/Face Select (1/2/3) | Selection mode toggles |
| 00:13:00 | Proportional Editing (O) | Affect nearby geometry with fall-off |
| 00:13:30 | A / Alt+A | Select All / Deselect All |
| 00:14:00 | Smooth Shading | Right-click > Shade Smooth |
| 00:14:20 | Subdivision Surface Modifier | Subdivides mesh for smoother geometry |
| 00:14:30 | Modifier Properties tab | Wrench icon in Properties panel |
| 00:14:45 | Viewport vs Render levels | Subdivision levels for preview vs final |
| 00:15:00 | Apply Modifier (Ctrl+A) | Make modifier permanent |

## Section 4: Sculpt Mode — Organic Shaping (00:30:00 – 00:45:00)

| Timestamp | Concept / Tool | Context |
|-----------|---------------|---------|
| 00:30:00 | Sculpt Mode | Organic sculpting with brushes |
| 00:30:20 | Inflate/Deflate Brush | Puff out or push in surface |
| 00:30:40 | Grab Brush | Pull/push geometry like clay |
| 00:31:00 | Brush Radius (F) | Hold F to resize brush |
| 00:31:10 | Brush Strength | Intensity of brush effect |
| 00:31:30 | Ctrl+click (subtract) | Invert brush effect |
| 00:32:00 | Symmetry (X/Y/Z) | Mirror sculpt strokes across axis |
| 00:33:00 | Dyntopo (Dynamic Topology) | Auto-add geometry where you sculpt |

## Section 5: Icing — Duplication & Solidify (00:45:00 – 01:10:00)

| Timestamp | Concept / Tool | Context |
|-----------|---------------|---------|
| 00:45:00 | Shift+D (Duplicate) | Duplicate selected geometry |
| 00:45:15 | P key (Separate) | Separate geometry into new object |
| 00:45:30 | L key (Select Linked) | Select all connected geometry |
| 00:46:00 | Solidify Modifier | Add thickness to a surface |
| 00:47:00 | E key (Extrude) | Extrude faces/edges/vertices |
| 00:47:20 | Alt+S (Shrink/Fatten) | Move vertices along normals |
| 00:48:30 | Shrinkwrap Modifier | Project mesh onto target surface |
| 00:49:00 | Normals | Face direction affecting shading |
| 00:50:00 | Ctrl+R (Loop Cut) | Add edge loops to mesh |

## Section 6: Icing Drips — Edit Mode Techniques (01:10:00 – 01:30:00)

| Timestamp | Concept / Tool | Context |
|-----------|---------------|---------|
| 01:10:00 | Alt+Click (Edge Loop Select) | Select entire edge loop |
| 01:10:30 | I key (Inset Faces) | Create inner faces from selection |
| 01:12:00 | M key (Merge Vertices) | Merge selected vertices |
| 01:13:00 | Bridge Edge Loops | Connect two edge loops with faces |
| 01:14:00 | Smooth Vertices | Relax vertex positions |
| 01:15:00 | Checker Deselect | Deselect every other element |
| 01:16:00 | H / Alt+H | Hide / Unhide geometry |

## Section 7: Materials & Shading (01:30:00 – 01:55:00)

| Timestamp | Concept / Tool | Context |
|-----------|---------------|---------|
| 01:30:00 | Material Properties | Material settings tab |
| 01:31:00 | Principled BSDF | Default PBR shader node |
| 01:31:15 | Roughness | Surface glossiness (0=mirror, 1=matte) |
| 01:31:30 | Metallic | Metal vs dielectric surface behavior |
| 01:32:00 | Subsurface Scattering (SSS) | Light scattering beneath surface |
| 01:33:00 | Material Slots | Multiple materials per object |
| 01:33:30 | Assign Material | Assign material to selected faces |
| 01:34:00 | Viewport Shading modes | Solid / Material Preview / Rendered / Wireframe |
| 01:34:30 | Z key (Shading Pie Menu) | Quick shading mode switch |

## Section 8: UV Unwrapping & Texturing (01:55:00 – 02:25:00)

| Timestamp | Concept / Tool | Context |
|-----------|---------------|---------|
| 01:55:00 | UV Unwrapping | Flatten 3D mesh to 2D for texturing |
| 01:55:30 | Seams / Mark Seam | Define UV cut lines (Ctrl+E) |
| 01:56:30 | U key (Unwrap Menu) | Access unwrap options |
| 01:57:00 | UV Editor | Panel showing 2D UV layout |
| 01:58:00 | Image Texture Node | Load image as texture in shader |
| 01:58:30 | Shader Editor | Node-based material editor |
| 01:59:00 | Ctrl+T (Texture Mapping) | Auto-add Texture Coordinate + Mapping nodes |
| 02:00:00 | PBR Textures | Albedo, normal, roughness, displacement sets |
| 02:06:00 | Normal Map Node | Interpret normal map images |
| 02:07:00 | Displacement Node | Surface displacement from texture |
| 02:07:30 | Color Space: Non-Color | Setting for data textures (not color) |
| 02:09:00 | MixRGB / Mix Node | Blend two colors/textures |
| 02:10:00 | RGB Curves Node | Color curve adjustments |
| 02:11:00 | Color Ramp Node | Map values to color gradient |
| 02:12:00 | Noise Texture Node | Procedural noise generator |

## Section 9: Sprinkles — Scatter & Geometry Nodes (02:25:00 – 02:55:00)

| Timestamp | Concept / Tool | Context |
|-----------|---------------|---------|
| 02:25:30 | Edge Split Modifier | Control sharp/smooth shading at edges |
| 02:26:00 | Scatter on Surface | Extension for distributing objects on surfaces |
| 02:27:00 | Extensions (Add-ons) | Edit > Preferences > Extensions |
| 02:28:00 | Density / Scale / Rotation Randomization | Scatter instance parameters |
| 02:30:00 | Geometry Nodes | Node-based procedural geometry system |
| 02:30:30 | Weight Paint Mode | Paint vertex weights (influence maps) |
| 02:31:00 | Vertex Group | Named vertex set with weight values |
| 02:33:00 | Align to Normal | Orient instances to surface normals |

## Section 10: Lattice & Scene Organization (02:35:00 – 02:50:00)

| Timestamp | Concept / Tool | Context |
|-----------|---------------|---------|
| 02:35:00 | Lattice Object + Modifier | Cage-based deformation |
| 02:36:00 | Lattice Resolution (U/V/W) | Control point density |
| 02:40:00 | Collections | Outliner folders for organizing objects |
| 02:40:30 | Eye / Camera icons | Viewport visibility / Render visibility |
| 02:41:00 | Ctrl+P (Parent) | Set parent-child relationships |

## Section 11: Lighting (02:55:00 – 03:15:00)

| Timestamp | Concept / Tool | Context |
|-----------|---------------|---------|
| 02:55:00 | Sun / Point / Area / Spot Lamps | Light types |
| 02:57:00 | Light Strength / Radius / Color | Light properties |
| 03:00:00 | Three-Point Lighting | Key, fill, and rim light setup |
| 03:01:00 | HDRI / Environment Texture | 360-degree environment lighting |
| 03:01:30 | World Properties | Scene background/environment settings |
| 03:03:00 | Light Probe | Eevee indirect lighting capture |

## Section 12: Camera & Composition (03:15:00 – 03:30:00)

| Timestamp | Concept / Tool | Context |
|-----------|---------------|---------|
| 03:15:15 | Numpad 0 (Camera View) | Switch to camera viewpoint |
| 03:15:30 | Lock Camera to View | Navigate viewport to move camera |
| 03:16:00 | Focal Length | Lens mm (field of view) |
| 03:16:30 | Depth of Field / F-Stop | Camera blur effect |
| 03:17:30 | Focus Object | DoF focus target |
| 03:19:00 | Composition Guides | Rule of thirds, golden ratio overlays |
| 03:20:00 | Output Resolution | Render size (e.g., 1920x1080) |

## Section 13: Rendering — Eevee & Cycles (03:30:00 – 04:10:00)

| Timestamp | Concept / Tool | Context |
|-----------|---------------|---------|
| 03:30:15 | Eevee (Rasterized) | Fast real-time render engine |
| 03:30:30 | Cycles (Path Tracing) | Physically-based ray tracing engine |
| 03:32:00 | Samples | Light samples per pixel (quality vs speed) |
| 03:32:30 | Denoiser | Post-process noise removal |
| 03:33:00 | GPU Rendering (CUDA/OptiX/HIP/Metal) | Hardware acceleration |
| 03:34:00 | F12 (Render Image) | Render current frame |
| 03:35:00 | Color Management / Contrast Looks | Display color settings |
| 03:36:00 | Film > Transparent | Transparent background rendering |
| 03:38:00 | Eevee Ray Tracing toggle | Enable RT features in Eevee |
| 03:55:00 | Light Paths (Bounces) | Max indirect light bounces |

## Section 14: Final Touches (04:00:00 – 04:19:00)

| Timestamp | Concept / Tool | Context |
|-----------|---------------|---------|
| 04:00:00 | Compositing | Post-processing node editor |
| 04:01:00 | Glare Node | Bloom/glare compositing effect |
| 04:02:30 | Auto Save | Automatic save interval |
| 04:03:00 | Save Startup File | Save current setup as default |
| 04:05:00 | Append vs Link | Import from other .blend files |
| 04:10:00 | Ctrl+F12 (Render Animation) | Render all frames |
| 04:10:30 | Output Format | PNG, JPEG, OpenEXR, FFmpeg |

---

## Keyboard Shortcuts Quick Reference

| Shortcut | Action |
|----------|--------|
| G | Grab / Move |
| R | Rotate |
| S | Scale |
| E | Extrude |
| I | Inset Faces |
| X / Delete | Delete |
| Tab | Toggle Object/Edit Mode |
| 1, 2, 3 | Vertex, Edge, Face select mode (Edit Mode) |
| A | Select All |
| Alt+A | Deselect All |
| Alt+Click | Select Edge Loop |
| Ctrl+R | Loop Cut |
| Ctrl+E | Edge Menu (Mark Seam, etc.) |
| U | Unwrap Menu |
| O | Toggle Proportional Editing |
| H | Hide Selected |
| Alt+H | Unhide All |
| L | Select Linked |
| M | Merge / Move to Collection |
| P | Separate (Edit Mode) |
| Shift+A | Add Menu |
| Shift+D | Duplicate |
| Ctrl+P | Parent |
| Ctrl+Z | Undo |
| Ctrl+S | Save |
| Ctrl+T | Add Texture Mapping Nodes (Shader Editor) |
| Alt+S | Shrink/Fatten along normals |
| F | Brush Radius (Sculpt Mode) |
| F9 | Adjust Last Operation |
| F12 | Render Image |
| Ctrl+F12 | Render Animation |
| Z | Shading Pie Menu |
| Numpad 0 | Camera View |
| Numpad 1/3/7 | Front/Right/Top View |
| Numpad 5 | Toggle Perspective/Orthographic |
| MMB | Orbit Viewport |
| Shift+MMB | Pan Viewport |
| Scroll Wheel | Zoom / Loop Cut count |

## Modifiers Referenced

| Modifier | Purpose |
|----------|---------|
| Subdivision Surface | Smooth mesh by subdividing |
| Solidify | Add thickness to a surface |
| Shrinkwrap | Project mesh onto target surface |
| Lattice | Deform mesh via lattice cage |
| Edge Split | Control smooth/sharp shading by splitting edges |
| Scatter on Surface | Distribute object instances across a surface (extension) |

## Shader Nodes Referenced

| Node | Purpose |
|------|---------|
| Principled BSDF | Main PBR shader |
| Image Texture | Load image file as texture input |
| Normal Map | Interpret normal map images |
| Displacement | Surface displacement from texture |
| Color Ramp | Map values to color gradient |
| RGB Curves | Adjust color/value curves |
| Hue Saturation Value | Shift hue, saturation, brightness |
| MixRGB / Mix | Blend two colors/textures |
| Noise Texture | Procedural noise pattern |
| Object Info (Random output) | Per-instance random value |
| Texture Coordinate | Provide UV/Object/Generated coordinates |
| Mapping | Transform texture coordinates |
| Environment Texture | Load HDRI for world lighting |
| Glare (Compositing) | Bloom/glare post-effect |

---

> **Note:** Timestamps are approximate, derived from auto-generated captions. They indicate the first significant mention of each concept.
