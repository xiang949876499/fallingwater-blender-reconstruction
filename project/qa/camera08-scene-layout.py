"""Read fixed furniture footprints for11 bounded camera repairs."""
import sys,json,hashlib
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'scene/Fallingwater_iteration07.blend'
bpy.ops.wm.open_mainfile(filepath=str(p))
ids={'GUEST_L1_BOILER','MAIN_B_PLUNGE','MAIN_L1_COAT','MAIN_L1_SERVANT','MAIN_L2_CLOSET_G','MAIN_L2_CLOSET_M','MAIN_L3_ALCOVE','MAIN_L3_BATH','MAIN_L3_STAIR'}
groups={}
for obj in bpy.context.scene.objects:
    if obj.get('room_id') not in ids or obj.get('component_type')!='furniture' or obj.type not in ('MESH','CURVE','SURFACE','EMPTY'):continue
    k=obj.get('asset_id',obj.name)
    g=groups.setdefault(k,{'room_id':obj.get('room_id'),'asset_type':obj.get('asset_type'),'objects':[],'lo':[1e6]*3,'hi':[-1e6]*3})
    if obj.type=='EMPTY':g['root']={'name':obj.name,'location':list(obj.location),'rotation_euler':list(obj.rotation_euler),'matrix_world':[list(row) for row in obj.matrix_world]};continue
    g['objects'].append(obj.name)
    for q in obj.bound_box:
        v=obj.matrix_world@Vector(q)
        for i in range(3):g['lo'][i]=min(g['lo'][i],v[i]);g['hi'][i]=max(g['hi'][i],v[i])
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
report={'scene':str(p),'scene_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rooms':[r for r in rooms if r['id'] in ids],'furniture':groups,'scope':'Read only; original object world bounding boxes, not new ray visibility or geometric acceptance.'}
(ROOT/'qa/camera08-scene-layout.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for k,g in groups.items():print(k,json.dumps({f:g.get(f) for f in ('room_id','asset_type','lo','hi','root')}),flush=True)
