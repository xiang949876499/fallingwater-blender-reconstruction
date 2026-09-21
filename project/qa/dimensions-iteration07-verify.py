"""Validate nominal target guards and independently remeasure the frozen scene."""
import copy
import hashlib
import json
import sys
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from dimension_audit import audit_dimensions
from nominal_targets import load_reviews, qualify

source = ROOT / 'scene/Fallingwater_iteration07.blend'
digest = hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
report = audit_dimensions(ROOT, scene_path=source, expected_sha256=digest,
                          prefix='dimensions-iteration07-independent', write_csv=False)
rows = {r['id']: r for r in report['measurements']}
reviews = load_reviews(ROOT)
checks = []
def check(name, condition):
    checks.append({'test': name, 'pass': bool(condition)})

check('22_numeric_and_only_two_new_nominal_qualifications',
      report['numeric_counts'] == {'NOT_RUN': 21, 'PASS': 22}
      and report['standard_counts'] == {'NOT_RUN': 21, 'PASS': 14, 'SOURCE_PRECISION_LIMIT': 8})
for key, historical in [('MAIN_LEVEL_2', .025), ('GUEST_POOL_WIDTH', .0254)]:
    row = rows[key]
    check(key + '_unknown_precision_preserved_without_zero',
          row['source_recorded_uncertainty_m'] == historical
          and row['source_reading_uncertainty_m'] is None
          and row['survey_absolute_accuracy_m'] is None
          and row['tolerance_m'] == .020)
    for label, change in [('source_label', 'different label'), ('source', 'different sheet'),
                          ('reference_m', row['reference_m'] + .001),
                          ('endpoints', [{'object': 'WRONG_SURFACE'}]), ('actual_mesh_m', None)]:
        changed = copy.deepcopy(row); changed[label] = change
        check(key + '_reject_changed_' + label, qualify(changed, reviews) is None)
check('unreviewed_room_endpoints_remain_limited', all(rows[k]['standard_result'] == 'SOURCE_PRECISION_LIMIT'
      for k in rows if k.startswith(('GUEST_BOILER_', 'GUEST_GUEST_ROOM_', 'GUEST_LAUNDRY_', 'GUEST_BASE_BATH_')) and rows[k]['actual_mesh_m'] is not None))
check('unmeasured_values_remain_null', all(r['actual_mesh_m'] is None and r['delta_m'] is None
      for r in rows.values() if r['numeric_result'] == 'NOT_RUN'))
check('missing_categories_still_incomplete', report['geo02_overall'] == 'INCOMPLETE'
      and all(report['category_coverage'][k]['coverage'] == 'MISSING' for k in ['cantilever', 'openings', 'connections']))
check('saved_scene_unchanged', digest == hashlib.sha256(source.read_bytes()).hexdigest())
result = {'status': 'PASS' if all(c['pass'] for c in checks) else 'FAIL',
          'scene_sha256': digest, 'checks': checks, 'saved_scene_changes': False}
(ROOT / 'qa/dimensions-iteration07-verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
assert result['status'] == 'PASS'
