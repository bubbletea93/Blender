"""Read-only audit of lacquer shader ownership and references."""
import bpy,json
from pathlib import Path
ROOT=Path('C:/Users/danht/Documents/GitHub/Blender')
OUT=ROOT/'renders/lacquer_glitter_review'
files=[ROOT/'assets/products/gel_polish_bottle.blend']+list((ROOT/'scenes').glob('*.blend'))
report=[]
for path in files:
    bpy.ops.wm.open_mainfile(filepath=str(path))
    groups=[g for g in bpy.data.node_groups if 'glitter' in g.name.lower()]
    mats=[m for m in bpy.data.materials if 'lacquer' in m.name.lower()]
    report.append({'file':str(path),'groups':[{'name':g.name,'library':g.library.filepath if g.library else None,'nodes':len(g.nodes),'inputs':[i.name for i in g.interface.items_tree if i.item_type=='SOCKET' and i.in_out=='INPUT'],'users':g.users,'voronoi_scales':[n.inputs['Scale'].default_value for n in g.nodes if n.type=='TEX_VORONOI']} for g in groups],'lacquer_material_count':len(mats),'lacquer_materials':[{'name':m.name,'library':m.library.filepath if m.library else None,'groups':[n.node_tree.name for n in m.node_tree.nodes if n.type=='GROUP']} for m in mats if m.node_tree],'lacquer_objects':[{'name':o.name,'active_material':o.active_material.name if o.active_material else None,'uvs':{uv.name:{'min':[min(item.uv[a] for item in uv.data) for a in [0,1]],'max':[max(item.uv[a] for item in uv.data) for a in [0,1]]} for uv in o.data.uv_layers}} for o in bpy.data.objects if o.type=='MESH' and ('lacquer' in o.name.lower() or (o.override_library and o.override_library.reference.name=='Lacquer'))]})
    print('AUDITED',path.name,flush=True)
(OUT/'material_audit.json').write_text(json.dumps(report,indent=2))
print('AUDIT_COMPLETE',flush=True)
