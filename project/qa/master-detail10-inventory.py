import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];SRC=R/'scene/Fallingwater_main_interface_candidate10c.blend'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='f85d813129fab175257f00be12c8d1116505b62d2ca1f9f8a6ffae57926e4a2a'
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;out=[]
for o in s.objects:
 if not o.name.startswith(('FW_FURN_MAIN_L2_MASTER_','FW_FURN_MAIN_L2_CLOSET_M_','MAIN_L2_master_','MAIN_L2_core_','MAIN_L2_MASTER_','MAIN_L2_CLOSET_M_','MAIN_floor_threshold_hall_master')):continue
 if 'course' in o.name:continue
 b=None
 if o.type=='MESH':
  vv=[o.matrix_world@Vector(v) for v in o.bound_box];b=[[min(v[k] for v in vv),max(v[k] for v in vv)] for k in range(3)]
 out.append(dict(name=o.name,type=o.type,parent=o.parent.name if o.parent else None,location=list(o.matrix_world.translation),bounds=b,materials=[m.name for m in getattr(o.data,'materials',[])],properties={k:str(o[k]) for k in o.keys()}))
(R/'qa/master-detail10-inventory.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps([o for o in out if o['type']=='EMPTY'],indent=2))
