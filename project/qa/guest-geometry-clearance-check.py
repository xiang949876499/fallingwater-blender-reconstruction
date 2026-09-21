"""P1 regression: real evaluated-mesh stair headroom, no rendering/GPU use."""
import sys,json,math
from pathlib import Path
from types import SimpleNamespace
import bpy
from mathutils import Vector
root=Path('D:/zx/test/project');sys.path.insert(0,str(root/'scripts'))
from fwlib import collection,poly_prism
from materials import build_materials
import guest_house
bpy.ops.wm.read_factory_settings(use_empty=True)
ctx=SimpleNamespace(root=root,mats=build_materials(),collection=collection,config=json.loads((root/'config.json').read_text(encoding='utf-8')))
rooms=guest_house.build(ctx)
data=json.loads((root/'data/guest_house.json').read_text(encoding='utf-8'))
reg=ctx.config['guest_actual_registration'];sx,sy=reg['meters_per_pixel'];ox,oy=reg['origin_px'];wx,wy,gz=reg['world_origin']
def p(x,y):return wx+(x-ox)*sx,wy+(oy-y)*sy
upper=gz+data['levels']['L2']['offset'];rise=upper-gz
bpy.context.view_layer.update();scene=bpy.context.scene
positions=[]
for i in range(14):
 y=354+50*(i+.5)/14
 for lateral in (-.30,0,.30):
  x=316+lateral/sx
  positions.append((f'tread_{i:02}_offset_{lateral:+.2f}',x,y,gz+rise*(i+1)/14))
positions += [('north_lower_approach',316,350,gz),('top_landing',316,409,upper),('west_return_south',297,400,upper),('west_return_mid',297,376,upper),('west_return_north',297,352,upper)]
def measure():
 deps=bpy.context.evaluated_depsgraph_get();out=[]
 for name,x,y,expected in positions:
  xx,yy=p(x,y)
  hit,loc,normal,idx,obj,matrix=scene.ray_cast(deps,Vector((xx,yy,expected+.035)),Vector((0,0,-1)),distance=.10)
  if not hit:
   out.append({'sample':name,'status':'NO_WALKING_SURFACE','source_xy':[x,y]});continue
  floor_z=loc.z;floor_object=obj.name
  hit,loc,normal,idx,obj,matrix=scene.ray_cast(deps,Vector((xx,yy,floor_z+.02)),Vector((0,0,1)),distance=8)
  clearance=loc.z-floor_z if hit else None
  out.append({'sample':name,'source_xy':[x,y],'walking_surface':floor_object,'floor_z':round(floor_z,6),'ceiling_object':obj.name if hit else None,'clearance_m':round(clearance,6) if clearance else None,'status':'PASS' if (clearance is None or clearance>=1.95) else 'FAIL'})
 return out
current=measure()
# Reintroduce the independently identified original offending slab only in memory;
# a meaningful regression test must detect its physical obstruction.
old=poly_prism('QA_OLD_BAD_UPPER_CORRIDOR',[p(287,204),p(326,204),p(326,372),p(287,372)],upper-.21,upper,ctx.mats['stone'],collection('90_QA'))
bpy.context.view_layer.update();old_result=measure();bpy.data.objects.remove(old,do_unlink=True)
linings={}
for obj in scene.objects:
 if obj.get('surface_type')=='cork_wall_lining':
  linings.setdefault(obj.get('room_id'),[]).append({'object':obj.name,'material':obj.active_material.name})
report={'status':'PASS' if all(r['status']=='PASS' for r in current) and any(r['status']=='FAIL' for r in old_result) else 'FAIL','blender_version':bpy.app.version_string,'test_method':'Up/down ray casts against evaluated actual guest mesh at 14 tread centers ×3 lateral positions, lower approach, upper landing and west return. Old solid slab reintroduced in memory to prove regression sensitivity. No rendering.','required_clearance_m':1.95,'minimum_current_clearance_m':min(r['clearance_m'] for r in current if r.get('clearance_m') is not None),'current_samples':current,'old_slab_failure_count':sum(r['status']=='FAIL' for r in old_result),'old_slab_min_clearance_m':min(r['clearance_m'] for r in old_result if r.get('clearance_m') is not None),'bathroom_cork_wall_linings':linings,'limits':['Module geometry only; integrated furnishings, main-building or terrain objects may require the same navigation check.','Doorway heights are not measured by this stair-focused regression.']}
(root/'qa/guest-geometry-clearance-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':report['status'],'samples':len(current),'minimum_clearance_m':report['minimum_current_clearance_m'],'old_slab_failure_count':report['old_slab_failure_count'],'cork_rooms':{k:len(v) for k,v in linings.items()}}))
if report['status']!='PASS':raise RuntimeError('Stair clearance regression failed; inspect report')
