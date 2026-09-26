"""Reusable manicure props for the final hero shot; run in background Blender.

Preserves the approved product and all shot files. Scene scale is metres.
Collections have their logical origin at the base, front faces toward -Y.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'assets/props/manicure_finale_props.blend'
QA = ROOT / 'renders/shot5_polish_finale_v001'
SOURCE = ROOT / 'scenes/gel_polish_lapohka_shot4_285_375_bottle_array_v004_fine_shimmer.blend'
DEST.parent.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = 'ManicureFinale_ReusableAssets'
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1

shades = ['Aubergine', 'PetrolTeal', 'PearlIvory', 'Raspberry', 'MidnightBlue']
with bpy.data.libraries.load(str(SOURCE), link=False) as (src, dst):
    dst.materials = ['SHOT04_Lacquer_' + name for name in shades]
lacquers = dict(zip(shades, dst.materials))
for label, mat in lacquers.items():
    assert mat, label
    mat.name = 'PROP_Lacquer_' + label
    mat.animation_data_clear()
    mat.node_tree.animation_data_clear()
    mat['source_finish'] = 'Approved Shot 4 v004 fine shimmer; UV physical density retained'
    for node in mat.node_tree.nodes:
        if node.type == 'TEX_COORD':
            node.object = None

def principled(name, color, metallic=0, roughness=.3, transmission=0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    p = mat.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    p.inputs['Transmission Weight'].default_value = transmission
    p.inputs['IOR'].default_value = 1.49
    return mat

gold = principled('PROP_ChampagneGold', (.58, .34, .13), 1, .22)
charcoal = principled('PROP_Magnet_SatinCharcoal', (.009, .012, .015), .15, .31)
steel = principled('PROP_Magnet_BrushedSteel', (.24, .27, .29), 1, .3)
acrylic = principled('PROP_ClearAcrylic', (.97, .99, 1), 0, .035, 1)
ceramic = principled('PROP_IvorySatinCeramic', (.59, .555, .49), 0, .28)
cn = ceramic.node_tree.nodes
noise = cn.new('ShaderNodeTexNoise'); noise.name = 'Subtle ceramic microtexture'
noise.inputs['Scale'].default_value = 1300
noise.inputs['Detail'].default_value = 2
bump = cn.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = .10
bump.inputs['Distance'].default_value = .000012
ceramic.node_tree.links.new(noise.outputs['Fac'], bump.inputs['Height'])
ceramic.node_tree.links.new(bump.outputs['Normal'], cn['Principled BSDF'].inputs['Normal'])

def collection(name, description):
    col = bpy.data.collections.new(name)
    scene.collection.children.link(col)
    col.asset_mark()
    col.asset_data.description = description
    col['units'] = 'metres'
    col['orientation'] = 'Front -Y, up +Z, collection origin at floor'
    return col

fan = collection('Prop_NailSwatchFan', 'Five fine-shimmer nail swatches on clear stems, champagne ring and acrylic standing support')
wand = collection('Prop_CatEyeMagnetWand', 'Satin charcoal magnetic nail-art wand, brushed steel head and gold collar; 85 mm long')
teal = collection('Prop_LooseTip_Teal', 'Petrol teal polished convex nail display tip; 28 by 11 mm')
raspberry = collection('Prop_LooseTip_Raspberry', 'Raspberry polished convex nail display tip; 28 by 11 mm')
podium = collection('Stage_CeramicPodium', 'Ivory satin ceramic circular hero platform, radius 160 mm, height 50 mm')
brushes = collection('Prop_ManicureBrushHolder', 'Fluted rose-smoke glass holder with three fine nail-art brushes; 125 mm high')

def move_to(obj, col):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    col.objects.link(obj)

def finish(obj, name, col, mat, bevel=0):
    obj.name = name
    move_to(obj, col)
    obj.data.materials.append(mat)
    if bevel:
        b = obj.modifiers.new('Soft manufactured edges', 'BEVEL')
        b.width = bevel; b.segments = 4
        b.limit_method = 'ANGLE'
        b.harden_normals = True
        wn = obj.modifiers.new('Manufactured surface normals', 'WEIGHTED_NORMAL')
        wn.keep_sharp = True
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj

def cube(name, col, mat, location, size, bevel):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object; obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, col, mat, bevel)

def cylinder(name, col, mat, location, radius, depth, bevel=.00025):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=radius, depth=depth, location=location)
    return finish(bpy.context.object, name, col, mat, bevel)

def torus(name, col, mat, center, major, minor, rotation):
    bpy.ops.mesh.primitive_torus_add(major_segments=96, minor_segments=16,
        location=center, rotation=rotation, major_radius=major, minor_radius=minor)
    return finish(bpy.context.object, name, col, mat)

def nail(name, col, mat, length=.028, width=.011):
    # Closed convex shell: generous polished front, almost-flat clear underside.
    # Physical planar UVs make pigment flakes identical in scale to the bottle.
    segs, rings = 80, 48
    verts = [(0, 0, length/2)]
    for j in range(1, rings):
        theta = math.pi*j/rings
        z = length/2*math.cos(theta)
        taper = .94 - .10*(z/(length/2))
        for i in range(segs):
            phi = 2*math.pi*i/segs
            x = width/2*math.sin(theta)*math.cos(phi)*taper
            sy = math.sin(phi)
            y = (-.00245 if sy >= 0 else -.00045)*math.sin(theta)*sy
            verts.append((x, y, z))
    verts.append((0, 0, -length/2))
    faces = []
    for i in range(segs):
        faces.append((0, 1+i, 1+(i+1)%segs))
    for j in range(rings-2):
        a, b = 1+j*segs, 1+(j+1)*segs
        for i in range(segs):
            ni=(i+1)%segs
            faces.append((a+i, b+i, b+ni, a+ni))
    last=1+(rings-2)*segs
    for i in range(segs):
        faces.append((last+i, len(verts)-1, last+(i+1)%segs))
    mesh = bpy.data.meshes.new(name+'_Mesh')
    mesh.from_pydata(verts, [], [tuple(reversed(f)) for f in faces]); mesh.update()
    obj = bpy.data.objects.new(name, mesh); col.objects.link(obj)
    mesh.materials.append(mat)
    uv = mesh.uv_layers.new(name='UVMap')
    for poly in mesh.polygons:
        poly.use_smooth = True
        for idx in poly.loop_indices:
            co = mesh.vertices[mesh.loops[idx].vertex_index].co
            uv.data[idx].uv = (.5+co.x*14.5, .5+co.z*14.5)
    obj['lacquer_uv_units_per_metre'] = 14.5
    obj['manufactured_dimensions_mm'] = [width*1000, length*1000, 2.9]
    return obj

# Five swatches are supported physically by a rear acrylic cradle and base.
cube('SwatchStand_AcrylicBase', fan, acrylic, (0,.007,.0045), (.056,.026,.009), .002)
cube('SwatchStand_RearSupport', fan, acrylic, (0,.007,.018), (.014,.007,.030), .0015)
torus('SwatchFan_GoldSplitRing', fan, gold, (0,-.001,.017), .0057,.00062,(math.pi/2,0,0))
pin = cylinder('SwatchFan_GoldPivotPin', fan, gold, (0,.001,.017), .0012,.010)
pin.rotation_euler.x = math.pi/2
for i, (label, angle) in enumerate(zip(shades, [-31,-15.5,0,15.5,31])):
    rot = Matrix.Rotation(math.radians(angle), 4, 'Y')
    trans = Matrix.Translation((0, .0015+i*.00015, .017))
    stem = cube('SwatchStem_'+label, fan, acrylic, (0,0,.027), (.0038,.00125,.059), .001)
    # The end encircles the shared pivot; its round hole is genuine geometry.
    bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=.0013, depth=.008,
        location=(0,0,0), rotation=(math.pi/2,0,0))
    cut=bpy.context.object; cut.name='TEMP_PivotHole'
    mod=stem.modifiers.new('Pivot hole','BOOLEAN'); mod.operation='DIFFERENCE'; mod.object=cut
    bpy.context.view_layer.objects.active=stem
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cut,do_unlink=True)
    stem.matrix_world=trans@rot@stem.matrix_world
    tip=nail('NailSwatch_'+label,fan,lacquers[label])
    tip.matrix_world=trans@rot@Matrix.Translation((0,-.001,.071))

# Magnet tool is low and lies along X. Slight bevels retain clean catchlights.
cube('MagnetWand_CharcoalHandle',wand,charcoal,(-.0085,0,.003),(.064,.0065,.006),.0021)
cube('MagnetWand_GoldCollar',wand,gold,(.0240,0,.003),(.0035,.0068,.0062),.00055)
cube('MagnetWand_SteelHead',wand,steel,(.0335,0,.003),(.015,.0075,.0045),.00065)
# Thin etched join, modeled rather than a decal.
cube('MagnetWand_HeadInset',wand,charcoal,(.034,0,.00527),(.011,.0004,.00012),.00005)
cube('MagnetWand_EndCap',wand,gold,(-.042,0,.003),(.003,.0061,.0056),.0012)
for ob in wand.objects:
    ob.location.z += .0001

# Two independently placeable foreground samples, polished surfaces face up.
for col, label in [(teal,'PetrolTeal'),(raspberry,'Raspberry')]:
    tip=nail('LoosePolishTip_'+label,col,lacquers[label])
    tip.matrix_world=Matrix.Translation((0,0,.00046))@Matrix.Rotation(-math.pi/2,4,'X')

cylinder('CeramicPodium',podium,ceramic,(0,0,.025),.16,.050,.003)

# A genuinely hollow fluted glass vessel, with three distinct manicure brushes.
rose_glass = principled('PROP_RoseSmokeGlass',(.62,.37,.32),0,.10,1)
rose_glass.node_tree.nodes['Principled BSDF'].inputs['IOR'].default_value=1.46
bristle = principled('PROP_NailBrush_Bristles',(.065,.026,.010),0,.38)
verts=[];faces=[];segments=192
profile=[(.018,0),(.021,.002),(.021,.063),(.0207,.065),(.0188,.065),(.0185,.063),(.0185,.004)]
for radius,z in profile:
    for i in range(segments):
        a=2*math.pi*i/segments
        r=radius+(.00045*math.cos(a*48) if radius>.02 else 0)
        verts.append((r*math.cos(a),r*math.sin(a),z))
for j in range(len(profile)-1):
    for i in range(segments):
        a=j*segments+i;b=j*segments+(i+1)%segments
        faces.append((a,b,b+segments,a+segments))
# The inner floor and outer underside meet single center vertices. Repeated
# zero-radius rings create degenerate faces and leave the underside open.
inner_center=len(verts);verts.append((0,0,.004))
outer_center=len(verts);verts.append((0,0,0))
inner_ring=(len(profile)-1)*segments
for i in range(segments):
    nxt=(i+1)%segments
    faces.append((inner_center,inner_ring+i,inner_ring+nxt))
    faces.append((outer_center,nxt,i))
me=bpy.data.meshes.new('ManicureCup_MESH');me.from_pydata(verts,[],faces);me.update()
ob=bpy.data.objects.new('ManicureCup_FlutedGlass',me);brushes.objects.link(ob);me.materials.append(rose_glass)
for p in me.polygons:p.use_smooth=True
torus('ManicureCup_GoldFoot',brushes,gold,(0,0,.003),.0204,.0006,(0,0,0))
for i,(x,y,height,lean) in enumerate([(-.009,0,.118,-9),(0,.003,.128,0),(.009,-.002,.110,10)]):
    transform=Matrix.Translation((x,y,.006))@Matrix.Rotation(math.radians(lean),4,'Y')
    handle=cylinder('NailBrush_Handle_'+str(i),brushes,charcoal,(0,0,(height-.026)/2),.0018,height-.026,.0003)
    ferrule=cylinder('NailBrush_GoldFerrule_'+str(i),brushes,gold,(0,0,height-.020),.00195,.012,.00025)
    bpy.ops.mesh.primitive_cone_add(vertices=48,radius1=.0016,radius2=.00025,depth=.014,location=(0,0,height-.007))
    tip=finish(bpy.context.object,'NailBrush_FineTip_'+str(i),brushes,bristle)
    for part in (handle,ferrule,tip):part.matrix_world=transform@part.matrix_world

for obj in scene.objects:
    if obj.type == 'MESH':
        obj['asset_builder'] = 'scripts/build_manicure_finale_props.py'
for col in [fan,wand,teal,raspberry,podium,brushes]:
    col['placement'] = 'Instance the collection; local Z=0 is the supporting floor'

# Collection geometry is intentionally co-located at authored local origins.
# Hide the stage in asset-library viewport so the small props can be inspected.
scene['asset_library_usage'] = 'Append or link individual asset collections; all are authored at their own origin.'
text=bpy.data.texts.new('MANICURE_PROPS_README')
text.write('Reusable finale props in metres. Link individual collections into Shot5.\n'
    'Swatch fan fronts -Y; up +Z. Wand lies along X. Loose tips face +Z.\n'
    'Podium radius 160mm, top 50mm above origin. All other bases rest on Z0.\n'
    'The lacquer materials are appended from approved Shot4 v004; sources untouched.\n'
    'Physical UV scale is 14.5units/metre on all tips. Five supported fan tips and two loose tips.\n')
bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
bpy.context.view_layer.update()
deps=scene.view_layers[0].depsgraph
report={'source_finish':str(SOURCE.relative_to(ROOT)), 'asset_file':str(DEST.relative_to(ROOT)),
    'collections':{}, 'materials':list(m.name for m in lacquers.values())}
for col in [fan,wand,teal,raspberry,podium,brushes]:
    points=[]
    for ob in col.all_objects:
        ev=ob.evaluated_get(deps)
        points.extend(ev.matrix_world@Vector(v) for v in ev.bound_box)
    lower=[min(v[i] for v in points) for i in range(3)]
    upper=[max(v[i] for v in points) for i in range(3)]
    report['collections'][col.name]={'objects':len(col.all_objects),'min':lower,'max':upper,
        'dimensions_m':[upper[i]-lower[i] for i in range(3)]}
report['external_libraries']=sorted({block.library.filepath for blocks in
    [bpy.data.objects,bpy.data.materials,bpy.data.node_groups,bpy.data.images]
    for block in blocks if block.library})
(QA/'props_asset_report.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
print('PROPS_ASSET_READY',json.dumps(report),flush=True)
