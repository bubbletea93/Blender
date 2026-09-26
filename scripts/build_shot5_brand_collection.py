"""Replace Shot5 props with a brand collection presentation in separate v005.

Run against v004 with factory startup; requires both reusable display libraries.
The hero's opening and vertical three-beat choreography remain unchanged.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Matrix, Vector

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'scenes/gel_polish_lapohka_shot5_376_528_polish_finale_v005.blend'
OUT=ROOT/'renders/shot5_brand_collection_v005';OUT.mkdir(parents=True,exist_ok=True)
assert Path(bpy.data.filepath).name.endswith('polish_finale_v004.blend')
s=bpy.context.scene;s.frame_set(480)

def curves(ob):
    ad=ob.animation_data
    if not ad or not ad.action:return []
    return [fc for l in ad.action.layers for st in l.strips for bag in st.channelbags
            if bag.slot_handle==ad.action_slot_handle for fc in bag.fcurves]

def keys(ob,path,axis,values):
    for frame,value in values:
        getattr(ob,path)[axis]=value
        ob.keyframe_insert(path,index=axis,frame=frame,group='Collection display response')
    for fc in curves(ob):
        for k in fc.keyframe_points:
            k.interpolation='BEZIER';k.handle_left_type=k.handle_right_type='AUTO_CLAMPED'

def empty(name,parent=None):
    ob=bpy.data.objects.new(name,None);props.objects.link(ob);ob.parent=parent
    ob.empty_display_size=.012
    return ob

# Remove only obsolete dressing from the new scene; v004 and source assets stay intact.
old=bpy.data.collections['SHOT05_02_MANICURE_PROPS']
removed=[o.name for o in old.objects]
for ob in list(old.objects):bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.collections.remove(old)
props=bpy.data.collections.new('SHOT05_02_BRAND_COLLECTION')
bpy.data.collections['SHOT05_MASTER'].children.link(props)
stage=bpy.data.objects['SHOT05_StageReveal']
podium=bpy.data.objects['SHOT05_CeramicPodium']
podium.scale.x=podium.scale.y=.205/.160
podium['diameter_mm']=410

assets={}
for filename,name in [('brand_collection_bottle_rack.blend','Prop_BrandCollection_AcrylicRack'),
                      ('brand_collection_sample_board.blend','Prop_BrandCollection_SampleBoard')]:
    path=ROOT/'assets/props'/filename
    assert path.is_file(),path
    with bpy.data.libraries.load(str(path),link=True) as (available,loaded):
        assert name in available.collections,(name,available.collections)
        loaded.collections=[name]
    assets[name]=loaded.collections[0]

rack=empty('SHOT05_CollectionRack',stage)
rack.location=(.098,.029,.0502);rack.rotation_euler.z=math.radians(-8)
rack['description']='Six full-size shades on two clear acrylic tiers. Editable bottle controls.'
# Local object containers provide independent reactions; geometry/materials remain linked.
bottles=[]
for source in assets['Prop_BrandCollection_AcrylicRack'].objects:
    ob=source.copy();ob.name='SHOT05_'+source.name;props.objects.link(ob)
    ob.parent=rack;ob.matrix_parent_inverse=Matrix.Identity(4)
    # Library collections are not linked into the active view layer. Their
    # stored matrix_world can be identity; rebuild from saved local channels.
    ob.matrix_basis=Matrix.LocRotScale(source.location,source.rotation_euler.to_quaternion(),source.scale)
    ob.animation_data_clear()
    if source.name.startswith('CollectionRack_Bottle_'):bottles.append(ob)

board=empty('SHOT05_CollectionSampleBoard',stage)
board.instance_type='COLLECTION';board.instance_collection=assets['Prop_BrandCollection_SampleBoard']
board.location=(-.107,.023,.0502);board.rotation_euler.z=math.radians(10)
board['description']='Pearl-bordered landscape collection board, raised display support, mounted paired cat-eye samples.'

# The heavy display bases react first and very little. Individual bottles
# respond one to three frames later with small supported rebounds.
for ob,delay,hop in [(rack,2,.00022),(board,3,.0003)]:
    z=ob.location.z
    keys(ob,'location',2,[(376,z),(432+delay,z),(436+delay,z+hop),
                         (442+delay,z),(447+delay,z+hop*.25),(453+delay,z),(528,z)])
for i,ob in enumerate(sorted(bottles,key=lambda x:x.name)):
    z=ob.location.z;delay=3+(i%3);sign=1 if i%2==0 else -1
    keys(ob,'location',2,[(376,z),(432+delay,z),(436+delay,z+.0006),
                         (441+delay,z+.0002),(446+delay,z+.0003),(453+delay,z),(528,z)])
    keys(ob,'rotation_euler',1,[(376,0),(432+delay,0),(436+delay,math.radians(sign*.4)),
                               (441+delay,math.radians(-sign*.16)),(446+delay,math.radians(sign*.08)),
                               (453+delay,0),(528,0)])

# Bring hero forward after the tight opening to keep its silhouette separated
# from the rack. Vertical position/timing and all tilt curves are preserved.
hero=bpy.data.objects['SHOT05_Bottle_Travel']
for fc in curves(hero):
    if fc.data_path=='location' and fc.array_index==1:
        for k in fc.keyframe_points:
            blend=max(0,min(1,(k.co.x-386)/30))
            delta=-.038*blend
            k.co.y+=delta;k.handle_left.y+=delta;k.handle_right.y+=delta
        fc.update()

# Widen only the reveal/held composition; preserve low-angle f376 and f384.
cam=s.camera;target=bpy.data.objects['SHOT05_CameraTarget']
camera={392:(-.010,-.56,.22),400:(-.004,-.70,.30),416:(.006,-.735,.325),
        442:(.020,-.735,.322),482:(.026,-.740,.320),512:(.027,-.740,.320),528:(.027,-.740,.320)}
aim={392:(-.004,.006,.156),400:(-.003,.015,.147),416:(-.003,.021,.124),
     442:(-.003,.020,.115),482:(-.003,.020,.114),512:(-.003,.020,.114),528:(-.003,.020,.114)}
for ob,values in [(cam,camera),(target,aim)]:
    for fc in curves(ob):
        if fc.data_path!='location':continue
        for k in fc.keyframe_points:
            f=round(k.co.x)
            if f in values:
                delta=values[f][fc.array_index]-k.co.y
                k.co.y+=delta;k.handle_left.y+=delta;k.handle_right.y+=delta
        fc.update()

s.render.use_persistent_data=False
s.render.filepath='//../renders/shot5_polish_finale_v005/production_4k/frame_'
s['adaptation']='Brand collection display: pearl-bordered paired sample board and six full-size polish shades on clear acrylic tiers.'
s['community_assets_status']='v005 replaces the community tray/glass dressing with purpose-built brand collection displays. v004 preserved.'
s['brand_reference']='User supplied Hang Pure sample-collection and acrylic rack photographs, 2026-09-25.'
s['motion_revision']='v003 vertical hero choreography retained; forward separation during reveal; small delayed display and bottle reactions.'
txt=bpy.data.texts['SHOT05_README'];txt.clear()
txt.write('SHOT5 v005 / f376-528 / 30 fps\nBrand collection presentation based on supplied Hang Pure product photographs.\nNew reusable assets: assets/props/brand_collection_sample_board.blend and brand_collection_bottle_rack.blend.\nPearl-bordered landscape sample board, mounted paired tips, and two-tier clear acrylic rack with six full-size product variants.\nHero remains the approved bottle mesh/shader. Low-angle opening and vertical hover/drop/bounce/exit remain.\nBottle_Travel Y brings hero forward after the opening; camera pulls back to reveal the larger 410 mm podium.\nCollectionRack, CollectionSampleBoard and six CollectionRack_Bottle controls have direct editable response keys.\nAttached swatches follow their board. No tool props, loose tips, cup, tray or fan remain in this scene.\n4K/512-sample production settings retained. Render composition stills before a new production sequence.\n')
s.frame_set(480);bpy.context.view_layer.update()
for ob in list(bpy.context.selected_objects):ob.select_set(False)
hero.select_set(True);bpy.context.view_layer.objects.active=hero
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.shading.type='SOLID'
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
(OUT/'scene_build.json').write_text(json.dumps({'scene':str(DEST),'removed_old_dressing':removed,
    'bottle_controls':[o.name for o in bottles],'rack_location':list(rack.location),
    'board_location':list(board.location),'podium_radius_m':.205,
    'opening_camera_preserved':True,'hero_vertical_choreography_preserved':True},indent=2))
print('BRAND_COLLECTION_SCENE_READY',str(DEST),flush=True)
