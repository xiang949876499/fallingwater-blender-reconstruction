"""Finite face, joints, saved camera/path and C-seat candidate checks. No render."""
import bpy,sys,json,hashlib,array,ast,math,bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import guest_bays11 as helper
tree=ast.parse((R/'qa/guest-bays11-build-check.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<own QA functions>','exec'))
a=json.loads((R/'qa/guest-bays11-build-check.json').read_text(encoding='utf-8'))
S=Path(a['candidate_scene']);assert hashlib.sha256(S.read_bytes()).hexdigest()==a['candidate_sha256']
bpy.ops.wm.open_mainfile(filepath=str(S));scene=bpy.context.scene;before={o.name:signature(o) for o in scene.objects};index=make_bvh()
print('REOPEN_BVH_READY',flush=True)
g=helper.design();d=helper.xy3(g['md']);ab=(g['ab'][0]+g['ab'][1])/2
ma=helper.p((202.4,185));offset=(ab-ma)-g['md']*((ab-ma).dot(g['md']))
dimensions=[]
for frac in (.15,.5,.85):
 q=g['ab'][0]+(g['ab'][1]-g['ab'][0])*frac;origin=helper.xy3(q,9.5)-d*.7;hits=[]
 for name,dr in [('GUEST_L1_CARPORT_RETAINED_PIER_2_pier_end',-d),('GUEST_BAYS11_MIDDLE_short_return_AB',d)]:
  co,no,face,dist=index[2][name].ray_cast(origin,dr,10);hits.append(None if co is None else {'object':name,'point':list(co),'normal':list(no),'face':face})
 val=(Vector(hits[1]['point'])-Vector(hits[0]['point'])).dot(d) if all(hits) else None
 angle=math.degrees(math.acos(min(1,abs(Vector(hits[0]['normal']).dot(Vector(hits[1]['normal'])))))) if all(hits) else None
 dimensions.append({'AB_fraction':frac,'hits':hits,'span_m':val,'normal_parallelism_angle_degrees':angle,'parallel_shift_from_old_locator_m':list((q-ma)-g['md']*((q-ma).dot(g['md']))),'qualification':'C_DIAGNOSTIC_NONPARALLEL_FACES_NOT_PRINTED_DIMENSION_PASS'})
# At perimeter endpoints, the existing stone volume occupies the vertical ray;
# separately test the preserved actual slab underneath and clear interior steps.
floor=index[2]['GUEST_L1_THEATER_FLOOR'];floorrows=[]
for row in a['inside_floor_support']:
 q=row['xy'];co,no,face,dist=floor.ray_cast(Vector((*q,8.5)),Vector((0,0,-1)),.4)
 floorrows.append({'xy':q,'floor_hit':list(co) if co is not None else None,'pass':co is not None and abs(co.z-8.4)<.004,'original_full_scene_hit':row['hit']})
# Check wall/frame boundaries horizontally at all inhabited wall heights.
joints=[]
for key in ('north_glazing','middle_glazing'):
 v0,v1=map(Vector,a[key]);axis=(v1-v0).normalized();cross=Vector((-axis.y,axis.x))
 for end in (v0,v1):
  for along in (-.015,0,.015):
   q=end+axis*along
   for z in (8.45,8.60,8.80,9.5,10.45,10.54):
    hit=ray(index,(*(q-cross*.4),z),(*cross,0),.8)
    joints.append({'group':key,'joint':list(end),'along_m':along,'z':z,'hit':hit,'closed':hit is not None})
names=[n for n in scene.objects if n.type=='CAMERA']
camera_inventory=[{'name':c.name,'pose':list(c.matrix_world.translation),'animated':bool(c.animation_data and c.animation_data.action)} for c in names]
texts=[t.name for t in bpy.data.texts];route_texts=[t for t in bpy.data.texts if 'TOUR' in t.name]
route_inventory=[{'name':t.name,'prefix':t.as_string()[:500]} for t in route_texts]
roots=[bpy.data.objects[f'FW_FURN_GUEST_L1_THEATER_theater_seat_{i:02}'] for i in (8,9)]
groups={r.name:[r]+list(r.children_recursive) for r in roots};owned={o.name for group in groups.values() for o in group}
oldpos={r.name:r.location.copy() for r in roots};t=helper.xy3(g['t'])
protected_bvh=[];vs=[];fs=[];owners=[]
deps=bpy.context.evaluated_depsgraph_get()
for name in index[2]:
 if name in owned or name=='GUEST_L1_THEATER_FLOOR':continue
 ob=bpy.data.objects[name];eo=ob.evaluated_get(deps);me=eo.to_mesh();off=len(vs)
 vs.extend(eo.matrix_world@v.co for v in me.vertices);fs.extend(tuple(off+i for i in p.vertices) for p in me.polygons);owners.extend([name]*len(me.polygons));eo.to_mesh_clear()
fixed=BVHTree.FromPolygons(vs,fs)
def moving_bvh():
 deps=bpy.context.evaluated_depsgraph_get();vv=[];ff=[];own=[]
 for group in groups.values():
  for ob in group:
   if ob.type!='MESH':continue
   eo=ob.evaluated_get(deps);me=eo.to_mesh();off=len(vv);vv.extend(eo.matrix_world@v.co for v in me.vertices);ff.extend(tuple(off+i for i in p.vertices) for p in me.polygons);own.extend([ob.name]*len(me.polygons));eo.to_mesh_clear()
 return BVHTree.FromPolygons(vv,ff),own
attempts=[];chosen=None
for step in range(0,41):
 shift=step*.05
 for root in roots:root.location=oldpos[root.name]+t*shift
 bpy.context.view_layer.update();moving,mown=moving_bvh();pairs=moving.overlap(fixed)
 collisions=sorted({(mown[i],owners[j]) for i,j in pairs})
 attempts.append({'distance_along_interior_axis_m':shift,'collisions':collisions})
 print('SEAT_SHIFT',round(shift,2),'COLLISIONS',len(collisions),flush=True)
 if not pairs:chosen=shift;break
assert chosen is not None,'No bounded <=2m C-chair translation resolves actual triangles'
index2=make_bvh();feet=[]
for group in groups.values():
 for ob in group:
  if ob.type!='MESH' or '_leg' not in ob.name:continue
  corners=[ob.matrix_world@v.co for v in ob.data.vertices];q=sum(corners,Vector())/len(corners);bottom=min(v.z for v in corners)
  # Start above the actual slab; a ray beginning below a coincident contact
  # plane cannot hit its top. Restrict to the slab to avoid self-hitting the leg.
  co,no,face,dist=floor.ray_cast(Vector((q.x,q.y,bottom+.02)),Vector((0,0,-1)),.08)
  hit=None if co is None else {'object':'GUEST_L1_THEATER_FLOOR','point':list(co),'normal':list(no),'face':face}
  feet.append({'leg':ob.name,'bottom_z':bottom,'support':hit,'pass':hit is not None and abs(bottom-hit['point'][2])<.004})
door=[]
for row in a['new_north_door_body_samples']:door.append({'xy':row['xy'],'before_failure':row['failure'],'after_failure':body(index2,row['xy'])})
cams=[{'camera':row['camera'],'pose':row['pose'],'before_failure':row['after_failure'],'after_failure':body(index2,row['pose'],row['pose'][2]-1.6)} for row in a['saved_pose_regression']['checks']]
after={o.name:signature(o) for o in scene.objects};changed=[n for n in before if after.get(n)!=before[n]]
assert set(changed)<=owned and set(after)==set(before)
assert all(p['pass'] for p in feet),feet
assert not any(not p['before_failure'] and p['after_failure'] for p in door+cams)
out=R/'scene/Fallingwater_guest_bays_candidate11b.blend';assert not out.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(out),check_existing=False)
result={'source11a_scene':str(S),'source11a_sha256':a['candidate_sha256'],'scene11b':str(out),'scene11b_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'scene11b_bytes':out.stat().st_size,'middle_finite_face_station_diagnostics':dimensions,'original_middle_locator_miss_preserved':True,'floor_support':floorrows,'wall_joint_rays':joints,'camera_inventory':camera_inventory,'embedded_text_names':texts,'embedded_route_inventory':route_inventory,'seat_evidence':'C: room_theater explicitly unverified current seats/projector; algorithmic fixed rows, not archival coordinates','seat_search_50mm_step_attempts':attempts,'seat_translation_m':list(t*chosen),'seat_axis_distance_m':chosen,'seat_roots':{r.name:{'old':list(oldpos[r.name]),'new':list(r.location)} for r in roots},'seat_actual_foot_contacts':feet,'target_object_changes':changed,'non_target_fingerprints_unchanged':True,'north_door_regression':door,'unchanged_saved_camera_geometry':cams,'status':'LOCAL_CANDIDATE_WITH_PREEXISTING_CAMERA_FAILS_AND_MIDDLE_DIMENSION_NOT_PASS','rendered':False}
(R/'qa/guest-bays11-reopen-and-seat-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:result[k] for k in ['scene11b_sha256','scene11b_bytes','seat_translation_m','middle_finite_face_station_diagnostics']},indent=2));print('JOINT_MISSES',sum(not x['closed'] for x in joints));print('DONE',flush=True)
