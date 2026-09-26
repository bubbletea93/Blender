"""Build the reference-inspired HANG PURE paired nail-sample display.

Standalone asset only: dimensions in metres; front -Y; mounting foot at Z0.
Preserves all existing product and shot files. Run in background Blender.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'assets/props/brand_collection_sample_board.blend'
QA = ROOT / 'renders/shot5_brand_collection_v005'
SOURCE = ROOT / 'assets/props/manicure_finale_props.blend'
QA.mkdir(parents=True, exist_ok=True)
DEST.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = 'BrandCollection_SampleBoard'
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
col = bpy.data.collections.new('Prop_BrandCollection_SampleBoard')
scene.collection.children.link(col)
col.asset_mark()
col.asset_data.description = 'Reference-inspired pearl-bordered upright swatch collection; 36 shades, 72 mounted cat-eye tips. Front -Y, supporting foot at Z0.'
col['dimensions_mm'] = [140, 35, 148]
col['source_reference'] = 'User-supplied HANG PURE Starry Cat Eye pearl-bordered sample collection photograph'
col['interpretation'] = 'Modeled editorial adaptation: four groups of nine shade pairs numbered 211-246; colors follow the reference families, not a color-calibrated retail catalogue.'

with bpy.data.libraries.load(str(SOURCE), link=False) as (src, dst):
    dst.materials = ['PROP_Lacquer_PetrolTeal']
source_finish = dst.materials[0]
assert source_finish

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

panel = principled('BOARD_PearlWhiteSatinPanel', (.72, .705, .68), roughness=.34)
nt = panel.node_tree
noise = nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 2100
noise.inputs['Detail'].default_value = 2
bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = .11
bump.inputs['Distance'].default_value = .000005
nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
nt.links.new(bump.outputs['Normal'], nt.nodes['Principled BSDF'].inputs['Normal'])
inset = principled('BOARD_IvorySampleMount', (.86, .825, .795), roughness=.30)
pearl = principled('BOARD_WarmCulturedPearl', (.81, .68, .54), metallic=.20, roughness=.22)
pearl.node_tree.nodes['Principled BSDF'].inputs['Coat Weight'].default_value = .55
pearl.node_tree.nodes['Principled BSDF'].inputs['Coat Roughness'].default_value = .16
gold = principled('BOARD_ChampagneFineTrim', (.55, .35, .13), metallic=.9, roughness=.24)
ink = principled('BOARD_WarmGreyTypography', (.12, .095, .075), roughness=.5)
acrylic = principled('BOARD_ClearSupport', (.96, .98, 1), roughness=.028, transmission=1)

def finish(obj, name, mat, bevel=0):
    obj.name = name
    for c in list(obj.users_collection): c.objects.unlink(obj)
    col.objects.link(obj)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft manufactured edge', 'BEVEL')
        mod.width = bevel; mod.segments = 3
        mod.limit_method = 'ANGLE'; mod.harden_normals = True
        mod = obj.modifiers.new('Weighted surface normals', 'WEIGHTED_NORMAL')
        mod.keep_sharp = True
    if obj.type == 'MESH':
        for p in obj.data.polygons: p.use_smooth = True
    obj['asset_builder'] = 'scripts/build_brand_sample_board.py'
    return obj

def cube(name, location, dimensions, mat, bevel=.0004):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object; obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, bevel)

def outline_solid(name, coords, front_y, back_y, mat, bevel=.0002):
    n = len(coords)
    verts = [(x, front_y, z) for x,z in coords] + [(x, back_y, z) for x,z in coords]
    faces = [tuple(range(n)), tuple(range(n, 2*n))[::-1]]
    faces += [(i, (i+1)%n, (i+1)%n+n, i+n) for i in range(n)]
    mesh = bpy.data.meshes.new(name+'_Mesh'); mesh.from_pydata(verts, [], faces); mesh.update()
    obj = bpy.data.objects.new(name, mesh); col.objects.link(obj)
    return finish(obj, name, mat, bevel)

# An actual rounded board, not a cube whose thickness limits the corner radius.
coords = []
for cx,cz,start in [(.060,.138,0),(-.060,.138,90),(-.060,.050,180),(.060,.050,270)]:
    for k in range(17):
        a = math.radians(start+k*90/16)
        coords.append((cx+.010*math.cos(a), cz+.010*math.sin(a)))
outline_solid('SampleBoard_RoundedWhiteBacking', coords, -.0016, .0016, panel)

# The softly scalloped inner silhouette echoes the pearl collection reference.
outline = []
for i in range(384):
    a = 2*math.pi*i/384
    c,s = math.cos(a), math.sin(a)
    wobble = .84+.16*math.cos(4*a)
    x = .06405*c*wobble
    z = .094+.0483*s*wobble
    outline.append((x,z))
outline_solid('SampleBoard_CloudIvoryInset', outline, -.0024, -.00165, inset, .00012)

# Resample the rim at equal arc distance for a regular single row of pearls.
distance = [0.]
for i in range(len(outline)):
    a,b = Vector(outline[i]), Vector(outline[(i+1)%len(outline)])
    distance.append(distance[-1]+(b-a).length)
pearl_count = round(distance[-1]/.00355)
pearl_mesh = None
for i in range(pearl_count):
    d = distance[-1]*i/pearl_count
    j = next(j for j in range(len(outline)) if distance[j+1]>=d)
    f = (d-distance[j])/(distance[j+1]-distance[j])
    p = Vector(outline[j]).lerp(Vector(outline[(j+1)%len(outline)]), f)
    if pearl_mesh is None:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=.0017, location=(p.x,-.0033,p.y))
        obj=finish(bpy.context.object, 'SampleBoard_Pearl_001', pearl)
        pearl_mesh = obj.data
    else:
        obj=bpy.data.objects.new('SampleBoard_Pearl_%03d'%(i+1), pearl_mesh)
        obj.location=(p.x,-.0033,p.y); col.objects.link(obj)

cube('SampleBoard_AcrylicStandingFoot', (0,.007,.002), (.058,.035,.004), acrylic, .0008)
cube('SampleBoard_AcrylicRearSpine', (0,.004,.035), (.014,.007,.062), acrylic, .0006)
cube('SampleBoard_GoldFootAccent', (0,-.0107,.0026), (.046,.00045,.0006), gold, .00016)

def text(name, body, location, size, mat, spacing=1.0):
    data=bpy.data.curves.new(name+'_Text', 'FONT')
    data.body=body; data.align_x='CENTER'; data.align_y='CENTER'
    data.size=size; data.space_character=spacing
    data.extrude=.000012; data.bevel_depth=.000003; data.resolution_u=6
    obj=bpy.data.objects.new(name,data);col.objects.link(obj)
    obj.location=location;obj.rotation_euler.x=math.pi/2
    data.materials.append(mat)
    return obj

text('SampleBoard_Brand', 'HANG PURE', (0,-.00262,.0980), .0031, gold, 1.15)
text('SampleBoard_Collection', 'STARRY CAT EYE', (0,-.00262,.0923), .0019, ink, 1.05)
cube('SampleBoard_CentreHairline', (0,-.00262,.1034), (.012,.000035,.00012), gold, 0)

# The approved finish remains UV-locked at the same physical pigment density.
palette = [
    ('Pearl',(.37,.33,.29),(.78,.77,.72)),
    ('RoseQuartz',(.22,.063,.080),(.64,.27,.31)),
    ('Peach',(.32,.078,.030),(.74,.34,.15)),
    ('PetalPink',(.33,.004,.065),(.85,.06,.28)),
    ('Raspberry',(.24,.007,.052),(.60,.055,.20)),
    ('Mauve',(.14,.026,.090),(.46,.13,.34)),
    ('CopperRose',(.17,.032,.018),(.58,.18,.06)),
    ('Aubergine',(.066,.008,.100),(.27,.065,.34)),
    ('RoyalViolet',(.027,.006,.091),(.18,.045,.36)),
    ('SilverLilac',(.19,.19,.27),(.56,.56,.76)),
    ('Lilac',(.084,.035,.19),(.34,.17,.59)),
    ('SoftViolet',(.055,.027,.15),(.24,.15,.55)),
    ('Periwinkle',(.022,.055,.22),(.12,.24,.66)),
    ('GlacierBlue',(.063,.15,.21),(.29,.59,.66)),
    ('PetrolTeal',(.004,.078,.068),(.025,.29,.235)),
    ('MidnightBlue',(.012,.025,.115),(.045,.105,.37)),
    ('Lagoon',(.005,.115,.090),(.035,.42,.27)),
    ('Emerald',(.015,.073,.012),(.11,.35,.035)),
    ('GoldenAmber',(.40,.16,.008),(.88,.48,.035)),
    ('Apricot',(.35,.076,.020),(.76,.27,.090)),
    ('Cinnamon',(.11,.018,.006),(.39,.105,.015)),
    ('Mahogany',(.042,.0025,.0018),(.16,.019,.006)),
    ('RoseCopper',(.19,.026,.015),(.52,.11,.04)),
    ('BurnishedRose',(.12,.012,.009),(.42,.10,.05)),
    ('Mandarin',(.38,.046,.007),(.86,.20,.027)),
    ('Champagne',(.25,.17,.072),(.65,.49,.24)),
    ('Platinum',(.22,.20,.18),(.70,.66,.54)),
    ('Oxblood',(.035,.0015,.004),(.18,.020,.032)),
    ('Ruby',(.22,.0015,.006),(.62,.018,.028)),
    ('Fuchsia',(.20,.004,.077),(.64,.043,.33)),
    ('Magenta',(.14,.0015,.038),(.43,.018,.18)),
    ('Orchid',(.085,.013,.054),(.33,.085,.24)),
    ('Gunmetal',(.012,.013,.014),(.17,.19,.20)),
    ('SilverBlack',(.009,.010,.011),(.28,.30,.31)),
    ('BronzeBlack',(.018,.008,.002),(.20,.075,.014)),
    ('RoseGold',(.18,.048,.022),(.52,.20,.08)),
]

def shade_material(label, base, band):
    m=source_finish.copy();m.name='BOARD_Lacquer_'+label
    m.animation_data_clear(); m.node_tree.animation_data_clear()
    for n in m.node_tree.nodes:
        if n.type=='TEX_COORD':n.object=None
        if n.type=='RGB' and n.name.startswith('Base Color'):n.outputs[0].default_value=(*base,1)
        if n.type=='RGB' and n.name.startswith('Band Color'):n.outputs[0].default_value=(*band,1)
        if n.type=='BSDF_GLOSSY':n.inputs['Color'].default_value=(*base,1)
    m['finish_source']='Approved Shot4 v004 fine shimmer, physical UV scale 14.5 units/m'
    return m

def nail(name, material, variant):
    length,width=.0082,.0033
    segs,rings=32,24
    verts=[(0,0,length/2)]
    for j in range(1,rings):
        th=math.pi*j/rings; z=length/2*math.cos(th)
        taper=.94-.10*z/(length/2)
        for i in range(segs):
            ph=2*math.pi*i/segs;sy=math.sin(ph)
            verts.append((width/2*math.sin(th)*math.cos(ph)*taper,
                          (-.00078 if sy>=0 else -.00012)*math.sin(th)*sy,z))
    verts.append((0,0,-length/2))
    faces=[(0,1+i,1+(i+1)%segs) for i in range(segs)]
    for j in range(rings-2):
        a,b=1+j*segs,1+(j+1)*segs
        for i in range(segs):
            q=(i+1)%segs;faces.append((a+i,b+i,b+q,a+q))
    a=1+(rings-2)*segs
    faces.extend((a+i,len(verts)-1,a+(i+1)%segs) for i in range(segs))
    mesh=bpy.data.meshes.new(name+'_Mesh');mesh.from_pydata(verts,[],[tuple(reversed(f)) for f in faces]);mesh.update()
    obj=bpy.data.objects.new(name,mesh);col.objects.link(obj);mesh.materials.append(material)
    uv=mesh.uv_layers.new(name='UVMap')
    for p in mesh.polygons:
        p.use_smooth=True
        for idx in p.loop_indices:
            co=mesh.vertices[mesh.loops[idx].vertex_index].co
            angle=math.radians(24 if variant==0 else -24)
            u=co.x*math.cos(angle)-co.z*math.sin(angle)
            v=co.x*math.sin(angle)+co.z*math.cos(angle)
            uv.data[idx].uv=(.5+u*14.5,.5+v*14.5)
    obj['shade_pair_variant']=variant
    obj['lacquer_uv_units_per_metre']=14.5
    return obj

for shade,(label,base,band) in enumerate(palette):
    material=shade_material(label,base,band)
    group,col_index=divmod(shade,9)
    if group==0:
        x=(col_index-4)*.0046;zs=(.126,.1165)
    elif group==1:
        x=-.052+col_index*.00435;zs=(.0995,.090)
    elif group==2:
        x=.0172+col_index*.00435;zs=(.0995,.090)
    else:
        x=(col_index-4)*.0046;zs=(.073,.0635)
    for row,z in enumerate(zs):
        obj=nail('SampleBoard_Tip_%d_%s_%s'%(211+shade,label,'CatEye' if row==0 else 'Velvet'),material,row)
        # The flat rear surface touches a short mount, which is seated on panel.
        obj.location=(x,-.00253,z)
        cube('SampleBoard_TipMount_%d_%d'%(211+shade,row),(x,-.00248,z),(.0012,.00016,.0045),inset,.00006)
    text('SampleBoard_Shade_%d'%(211+shade),str(211+shade),(x,-.00262,zs[-1]-.0057),.0012,ink)

col['object_count']=len(col.objects)
col['mounted_tip_count']=72
col['shade_count']=36
col['front']='-Y'
col['foot_origin']='Z0; board itself spans Z .040 to .148'
scene['asset_notes']='Paired shade display inspired by user brand references. All tips modeled and mounted. Existing approved fine-shimmer shader reused without changing product sources.'
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
points=[ob.evaluated_get(deps).matrix_world@Vector(p) for ob in col.objects for p in ob.evaluated_get(deps).bound_box]
lower=[min(p[i] for p in points) for i in range(3)]
upper=[max(p[i] for p in points) for i in range(3)]
report={'collection':col.name,'asset_file':str(DEST),'objects':len(col.objects),'mounted_tips':72,
        'pearl_count':pearl_count,'min':lower,'max':upper,'dimensions_m':[upper[i]-lower[i] for i in range(3)],
        'physical_uv_units_per_metre':14.5,'finish_source':str(SOURCE)}
(QA/'board_report.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
print('BOARD_ASSET_SAVED',json.dumps(report),flush=True)

# Isolated review, deliberately not saved into the reusable asset file.
world=bpy.data.worlds.new('BoardReviewWorld');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.65,.65,1);world.node_tree.nodes['Background'].inputs[1].default_value=.35;scene.world=world
bpy.ops.object.camera_add(location=(.040,-.32,.108));cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,.077))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.18;scene.camera=cam
for pos,energy,size in [((-.13,-.12,.23),7,.12),((.14,-.04,.15),4,.10),((0,.05,.23),5,.08)]:
    bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=energy;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.077))-o.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=True
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    scene.cycles.device='GPU'
except Exception:pass
scene.render.resolution_x=1200;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(QA/'board_review.png')
scene.view_settings.view_transform='AgX'
bpy.ops.render.render(write_still=True)
