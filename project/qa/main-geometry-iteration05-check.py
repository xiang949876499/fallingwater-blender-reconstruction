import bpy,json,sys,math,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,'D:/zx/test/project/scripts')
import main_house
P=Path('D:/zx/test/project/qa');bpy.ops.wm.open_mainfile(filepath=str(P/'main-geometry-smoke.blend'))
s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
def ray(a,b):
 a,b=Vector(a),Vector(b);d=b-a
 hit,p,n,i,o,m=s.ray_cast(dg,a,d.normalized(),distance=d.length)
 return {'object':o.name,'position':list(p)} if hit else None
def sweep(name,a,b,z,radius=.18):
 av,bv=Vector(main_house.xy(a)),Vector(main_house.xy(b));d=(bv-av).normalized();normal=Vector((-d.y,d.x));rows=[]
 for i in range(13):
  c=av.lerp(bv,i/12)
  for side in (-radius,0,radius):
   p=c+normal*side;g=ray((*p,z+.20),(*p,z-.25));head=None
   if g:head=ray((*p,g['position'][2]+.025),(*p,g['position'][2]+1.95))
   rows.append({'t':i/12,'side':side,'ground':g,'head':head,'status':'PASS' if g and abs(g['position'][2]-z)<.06 and not head else 'FAIL'})
 return {'name':name,'samples':rows,'failures':[x for x in rows if x['status']=='FAIL']}
out={'wine_north_passage':sweep('internal north passage',(264,239),(264,250),-2.15),
     'bath_hall_passage':sweep('Hall to BathG',(456,323),(474,323),2.8448)}
old=ray(main_house.xyz((245,253.5),-1.2),main_house.xyz((256,253.5),-1.2))
out['west_rock_boundary']={'hit':old,'status':'PASS' if old and old['object']=='MAIN_B_cellar_0' else 'FAIL'}
rows=[];centers=[];cc=Vector(main_house.xy((473,125)))
for i in range(16):
 ob=bpy.data.objects[f'MAIN_north_spiral_{i:02}'];vs=[ob.matrix_world@v.co for v in ob.data.vertices];z=max(v.z for v in vs);top=[v for v in vs if abs(v.z-z)<1e-5];c=sum(top,Vector())/len(top);centers.append(list(c));radial=(Vector((c.x,c.y))-cc).normalized()
 for side in (-.18,0,.18):
  p=Vector((c.x,c.y))+side*radial;g=ray((*p,z+.12),(*p,z-.25));head=ray((*p,z+.025),(*p,z+1.95))
  rows.append({'step':i,'side':side,'expected_z':z,'ground':g,'head':head,'status':'PASS' if g and abs(g['position'][2]-z)<.04 and not head else 'FAIL'})
out['spiral']={'centers':centers,'samples':rows,'failures':[r for r in rows if r['status']=='FAIL']}
approaches=[]
for name,a,b,lo,hi in [('lower',main_house.xyz((469,158.5),2.8448),centers[0],2.8448,centers[0][2]),('upper',centers[-1],main_house.xyz((455,98),5.26415),5.26415,5.26415),('handoff',main_house.xyz((455,98),5.26415),main_house.xyz((431,98),5.26415),5.26415,5.26415)]:
 a,b=Vector(a),Vector(b);dv=Vector((b.x-a.x,b.y-a.y)).normalized();normal=Vector((-dv.y,dv.x));rs=[]
 for i in range(25):
  c=a.lerp(b,i/24)
  for side in (-.18,0,.18):
   xy=Vector((c.x,c.y))+side*normal;g=ray((*xy,max(lo,hi)+.20),(*xy,min(lo,hi)-.22));head=None
   if g:head=ray((*xy,g['position'][2]+.025),(*xy,g['position'][2]+1.95))
   rs.append({'t':i/24,'side':side,'ground':g,'head':head,'status':'PASS' if g and min(lo,hi)-.03<=g['position'][2]<=max(lo,hi)+.05 and not head else 'FAIL'})
 approaches.append({'name':name,'samples':rs,'failures':[r for r in rs if r['status']=='FAIL']})
out['approaches']=approaches
out['summary']={'wine_failures':len(out['wine_north_passage']['failures']),'bath_failures':len(out['bath_hall_passage']['failures']),'spiral_failures':len(out['spiral']['failures']),'approach_failures':{r['name']:len(r['failures']) for r in approaches},'old_west_boundary':out['west_rock_boundary']['status']}
out['limitations']='Architecture-only evaluated-mesh sampled width0.36m and height1.95m. Integrated guest/furniture/site navigation remains separate. Sheet05/06 graphical stair/landing trace isC.'
out['provenance']={'scene':str(P/'main-geometry-smoke.blend'),'scene_sha256':hashlib.sha256((P/'main-geometry-smoke.blend').read_bytes()).hexdigest(),'module_sha256':hashlib.sha256((P.parent/'scripts/main_house.py').read_bytes()).hexdigest(),'data_sha256':hashlib.sha256((P.parent/'data/main_house.json').read_bytes()).hexdigest(),'scope':'main-house-only iteration05 source; frozen integrated iteration04 is unchanged'}
out['check_count']=len(out['wine_north_passage']['samples'])+len(out['bath_hall_passage']['samples'])+len(out['spiral']['samples'])+sum(len(a['samples']) for a in approaches)+1
(P/'main-geometry-iteration05-check.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out['summary'],indent=2));print('SPIRAL_CENTERS',json.dumps(centers))
for k in ('wine_north_passage','bath_hall_passage','spiral'):
 if out[k]['failures']:print(k,json.dumps(out[k]['failures'][:10]))
for row in approaches:
 if row['failures']:print(row['name'],json.dumps(row['failures'][:10]))
