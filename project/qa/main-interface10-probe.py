"""Read-only full09 original-pixel geometry and source identity probes."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import closest_point_on_tri
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import main_house as mh
SRC=R/'scene/Fallingwater_iteration09.blend';SHA='489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SHA
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene
s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.frame_set(48)
dg=bpy.context.evaluated_depsgraph_get()
def src(p):return [p.x/mh.SX+327,540-p.y/mh.SY]
def rec(hit):
 h,p,n,f,o,_=hit
 if not h:return None
 return dict(object=o.name,point=list(p),normal=list(n),evaluated_polygon=f,source_plan_px=src(p))
def scene_cast(o,d,dist=200):return s.ray_cast(dg,o,d,distance=dist)
def triangle(ob,point,face):
 e=ob.evaluated_get(dg);me=e.to_mesh();me.calc_loop_triangles();out=[]
 for t in me.loop_triangles:
  if t.polygon_index!=face:continue
  vv=[e.matrix_world@me.vertices[i].co for i in t.vertices]
  nearest=closest_point_on_tri(point,*vv)
  if (nearest-point).length<.0001:out.append(dict(vertices=[list(v) for v in vv],source_plan_px=[src(v) for v in vv],point_distance_m=(nearest-point).length,material=me.materials[t.material_index].name if len(me.materials)>t.material_index else None))
 e.to_mesh_clear();return out
bvhs={};bounds={};polys={}
for ob in s.objects:
 if ob.type!='MESH' or not ob.name.startswith(('MAIN_','FW_FURN_MAIN_')) or len(ob.data.vertices)>1000:continue
 e=ob.evaluated_get(dg);me=e.to_mesh();vv=[e.matrix_world@v.co for v in me.vertices]
 if not vv:e.to_mesh_clear();continue
 bounds[ob.name]=[[min(v[k] for v in vv),max(v[k] for v in vv)] for k in range(3)]
 bvhs[ob.name]=BVHTree.FromPolygons(vv,[tuple(f.vertices) for f in me.polygons]);e.to_mesh_clear()
groups={'CAM_MAIN_L1_LOGGIA_A':[(100,475),(240,445),(293,429),(302,432),(335,416),(536,340),(552,350),(543,337),(500,304),(494,275),(499,293),(484,250),(500,255),(477,247)],'CAM_MAIN_L2_MASTER_A':[(170,465),(204,458),(140,472),(175,457),(218,452),(503,183),(531,207),(460,152),(537,164),(541,366),(554,384)]}
out=[]
for name,pixels in groups.items():
 cam=s.objects[name];co=cam.data.view_frame(scene=s);xmin,xmax=min(v.x for v in co),max(v.x for v in co);ymin,ymax=min(v.y for v in co),max(v.y for v in co)
 for x,y in pixels:
  origin=cam.matrix_world.translation;direction=(cam.matrix_world.to_quaternion()@Vector((xmin+(x+.5)/960*(xmax-xmin),ymax-(y+.5)/540*(ymax-ymin),co[0].z))).normalized();hit=scene_cast(origin,direction)
  rr=dict(camera=name,pixel=[x,y],ray_origin=list(origin),ray_direction=list(direction),first_hit=rec(hit))
  if hit[0]:rr['first_hit']['triangles']=triangle(hit[4],hit[1],hit[3])
  z=.122 if '_LOGGIA_' in name else 2.8668
  expected=origin+direction*((z-origin.z)/direction.z)
  rr.update(floor_plane_z=z,floor_plane_point=list(expected),floor_plane_source_px=src(expected),floor_support=rec(scene_cast(expected+Vector((0,0,.07)),Vector((0,0,-1)),10)),upward_from_floor=rec(scene_cast(expected+Vector((0,0,.08)),Vector((0,0,1)),10)))
  rr['local_first_surfaces']=[];rr['local_floor_surfaces']=[];rr['nearby_architecture']=[]
  for nm,bvh in bvhs.items():
   if hit[0]:
    p,n,f,dist=bvh.ray_cast(hit[1]-direction*.035,direction,.070)
    if p is not None:rr['local_first_surfaces'].append(dict(object=nm,point=list(p),normal=list(n),evaluated_polygon=f,distance_from_first_m=(p-hit[1]).length))
   p,n,f,dist=bvh.ray_cast(expected+Vector((0,0,.07)),Vector((0,0,-1)),.25)
   if p is not None:rr['local_floor_surfaces'].append(dict(object=nm,point=list(p),normal=list(n),evaluated_polygon=f))
   b=bounds[nm]
   if nm.startswith('MAIN_') and b[0][0]-.1<=expected.x<=b[0][1]+.1 and b[1][0]-.1<=expected.y<=b[1][1]+.1 and b[2][0]-.1<=z<=b[2][1]+.1:rr['nearby_architecture'].append(nm)
  out.append(rr)
result=dict(status='READ_ONLY_PIXELS_AND_TRIANGLES_SOURCE_IDENTITY_PENDING',source_scene=str(SRC),sha256=SHA,source_script_sha256=hashlib.sha256((R/'scripts/main_house.py').read_bytes()).hexdigest(),actual_images_opened=list(groups),resolution=[960,540],frame=48,results=out,bounds=bounds)
(R/'qa/main-interface10-probe.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps([{'camera':x['camera'],'pixel':x['pixel'],'first':{k:v for k,v in (x['first_hit'] or {}).items() if k!='triangles'},'floor_source':x['floor_plane_source_px'],'support':x['floor_support'],'local_floor':[y['object'] for y in x['local_floor_surfaces']]} for x in out],indent=2))
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SHA
