"""Independent saved-animation reopen on evaluated actual meshes, no re-keying."""
import bpy,sys,json,hashlib,importlib.util
from pathlib import Path
R=Path('D:/zx/test/project');sys.path.insert(0,str(R/'scripts'))
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
attempt=args[args.index('--attempt')+1] if '--attempt' in args else '04'
assert attempt.isdigit()
work=R/f'qa/guest-circulation10-navigation-attempt{attempt}-workspace'
# The saved scene is checked with its byte-identical archived adapter, allowing
# a separately documented runtime-path migration in current integration code.
module_spec=importlib.util.spec_from_file_location('guest_routes_frozen_reopen',work/'scripts/guest_circulation10_routes.py')
adapter=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(adapter);adapter.ROOT=R
result_path=R/f'qa/guest-circulation10-navigation-result-attempt{attempt}.json'
result=json.loads(result_path.read_text(encoding='utf-8'))
assert result['graph_pass'] and result['frame_pass'] and result['checked_scene_saved']
scene_path=Path(bpy.data.filepath)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(scene_path)==result['candidate_tour_sha256']
assert sha(adapter.__file__)==result['adapter_sha256']
files=[R/'data/tour-route.json',R/'data/guest_circulation10.json',work/'data/guest_house.json',work/'data/guest_circulation10.json']
before={str(p):sha(p) for p in files}
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
tour,rooms,spec=adapter.prepare(work,bpy.context.scene,rooms,read_only=True)
assert json.loads(bpy.data.texts['FW_GUEST_CIRCULATION10_ROUTES.json'].as_string())==spec
route=json.loads((work/'data/tour-route.json').read_text(encoding='utf-8'))
coverage=tour.camera_evidence(bpy.context.scene,rooms,route)
count=sum(s['frames_checked'] for s in coverage['segment_checks'])
fail=sum(s.get('geometry_failure_frame_count',0) for s in coverage['segment_checks'])
passed=count==7584 and fail==0 and coverage['status']=='PASS_CAMERA_VALUES_AND_COVERAGE'
coverage.update(reopened_scene=str(scene_path),reopened_sha256=result['candidate_tour_sha256'],
                saved_camera_keys_not_rebuilt=True,checked_blend=str(scene_path),independent_reopen=True)
(R/f'qa/guest-circulation10-navigation-reopen-coverage-attempt{attempt}.json').write_text(json.dumps(coverage,indent=2),encoding='utf-8')
reopen={'status':'PASS_INDEPENDENT_SAVED_INTEGER_FRAMES' if passed else 'FAIL_INDEPENDENT_SAVED_INTEGER_FRAMES',
        'scene':str(scene_path),'sha256':result['candidate_tour_sha256'],'actual_integer_frames':count,
        'geometry_failures':fail,'keys_rebuilt':False,'scene_saved':False,'evaluated_meshes':True,
        'frozen_adapter_sha256':sha(adapter.__file__),
        'protected_data_unchanged':{str(p):sha(p)==before[str(p)] for p in files},'source_hash_unchanged':sha(scene_path)==result['candidate_tour_sha256']}
(R/f'qa/guest-circulation10-navigation-reopen-result-attempt{attempt}.json').write_text(json.dumps(reopen,indent=2),encoding='utf-8')
result['independent_reopen']=reopen['status'];result['independent_reopen_evidence']=f'qa/guest-circulation10-navigation-reopen-result-attempt{attempt}.json'
result_path.write_text(json.dumps(result,indent=2),encoding='utf-8')
print('C10_REOPEN',json.dumps(reopen),flush=True)
assert passed and all(reopen['protected_data_unchanged'].values()) and reopen['source_hash_unchanged']
