"""Derive a stitched leather board with fine magnetic lacquer pigment.

Rebuilds from the user-sized, stand-free source board. The logo and magnetic
materials are prepared in memory, so no cat-eye intermediate .blend is needed.
Only writes the stitched asset and its reviews; does not touch any shot scene.
"""
import json
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'assets/props/brand_collection_sample_board.blend'
DEST = ROOT / 'assets/props/brand_collection_sample_board_stitched.blend'
QA = ROOT / 'renders/shot5_sample_board_stitched'
QA.mkdir(parents=True, exist_ok=True)
runpy.run_path(str(ROOT / 'scripts/refine_shot5_sample_board.py'),
               init_globals={'BUILD_FOR_STITCHED': True})
scene = bpy.context.scene
col = bpy.data.collections['Prop_BrandCollection_SampleBoard_CatEye']
col.name = 'Prop_BrandCollection_SampleBoard_Stitched'
source_objects = list(col.objects)
source_matrices = {o.name: [list(row) for row in o.matrix_world] for o in col.objects}

def bounds(objects):
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    points = [obj.evaluated_get(deps).matrix_world @ Vector(p)
              for obj in objects for p in obj.evaluated_get(deps).bound_box]
    return [[min(p[i] for p in points) for i in range(3)],
            [max(p[i] for p in points) for i in range(3)]]

original_bounds = bounds(source_objects)

def simple_material(name, color, roughness):
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    p = mat.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = roughness
    return mat

# Real stitch geometry follows an inset rounded rectangle, respecting the user's
# enlarged backing mesh. The front surface is -Y and the rear remains unchanged.
backing = bpy.data.objects['SampleBoard_RoundedWhiteBacking']
bb = bounds([backing])
front_y = backing.matrix_world @ Vector((0, -.0016, 0))
front_y = front_y.y
edge_inset = .0027
left, right = bb[0][0] + edge_inset, bb[1][0] - edge_inset
bottom, top = bb[0][2] + edge_inset, bb[1][2] - edge_inset
radius = .0206 - edge_inset
path = []
for cx, cz, start in [(right-radius, top-radius, 0), (left+radius, top-radius, 90),
                      (left+radius, bottom+radius, 180), (right-radius, bottom+radius, 270)]:
    for k in range(65):
        angle = math.radians(start + k * 90 / 64)
        path.append(Vector((cx+radius*math.cos(angle), cz+radius*math.sin(angle))))
distances = [0.0]
for a, b in zip(path, path[1:] + path[:1]): distances.append(distances[-1]+(b-a).length)
perimeter = distances[-1]
stitch_count = round(perimeter / .00195)
pitch = perimeter / stitch_count

def at_distance(distance):
    distance %= perimeter
    for j in range(len(path)):
        if distances[j+1] >= distance:
            f=(distance-distances[j])/(distances[j+1]-distances[j])
            return path[j].lerp(path[(j+1)%len(path)], f)
    return path[0]

thread_verts, thread_faces, hole_verts, hole_faces = [], [], [], []
thread_radius = .000082
stitch_length = .00120
for stitch in range(stitch_count):
    start = stitch*pitch
    centers=[]
    # The thread disappears into both punctures, with a very slight crown.
    for step in range(7):
        t=step/6
        q=at_distance(start+(t-.5)*stitch_length)
        y=front_y - .000025 - .000062*math.sin(math.pi*t)
        centers.append(Vector((q.x,y,q.y)))
    offset=len(thread_verts)
    for j,p in enumerate(centers):
        tangent=(centers[min(j+1,6)]-centers[max(j-1,0)]).normalized()
        side=Vector((tangent.z,0,-tangent.x)).normalized()
        up=tangent.cross(side).normalized()
        for k in range(8):
            a=2*math.pi*k/8
            thread_verts.append(tuple(p+thread_radius*(side*math.cos(a)+up*math.sin(a))))
    for j in range(6):
        for k in range(8):
            a=offset+j*8+k;b=offset+j*8+(k+1)%8
            thread_faces.append((a,b,b+8,a+8))
    thread_faces += [tuple(offset+i for i in reversed(range(8))),
                     tuple(offset+6*8+i for i in range(8))]
    for d in (start-stitch_length*.5, start+stitch_length*.5):
        q=at_distance(d);tangent=(at_distance(d+.00003)-at_distance(d-.00003)).normalized()
        side=Vector((-tangent.y,tangent.x))
        offset=len(hole_verts)
        hole_verts.append((q.x,front_y-.000028,q.y))
        for k in range(12):
            a=2*math.pi*k/12
            p=q+tangent*(.00013*math.cos(a))+side*(.000104*math.sin(a))
            hole_verts.append((p.x,front_y-.000031,p.y))
        for k in range(12): hole_faces.append((offset,offset+1+k,offset+1+(k+1)%12))

def mesh_object(name, vertices, faces, material, smooth=True):
    mesh=bpy.data.meshes.new(name+'_Mesh');mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);col.objects.link(obj);mesh.materials.append(material)
    for p in mesh.polygons:p.use_smooth=smooth
    return obj

thread_mat=simple_material('BOARD_WarmGreyFineThread',(.35,.325,.29),.68)
thread=mesh_object('SampleBoard_OuterBorder_StitchedThreads',thread_verts,thread_faces,thread_mat)
thread['stitch_count']=stitch_count;thread['pitch_mm']=pitch*1000;thread['thread_diameter_mm']=thread_radius*2000
hole_mat=simple_material('BOARD_SubtleNeedlePunctures',(.19,.175,.16),.83)
holes=mesh_object('SampleBoard_OuterBorder_NeedlePunctures',hole_verts,hole_faces,hole_mat,False)
holes['purpose']='Small puncture shadows at thread entry and exit; no geometric change to backing outline'

# Only the outer rectangular cover gets leather grain. The central printed
# quatrefoil and mounted tips remain independent materials.
leather=bpy.data.materials.new('BOARD_PearlWhiteFineLeather');leather.use_nodes=True
nt=leather.node_tree;n=nt.nodes.new;link=nt.links.new
nt.nodes.clear()
tc=n('ShaderNodeTexCoord');tc.location=(-1000,0)
physical=n('ShaderNodeVectorMath');physical.operation='SCALE';physical.inputs['Scale'].default_value=2.06
physical.name='Physical leather coordinates in metres';link(tc.outputs['Object'],physical.inputs[0]);physical.location=(-820,0)
sep=n('ShaderNodeSeparateXYZ');link(physical.outputs[0],sep.inputs[0]);sep.location=(-640,0)
plane=n('ShaderNodeCombineXYZ');link(sep.outputs['X'],plane.inputs['X']);link(sep.outputs['Z'],plane.inputs['Y']);plane.location=(-460,0)
cells=n('ShaderNodeTexVoronoi');cells.name='Fine irregular leather pebbles';cells.voronoi_dimensions='2D';cells.feature='SMOOTH_F1';cells.inputs['Smoothness'].default_value=.24;cells.inputs['Scale'].default_value=3100
link(plane.outputs[0],cells.inputs['Vector']);cells.location=(-240,180)
height=n('ShaderNodeMapRange');height.name='Soft pebble depressions';height.interpolation_type='SMOOTHSTEP';height.clamp=True
height.inputs['From Min'].default_value=.12;height.inputs['From Max'].default_value=.64
height.inputs['To Min'].default_value=1;height.inputs['To Max'].default_value=0
link(cells.outputs['Distance'],height.inputs['Value']);height.location=(-30,180)
micro=n('ShaderNodeTexNoise');micro.name='Leather microscopic pores';micro.inputs['Scale'].default_value=14000;micro.inputs['Detail'].default_value=2
link(physical.outputs[0],micro.inputs['Vector']);micro.location=(-250,-220)
microbump=n('ShaderNodeBump');microbump.inputs['Strength'].default_value=.13;microbump.inputs['Distance'].default_value=.000014
link(micro.outputs['Fac'],microbump.inputs['Height']);microbump.location=(0,-200)
bump=n('ShaderNodeBump');bump.name='Soft pebbled leather relief';bump.inputs['Strength'].default_value=.55;bump.inputs['Distance'].default_value=.000080
link(height.outputs[0],bump.inputs['Height']);link(microbump.outputs['Normal'],bump.inputs['Normal']);bump.location=(200,100)
rough=n('ShaderNodeMapRange');rough.inputs['To Min'].default_value=.43;rough.inputs['To Max'].default_value=.57
link(micro.outputs['Fac'],rough.inputs['Value']);rough.location=(200,-230)
p=n('ShaderNodeBsdfPrincipled');p.inputs['Base Color'].default_value=(.74,.724,.70,1)
p.inputs['Sheen Weight'].default_value=.16;link(rough.outputs[0],p.inputs['Roughness']);link(bump.outputs['Normal'],p.inputs['Normal']);p.location=(450,80)
out=n('ShaderNodeOutputMaterial');link(p.outputs[0],out.inputs['Surface']);out.location=(750,80)
leather['grain_cell_spacing_mm']=1000/3100
leather['relief_micrometres']=80
backing.data.materials.clear();backing.data.materials.append(leather)

# Keep the view-responsive magnetic bands, add the approved bottle's fine pearl
# facet mechanism, and avoid its separate coarse-glint layer on these tiny tips.
# Existing UVs are 14.5 units per original metre; multiply by user enlargement to
# retain 800 * 14.5 = 11,600 pigment cells per physical metre (~86 micrometres).
updated_mats=[]
for mat in bpy.data.materials:
    if not mat.name.startswith('BOARD_Magnetic_'):continue
    mat.name=mat.name.replace('BOARD_Magnetic_','BOARD_GrainedCatEye_')
    nt=mat.node_tree;n=nt.nodes.new;link=nt.links.new
    tc=nt.nodes['Object-locked nail coordinates']
    old=nt.nodes['Magnetic lacquer under clear topcoat']
    old.inputs['Metallic'].default_value=.34
    old.inputs['Roughness'].default_value=.30
    old.inputs['Anisotropic'].default_value=.14
    old.inputs['Coat Weight'].default_value=.20
    old.inputs['Coat Roughness'].default_value=.17
    pigment_color=nt.nodes['Pigment aligned by magnetic field']
    old_base=pigment_color.inputs[1].default_value[:]
    pigment_color.inputs[1].default_value=(*(v*.64 for v in old_base[:3]),1)
    nt.nodes['Fine pigment modulation'].inputs[1].default_value=.70
    nt.nodes['Micro contrast'].inputs[1].default_value=.52
    physical=n('ShaderNodeVectorMath');physical.name='User enlargement physical UV correction';physical.operation='SCALE';physical.inputs['Scale'].default_value=2.06
    link(tc.outputs['UV'],physical.inputs[0])
    fine=n('ShaderNodeTexVoronoi');fine.name='Fine bottle-matched pigment facets';fine.voronoi_dimensions='2D';fine.feature='F1';fine.inputs['Scale'].default_value=800
    link(physical.outputs[0],fine.inputs['Vector'])
    sep=n('ShaderNodeSeparateColor');sep.mode='RGB';link(fine.outputs['Color'],sep.inputs[0])
    orient=n('ShaderNodeVectorMath');orient.operation='SCALE';orient.inputs['Scale'].default_value=.65;link(fine.outputs['Color'],orient.inputs[0])
    center=n('ShaderNodeVectorMath');center.operation='ADD';center.inputs[1].default_value=(.175,.175,.85);link(orient.outputs[0],center.inputs[0])
    normal=n('ShaderNodeNormalMap');normal.name='UV-locked microscopic facet orientations';normal.space='TANGENT';normal.inputs['Strength'].default_value=.75;link(center.outputs[0],normal.inputs['Color'])
    tint=n('ShaderNodeMixRGB');tint.name='Magnetically concentrated colored pigment';tint.inputs[0].default_value=.012;tint.inputs[2].default_value=(.72,.76,.80,1)
    link(pigment_color.outputs[0],tint.inputs[1])
    brightness=n('ShaderNodeMapRange');brightness.name='Fine pigment luster variation';brightness.inputs['To Min'].default_value=.018;brightness.inputs['To Max'].default_value=.85
    link(sep.outputs['Blue'],brightness.inputs['Value'])
    color=n('ShaderNodeVectorMath');color.operation='SCALE';link(tint.outputs[0],color.inputs[0]);link(brightness.outputs[0],color.inputs['Scale'])
    flakes=n('ShaderNodeBsdfPrincipled');flakes.name='Fine reflective pigment beneath topcoat';flakes.inputs['Metallic'].default_value=1.0;flakes.inputs['Roughness'].default_value=.23
    flakes.inputs['Coat Weight'].default_value=.04;flakes.inputs['Coat Roughness'].default_value=.20
    link(color.outputs[0],flakes.inputs['Base Color']);link(normal.outputs[0],flakes.inputs['Normal'])
    weight=n('ShaderNodeMath');weight.name='Pigment is strongest inside magnetic band';weight.operation='MULTIPLY_ADD';weight.inputs[1].default_value=.50;weight.inputs[2].default_value=.24;weight.use_clamp=True
    link(nt.nodes['Magnetic band plus halo'].outputs[0],weight.inputs[0])
    mix=n('ShaderNodeMixShader');mix.name='Fine grain over magnetic cat-eye';link(weight.outputs[0],mix.inputs[0]);link(old.outputs[0],mix.inputs[1]);link(flakes.outputs[0],mix.inputs[2])
    output=next(o for o in nt.nodes if o.type=='OUTPUT_MATERIAL');link(mix.outputs[0],output.inputs['Surface'])
    # Keep every layer inspectable in the node editor.
    for index,node in enumerate(nt.nodes):node.location=((index%8)*230,-(index//8)*250)
    mat['finish']='Fine UV-locked pigment facets over a view-responsive magnetic band; no coarse glitter and no emission'
    mat['physical_cells_per_metre']=11600
    mat['approx_cells_across_tip']=79
    mat['physical_pigment_spacing_micrometres']=1e6/11600
    mat['algorithm_source']='Approved Shot4 FineShimmer: 800-cell Voronoi orientations, per-facet luster; coarse glints omitted'
    updated_mats.append(mat.name)

for obj in source_objects:
    assert max(abs(a-b) for rows in zip(source_matrices[obj.name],obj.matrix_world) for a,b in zip(*rows))<1e-8
assert len(updated_mats)==72
final_bounds=bounds(col.objects)
assert max(abs(a-b) for rows in zip(original_bounds,final_bounds) for a,b in zip(*rows))<.000001
col['object_count']=len(col.objects)
col['stitch_count']=stitch_count
col['outer_finish']='Fine pebbled pearl-white leather with warm-grey stitched perimeter'
col['finish_revision']='Fine physical pigment facets preserve focused and velvet magnetic bands'
col.asset_data.description='Stand-free Hang Pure collection board: pearl border, leather cover, sewn edge, and 36 paired finely pigmented cat-eye shades.'
scene.name='BrandCollection_SampleBoard_Stitched'
report={'source':str(SOURCE),'asset':str(DEST),'collection':col.name,'objects':len(col.objects),
        'nail_count':72,'shade_count':36,'original_object_transforms_unchanged':True,
        'original_bounds':original_bounds,'final_bounds':final_bounds,
        'stitches':stitch_count,'pitch_mm':pitch*1000,'thread_diameter_mm':thread_radius*2000,
        'physical_pigment_spacing_micrometres':1e6/11600,'materials_refined':len(updated_mats),
        'center_panel_unchanged':True,'logo_unchanged':True,'coarse_glitter_layer':False,'emission':False}
(QA/'asset_report.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
print('STITCHED_BOARD_READY',json.dumps(report),flush=True)

# Isolated studio reviews are deliberately not saved into the asset file.
for obj in list(scene.objects):
    if obj.name not in col.all_objects:bpy.data.objects.remove(obj,do_unlink=True)
world=bpy.data.worlds.new('StitchedBoardReviewWorld');world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.57,.60,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.35;scene.world=world
bpy.ops.object.camera_add(location=(0,-.65,.151));cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,.151))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.32;scene.camera=cam
for i,(pos,energy,size) in enumerate([((-.20,-.23,.37),13,.18),((.22,-.11,.23),4,.16),((0,.12,.35),7,.12)]):
    bpy.ops.object.light_add(type='AREA',location=pos);obj=bpy.context.object;obj.name='ReviewLight%d'%i;obj.data.energy=energy;obj.data.shape='DISK';obj.data.size=size
    obj.rotation_euler=(Vector((0,0,.151))-obj.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES';scene.cycles.samples=256;scene.cycles.use_denoising=True
scene.cycles.denoising_input_passes='RGB_ALBEDO_NORMAL'
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for device in prefs.devices:device.use=device.type=='OPTIX'
    scene.cycles.device='GPU'
except Exception:pass
scene.view_settings.view_transform='AgX'
scene.render.resolution_x=2400;scene.render.resolution_y=2000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(QA/'board_review.png');bpy.ops.render.render(write_still=True)
cam.location=(0,-.65,.161);cam.rotation_euler=(Vector((0,0,.161))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.12
scene.render.resolution_x=1800;scene.render.resolution_y=1300;scene.render.filepath=str(QA/'pigment_closeup.png');bpy.ops.render.render(write_still=True)
cam.location=(-.112,-.65,.238);cam.rotation_euler=(Vector((-.112,0,.238))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.060
scene.render.resolution_x=1600;scene.render.resolution_y=1300;scene.render.filepath=str(QA/'leather_stitch_closeup.png');bpy.ops.render.render(write_still=True)
print('STITCHED_BOARD_REVIEW_COMPLETE',flush=True)
