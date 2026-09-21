"""Read the actual saved film keys and repeat all integer-frame checks."""
from pathlib import Path
import bpy,json,sys,hashlib,shutil,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import guest_circulation10_routes as guest,master_navigation10 as master
SOURCE=ROOT/'scene/Fallingwater_navigation_candidate10a.blend'
EXPECTED='1e7b17d9c2396513f005724e50788bf834097eedb401b91a7f1030825e2c4ed9'
WORK=ROOT/'qa/integration10-navigation-reopen-workspace'
REPORT=ROOT/'qa/integration10-navigation-reopen.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(SOURCE)==EXPECTED and not WORK.exists() and not REPORT.exists()
inputs=json.loads((ROOT/'qa/integration10-navigation-result.json').read_text(encoding='utf8'))['adapter_inputs']
assert all(sha(ROOT/'scripts'/n)==v for n,v in inputs.items())
shutil.copytree(ROOT/'qa/integration10-navigation-workspace',WORK)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene
scene.render.threads_mode='FIXED';scene.render.threads=4
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
tour,rooms,guest_spec=guest.prepare(WORK,scene,rooms,read_only=True)
master.apply(tour,scene,rooms,WORK)
route=json.loads((WORK/'data/tour-route.json').read_text(encoding='utf8'))
def keys():
    rows=[]
    for ob in scene.objects:
        if ob.type!='CAMERA' or not ob.animation_data or not ob.animation_data.action:continue
        action=ob.animation_data.action
        curves=[]
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        curves.append((curve.data_path,curve.array_index,[(list(p.co),p.interpolation) for p in curve.keyframe_points]))
        rows.append((ob.name,curves))
    return hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()
before=keys();started=time.monotonic()
coverage=tour.camera_evidence(scene,rooms,route)
after=keys()
frames=sum(s['frames_checked'] for s in coverage['segment_checks'])
failures=sum(s.get('geometry_failure_frame_count',0) for s in coverage['segment_checks'])
passed=before==after and sha(SOURCE)==EXPECTED and frames==7584 and failures==0 and coverage['status']=='PASS_CAMERA_VALUES_AND_COVERAGE'
record={'status':'PASS_FRESH_REOPEN_ALL_SAVED_FRAMES' if passed else 'FAIL_RETAINED',
        'source_scene':str(SOURCE),'source_sha256':EXPECTED,'source_unchanged':sha(SOURCE)==EXPECTED,
        'frames':frames,'geometry_failure_frames':failures,'coverage_status':coverage['status'],
        'camera_keys_before':before,'camera_keys_after':after,'camera_keys_rebuilt':False,
        'covered_room_count':coverage['covered_room_count'],'seconds':time.monotonic()-started,
        'scope':'All actual saved film integer frames; graph not regenerated; no save or camera placement installation',
        'limits':'Geometric sampling only; actual GUI, photographs and complete videos still unaccepted'}
REPORT.write_text(json.dumps(record,indent=2),encoding='utf8');print(json.dumps(record),flush=True)
if not passed:raise RuntimeError('Saved-key/frame reopen check failed')
