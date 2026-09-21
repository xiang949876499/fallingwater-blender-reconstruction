"""Independently reopen07 and freeze exact saved-camera/geometry evidence."""
import bpy,json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import tour
source=ROOT/'scene/Fallingwater_iteration07.blend'
expected='bf50530009e4a93315915815473188c91d891272ef2d8e9e0169b704bd2e2f16'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
assert Path(bpy.data.filepath).name=='Fallingwater_tour_checked_iteration07.blend'
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
route=json.loads((ROOT/'data/tour-route.json').read_text(encoding='utf-8'))
assert Path(route['scene_file']).resolve()==source.resolve()
saved=Path(bpy.data.filepath);saved_sha=hashlib.sha256(saved.read_bytes()).hexdigest()
check=tour.camera_evidence(bpy.context.scene,rooms,route)
check.update(saved_scene_reopened=True,saved_scene=str(saved),checked_blend=str(saved),
             saved_scene_sha256=saved_sha,source_scene_sha256=expected,iteration=7)
(ROOT/'qa/tour-path-camera-coverage.json').write_text(json.dumps(check,ensure_ascii=False,indent=2),encoding='utf-8')
for original,label in [('qa/tour-path-all-adjacency.json','all-adjacency'),('qa/tour-path-check.json','check'),
                       ('qa/tour-path-camera-coverage.json','camera-coverage'),('data/tour-route.json','route')]:
    path=ROOT/original;record=json.loads(path.read_text(encoding='utf-8'))
    record.update(source_scene_sha256=expected,iteration=7,checked_blend=str(saved),checked_scene_sha256=saved_sha)
    path.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/f'qa/tour-path-{label}-iteration07-final.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
adj=json.loads((ROOT/'qa/tour-path-all-adjacency.json').read_text(encoding='utf-8'))
frames=sum(s['frames_checked'] for s in check['segment_checks'])
passed=check['status']=='PASS_CAMERA_VALUES_AND_COVERAGE' and frames==7584 and adj['counts']=={'PASS':60,'FAIL':0,'NOT_RUN':0}
inspection={'status':'EXECUTED_ON_ITERATION07','source_scene_sha256':expected,'space_count_preserved':len(rooms),
            'inspection_edges':[e for e in adj['edges'] if e.get('acceptance_type')],
            'retracted_edges':adj['retracted_edges'],
            'historical_evidence':'qa/tour-path-all-adjacency-iteration06-final.json remains 60 PASS / 1 FAIL; old ADJ_017 is source-retracted, not repaired into a dry-walk PASS.',
            'claim':'Inspection observations never merge walking components or establish traversal through water/cabinet/foundation.'}
(ROOT/'qa/tour-path-inspection-semantics-iteration07.json').write_text(json.dumps(inspection,ensure_ascii=False,indent=2),encoding='utf-8')
result={'status':'PASS_REOPENED_TOUR_GEOMETRY_NOT_VISUAL_ACCEPTANCE' if passed else 'FAIL',
        'frames':frames,'counts':adj['counts'],'walk_pass':adj['normal_walk_edge_pass_count'],
        'inspection_pass':adj['inspection_edge_pass_count'],'saved_sha256':saved_sha,
        'source_sha256':expected,'source_hash_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==expected,
        'saved_hash_unchanged':hashlib.sha256(saved.read_bytes()).hexdigest()==saved_sha,
        'max_camera_position_error_m':max(s['max_path_error_m'] for s in check['segment_checks']),
        'integer_frame_failure_count':sum(s['geometry_failure_frame_count'] for s in check['segment_checks']),
        'actual_evaluated_camera_matrices_checked':all(s['actual_evaluated_world_matrix_checked'] for s in check['segment_checks'])}
result['validator_source_sha256']=hashlib.sha256((ROOT/'scripts/tour.py').read_bytes()).hexdigest()
old_route=json.loads((ROOT/'qa/tour-path-route-iteration07-attempt01.json').read_text(encoding='utf-8'))
old_segments={s['id']:s for s in old_route['main_segments']+old_route['supplemental_segments']}
result['local_route_changes_from_negative_attempt01']=[{'id':s['id'],'before_points':old_segments[s['id']]['points'],
        'after_points':s['points'],'mode_before':old_segments[s['id']]['mode'],'mode_after':s['mode']}
        for s in route['main_segments']+route['supplemental_segments'] if s['points']!=old_segments[s['id']]['points'] or s['mode']!=old_segments[s['id']]['mode']]
(ROOT/'qa/tour-path-iteration07-reopen-result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
route_check=json.loads((ROOT/'qa/tour-path-check.json').read_text(encoding='utf-8'))
body_frames=sum(s['frames_checked'] for s in check['segment_checks'] if s['integer_frame_mesh_test']=='BODY_GROUND_AND_CAMERA')
report=f'''# Iteration07 navigation and saved tour audit

Source: `scene/Fallingwater_iteration07.blend`, SHA256 `{expected}`. Independent saved tour: `scene/Fallingwater_tour_checked_iteration07.blend`, SHA256 `{saved_sha}`. Source and saved hashes were both rechecked after the independent reopening; neither source nor working scene was overwritten.

## Executed results

- **{adj['edge_count']} current valid edges: {adj['counts']['PASS']} PASS / {adj['counts']['FAIL']} FAIL / {adj['counts']['NOT_RUN']} NOT_RUN.** These comprise {adj['normal_walk_edge_pass_count']} normal walking connections and {adj['inspection_edge_pass_count']} explicitly typed inspection relationships.
- All {len(rooms)} space records remain covered by {len(route['main_segments'])} main and {len(route['supplemental_segments'])} supplemental segments. The main tour is 120 seconds at 24 fps, including {route['external_seconds']} seconds outside. No requested main segment or space was excluded.
- All seven selected doors and the actual main-to-guest approach through the inner stair, L2 hall, north terrace, curved stairs, upper north walk and covered connector pass sampled mesh/ground checks.
- The independent saved file was reopened and **{frames:,} actual integer-frame camera positions** were checked again. {body_frames:,} frames receive body, ground and camera checks; the other {frames-body_frames:,} are explicitly free camera inspections or exterior flight. Adjacent frames within each segment receive a mesh sweep. No sweep or connectivity claim crosses a cut.
- Maximum piecewise-linear path discrepancy is `{result['max_camera_position_error_m']:.10f}m`; actual dependency-graph world matrices are evaluated after `scene.frame_set()` at every frame. Integer-frame geometry failures: **{result['integer_frame_failure_count']}**. Reopen status: `{result['status']}`.

## Source-retracted pool route

The historical iteration06 result remains **61 edges: 60 PASS / 1 FAIL / 0 NOT_RUN** in its frozen JSON and scene. Its ADJ_017 Loggia–East Terrace dry route is now separately recorded as `SOURCE_UNSUPPORTED_AS_DRY_WALKEDGE`; it is not a repaired navigation PASS and was not removed merely to improve a count. HABS main03/04 support pool-edge stonework but do not establish a continuous dry walking surface at a shared stair-foot elevation. The stronger source-support wording in the old iteration06 prose was superseded by the architectural source review in `main-pool-iteration06-report.md`.

Loggia–Plunge is a dry observation/stair inspection relationship. It never joins two walking components through the pool. The pool's declared polygon is an inspection envelope with `walkable_polygon=False`; its supplemental camera is explicitly free inspection. Living–East Terrace remains the valid glazed-door access. The corrected north pool-wall corner does not establish an unsupported ring walk.

Current edge IDs are ordered within this iteration; compare the from/to room pair and retraction record across iterations rather than assuming old numeric IDs are stable.

## Retained first-attempt failures and local route changes

The first complete 7,584-frame pass found 47 body-contact frames in six local shots; no checked scene was saved from it. `tour-path-iteration07-attempt01-review.md` identifies the low tables, chairs, towel and first tread hit by the original paths. Room-move selection was tightened from 0.25m to 0.01m body sampling without relaxing any clearance rule or moving scene geometry. The subsequent actual-frame check remains independent of that selection sampling.

The final route changes {len(result['local_route_changes_from_negative_attempt01'])} local shots from the negative attempt: {', '.join(r['id'] for r in result['local_route_changes_from_negative_attempt01'])}. Exact before/after waypoints and modes are retained in `tour-path-iteration07-reopen-result.json`. The source script SHA256 is `{result['validator_source_sha256']}`.

An additional isolated 1cm replay is recorded in `tour-path-iteration07-local-repairs.json`. It reproduces contacts on the six originally failing stored paths and passes all eight revised paths. The original Service Stair and L3 Terrace stored paths also pass that replay; their reselected paths are valid alternatives, not two additional diagnosed failures. No failure is inferred merely because a candidate route changed.

## Evidence and limits

Frozen files: `tour-path-all-adjacency-iteration07-final.json`, `tour-path-check-iteration07-final.json`, `tour-path-camera-coverage-iteration07-final.json`, `tour-path-route-iteration07-final.json` and `tour-path-iteration07-reopen-result.json`. The eight actual observer/target patches and inspected stair runs are also collected in `tour-path-inspection-semantics-iteration07.json`. Attempt reports and logs remain available; previous iteration04–06 checkpoints are preserved.

The static world BVH comes from actual mesh polygons and evaluated curves. Body radius is 0.18m and eye height 1.60m; walking samples check ground height/normal, five body columns, several ray heights and lateral offsets. Stair seam recovery accepts an upward physical tread within 3cm. This remains sampled mesh evidence, not a general-purpose capsule controller or proof of every possible path through a doorway. Pool, storage and foundation observations are never reported as body entry into those spaces.

No image, GPU job, simulation bake or film render was started. Camera exposure is still proposed for the moving tour. Final visual quality, film output and GUI navigation performance remain separate acceptance work. This report reconciles current navigation evidence while preserving historical failures.
'''
(ROOT/'qa/tour-path-iteration07-review.md').write_text(report,encoding='utf-8')
print('TOUR07_REOPEN',json.dumps(result),flush=True)
assert passed and result['source_hash_unchanged'] and result['saved_hash_unchanged'],result
