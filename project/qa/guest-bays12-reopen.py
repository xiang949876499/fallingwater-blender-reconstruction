"""Independently reopen before apply; verify real finished faces and joints."""
import bpy,sys,json,hashlib,ast,array,math,bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));import guest_bays11 as h;import guest_bays12 as fix
for file in ('guest-bays11-build-check.py','guest-bays12-build-check.py'):
 tree=ast.parse((R/'qa'/file).read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<own readonly functions>','exec'))
result=json.loads((R/'qa/guest-bays12-build-check.json').read_text(encoding='utf-8'));src=Path(result['candidate']);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(src)==result['candidate_sha256']
assert sha(R/'scripts/guest_bays12.py')==result['helper_sha256']
bpy.ops.wm.open_mainfile(filepath=str(src));scene=bpy.context.scene;dep=bpy.context.evaluated_depsgraph_get();stone=scene.objects[fix.COURSES]
saved_fp={o.name:signature(o) for o in scene.objects}
panels=result['report']['panels'];left=component(panels[0]['object'],panels[0]['course_block_ids']);right=component(panels[1]['object'],panels[1]['course_block_ids'])
g=h.design();d=h.xy3(g['d']);t=h.xy3(g['t']);mid=h.xy3((h.p((191.7,126.3))+h.p((215.9,167.6)))/2);checks=[]
for old in result['actual_complete_surface_samples']:
 origin=mid+t*old['station_m'];origin.z=old['z'];hits=[]
 for (bvh,owners),dr in [(left,-d),(right,d)]:
  co,no,face,dist=bvh.ray_cast(origin,dr,5);hits.append(None if co is None else {'point':list(co),'normal':list(no),'object':owners[face],'face':face})
 value=(Vector(hits[1]['point'])-Vector(hits[0]['point'])).dot(d) if all(hits) else None
 checks.append({'station_m':old['station_m'],'z':old['z'],'actual_finished_span_m':value,'hits':hits,'difference_from_before_save_m':None if value is None else value-old['completed_face_span_m'],'pass':value is not None and abs(value-2.486025)<=.02})
assert all(x['pass'] and abs(x['difference_from_before_save_m'])<.000001 for x in checks)
print('REOPEN_FINISH_PASS',len(checks),flush=True)
# Test actual occupied union at the two construction junction centerlines,
# not an unrelated first surface several meters away. Course/core members are
# individually closed and their volumes overlap; a first exit normal proves
# the point lies inside that closed component. On-surface distance counts contact.
# Containment must test each closed solid independently: a combined overlapping
# core+stone BVH can encounter an internal stone-entry face before core exit.
# That entry does not prove the query is outside the core. Finished-face rays
# above intentionally use the combined BVH from an exterior origin instead.
neighbors=[(panels[0]['object'],component(panels[0]['object'])[0]),
           (panels[1]['object'],component(panels[1]['object'])[0])]
for ob in scene.objects:
 if ob.type=='MESH' and ob.name.startswith('GUEST_BAYS11_NORTH_'):neighbors.append((ob.name,component(ob.name)[0]))
direction=Vector((.371,.593,.714)).normalized()
def occupies(point,tree):
 near,normal,face,dist=tree.find_nearest(point)
 if near is not None and dist<.00001:return {'kind':'CONTACT','face':face,'distance':dist}
 co,no,face,dist=tree.ray_cast(point,direction,10)
 return {'kind':'INSIDE_CLOSED_COMPONENT','exit_point':list(co),'exit_normal':list(no),'face':face} if co is not None and no.dot(direction)>.00001 else None
old=json.loads((R/'qa/guest-bays11-build-check.json').read_text(encoding='utf-8'));a,b=map(Vector,old['north_glazing']);axis=(b-a).normalized();joints=[]
for label,end in [('north-wall/window',a),('north-return/pier2',b)]:
 for step in range(41):
  offset=-.02+step*.001;q=end+axis*offset
  for z in (8.42,8.45,8.6,8.8,9.5,10.45,10.54):
   point=Vector((*q,z));hit=None
   for name,tree in neighbors:
    found=occupies(point,tree)
    if found:hit=dict(found,object=name);break
   joints.append({'junction':label,'offset_m':offset,'z':z,'point':list(point),'occupied':hit})
assert all(x['occupied'] for x in joints),[x for x in joints if not x['occupied']][:8]
print('JOINT_OCCUPANCY_PASS',len(joints),flush=True)
# Source reproduction happens only AFTER saved candidate probes. Never reapply
# the correction onto the candidate before checking its actual saved geometry.
base=R/'scene/Fallingwater_guest_bays_candidate11b.blend';assert sha(base)==result['source11b_sha256']
bpy.ops.wm.open_mainfile(filepath=str(base));scene=bpy.context.scene;fix.apply(scene)
fresh_fp={o.name:signature(o) for o in scene.objects};diff=sorted(n for n in set(fresh_fp)|set(saved_fp) if fresh_fp.get(n)!=saved_fp.get(n));assert not diff,diff
out={'status':'PASS_SAVED_FINISHED_SURFACES_AND_JOINTS_SOURCE_REPRODUCED','candidate_sha256':result['candidate_sha256'],'helper_sha256':result['helper_sha256'],'saved_read_before_reapply':True,'actual_finished_surface_checks':checks,'actual_finished_surface_count':len(checks),'all_finished_samples_pass_20mm':True,'all_finished_values_equal_before_save':True,'joint_occupied_union_checks':joints,'joint_occupied_union_count':len(joints),'all_joints_occupied':True,'source_reproduction_every_object_fingerprint_equal':True,'source11b_unchanged':sha(base)==result['source11b_sha256'],'candidate_unchanged':sha(src)==result['candidate_sha256'],'scene_saved':False,'rendered':False}
(R/'qa/guest-bays12-reopen.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('REPRODUCTION_PASS',len(fresh_fp),flush=True)
