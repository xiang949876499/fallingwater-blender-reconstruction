import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,'D:/zx/test/project/scripts')
import main_house
bpy.ops.wm.open_mainfile(filepath='D:/zx/test/project/qa/main-geometry-smoke.blend')
dg=bpy.context.evaluated_depsgraph_get()
obs=[]
for ob in bpy.data.objects:
 if ob.type!='MESH' or ob.get('component_type')=='stairs':continue
 ps=[ob.matrix_world@Vector(c) for c in ob.bound_box]
 mn=Vector(tuple(min(p[i] for p in ps) for i in range(3)));mx=Vector(tuple(max(p[i] for p in ps) for i in range(3)))
 obs.append((ob,mn,mx))
def inside(ob,p):
 eo=ob.evaluated_get(dg);inv=eo.matrix_world.inverted();loc=inv@p;dire=(inv.to_3x3()@Vector((1,.137,.051))).normalized();count=0
 for _ in range(50):
  hit,q,n,f=eo.ray_cast(loc,dire)
  if not hit:break
  count+=1;loc=q+dire*.00001
 return count%2==1
report={'tests':[]}
for label,a,b,z0,z1,width in [('stair2',(432,279.7),(367,279.7),2.8448,5.26415,.82),('pool_stair',(540,423),(540,380),-2.5,0,.93),('hatch',(527,480),(459,480),-2.8467,.1,1.53)]:
 a=Vector(main_house.xyz(a,z0));b=Vector(main_house.xyz(b,z1));n=math.ceil((z1-z0)/.175);hits=[]
 for i in range(1,20):
  t=i/20;p=a.lerp(b,t);p.z=z0+math.ceil(t*n)*(z1-z0)/n
  for h in (.15,.6,1.2,1.65):
   q=p+Vector((0,0,h))
   for ob,mn,mx in obs:
    if all(mn[k]-.0001<=q[k]<=mx[k]+.0001 for k in range(3)) and inside(ob,q):hits.append({'fraction':t,'height':h,'object':ob.name})
 report['tests'].append({'name':label,'centerline_obstacles':hits,'status':'PASS' if not hits else 'FAIL','limitation':'centerline samples; not a swept-body navigation test'})
# Pool opening: only its water surface should be first encountered below the deck top.
origin=Vector(main_house.xyz((615,402),-2.49));dist=999;name=None;z=None
for ob,mn,mx in obs:
 eo=ob.evaluated_get(dg);inv=eo.matrix_world.inverted();hit,q,normal,face=eo.ray_cast(inv@origin,(inv.to_3x3()@Vector((0,0,-1))).normalized())
 if hit:
  w=eo.matrix_world@q;d=(w-origin).length
  if d<dist:dist=d;name=ob.name;z=w.z
report['pool_opening']={'first_hit':name,'world_z':z,'status':'PASS' if name=='MAIN_B_plunge_water' else 'FAIL'}
seen={}
for ob in bpy.data.objects:
 if ob.get('opening_use')=='terrace_door':
  base=ob.name.split('_open_casement')[0].split('_sill')[0].split('_head')[0].split('_mullion')[0].split('_transom')[0].split('_glass')[0].split('_hinge')[0].split('_latch')[0]
  seen[base]=ob['clear_width_m']
report['door_clearances']={n:round(w,3) for n,w in seen.items()};report['minimum_terrace_door_m']=min(seen.values())
Path('D:/zx/test/project/qa/main-geometry-fixes.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
