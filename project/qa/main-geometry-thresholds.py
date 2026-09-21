import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,'D:/zx/test/project/scripts')
import main_house,validate_scene
bpy.ops.wm.open_mainfile(filepath='D:/zx/test/project/qa/main-geometry-smoke.blend')
dg=bpy.context.evaluated_depsgraph_get();floorobs=[];bodyobs=[]
for ob in bpy.data.objects:
 if ob.type!='MESH':continue
 ps=[ob.matrix_world@Vector(c) for c in ob.bound_box];mn=Vector(tuple(min(p[k] for p in ps) for k in range(3)));mx=Vector(tuple(max(p[k] for p in ps) for k in range(3)))
 kind=validate_scene.component(ob)
 if kind in ('floor','stairs'):floorobs.append((ob,mn,mx))
 elif kind in ('wall','door','window','ceiling'):bodyobs.append((ob,mn,mx))
def ground(p,z):
 closest=None
 for ob,mn,mx in floorobs:
  if not (mn.x-.01<=p[0]<=mx.x+.01 and mn.y-.01<=p[1]<=mx.y+.01 and mn.z<z+.2 and mx.z>z-.30):continue
  eo=ob.evaluated_get(dg);inv=eo.matrix_world.inverted();start=Vector((*p,z+.2));hit,q,normal,face=eo.ray_cast(inv@start,(inv.to_3x3()@Vector((0,0,-1))).normalized())
  if hit:
   w=eo.matrix_world@q
   if z-.3<=w.z<=z+.2 and (closest is None or w.z>closest[1]):closest=(ob.name,w.z)
 return closest
def inside(ob,p):
 eo=ob.evaluated_get(dg);inv=eo.matrix_world.inverted();loc=inv@p;d=(inv.to_3x3()@Vector((1,.137,.051))).normalized();count=0
 for _ in range(40):
  hit,q,n,f=eo.ray_cast(loc,d)
  if not hit:break
  count+=1;loc=q+d*.00001
 return count%2==1
out={'tests':[]}
for name,rid,rr,lev,mat,path in main_house.THRESHOLDS:
 a,b=Vector(main_house.xy(path[0])),Vector(main_house.xy(path[1]));z=main_house.LEVELS[lev];samples=[];badbody=[]
 for i in range(13):
  p=a.lerp(b,i/12);hit=ground(p,z);samples.append({'fraction':i/12,'hit':hit,'ground_ok':hit is not None and abs(hit[1]-z)<=.16})
  for h in (.35,.9,1.65):
   q=Vector((p.x,p.y,z+h))
   for ob,mn,mx in bodyobs:
    if all(mn[k]<=q[k]<=mx[k] for k in range(3)) and inside(ob,q):badbody.append({'fraction':i/12,'object':ob.name,'height':h})
 out['tests'].append({'id':name,'ground_status':'PASS' if all(t['ground_ok'] for t in samples) else 'FAIL','body_centerline_status':'PASS' if not badbody else 'FAIL','samples':samples,'body_hits':badbody})
out['requested_points']=[]
for p,z in [((.102,12.94),5.26415),((3.111,12.537),2.8448)]:out['requested_points'].append({'xy':p,'expected_z':z,'hit':ground(p,z)})
out['summary']={'count':len(out['tests']),'ground_failures':[t['id'] for t in out['tests'] if t['ground_status']=='FAIL'],'body_failures':[t['id'] for t in out['tests'] if t['body_centerline_status']=='FAIL'],'limitation':'actual evaluated mesh centerline probes; no furniture, no swept-body test'}
Path('D:/zx/test/project/qa/main-geometry-thresholds.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out['summary'],indent=2));print(json.dumps(out['requested_points'],indent=2))
for t in out['tests']:
 if t['body_hits']:print(t['id'],t['body_hits'])
