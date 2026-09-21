import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
root=Path('D:/zx/test/project')
rows=[]
for o in bpy.context.scene.objects:
    if o.name.startswith('GUEST_') and (any(k in o.name for k in ('STAIR','HALL','SERVICE','LAUNDRY','CONNECTOR','MAIN_FLOOR','WEST_LOUNGE','CORRIDOR'))):
        vs=[o.matrix_world@Vector(v) for v in o.bound_box]
        rows.append({'name':o.name,'type':o.type,'bounds':[[min(v[a] for v in vs),max(v[a] for v in vs)] for a in range(3)],'materials':[m.name for m in getattr(o.data,'materials',[]) if m]})
(root/'qa/guest-circulation10-inventory.json').write_text(json.dumps({'objects':rows,'materials':[m.name for m in bpy.data.materials]},indent=2),encoding='utf-8')
print('INVENTORY',len(rows),flush=True)
