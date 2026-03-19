# Nail Polish Bottle — Fundamental Parts Breakdown & Modeling Approach

## Context
The user has a real-world gel nail polish bottle (HANC PURE "Starry Cat Eye", 18ml) and wants to model it in Blender. The goal is a clean, modular breakdown so each part can be independently modified. The scene already has several objects started (GoldHousing, RedCore, BackLens, NeckCollar, FlutedCap, BrandText, GelPolishText, GoldHousing_Cylinder). This plan is an **analysis + recommended approach** — no code will be executed until approved.

---

## Part Breakdown (from reference photos)

### 1. GoldHousing (Body / Cap Shell)
- The large gold squircle-shaped main body
- **Shape**: Rounded square (squircle) profile, taller than wide, slight taper (narrower at top, wider at bottom)
- **Key features**: Very smooth, high-polish gold surface; subtle rounding on all edges
- **Approach**: Subdivided cube with Subdivision Surface modifier + Bevel modifier on edges. A Lattice or ShapeKey handles the top-to-bottom taper.
- **Already started**: `GoldHousing` object exists

### 2. GoldHousingBase (Foot / Stand)
- The flat, pill/squircle-shaped base ring the bottle rests on
- **Shape**: Wide squircle ring that protrudes slightly outward from the bottom of the housing
- **Key features**: Flat bottom face, rounded outer edge, slightly raised from ground
- **Approach**: Loop cut from the bottom of GoldHousing, or separate object — flat cylinder/box with Bevel modifier
- **Already started**: `GoldHousingBase` referenced in git history; appears merged into GoldHousing

### 3. RedCore / Polish Disc (Front Face)
- The circular, convex glitter-filled disc visible on the front
- **Shape**: Large circle (nearly fills the front face of the housing), slightly convex dome
- **Key features**: Deep red/burgundy with sparkle/glitter — will need a special material (Subsurface + Glitter via noise/sparkle shader)
- **Approach**: Circle/disc mesh, slightly extruded with a Subdivision Surface to get the gentle dome. Separate object placed in front of GoldHousing.
- **Already started**: `RedCore` object exists at Z=2.94

### 4. BackLens
- Small gold oval/squircle window on the back side of the housing (visible in back view photo — the small oval opening at the bottom back)
- **Approach**: Simple extruded oval shape, inset into the GoldHousing back face
- **Already started**: `BackLens` exists at Z=4.44

### 5. NeckCollar (Transition Ring)
- The ribbed/ringed collar that connects the housing body to the fluted cap handle
- **Shape**: 3 stacked rings/bands — smooth torus-like bands that step down in diameter
- **Key features**: 3 distinct ridges, gold finish, acts as a visual transition piece
- **Approach**: Stack of 3 torus/ring shapes, or a single mesh with loop cuts creating the bands. Subdivision Surface for smoothness.
- **Already started**: `NeckCollar` exists at Z=10.12

### 6. FlutedCap (Handle / Applicator Housing)
- The elongated cylindrical handle extending from the neck
- **Shape**: Cylinder with 4 deep vertical flutes/grooves running its full length; capped ends (rounded on tip, open at neck end)
- **Key features**: 4 evenly spaced vertical channels/slots cut into the cylinder surface; the slots have rounded ends
- **Approach**: Cylinder with 4 boolean-cut or loop-modeled vertical slots. OR: model the 4 "fins" between the slots as separate geometry. Subdivision Surface for rounding.
- **Already started**: `FlutedCap` exists at Z=11.91; `GoldHousing_Cylinder` is the current WIP (basic cylinder, 4.5cm diameter, lattice taper)

### 7. BrandText / GelPolishText (Embossed Text)
- "HANC PURE" and "Gel Polish" text embossed/debossed on the back of the housing
- **Approach**: Blender Text objects converted to mesh, slightly extruded, Boolean-subtracted or manually merged into GoldHousing surface
- **Already started**: `BrandText` at Z=6.14, `GelPolishText` at Z=8.02

---

## Recommended Modeling Strategy

### Object Hierarchy (one object per distinct part)
```
GelPolishBottle (collection)
├── GoldHousing          ← squircle body shell
├── GoldHousingBase      ← foot ring
├── RedCore              ← front glitter disc (convex)
├── BackLens             ← back oval window
├── NeckCollar           ← 3-band transition ring
├── FlutedCap            ← grooved cylinder handle
├── BrandText            ← embossed text
└── GelPolishText        ← embossed text
```

### Modifier Stack Per Part
| Part | Modifiers |
|------|-----------|
| GoldHousing | Bevel → Subdivision Surface |
| GoldHousingBase | Bevel → Subdivision Surface |
| RedCore | Subdivision Surface |
| NeckCollar | Subdivision Surface |
| FlutedCap | Edge Split → Subdivision Surface → Lattice (taper) |
| BackLens | Subdivision Surface |

### Materials (6 materials already in scene)
1. **Gold** — Principled BSDF, Metallic=1, Roughness≈0.05, Base Color=(1.0, 0.76, 0.2)
2. **RedGlitter** — Principled BSDF base (deep red) + Noise-driven sparkle emission layer
3. **GoldText** — same as Gold but slightly rougher for matte embossed look

---

## Current State vs. What's Needed

| Part | Status | Next Action |
|------|--------|-------------|
| GoldHousing | In progress | Refine squircle taper, verify proportions |
| GoldHousingBase | Merged/done | Verify foot ring geometry |
| RedCore | Started | Add convex dome, glitter material |
| BackLens | Started | Verify shape/placement |
| NeckCollar | Started | Add 3 distinct bands |
| FlutedCap | In progress (GoldHousing_Cylinder) | Add 4 vertical flute grooves |
| BrandText | Started | Verify placement on housing |
| GelPolishText | Started | Verify placement on housing |

---

## Verification
- Use `mcp__blender__get_viewport_screenshot` after each part to visually compare against reference photos
- Use `mcp__blender__get_object_info` to verify dimensions match real bottle (~18ml bottle is roughly 14cm tall total)
- Final assembled render should match all 8 reference photo angles: front, back, bottom, side, top-down
