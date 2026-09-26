"""Export the restored bottle with full evaluated detail and minimal closure.

The source asset is never saved. Reimport checks verify geometry and UVs;
the companion blend restores the original Blender materials for rendering.
"""
import bpy
import bmesh
import hashlib
import json
from pathlib import Path
import numpy as np
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / 'assets/products/gel_polish_bottle.blend'
OUT = ROOT / 'assets/products/exports/gel_polish_bottle_detailed'
REVIEW = ROOT / 'renders/detailed_fbx_review'
OUT.mkdir(parents=True, exist_ok=True)
REVIEW.mkdir(parents=True, exist_ok=True)
NAMES = {'Housing':'Bottle_Housing_Gold', 'New_Cap':'Bottle_Cap_Detailed',
         'FrontLens':'Bottle_FrontLens_Glass', 'Lacquer':'Bottle_Lacquer_Pearl'}


def coords(mesh):
    data = np.empty(len(mesh.vertices)*3, dtype=np.float32)
    mesh.vertices.foreach_get('co', data)
    return data.reshape(-1, 3)


def unique_points(points):
    return np.unique(points, axis=0)


def topology(mesh):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    result = {'vertices':len(bm.verts), 'faces':len(bm.faces),
              'boundary_edges':sum(e.is_boundary for e in bm.edges),
              'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
              'loose_vertices':sum(not v.link_faces for v in bm.verts),
              'degenerate_faces':sum(f.calc_area()<1e-18 for f in bm.faces),
              'signed_volume_m3':bm.calc_volume(signed=True)}
    bm.free()
    return result


def close_mesh(mesh):
    """Separate ambiguous neck seams and cap openings without moving vertices."""
    bm = bmesh.new()
    bm.from_mesh(mesh)
    # Store evaluated corner normals so boundary repairs don't soften details.
    layer = bm.loops.layers.float_vector.new('original_render_normal')
    bm.faces.ensure_lookup_table()
    for face, poly in zip(bm.faces, mesh.polygons):
        for loop, index in zip(face.loops, poly.loop_indices):
            loop[layer] = mesh.corner_normals[index].vector
    branches = [e for e in bm.edges if len(e.link_faces)>2]
    if branches:
        bmesh.ops.split_edges(bm, edges=branches)
    boundary = [e for e in bm.edges if e.is_boundary]
    caps = bmesh.ops.holes_fill(bm, edges=boundary, sides=0).get('faces', []) if boundary else []
    for face in caps:
        face.smooth = False
    bm.normal_update()
    # Recalculate face winding for a well-defined interior; retained corner
    # normals keep the original visible shading, including the pearl surface.
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    for face in caps:
        for loop in face.loops:
            loop[layer] = face.normal
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    normals = [tuple(loop[layer]) for face in bm.faces for loop in face.loops]
    bm.to_mesh(mesh)
    bm.free()
    mesh.normals_split_custom_set(normals)
    mesh.update()
    check = topology(mesh)
    assert check['nonmanifold_edges']==0 and check['loose_vertices']==0, check
    assert check['signed_volume_m3']>0, check
    return {'split_branch_edges':len(branches), 'capped_openings':len(caps), 'topology':check}


def setup_review(scene, objects):
    scene.render.engine='CYCLES'
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='OPTIX'
    prefs.get_devices()
    for device in prefs.devices:
        device.use=device.type=='OPTIX'
    scene.cycles.device='GPU'
    scene.cycles.samples=128
    scene.cycles.use_denoising=True
    scene.render.resolution_x=1200
    scene.render.resolution_y=1500
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.render.image_settings.color_mode='RGB'
    world=bpy.data.worlds.new('Detailed_Review_World')
    world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.16,0.18,0.22,1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
    scene.world=world
    points=np.concatenate([coords(o.data) for o in objects])
    low=points.min(axis=0);high=points.max(axis=0)
    center=Vector((low+high)*.5)
    for name,offset,power,size,size_y in [
        ('Key',(.11,-.10,.07),7,.055,.17),('Fill',(.12,.11,.025),4,.07,.13),
        ('Rim',(-.08,.07,.09),9,.055,.15),('Back',(-.12,-.11,.015),6,.09,.17),
        ('Top',(.01,0,.15),3,.08,.08)]:
        data=bpy.data.lights.new('Review_'+name,'AREA')
        data.energy=power;data.shape='RECTANGLE';data.size=size;data.size_y=size_y
        light=bpy.data.objects.new(data.name,data);scene.collection.objects.link(light)
        light.location=center+Vector(offset)
        light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
    camera_data=bpy.data.cameras.new('Detailed_Bottle_Camera')
    camera=bpy.data.objects.new(camera_data.name,camera_data)
    scene.collection.objects.link(camera);scene.camera=camera
    camera_data.type='ORTHO';camera_data.ortho_scale=float(high[2]-low[2])*1.24
    camera_data.clip_start=.001
    return center


def render_views(scene, center, prefix):
    for label,offset in [('front',(.24,-.045,.035)),('back',(-.24,.045,.035))]:
        camera=scene.camera;camera.location=center+Vector(offset)
        camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(REVIEW/f'{prefix}_{label}.png')
        bpy.ops.render.render(write_still=True)
        print('DETAIL_RENDERED',prefix,label,flush=True)


def main():
    source_hash=hashlib.sha256(ASSET.read_bytes()).hexdigest()
    fbx=OUT/'gel_polish_bottle_detailed.fbx'
    assert not fbx.exists(), 'Preserve previous package; choose a new version.'
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    source_scene=bpy.context.scene
    frame=source_scene.frame_current
    inverse=bpy.data.objects['Housing'].matrix_world.inverted()
    report={'source_asset':str(ASSET.relative_to(ROOT)), 'source_sha256':source_hash,
            'source_frame':frame,'units':'metres','coordinate_space':'Housing mesh local',
            'fbx_axis_up':'Y','fbx_axis_forward':'-Z', 'parts':{},
            'liquigen_host_import_verified':False,
            'blender_shader_restoration_required_for_exact_render':True}
    original_material_names={}
    objects=[]
    for source_name, export_name in NAMES.items():
        source=bpy.data.objects[source_name]
        for mod in source.modifiers:
            mod.show_viewport=mod.show_render
            if mod.type=='SUBSURF':mod.levels=mod.render_levels
        bpy.context.view_layer.update()
        dg=bpy.context.evaluated_depsgraph_get()
        evaluated=source.evaluated_get(dg)
        mesh=bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=dg)
        mesh.transform(inverse@source.matrix_world)
        initial=unique_points(coords(mesh))
        before=topology(mesh)
        closure=close_mesh(mesh)
        assert np.array_equal(initial,unique_points(coords(mesh))), 'Surface vertices changed'
        ob=bpy.data.objects.new(export_name,mesh)
        objects.append(ob)
        original_material_names[export_name]=[slot.material.name if slot.material else None for slot in source.material_slots]
        report['parts'][export_name]={'source_object':source_name,'original_topology':before,
                                     **closure,'surface_vertex_positions_unchanged':True,
                                     'materials':original_material_names[export_name]}
        print('DETAIL_CLOSED',export_name,json.dumps(closure),flush=True)
    # Keep the original shader networks locally for exact Blender final renders.
    materials={bpy.data.materials[name] for names in original_material_names.values() for name in names if name}
    shader_library=REVIEW/'original_materials.blend'
    bpy.data.libraries.write(str(shader_library),materials,path_remap='ABSOLUTE',fake_user=True,compress=True)
    scene=bpy.data.scenes.new('Detailed_Bottle_FBX')
    scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    scene.frame_set(frame)
    for ob in objects:scene.collection.objects.link(ob)
    bpy.context.window.scene=scene
    for ob in objects:ob.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    expected={o.name:coords(o.data).copy() for o in objects}
    expected_uv={}
    for ob in objects:
        expected_uv[ob.name]=[]
        for uv in ob.data.uv_layers:
            data=np.empty(len(uv.data)*2,dtype=np.float32);uv.data.foreach_get('uv',data)
            expected_uv[ob.name].append((uv.name,data))
    bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},
                            apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',global_scale=1,
                            axis_forward='-Z',axis_up='Y',bake_space_transform=False,
                            use_mesh_modifiers=False,use_triangles=True,bake_anim=False,
                            add_leaf_bones=False,path_mode='COPY',embed_textures=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(fbx))
    imported=[o for o in bpy.context.scene.objects if o.type=='MESH']
    assert set(o.name for o in imported)==set(expected)
    for ob in imported:
        actual=coords(ob.data)
        # Axis conversions are stored as object transforms, so compare world space.
        matrix=np.array(ob.matrix_world,dtype=np.float64)
        actual=actual @ matrix[:3,:3].T + matrix[:3,3]
        assert actual.shape==expected[ob.name].shape
        error=float(np.max(np.linalg.norm(actual-expected[ob.name],axis=1)))
        assert error<1e-7,(ob.name,error)
        checks=topology(ob.data);assert checks['nonmanifold_edges']==0,checks
        report['parts'][ob.name]['fbx_reimport_max_vertex_error_m']=error
        report['parts'][ob.name]['reimport_topology']=checks
        uv_errors=[]
        for (name,uv_before),uv in zip(expected_uv[ob.name],ob.data.uv_layers):
            data=np.empty(len(uv.data)*2,dtype=np.float32);uv.data.foreach_get('uv',data)
            assert data.shape==uv_before.shape
            uv_errors.append(float(np.max(np.abs(data-uv_before))))
        assert len(expected_uv[ob.name])==len(ob.data.uv_layers)
        assert all(e<1e-6 for e in uv_errors),uv_errors
        report['parts'][ob.name]['uv_max_errors']=uv_errors
    # Load original shaders under distinct names; record this restoration explicitly.
    for material in list(bpy.data.materials):material.name='FBX_Basic_'+material.name
    needed=sorted({n for names in original_material_names.values() for n in names if n})
    with bpy.data.libraries.load(str(shader_library),link=False) as (available,loaded):
        loaded.materials=needed
    for ob in imported:
        ob.data.materials.clear()
        for name in original_material_names[ob.name]:
            ob.data.materials.append(bpy.data.materials[name] if name else None)
    scene=bpy.context.scene;scene.name='Detailed_Bottle_Original_Materials';scene.frame_set(frame)
    center=setup_review(scene,imported)
    render_views(scene,center,'fbx_original_materials')
    camera=scene.camera;camera.location=center+Vector((.24,-.045,.035))
    camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'gel_polish_bottle_detailed.blend'))
    assert hashlib.sha256(ASSET.read_bytes()).hexdigest()==source_hash
    report['source_unchanged']=True
    report['fbx_file']=str(fbx.relative_to(ROOT))
    report['fbx_bytes']=fbx.stat().st_size
    report['preview_provenance']='Reimported FBX meshes rendered in Cycles with the original Blender materials explicitly restored.'
    (OUT/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('DETAILED_FBX_VERIFIED',flush=True)


if __name__=='__main__':main()
