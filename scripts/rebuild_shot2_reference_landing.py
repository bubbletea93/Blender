"""Restore Shot 2's missing opening and author a small, supported landing bounce.

Open the existing Shot 2 scene, then run this script. Writes a new scene only.
The existing procession and the approved edge fall from f96 onward are retained.
"""
import bpy
import json
import math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'renders/shot2_reference_rebuild'
OUT.mkdir(parents=True,exist_ok=True)
DEST=ROOT/'scenes/gel_polish_lapohka_shot2_57_198_reference_v002.blend'
s=bpy.context.scene
assert bpy.data.objects.get('SHOT02_57_96_Travel')
travel=bpy.data.objects['SHOT02_57_96_Travel']
rock=bpy.data.objects['SHOT02_57_96_Rock']
spin=bpy.data.objects['SHOT02_57_96_Spin']

def curves(obj):
    return [f for l in obj.animation_data.action.layers for t in l.strips
            for b in t.channelbags for f in b.fcurves]

def state(frame):
    s.frame_set(frame)
    return {o.name:([float(x) for row in o.matrix_world for x in row],o.hide_render)
            for o in s.objects}

later={f:state(f) for f in [96,100,117,135,160,182,198]}
s.frame_set(96)
original_locations={o.name:list(o.location) for o in (travel,rock,spin)}
original_rotations={o.name:list(o.rotation_euler) for o in (travel,rock,spin)}
first_meshes=[o for o in s.objects if o.type=='MESH' and
              o.name.startswith('SHOT02_57_96_') and
              any(o.name.endswith(n) for n in ['BottleBody','Lacquer','OldCap','FrontLens'])]
deps=bpy.context.evaluated_depsgraph_get()
points=[]
for obj in first_meshes:
    evaluated=obj.evaluated_get(deps)
    mesh=evaluated.to_mesh()
    xyz=np.empty(len(mesh.vertices)*3,dtype=np.float32)
    mesh.vertices.foreach_get('co',xyz)
    m=np.array(spin.matrix_world.inverted() @ evaluated.matrix_world)
    points.append(xyz.reshape(-1,3) @ m[:3,:3].T + m[:3,3])
    evaluated.to_mesh_clear()
support=np.concatenate(points)
for obj in (travel,rock,spin): obj.animation_data_clear()

def key(obj,path,index,values):
    for frame,value in values:
        getattr(obj,path)[index]=value
        obj.keyframe_insert(path,index=index,frame=frame,group='Opening landing')
    for fc in curves(obj):
        for k in fc.keyframe_points:
            k.interpolation='BEZIER'
            k.handle_left_type=k.handle_right_type='AUTO_CLAMPED'

key(rock,'rotation_euler',0,[(57,math.radians(-3)),(61,math.radians(2)),
    (64,math.radians(-1.2)),(67,math.radians(.6)),(69,math.radians(-.3)),
    (72,math.radians(.12)),(78,0),(96,0)])
key(spin,'rotation_euler',2,[(57,math.radians(-14)),(61,math.radians(-12)),
    (67,math.radians(-6)),(78,math.radians(2)),(87,math.radians(3.5)),
    (96,original_rotations[spin.name][2])])
key(travel,'location',1,[(57,-.002),(61,0),(78,0),(96,0)])

def minimum_z():
    bpy.context.view_layer.update()
    m=np.array(spin.matrix_world)
    return float(np.min(support @ m[2,:3] + m[2,3]))

# Independent incoming and outgoing tangents make contact crisp while the
# increasingly small ballistic arcs provide the reaction; the bottle is rigid.
beats=[(57,.059,-.012,-.012),(61,0,-.020,.00235),
       (64,.0035,0,0),(67,0,-.00235,.00085),(69,.00085,0,0),
       (72,0,-.00048,0),(78,0,0,0),(87,0,0,0),(96,0,0,0)]
zkeys=[]
for frame,lift,in_slope,out_slope in beats:
    s.frame_set(frame);travel.location.z=0
    base=-minimum_z()
    z=lift+base+.00008 if frame<78 else original_locations[travel.name][2]
    zkeys.append((frame,z,in_slope,out_slope))
key(travel,'location',2,[(f,z) for f,z,_,_ in zkeys])
fc=next(c for c in curves(travel) if c.data_path=='location' and c.array_index==2)
for i,(k,beat) in enumerate(zip(fc.keyframe_points,zkeys)):
    f,z,ins,outs=beat
    left=(f-zkeys[i-1][0])/3 if i else 1
    right=(zkeys[i+1][0]-f)/3 if i<len(zkeys)-1 else 1
    k.handle_left_type=k.handle_right_type='FREE'
    k.handle_left=(f-left,z-ins*left)
    k.handle_right=(f+right,z+outs*right)

s.frame_start=57;s.frame_end=198;s.render.fps=30
s.name='SHOT02_ReferenceLanding_57_198'
for label,frame in [('DROP FROM ABOVE',57),('SHELF CONTACT',61),('SMALL REBOUND',64),
                    ('SECOND CONTACT',67),('SETTLED',78),('PROCESSION',99)]:
    s.timeline_markers.new(label,frame=frame)

# Verify the restored opening at quarter-frame intervals. Existing tiny mesh
# bevel tolerances are measured rather than concealed by a large levitation gap.
samples=[]
for t in np.arange(57,96.001,.25):
    s.frame_set(int(t),subframe=float(t%1));samples.append({'frame':float(t),'minimum_z':minimum_z()})
minimum=min(r['minimum_z'] for r in samples)
assert minimum > -.00015, minimum
later_errors={}
for frame,before in later.items():
    after=state(frame)
    errors={name:max(abs(x-y) for x,y in zip(vals[0],after[name][0]))
            for name,vals in before.items() if after[name][1]!=vals[1] or
            (not vals[1] and max(abs(x-y) for x,y in zip(vals[0],after[name][0]))>1e-6)}
    if errors:later_errors[frame]=errors
assert not later_errors,later_errors
s.frame_set(64)
s['opening_revision']='Restored f57–95. Contact61; small rebound64; contact67; micro rebound69; settled78. Original f96–198 transforms and visibility retained.'
note=bpy.data.texts.new('SHOT02_OPENING_README')
note.write(s['opening_revision']+'\nEdit SHOT02_57_96_Travel, Rock, and Spin in the Dope Sheet.\n')
note.use_fake_user=True
s.render.filepath='//../renders/shot2_reference_rebuild/production_4k/frame_'
s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100
for obj in list(bpy.context.selected_objects):obj.select_set(False)
for obj in (travel,rock,spin):obj.select_set(True)
bpy.context.view_layer.objects.active=travel
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
report={'scene':str(DEST),'frames':[57,198],'fps':30,'opening_keys':zkeys,
        'quarter_frame_support_samples':samples,'minimum_support_z':minimum,
        'later_frames_verified':list(later),'later_transform_errors':later_errors}
(OUT/'landing_validation.json').write_text(json.dumps(report,indent=2))
print('SHOT2_LANDING_READY',json.dumps({k:v for k,v in report.items() if k!='quarter_frame_support_samples'}),flush=True)
