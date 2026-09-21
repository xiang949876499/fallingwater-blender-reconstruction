import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];src=R/'scene/Fallingwater_iteration09.blend'
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;out=[]
keys=('headboard','mattress','bedcover','back_board','drawer_front','wardrobe','desk_top','table_top','armchair','chair_seat')
for o in s.objects:
 selected=o.name in ['MAIN_L2_MASTER_finish','MAIN_L2_CLOSET_M_finish','MAIN_floor_threshold_hall_master_finish','MAIN_L2_master_hearth','MAIN_L2_master_north','MAIN_L2_master_north_east'] or o.name.startswith(('MAIN_L2_master_entry','MAIN_L2_master_south_')) or (o.name.startswith(('FW_FURN_MAIN_L2_MASTER_','FW_FURN_MAIN_L2_CLOSET_M_')) and any(k in o.name for k in keys))
 if not selected or o.type!='MESH':continue
 vv=[o.matrix_world@Vector(v) for v in o.bound_box];b=[[min(v[k] for v in vv),max(v[k] for v in vv)] for k in range(3)]
 out.append(dict(object=o.name,world_bounds=b,world_center=[sum(x)/2 for x in b],source_plan_bounds=[b[0][0]/.0524+327,540-b[1][1]/.0531,b[0][1]/.0524+327,540-b[1][0]/.0531],materials=[m.name for m in o.data.materials],world_rotation=list(o.matrix_world.to_euler()),vertices=len(o.data.vertices),faces=len(o.data.polygons)))
result=dict(status='READ_ONLY_REAL_SAVED09_OBJECTS',scene_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),objects=out,no_scene_saved=True)
(R/'qa/master-source10-model-audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
