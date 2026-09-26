# Gel-polish bottle simulation proxy

`gel_polish_bottle_sim_proxy.fbx` is a static, simplified collision stand-in derived from the currently visible bottle body, front lens and cap in Shot 3 at frame 199.

- One connected, watertight mesh: 402 vertices, 800 triangles.
- Actual size: 32.845 mm deep x 45.884 mm wide x 101.072 mm tall.
- Bottom-center pivot, unit scale, no animation, textures or interior parts.
- Blender coordinates: Z up, front toward +X. FBX exported with Y up and -Z forward; physical unit metadata is included.
- Grooves, embossing, internal cavities and small rim details are omitted. The round body and cap silhouette are retained.

Use at original size as a collision object. Apply the intended drop animation in the simulation application. The detailed render bottle and existing liquid simulation were not replaced.

`gel_polish_bottle_sim_proxy.blend` contains the editable proxy. `preview.png` shows its shape. `validation.json` records topology, dimensions and the successful FBX re-import checks.
