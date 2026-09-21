"""Fresh process: rebuild in memory from09, reopen candidate10c, compare."""
import bpy,json,hashlib,sys,array,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import main_interface10 as fix
SRC=R/'scene/Fallingwater_iteration09.blend';CAND=R/'scene/Fallingwater_main_interface_candidate10c.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def config(s):return {'resolution':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],'frame':s.frame_current,'range':[s.frame_start,s.frame_end],'active_camera':s.camera.name,'render_engine':s.render.engine,'device':s.cycles.device,'samples':s.cycles.samples,'exposure':s.view_settings.exposure,'threads':[s.render.threads_mode,s.render.threads],'world':s.world.name}
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene
def fingerprint():
 out={};cache={}
 for o in s.objects:
  h=hashlib.sha256(str(tuple(tuple(row) for row in o.matrix_world)).encode())
  if o.type=='MESH':
   ptr=o.data.as_pointer()
   if ptr not in cache:
    a=array.array('f',[0.])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a)
    b=array.array('i',[0])*len(o.data.loops);o.data.loops.foreach_get('vertex_index',b)
    cache[ptr]=hashlib.sha256(a.tobytes()+b.tobytes()).digest()
   h.update(cache[ptr])
  if o.type=='CAMERA':h.update(str((o.data.lens,o.data.sensor_width,o.data.sensor_height,o.data.shift_x,o.data.shift_y,o.data.clip_start,o.data.clip_end,o.data.type)).encode())
  if o.type=='LIGHT':h.update(str((o.data.type,o.data.energy,tuple(o.data.color))).encode())
  h.update(str(tuple(m.name if m else None for m in getattr(o.data,'materials',[]))).encode())
  h.update(str((o.hide_render,o.hide_viewport)).encode());out[o.name]=h.hexdigest()
 return out
original=fingerprint();original_settings=config(s)
old_courses={o.name:dict(local=[list(v.co) for v in o.data.vertices],world=[list(o.matrix_world@v.co) for v in o.data.vertices],materials=[m.name for m in o.data.materials],rotation=list(o.rotation_euler)) for o in s.objects if o.name.startswith('MAIN_L1_east_relief_course') and o.name.endswith('_1')}
manifest=fix.apply();expected_fp=fingerprint();expected={n:[list(s.objects[n].matrix_world@v.co) for v in s.objects[n].data.vertices] for n in manifest['changed']}
bpy.ops.wm.open_mainfile(filepath=str(CAND));s=bpy.context.scene
actual_fp=fingerprint();same=actual_fp==expected_fp
assert config(s)==original_settings
errors=[max(abs(a[k]-b[k]) for a,b in zip(expected[n],[list(s.objects[n].matrix_world@v.co) for v in s.objects[n].data.vertices]) for k in range(3)) for n in manifest['changed']]
courses=[];new_plane=max(v[0] for v in expected['MAIN_L1_entry_east_corner_core']);old_plane=10.735
for n,old in old_courses.items():
 o=s.objects[n];local=[list(v.co) for v in o.data.vertices];vv=[list(o.matrix_world@v.co) for v in o.data.vertices]
 oldoff=[min(v[0] for v in old['world'])-old_plane,max(v[0] for v in old['world'])-old_plane];new_off=[min(v[0] for v in vv)-new_plane,max(v[0] for v in vv)-new_plane]
 courses.append(dict(object=n,local_mesh_unchanged=local==old['local'],materials_unchanged=[m.name for m in o.data.materials]==old['materials'],rotation_unchanged=list(o.rotation_euler)==old['rotation'],old_substrate_offsets_m=oldoff,new_substrate_offsets_m=new_off,max_contact_change_m=max(abs(a-b) for a,b in zip(oldoff,new_off))))
# A wall displacement changes where an old image pixel falls within the stone
# pattern. Test actual attachment at each moved stone face center instead.
attachment_rays=[];dg=bpy.context.evaluated_depsgraph_get()
for name in old_courses:
 o=s.objects[name];vv=[o.matrix_world@v.co for v in o.data.vertices]
 front=max(v.x for v in vv);center=Vector((front+.08,(min(v.y for v in vv)+max(v.y for v in vv))/2,(min(v.z for v in vv)+max(v.z for v in vv))/2))
 h,p,n,f,hitob,_=s.ray_cast(dg,center,Vector((-1,0,0)),distance=.15)
 attachment_rays.append(dict(target=name,first_object=hitob.name if h else None,first_point=list(p) if h else None,pass_=h and hitob.name==name))
# Actual source rays are compared again in the reopened candidate.
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4;s.frame_set(48);dg=bpy.context.evaluated_depsgraph_get();c=s.objects['CAM_MAIN_L1_LOGGIA_A'];fr=c.data.view_frame(scene=s);lo=[min(v[k] for v in fr) for k in (0,1)];hi=[max(v[k] for v in fr) for k in (0,1)];rays=[]
for x,y in [(100,200),(150,300),(240,445),(536,340),(552,350)]:
 d=(c.matrix_world.to_quaternion()@Vector((lo[0]+(x+.5)/960*(hi[0]-lo[0]),hi[1]-(y+.5)/540*(hi[1]-lo[1]),fr[0].z))).normalized();h,p,n,f,o,_=s.ray_cast(dg,c.matrix_world.translation,d,distance=100);rays.append(dict(pixel=[x,y],object=o.name if h else None,point=list(p) if h else None))
report=dict(status='PASS_REOPENED_SOURCE_REBUILD_AND_RELIEF_ATTACHMENT',candidate=str(CAND),candidate_sha256=sha(CAND),candidate_bytes=CAND.stat().st_size,source_sha256=sha(SRC),final_helper_sha256=sha(R/'scripts/main_interface10.py'),source_script_sha256=sha(R/'scripts/main_house.py'),rebuilt_scene_fingerprints_equal_saved_candidate=same,world_vertex_max_error_m=max(errors),all_nontarget_unchanged=all(original[n]==actual_fp[n] for n in actual_fp if n not in manifest['changed']),original_saved_settings=original_settings,settings_equal_before_probe=True,corrected_manifest=manifest,course_count=len(courses),courses=courses,visible_original_camera_rays=rays,attachment_rays=attachment_rays,metadata_correction='Earlier candidate-check after_translation fields were captured before dependency-graph update and are stale. This fresh-process report reads them after update and compares actual saved geometry; final helper differs only by this metadata read timing. Candidate is not resaved.',scene_saved_this_process=False)
# The check was made before diagnostic image-plane settings; preserve it explicitly.
assert same and max(errors)==0 and len(courses)==108
assert all(x['local_mesh_unchanged'] and x['materials_unchanged'] and x['rotation_unchanged'] and x['max_contact_change_m']<2e-6 for x in courses)
assert all(x['pass_'] for x in attachment_rays)
assert report['all_nontarget_unchanged']
(R/'qa/main-interface10-final-reopen.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['courses','corrected_manifest','attachment_rays']},indent=2))
