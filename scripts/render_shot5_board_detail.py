"""Render the current linked sample board under the shot lighting; never save.

Blender --background SHOT.blend --python scripts/render_shot5_board_detail.py
"""
import bpy, re
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parents[1]
match=re.search(r'_v(\d+)\.blend$',bpy.data.filepath)
out=root/(f'renders/shot5_polish_finale_v{match.group(1)}' if match else 'renders/shot5_polish_finale_review')
out.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene;s.frame_set(480)
board=s.objects['SHOT05_CollectionSampleBoard']
cam=s.camera.copy();cam.data=s.camera.data.copy()
s.collection.objects.link(cam)
cam.animation_data_clear()
for c in list(cam.constraints):cam.constraints.remove(c)
center=board.matrix_world@Vector((0,-.004,.15124))
cam.location=center+Vector((.02,-1,.36)).normalized()*.76
cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens=62;cam.data.dof.use_dof=False
s.camera=cam
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU';s.cycles.samples=512;s.cycles.adaptive_threshold=.003
s.render.use_motion_blur=False;s.render.use_persistent_data=False
s.render.resolution_x=2560;s.render.resolution_y=2048;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='16'
s.render.filepath=str(out/'board_detail.png')
bpy.ops.render.render(write_still=True)
print('BOARD_DETAIL_READY',s.render.filepath,flush=True)
