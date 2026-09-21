"""Exercise empty Boolean-rim handling without changing any saved scene."""
import csv, hashlib, json, sys
from pathlib import Path
import bpy
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from dimension_audit import MeshReader, audit_dimensions

checks = []
scene05 = ROOT / 'scene/Fallingwater_iteration05.blend'
scene06 = ROOT / 'scene/Fallingwater_iteration06.blend'
before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in [scene05, scene06]}
bpy.ops.wm.open_mainfile(filepath=str(scene05))
reader05 = MeshReader()
reader05.pool_coping_names()
checks.append({'test': 'uncut_iteration05_keeps_all_nonempty_rim_segments', 'pass': reader05.empty_coping_segments == []})
bpy.ops.wm.open_mainfile(filepath=str(scene06))
report = audit_dimensions(ROOT, scene_path=scene06, prefix='dimensions-iteration06-verification-measurements',
                          expected_sha256=before[str(scene06)], write_csv=False)
checks.append({'test': 'four_documented_cut_segments_recorded', 'pass': report['documented_empty_coping_segments'] == ['GUEST_POOL_coping_13', 'GUEST_POOL_coping_14', 'GUEST_POOL_coping_15', 'GUEST_POOL_coping_16']})
checks.append({'test': '22_numeric_12_precision_qualified', 'pass': report['numeric_counts'] == {'NOT_RUN': 21, 'PASS': 22} and report['standard_counts'] == {'NOT_RUN': 21, 'PASS': 12, 'SOURCE_PRECISION_LIMIT': 10}})
with (ROOT / 'dimensions.csv').open(encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))
checks.append({'test': 'untested_values_stay_blank', 'pass': all(r['model_m'] == r['difference_m'] == '' for r in rows if r['numeric_result'] == 'NOT_RUN')})
try:
    MeshReader().names(exact=['NONEXISTENT_DIMENSION_MESH'])
    rejected = False
except ValueError:
    rejected = True
checks.append({'test': 'missing_object_still_rejected', 'pass': rejected})
ob = bpy.data.objects['GUEST_POOL_coping_16']
original = ob['source_entry_cut']
del ob['source_entry_cut']
try:
    MeshReader().pool_coping_names()
    rejected = False
except ValueError as exc:
    rejected = 'Undocumented empty pool coping segment' in str(exc)
finally:
    ob['source_entry_cut'] = original
checks.append({'test': 'undocumented_empty_segment_rejected', 'pass': rejected})
checks.append({'test': 'both_saved_scenes_unchanged', 'pass': all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == digest for p, digest in before.items())})
checks.append({'test': 'geo02_stays_incomplete', 'pass': report['geo02_overall'] == 'INCOMPLETE'})
out = {'tests': checks, 'status': 'PASS' if all(c['pass'] for c in checks) else 'FAIL', 'saved_scene_changes': False}
(ROOT / 'qa/dimensions-iteration06-verification.json').write_text(json.dumps(out, indent=2), encoding='utf8')
print(json.dumps(out, indent=2))
assert out['status'] == 'PASS'
