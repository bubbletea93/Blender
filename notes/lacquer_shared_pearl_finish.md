# Shared pearlescent lacquer

The shared finish lives in `assets/products/gel_polish_bottle.blend`, node group
`Lacquer_RenderGlitter_SHARED`, version `2026-09-15.2`. The `Glitter_UVFix`
groups in the product and all six current scene files use this core through
their `Shared render glitter finish` node. Reload linked libraries or reopen
a scene after editing the product asset.

The finish adds dense, fine pearl facets and occasional larger glints over the
existing cat-eye shader. Facets stay attached to the UVs and respond to changing
view and light directions. Grazing angles increase silver luster and coverage.
The separate glossy front lens, local shade colors, and animated cat-eye inputs
remain in place. There is no emission or animated noise seed.

## Artist controls

Edit these nodes inside the shared core in the product asset:

| Node | Setting | Current value |
| --- | --- | --- |
| Fine pearl facet density | Voronoi Scale | 220 per UV unit |
| Shimmer coverage | Multiply Add offset / multiplier | 0.42 / 1.2 |
| Dense pearlescent shimmer | Metallic / Roughness | 0.88 / 0.23 |
| Per-facet luster | Output range | 0.22 to 1.0 |
| Silver luster at grazing angles | Multiply Add offset / multiplier | 0.10 / 0.85 |
| Coarse flake cells | Voronoi Scale | 90 per UV unit |
| Occasional larger glints | Greater Than threshold | 0.94 |

Larger density values make smaller facets. The previous very fine base texture
was largely averaged away by final image filtering and denoising. The new layer
uses a scale that remains visible at the product's size in the 1080p shot.

## Verification and recovery

Review outputs are in `renders/lacquer_pearl_review/`:

- `final_glitter_0199.png` and `final_glitter_0231.png`: renders from the saved
  Shot 3 file and linked product asset, 1920 x 1080, Cycles 128 samples,
  denoising enabled, existing Blackman-Harris filter and 1.5 filter width.
- `pearl_comparison.png`: before and after crops at one image pixel per source
  pixel; no sharpening, upscaling, or added sparkle.
- `lacquer_pearl_shimmer_219_247.mp4`: short 1080p, 30 fps verification segment.
- Shot 2 frame 150 and Shot 4 frame 310 verify the same core in other lighting
  and shade contexts.
- `core_validation.json` records all six scene consumers and the source owner.
- `render_validation.json` records final render settings.

The source mesh coordinates and material RGB values were checked before and
after the core update. A remaining local legacy wrapper in Shot 3 was connected
to the same core. Backups are kept in the review directory, including
`gel_polish_bottle_before_pearl.blend` and the original current Shot 3 session.
The raw source backup should be restored to its canonical asset path before use
so its existing relative dependencies resolve correctly.

`scripts/lacquer_glitter_shared.py` defines the core. The product file also
contains its source in `LACQUER_GLITTER_SHARED.PY` and artist notes in
`LACQUER_SHARED_GLITTER_NOTES`. `publish_lacquer_pearl_core.py` updates the
existing shared group in place and checks consumer links; it does not rebuild
the shots or their animation.
