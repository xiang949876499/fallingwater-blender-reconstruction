"""Do not let existing22mm terrace-camera datum failures mask new leaf hits."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import master_navigation10 as nav
base=json.loads((R/'qa/master-ceiling11-build-check.json').read_text(encoding='utf-8'))
rows={}
for tag,path in [('source',base['source']),('candidate',base['candidate'])]:
    bpy.ops.wm.open_mainfile(filepath=path);s=bpy.context.scene;p=nav.StrictProbe(s);out=[];previous=None
    for frame in range(5089,5185):
        s.frame_set(frame);eye=s.objects['CAM_TOUR_SUPPLEMENTAL'].matrix_world.translation.copy()
        # The actual eye stays at4.4448. The separate standing body originates
        # on real finish2.8668 and remains1.95m tall; no shortening to make a
        # camera whose nominal1.6m datum is wrong pass the original foot test.
        body_proxy=Vector((eye.x,eye.y,nav.TOP+nav.EYE))
        body=p.point(body_proxy,True)
        if body is None and previous is not None:body=p.segment(previous,body_proxy,True)
        out.append({'frame':frame,'actual_eye':list(eye),'actual_camera_only_failure':p.point(eye,False),
                    'physical_floor_z':nav.TOP,'standing_head_z':nav.TOP+nav.HEAD,'body_failure':body,
                    'original_nominal_foot_datum_error_m':nav.TOP-(eye.z-nav.EYE)})
        previous=body_proxy
    rows[tag]=out
new=[{'baseline':a,'candidate':b} for a,b in zip(rows['source'],rows['candidate'])
     if (b['body_failure'] and not a['body_failure']) or (b['actual_camera_only_failure'] and not a['actual_camera_only_failure'])]
out={'source':base['source'],'candidate':base['candidate'],'candidate_sha256':base['candidate_sha256'],
     'frames_per_scene':96,'body_ground_tolerance_m':.004,'body_radius_m':.18,'body_height_m':1.95,
     'source_body_failures':sum(bool(r['body_failure']) for r in rows['source']),
     'candidate_body_failures':sum(bool(r['body_failure']) for r in rows['candidate']),
     'candidate_actual_camera_failures':sum(bool(r['actual_camera_only_failure']) for r in rows['candidate']),
     'new_failures':new,'rows':rows,'pass_no_new_body_or_eye_conflict':not new,
     'original_96_literal_saved_pose_foot_failures':'PRESERVED:22mm structural-versus-finish datum mismatch; this separate body test does not promote them to original-posePASS.',
     'saved':False,'rendered':False,'candidate_file_unchanged':hashlib.sha256(Path(base['candidate']).read_bytes()).hexdigest()==base['candidate_sha256']}
(R/'qa/master-ceiling11-exterior-body-reopen.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2),flush=True);assert not new
