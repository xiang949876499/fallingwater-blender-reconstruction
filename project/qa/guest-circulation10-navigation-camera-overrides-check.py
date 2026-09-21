"""Candidate replacements for changed census camera planes; no saved poses."""
import bpy,sys,json,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
R=Path('D:/zx/test/project');sys.path.insert(0,str(R/'scripts'))
import guest_circulation10_routes as routes
spec=importlib.util.spec_from_file_location('local_check',R/'qa/guest-circulation10-check.py')
local=importlib.util.module_from_spec(spec);spec.loader.exec_module(local)
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==routes.CANDIDATE_SHA
probe=local.Actual()
reviewed=json.loads((R/'data/camera-settings-reviewed.json').read_text(encoding='utf-8'))
data={
 'CAM_GUEST_B1_STAIR_A':([294.45,364,-2.36],[294.45,394,-1.51],22,2.6,'Old camera was at L1; relocate to actual B1 platform and lower flight'),
 'CAM_GUEST_L1_STAIR_HALL_A':([296.75,359.75,0],[316.35,357,1.1],24,2.6,'Old pose above new upper-right flight belongs to wrong level; use northern L1 platform'),
 'CAM_GUEST_L1_STAIR_HALL_B':([305,423,-1.18],[316.35,395,-.15],22,2.6,'Old south flat0 floor was removed; use real low south arrival'),
 'CAM_GUEST_L2_HALL_A':([305.5,414,1.4478],[306.45,386,2.3],20,2.6,'Inspect source upper divider and south intermediate return; explicit nonplanar Hall camera'),
 'CAM_GUEST_L1_TERRACE_B':([417,461,-.6742857142857143],[400,443,.85],24,1.8,'Old west paving camera retains former flat0 eye height; use actual intermediate front paving'),
}
settings={};reports=[]
for name,(p,target,lens,exposure,reason) in data.items():
    foot=routes.source(p);eye=Vector(foot)+Vector((0,0,1.6));look=Vector(routes.source(target))
    issues,head=probe.check(foot,False);eye_hits=[]
    for d in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
        h=probe.ray(eye,d,.13)
        if h:eye_hits.append(h)
    direction=look-eye;first=probe.ray(eye,direction.normalized(),direction.length)
    row={'camera':name,'status':'FAIL' if issues or eye_hits else 'PASS_GEOMETRY_ONLY','reason':reason,
         'old_location':list(bpy.data.objects[name].matrix_world.translation),'new_location':list(eye),
         'support_z':foot[2],'body_1p95_failures':issues,'eye_failures':eye_hits,'target_first_hit':first,'lowest_overhead':head}
    reports.append(row)
    if row['status'].startswith('PASS'):
        settings[name]={'location':list(eye),'target':list(look),'lens':lens,'exposure':exposure,
                        'shift_x':0,'shift_y':0,'support_z':foot[2],'room_id':reviewed[name]['room_id'],
                        'evidence':'Candidate10 actual mesh test only. '+reason,'render_reviewed':False,
                        'candidate_only':True,'mode':'GROUNDED_DIAGNOSTIC'}
    print('C10_CAMERA_OVERRIDE',name,row['status'],issues,first,flush=True)
(R/'qa/guest-circulation10-navigation-camera-overrides.json').write_text(json.dumps(settings,indent=2),encoding='utf-8')
(R/'qa/guest-circulation10-navigation-camera-overrides-check.json').write_text(json.dumps({
 'candidate_sha256':routes.CANDIDATE_SHA,'reports':reports,'saved_camera_mutations':False,
 'not_a_rerender_or_120_camera_acceptance':True,
 'unchanged_notes':['CAM_CONNECTOR was an exterior free camera: no ground is not a collision failure. A separate grounded diagnostic is provided.',
                    'CarCourt A/B and original L2 Hall A marginal stone/body findings are not caused by the candidate geometry and are not reclassified as new regressions.'],
 'production_settings_hash':hashlib.sha256((R/'data/camera-settings-reviewed.json').read_bytes()).hexdigest()},indent=2),encoding='utf-8')
assert len(settings)==len(data),'Keep failed proposed poses for review; do not install'
