import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(root/'scene/Fallingwater_iteration04.blend'))
rows=[]
for o in bpy.data.objects:
    if o.type!='MESH':continue
    if ('MAIN_L1_hearth' in o.name and '_course' not in o.name) or (o.name.startswith('GUEST_') and not any(x in o.name for x in ('window','jamb','leaf','handle','steel','POOL','CONNECTOR','LAYERED'))):
        bounds=[o.matrix_world@Vector(p) for p in o.bound_box]
        rows.append({'name':o.name,'materials':[m.name for m in o.data.materials], 'min':[min(p[i] for p in bounds) for i in range(3)],'max':[max(p[i] for p in bounds) for i in range(3)],'matrix':[list(r) for r in o.matrix_world],'vertices':len(o.data.vertices)})
(root/'qa/masonry-detail-objects.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows,indent=2))
