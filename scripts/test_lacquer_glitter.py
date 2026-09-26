"""Review shared glitter at production resolution before editing the source asset."""
import bpy,sys,os
from pathlib import Path
ROOT=Path('C:/Users/danht/Documents/GitHub/Blender');OUT=ROOT/os.environ.get('LACQUER_REVIEW_DIR','renders/lacquer_glitter_review')
sys.path.insert(0,str(ROOT/'scripts'))
from lacquer_glitter_shared import build_group,attach_finish
s=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
s.cycles.device='GPU';s.cycles.samples=128;s.render.resolution_percentage=100
# Keep final denoising and pixel filtering enabled for the comparison.
for f in [199,231]:
    s.frame_set(f);path=OUT/f'before_{f:04d}.png'
    if not path.exists():s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
shared=build_group()
copies={}
for mat in bpy.data.materials:
    if mat.library or not mat.node_tree or 'lacquer' not in mat.name.lower():continue
    for node in mat.node_tree.nodes:
        if node.type!='GROUP' or not node.node_tree.name.startswith('Glitter_UVFix'):continue
        original=node.node_tree
        if original not in copies:
            copies[original]=original.copy();attach_finish(copies[original],shared)
        node.node_tree=copies[original]
s.frame_set(231)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'shot3_glitter_test.blend'))
for f in [199,231]:
    s.frame_set(f);s.render.filepath=str(OUT/f'glitter_{f:04d}.png');bpy.ops.render.render(write_still=True)
    print('GLITTER_REVIEW_FRAME',f,flush=True)
print('GLITTER_REVIEW_COMPLETE',flush=True)
