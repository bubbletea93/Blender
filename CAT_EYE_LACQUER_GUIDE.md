# Cat Eye Lacquer Guide

This guide translates the referenced glitter and anisotropy tutorials into one practical workflow for this bottle's front lacquer insert in Blender 5.1.

Defaults chosen for this guide:

- Final renderer: `Cycles`
- Primary use case: turntable-stable product motion
- Material scope: a dedicated front-face lacquer material, not the shared `Bottle_Red`
- Sparkle method: procedural microflakes, not an image texture
- Directional sheen method: anisotropy driven by `Tangent` plus a dedicated UV map

This is not a verbatim transcript of the videos. It is a project-specific build recipe synthesized from their relevant sections.

## Progress Tracker

Use this section as the working checkpoint for the actual Blender file, not just the target plan.

### Done

- `CatEye_Lacquer` was created as a dedicated material instead of continuing to edit the shared `Bottle_Red`.
- The front lacquer work was recovered from Blender autosave and saved back into [scenes/main.blend](C:/Users/danht/Documents/GitHub/Blender/scenes/main.blend).
- The base lacquer `Principled BSDF` was rebuilt away from flat pink and toward a dark auburn / copper-red body.
- A three-scale object-space microflake mask was built using `Voronoi` scales around `250`, `500`, and `1000`.
- The three flake branches are combined with chained `Math > Maximum` nodes.
- A metallic glitter lobe exists as a second `Principled BSDF`.
- The glitter lobe is driven by the flake mask through `Mix Shader` and `Bump`.
- A master `Flake Control` `ColorRamp` was added after the second `Maximum` to control glitter visibility globally.
- A first-pass warm per-flake tint branch was added:
  - `Math.001 -> Flake Tint Range -> Flake Tint -> glitter Base Color`
- Current saved tuning includes:
  - `Bump Strength`: `0.12`
  - glitter `Roughness`: `0.05`
- The area light was resized and moved for the small lacquer face:
  - shape: `RECTANGLE`
  - size: `0.035 x 0.06`
  - energy: `180`

### In Progress

- The glitter structure exists, but the camera view still reads too broad and too smooth.
- The material is at the "first readable glitter pass" stage, not the final cat-eye lacquer stage.
- The current lighting is good enough for lookdev, but not yet tuned for the final beauty result.

### Not Done Yet

- Create `cat_eye_uv` and use it for controlled anisotropic direction.
- Add a separate anisotropic sheen lobe for the cat-eye effect.
- Tune `Anisotropic`, `Anisotropic Rotation`, `Tangent`, and sheen masking until the sweep is soft and directional rather than metallic.
- Re-evaluate the lacquer through `FrontLens` as the approval view.
- Run a final turntable check for sparkle stability and highlight travel.

### Immediate Next Task

- Create `cat_eye_uv` and build the separate anisotropic sheen lobe before doing the final lens and turntable approval pass.

## 1. Target Read

The front lacquer should read as four layers working together:

- A dark copper-red lacquer body, closer to auburn and ember than flat pink.
- A dense field of fine, reflective microflakes that stay small in close-up.
- A soft pearlescent cat-eye sheen that appears more strongly at certain light angles.
- A clear top read through the existing `FrontLens`, so the finish still feels sealed under a smooth lens.

What you are chasing is not a single "glitter texture." It is a layered response:

- base color depth
- microflake breakup
- directional specular bias
- controlled lighting

## 2. Current Scene Status

Current saved checkpoint in [scenes/main.blend](C:/Users/danht/Documents/GitHub/Blender/scenes/main.blend):

- `CatEye_Lacquer` exists and is the active dedicated lacquer material for the front insert work.
- The base lacquer lobe is in place.
- The microflake mask stack is in place.
- The glitter lobe is in place.
- The master `Flake Control` ramp is in place.
- The anisotropic cat-eye sheen is not built yet.
- A dedicated `cat_eye_uv` direction setup is not built yet.
- The current camera verification still reads too smooth and too uniform, which means the directional sheen pass is now the main missing layer.

Working interpretation:

- The shader has moved past the planning stage.
- The warm per-flake variation branch now exists as a first pass.
- The next real shader milestone is the anisotropic sheen pass.

## 3. Material Architecture

Build the lacquer as four logical blocks:

| Block | Purpose | Main Nodes | Starting Intent |
|---|---|---|---|
| Base lacquer | Gives the disc its deep red/copper body | `Principled BSDF` | Non-metallic, rich, glossy, slightly coated |
| Microflake mask | Creates dense fine glitter breakup | `Texture Coordinate`, `Voronoi`, `ColorRamp`, `Math Maximum` | Small, dense, object-space sparkles |
| Microflake response | Gives flakes their reflective pop | `Bump` or `Normal Map`, second `Principled BSDF` | Warm metallic sparkle layer |
| Cat-eye sheen | Gives the broad pearlescent sweep | `Principled BSDF`, `Tangent`, `Layer Weight`, optional soft gradient | Directional, soft, angle-dependent sheen |

Suggested starting values:

### Base lacquer lobe

- `Base Color`: deep auburn / copper-red
- `Metallic`: `0.0`
- `Roughness`: `0.22` to `0.32`
- `Coat Weight`: `0.12` to `0.25`
- `Coat Roughness`: `0.03` to `0.06`
- `Emission Strength`: `0.0`

### Microflake lobe

- `Metallic`: `1.0`
- `Roughness`: `0.05` to `0.12`
- `Base Color`: warm gold / rose / ember variation
- Flake normal strength: low to medium, only enough to break reflections

### Cat-eye sheen lobe

- `Metallic`: `0.0` to `0.1`
- `Roughness`: `0.12` to `0.18`
- `Anisotropic`: `0.55` to `0.75`
- `Anisotropic Rotation`: start at `0.0`, then align by eye
- `Base Color`: lighter, pearlier version of the lacquer hue

## 4. Build Order In Blender 5.1

Follow this order. Do not jump straight to glitter color before the flake mask is stable.

Current status against this build order:

| Step | Status | Notes |
|---|---|---|
| Step 1: Duplicate the current red material | Done | `CatEye_Lacquer` exists and was recovered from autosave |
| Step 2: Reserve a UV map for directional control | Not done | `cat_eye_uv` still needs to be created |
| Step 3: Rebuild the base lacquer first | Done | Base color and base lacquer response are already in place |
| Step 4: Build the microflake field | Done | Three `Voronoi` scales plus chained `Maximum` nodes are built |
| Step 5: Turn the flake mask into reflective response | Done | `Bump`, glitter lobe, and `Flake Control` are in place |
| Step 6: Add warm per-flake color variation | Done | First-pass tint branch is in place and saved |
| Step 7: Mix in the microflake lobe | Done | Mixed through `Mix Shader` and flake mask |
| Step 8: Build the cat-eye sheen separately | Next | No anisotropic sheen lobe yet |
| Step 9: Tune the sheen to stay soft | Not done | Depends on Step 8 |
| Step 10: Evaluate through the lens | Not done | Final approval pass still pending |

### Step 1: Duplicate the current red material

1. Select the front lacquer faces on `Housing`.
2. Duplicate `Bottle_Red` and rename it to `CatEye_Lacquer`.
3. Assign `CatEye_Lacquer` only to the front insert faces.
4. Keep `Bottle_Red` untouched so you can compare before/after.

Why:

- This prevents the lacquer changes from leaking into unrelated objects or placeholder geometry.

### Step 2: Reserve a UV map for directional control

1. Add a UV map named `cat_eye_uv`.
2. In Edit Mode, unwrap only the front lacquer faces with a front-facing planar projection.
3. Keep this UV map clean and centered.
4. Use this UV map only for anisotropy direction and optional broad sheen shaping.
5. Keep the microflake field in `Object` space to reduce crawling in turntable motion.

Why:

- Sparkle density wants stable object-space placement.
- The cat-eye sheen wants a controllable direction field.

### Step 3: Rebuild the base lacquer first

Set up a clean base `Principled BSDF` before adding flakes:

- Push the base color away from pink and toward dark copper-red.
- Keep it non-metallic.
- Use moderate roughness and a small coat.
- Do not use emission to fake luminance.

If the base layer already looks flat, the glitter layer will not save it.

### Step 4: Build the microflake field

Create a procedural flake field using three stacked Voronoi layers.

Recommended node logic:

```text
Texture Coordinate (Object)
  -> Voronoi #1 (Scale ~250)
  -> Voronoi #2 (Scale ~500)
  -> Voronoi #3 (Scale ~1000)

Each Voronoi Distance
  -> ColorRamp / Map Range to isolate tiny bright flakes

Then:
  -> combine with chained Math: Maximum
  -> output a single scalar flake mask
```

Use this scalar flake mask for:

- mix factor into the flake lobe
- roughness breakup
- a flake bump/normal input
- subtle warm color variation

Rules for this step:

- Keep flakes fine and dense.
- Avoid large visible cells.
- Narrow the white range in the ramps so only a small part of the pattern becomes a bright flake.

### Step 5: Turn the flake mask into reflective response

Use the combined flake field to drive reflective breakup:

1. Feed the flake field into a low-strength `Bump` node.
2. Send that bump into the `Normal` of the microflake lobe.
3. Optionally also use a higher-contrast version of the same flake field to reduce roughness only where flakes exist.

The goal is:

- the lacquer stays smooth overall
- the flakes catch light differently from the body
- the sparkle feels embedded, not pasted on

### Step 6: Add warm per-flake color variation

Create a subtle color variation branch from the same flake field:

1. Duplicate the flake mask branch.
2. Remap its values with `Map Range`.
3. Feed it into a `ColorRamp`.
4. Use a restrained palette:
   - warm gold
   - rose gold
   - copper
   - ember orange

Do not make the glitter rainbow unless that is the product brief. The reference image reads as warm metallic sparkle, not multicolor craft glitter.

### Step 7: Mix in the microflake lobe

Use a second `Principled BSDF` for the flakes and mix it over the base lacquer using the flake mask.

Recommended logic:

```text
Base lacquer Principled
Flake Principled
Flake mask
  -> Mix Shader
```

Keep the mix restrained:

- If the glitter fully replaces the lacquer, the disc will look like loose glitter instead of lacquer with suspended particles.

### Step 8: Build the cat-eye sheen separately

Do not try to get the cat-eye effect from the glitter pattern alone. Build it as a separate directional specular lobe.

Recommended setup:

1. Add another `Principled BSDF` for the sheen.
2. Set `Anisotropic` to a moderate value.
3. Add a `Tangent` node.
4. Set the `Tangent` node to use the `cat_eye_uv` map.
5. Connect the `Tangent` output to the sheen lobe's `Tangent` input.
6. Adjust `Anisotropic Rotation` until the highlight travels in the intended direction.
7. Use `Layer Weight > Facing` through a `ColorRamp` to keep the sheen strongest at glancing angles.
8. Mix this sheen lobe over the lacquer stack gently.

Key point:

- The cat-eye band should appear because the light is being biased directionally, not because you painted a hard stripe.

Optional extra control:

- If you need more shaping, add a very soft UV-driven gradient mask on `cat_eye_uv`.
- Keep it broad and blurred. This should only guide the sheen, not replace the light-driven effect.

### Step 9: Tune the sheen to stay soft

The reference looks luminous, but not neon and not chrome.

To keep the effect soft:

- lower `Metallic` on the sheen lobe
- keep `Roughness` above mirror-like values
- keep the color lighter and warmer than the base, not pure white
- use a soft ramp on the `Facing` mask
- avoid a hard central stripe

If the band looks too sharp, the problem is usually one of these:

- anisotropy too high
- roughness too low
- masking too hard
- lighting too small and too intense

### Step 10: Evaluate through the lens

Do not approve the material with the lens hidden.

Check the finish:

- with `FrontLens` visible
- in close-up
- in glancing light
- in turntable motion

The final read has to survive the extra layer of reflection and refraction from the front lens.

## 5. Lighting And Lookdev Defaults

For a turntable-stable product look:

1. Use `Cycles`.
2. Keep the studio HDRI, but desaturate it if it colors the lacquer too heavily.
3. Add one controlled area light or spot light that sweeps a glancing angle across the front face.
4. Judge the material in motion, not only in a still frame.

Lighting intent:

- HDRI gives environmental richness.
- The controlled key light reveals the cat-eye sheen.
- The microflakes should brighten and dim naturally as the object rotates.

## 6. What To Borrow From The Videos

Use the tutorials for the parts they actually solve.

### Ryan King Art: object-space glitter structure

Use this for:

- object-space glitter mapping
- driving roughness and normal from the same flake field
- reusable color control

Do not copy literally:

- the entire scene/compositing treatment
- color palettes that are too bright or stylized for this product

### Under 2 Minutes Glitter Shader: best microflake blueprint

Use this for:

- three-scale Voronoi layering
- `Maximum` combination logic
- random per-flake color variation

This is the clearest short reference for the microflake problem.

### Eevee Glitter Tutorial: preview logic only

Use this for:

- understanding reflective dot isolation
- seeing how Voronoi plus `Map Range` can create a glitter mask
- quick Eevee-side preview ideas

Do not copy literally:

- glossy-only final shading
- Bloom as a fake source of luminance for the final Cycles look

### Anisotropy Tutorials: broad sheen control

Use these for:

- understanding why the cat-eye effect needs directional reflection bias
- learning how `Anisotropic`, `Anisotropic Rotation`, and `Tangent` work together
- understanding that strand direction and highlight bias are related, not arbitrary

Do not copy literally:

- brushed-metal assumptions
- aggressive machined-metal highlight shapes

Your sheen should feel lacquered and pearlescent, not brushed stainless steel.

## 7. Recommended Video Watch Order

Watch these sections only. They are the parts that map cleanly onto this bottle.

| Video | Timestamp(s) | Why It Matters Here |
|---|---|---|
| [Procedural Glitter Material (Ryan King Art)](https://www.youtube.com/watch?v=jnTwqVENCtA) | `1:37-4:46` | Scene and HDRI setup reference only |
| [Procedural Glitter Material (Ryan King Art)](https://www.youtube.com/watch?v=jnTwqVENCtA) | `4:46-11:54` | Main procedural glitter construction |
| [Procedural Glitter Material (Ryan King Art)](https://www.youtube.com/watch?v=jnTwqVENCtA) | `13:32-26:22` | Color control and reusable parameterization |
| [How to Make Glitter Shader in Blender in under 2 mins](https://www.youtube.com/watch?v=wSWSdW67B5Y) | `0:13` | Metallic/specular setup |
| [How to Make Glitter Shader in Blender in under 2 mins](https://www.youtube.com/watch?v=wSWSdW67B5Y) | `0:19` | Roughness target |
| [How to Make Glitter Shader in Blender in under 2 mins](https://www.youtube.com/watch?v=wSWSdW67B5Y) | `0:27` | Introduces the flake-normal idea |
| [How to Make Glitter Shader in Blender in under 2 mins](https://www.youtube.com/watch?v=wSWSdW67B5Y) | `0:41` | First Voronoi scale (`250`) |
| [How to Make Glitter Shader in Blender in under 2 mins](https://www.youtube.com/watch?v=wSWSdW67B5Y) | `0:52` | Additional Voronoi scales (`500`, `1000`) |
| [How to Make Glitter Shader in Blender in under 2 mins](https://www.youtube.com/watch?v=wSWSdW67B5Y) | `1:02` | `Vector Math > Maximum` combination idea |
| [How to Make Glitter Shader in Blender in under 2 mins](https://www.youtube.com/watch?v=wSWSdW67B5Y) | `1:20` | Normal-map strength tuning |
| [How to Make Glitter Shader in Blender in under 2 mins](https://www.youtube.com/watch?v=wSWSdW67B5Y) | `1:28` | Random per-flake color variation |
| [Glitter Material Tutorial Easy - Blender Eevee](https://www.youtube.com/watch?v=tUJ8m2WEvnE) | `~0:25` | Glossy plus Mix Shader preview setup |
| [Glitter Material Tutorial Easy - Blender Eevee](https://www.youtube.com/watch?v=tUJ8m2WEvnE) | `~0:55` | Voronoi driving reflective dots |
| [Glitter Material Tutorial Easy - Blender Eevee](https://www.youtube.com/watch?v=tUJ8m2WEvnE) | `~1:20` | `Map Range` isolation of glitter dots |
| [Glitter Material Tutorial Easy - Blender Eevee](https://www.youtube.com/watch?v=tUJ8m2WEvnE) | `~1:50` | Voronoi into `Normal Map` for randomized reflections |
| [Glitter Material Tutorial Easy - Blender Eevee](https://www.youtube.com/watch?v=tUJ8m2WEvnE) | `~2:10` | Metallic adjustment |
| [Glitter Material Tutorial Easy - Blender Eevee](https://www.youtube.com/watch?v=tUJ8m2WEvnE) | `~2:20-3:00` | `ColorRamp` plus Object Coordinates plus Mapping for color placement |
| [Glitter Material Tutorial Easy - Blender Eevee](https://www.youtube.com/watch?v=tUJ8m2WEvnE) | `~3:20` | Bloom mention; use only as Eevee context, not final Cycles guidance |
| [Introduction to Anisotropic Shading in Blender](https://www.youtube.com/watch?v=t4MTnpnahu0) | `0:00-5:40` | Concept of directional reflection bias |
| [Introduction to Anisotropic Shading in Blender](https://www.youtube.com/watch?v=t4MTnpnahu0) | `8:38-10:33` | Material setup context |
| [Introduction to Anisotropic Shading in Blender](https://www.youtube.com/watch?v=t4MTnpnahu0) | `10:33-12:56` | Grain and bump explanation |
| [Introduction to Anisotropic Shading in Blender](https://www.youtube.com/watch?v=t4MTnpnahu0) | `13:06-15:11` | Tangent and cylindrical direction workflow |
| [Introduction to Anisotropic Shading in Blender](https://www.youtube.com/watch?v=t4MTnpnahu0) | `15:11-15:35` | Rotation alignment |
| [Anisotropy in Blender 4.3](https://www.youtube.com/watch?v=7HeDHWsotkk) | `0:20-1:18` | What anisotropy is |
| [Anisotropy in Blender 4.3](https://www.youtube.com/watch?v=7HeDHWsotkk) | `1:18-2:00` | Principled BSDF specular context |
| [Anisotropy in Blender 4.3](https://www.youtube.com/watch?v=7HeDHWsotkk) | `2:00-7:05` | Strands mental model |
| [Anisotropy in Blender 4.3](https://www.youtube.com/watch?v=7HeDHWsotkk) | `7:05-8:34` | Strand direction |
| [Anisotropy in Blender 4.3](https://www.youtube.com/watch?v=7HeDHWsotkk) | `8:34-9:05` | Actual anisotropy values |
| [Anisotropy in Blender 4.3](https://www.youtube.com/watch?v=7HeDHWsotkk) | `9:05-10:14` | Anisotropy rotation |
| [Anisotropy in Blender 4.3](https://www.youtube.com/watch?v=7HeDHWsotkk) | `10:14-11:46` | `Tangent` node usage |
| [Anisotropy in Blender 4.3](https://www.youtube.com/watch?v=7HeDHWsotkk) | `11:46-15:10` | Radial vs UV direction control |
| [Anisotropy in Blender 4.3](https://www.youtube.com/watch?v=7HeDHWsotkk) | `26:07-end` | UV mode for anisotropy |

## 8. What Not To Copy Literally

Do not build the final lacquer by copying any one tutorial literally.

- Do not use a single glossy-only glitter trick as the final material.
- Do not rely on Bloom or emission to fake the luminous finish in Cycles.
- Do not map the whole sparkle pattern in UV space if it causes crawling in motion.
- Do not keep the lacquer tied to the shared `Bottle_Red` material.
- Do not turn the cat-eye band into a hard painted stripe.
- Do not make the anisotropic lobe behave like brushed metal unless that is the intentional style shift.

## 9. Troubleshooting

### Sparkles are too chunky

- Increase Voronoi scales.
- Narrow the white end of each `ColorRamp`.
- Lower bump strength.
- Reduce the mix amount of the flake lobe.

### Sparkle crawls in motion

- Keep the flake field in `Object` space.
- Avoid animated Mapping transforms on the flake field.
- Reduce overly hard contrast in the flake mask.
- Slightly raise microflake roughness if reflections are flickering too hard.

### Cat-eye band is too metallic or too sharp

- Lower sheen-lobe metallic.
- Raise sheen-lobe roughness.
- Reduce `Anisotropic`.
- Soften the `Facing` ramp.
- Use a larger, softer key light.

### Lacquer looks flat under the lens

- Increase coat slightly on the base lacquer.
- Add more warm per-flake color variation.
- Make sure the key light hits the face at a glancing angle.
- Reduce HDRI saturation if it is washing out the lacquer.

### Anisotropy rotates the wrong way

- Adjust `Anisotropic Rotation`.
- Rotate the `cat_eye_uv` map by `90` degrees.
- Remember: the visible highlight bias usually appears perpendicular to the perceived strand direction.

### Material looks good in stills but noisy in a turntable

- Reduce the brightest flake whites.
- Raise microflake roughness slightly.
- Lower bump strength a little.
- Use more Cycles samples and adaptive sampling.
- Judge the effect in motion before approving any still.

## 10. Final Checklist

Before calling the lacquer done, make sure all of these are true:

- The front lacquer uses `CatEye_Lacquer`, not the shared `Bottle_Red`.
- The lacquer reads dark copper-red, not flat pink.
- The microflakes are fine and dense, not chunky.
- The sparkle is embedded in the lacquer, not pasted on top.
- The cat-eye sheen is broad and soft, not a hard stripe.
- The sheen moves believably with light angle.
- The material still reads correctly through `FrontLens`.
- The turntable remains stable without distracting crawling or popping.

## Notes On Timestamp Accuracy

- Exact chapter ranges are used where YouTube metadata exposed them.
- Approximate timestamps are marked with `~` where the reference came from transcript/caption review rather than a chapter boundary.
