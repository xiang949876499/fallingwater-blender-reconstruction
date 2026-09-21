"""Independent saved-scene measurements and negative nominal/mesh checks."""
import copy
import hashlib
import json
import sys
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from dimension_audit import audit_dimensions, MeshReader
from nominal_targets import load_reviews, qualify

checks = []
def check(name, condition):
    checks.append({'test': name, 'pass': bool(condition)})

sources = [ROOT / 'scene/Fallingwater_iteration07.blend',
           ROOT / 'scene/Fallingwater_iteration08.blend']
digests = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
reports = []
for index, source in enumerate(sources):
    bpy.ops.wm.open_mainfile(filepath=str(source))
    report = audit_dimensions(ROOT, scene_path=source, expected_sha256=digests[source.name],
        prefix='dimensions-iteration08-independent-' + str(index), write_csv=False)
    reports.append(report)
    rows = {r['id']: r for r in report['measurements']}
    stair = rows['GUEST_LAUNDRY_STAIR_CLEAR']
    check(source.stem + '_all_missing_values_are_null', all(
        r['actual_mesh_m'] is None and r['delta_m'] is None
        for r in rows.values() if r['numeric_result'] == 'NOT_RUN'))
    if index == 0:
        check('old_scene_missing_new_wall_is_NOT_RUN', stair['numeric_result'] == 'NOT_RUN'
              and stair['standard_result'] == 'NOT_RUN' and stair['actual_mesh_m'] is None)
    else:
        check('new_scene_visible_finish_stair_target_PASS', stair['numeric_result'] == 'PASS'
              and stair['standard_result'] == 'PASS' and len(stair['stations']) == 3)
        check('new_stair_rough_finish_not_base_plane_measurement',
              stair['endpoints'][0]['object'] == 'GUEST_LAYERED_SANDSTONE_COURSES'
              and abs(stair['actual_mesh_m'] - .7475495338) < 1e-5)
        check('all_three_stair_stations_within_original_tolerance',
              stair['tolerance_m'] == .020
              and max(abs(s['actual_mesh_m'] - stair['reference_m'])
                      for s in stair['stations']) <= .020)
        check('nominal_review_does_not_invent_source_survey_precision',
              stair['source_reading_uncertainty_m'] is None
              and stair['survey_absolute_accuracy_m'] is None)
        reviews = load_reviews(ROOT)
        for key in ['MAIN_LEVEL_2', 'GUEST_POOL_WIDTH', 'GUEST_LAUNDRY_STAIR_CLEAR']:
            row = rows[key]
            check(key + '_actual_review_matches', qualify(row, reviews) is not None)
            for field, value in [('source_label', 'WRONG LABEL'), ('source', 'WRONG SHEET'),
                                 ('reference_m', row['reference_m'] + .001),
                                 ('endpoints', [{'object': 'WRONG_SURFACE'}]),
                                 ('actual_mesh_m', None)]:
                altered = copy.deepcopy(row)
                altered[field] = value
                check(key + '_reject_' + field, qualify(altered, reviews) is None)
        check('room_face_inferences_not_upgraded', all(rows[key]['standard_result'] == 'SOURCE_PRECISION_LIMIT'
            for key in ['GUEST_BOILER_DIM_1', 'GUEST_BOILER_DIM_2', 'GUEST_GUEST_ROOM_LENGTH',
                        'GUEST_GUEST_ROOM_DEPTH', 'GUEST_LAUNDRY_LENGTH', 'GUEST_LAUNDRY_DEPTH',
                        'GUEST_BASE_BATH_LENGTH', 'GUEST_BASE_BATH_WIDTH']))
        check('connection_present_does_not_close_other_missing_categories',
              report['category_coverage']['connections']['coverage'] == 'PRESENT'
              and report['geo02_overall'] == 'INCOMPLETE'
              and report['category_coverage']['openings']['coverage'] == 'MISSING'
              and report['category_coverage']['cantilever']['coverage'] == 'MISSING')
        # In-memory negative control only: fresh BVH must detect an incorrect wall.
        # Never save it or label its measurements as the immutable saved-scene audit.
        wall = bpy.data.objects['GUEST_LAUNDRY_DESCENT_outer_retaining_wall']
        previous_x = wall.location.x
        try:
            wall.location.x += .050
            bpy.context.view_layer.update()
            sample = stair['stations'][0]['endpoints'][0]
            reader = MeshReader()
            ends = reader.opposite_rays(sample['selected_objects'], sample['ray_origin_m'], 0)
            shifted_width = ends[1]['point_m'][0] - ends[0]['point_m'][0]
            check('fresh_mesh_detects_50mm_wrong_wall',
                  abs(shifted_width - stair['actual_mesh_m'] - .050) < 1e-5
                  and abs(shifted_width - stair['reference_m']) > .020)
        finally:
            wall.location.x = previous_x
            bpy.context.view_layer.update()

for source in sources:
    check(source.stem + '_file_unchanged',
          hashlib.sha256(source.read_bytes()).hexdigest() == digests[source.name])
result = {'status': 'PASS' if all(c['pass'] for c in checks) else 'FAIL',
          'checks': checks, 'scene_sha256': digests,
          'audit_reports': ['dimensions-iteration08-independent-0.json', 'dimensions-iteration08-independent-1.json'],
          'negative_control': 'Temporary in-memory wall translation only; no save, render or production mutation.'}
(ROOT / 'qa/dimensions-iteration08-verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
assert result['status'] == 'PASS'

