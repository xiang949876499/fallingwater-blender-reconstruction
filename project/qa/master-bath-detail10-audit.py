from pathlib import Path
import bpy,json,hashlib
root=Path(__file__).resolve().parents[1]
src=root/'scene/Fallingwater_iteration09.blend'
bpy.ops.wm.open_mainfile(filepath=str(src))
rows=[]
for o in bpy.context.scene.objects:
    if o.get('room_id')=='MAIN_L2_BATH_M' or 'master_bath' in o.name or 'bath_master' in o.name or o.name in ('MAIN_L2_master_east_n','MAIN_L2_master_east_s'):
        pts=[o.matrix_world@v.co for v in o.data.vertices] if o.type=='MESH' else []
        rows.append({'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,
            'component':o.get('component_type'),'asset':o.get('asset_type'),'location':list(o.matrix_world.translation),
            'bbox':[[min(p[k] for p in pts),max(p[k] for p in pts)] for k in range(3)] if pts else None,
            'materials':[m.name if m else None for m in o.data.materials] if o.type in ('MESH','CURVE') else [],
            'modifiers':[(m.name,m.type) for m in o.modifiers]})
rec={'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'objects':rows}
(root/'qa/master-bath-detail10-audit.json').write_text(json.dumps(rec,indent=2),encoding='utf-8')
print(json.dumps({'count':len(rows),'roots':[r for r in rows if r['parent'] is None]},indent=2))
