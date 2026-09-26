"""Enlarge the two collection displays in a separate Shot5 v006 scene.

Run in the live v005 scene so any current edits are preserved. The linked asset
libraries stay at their original dimensions; scene controls expose the scaling.
"""
import bpy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'renders/shot5_brand_collection_v006'
OUT.mkdir(parents=True, exist_ok=True)
DEST = ROOT / 'scenes/gel_polish_lapohka_shot5_376_528_polish_finale_v006.blend'
assert Path(bpy.data.filepath).name.endswith('polish_finale_v005.blend')
s = bpy.context.scene
# Includes any live edits that have not yet been saved to v005.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'source_v005_snapshot.blend'), copy=True)
s.frame_set(480)
board = s.objects['SHOT05_CollectionSampleBoard']
rack = s.objects['SHOT05_CollectionRack']
podium = s.objects['SHOT05_CeramicPodium']
board.scale = (1.20,) * 3
board.location.x = -.121
board.location.y = .030
rack.scale = (1.10,) * 3
rack.location.x = .104
rack.location.y = .035
podium.scale.x = podium.scale.y = .225 / .160
podium['diameter_mm'] = 450
board['presentation_scale'] = '120% of reusable sample board; mounted samples and support enlarge together.'
rack['presentation_scale'] = '110% of reusable rack and supporting bottles; hero dimensions unchanged.'
s['collection_size_revision'] = 'v006: sample board +20%, bottle collection +10%, podium 450 mm. Camera framing unchanged.'
s.render.use_persistent_data = False
s.render.filepath = '//../renders/shot5_polish_finale_v006/production_4k/frame_'
txt = bpy.data.texts.get('SHOT05_README')
if txt:
    txt.write('\nV006 / larger collection displays\nSample board 120%, complete rack 110%. Linked source assets retain original dimensions.\n450 mm podium supports the enlarged footprints. Repositioned display controls retain their landing responses.\nCamera and hero animation are unchanged from v005; display scaling is editable on CollectionSampleBoard and CollectionRack.\n')
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
(OUT / 'scene_build.json').write_text(json.dumps({
    'scene': str(DEST),
    'source_snapshot': str(OUT / 'source_v005_snapshot.blend'),
    'board_scale': list(board.scale), 'rack_scale': list(rack.scale),
    'board_location': list(board.location), 'rack_location': list(rack.location),
    'podium_diameter_mm': 450,
    'camera_changed': False, 'hero_animation_changed': False,
}, indent=2), encoding='utf-8')
print('LARGER_COLLECTION_READY', str(DEST), flush=True)
