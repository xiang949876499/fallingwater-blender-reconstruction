"""Update the live issue register without erasing historical QA reports."""
import csv
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / 'qa/issues.csv'
with path.open(encoding='utf8', newline='') as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    rows = list(reader)
by_id = {r['issue_id']: r for r in rows}
updates = {
    'FW-001': dict(scene_version='iteration06; source candidate07', result='INCOMPLETE', description='Iteration06 61 declared edges: 60 PASS and one FAIL. Original drawings disprove the assumed dry route across the plunge; candidate07 retracts this unsupported edge and shortens an erroneous wall. Updated integrated graph still needs verification.', evidence_path='project/qa/main-pool-iteration06-report.md', required_retest='Rebuild source-corrected graph; validate real room access and typed pool observation, retaining old ADJ017 failure history'),
    'FW-002': dict(scene_version='iteration06', description='Full check 118 of 120 original positions pass; Loggia A and Plunge A need support repairs. Both Guest Lounge actual images fail semantic framing. Four candidates and an additional firebox detail are being rendered.', evidence_path='project/qa/iteration06-focus-review.md', required_retest='Final 120 camera geometry plus actual complementary images; two room views cannot be replaced by a detail image'),
    'FW-004': dict(result='FAIL', scene_version='run06; entry01', description='Run06 source head does not join the program river. Entry01 36-frame experiment produces insufficient outlet water depth and coverage; preserved as failed local experiment.', evidence_path='project/qa/fluid-entry01-review.md', required_retest='Same-view program/cache diagnostic with real contact and safe upstream water level, then continuous sequence'),
    'FW-006': dict(scene_version='iteration06', description='Independent seven-level EEVEE bake and nine images completed. Bath self-shadow and Living FastGI symptoms improve; Kitchen Study Laundry and guest-bedroom image defects remain.', evidence_path='project/qa/eevee-iteration06-review.md'),
    'FW-007': dict(scene_version='iteration06', result='INCOMPLETE', description='Glass preview survived integration without changing Cycles glass surface or panes; guest glazing and reflection artifacts still need actual-image checks.', evidence_path='project/qa/eevee-iteration06-review.md'),
    'FW-009': dict(scene_version='iteration06', issue_state='RESOLVED', result='PASS', description='Central ledger now measures saved evaluated meshes. Four completely cut coping segments are explicitly recorded rather than treated as missing geometry. 22 actual values and 21 blank NOT_RUN values; eight regression checks PASS.', evidence_path='project/qa/dimensions-iteration06-verification.json', required_retest='Repeat independent measured ledger after each saved rebuild; GEO02 category and source-precision gaps tracked separately'),
    'FW-013': dict(scene_version='iteration06', description='Saved tour reopened and 7584 integer frames checked. Two static 384x216 EEVEE frames and signature-verified resume pass only the rendering pipeline; no final film.', evidence_path='project/qa/animation-renderer06-smoke-review.md'),
}
for key, values in updates.items():
    by_id[key].update(values)
extra = [
    dict(issue_id='FW-015', severity='P1', test_id='GEO-02', scene_version='iteration06', room_or_asset_id='Dimension coverage and source precision', issue_state='OPEN', result='INCOMPLETE', description='22 numeric agreements contain only 12 standard passes; 10 source precision limits remain. Cantilever opening and connection categories are missing.', evidence_path='project/qa/dimensions-iteration06.json', required_retest='Source-supported independent endpoints and category coverage without relaxing tolerance'),
    dict(issue_id='FW-016', severity='P1', test_id='VIS-01;VIS-03;VIS-07', scene_version='iteration06', room_or_asset_id='Core sandstone and near-bank terrain', issue_state='OPEN', result='FAIL', description='Actual HERO and WATER_DETAIL show repeated slab-like rock layers and smooth near-bank terrain. Independent source-based core candidate awaits matched render review; old liquid cache cannot qualify changed bedrock.', evidence_path='project/qa/site-visual-iteration06-review.md', required_retest='Matched baseline/candidate geology images and reference review before final water cache'),
    dict(issue_id='FW-017', severity='P1', test_id='GEO-06;VIS-03', scene_version='iteration06', room_or_asset_id='Bathroom curved fittings', issue_state='OPEN', result='FAIL', description='Actual towel rail curve exceeds its intended control envelope by 91mm; shower riser also overshoots. Scoped curve correction under construction; general C-level fixture realism remains unaccepted.', evidence_path='project/qa/bath-fixtures-iteration06-probe.json', required_retest='Actual evaluated bounds and same-camera fixture renders; preserve placement and source form'),
]
for row in extra:
    if row['issue_id'] in by_id:
        by_id[row['issue_id']].update(row)
    else:
        rows.append(row)
assert len({r['issue_id'] for r in rows}) == len(rows)
assert all(set(r) == set(fields) for r in rows)
with path.open('w', encoding='utf8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
print({'issues': len(rows), 'resolved': sum(r['issue_state'] == 'RESOLVED' for r in rows)})
