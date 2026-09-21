"""Validate the immutable07 source; save a checked tour only after actual checks pass."""
import bpy,json,sys,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import tour
expected='bf50530009e4a93315915815473188c91d891272ef2d8e9e0169b704bd2e2f16'
source=ROOT/'scene/Fallingwater_iteration07.blend'
assert Path(bpy.data.filepath).resolve()==source.resolve()
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
attempt=sys.argv[sys.argv.index('--attempt')+1] if '--attempt' in sys.argv else '01'
assert attempt.isdigit()
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
manifest=tour.adjacency_manifest(rooms)
assert len(rooms)==60 and manifest['edge_count']==60,(len(rooms),manifest['edge_count'])
assert any(e['from']=='MAIN_L1_LOGGIA' and e['to']=='MAIN_L1_TERRACE_E' for e in manifest['retracted_edges'])
tour.install(bpy.context.scene,rooms)
checks={}
for name,label in [('qa/tour-path-all-adjacency.json','all-adjacency'),('qa/tour-path-check.json','check'),
                   ('qa/tour-path-camera-coverage.json','camera-coverage'),('data/tour-route.json','route')]:
    path=ROOT/name;record=json.loads(path.read_text(encoding='utf-8'))
    record.update(source_scene_sha256=expected,iteration=7,attempt=attempt)
    path.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/f'qa/tour-path-{label}-iteration07-attempt{attempt}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    checks[label]=record
adj=checks['all-adjacency'];check=checks['check'];coverage=checks['camera-coverage']
frame_count=sum(s['frames_checked'] for s in coverage['segment_checks'])
passed=adj['counts']=={'PASS':60,'FAIL':0,'NOT_RUN':0} and check['status']=='PASS_RAY_CHECKS_NOT_VISUAL_ACCEPTANCE' and frame_count==7584
result={'status':'PASS_PENDING_INDEPENDENT_REOPEN' if passed else 'FAIL_NO_CHECKED_SCENE_SAVED',
        'source_sha256':expected,'counts':adj['counts'],'frame_count':frame_count,
        'route_status':check['status'],'camera_status':coverage['status'],'attempt':attempt,
        'source_hash_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==expected}
if passed:
    destination=ROOT/'scene/Fallingwater_tour_checked_iteration07.blend'
    assert not destination.exists(),'Preserve an existing checked07; explicitly version a replacement.'
    bpy.ops.wm.save_as_mainfile(filepath=str(destination),compress=True)
    result.update(checked_scene=str(destination),checked_scene_sha256=hashlib.sha256(destination.read_bytes()).hexdigest())
(ROOT/f'qa/tour-path-iteration07-attempt{attempt}-result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('TOUR07_RESULT',json.dumps(result),flush=True)
assert passed and result['source_hash_unchanged'],result
