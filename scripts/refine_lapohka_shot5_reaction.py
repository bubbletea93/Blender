"""Author a low-angle opening and editable three-beat landing in a v002 snapshot.

Run with background Blender opening the preserved source session. No shared
assets are changed. Motion is authored choreography rather than a rigid-body bake.
"""
import bpy,math,json,sys,os
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from shot5_secondary_flex import apply_secondary_flex
OUT=ROOT/'renders/shot5_polish_finale_v003';OUT.mkdir(parents=True,exist_ok=True)
DEST=ROOT/'scenes/gel_polish_lapohka_shot5_376_528_polish_finale_v003.blend'
s=bpy.context.scene;P='SHOT05_';source_path=bpy.data.filepath;s.frame_set(480);bpy.context.view_layer.update()
def ob(name):return bpy.data.objects[P+name]
def curves(obj):
    ad=obj.animation_data
    if not ad or not ad.action:return []
    return [f for layer in ad.action.layers for strip in layer.strips for bag in strip.channelbags for f in bag.fcurves]
def keys(obj,path,axis,values,group):
    for frame,value in values:
        getattr(obj,path)[axis]=value;obj.keyframe_insert(path,index=axis,frame=frame,group=group)
def smooth(obj):
    for fc in curves(obj):
        for k in fc.keyframe_points:
            k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
def segment(obj,path,axis,start,end,left_slope,right_slope):
    fc=next(f for f in curves(obj) if f.data_path==path and f.array_index==axis)
    a=next(k for k in fc.keyframe_points if abs(k.co.x-start)<.01)
    b=next(k for k in fc.keyframe_points if abs(k.co.x-end)<.01)
    dt=(end-start)/3
    a.handle_right_type='FREE';a.handle_right=(start+dt,a.co.y+left_slope*dt)
    b.handle_left_type='FREE';b.handle_left=(end-dt,b.co.y-right_slope*dt)
    fc.update()
def bounce_segments(obj,base,arches):
    for start,peak,end,height in arches:
        segment(obj,'location',2,start,peak,2*height/(peak-start),0)
        segment(obj,'location',2,peak,end,0,-2*height/(end-peak))

travel=ob('Bottle_Travel');tilt=ob('Bottle_Tilt');hero=ob('Bottle_Assembly')
settled=travel.location.z
travel_inv=travel.matrix_world.inverted()
local_points=[]
for inst in bpy.context.evaluated_depsgraph_get().object_instances:
    if inst.is_instance and inst.parent and inst.parent.original==hero:
        local_points.extend(travel_inv@inst.matrix_world@Vector(v) for v in inst.object.bound_box)
foot_z=min(p.z for p in local_points)
travel.animation_data_clear();tilt.animation_data_clear()
# Place orientation pivot at the actual supporting foot, retaining the rest pose.
tilt.location.z=foot_z;hero.location.z-=foot_z
impact=bpy.data.objects.new(P+'StageImpact',None)
bpy.data.collections[P+'03_STAGE'].objects.link(impact)
impact.empty_display_size=.025;impact['purpose']='Common stage impulse, followed by delayed individual prop reactions.'
ob('StageReveal').parent=impact;ob('StageReveal').matrix_parent_inverse=Matrix.Identity(4)
travel.parent=impact;travel.matrix_parent_inverse=Matrix.Identity(4)
keys(impact,'location',2,[(376,0),(431,0),(432,0),(434,-.0014),(438,.0010),(442,-.00045),(446,.00016),(451,0),(528,0)],'Impact transmission')
smooth(impact)

height=[(376,.050),(388,.0505),(406,.032),(418,.014),(422,.012),(425,.012),
        (426,.0125),(432,0),(436,.0055),(440,0),(443,.0014),(446,0),(448,.00035),(451,0),
        (508,0),(513,0),(521,.044),(528,.132),(535,.26)]
keys(travel,'location',0,[(376,-.003),(393,.001),(418,0),(451,0),(513,0),(521,.003),(528,.007),(535,.012)],'Drift and exit')
keys(travel,'location',1,[(376,-.015),(406,-.013),(426,-.014),(535,-.014)],'Drift and exit')
keys(travel,'location',2,[(f,settled+h) for f,h in height],'Anticipation action reaction')
rotations={
0:[(376,1),(393,1.5),(418,-1),(425,-1),(426,-1.3),(432,0),(436,-.9),(440,0),(443,.3),(446,0),(451,0),(508,0),(518,0),(528,-4),(535,-6)],
1:[(376,-1),(393,1),(418,-1),(425,-1),(426,-1.2),(432,0),(436,2),(440,0),(443,-.65),(446,0),(448,.15),(451,0),(508,0),(518,0),(528,7),(535,10)],
2:[(376,-16),(393,-8),(418,-2),(426,-2),(432,0),(437,1.2),(445,-.4),(455,0),(508,0),(518,0),(528,-8),(535,-12)]}
for axis,values in rotations.items():keys(tilt,'rotation_euler',axis,[(f,math.radians(v)) for f,v in values],'Foot pivot follow-through')
smooth(travel);smooth(tilt)
# Preserve the accelerating approach and abrupt energy change at each contact.
segment(travel,'location',2,426,432,0,-2*.0125/6)
bounce_segments(travel,settled,[(432,436,440,.0055),(440,443,446,.0014),(446,448,451,.00035)])
travel['timing']='f418-425: slow near-stage anticipation; f426-432: accelerated drop; f432-451: contact/rebound/settle.'
tilt['editing']='Rotation pivot sits at bottle foot. Direct Euler keys; no spin drivers.'

# All props ride the stage immediately; relative hops and rotation lag by mass.
prop_defs=[
 ('ManicureBrushHolder',[(433,436,440,.00045),(440,443,447,.00012)],(.22,.12,.25)),
 ('SwatchFan',[(434,438,443,.00065),(443,447,452,.00020)],(.20,.18,.40)),
 ('CatEyeMagnet',[(434,438,443,.0020),(443,448,454,.00065)],(.9,.35,1.8)),
 ('LooseTip_Teal',[(435,440,446,.0035),(446,451,457,.0015),(457,461,467,.0005)],(5,4,4)),
 ('LooseTip_Raspberry',[(437,442,448,.0040),(448,454,460,.0017),(460,464,470,.00055)],(-4,5,-3.5))]
prop_report=[]
for name,arches,angles in prop_defs:
    obj=ob(name);rest=obj.location.copy();rotation=obj.rotation_euler.copy();obj.animation_data_clear()
    zkeys={376:rest.z,432:rest.z,528:rest.z}
    for start,peak,end,h in arches:zkeys.update({start:rest.z,peak:rest.z+h,end:rest.z})
    keys(obj,'location',2,sorted(zkeys.items()),'Delayed weight response')
    for axis,angle in enumerate(angles):
        values={376:rotation[axis],432:rotation[axis],528:rotation[axis]}
        for i,(start,peak,end,h) in enumerate(arches):
            values[start]=rotation[axis];values[peak]=rotation[axis]+math.radians(angle)*((-1)**i)*(h/arches[0][3]);values[end]=rotation[axis]
        keys(obj,'rotation_euler',axis,sorted(values.items()),'Overlapping settle')
    smooth(obj);bounce_segments(obj,rest.z,arches)
    obj['reaction_delay_frames']=arches[0][0]-432
    obj['reaction_peak_mm']=arches[0][3]*1000
    prop_report.append({'object':obj.name,'delay_frames':arches[0][0]-432,'first_hop_mm':arches[0][3]*1000,'settled_frame':arches[-1][2]})
flex=apply_secondary_flex(s,impact_frame=432)

cam=s.camera;target=ob('CameraTarget')
cam.animation_data_clear();cam.data.animation_data_clear();target.animation_data_clear()
camera_beats=[
 (376,(-.012,-.315,.084),(-.009,-.014,.166),62),
 (384,(-.014,-.390,.122),(-.005,-.010,.166),62),
 (392,(-.010,-.495,.200),(-.004,.006,.156),62),
 (400,(-.004,-.540,.265),(-.003,.010,.145),62),
 (416,(.006,-.540,.280),(-.003,.014,.120),62),
 (442,(.015,-.535,.262),(-.003,.018,.097),62),
 (482,(.021,-.540,.260),(-.003,.018,.096),62),
 (512,(.022,-.540,.260),(-.003,.018,.096),62),
 (528,(.022,-.540,.260),(-.003,.018,.096),62)]
for axis in range(3):
    keys(cam,'location',axis,[(f,p[axis]) for f,p,t,l in camera_beats],'Low hero to tabletop reveal')
    keys(target,'location',axis,[(f,t[axis]) for f,p,t,l in camera_beats],'Composition aim')
cam.data.lens=62;smooth(cam);smooth(target)
cam['opening']='f376 camera at84mm above origin, below the raised bottle, looking upward toward166mm.'
s.timeline_markers.clear()
for frame,label in [(376,'LOW ANGLE HERO'),(392,'REVEAL'),(422,'ANTICIPATION - HOVER'),(426,'ACTION - RELEASE'),(432,'IMPACT'),(436,'REACTION - REBOUND'),(451,'BOTTLE SETTLED'),(470,'PROPS SETTLED'),(508,'LIFT PREPARE'),(528,'CUT')]:s.timeline_markers.new(label,frame=frame)
s['motion_revision']='v003: low-angle closeup, anticipation hover, accelerating drop, stage impulse and weight-dependent delayed follow-through.'
s.render.filepath='//../renders/shot5_polish_finale_v003/production/frame_'
s.render.use_persistent_data=False
txt=bpy.data.texts.get('SHOT05_README') or bpy.data.texts.new('SHOT05_README')
txt.clear();txt.write('SHOT5 v003 / f376-528 / 30fps\nLow-angle opening, hover/drop/impact, delayed reaction.\nBottle_Travel controls height and drift. Bottle_Tilt pivots at the foot.\nStageImpact transmits the landing; StageReveal retains the introductory reveal.\nEach prop root has editable delayed bounce/rotation keys. BrushFlex and SwatchFlex controls add independent overlapping motion.\nAuthored choreography, not a rigid-body simulation.\nProduction:4K512samples. Review:960x540/64samples. Community replacement assets await selection.\n')
s.frame_set(480);bpy.context.view_layer.update()
for obj in bpy.context.selected_objects:obj.select_set(False)
travel.select_set(True);bpy.context.view_layer.objects.active=travel
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.shading.type='SOLID';area.spaces.active.region_3d.view_perspective='CAMERA'
# Resolve against the source session BEFORE moving the scene to another folder.
# Remapping an already destination-relative library while saving would apply
# the directory change twice and silently leave missing mesh libraries.
for lib in bpy.data.libraries:lib.filepath=os.path.normpath(bpy.path.abspath(lib.filepath))
bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
(OUT/'motion_build_report.json').write_text(json.dumps({'scene':str(DEST),'source':source_path,'settled_root_z':settled,'foot_pivot_local_z':foot_z,'impact_frame':432,'height_keys_m':height,'prop_reactions':prop_report,'flex':flex},indent=2))
print('SHOT5_REACTION_SAVED',DEST,flush=True)
