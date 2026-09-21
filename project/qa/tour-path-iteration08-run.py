"""Validate the immutable08 source; save a checked tour only after actual checks pass."""
import bpy,json,sys,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import tour
expected='c5cd501e4c8ae0205ecb2437cd2d06d0c92bcc9a87e7d93d3986aeef976070d7'
source=ROOT/'scene/Fallingwater_iteration08.blend'
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
    record.update(source_scene_sha256=expected,iteration=8,attempt=attempt)
    path.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/f'qa/tour-path-{label}-iteration08-attempt{attempt}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    checks[label]=record
adj=checks['all-adjacency'];check=checks['check'];coverage=checks['camera-coverage']
frame_count=sum(s['frames_checked'] for s in coverage['segment_checks'])
frame_failures=sum(s.get('geometry_failure_frame_count',0) for s in coverage['segment_checks'])
passed=(adj['counts']=={'PASS':60,'FAIL':0,'NOT_RUN':0} and adj['normal_walk_edge_pass_count']==52 and adj['inspection_edge_pass_count']==8
    and check['status']=='PASS_RAY_CHECKS_NOT_VISUAL_ACCEPTANCE' and frame_count==7584 and frame_failures==0
    and coverage['status']=='PASS_CAMERA_VALUES_AND_COVERAGE' and coverage['covered_room_count']==60
    and all(s.get('actual_evaluated_world_matrix_checked') and s.get('intra_segment_previous_frame_sweeps_checked') for s in coverage['segment_checks'])
    and len(checks['route']['main_segments'])==10 and len(checks['route']['supplemental_segments'])==49
    and not checks['route']['excluded_requested_segments'] and not checks['route']['uncovered_room_ids'])
result={'status':'PASS_PENDING_INDEPENDENT_REOPEN' if passed else 'FAIL_NO_CHECKED_SCENE_SAVED',
        'source_sha256':expected,'counts':adj['counts'],'frame_count':frame_count,
        'route_status':check['status'],'camera_status':coverage['status'],'attempt':attempt,'integer_frame_failure_count':frame_failures,
        'walk_pass':adj['normal_walk_edge_pass_count'],'inspection_pass':adj['inspection_edge_pass_count'],
        'validator_source_sha256':hashlib.sha256((ROOT/'scripts/tour.py').read_bytes()).hexdigest(),
        'source_hash_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==expected}
if passed:
    destination=ROOT/'scene/Fallingwater_tour_checked_iteration08.blend'
    assert not destination.exists(),'Preserve an existing checked08; explicitly version a replacement.'
    bpy.ops.wm.save_as_mainfile(filepath=str(destination),compress=True)
    result.update(checked_scene=str(destination),checked_scene_sha256=hashlib.sha256(destination.read_bytes()).hexdigest())
(ROOT/f'qa/tour-path-iteration08-attempt{attempt}-result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('TOUR08_RESULT',json.dumps(result),flush=True)
assert passed and result['source_hash_unchanged'],result
