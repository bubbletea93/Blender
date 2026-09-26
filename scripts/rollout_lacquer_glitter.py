"""Publish the reviewed finish in the product asset and link local shader copies.

Preserves per-shot color/animation nodes, geometry, and source file backups.
"""
import bpy,sys,json,shutil,hashlib,array
from pathlib import Path
ROOT=Path('C:/Users/danht/Documents/GitHub/Blender');OUT=ROOT/'renders/lacquer_glitter_review'
sys.path.insert(0,str(ROOT/'scripts'))
from lacquer_glitter_shared import GROUP,VERSION,build_group,attach_finish
ASSET=ROOT/'assets/products/gel_polish_bottle.blend'
BACKUP=OUT/'source_backups';BACKUP.mkdir(exist_ok=True)
files=[ASSET]+list((ROOT/'scenes').glob('*.blend'))
for path in files:
    dst=BACKUP/path.relative_to(ROOT);dst.parent.mkdir(parents=True,exist_ok=True)
    if not dst.exists():shutil.copy2(path,dst)

def fingerprint():
    meshes={}
    for mesh in bpy.data.meshes:
        if mesh.library:continue
        coords=array.array('f',[0])*(len(mesh.vertices)*3);mesh.vertices.foreach_get('co',coords)
        meshes[mesh.name]=[len(mesh.vertices),len(mesh.polygons),hashlib.sha256(coords.tobytes()).hexdigest()]
    materials={}
    for m in bpy.data.materials:
        if m.library or not m.node_tree:continue
        # Material nodes/color/animation stay local; nested wrapper internals change.
        materials[m.name]=[(n.name,n.bl_idname,tuple(n.outputs[0].default_value) if n.type=='RGB' else None) for n in m.node_tree.nodes]
    actions=sorted((a.name,a.library.filepath if a.library else '') for a in bpy.data.actions)
    return {'meshes':meshes,'materials':materials,'actions':actions}

report=[]
for path in files:
    source=(OUT/'source_session.txt').read_text() if path.name=='gel_polish_lapohka_shot3_199_284.blend' else str(path)
    bpy.ops.wm.open_mainfile(filepath=source)
    repaired=[]
    # Older shots can carry another machine's absolute asset paths. Relocate
    # only missing references with an unambiguous matching project asset.
    missing=[(lib.name,lib.filepath) for lib in bpy.data.libraries if not Path(bpy.path.abspath(lib.filepath,library=lib.parent)).is_file()]
    for name,old in missing:
        basename=Path(old).name
        candidates=list((ROOT/'assets').rglob(basename))
        if len(candidates)==1:
            target=candidates[0]
            bpy.ops.wm.lib_relocate(library=name,filepath=str(target),directory=str(target.parent)+'/',filename=target.name,relative_path=True)
            repaired.append({'old':old,'new':str(target)})
    wrappers=[g for g in bpy.data.node_groups if not g.library and g.name.startswith('Glitter_UVFix')]
    if not wrappers:
        if repaired:bpy.ops.wm.save_as_mainfile(filepath=str(path))
        report.append({'file':str(path),'saved':bool(repaired),'repaired_libraries':repaired,'reason':'No local glitter wrappers; existing library references inherit their source updates.'})
        continue
    before=fingerprint()
    if path==ASSET:
        shared=next((g for g in bpy.data.node_groups if g.name==GROUP and not g.library),None) or build_group()
    else:
        shared=next((g for g in bpy.data.node_groups if g.name==GROUP and g.library and Path(bpy.path.abspath(g.library.filepath)).resolve()==ASSET.resolve()),None)
        if shared is None:
            with bpy.data.libraries.load(str(ASSET),link=True) as (src,dst):
                assert GROUP in src.node_groups;dst.node_groups=[GROUP]
            shared=dst.node_groups[0]
    updated=[]
    for wrapper in wrappers:
        if attach_finish(wrapper,shared):updated.append(wrapper.name)
    assert before==fingerprint(), 'Unexpected geometry, material color, or action change'
    if path==ASSET:
        t=bpy.data.texts.get('LACQUER_SHARED_GLITTER_NOTES') or bpy.data.texts.new('LACQUER_SHARED_GLITTER_NOTES')
        t.clear();t.write('SHARED RENDER GLITTER - '+VERSION+'\n\nEdit Lacquer_RenderGlitter_SHARED here to update every linked finish.\nExisting Glitter_UVFix wrappers retain their old interface and base shader. Shot-local colors and cat-eye animations feed this shared layer.\nCoarse flake cells Scale: density (90). Vary individual flake size: footprint range. Metallic flakes Roughness: highlight sharpness (0.10). Silver flakes tint factor: 0.35.\nThe flake orientation is fixed to UV cells; changing light/view angles produces the shimmer. No emission and no animated random seed are used.\n\nThe original fine glitter is below pixel scale in wider shots; this sparse resolvable layer remains visible at 1920x1080 with Cycles 128 samples and denoising.\n')
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':area.spaces.active.shading.type='SOLID'
    if shared.library:shared.library.filepath=bpy.path.relpath(str(ASSET))
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    # Save As has remapped the new direct shader dependency relatively.
    if path!=ASSET:assert shared.library.filepath.startswith('//')
    report.append({'file':str(path),'saved':True,'wrappers_updated':updated,'shared_source':str(ASSET),'geometry_colors_actions_preserved':True,'repaired_libraries':repaired})
    print('ROLLED_OUT',path.name,updated,flush=True)

# Reopen consumers to verify the actual library graph after all saves.
verification=[]
for path in files:
    bpy.ops.wm.open_mainfile(filepath=str(path))
    wrappers=[g for g in bpy.data.node_groups if g.name.startswith('Glitter_UVFix')]
    for wrapper in wrappers:
        node=wrapper.nodes.get('Shared render glitter finish')
        assert node and node.node_tree.name==GROUP, (path,wrapper.name)
        core=node.node_tree
        owner=Path(bpy.path.abspath(core.library.filepath)).resolve() if core.library else path.resolve()
        assert owner==ASSET.resolve(),(path,owner)
    verification.append({'file':str(path),'wrapper_count':len(wrappers),'all_finish_owners_are_product_asset':True})
    print('VERIFIED',path.name,len(wrappers),flush=True)
(OUT/'rollout_report.json').write_text(json.dumps({'shared_group':GROUP,'version':VERSION,'files':report,'reopened_verification':verification,'backups':str(BACKUP)},indent=2))
print('ROLLOUT_COMPLETE',flush=True)
