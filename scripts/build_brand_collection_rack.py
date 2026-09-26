"""Build an acrylic six-bottle display inspired by the supplied brand photographs.

Uses the exact full-size approved product meshes. Run in factory background
Blender; writes a new reusable library and never changes the source shot.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'scenes/gel_polish_lapohka_shot5_376_528_polish_finale_v004.blend'
DEST = ROOT/'assets/props/brand_collection_bottle_rack.blend'
OUT = ROOT/'renders/shot5_brand_collection_v005'
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
s = bpy.context.scene
s.name = 'BrandCollection_ReusableRack'
with bpy.data.libraries.load(str(SOURCE), link=False) as (a,b):
    b.collections=['SHOT05_Product_PetrolTeal']
source = b.collections[0]
s.collection.children.link(source)
bpy.context.view_layer.update()
rotation = Matrix.Rotation(math.pi/2, 4, 'X')
dg = bpy.context.evaluated_depsgraph_get()
points = [rotation @ o.matrix_world @ Vector(p) for o in source.all_objects
          if o.type=='MESH' for p in o.evaluated_get(dg).bound_box]
lo = Vector([min(p[i] for p in points) for i in range(3)])
hi = Vector([max(p[i] for p in points) for i in range(3)])
normalise = Matrix.Translation((-((lo.x+hi.x)/2),-((lo.y+hi.y)/2),-lo.z)) @ rotation
original_lacquer=next(slot.material for o in source.objects if o.name.endswith('_Lacquer') for slot in o.material_slots)

palette = [
    ('PearlIvory',(.34,.29,.21),(.78,.73,.61)),
    ('BlushRose',(.20,.018,.051),(.61,.14,.25)),
    ('Amethyst',(.052,.007,.09),(.26,.045,.36)),
    ('MoltenCopper',(.15,.025,.009),(.51,.17,.06)),
    ('Sapphire',(.006,.035,.13),(.025,.19,.47)),
    ('Emerald',(.004,.055,.021),(.026,.25,.08)),
]
variants=[]
for name,base,band in palette:
    col=bpy.data.collections.new('CollectionBottle_'+name)
    lacquer=original_lacquer.copy();lacquer.name='COLLECTION_Lacquer_'+name
    lacquer.animation_data_clear();lacquer.node_tree.animation_data_clear()
    for n in lacquer.node_tree.nodes:
        if n.type=='RGB' and n.name.startswith('Base Color'):n.outputs[0].default_value=(*base,1)
        if n.type=='RGB' and n.name.startswith('Band Color'):n.outputs[0].default_value=(*band,1)
        if n.type=='BSDF_GLOSSY':n.inputs['Color'].default_value=(*base,1)
        if n.type=='TEX_COORD':n.object=None
    for obj in source.objects:
        copy=obj.copy();copy.name='CollectionBottle_'+name+'_'+obj.name.rsplit('_',1)[-1]
        copy.animation_data_clear();copy.parent=None
        copy.matrix_world=normalise @ obj.matrix_world
        col.objects.link(copy)
        copy.light_linking.receiver_collection=None;copy.light_linking.blocker_collection=None
        if obj.name.endswith('_Lacquer'):
            for slot in copy.material_slots:slot.link='OBJECT';slot.material=lacquer
    variants.append(col)
s.collection.children.unlink(source)

rack=bpy.data.collections.new('Prop_BrandCollection_AcrylicRack')
s.collection.children.link(rack)
rack.asset_mark()
rack.asset_data.description='Six full-size gold polish bottles on a two-tier clear acrylic retail display; fronts -Y, origin on floor.'
rack['reference']='User supplied Hang Pure collection/rack photographs, 2026-09-25'
rack['dimensions_m']=[.169,.096,.1453]
rack['product_scale']=1.0
rack['display_note']='Curated six shades; not a colorimetric reproduction of catalogue shades.'

def material(name,color,metal=0,rough=.25,transmission=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    p.inputs['Transmission Weight'].default_value=transmission;p.inputs['IOR'].default_value=1.49
    return m
acrylic=material('COLLECTION_OpticalAcrylic',(.985,.994,1),rough=.035,transmission=1)
silver=material('COLLECTION_SilverFasteners',(.60,.65,.69),1,.2)
ink=material('COLLECTION_SubtleEngraving',(.16,.12,.075),.35,.32)

def finish(ob,name,mat,bevel=0):
    ob.name=name
    for old in list(ob.users_collection):old.objects.unlink(ob)
    rack.objects.link(ob);ob.data.materials.append(mat)
    if bevel:
        mod=ob.modifiers.new('Polished manufactured edge','BEVEL');mod.width=bevel;mod.segments=3
        mod.harden_normals=True
        ob.modifiers.new('Flat optical face normals','WEIGHTED_NORMAL')
    return ob

def cube(name,loc,size,mat=acrylic,bevel=.00045):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    ob=bpy.context.object;ob.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(ob,name,mat,bevel)

cube('CollectionRack_FrontShelf',(0,-.023,.0045),(.164,.046,.003))
cube('CollectionRack_RearShelf',(0,.023,.0425),(.164,.046,.003))
cube('CollectionRack_CenterRiser',(0,0,.0235),(.164,.0025,.038))
cube('CollectionRack_Back',(0,.047,.027),(.164,.0025,.054))
cube('CollectionRack_FrontRetainingRail',(0,-.047,.0115),(.164,.002,.011))
cube('CollectionRack_RearRetainingRail',(0,.0005,.0495),(.164,.002,.011))
# Closed sloping side panels with visible machined edges.
profile=[(-.048,0),(.048,0),(.048,.055),(-.048,.018)]
for side in (-1,1):
    xs=(side*.082-.00125,side*.082+.00125)
    verts=[(x,y,z) for x in xs for y,z in profile]
    faces=[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]
    me=bpy.data.meshes.new('CollectionRack_Side_MESH');me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new('CollectionRack_Side',me);rack.objects.link(ob)
    finish(ob,'CollectionRack_Side_'+str(side),acrylic,.0006)
    for j,(y,z) in enumerate([(-.036,.008),(.034,.008),(.034,.041)]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.0026,depth=.0015,
             location=(side*.084,y,z),rotation=(0,math.pi/2,0))
        ob=finish(bpy.context.object,f'CollectionRack_SilverBolt_{side}_{j}',silver,.00022)
        cube(f'CollectionRack_ScrewSlot_{side}_{j}',(side*.0848,y,z),(.00008,.0028,.00035),ink,.00007)
for x in (-.065,.065):
    for y in (-.034,.034):cube('CollectionRack_ClearFoot',(x,y,.0015),(.012,.012,.003),bevel=.0007)

for row in range(2):
    for column in range(3):
        idx=row*3+column
        ob=bpy.data.objects.new(f'CollectionRack_Bottle_R{row+1}_C{column+1}_{palette[idx][0]}',None)
        rack.objects.link(ob);ob.instance_type='COLLECTION';ob.instance_collection=variants[idx]
        ob.location=((column-1)*.052,-.023+row*.046,.0062+row*.038)
        ob.empty_display_size=.007
        ob['shade']=palette[idx][0];ob['shelf_top_m']=.006+row*.038
        ob['motion_note']='Base at true evaluated product foot; full-size copy.'

def text_obj(body,loc,size):
    cu=bpy.data.curves.new('CollectionRack_Label_DATA','FONT');cu.body=body
    cu.align_x='CENTER';cu.size=size;cu.extrude=.000005
    ob=bpy.data.objects.new('CollectionRack_Label',cu);rack.objects.link(ob)
    ob.location=loc;ob.rotation_euler.x=math.pi/2;cu.materials.append(ink)
text_obj('H A N G   P U R E',(0,-.04808,.008),.0026)

bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
points=[i.matrix_world@Vector(v) for i in dg.object_instances if i.object.type=='MESH' for v in i.object.bound_box]
minimum=[min(p[i] for p in points) for i in range(3)]
maximum=[max(p[i] for p in points) for i in range(3)]
bpy.data.libraries.write(str(DEST),{rack},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
(OUT/'rack_build.json').write_text(json.dumps({'asset':str(DEST),'collection':rack.name,
    'bounds':[minimum,maximum],'bottle_dimensions_m':list(hi-lo),'bottle_count':6,'palette':[p[0] for p in palette]},indent=2))
print('RACK_LIBRARY_READY',str(DEST),flush=True)
