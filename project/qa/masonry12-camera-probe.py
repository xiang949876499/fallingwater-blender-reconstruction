import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];Q=R/'qa';sys.path[:0]=[str(R/'scripts'),str(Q)]
import shrub08_auditlib as audit
record=json.loads((Q/'masonry12-build-check.json').read_text(encoding='utf-8'));p=Path(record['candidate'])
assert hashlib.sha256(p.read_bytes()).hexdigest()==record['candidate_sha256']
bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;s.frame_set(48);dep=bpy.context.evaluated_depsgraph_get()
cfg=json.loads((Q/'masonry12-camera-settings.json').read_text(encoding='utf-8'))['CAM_WATER_DETAIL']
eye=Vector(cfg['location']);target=Vector(cfg['target']);look=(target-eye).normalized();right=look.cross(Vector((0,0,1))).normalized();up=right.cross(look).normalized()
half=s.objects['CAM_WATER_DETAIL'].data.sensor_width/(cfg['lens']*2);vhalf=half*540/960
pixels=[]
for n in record['application']['added']+list(record['application']['guards']):
 for v in s.objects[n].data.vertices:
  q=s.objects[n].matrix_world@v.co-eye;depth=q.dot(look)
  pixels.append([(.5+.5*q.dot(right)/(depth*half))*960,(.5-.5*q.dot(up)/(depth*vhalf))*540])
roi=[[min(q[i] for q in pixels),max(q[i] for q in pixels)] for i in range(2)]
print('PROPOSED_ROI',roi,'sensor_width',s.objects['CAM_WATER_DETAIL'].data.sensor_width,flush=True)
assert 0<=roi[0][0]<roi[0][1]<=960 and 0<=roi[1][0]<roi[1][1]<=540
near=[]
for obj in s.objects:
 if obj.type!='MESH' or obj.hide_render:continue
 bb=audit.bounds(obj)
 if all(bb[2*i]-.4<=eye[i]<=bb[2*i+1]+.4 for i in range(3)):near.append(obj)
if near:
 tree,owners=audit.world_bvh(near,True);hit,norm,index,distance=tree.find_nearest(eye);nearest={'object':owners[index],'distance_m':distance};assert distance>.18
else:nearest={'distance_m':'>0.4 from all mesh bounding boxes'}
rays=[]
for z in (5.5,6.4,7.35,8.3,9.2):
 for y in (8.6,9.3,10.15):
  goal=Vector((-.94,y,z));direction=goal-eye;length=direction.length
  hit,point,normal,index,obj,matrix=s.ray_cast(dep,eye,direction.normalized(),distance=length+.5)
  rays.append({'aim':list(goal),'first_object':obj.name if obj else None,'point':list(point) if hit else None})
hit,point,normal,index,obj,matrix=s.ray_cast(dep,eye,look,distance=30)
out={'status':'PASS_CAMERA_FOOT_AND_FULL_TOWER_FRAMING','candidate_sha256':record['candidate_sha256'],'settings':cfg,'camera_name':'CAM_WATER_DETAIL',
     'saved_camera_modified':False,'rendered':False,'tower_and_guard_bounds_960x540':roi,'nearest_scene_surface_to_external_camera':nearest,
     'center_ray_first_object':obj.name if obj else None,'target_visibility_sample_rays':rays,
     'usage':'Apply exact same external override on iteration10 source and candidate12a. CAM_HERO is intentionally absent and retains saved settings.'}
(Q/'masonry12-camera-probe.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
