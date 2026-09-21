"""Read-only diagnostic camera and affected saved-camera mesh audit."""
import bpy,sys,json,hashlib,importlib.util,math
from pathlib import Path
from mathutils import Vector
R=Path('D:/zx/test/project');sys.path.insert(0,str(R/'scripts'))
import guest_circulation10 as c10
spec=importlib.util.spec_from_file_location('local_check',R/'qa/guest-circulation10-check.py')
local=importlib.util.module_from_spec(spec);spec.loader.exec_module(local)
expected='7286427d1f47ae9219204ed5dd54a970387683c8b384d1b4259244a7b991d852'
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==expected
manifest=json.loads(bpy.data.texts['FW_GUEST_CIRCULATION10_CANDIDATE.json'].as_string())
probe=local.Actual();settings={};records=[]
def eye(p):return list(c10.world_point(p[:2]+[p[2]+1.6]))
def sphere(p):
    hits=[]
    for x in (-1,0,1):
        for y in (-1,0,1):
            for z in (-1,0,1):
                if not (x or y or z):continue
                d=Vector((x,y,z)).normalized();h=probe.ray(p,d,.13)
                if h:hits.append(h)
    return hits
def add(name,loc,target,lens,exposure,purpose,grounded=True):
    assert name in bpy.data.objects and bpy.data.objects[name].type=='CAMERA'
    foot=[*loc[:2],loc[2]-1.6];body,head=probe.check(foot,True) if grounded else ([],None)
    raydir=Vector(target)-Vector(loc);hit=probe.ray(loc,raydir.normalized(),raydir.length)
    row={'camera':name,'location':loc,'target':target,'lens':lens,'exposure':exposure,
         'purpose':purpose,'mode':'GROUNDED_DIAGNOSTIC' if grounded else 'FREE_INSPECTION',
         'body_failures':body,'camera_radius_failures':sphere(loc),'target_first_hit':hit,
         'lowest_overhead':head,'visual_acceptance':False}
    row['status']='PASS_GEOMETRY_ONLY' if not body and not row['camera_radius_failures'] else 'FAIL_GEOMETRY'
    records.append(row)
    if row['status'].startswith('PASS'):
        settings[name]={k:row[k] for k in ('location','target','lens','exposure','purpose','mode')}
    print('DIAGNOSTIC',name,row['status'],hit,flush=True)
add('CAM_GUEST_B1_STAIR_A',eye([294.45,366.5,-2.36]),list(c10.world_point((294.45,394,-1.51))),22,2.6,'Lower left B1 flight rising south, lower wall and overhead flight')
add('CAM_GUEST_L2_HALL_A',eye([305.5,414,1.4478]),list(c10.world_point((306.45,386,2.3))),20,2.6,'Upper south return with solid source divider and both flight margins')
add('CAM_GUEST_L1_LOUNGE_B',eye([466,441,0]),list(c10.world_point((466,422,1.3))),24,2.2,'Actual southeast glazed entrance and screen-side passage')
t=manifest['connector'][-12];a,b=Vector(t['a']),Vector(t['b']);pos=(a+b)/2;pos.z+=1.6
u=manifest['connector'][-18];target=(Vector(u['a'])+Vector(u['b']))/2;target.z+=.65
add('CAM_CONNECTOR',list(pos),list(target),22,1.2,'Physical canopy and stepped external connector, looking down toward main house')
affected=[]
for cam in bpy.context.scene.objects:
    if cam.type!='CAMERA':continue
    if not cam.name.startswith(('CAM_GUEST_B1_STAIR_','CAM_GUEST_L1_STAIR_HALL_','CAM_GUEST_L2_HALL_','CAM_GUEST_L1_LOUNGE_','CAM_GUEST_L1_GALLERY_','CAM_GUEST_L1_TERRACE_','CAM_GUEST_L1_CAR_COURT_','CAM_CONNECTOR')):continue
    p=cam.matrix_world.translation.copy();foot=[p.x,p.y,p.z-1.6]
    issues,head=probe.check(foot,False)
    affected.append({'camera':cam.name,'saved_location':list(p),'camera_radius_failures':sphere(p),
                     'grounded_1p6_eye_diagnostic_failures':issues,'diagnostic_not_assuming_saved_camera_eyeheight':True,
                     'requires_eye_relocation':bool(sphere(p)),'needs_grounded_or_free_mode_review':bool(issues),'lowest_overhead':head})
out={'candidate_sha256':expected,'diagnostic_cameras':records,'saved_affected_cameras':affected,
     'geometric_method':'Actual evaluated regional meshes; 26 eye rays at0.13m. Grounded diagnostics additionally reuse13 body columns,0.18m radius,1.95m headroom and4mm foot support. Saved-camera grounded probe assumes1.6m eye only to identify review needs, not automatic failure.',
     'rendered':False,'scene_or_camera_saved':False,'source_sha_unchanged':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==expected}
(R/'qa/guest-circulation10-navigation-camera-check.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
(R/'qa/guest-circulation10-render-cameras.json').write_text(json.dumps(settings,indent=2),encoding='utf-8')
assert len(settings)==4,'Keep negative report; fix only diagnostic poses before render'
