import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,'D:/zx/test/project/scripts');import main_house
bpy.ops.wm.open_mainfile(filepath='D:/zx/test/project/qa/main-geometry-smoke.blend')
s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();old=json.loads(Path('D:/zx/test/project/qa/main-geometry-living-ray.json').read_text())
origin=Vector(old['camera']);out={'green_hole_pixel_regression':[],'upper_arc_ground':[],'master_approach':[]}
for entry in old['pixels']:
 if entry['pixel'] not in ([225,490],[300,493],[210,480],[350,498]):continue
 d=(Vector(entry['hits'][0]['location'])-origin).normalized();hit,loc,n,i,ob,m=s.ray_cast(dg,origin,d,distance=100)
 out['green_hole_pixel_regression'].append({'pixel':entry['pixel'],'old_first':entry['hits'][0]['object'],'new_first':ob.name if hit else None,'location':list(loc) if hit else None,'status':'PASS' if hit and ob.name=='MAIN_L1_LIVING_finish' else 'FAIL'})
for x,y in [(7.63102,20.37604),(7.61631,20.34709),(7.82163,20.27474),(7.18,20.27474)]:
 hit,loc,n,i,ob,m=s.ray_cast(dg,Vector((x,y,5.58)),Vector((0,0,-1)),distance=.70)
 out['upper_arc_ground'].append({'xy':[x,y],'hit':ob.name if hit else None,'ground_z':loc.z if hit else None,'status':'PASS' if hit and abs(loc.z-5.26415)<.05 else 'FAIL'})
# Test the source-aligned Master threshold approach (tour's old off-axis sample was invalid) with a0.18m radius, through full1.95m body height.
ob=bpy.data.objects['MAIN_L2_master_entry_open_door'];eo=ob.evaluated_get(dg);inv=eo.matrix_world.inverted()
for center in [main_house.xy((378,298)),main_house.xy((378,303)),main_house.xy((378,310))]:
 hits=[]
 for dx,dy in [(0,0),(.18,0),(-.18,0),(0,.18),(0,-.18)]:
  for h in (.18,.72,1.13,1.60,1.95):
   p=Vector((center[0]+dx,center[1]+dy,2.8448+.022+h));d=Vector((1,.127,.031)).normalized();loc=inv@p;ld=(inv.to_3x3()@d).normalized();count=0
   for k in range(20):
    hit,q,n,f=eo.ray_cast(loc,ld)
    if not hit:break
    count+=1;loc=q+ld*.00001
   if count%2:hits.append([dx,dy,h])
 out['master_approach'].append({'center':center,'old_leaf_collision_samples':hits,'status':'PASS' if not hits else 'FAIL'})
out['limitations']='Main architecture-only pixel and body checks; integrated furniture-aware tour and relit visual image remain to be checked.'
Path('D:/zx/test/project/qa/main-geometry-living-fixes.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
