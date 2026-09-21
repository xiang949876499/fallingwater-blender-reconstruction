"""Bounded three-segment candidate with actual saved pose/key reopen; no render."""
import bpy,sys,json,hashlib,array,shutil,copy,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import master_navigation10 as nav
import guest_circulation10_routes as guest
SRC=R/'scene/Fallingwater_integration_candidate10a.blend'
OUT=R/'scene/Fallingwater_master_navigation_candidate10a.blend'
W=R/'qa/master-navigation10-final-workspace'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC)=='dc7594d60b68effaf10b85dd1804827fc9cb16dd786656daa4da16c761b33518'
assert not OUT.exists()
protected=[SRC]+[R/'scripts'/n for n in ('main_house.py','furnishings.py','tour.py','master_detail10.py','master_bath_detail10.py','guest_circulation10_routes.py')]+[R/'data'/n for n in ('main_house.json','guest_house.json','guest_circulation10.json','camera-settings-reviewed.json')]
protected_before={str(p):sha(p) for p in protected}
(W/'data').mkdir(parents=True,exist_ok=True);(W/'qa').mkdir(exist_ok=True)
for name in ('main_house.json','guest_house.json','guest_circulation10.json'):
 shutil.copyfile(R/'data'/name,W/'data'/name)
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene
old_settings=(s.frame_current,s.frame_start,s.frame_end,s.camera.name,s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.view_settings.exposure,s.cycles.samples)
def fp():
 out={};meshes={}
 for o in s.objects:
  h=hashlib.sha256(str([list(row) for row in o.matrix_world]).encode())
  if o.type=='MESH':
   key=o.data.as_pointer()
   if key not in meshes:
    vs=array.array('f',[0.]*(len(o.data.vertices)*3));ls=array.array('i',[0]*len(o.data.loops));o.data.vertices.foreach_get('co',vs);o.data.loops.foreach_get('vertex_index',ls);meshes[key]=hashlib.sha256(vs.tobytes()+ls.tobytes()).digest()
   h.update(meshes[key])
  h.update(str([m.name if m else None for m in getattr(o.data,'materials',[])]).encode())
  if o.type=='CAMERA':h.update(str((o.data.lens,o.data.sensor_width,o.data.shift_x,o.data.shift_y,o.data.clip_start,o.data.clip_end)).encode())
  if o.type=='LIGHT':h.update(str((o.data.energy,list(o.data.color))).encode())
  out[o.name]=h.hexdigest()
 return out
before=fp();rooms0=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
tour,rooms,gs=guest.prepare(W,s,rooms0,read_only=True)
guest_before={n:getattr(tour,n) for n in ('Probe','hinted_connection','stair_connection','room_candidates','stair_space_anchors','connector_shot')}
spec=nav.apply(tour,s,rooms,W);p=tour.master_navigation10_probe
preserved={n:getattr(tour,n) is fn for n,fn in guest_before.items() if n not in ('hinted_connection','room_candidates')}
assert all(preserved.values())
assert tour.master_navigation10_prior['hinted_connection'] is guest_before['hinted_connection']
assert tour.master_navigation10_prior['room_candidates'] is guest_before['room_candidates']
byid={r['id']:r for r in rooms};ids=(nav.MASTER,nav.BATH,nav.CLOSET)
candidates={rid:tour.room_candidates(byid[rid],p,True) for rid in ids}
edges={name:tour.hinted_connection(byid[path['from']],byid[path['to']],p,candidates,[]) for name,path in spec['paths'].items()}
edges['ACTUAL_NORTH_WARDROBE']=tour.storage_inspection(s,byid[nav.MASTER],byid[nav.CLOSET],p,candidates)
assert all(row['status'].startswith('PASS') for row in edges.values()),edges
old_cameras={}
for name in spec['cameras']:
 eye=list(s.objects[name].matrix_world.translation)
 old_cameras[name]={'saved_eye':eye,'strict_exact_saved_pose_failure':p.point(eye,True),'same_xy_at_finish_plus_1_6_failure':p.point([eye[0],eye[1],nav.TOP+nav.EYE],True)}
camera_changes=nav.apply_cameras(s)
shots={rid:tour.room_shot(byid[rid],p,candidates) for rid in ids}
assert all(shot and issue is None for shot,issue in shots.values()),shots
local_attachments={
 'master_shot_to_storage':nav.eyes([nav.px(359,338),nav.px(359,323),nav.px(375,325)]),
 'master_anchor_to_B':nav.eyes([nav.px(359,381),nav.px(380,385)]),
 'bath_anchor_to_A':nav.eyes([[6.2,8.35,nav.TOP],[6.45,7.75,nav.TOP]]),
 'bath_anchor_to_B':nav.eyes([[6.2,8.35,nav.TOP],[5.6,9.0,nav.TOP]])}
attachments={key:{'points':pts,'failure':p.path(pts,True)} for key,pts in local_attachments.items()}
assert not any(a['failure'] for a in attachments.values()),attachments
cam1=tour.new_camera(s,'QA_MASTER10_TOUR');cam2=tour.new_camera(s,'QA_MASTER10_SUPPLEMENTAL')
main=[dict(shots[nav.MASTER][0],id='MASTER_LOCAL',room_ids=[nav.MASTER],start_frame=1,end_frame=168)]
supp=[dict(shots[nav.BATH][0],id='MASTER_BATH_LOCAL',room_ids=[nav.BATH],start_frame=169,end_frame=264),dict(shots[nav.CLOSET][0],id='MASTER_WARDROBE_INSPECTION_LOCAL',room_ids=[nav.CLOSET],start_frame=265,end_frame=360)]
for seg in main:tour.set_keys(cam1,seg)
for seg in supp:tour.set_keys(cam2,seg)
route={'scene_file':str(SRC),'main_camera':cam1.name,'supplemental_camera':cam2.name,'main_segments':main,'supplemental_segments':supp}
frame_report=tour.camera_evidence(s,[byid[rid] for rid in ids],route,p)
assert all(v['frame_geometry_status']=='PASS' and v['animation_values_status']=='PASS' for v in frame_report['segment_checks'])
frame_report.update(scope='LOCAL_3_SEGMENTS_ONLY_NOT_FULL_60_OR_7584',main_frames=168,supplemental_frames=192,checked_blend=str(OUT))
(R/'qa/master-navigation10-local-frames-initial.json').write_text(json.dumps(frame_report,indent=2),encoding='utf-8')
s.frame_set(old_settings[0]);bpy.context.view_layer.update()
after=fp();changed=[n for n in before if before[n]!=after[n]];added=sorted(set(after)-set(before));removed=sorted(set(before)-set(after))
assert sorted(changed)==sorted(spec['cameras']) and added==['QA_MASTER10_SUPPLEMENTAL','QA_MASTER10_TOUR'] and not removed,(changed,added,removed)
assert old_settings==(s.frame_current,s.frame_start,s.frame_end,s.camera.name,s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.view_settings.exposure,s.cycles.samples)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));saved_sha=sha(OUT)
bpy.ops.wm.open_mainfile(filepath=str(OUT));s=bpy.context.scene
assert fp()==after
# Reopen audit reads the saved poses/keys before any camera or key apply.
reopen_cameras={}
reprobe=nav.StrictProbe(s)
for name,c in spec['cameras'].items():
 o=s.objects[name];actual=o.matrix_world.translation
 delta=(actual-Vector(c['eye'])).length
 aim=(Vector(c['target'])-actual).normalized();forward=o.matrix_world.to_quaternion()@Vector((0,0,-1))
 angle=forward.angle(aim)
 failure=reprobe.point(actual,True)
 assert delta<.0001 and angle<.0002 and abs(o.data.lens-c['lens_mm'])<.0001 and failure is None
 reopen_cameras[name]={'saved_eye':list(actual),'position_error_m':delta,'look_angle_error_radians':angle,'failure':failure,'lens_mm':o.data.lens}
reopen=tour.camera_evidence(s,[byid[rid] for rid in ids],route,reprobe)
assert all(v['frame_geometry_status']=='PASS' and v['animation_values_status']=='PASS' for v in reopen['segment_checks'])
reopen.update(scope='LOCAL_3_SEGMENTS_SAVED_REOPEN_ONLY_NOT_FULL_60_OR_7584',main_frames=168,supplemental_frames=192,checked_blend=str(OUT),saved_scene_sha256=saved_sha,read_keys_without_reapplying=True)
(R/'qa/master-navigation10-local-frames-reopen.json').write_text(json.dumps(reopen,indent=2),encoding='utf-8')
assert protected_before=={str(p):sha(p) for p in protected}
freeze={'status':'FROZEN_LOCAL_NAVIGATION_CAMERA_PROPOSAL_NOT_FULL_BUILD_ACCEPTANCE','source_scene':str(SRC),'source_sha256':sha(SRC),'candidate_scene':str(OUT),'candidate_sha256':saved_sha,'candidate_bytes':OUT.stat().st_size,'adapter_sha256':sha(R/'scripts/master_navigation10.py'),'camera_changes':camera_changes,'old_cameras':old_cameras,'reopen_cameras':reopen_cameras,'edges':edges,'local_attachments':attachments,'local_frames':360,'local_frames_reopen':360,'local_frame_failures':0,'object_scope':{'changed':changed,'added':added,'removed':removed,'all_other_fingerprints_identical':True},'saved_reopen_fingerprints_identical':True,'saved_settings_identical':True,'protected_file_hashes':protected_before,'guest_composition':{'preserved_functions':preserved,'wrapped_prior_guest_dispatch_retained':True,'prepare_read_only':True},'room_changes':{rid:{'before':next(r for r in rooms0 if r['id']==rid),'candidate':byid[rid]} for rid in ids},'limits':['No render. Root owns complete 60-edge and 7584-frame combined validation.','No geometry, lights, materials, production camera data, original scenes or route keys changed.','Source panel/78-degree inward pose and gait dimensions remain C; visible true terrace door identity B.','Root EV2.4 Master suggestion is exposure-only metadata; scene exposure unchanged.','Flat crossing FAIL retained separately; two-foot step does not relax 4mm floor or 1.95m head/body tests.']}
(R/'qa/master-navigation10-final-freeze.json').write_text(json.dumps(freeze,indent=2),encoding='utf-8')
shutil.copyfile(W/'qa/master-navigation10-sill-step.json',R/'qa/master-navigation10-sill-step-final.json')
print(json.dumps({k:freeze[k] for k in ('status','source_sha256','candidate_sha256','candidate_bytes','adapter_sha256','local_frames','local_frames_reopen')},indent=2),flush=True)
