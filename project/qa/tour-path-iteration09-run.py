"""Independent full09 graph/frame audit; NEVER save a checked scene.

The frozen build contains room cameras, not delivered tour keys. Read all
saved camera matrices first, then construct/evaluate candidate tour keys only
in this unsaved background process. Production route/config/source is frozen.
"""
import bpy,json,sys,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import tour
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
freeze=json.loads((ROOT/'qa/integration09-freeze.json').read_text(encoding='utf-8'))
assert freeze['status']=='BUILD_SAVED_PENDING_INTEGRATED_QA'
expected=freeze['scene_sha256'];source=ROOT/freeze['checkpoint'];assert sha(source)==expected
attempt=sys.argv[sys.argv.index('--attempt')+1] if '--attempt' in sys.argv else '01';assert attempt.isdigit()
work=ROOT/f'qa/tour-path-iteration09-attempt{attempt}-workspace'
assert not work.exists(),'Preserve an existing09 attempt; select a new attempt number.'
for folder in ('data','qa','scene'):(work/folder).mkdir(parents=True,exist_ok=True)
inputs=['data/main_house.json','data/guest_house.json','config.json','adjacency.csv']
input_hashes={}
for name in inputs:
 p=ROOT/name;assert p.exists();shutil.copy2(p,work/name);input_hashes[name]=sha(p);assert sha(work/name)==input_hashes[name]
protected_names=inputs+['data/tour-route.json','data/camera-settings-reviewed.json','scripts/tour.py','scripts/camera_review.py','scripts/main_house.py','scripts/guest_house.py','scripts/furnishings.py','scripts/furnishing_softgoods.py']
protected={n:sha(ROOT/n) for n in protected_names}
shutil.copy2(ROOT/'data/tour-route.json',ROOT/f'qa/tour-path-route-before-iteration09-attempt{attempt}.json')
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=4
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
saved_cameras={ob.name:{'matrix_world':[list(r) for r in ob.matrix_world],'lens':ob.data.lens,'shift_x':ob.data.shift_x,'shift_y':ob.data.shift_y,'exposure':ob.get('fw_exposure'),'has_animation':bool(ob.animation_data and ob.animation_data.action)} for ob in scene.objects if ob.type=='CAMERA'}
saved_pose_path=ROOT/f'qa/tour-path-saved-camera-read-iteration09-attempt{attempt}.json'
saved_pose_path.write_text(json.dumps({'source_sha256':expected,'cameras':saved_cameras,'read_before_tour_install':True,'note':'Tour keys may be absent from full build. No room camera config is applied by this script.'},indent=2))
# Redirect the unmodified validator's input/output root to byte-identical
# metadata copies. In particular its tour-route.json cannot overwrite08's.
tour.ROOT=work
manifest=tour.adjacency_manifest(rooms)
assert len(rooms)==60 and manifest['edge_count']==60,(len(rooms),manifest['edge_count'])
assert any(e['from']=='MAIN_L1_LOGGIA' and e['to']=='MAIN_L1_TERRACE_E' for e in manifest['retracted_edges'])
tour.install(scene,rooms)
checks={}
for name,label in [('qa/tour-path-all-adjacency.json','all-adjacency'),('qa/tour-path-check.json','check'),('qa/tour-path-camera-coverage.json','camera-coverage'),('data/tour-route.json','route')]:
 record=json.loads((work/name).read_text(encoding='utf-8'));record.update(source_scene_sha256=expected,iteration=9,attempt=attempt,checked_scene_saved=False,accepted_for_delivery=False)
 if label=='camera-coverage':record.update(checked_blend=None,checked_blend_note='No checked09 was saved; the unmodified validator placeholder is not a saved artifact.')
 if label=='route':
  record.update(delivery_status='CANDIDATE_TEST_EVIDENCE_ONLY_NOT_ACCEPTED_NOT_SAVED',camera_coverage_evidence=f'qa/tour-path-camera-coverage-iteration09-attempt{attempt}.json',all_adjacency_evidence=f'qa/tour-path-all-adjacency-iteration09-attempt{attempt}.json')
 out=ROOT/f'qa/tour-path-{label}-iteration09-attempt{attempt}.json';out.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');checks[label]=record
adj=checks['all-adjacency'];check=checks['check'];coverage=checks['camera-coverage'];route=checks['route']
frames=sum(s['frames_checked'] for s in coverage['segment_checks']);frame_failures=sum(s.get('geometry_failure_frame_count',0) for s in coverage['segment_checks'])
graph_pass=adj['counts']=={'PASS':60,'FAIL':0,'NOT_RUN':0} and adj['normal_walk_edge_pass_count']==52 and adj['inspection_edge_pass_count']==8
frame_pass=frames==7584 and frame_failures==0 and coverage['status']=='PASS_CAMERA_VALUES_AND_COVERAGE' and coverage['covered_room_count']==60 and all(s.get('actual_evaluated_world_matrix_checked') and s.get('intra_segment_previous_frame_sweeps_checked') for s in coverage['segment_checks']) and len(route['main_segments'])==10 and len(route['supplemental_segments'])==49 and not route['excluded_requested_segments'] and not route['uncovered_room_ids']
failures=[e for e in adj['edges'] if not e['status'].startswith('PASS')]
room_camera_changes=[]
for name,old in saved_cameras.items():
 if name in ('CAM_TOUR','CAM_TOUR_SUPPLEMENTAL'):continue
 ob=scene.objects.get(name)
 if ob is None or [list(r) for r in ob.matrix_world]!=old['matrix_world'] or ob.data.lens!=old['lens'] or ob.data.shift_x!=old['shift_x'] or ob.data.shift_y!=old['shift_y'] or ob.get('fw_exposure')!=old['exposure']:room_camera_changes.append(name)
unchanged={n:sha(ROOT/n)==h for n,h in protected.items()}
result={'status':'FAIL_FULL_CONNECTION_GRAPH_NO_CHECKED_SCENE_SAVED' if not graph_pass else ('GEOMETRY_PASS_CHECKED_SCENE_NOT_SAVED' if frame_pass else 'FAIL_INTEGER_FRAME_CHECK_NO_CHECKED_SCENE_SAVED'),'source':str(source),'source_sha256':expected,'iteration':9,'attempt':attempt,'counts':adj['counts'],'full_connection_graph_pass':graph_pass,'frame_count':frames,'integer_frame_failure_count':frame_failures,'all_integer_frames_pass':frame_pass,'route_status':check['status'],'camera_status':coverage['status'],'walk_pass':adj['normal_walk_edge_pass_count'],'inspection_pass':adj['inspection_edge_pass_count'],'failed_edges':failures,'source_hash_unchanged':sha(source)==expected,'validator_source_sha256':protected['scripts/tour.py'],'input_metadata_hashes':input_hashes,'production_files_unchanged':unchanged,'room_saved_camera_changes':room_camera_changes,'actual_saved_cameras_read_first':True,'candidate_tour_created_only_in_memory':True,'checked_scene_saved':False,'accepted_for_delivery':False,'central_production_route_overwritten':False,'limits':['7584-frame mesh PASS is independent of the 60-edge graph. Camera cuts never satisfy failed room connections.','No old PASS state imported; graph re-evaluated on actual frozen09 mesh.','No render, GUI navigation, or full visual acceptance. No checked09 scene is written, regardless of test outcome.']}
(ROOT/f'qa/tour-path-iteration09-attempt{attempt}-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
status_text=f'''# Full09 independent graph and integer-frame audit

Source SHA: `{expected}`. Actual saved room cameras were read before any tour animation was built; production camera settings were not applied.

60-edge graph: **{adj['counts']}**. Normal walking PASS {adj['normal_walk_edge_pass_count']}; inspection-only PASS {adj['inspection_edge_pass_count']}. These categories remain distinct.

Delivered integer-frame audit: {frames} frames; {frame_failures} mesh failures; coverage `{coverage['status']}`. This does not convert the connection graph to PASS.

No checked09 scene was saved. Candidate route evidence is under the09-prefixed QA files; production `data/tour-route.json` was not overwritten. Overall: `{result['status']}`.
'''
(ROOT/f'qa/tour-path-status-iteration09-attempt{attempt}.md').write_text(status_text,encoding='utf-8')
print('TOUR09_RESULT '+json.dumps({k:result[k] for k in ('status','counts','frame_count','integer_frame_failure_count','walk_pass','inspection_pass','source_hash_unchanged','room_saved_camera_changes')}),flush=True)
assert result['source_hash_unchanged'] and all(unchanged.values()) and not room_camera_changes
assert frames==7584 and coverage['covered_room_count']==60
