"""Pair the closed FBX with unchanged evaluated render surfaces and shaders.

Closing a refractive surface changes the optical path. Final Blender renders
therefore use the original visual surfaces, aligned with the detailed collider.
"""
import bpy
import bmesh
import hashlib
import json
import sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from export_detailed_polish_fbx import NAMES, coords, setup_review, render_views
OUT=ROOT/'assets/products/exports/gel_polish_bottle_detailed'
REVIEW=ROOT/'renders/detailed_fbx_review'
ASSET=ROOT/'assets/products/gel_polish_bottle.blend'
source_hash=hashlib.sha256(ASSET.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
frame=bpy.context.scene.frame_current
inverse=bpy.data.objects['Housing'].matrix_world.inverted()
visuals=[]
for source_name,export_name in NAMES.items():
    source=bpy.data.objects[source_name]
    dg=bpy.context.evaluated_depsgraph_get()
    mesh=bpy.data.meshes.new_from_object(source.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
    mesh.transform(inverse@source.matrix_world)
    visual=bpy.data.objects.new('Render_'+export_name,mesh)
    visual['source_object']=source_name
    visual['purpose']='Original evaluated render surface, with original shaders and optical behavior.'
    visuals.append(visual)
names=[o.name for o in visuals]
library=REVIEW/'original_visual_surfaces.blend'
bpy.data.libraries.write(str(library),set(visuals),path_remap='ABSOLUTE',fake_user=True,compress=True)

# The already verified FBX geometry stays present, hidden from final rendering.
bpy.ops.wm.open_mainfile(filepath=str(OUT/'gel_polish_bottle_detailed.blend'))
scene=bpy.context.scene
colliders=[o for o in scene.objects if o.type=='MESH']
collision_collection=bpy.data.collections.new('LiquiGen_Detailed_Closed_Geometry')
scene.collection.children.link(collision_collection)
for ob in colliders:
    for collection in list(ob.users_collection):collection.objects.unlink(ob)
    collision_collection.objects.link(ob)
    ob.hide_render=True
    ob.hide_set(True)
    ob.display_type='WIRE'
    ob['purpose']='Closed detailed FBX geometry for LiquiGen; hidden from Blender beauty render.'
with bpy.data.libraries.load(str(library),link=False) as (available,loaded):
    loaded.objects=names
visuals=loaded.objects
render_collection=bpy.data.collections.new('Bottle_Original_Render_Surfaces')
scene.collection.children.link(render_collection)
for ob in visuals:render_collection.objects.link(ob)
scene.frame_set(frame)
points=[v.co for o in visuals for v in o.data.vertices]
center=Vector([(min(p[i] for p in points)+max(p[i] for p in points))*.5 for i in range(3)])
render_views(scene,center,'final_detailed_package')
scene.camera.location=center+Vector((.24,-.045,.035))
scene.camera.rotation_euler=(center-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.name='Detailed_Bottle_Render_And_LiquiGen'
note=bpy.data.texts.new('START_HERE')
note.write('Use gel_polish_bottle_detailed.fbx in LiquiGen. All modeled detail is retained.\n'
           'Bottle_Original_Render_Surfaces preserves the original Blender materials and lens behavior.\n'
           'LiquiGen_Detailed_Closed_Geometry contains the matching closed FBX meshes, hidden from beauty renders.\n'
           'Both sets share Housing-local coordinates in metres. Move them together if animating.\n'
           'Import the fluid cache back into Blender to retain the exact procedural pearl and glass finish.\n'
           'FBX does not carry the full Blender shader graphs. Native LiquiGen appearance needs separate setup.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'gel_polish_bottle_detailed.blend'))
assert hashlib.sha256(ASSET.read_bytes()).hexdigest()==source_hash
report=json.loads((OUT/'validation.json').read_text())
report['companion_render_strategy']='Original evaluated visual surfaces and shader graphs; matching closed FBX objects retained in a hidden collection.'
report['final_render_provenance']='Companion Blender file renders the original optical surfaces. The closed FBX retains their vertex positions but adds closure faces needed for simulation.'
report['final_renders']=[str((REVIEW/f'final_detailed_package_{side}.png').relative_to(ROOT)) for side in ['front','back']]
(OUT/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('DETAILED_RENDER_PACKAGE_COMPLETE',flush=True)
