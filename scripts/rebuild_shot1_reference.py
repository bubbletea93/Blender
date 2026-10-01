"""Recreate the reference's rise, product hold, spin/swap and requested drop-out.

Reuses Shot 1's linked bottle and world; saves a separate review scene.
The reference itself cuts at f57; the f47-56 downward exit is an authored bridge.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'renders/shot1_reference_rebuild'
OUT.mkdir(parents=True,exist_ok=True)
DEST=ROOT/'scenes/gel_polish_lapohka_shot1_0_56_reference_v002.blend'
s=bpy.context.scene
assert bpy.data.objects.get('Housing')
s.frame_set(48)
housing=bpy.data.objects['Housing']
housing.animation_data_clear()
housing.rotation_mode='XYZ';housing.rotation_euler=(0,0,0)
bpy.context.view_layer.update()
product=[housing]+list(housing.children_recursive)
visible=[o for o in product if o.type=='MESH' and not o.hide_render]
dg=bpy.context.evaluated_depsgraph_get()
corners=[o.evaluated_get(dg).matrix_world @ Vector(p) for o in visible
         for p in o.evaluated_get(dg).bound_box]
lo=Vector(tuple(min(p[i] for p in corners) for i in range(3)))
hi=Vector(tuple(max(p[i] for p in corners) for i in range(3)))
center=(lo+hi)/2
height=hi.z-lo.z
rig=bpy.data.collections.new('SHOT01_MOTION_CONTROLS');s.collection.children.link(rig)

def empty(name,parent=None):
    obj=bpy.data.objects.new(name,None);rig.objects.link(obj)
    obj.empty_display_type='PLAIN_AXES';obj.empty_display_size=.025
    if parent:obj.parent=parent
    return obj

travel=empty('SHOT01_Travel')
tilt=empty('SHOT01_Tilt',travel)
spin=empty('SHOT01_Spin',tilt)
housing.parent=spin;housing.matrix_parent_inverse=Matrix.Identity(4)
housing.location-=center
travel.location=(center.x,center.y,.16)
travel['purpose']='Screen entrance and exit. Z keys control the rise and drop.'
tilt['purpose']='Independent lean about the bottle center; X is screen-space lean.'
spin['purpose']='Editable one-way axial turn on Z. One fast revolution around the color swap.'

def fcurves(obj):
    return [fc for layer in obj.animation_data.action.layers for strip in layer.strips
            for bag in strip.channelbags for fc in bag.fcurves]

def curve(obj,path,index,table):
    for f,value in table:
        getattr(obj,path)[index]=value
        obj.keyframe_insert(path,index=index,frame=f,group=obj.name)
    fc=next(c for c in fcurves(obj) if c.data_path==path and c.array_index==index)
    for p in fc.keyframe_points:
        p.interpolation='BEZIER';p.handle_left_type=p.handle_right_type='AUTO_CLAMPED'
    return fc

# Rise is fast at the bottom, arrests around f12, then retains subtle drift.
# A final acceleration takes the complete bottle below frame before the cut.
rise=[(0,.012),(4,.108),(9,.159),(12,.170),(19,.163),(26,.162),
      (36,.164),(45,.162),(47,.158),(50,.126),(53,.071),(56,-.006)]
zcurve=curve(travel,'location',2,rise)
slopes=[.028,.018,.004,0,-.0004,0,0,-.0003,-.005,-.014,-.022,-.030]
for i,(point,(f,z),slope) in enumerate(zip(zcurve.keyframe_points,rise,slopes)):
    left=(f-rise[i-1][0])/3 if i else 1
    right=(rise[i+1][0]-f)/3 if i<len(rise)-1 else 1
    point.handle_left_type=point.handle_right_type='FREE'
    point.handle_left=(f-left,z-left*slope);point.handle_right=(f+right,z+right*slope)
curve(travel,'location',1,[(0,center.y-.005),(12,center.y),(26,center.y+.001),
                         (38,center.y),(47,center.y),(56,center.y+.002)])
curve(tilt,'rotation_euler',0,[(0,math.radians(-4)),(12,math.radians(-10)),
    (22,math.radians(-14)),(28,math.radians(-16)),(34,math.radians(7)),
    (43,math.radians(1)),(47,math.radians(-2)),(56,math.radians(4))])
curve(tilt,'rotation_euler',1,[(0,math.radians(3)),(12,math.radians(-3)),
    (25,math.radians(-4)),(33,math.radians(3)),(44,math.radians(1)),(56,math.radians(4))])
turns=[(0,-8),(12,0),(23,9),(27,65),(30,180),(33,302),(37,355),(45,363),(56,371)]
fc=curve(spin,'rotation_euler',2,[(f,math.radians(v)) for f,v in turns])
rates=[.8,.6,2,29,45,29,2.5,.8,.8]
for i,(k,(f,v),rate) in enumerate(zip(fc.keyframe_points,turns,rates)):
    left=(f-turns[i-1][0])/3 if i else 1
    right=(turns[i+1][0]-f)/3 if i<len(turns)-1 else 1
    k.handle_left_type=k.handle_right_type='FREE'
    k.handle_left=(f-left,math.radians(v-left*rate))
    k.handle_right=(f+right,math.radians(v+right*rate))

# Fixed framing lets the bottle visibly cross the lower image edge.
camera=s.camera
camera.animation_data_clear();camera.parent=None;camera.matrix_parent_inverse=Matrix.Identity(4)
for c in list(camera.constraints):camera.constraints.remove(c)
camera.name='SHOT01_Camera'
camera.data.animation_data_clear();camera.data.lens=50
target=Vector((center.x,center.y,.160))
camera.location=target+Vector((.355,0,.020))
camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
camera.scale=(1,1,1);camera.data.dof.use_dof=False
oldtarget=bpy.data.objects.get('Target_Gel_macro_closeup')
if oldtarget:oldtarget.animation_data_clear();oldtarget.hide_viewport=True;oldtarget.hide_render=True

# Keep the original coral and green lacquers. The back-facing spin conceals
# the color cut; blue is omitted because the supplied reference shows two looks.
mat=next(m for m in bpy.data.materials if m.name=='LacquerShade_Swap_AB' and not m.library)
mat.name='SHOT01_Coral_to_Emerald'
mat.node_tree.animation_data_clear()
for name in ['SwapMix','SwapBC']:
    socket=mat.node_tree.nodes[name].inputs[0]
    for frame,value in [(0,0),(29,0),(30,1),(56,1)]:
        socket.default_value=value;socket.keyframe_insert('default_value',frame=frame)
for fc in fcurves(mat.node_tree):
    for p in fc.keyframe_points:p.interpolation='CONSTANT'
# Fine shimmer uses the same settings approved for the later product shots.
wrapper=next(g for g in bpy.data.node_groups if g.name.startswith('Glitter_UVFix') and not g.library).copy()
wrapper.name='SHOT01_FineShimmer_Wrapper'
core=wrapper.nodes['Shared render glitter finish'].node_tree.copy();core.name='SHOT01_FineShimmer_Core'
wrapper.nodes['Shared render glitter finish'].node_tree=core
for node in mat.node_tree.nodes:
    if node.type=='GROUP' and node.node_tree and node.node_tree.name.startswith('Glitter_UVFix'):node.node_tree=wrapper
core.nodes['Fine pearl facet density'].inputs['Scale'].default_value=800
core.nodes['Coarse flake cells'].inputs['Scale'].default_value=400
core.nodes['Occasional larger glints'].inputs[1].default_value=.80
core.nodes['Dense pearlescent shimmer'].inputs['Roughness'].default_value=.14
core.nodes['Per-facet luster'].inputs['To Min'].default_value=.03
core.nodes['Shimmer coverage'].inputs[2].default_value=.68
lens=bpy.data.objects['FrontLens']
lens_mat=lens.material_slots[0].material.copy();lens_mat.name='SHOT01_ClearProductLens'
for node in lens_mat.node_tree.nodes:
    if node.type=='BSDF_GLASS':node.inputs['Roughness'].default_value=.002
lens.material_slots[0].link='OBJECT';lens.material_slots[0].material=lens_mat

# A smooth vertical studio wall fills the shot. Real off-camera flags create
# the broad diagonal shadows, instead of baking shadow bands into the texture.
for parent in list(bpy.data.collections):
    if parent.library:continue
    for child in list(parent.children):
        if child.name.startswith('Studio_Backdrop'):parent.children.unlink(child)
env=bpy.data.collections.new('SHOT01_STUDIO_WALL');s.collection.children.link(env)
def move_to(obj,collection):
    for old in list(obj.users_collection):old.objects.unlink(obj)
    collection.objects.link(obj)
bpy.ops.mesh.primitive_plane_add(size=2,location=(-.22,0,.20),rotation=(0,math.pi/2,0))
wall=bpy.context.object;wall.name='SHOT01_ColorBackdrop';move_to(wall,env)
wall_mat=bpy.data.materials.new('SHOT01_Coral_to_Olive_Backdrop');wall_mat.use_nodes=True
principled=wall_mat.node_tree.nodes.get('Principled BSDF')
principled.inputs['Roughness'].default_value=.78
principled.inputs['Specular IOR Level'].default_value=.15
for frame,color in [(0,(.30,.095,.068,1)),(29,(.30,.095,.068,1)),
                    (30,(.115,.17,.062,1)),(56,(.115,.17,.062,1))]:
    principled.inputs['Base Color'].default_value=color
    principled.inputs['Base Color'].keyframe_insert('default_value',frame=frame)
for fc in fcurves(wall_mat.node_tree):
    for p in fc.keyframe_points:p.interpolation='CONSTANT'
wall.data.materials.append(wall_mat)
for i,y in enumerate([-.22,-.14,-.06]):
    bpy.ops.mesh.primitive_cube_add(size=1,location=(-.10,y,.20))
    flag=bpy.context.object;flag.name=f'SHOT01_ShadowFlag_{i+1:02d}'
    flag.scale=(.006,.018,.80);flag.rotation_euler.x=math.radians(-14)
    flag.visible_camera=False;flag.visible_glossy=False;flag.visible_transmission=False
    move_to(flag,env)

# SHOT01_LOCAL_LIGHTING: source rig has missing tracking targets. Rebuild the
# three lights locally so their beams follow the raised product center.
for parent in [s.collection]+list(bpy.data.collections):
    if parent.library:continue
    for child in list(parent.children):
        if child.name.startswith('Lights_ThreePoint_Studio'):parent.children.unlink(child)
lights=bpy.data.collections.new('SHOT01_PRODUCT_LIGHTING');s.collection.children.link(lights)
light_target=Vector((center.x,center.y,.160))
for name,position,power,size in [
    ('Key',(.28,-.22,.36),6.5,.09),
    ('Fill',(.30,.24,.19),1,.14),
    ('Rim',(-.10,.10,.28),2.5,.055)]:
    data=bpy.data.lights.new('SHOT01_'+name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    obj=bpy.data.objects.new('SHOT01_'+name,data);lights.objects.link(obj);obj.location=position
    obj.rotation_euler=(light_target-obj.location).to_track_quat('-Z','Y').to_euler()
s.world=s.world.copy();s.world.name='SHOT01_StudioEnvironment'
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.3
# END_SHOT01_LOCAL_LIGHTING

s.frame_start=0;s.frame_end=56;s.render.fps=30;s.name='SHOT01_ReferenceRiseSpin_0_56'
s.render.engine='CYCLES';s.render.use_motion_blur=True;s.render.motion_blur_shutter=.25
s.render.use_persistent_data=False
s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='16';s.render.image_settings.color_mode='RGB'
s.render.filepath='//../renders/shot1_reference_rebuild/production_4k/frame_'
s.cycles.samples=1024;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.002;s.cycles.adaptive_min_samples=64
s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_input_passes='RGB_ALBEDO_NORMAL'
s.cycles.denoising_prefilter='ACCURATE';s.cycles.denoising_quality='HIGH';s.cycles.use_animated_seed=False
for old in list(s.timeline_markers):s.timeline_markers.remove(old)
for label,frame in [('RISE FROM BELOW',0),('RISE APEX',12),('SPIN',24),('SHADE SWITCH',30),('GREEN HERO',38),('DROP OUT',47),('CUT TO LANDING',56)]:
    s.timeline_markers.new(label,frame=frame)

report={'scene':str(DEST),'range':[0,56],'fps':30,'bottle_height_m':height,
        'reference_observations':{'entrance':[1,12],'spin_swap':[26,36],
         'color_cut':30,'original_cut_to_landing':57},
        'authored_adaptation':'Requested downward exit added at f47–56; original reference cuts directly to the landing.',
        'screen_bounds':[]}
for f in range(57):
    s.frame_set(f);dg=bpy.context.evaluated_depsgraph_get()
    pts=[world_to_camera_view(s,camera,o.evaluated_get(dg).matrix_world @ Vector(p))
         for o in visible for p in o.evaluated_get(dg).bound_box]
    report['screen_bounds'].append({'frame':f,'xmin':min(p.x for p in pts),'xmax':max(p.x for p in pts),
          'ymin':min(p.y for p in pts),'ymax':max(p.y for p in pts)})
assert report['screen_bounds'][0]['ymax']<0,report['screen_bounds'][0]
assert report['screen_bounds'][56]['ymax']<0,report['screen_bounds'][56]
assert all(0<r['ymin']<r['ymax']<1 for r in report['screen_bounds'][9:47]),report['screen_bounds'][9:47]
s.frame_set(18)
for obj in list(bpy.context.selected_objects):obj.select_set(False)
for obj in (travel,tilt,spin):obj.select_set(True)
bpy.context.view_layer.objects.active=travel
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
note=bpy.data.texts.new('SHOT01_REFERENCE_README')
note.write('SHOT 1 / 0–56 at30fps\nRise1–12; hold; one rapid revolution26–37; coral-to-green cut30; authored drop47–56.\nDirect editable animation: SHOT01_Travel / SHOT01_Tilt / SHOT01_Spin.\nOriginal clip ends before any exit, so the requested exit is an intentional adaptation.\n')
note.use_fake_user=True
bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
(OUT/'animation_validation.json').write_text(json.dumps(report,indent=2))
print('SHOT1_REFERENCE_READY',str(DEST),flush=True)
