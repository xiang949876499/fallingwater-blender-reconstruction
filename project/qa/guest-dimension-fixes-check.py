import bpy,sys,json,math,hashlib
from pathlib import Path
from types import SimpleNamespace
from mathutils import Vector
p=Path('D:/zx/test/project');sys.path.insert(0,str(p/'scripts'))
from fwlib import collection,poly_prism
from materials import build_materials
import guest_house
bpy.ops.wm.read_factory_settings(use_empty=True)
ctx=SimpleNamespace(root=p,mats=build_materials(),collection=collection,config=json.loads((p/'config.json').read_text(encoding='utf-8')))
rooms=guest_house.build(ctx)
bpy.context.view_layer.update()
(p/'qa/guest-dimension-fixes-rooms.json').write_text(json.dumps(rooms,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(p/'qa/guest-dimension-fixes-module.blend'))
# Run same independent anchor measurement implementation against this saved fresh mesh.
s=(p/'qa/guest-dimensions-measured-extract.py').read_text(encoding='utf-8')
s=s.replace("root/'scene/Fallingwater_working.blend'","root/'qa/guest-dimension-fixes-module.blend'")
s=s.replace('guest-dimensions-measured-projection.json','guest-dimension-fixes-projection.json').replace('guest-dimensions-measured.json','guest-dimension-fixes-measured.json').replace('saved iteration03','fresh corrected module')
exec(compile(s,'guest-dimension-fixes-actual-extract','exec'),{})
# Preserve previous stair evidence and run same regression sensitivity test on revised module.
s=(p/'qa/guest-geometry-clearance-check.py').read_text(encoding='utf-8').replace('guest-geometry-clearance-report.json','guest-dimension-fixes-clearance.json')
exec(compile(s,'guest-dimension-fixes-stair-regression','exec'),{})
# Door tunnel cross sections measure genuine passage between jambs, not metadata width.
data=json.loads((p/'data/guest_house.json').read_text(encoding='utf-8'));reg=ctx.config['guest_actual_registration'];sx,sy=reg['meters_per_pixel'];ox,oy=reg['origin_px'];wx,wy,gz=reg['world_origin']
scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
def world(v):return Vector((wx+(v[0]-ox)*sx,wy+(oy-v[1])*sy))
doors=[]
for wall in data['walls']:
 if wall['id'] not in ['GUEST_L1_BED_EAST','GUEST_L1_BOILER_WEST','GUEST_B1_BASE_EAST','GUEST_B1_BASE_BATH_EAST','GUEST_L1_BATH_NORTH_TUB']:continue
 a,b=world(wall['a']),world(wall['b']);v=(b-a).normalized();n=Vector((-v.y,v.x));level=gz+data['levels'][wall['level']]['offset'];thick=wall.get('thickness',.29)
 for i,op in enumerate(wall.get('openings',[])):
  if op['type']!='door':continue
  t0,t1=op['span'];mid=a+(b-a)*((t0+t1)/2);samples=[]
  for lateral in [-.24,0,.24]:
   for h in [.3,.9,1.70,1.94]:
    q=mid+v*lateral-n*(thick/2+.035)
    found,loc,normal,idx,obj,mat=scene.ray_cast(deps,Vector((q.x,q.y,level+h)),Vector((n.x,n.y,0)),distance=thick+.07)
    samples.append({'offset_m':lateral,'height_m':h,'hit':obj.name if found else None,'hit_xyz':list(loc) if found else None,'status':'FAIL' if found else 'PASS'})
  # Actual header underside along vertical centerline from datum.
  found,loc,normal,idx,obj,mat=scene.ray_cast(deps,Vector((mid.x,mid.y,level+.04)),Vector((0,0,1)),distance=3)
  clearance=loc.z-level if found else None
  doors.append({'wall':wall['id'],'opening_index':i,'center_world':[mid.x,mid.y,level],'actual_header_hit':obj.name if found else None,'actual_height_m':clearance,'body_width_m':.48,'samples':samples,'status':'PASS' if all(t['status']=='PASS' for t in samples) and clearance is not None and clearance>=1.95 else 'FAIL'})
report={'status':'PASS' if all(x['status']=='PASS' for x in doors) else 'FAIL','source_scene':'qa/guest-dimension-fixes-module.blend','method':'Real scene.ray_cast cross-sections across wall thickness at5 affected door openings;3 lateral positions x4 body heights, plus true head underside. No furnishings or terrain included.','doors':doors}
(p/'qa/guest-dimension-fixes-doors.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('DOOR_REGRESSION',[(r['wall'],r['status'],r['actual_height_m'],[(s['offset_m'],s['height_m'],s['hit']) for s in r['samples'] if s['hit']]) for r in doors])
