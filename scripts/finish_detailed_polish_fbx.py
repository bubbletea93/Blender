"""Remove microscopic zero-area export triangles and verify the final FBX."""
import bpy,bmesh,json,hashlib,sys,shutil
from pathlib import Path
import numpy as np
from mathutils.kdtree import KDTree
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from export_detailed_polish_fbx import coords,topology
OUT=ROOT/'assets/products/exports/gel_polish_bottle_detailed'
REVIEW=ROOT/'renders/detailed_fbx_review'
source=ROOT/'assets/products/gel_polish_bottle.blend'
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
fbx=OUT/'gel_polish_bottle_detailed.fbx'
blend=OUT/'gel_polish_bottle_detailed.blend'
candidate=REVIEW/'gel_polish_bottle_detailed_cleaned.fbx'
report=json.loads((OUT/'validation.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(blend))
colliders=list(bpy.data.collections['LiquiGen_Detailed_Closed_Geometry'].objects)
expected={}
for ob in colliders:
    original=coords(ob.data).copy()
    bm=bmesh.new();bm.from_mesh(ob.data)
    tiny=[f for f in bm.faces if f.calc_area()<1e-18]
    zeros=sum(f.calc_area()==0 for f in bm.faces)
    if tiny:
        edges=list({e for f in tiny for e in f.edges})
        bmesh.ops.dissolve_degenerate(bm,dist=1e-8,edges=edges)
        bm.to_mesh(ob.data)
        ob.data.update()
    after_zeros=sum(f.calc_area()==0 for f in bm.faces)
    bm.free()
    check=topology(ob.data)
    assert check['nonmanifold_edges']==0 and after_zeros==0,check
    cleaned=coords(ob.data)
    deviation=0.0
    if len(original)!=len(cleaned):
        tree=KDTree(len(cleaned))
        for i,p in enumerate(cleaned):tree.insert(p,i)
        tree.balance()
        deviation=max(tree.find(p)[2] for p in original)
        assert deviation<2e-8,deviation
    row=report['parts'][ob.name]
    row['final_cleanup']={'removed_vertices':len(original)-len(cleaned),'max_source_vertex_to_cleaned_surface_vertex_m':deviation,
                          'zero_area_faces_before':zeros,'zero_area_faces_after':after_zeros}
    row['surface_vertex_positions_unchanged']=bool(len(original)==len(cleaned))
    row['topology']=check
    expected[ob.name]=cleaned.copy()
    ob.hide_set(False)
for ob in bpy.context.scene.objects:ob.select_set(False)
for ob in colliders:ob.select_set(True)
bpy.context.view_layer.objects.active=colliders[0]
bpy.ops.export_scene.fbx(filepath=str(candidate),use_selection=True,object_types={'MESH'},
                        apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',global_scale=1,
                        axis_forward='-Z',axis_up='Y',use_mesh_modifiers=False,use_triangles=True,
                        bake_anim=False,add_leaf_bones=False,path_mode='COPY',embed_textures=True)
for ob in colliders:ob.hide_set(True)
staged=REVIEW/'final_detailed_package.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(staged))
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(candidate))
imported=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert {o.name for o in imported}==set(expected)
for ob in imported:
    actual=coords(ob.data)
    matrix=np.array(ob.matrix_world,dtype=np.float64)
    actual=actual@matrix[:3,:3].T+matrix[:3,3]
    assert actual.shape==expected[ob.name].shape
    error=float(np.max(np.linalg.norm(actual-expected[ob.name],axis=1)))
    assert error<1e-7,error
    check=topology(ob.data);assert check['nonmanifold_edges']==0
    bm=bmesh.new();bm.from_mesh(ob.data)
    assert not any(f.calc_area()==0 for f in bm.faces)
    bm.free()
    row=report['parts'][ob.name]
    row['reimport_topology']=check
    row['fbx_reimport_max_vertex_error_m']=error
# Publish only after reimport verification, retaining the earlier candidate.
shutil.copy2(fbx,REVIEW/'detailed_before_triangle_cleanup.fbx')
shutil.copy2(candidate,fbx)
# Save-as with the delivery path so Blender remaps any relative references.
bpy.ops.wm.open_mainfile(filepath=str(staged))
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
report['source_unchanged']=True
report['fbx_sha256']=hashlib.sha256(fbx.read_bytes()).hexdigest()
report['fbx_bytes']=fbx.stat().st_size
(OUT/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('FINAL_DETAILED_FBX_VERIFIED',flush=True)
