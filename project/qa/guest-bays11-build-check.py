import bpy,sys,json,hashlib,math,array,bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import guest_bays11 as helper
S=R/'scene/Fallingwater_integration_candidate10a.blend'
EXPECTED='dc7594d60b68effaf10b85dd1804827fc9cb16dd786656daa4da16c761b33518'
assert hashlib.sha256(S.read_bytes()).hexdigest()==EXPECTED
bpy.ops.wm.open_mainfile(filepath=str(S));scene=bpy.context.scene
def signature(o):
 h=hashlib.sha256();h.update(str((o.type,list(map(list,o.matrix_world)),o.hide_render,[(m.name,m.type) for m in o.modifiers],sorted(o.items()),[m.name if m else None for m in getattr(o.data,'materials',[])])).encode())
 if o.type=='MESH':
  v=array.array('f',[0.])*len(o.data.vertices)*3;o.data.vertices.foreach_get('co',v);h.update(v.tobytes())
  h.update(str([tuple(p.vertices) for p in o.data.polygons]).encode())
 if o.type=='CAMERA':h.update(str((o.data.lens,o.data.clip_start,o.data.clip_end)).encode())
 return h.hexdigest()
before={o.name:signature(o) for o in scene.objects}
texts={x.name:hashlib.sha256(x.as_string().encode()).hexdigest() for x in bpy.data.texts}
course=[tuple(v.co) for v in bpy.data.objects[helper.COURSES].data.vertices]
def make_bvh():
 dep=bpy.context.evaluated_depsgraph_get();vs=[];fs=[];owners=[];per={}
 for o in scene.objects:
  if o.type!='MESH' or o.hide_render or o.name.startswith(('REF_','QA_')):continue
  cs=[o.matrix_world@Vector(q) for q in o.bound_box]
  if any(max(q[k] for q in cs)<lo or min(q[k] for q in cs)>hi for k,(lo,hi) in enumerate([(-7,5),(43,57),(8,12)])):continue
  eo=o.evaluated_get(dep);me=eo.to_mesh();vv=[eo.matrix_world@v.co for v in me.vertices];ff=[tuple(p.vertices) for p in me.polygons]
  per[o.name]=BVHTree.FromPolygons(vv,ff);off=len(vs);vs+=vv;fs +=[tuple(off+i for i in f) for f in ff];owners +=[o.name]*len(ff);eo.to_mesh_clear()
 return BVHTree.FromPolygons(vs,fs),owners,per
def ray(index,origin,direction,length=10):
 bvh,owners,_=index;co,no,face,dist=bvh.ray_cast(Vector(origin),Vector(direction),length)
 return None if co is None else {'object':owners[face],'face':face,'point':list(co),'normal':list(no),'distance':dist}
def body(index,xy,z=8.4002):
 failures=[]
 for dx,dy in [(0,0),(.18,0),(-.18,0),(0,.18),(0,-.18)]:
  floor=ray(index,(xy[0]+dx,xy[1]+dy,z+.1),(0,0,-1),.3)
  if not floor or abs(floor['point'][2]-z)>.004 or floor['normal'][2]<.5:failures.append({'kind':'FLOOR','offset':[dx,dy],'hit':floor})
  hit=ray(index,(xy[0]+dx,xy[1]+dy,z+.05),(0,0,1),1.90)
  if hit:failures.append({'kind':'BODY_1p95','offset':[dx,dy],'hit':hit})
 return failures
old_index=make_bvh();print('BASE_BVH_READY',flush=True)
poses=[];frame0=scene.frame_current
for name in ('CAM_TOUR','CAM_TOUR_SUPPLEMENTAL'):
 cam=bpy.data.objects.get(name)
 if not cam:continue
 # Save every actual integer pose in the local room, never re-plan the tour.
 for frame in range(scene.frame_start,scene.frame_end+1):
  scene.frame_set(frame);q=cam.matrix_world.translation.copy()
  if -5<q.x<3.5 and 43<q.y<55 and 9.9<q.z<10.2:poses.append({'camera':name,'frame':frame,'pose':list(q)})
for o in scene.objects:
 if o.type=='CAMERA' and o.name.startswith('CAM_GUEST_L1_THEATER_'):poses.append({'camera':o.name,'frame':frame0,'pose':list(o.matrix_world.translation)})
scene.frame_set(frame0)
for p in poses:p['before_failure']=body(old_index,p['pose'],p['pose'][2]-1.6)
report=helper.apply(scene);index=make_bvh();print('APPLIED',len(report['created']),flush=True)
after={o.name:signature(o) for o in scene.objects}
allowed=set(report['changed']+report['removed']);unauthorized=[n for n,h in before.items() if n not in allowed and after.get(n)!=h]
selected={i for ids in report['course_block_ids'].values() for b in ids for i in range(b*8,b*8+8)}
now=bpy.data.objects[helper.COURSES].data.vertices
course_bad=[i for i,v in enumerate(course) if i not in selected and tuple(now[i].co)!=v]
report['protection']={'before_objects':len(before),'after_objects':len(after),'unauthorized_changes':unauthorized,'unselected_course_vertices_changed':course_bad,'selected_course_vertices':len(selected),'unselected_course_vertices':len(course)-len(selected),'embedded_texts_unchanged':texts=={x.name:hashlib.sha256(x.as_string().encode()).hexdigest() for x in bpy.data.texts}}
assert not unauthorized and not course_bad and report['protection']['embedded_texts_unchanged']
g=helper.design();measurements=[]
for id,pa,pb,sa,sb,target in [('NORTH',(191.7,126.3),(215.9,167.6),'GUEST_L1_THEATER_DIAGONAL_BACK_pier_0','GUEST_L1_CARPORT_RETAINED_PIER_2_pier_end',2.486025),('MIDDLE',(202.4,185),(223.4,220.5),'GUEST_L1_CARPORT_RETAINED_PIER_2_pier_end','GUEST_BAYS11_MIDDLE_short_return_AB',2.162175)]:
 a,b=helper.xy3(helper.p(pa),9.5),helper.xy3(helper.p(pb),9.5);d=(b-a).normalized();mid=(a+b)/2;hits=[]
 for name,dr in [(sa,-d),(sb,d)]:
  co,no,face,dist=index[2][name].ray_cast(mid,dr,10);hits.append(None if co is None else {'object':name,'face':face,'point':list(co),'normal':list(no)})
 val=(Vector(hits[1]['point'])-Vector(hits[0]['point'])).dot(d) if all(hits) else None
 measurements.append({'id':id,'hits':hits,'axis':list(d),'nominal_m':target,'actual_evaluated_mesh_m':val,'error_m':None if val is None else val-target,'numerical_only_within_20mm':val is not None and abs(val-target)<=.02,'qualification':'PENDING_INDEPENDENT_SOURCE_AND_MESH_REVIEW; numerical agreement is not final PASS'})
report['measurements']=measurements
for p in poses:p['after_failure']=body(index,p['pose'],p['pose'][2]-1.6)
regressions=[p for p in poses if not p['before_failure'] and p['after_failure']]
report['saved_pose_regression']={'samples':len(poses),'new_failures':regressions,'before_failures':sum(bool(p['before_failure']) for p in poses),'after_failures':sum(bool(p['after_failure']) for p in poses),'checks':poses}
floor=[]
for key in ('north_glazing','middle_glazing'):
 a,b=map(Vector,report[key]);t=Vector((-(b-a).y,(b-a).x)).normalized()
 for i in range(21):
  q=a+(b-a)*i/20+t*.20;hit=ray(index,(*q,8.50),(0,0,-1),.3)
  floor.append({'group':key,'xy':list(q),'hit':hit,'pass':bool(hit and abs(hit['point'][2]-8.4)<.004 and hit['normal'][2]>.5)})
report['inside_floor_support']=floor
door=[];q=Vector(report['door_center']);t=Vector(report['door_cross_axis'])
for i in range(21):
 pos=q+t*(-.5+i*.05);door.append({'xy':list(pos),'failure':body(index,pos)})
report['new_north_door_body_samples']=door
# Mesh closure and signed volume for the new components and changed cores.
meshqa=[]
for name in report['created']+[n for n in report['changed'] if n!=helper.COURSES]:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data)
 meshqa.append({'object':name,'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_local_volume_m3':bm.calc_volume(signed=True)});bm.free()
report['mesh_closure']=meshqa
# Triangle intersections against protected theater furniture, not bbox alone.
collisions=[]
for name in ['GUEST_L1_CARPORT_RETAINED_PIER_1_pier_end','GUEST_L1_CARPORT_RETAINED_PIER_2_pier_end']+report['created']:
 for fn,fb in index[2].items():
  if not fn.startswith('FW_FURN_GUEST_L1_THEATER'):continue
  overlap=index[2][name].overlap(fb)
  if overlap:collisions.append({'architecture':name,'furniture':fn,'intersecting_triangle_pairs':len(overlap),'previously_intersected':bool(old_index[2].get(name) and old_index[2][name].overlap(old_index[2][fn]))})
report['protected_furniture_intersections']=collisions
report['source_scene_sha256']=EXPECTED;report['helper_sha256']=hashlib.sha256((R/'scripts/guest_bays11.py').read_bytes()).hexdigest()
report['status']='CANDIDATE_ONLY_GEOMETRY_CHECKED_NOT_VISUAL_OR_DIMENSION_ACCEPTED'
assert all(x['non_manifold_edges']==0 and x['signed_local_volume_m3']>0 for x in meshqa)
out=R/'scene/Fallingwater_guest_bays_candidate11a.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out),check_existing=False)
report['candidate_scene']=str(out);report['candidate_sha256']=hashlib.sha256(out.read_bytes()).hexdigest();report['candidate_bytes']=out.stat().st_size
assert hashlib.sha256(S.read_bytes()).hexdigest()==EXPECTED
(R/'qa/guest-bays11-build-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['candidate_sha256','measurements','protection','protected_furniture_intersections']},indent=2));print('DONE',flush=True)
