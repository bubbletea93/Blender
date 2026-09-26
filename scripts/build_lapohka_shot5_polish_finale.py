"""Build an independent final polish shot using reusable manicure props."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'renders/shot5_polish_finale_v002';WORK.mkdir(parents=True,exist_ok=True)
DEST=ROOT/'scenes/gel_polish_lapohka_shot5_376_528_polish_finale_v002.blend'
SOURCE=ROOT/'scenes/gel_polish_lapohka_shot4_285_375_bottle_array_v004_fine_shimmer.blend'
PROPS=ROOT/'assets/props/manicure_finale_props.blend'
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.name='SHOT05_PolishFinale_376_528'
P='SHOT05_'
def collection(name,parent=None):
    c=bpy.data.collections.new(P+name);(parent or s.collection).children.link(c);return c
master=collection('MASTER')
product=collection('01_HERO',master);props=collection('02_MANICURE_PROPS',master)
stage=collection('03_STAGE',master);lighting=collection('04_LIGHTS',master);cameras=collection('05_CAMERA',master)
def empty(name,c,parent=None):
    ob=bpy.data.objects.new(P+name,None);c.objects.link(ob);ob.parent=parent;ob.empty_display_size=.01;return ob
def instance(name,model,c,location=(0,0,0),rotation=(0,0,0),parent=None):
    ob=empty(name,c,parent);ob.instance_type='COLLECTION';ob.instance_collection=model
    ob.location=location;ob.rotation_euler=rotation;return ob
def keys(ob,path,axis,data,group):
    for frame,value in data:
        getattr(ob,path)[axis]=value;ob.keyframe_insert(path,index=axis,frame=frame,group=group)
def smooth(ob):
    ad=ob.animation_data
    if ad and ad.action:
        for layer in ad.action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for k in fc.keyframe_points:
                            k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'

with bpy.data.libraries.load(str(SOURCE),link=False) as (a,b):
    b.collections=['SHOT04_ASSET_PetrolTeal'];b.worlds=['SHOT04_World_ShadowStudio']
model=b.collections[0];model.name=P+'Product_PetrolTeal'
for ob in model.all_objects:
    ob.name=P+ob.name.removeprefix('SHOT04_');ob.animation_data_clear()
for mat in bpy.data.materials:
    if not mat.library and mat.name.startswith('SHOT04_'):mat.name=P+mat.name.removeprefix('SHOT04_')
for group in bpy.data.node_groups:
    if not group.library and group.name.startswith('SHOT04_'):group.name=P+group.name.removeprefix('SHOT04_')
s.world=b.worlds[0];s.world.name=P+'World_ChampagneStudio'
for node in s.world.node_tree.nodes:
    if node.type=='BACKGROUND':node.inputs['Strength'].default_value=.10
# Give polished metal a readable studio reflection without flattening cast shadows.
wn=s.world.node_tree.nodes;wl=s.world.node_tree.links
ambient=next(n for n in wn if n.type=='BACKGROUND')
reflection=wn.new('ShaderNodeBackground');reflection.name='Metal studio reflection';reflection.inputs['Strength'].default_value=.55
for link in list(ambient.inputs['Color'].links):wl.new(link.from_socket,reflection.inputs['Color'])
rays=wn.new('ShaderNodeLightPath');mix=wn.new('ShaderNodeMixShader')
wl.new(rays.outputs['Is Glossy Ray'],mix.inputs[0]);wl.new(ambient.outputs[0],mix.inputs[1]);wl.new(reflection.outputs[0],mix.inputs[2])
wl.new(mix.outputs[0],next(n for n in wn if n.type=='OUTPUT_WORLD').inputs['Surface'])
travel=empty('Bottle_Travel',product)
tilt=empty('Bottle_Tilt',product,travel)
hero=instance('Bottle_Assembly',model,product,rotation=(math.pi/2,0,0),parent=tilt)
hero['source']='Approved Shot 4 fine shimmer assembly; exact linked product meshes.'
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
points=[]
for inst in deps.object_instances:
    if inst.is_instance and inst.object.type=='MESH':
        points.extend(inst.matrix_world@Vector(v) for v in inst.object.bound_box)
lo=Vector([min(p[i] for p in points) for i in range(3)])
hi=Vector([max(p[i] for p in points) for i in range(3)])
settled=.05-lo.z+.00025
beats=[(376,-.003,-.015,settled+.05),(386,.002,-.012,settled+.052),
       (406,-.001,-.013,settled+.035),(428,0,-.014,settled+.008),
       (439,0,-.014,settled),(446,0,-.014,settled+.0015),
       (452,0,-.014,settled),(508,0,-.014,settled),
       (513,0,-.014,settled),(521,.003,-.014,settled+.044),
       (528,.007,-.014,settled+.132),(535,.012,-.014,settled+.26)]
for axis in range(3):keys(travel,'location',axis,[(v[0],v[axis+1]) for v in beats],'Arrival and lift')
for axis,data in [(0,[(376,1),(388,2),(410,-1),(430,0),(508,0),(518,0),(528,-4),(535,-6)]),
                  (1,[(376,-1),(388,2),(408,-2),(431,0),(508,0),(518,0),(528,7),(535,10)]),
                  (2,[(376,-16),(393,-8),(418,-2),(440,0),(508,0),(518,0),(528,-8),(535,-12)])]:
    keys(tilt,'rotation_euler',axis,[(f,math.radians(v)) for f,v in data],'Gentle orientation')
smooth(travel);smooth(tilt)
travel['editing']='Direct XYZ position keys: float in, settle, hero hold, then upward exit. No drivers.'

names=['Prop_NailSwatchFan','Prop_CatEyeMagnetWand','Prop_LooseTip_Teal','Prop_LooseTip_Raspberry','Stage_CeramicPodium','Prop_ManicureBrushHolder']
with bpy.data.libraries.load(str(PROPS),link=True) as (a,b):b.collections=names[:]
assets=dict(zip(names,b.collections))
podium=instance('CeramicPodium',assets['Stage_CeramicPodium'],stage)
# Keep the shared pedestal geometry, with shot-local ray visibility for a clean lacquer reflection.
local_podium=bpy.data.collections.new(P+'PodiumReflectionControl')
for source_ob in assets['Stage_CeramicPodium'].objects:
    ob=source_ob.copy();local_podium.objects.link(ob);ob.visible_glossy=False
podium.instance_collection=local_podium
fan=instance('SwatchFan',assets['Prop_NailSwatchFan'],props,(.073,.040,.0502),(0,0,math.radians(-9)))
fan.scale=(1.22,1.22,1.22)
holder=instance('ManicureBrushHolder',assets['Prop_ManicureBrushHolder'],props,(-.082,.028,.0502))
wand=instance('CatEyeMagnet',assets['Prop_CatEyeMagnetWand'],props,(-.069,-.048,.0502),(0,0,math.radians(-18)))
tip1=instance('LooseTip_Teal',assets['Prop_LooseTip_Teal'],props,(-.107,-.071,.0502),(0,0,math.radians(-20)))
tip2=instance('LooseTip_Raspberry',assets['Prop_LooseTip_Raspberry'],props,(.071,-.078,.0502),(0,0,math.radians(27)))
# The props settle very gently while the camera first reveals them.
for ob,delay,lift in [(fan,0,.010),(wand,4,.006),(tip1,3,.003),(tip2,6,.003)]:
    ground=ob.location.z
    keys(ob,'location',2,[(376,ground+lift),(402+delay,ground+lift*.45),(431+delay,ground),(450,ground),(528,ground)],'Prop settle')
    smooth(ob)
reveal=empty('StageReveal',stage)
for ob in (podium,fan,holder,wand,tip1,tip2):ob.parent=reveal
keys(reveal,'location',2,[(376,-.11),(384,-.085),(397,-.025),(414,0),(528,0)],'Tabletop reveal')
smooth(reveal)

# A vertical wall receives uninterrupted vertical window shadows.
backmat=bpy.data.materials.new(P+'MAT_ChampagneBackdrop');backmat.use_nodes=True
bs=backmat.node_tree.nodes.get('Principled BSDF')
bs.inputs['Base Color'].default_value=(.37,.22,.085,1);bs.inputs['Roughness'].default_value=.78
profile=[(.40,-2),(.40,2)]
verts=[(x,y,z) for y,z in profile for x in (-1,1)]
faces=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(profile)-1)]
mesh=bpy.data.meshes.new(P+'Backdrop_MESH');mesh.from_pydata(verts,[],faces);mesh.materials.append(backmat)
back=bpy.data.objects.new(P+'ChampagneCyclorama',mesh);stage.objects.link(back)
back.visible_glossy=False
for poly in mesh.polygons:poly.use_smooth=True

def area(name,loc,target,power,size,shape=(1,1),color=(1,1,1)):
    data=bpy.data.lights.new(P+name,'AREA');data.energy=power;data.color=color
    data.shape='RECTANGLE';data.size=size*shape[0];data.size_y=size*shape[1]
    ob=bpy.data.objects.new(P+name,data);lighting.objects.link(ob);ob.location=loc
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();return ob
area('WarmWindow',(-.32,.12,.40),(0,0,.07),10,.045,(1,1.5),(1,.87,.71))
area('CoolSoftFill',(.27,-.18,.25),(0,0,.10),.65,.25,(1,1),(.70,.82,1))
area('GoldEdgeStrip',(.16,.16,.32),(0,0,.10),1.5,.045,(1,4),(1,.91,.76))
left_strip=area('GoldLeftStrip',(-.12,-.22,.14),(0,-.01,.12),2.2,.040,(1,7),(1,.97,.90))
right_strip=area('GoldRightStrip',(.22,-.10,.14),(0,-.01,.12),1.2,.020,(1,12),(1,1,1))
for ob in (left_strip,right_strip):ob.data.diffuse_factor=0
# Slats sit behind the tabletop composition, so their shadows affect the backdrop.
gobos=collection('06_WINDOW_SHADOWS',master)
for index,x in enumerate([-.22,-.15,-.08]):
    me=bpy.data.meshes.new(P+f'Slat_{index+1}_MESH')
    me.from_pydata([(x-.016,.27,-2),(x+.016,.27,-2),(x+.016,.27,2),(x-.016,.27,2)],[],[(0,1,2,3)])
    ob=bpy.data.objects.new(P+f'WindowSlat_{index+1}',me);gobos.objects.link(ob)
    ob.visible_camera=False;ob.visible_glossy=False;ob.visible_transmission=False;ob.display_type='WIRE'

target=empty('CameraTarget',cameras)
focus=empty('LacquerFocus',cameras,hero);focus.location=(0,-.0283464,.0326)
cam=bpy.data.objects.new(P+'Camera',bpy.data.cameras.new(P+'Camera_DATA'));cameras.objects.link(cam);s.camera=cam
cam.data.type='PERSP';cam.data.sensor_width=36;cam.data.clip_start=.001;cam.data.clip_end=20
cam.data.dof.use_dof=True;cam.data.dof.focus_object=focus;cam.data.dof.aperture_fstop=64
track=cam.constraints.new('TRACK_TO');track.name='Aim at composition';track.target=target;track.track_axis='TRACK_NEGATIVE_Z';track.up_axis='UP_Y'
camera_beats=[(376,(-.005,-.295,.250),(-.012,-.005,.172),58),
 (384,(-.009,-.390,.260),(-.008,-.002,.168),60),
 (392,(-.010,-.495,.270),(-.005,.006,.156),62),
 (400,(-.004,-.540,.280),(-.003,.010,.145),62),
 (416,(.006,-.540,.280),(-.003,.014,.120),62),
 (442,(.015,-.535,.262),(-.003,.018,.097),62),
 (482,(.021,-.540,.260),(-.003,.018,.096),62),
 (512,(.022,-.540,.260),(-.003,.018,.096),62),
 (528,(.022,-.540,.260),(-.003,.018,.096),62)]
for axis in range(3):
    keys(cam,'location',axis,[(f,p[axis]) for f,p,t,l in camera_beats],'Dolly reveal')
    keys(target,'location',axis,[(f,t[axis]) for f,p,t,l in camera_beats],'Composition aim')
for f,p,t,lens in camera_beats:
    cam.data.lens=lens;cam.data.keyframe_insert('lens',frame=f,group='Dolly framing')
smooth(cam);smooth(cam.data);smooth(target)

s.frame_start=376;s.frame_end=528;s.render.fps=30
s.render.engine='CYCLES';s.cycles.samples=512;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.003
s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_input_passes='RGB_ALBEDO_NORMAL'
s.cycles.denoising_prefilter='ACCURATE';s.cycles.denoising_quality='HIGH';s.cycles.use_animated_seed=False
s.cycles.max_bounces=12;s.cycles.transmission_bounces=10;s.cycles.transparent_max_bounces=8;s.cycles.sample_clamp_indirect=10
s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100
s.render.film_transparent=False;s.render.use_motion_blur=True;s.render.motion_blur_shutter=.4
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='16'
s.render.filepath='//../renders/shot5_polish_finale_v002/production/frame_'
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-.85
s.unit_settings.system='METRIC'
for frame,label in [(376,'MACRO ARRIVAL'),(392,'PROP REVEAL'),(439,'BOTTLE SETTLE'),(452,'HERO COMPOSITION'),(508,'LIFT PREPARE'),(521,'UPWARD EXIT'),(528,'CUT')]:
    s.timeline_markers.new(label,frame=frame)
s['reference']='//../references/lapohka_3d_motion_shots/Lapohka 3D Motion - Shot 5 (f376-528).mp4'
s['adaptation']='Warm tabletop finale: fine-shimmer polish, five nail swatches, fluted manicure brush holder, cat-eye magnet, two loose tips, ceramic podium.'
note=bpy.data.texts.new('SHOT05_README')
note.write('SHOT 5 v002 / f376-528 / 30fps\n\nHero assembly and fine shimmer reused from approved Shot4 v004.\nReusable manicure props linked from assets/props/manicure_finale_props.blend: swatch fan, brush holder, magnetic tool, two tips, and podium.\nBottle_Travel and Bottle_Tilt have direct editable keys. Camera and CameraTarget control the pullback.\nStageReveal moves the entire tabletop into view during f376-414.\nWarmWindow casts rightward shadows. The vertical wall and tall shadow slats avoid a cutoff.\nFocus follows the actual lacquer surface; f/64 preserves fine shimmer.\nReference rhythm: close view, tableau reveal, gentle settle, held product view, upward exit.\nProduction settings are 4K / 512 samples. Delivered motion review uses 960x540 / 64 samples.\n')
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
s.cycles.device='GPU'
s.frame_set(460);bpy.context.view_layer.update()
for ob in s.objects:ob.select_set(False)
travel.select_set(True);bpy.context.view_layer.objects.active=travel
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':
            a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.overlay.show_extras=False
for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(lib.filepath,start=str(DEST.parent))
bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
(WORK/'build_report.json').write_text(json.dumps(dict(scene=str(DEST),hero_dimensions=list(hi-lo),settled_root_z=settled,
    props_asset=str(PROPS),prop_collections=names,frames=[376,528],fps=30),indent=2))
print('SHOT5_SCENE_SAVED',DEST,flush=True)
