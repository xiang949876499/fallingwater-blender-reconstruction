"""Finalize only from complete independent saved-frame evidence."""
import json,hashlib
from pathlib import Path
R=Path('D:/zx/test/project');Q=R/'qa'
def read(name):return json.loads((Q/name).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
r=read('guest-circulation10-navigation-result-attempt04.json')
reopen=read('guest-circulation10-navigation-reopen-result-attempt04.json')
migration=read('guest-circulation10-navigation-runtime-migration.json')
assert r['counts']=={'PASS':60,'FAIL':0,'NOT_RUN':0} and r['normal_walk_pass']==52 and r['inspection_pass']==8
assert r['frame_count']==7584 and r['frame_geometry_failures']==0 and r['frame_pass']
assert reopen['status']=='PASS_INDEPENDENT_SAVED_INTEGER_FRAMES' and reopen['actual_integer_frames']==7584 and reopen['geometry_failures']==0
assert all(reopen['protected_data_unchanged'].values()) and reopen['source_hash_unchanged']
assert r['source_scene_unchanged'] and not r['saved_room_camera_changes'] and all(r['production_files_unchanged'].values())
assert migration['design_bytes_identical'] and not migration['physical_values_changed'] and all(x['only_expected_path_literal_changed']for x in migration['source_edits'])
assert sha(r['candidate_tour_scene'])==r['candidate_tour_sha256']
for label in ('route','camera-coverage','check','all-adjacency'):
    path=Q/f'guest-circulation10-navigation-{label}-attempt04.json';record=json.loads(path.read_text(encoding='utf-8'))
    record.update(candidate_tour_scene=r['candidate_tour_scene'],candidate_tour_sha256=r['candidate_tour_sha256'],
                  independent_reopen=reopen['status'],accepted_for_delivery=False)
    if label=='check':
        record['ray_source']='Candidate adapter BVH of dependency-graph evaluated MESH/CURVE/SURFACE/FONT polygons, transformed to world space; built once for static physical geometry, with actual evaluated camera matrices tested at each integer frame.'
    if label=='camera-coverage':
        record.update(checked_blend=r['candidate_tour_scene'],checked_blend_note='Independent candidate saved and reopened; merged-scene and visual acceptance remain separate.')
    if label=='route':
        record.update(animation_scene_file=r['candidate_tour_scene'],delivery_status='CANDIDATE_GEOMETRY_CHECKED_VISUAL_AND_MERGED_SCENE_VALIDATION_PENDING',
          camera_coverage_evidence='qa/guest-circulation10-navigation-reopen-coverage-attempt04.json',
          all_adjacency_evidence='qa/guest-circulation10-navigation-all-adjacency-attempt04.json')
    path.write_text(json.dumps(record,indent=2),encoding='utf-8')
data_files=['data/guest_circulation10.json','data/guest_circulation10_design.json','scripts/guest_circulation10.py','scripts/guest_circulation10_routes.py']
final={'status':'PASS_GUEST_CANDIDATE_NAVIGATION_NOT_PRODUCTION_ACCEPTANCE',
       'physical_source_sha256':r['candidate_sha256'],'saved_candidate_scene':r['candidate_tour_scene'],
       'saved_candidate_sha256':r['candidate_tour_sha256'],'full_adjacency_counts':r['counts'],
       'normal_walk_edges':52,'typed_inspection_edges':8,'integer_frames_initial':7584,'integer_frames_independent_reopen':7584,
       'frame_geometry_failures':0,'main_segments':10,'supplemental_segments':49,'census_spaces':60,
       'saved_room_camera_changes':[],'production_route_or_geometry_installation':False,
       'thresholds':r['limits'],'runtime_migration':migration,
       'current_runtime_sha256':{name:sha(R/name)for name in data_files},
       'diagnostic_camera_settings':'qa/guest-circulation10-render-cameras.json',
       'southeast_diagnostic_superseding_first_render':'qa/guest-circulation10-navigation-entry-camera-retreat.json',
       'candidate_census_camera_overrides':'qa/guest-circulation10-navigation-camera-overrides.json',
       'limits':['Full graph/frame PASS applies only to this guest candidate, not a future master/guest combined scene.',
                 'C levels/counts/divider height remain C; no geometric pass upgrades source evidence.',
                 'The global legacy1.71m body-column method and strict local1.95m construction screen remain distinct.',
                 'No film render, production camera application or full120image acceptance was performed.']}
(Q/'guest-circulation10-navigation-final.json').write_text(json.dumps(final,indent=2),encoding='utf-8')
doc=Q/'guest-circulation10-navigation-handoff.md';text=doc.read_text(encoding='utf-8')
old='Current gate: full candidate graph and all 7,584 integer frames passed in\nattempt04; the independently reopened saved animation is still being checked.\nThis document will be finalized from the reopen result. No production install,\nrendered-film acceptance or all-room visual acceptance is claimed.'
new='Current gate: **60 / 0 / 0 adjacency and all 7,584 integer frames PASS**, followed\nby an independent reopen of the saved camera keys and **all 7,584 frames PASS\nagain**. No keys were rebuilt for the reopen. All source/candidate hashes and\nprotected data stayed unchanged in their respective frozen checks. No production\ninstall, rendered-film acceptance or all-room visual acceptance is claimed.\nThe machine-readable current entry point is `guest-circulation10-navigation-final.json`.'
assert old in text;text=text.replace(old,new)
doc.write_text(text,encoding='utf-8')
print(json.dumps({k:final[k]for k in ('status','saved_candidate_sha256','full_adjacency_counts','integer_frames_independent_reopen','current_runtime_sha256')},indent=2))
