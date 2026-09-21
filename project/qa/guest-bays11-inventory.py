import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
S=R/'scene/Fallingwater_integration_candidate10a.blend'
assert hashlib.sha256(S.read_bytes()).hexdigest()=='dc7594d60b68effaf10b85dd1804827fc9cb16dd786656daa4da16c761b33518'
bpy.ops.wm.open_mainfile(filepath=str(S));s=bpy.context.scene;dep=bpy.context.evaluated_depsgraph_get()
prefixes=('GUEST_L1_THEATER_WEST','GUEST_L1_CARPORT_RETAINED_PIER','GUEST_L1_THEATER_DIAGONAL_BACK','GUEST_L1_THEATER_FLOOR','FW_FURN_GUEST_L1_THEATER','CAM_GUEST_L1_THEATER','GUEST_LAYERED_SANDSTONE_COURSES')
rows=[]
for o in s.objects:
 if not o.name.startswith(prefixes):continue
 eo=o.evaluated_get(dep)
 v=[eo.matrix_world@Vector(x) for x in eo.bound_box]
 row={'name':o.name,'type':o.type,'matrix':[list(r) for r in o.matrix_world],'bounds':[[min(x[i] for x in v),max(x[i] for x in v)] for i in range(3)],'materials':[m.name if m else None for m in getattr(o.data,'materials',[])],'modifiers':[(m.name,m.type) for m in o.modifiers]}
 if o.type=='MESH':row['vertices']=len(o.data.vertices);row['faces']=len(o.data.polygons)
 if o.type=='CAMERA':row['pose']=list(o.matrix_world.translation)
 rows.append(row)
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
(R/'qa/guest-bays11-inventory.json').write_text(json.dumps({'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'objects':rows,'rooms':[r for r in rooms if r['id'] in ['GUEST_L1_THEATER','GUEST_L1_CAR_COURT']]},indent=2),encoding='utf-8')
print(json.dumps({'objects':len(rows),'names':[r['name'] for r in rows if not r['name'].startswith('FW_FURN')]},indent=2))
