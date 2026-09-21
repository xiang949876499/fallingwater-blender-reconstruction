import bpy,json,math
from pathlib import Path
from mathutils import Vector
p=Path('D:/zx/test/project');rooms=json.loads((p/'qa/guest-dimension-fixes-rooms.json').read_text(encoding='utf-8'))
scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
from mathutils.bvhtree import BVHTree
structural=[]
for obj in scene.objects:
 if obj.type!='MESH' or 'open_leaf' in obj.name or 'handle' in obj.name or obj.name=='GUEST_LAYERED_SANDSTONE_COURSES':continue
 ev=obj.evaluated_get(deps);me=ev.to_mesh();vs=[tuple(obj.matrix_world@v.co) for v in me.vertices]
 if vs and len(me.polygons):structural.append((obj.name,BVHTree.FromPolygons(vs,[tuple(x.vertices) for x in me.polygons],all_triangles=False)))
 ev.to_mesh_clear()
def structural_ray(origin,direction,distance):
 hits=[]
 for name,bvh in structural:
  loc,norm,idx,dist=bvh.ray_cast(Vector(origin),Vector(direction),distance)
  if loc is not None:hits.append((dist,name,loc))
 if not hits:return None
 _,name,loc=min(hits,key=lambda x:x[0]);return {'object':name,'z':loc.z}

def inside(pt,poly):
 x,y=pt;flag=False;j=len(poly)-1
 for i,(xi,yi) in enumerate(poly):
  xj,yj=poly[j]
  if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi)+xi:flag=not flag
  j=i
 return flag
records=[]
for r in rooms:
 if r['id'] not in ['GUEST_L1_GUEST_ROOM','GUEST_L1_BATH','GUEST_L1_BOILER','GUEST_B1_BATH','GUEST_B1_LAUNDRY']:continue
 poly=r['polygon'];xmin=min(t[0] for t in poly);xmax=max(t[0] for t in poly);ymin=min(t[1] for t in poly);ymax=max(t[1] for t in poly)
 samples=[]
 for i in range(5):
  for j in range(5):
   x=xmin+(xmax-xmin)*(i+.5)/5;y=ymin+(ymax-ymin)*(j+.5)/5
   if not inside((x,y),poly):continue
   found,loc,norm,idx,obj,mat=scene.ray_cast(deps,Vector((x,y,r['z']+.12)),Vector((0,0,-1)),distance=.3)
   first_scene_hit={'object':obj.name,'z':loc.z} if found else None
   floor=structural_ray((x,y,r['z']+.12),(0,0,-1),.3)
   fz=floor['z'] if floor else r['z']
   found,loc,norm,idx,obj,mat=scene.ray_cast(deps,Vector((x,y,fz+.12)),Vector((0,0,1)),distance=4)
   ceiling=structural_ray((x,y,fz+.12),(0,0,1),4)
   if ceiling:ceiling['clearance_m']=ceiling['z']-fz
   ok=floor and ceiling and abs(floor['z']-r['z'])<.025 and ceiling['clearance_m']>=1.95 and ceiling['clearance_m']<=r['height']+.10
   samples.append({'xy':[x,y],'first_scene_hit':first_scene_hit,'movable_door_leaf_at_sample':bool(first_scene_hit and 'open_leaf' in first_scene_hit['object']),'floor':floor,'ceiling':ceiling,'status':'PASS' if ok else 'FAIL'})
 records.append({'room':r['id'],'status':'PASS' if all(s['status']=='PASS' for s in samples) else 'FAIL','samples':samples})
report={'status':'PASS' if all(r['status']=='PASS' for r in records) else 'FAIL','method':'5x5 candidategrid clipped to eachchangedroompolygon; actual down/up scene.ray_cast to floor and overheadmesh. Floorwithin25mm,clearance>=1.95m and <=recordedheight+100mm. Movable open door leaves/handles and decorative ashlar excluded only for structural floor/ceiling queries; first all-scene hit separately retained, so occupied sample is not silently erased. No furniture/site.','rooms':records}
(p/'qa/guest-dimension-fixes-surfaces.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':report['status'],'rooms':[(r['room'],len(r['samples']),sum(s['status']=='FAIL' for s in r['samples'])) for r in records],'failures':[s for r in records for s in r['samples'] if s['status']=='FAIL']}))
