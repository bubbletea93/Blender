"""Build a bottle-specific Shot 4 adaptation, preserving the approved sources.

Run in a fresh background Blender process. Output is a new v003 scene.
"""
import bpy, math, json, numpy as np
from pathlib import Path
from mathutils import Matrix, Vector

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'renders/shot4_bottle_adaptation_v003'
DEST=ROOT/'scenes/gel_polish_lapohka_shot4_285_375_bottle_array_v003.blend'
OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scenes/gel_polish_lapohka_shot3_199_284_liquigen_v010_clearance.blend'))
old=bpy.context.scene
old.frame_set(199)
bpy.context.view_layer.update()
spin=bpy.data.objects['SHOT03_199_284_Spin']
parts=[]
for suffix in ['BottleBody','OldCap','FrontLens','Lacquer']:
    ob=bpy.data.objects['SHOT03_199_284_'+suffix]
    parts.append((suffix,ob,spin.matrix_world.inverted()@ob.matrix_world))
source_mat=bpy.data.objects['SHOT03_199_284_Lacquer'].material_slots[0].material
scene=bpy.data.scenes.new('SHOT04_BottleArray_285_375')
bpy.context.window.scene=scene
P='SHOT04_'
def col(name,parent=None):
    c=bpy.data.collections.new(P+name);(parent or scene.collection).children.link(c);return c
master=col('MASTER');products=col('01_BOTTLE_ARRAY',master);cameras=col('02_CAMERA',master)
stage=col('03_STAGE',master);lights=col('04_LIGHTS',master)
def empty(name,collection,parent=None):
    o=bpy.data.objects.new(P+name,None);collection.objects.link(o);o.parent=parent;o.empty_display_size=.02;return o
layout=empty('ArrayLayout',products)
layout['editing']='Bottle controls have direct Location and Euler Rotation keys. No motion drivers.'
palette=[('Aubergine',(.066,.008,.100),(.27,.065,.34)),
         ('PetrolTeal',(.004,.078,.068),(.025,.29,.235)),
         ('PearlIvory',(.37,.285,.17),(.72,.64,.46)),
         ('Raspberry',(.24,.007,.052),(.60,.055,.20)),
         ('MidnightBlue',(.012,.025,.115),(.045,.105,.37))]

# Rotate the exact approved product assembly onto its back, cap toward +Y.
front_basis=next(m for suffix,ob,m in parts if suffix=='FrontLens').to_quaternion().to_matrix().to_4x4()
flat=Matrix.Rotation(math.radians(-90),4,'Z')@Matrix.Rotation(math.radians(-90),4,'Y')@front_basis.inverted()
models=[]
for label,base,band in palette:
    model=bpy.data.collections.new(P+'ASSET_'+label)
    # Unlinked source collections are rendered only through collection instances.
    lacquer=source_mat.copy();lacquer.name=P+'Lacquer_'+label
    lacquer.animation_data_clear()
    if lacquer.node_tree:
        lacquer.node_tree.animation_data_clear()
        for n in lacquer.node_tree.nodes:
            if n.type=='RGB' and n.name.startswith('Base Color'): n.outputs[0].default_value=(*base,1)
            if n.type=='RGB' and n.name.startswith('Band Color'): n.outputs[0].default_value=(*band,1)
            if n.type=='BSDF_GLOSSY':n.inputs['Color'].default_value=(*base,1)
    for suffix,original,matrix in parts:
        ob=original.copy();ob.name=P+label+'_'+suffix;ob.animation_data_clear()
        ob.parent=None;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_world=flat@matrix
        ob.hide_render=False;ob.hide_viewport=False
        # Prior shot's light links must not suppress new studio illumination.
        ob.light_linking.receiver_collection=None;ob.light_linking.blocker_collection=None
        model.objects.link(ob)
        if suffix=='Lacquer':
            for slot in ob.material_slots:slot.link='OBJECT';slot.material=lacquer
    models.append(model)

# Remove prior shot scene objects after copying the four production parts.
copied={o for c in models for o in c.objects}
for s in list(bpy.data.scenes):
    if s!=scene:bpy.data.scenes.remove(s)
for o in list(bpy.data.objects):
    if o not in copied and o.name not in scene.objects:bpy.data.objects.remove(o,do_unlink=True)
for c in list(bpy.data.collections):
    if c not in models and c not in [master,products,cameras,stage,lights]:bpy.data.collections.remove(c)

# Compute a shared conservative envelope in the new flat-lay coordinates.
probe=empty('EnvelopeProbe',products);probe.instance_type='COLLECTION';probe.instance_collection=models[0]
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
mins=[];maxs=[]
for inst in deps.object_instances:
    if inst.is_instance and inst.object.type=='MESH':
        vertices=inst.object.data.vertices
        coords=np.empty(len(vertices)*3,dtype=np.float32);vertices.foreach_get('co',coords)
        matrix=np.array(inst.matrix_world);world=coords.reshape(-1,3)@matrix[:3,:3].T+matrix[:3,3]
        mins.append(world.min(axis=0));maxs.append(world.max(axis=0))
assert mins,'No instanced product geometry'
lo=Vector(np.min(mins,axis=0));hi=Vector(np.max(maxs,axis=0))
center=(lo+hi)*.5
for model in models:
    for ob in model.objects:ob.location-=Vector((center.x,center.y,lo.z))
bpy.data.objects.remove(probe,do_unlink=True)
half=(hi-lo)*.5

def curve_keys(ob,path,axis,keys):
    for f,v in keys:
        getattr(ob,path)[axis]=v
        ob.keyframe_insert(path,index=axis,frame=f,group={'location':'Glide','rotation_euler':'Rock and settle'}[path])
def smooth(ob):
    if not ob.animation_data or not ob.animation_data.action:return
    for layer in ob.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for kp in fc.keyframe_points:
                        kp.interpolation='BEZIER';kp.handle_left_type='AUTO_CLAMPED';kp.handle_right_type='AUTO_CLAMPED'

rigs=[]
for row in range(-2,3):
 for column in range(-3,4):
    idx=(column+2*row)%len(models)
    if row==0 and column==0:idx=0
    ob=empty(f'Bottle_R{row+3:02d}_C{column+4:02d}_{palette[idx][0]}',products,layout)
    ob.instance_type='COLLECTION';ob.instance_collection=models[idx]
    ob.rotation_mode='XYZ'
    delay=(column+3)%3 + (row+2)%2
    x=column*.060;y=row*.115
    ob.location=(x,y,.0008)
    ob['motion']='Short sideways glide + 7 degree maximum rock; face always visible.'
    ob['shade']=palette[idx][0]
    # Shared entry direction and small timing offsets prevent neighboring collisions.
    direction=1
    curve_keys(ob,'location',0,[(281+delay,x-direction*.022),(288+delay,x-direction*.008),
        (298+delay,x+direction*.0018),(307+delay,x-direction*.0005),(318+delay,x),(375,x)])
    curve_keys(ob,'rotation_euler',1,[(281+delay,math.radians(direction*7)),
        (292+delay,math.radians(-direction*3)),(301+delay,math.radians(direction*1.4)),
        (310+delay,math.radians(-direction*.5)),(320+delay,0),(375,0)])
    curve_keys(ob,'rotation_euler',2,[(281+delay,math.radians(direction*8)),
        (296+delay,math.radians(-direction*1.8)),(306+delay,math.radians(direction*.6)),
        (320+delay,0),(375,0)])
    # Lift only enough for the rounded bottle to rock above the stage.
    curve_keys(ob,'location',2,[(281+delay,.0039),(292+delay,.0023),
        (301+delay,.0015),(310+delay,.0011),(320+delay,.0008),(375,.0008)])
    lane=1 if column%2==0 else -1
    curve_keys(ob,'location',1,[(281,y),(354,y),(363+delay,y+lane*.009),(375,y+lane*.122),(382,y+lane*.235)])
    smooth(ob);rigs.append(ob)

# Reuse the studio sweep and linked world; shot-local floor finish.
with bpy.data.libraries.load(str(ROOT/'assets/environments/studio_backdrop.blend'),link=True) as (src,dst):dst.collections=['Studio_Backdrop']
linked=dst.collections[0];stage.children.link(linked)
back=linked.override_hierarchy_create(scene,bpy.context.view_layer,do_fully_editable=True)
if linked.name in stage.children:stage.children.unlink(linked)
if back.name not in stage.children:stage.children.link(back)
back.name=P+'Studio_Backdrop'
floor=bpy.data.materials.new(P+'MAT_WarmPorcelain');floor.use_nodes=True
bs=floor.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.27,.285,.31,1);bs.inputs['Roughness'].default_value=.72
for ob in back.all_objects:
    ob.animation_data_clear()
    if 'Lavender' in ob.name:ob.hide_render=True;ob.hide_viewport=True;continue
    ob.scale=(4,4,4);ob.location=(0,0,.048)
    for slot in ob.material_slots:slot.link='OBJECT';slot.material=floor
    bpy.context.view_layer.update()
    eo=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mi=eo.matrix_world.inverted()
    hit,position,normal,face=eo.ray_cast(mi@Vector((0,0,1)),(mi.to_3x3()@Vector((0,0,-1))).normalized())
    assert hit,'Stage floor not found'
    ob.location.z-=(eo.matrix_world@position).z
with bpy.data.libraries.load(str(ROOT/'assets/environments/studio_environment_world.blend'),link=True) as (src,dst):dst.worlds=['Studio_Environment_HDRI']
scene.world=dst.worlds[0].copy();scene.world.name=P+'World_ShadowStudio'
for node in scene.world.node_tree.nodes:
    if node.type=='BACKGROUND':node.inputs['Strength'].default_value=.16

def aim(ob,target):ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
with bpy.data.libraries.load(str(ROOT/'assets/lighting/three_point_studio.blend'),link=True) as (src,dst):dst.collections=['Lights_ThreePoint_Studio']
linked=dst.collections[0];lights.children.link(linked)
rig=linked.override_hierarchy_create(scene,bpy.context.view_layer,do_fully_editable=True)
if linked.name in lights.children:lights.children.unlink(linked)
if rig.name not in lights.children:lights.children.link(rig)
rig.name=P+'StudioLights'
specs=[('WarmWindow',(-.36,-.25,.55),30,(1,.83,.65),.065,.14),
       ('SoftFill',(.28,.10,.65),4,(.82,.9,1),.5,.5),
       ('CapStrip',(.02,.45,.45),7,(1,.94,.83),.045,.5)]
lightobs=[o for o in rig.all_objects if o.type=='LIGHT']
for i,ob in enumerate(lightobs):
    ob.animation_data_clear();ob.parent=None;ob.matrix_parent_inverse=Matrix.Identity(4)
    if i>=len(specs):ob.hide_render=True;ob.hide_viewport=True;continue
    name,loc,power,color,sx,sy=specs[i];ob.name=P+name;ob.data=ob.data.copy()
    ob.location=loc;ob.data.type='AREA';ob.data.shape='RECTANGLE';ob.data.energy=power
    ob.data.color=color;ob.data.size=sx;ob.data.size_y=sy;ob.hide_render=False;ob.hide_viewport=False
    ob.visible_glossy=True;aim(ob,(0,0,0))

# Physical off-camera window slats cast broad, softly edged bands on the sweep.
gobos=col('05_SHADOW_SLATS',master)
gobo_mat=bpy.data.materials.new(P+'MAT_ShadowBlocker');gobo_mat.diffuse_color=(.01,.01,.01,1)
for index,offset in enumerate([-.105,.115]):
    mesh=bpy.data.meshes.new(P+f'WindowSlat_{index+1}_MESH')
    mesh.from_pydata([(-.014,-.55,0),(.014,-.55,0),(.014,.55,0),(-.014,.55,0)],[],[(0,1,2,3)])
    ob=bpy.data.objects.new(P+f'WindowSlat_{index+1}',mesh);gobos.objects.link(ob)
    ob.location=(-.144+offset*.6,-.10,.22);ob.rotation_euler.z=math.radians(-24)
    ob.visible_camera=False;ob.visible_glossy=False;ob.visible_transmission=False
    ob.data.materials.append(gobo_mat);ob.display_type='WIRE'

focus=empty('Focus',cameras);focus.location=(0,0,.014)
cam=bpy.data.objects.new(P+'Camera',bpy.data.cameras.new(P+'Camera_DATA'));cameras.objects.link(cam)
scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.40;cam.data.lens=65
cam.data.clip_start=.001;cam.data.clip_end=10
cam.data.dof.use_dof=True;cam.data.dof.focus_object=focus;cam.data.dof.aperture_fstop=22
tilt=empty('CameraTilt',cameras);tilt.location=focus.location
cr=empty('CameraRoll',cameras,tilt)
cam.parent=cr;cam.location=(0,0,.82);cam.rotation_euler=(0,0,0)
for frame,roll,pitch,scale in [(285,35,14,.255),(298,35,14,.255),(321,35,14,.255),(336,35,14,.255),
                          (348,0,0,.305),(357,0,0,.305),(375,0,0,.305)]:
    cr.rotation_euler.z=math.radians(roll)
    cr.keyframe_insert('rotation_euler',index=2,frame=frame,group='Camera roll')
    tilt.rotation_euler.x=math.radians(pitch);tilt.keyframe_insert('rotation_euler',index=0,frame=frame,group='Face alignment')
    cam.data.ortho_scale=scale;cam.data.keyframe_insert('ortho_scale',frame=frame,group='Framing')
smooth(cr);smooth(tilt);smooth(cam.data)

scene.frame_start=285;scene.frame_end=375;scene.render.fps=30
scene.render.engine='CYCLES';scene.cycles.samples=256;scene.cycles.use_denoising=True
scene.cycles.adaptive_threshold=.005;scene.cycles.max_bounces=12;scene.cycles.transmission_bounces=10
scene.render.resolution_x=3840;scene.render.resolution_y=2160;scene.render.resolution_percentage=100
scene.render.use_motion_blur=True;scene.render.motion_blur_shutter=.4
scene.render.film_transparent=False;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
scene.render.filepath='//../renders/shot4_bottle_adaptation_v003/production/shot4_'
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.65
scene.unit_settings.system='METRIC'
for f,label in [(285,'GLIDE IN'),(299,'SOFT OVERSHOOT'),(321,'DIAGONAL PALETTE'),(336,'CAMERA UNROLL'),(348,'FRONT-FACING GRID'),(360,'LANES RELEASE'),(375,'CUT ON MOTION')]:scene.timeline_markers.new(label,frame=f)
scene['reference']='//../references/lapohka_3d_motion_shots/Lapohka 3D Motion - Shot 4 (f285-375).mp4'
scene['adaptation']='Full-frame array. Bottle on back: staggered glide and subtle rock, then camera unroll and alternating lane exit.'
scene['source_product']='Approved Shot 3 v010 assembly; linked product meshes and shared pearl shader.'
notes=bpy.data.texts.new('SHOT04_README')
notes.write('SHOT 4 v003 / f285–375 / 30 FPS\n\n35 bottle instances, five lacquer shades.\nTighter 60mm columns and 115mm rows. Diagonal crop shows three dominant bottles; frontal view shows five full middle-row bottles and partial adjacent rows.\nSource assembly tilt removed. CameraTilt reaches zero at f348 for true face-on view.\nWindowSlats cast real backdrop shadows.\nDirect editable Location and Euler Rotation keys on Bottle controls; no spin drivers.\nCameraRoll / CameraTilt / Camera_DATA scale control framing.\nProduction meshes, gold, glass, pearl finish, studio sweep and light assets reused.\nLocal world strength reduced to retain shadows.\n')
for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(lib.filepath,start=str(DEST.parent))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
scene.cycles.device='GPU'
scene.frame_set(321);bpy.context.view_layer.update()
for text in list(bpy.data.texts):
    if text!=notes and not text.library:bpy.data.texts.remove(text)
bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
for ob in scene.objects:ob.select_set(False)
hero_control=next(o for o in rigs if 'R03_C04' in o.name)
hero_control.select_set(True);bpy.context.view_layer.objects.active=hero_control
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
(OUT/'build_report.json').write_text(json.dumps({'scene':str(DEST),'bottles':len(rigs),'shades':len(models),'product_size':list(hi-lo),'source_parts':[s for s,_,_ in parts]},indent=2))
print('SHOT4_ARRAY_READY',DEST,flush=True)
