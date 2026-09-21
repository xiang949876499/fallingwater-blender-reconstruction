"""Record actual reviewed outcomes; retain final-quality gates separately."""
import csv
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = root / 'qa/issues.csv'
with p.open(encoding='utf-8-sig', newline='') as f:
    reader = csv.DictReader(f)
    columns = reader.fieldnames
    rows = list(reader)
by_id = {r['issue_id']: r for r in rows}
by_id['FW-002'].update(
    scene_version='furniture07e; camera07e', result='INCOMPLETE',
    description='Production camera configuration now includes supported Loggia/Plunge positions and complementary Lounge A/B. All120 geometry checks pass on07e; new Lounge A actual wide view composition accepted. Full07 geometry and complete actual room-image coverage pending.',
    evidence_path='project/qa/camera07e-final-review.md')
by_id['FW-016'].update(
    scene_version='geology07c', result='INCOMPLETE',
    description='Actual07c HERO and WATER_DETAIL improve bed separation and local fractures; exact reproduced geometry adopted as next-iteration collision baseline. Tan uniformity/gloss and smooth near-bank ground still below final realism. Independent bank covering candidate pending.',
    evidence_path='project/qa/core-geology07c-fresh-module-reproduction.json')
by_id['FW-017'].update(
    scene_version='furniture07e', issue_state='RESOLVED', result='PASS',
    description='Scoped27 bathroom curve overshoots repaired with endpoints/radii/transforms preserved. Evaluated towel center envelope181.10mm to90mm; same-camera actual Cycles image confirms slim straight rail. General fixture form/placement realism remains outside this closed shape defect.',
    evidence_path='project/qa/bath-fixtures-iteration06-review.md',
    required_retest='Reopen if pipe geometry changes; general fixture realism remains part of final room visual review')
new = [
    dict(issue_id='FW-018', severity='P1', test_id='GEO-01;GEO-07', scene_version='candidate07',
         room_or_asset_id='Main L1 west parapet and south fascia', issue_state='OPEN', result='INCOMPLETE',
         description='Independent main07/08 elevations show west exposed band was too shallow. Source-supported three-object correction and local clearance/reproduction pass; actual same-camera renders and full integration pending. South window upstand/axis needs separate source resolution.',
         evidence_path='project/qa/photo-match07-west-band-check.json',
         required_retest='Actual source comparison plus integrated geometry; do not accept ambiguous87 point identities from low residual'),
    dict(issue_id='FW-019', severity='P1', test_id='GEO-06', scene_version='iteration06',
         room_or_asset_id='Main L3 Study floor perimeter', issue_state='OPEN', result='FAIL',
         description='Actual first-hit camera ray below desk at pixel850,507 reaches L2 wall top Z5.06 below Study floor5.286. North Study room polygon ends321mm before actual wall inner face, exposing lower geometry. Most other bright-strip samples hit real cork floor; not all brightness is a hole.',
         evidence_path='project/qa/study-base-strip07-probe.json',
         required_retest='Source-constrained physical slab/finish perimeter closure, actual ray regression and same-view render')
]
for row in new:
    if row['issue_id'] in by_id:
        by_id[row['issue_id']].update(row)
    else:
        rows.append(row)
with p.open('w', encoding='utf8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)
print({'issues': len(rows), 'resolved': sum(r['issue_state'] == 'RESOLVED' for r in rows)})
