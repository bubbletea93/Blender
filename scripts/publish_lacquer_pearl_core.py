"""Update only the shared core, then verify its existing linked consumers."""
import bpy,sys,json,shutil,hashlib,array
from pathlib import Path
ROOT=Path('C:/Users/danht/Documents/GitHub/Blender');OUT=ROOT/'renders/lacquer_pearl_review'
sys.path.insert(0,str(ROOT/'scripts'))
from lacquer_glitter_shared import GROUP,VERSION,build_group,attach_finish
asset=ROOT/'assets/products/gel_polish_bottle.blend'
backup=OUT/'gel_polish_bottle_before_pearl.blend'
if not backup.exists():shutil.copy2(asset,backup)
bpy.ops.wm.open_mainfile(filepath=str(asset))
def fingerprint():
    meshes={}
    for m in bpy.data.meshes:
        a=array.array('f',[0])*(len(m.vertices)*3);m.vertices.foreach_get('co',a)
        meshes[m.name]=[len(m.vertices),len(m.polygons),hashlib.sha256(a.tobytes()).hexdigest()]
    colors={m.name:[(n.name,tuple(n.outputs[0].default_value)) for n in m.node_tree.nodes if n.type=='RGB'] for m in bpy.data.materials if m.node_tree}
    return meshes,colors
before=fingerprint()
core=bpy.data.node_groups[GROUP];assert core.library is None
build_group(existing=core)
assert before==fingerprint()
text=bpy.data.texts.get('LACQUER_SHARED_GLITTER_NOTES') or bpy.data.texts.new('LACQUER_SHARED_GLITTER_NOTES')
text.clear();text.write('SHARED PEARLESCENT LACQUER - '+VERSION+'\n\nCanonical group: Lacquer_RenderGlitter_SHARED in assets/products/gel_polish_bottle.blend.\nAll existing Glitter_UVFix wrappers in the product and shots reference this one core. Change it here and reload consumers.\n\nFine pearl facet density: 220 UV cells. Shimmer coverage: 0.42 plus grazing-angle emphasis. Dense pearlescent shimmer: metallic 0.88, roughness 0.23. Per-facet luster varies from 0.22 to 1.0. Silver luster increases toward grazing angles.\nOccasional larger glints use the separate 90-cell layer with a 0.94 selection threshold.\n\nThe original lacquer colors, cat-eye animation, clear front lens and base shader remain in place. Facets are UV-locked and respond to view/light changes; there is no emission or animated noise seed.\nValidated in Cycles at 1920x1080, 128 samples, with denoising and normal delivery filtering.\n')
t=bpy.data.texts.get('LACQUER_GLITTER_SHARED.PY') or bpy.data.texts.new('LACQUER_GLITTER_SHARED.PY');t.clear();t.write((ROOT/'scripts/lacquer_glitter_shared.py').read_text(encoding='utf-8'))
bpy.ops.wm.save_as_mainfile(filepath=str(asset))
records=[]
for path in [asset]+list((ROOT/'scenes').glob('*.blend')):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    wrappers=[g for g in bpy.data.node_groups if g.name.startswith('Glitter_UVFix')]
    repaired=[]
    missing=[g for g in wrappers if not g.nodes.get('Shared render glitter finish')]
    if missing:
        assert all(g.library is None for g in missing), 'Unwrapped linked source must be fixed at its owner'
        consumer_backup=OUT/(path.stem+'_before_link_repair.blend')
        if not consumer_backup.exists():shutil.copy2(path,consumer_backup)
        snapshot=fingerprint()
        shared=next(g for g in bpy.data.node_groups if g.name==GROUP and g.library and Path(bpy.path.abspath(g.library.filepath)).resolve()==asset.resolve())
        for wrapper in missing:
            attach_finish(wrapper,shared);repaired.append(wrapper.name)
        assert fingerprint()==snapshot
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
    for wrapper in wrappers:
        node=wrapper.nodes.get('Shared render glitter finish');assert node
        core=node.node_tree;assert core.get('finish_version')==VERSION
        owner=Path(bpy.path.abspath(core.library.filepath)).resolve() if core.library else path.resolve()
        assert owner==asset.resolve()
    records.append({'file':str(path),'glitter_wrappers':len(wrappers),'version':VERSION,'shared_owner_verified':True,'local_wrappers_connected':repaired})
    print('PEARL_LINK_VERIFIED',path.name,len(wrappers),flush=True)
(OUT/'core_validation.json').write_text(json.dumps({'source_asset':str(asset),'source_geometry_and_colors_preserved':True,'backup':str(backup),'consumers':records},indent=2))
print('PEARL_CORE_PUBLISHED',flush=True)
