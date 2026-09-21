"""Actual mesh evidence for boiler roof / terrace-pool census fixes; no render."""
import sys,json
from pathlib import Path
from types import SimpleNamespace
import bpy
from mathutils import Vector
root=Path('D:/zx/test/project');sys.path.insert(0,str(root/'scripts'))
from fwlib import collection
from materials import build_materials
import guest_house
bpy.ops.wm.read_factory_settings(use_empty=True)
ctx=SimpleNamespace(root=root,mats=build_materials(),collection=collection,config=json.loads((root/'config.json').read_text(encoding='utf-8')))
rooms={r['id']:r for r in guest_house.build(ctx)}
bpy.context.view_layer.update();scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
old=json.loads((root/'qa/automated-v2-old.json').read_text(encoding='utf-8'))
oldrooms={r['room_id']:r for r in old['room_results']}
def inside(pt,poly):
 x,y=pt;flag=False;j=len(poly)-1
 for i,(xi,yi) in enumerate(poly):
  xj,yj=poly[j]
  if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi)+xi:flag=not flag
  j=i
 return flag
def hit(xy,start_z,direction,distance):
 found,loc,normal,idx,obj,m=scene.ray_cast(deps,Vector((*xy,start_z)),Vector((0,0,direction)),distance=distance)
 return {'object':obj.name,'z':round(loc.z,6),'normal_z':round(normal.z,5)} if found else None
br=rooms['GUEST_L1_BOILER'];boiler=[]
for s in oldrooms['GUEST_L1_BOILER']['surface_samples']:
 xy=s['xy'];floor=hit(xy,br['z']+.08,-1,.16);roof=hit(xy,br['z']+.2,1,br['height']+.12)
 ok=floor and roof and abs(floor['z']-br['z'])<.025 and abs(roof['z']-(br['z']+br['height']))<.025 and roof['normal_z']<-.95
 boiler.append({'xy':xy,'floor':floor,'ceiling':roof,'status':'PASS' if ok else 'FAIL'})
tr=rooms['GUEST_L1_TERRACE'];terrace=[]
for s in oldrooms['GUEST_L1_TERRACE']['surface_samples']:
 xy=s['xy'];is_inside=inside(xy,tr['polygon']);surface=hit(xy,tr['z']+.08,-1,.16)
 terrace.append({'xy':xy,'inside_revised_terrace':is_inside,'flat_surface':surface,'status':'PASS' if (not is_inside or (surface and abs(surface['z']-tr['z'])<.025)) else 'FAIL'})
bad=(24.69994,35.67970);pool=rooms['GUEST_L1_POOL'];surface=hit(bad,tr['z']+1.5,-1,3)
poolcheck={'xy':bad,'outside_terrace':not inside(bad,tr['polygon']),'inside_pool_census':inside(bad,pool['polygon']),'actual_downward_hit':surface,'status':'PASS' if (not inside(bad,tr['polygon']) and inside(bad,pool['polygon']) and surface and 'water' in surface['object'].lower()) else 'FAIL'}
report={'status':'PASS' if all(s['status']=='PASS' for s in boiler+terrace) and poolcheck['status']=='PASS' else 'FAIL','blender_version':bpy.app.version_string,'method':'Built current guest module; evaluated actual mesh rays at all previous boiler/terrace probes. Independently confirmed excluded terrace point still hits pool water, not a new slab. No rendering.','boiler_original_probes':boiler,'terrace_original_probes':terrace,'pool_preservation_check':poolcheck,'limits':['Integrated scene must be rebuilt; no furniture/site/main geometry included in this focused check.','No final visual or navigation acceptance claimed.']}
(root/'qa/guest-geometry-v2fix-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
if report['status']!='PASS':raise RuntimeError('V2 fixes failed actual mesh verification')
