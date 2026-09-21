"""Bounded actual-mesh regression for the sheet04 corrections."""
import bpy, json, sys, math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,'D:/zx/test/project/scripts')
import main_house
P=Path('D:/zx/test/project/qa')
bpy.ops.wm.open_mainfile(filepath=str(P/'main-geometry-smoke.blend'))
s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
def ray(a,b):
 a,b=Vector(a),Vector(b);d=b-a
 hit,p,n,i,ob,m=s.ray_cast(dg,a,d.normalized(),distance=d.length)
 return {'object':ob.name,'position':list(p)} if hit else None
out={'new_kitchen_door':[],'old_kitchen_door_closure':[],'servant_north_bay':[],'service_stair':[],'kitchen_window_bay':[]}
a=Vector(main_house.xy((317,278.5)));b=Vector(main_house.xy((334,278.5)))
for lateral in (-.18,-.09,0,.09,.18):
 for h in (.18,.72,1.13,1.60,1.95):
  hit=ray((a.x,a.y+lateral,.122+h),(b.x,b.y+lateral,.122+h))
  out['new_kitchen_door'].append({'offset':lateral,'height':h,'obstacle':hit,'status':'PASS' if not hit else 'FAIL'})
for py in (296,303,311):
 hit=ray(main_house.xyz((319,py),1.2),main_house.xyz((330,py),1.2))
 out['old_kitchen_door_closure'].append({'source_y':py,'hit':hit,'status':'PASS' if hit and hit['object']=='MAIN_L1_kitchen_east_south' else 'FAIL'})
for px,py in ((213,219),(226,220),(239,224),(209,224),(227,229)):
 hit=ray(main_house.xyz((px,py),.45),main_house.xyz((px,py),-.3))
 head=ray(main_house.xyz((px,py),.122+.01),main_house.xyz((px,py),.122+1.95))
 out['servant_north_bay'].append({'source_px':[px,py],'ground':hit,'body_obstacle':head,'status':'PASS' if hit and hit['object']=='MAIN_L1_SERVANT_finish' and not head else 'FAIL'})
start=Vector(main_house.xyz((207,206.5),-2.15));end=Vector(main_house.xyz((264,206.5),.1));n=math.ceil(2.25/.175)
for i in range(1,n+1):
 t=(i-.5)/n;p=start.lerp(end,t);z=-2.15+i*2.25/n
 for lateral in (-.18,0,.18):
  q=p+Vector((0,lateral,0));ground=ray((q.x,q.y,z+.12),(q.x,q.y,z-.20));head=ray((q.x,q.y,z+.03),(q.x,q.y,z+1.95))
  out['service_stair'].append({'step':i,'offset':lateral,'expected_z':z,'ground':ground,'head_obstacle':head,'status':'PASS' if ground and abs(ground['position'][2]-z)<.035 and not head else 'FAIL'})
for px,py in ((277,326),(290,326),(304,326)):
 hit=ray(main_house.xyz((px,py),.45),main_house.xyz((px,py),-.3))
 out['kitchen_window_bay'].append({'source_px':[px,py],'kind':'bay_floor','hit':hit,'status':'PASS' if hit and hit['object']=='MAIN_L1_KITCHEN_finish' else 'FAIL'})
for z in (.27,.63,1.27,2.27):
 hit=ray(main_house.xyz((281,329),z),main_house.xyz((281,334),z))
 out['kitchen_window_bay'].append({'z':z,'kind':'full_height_glazing','hit':hit,'status':'PASS' if hit and 'MAIN_L1_kitchen_south_front_glass' in hit['object'] else 'FAIL'})
out['summary']={key:{'samples':len(rows),'failures':[r for r in rows if r['status']=='FAIL']} for key,rows in out.items()}
out['limitations']='Main architecture only,5-column short-door sweep and staircase sample rays,not a complete furniture-aware navigation certificate.'
(P/'main-dimension-resolution-check.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out['summary'],indent=2))
