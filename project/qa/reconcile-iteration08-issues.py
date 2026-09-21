"""Record current measured results without closing wider visual acceptance."""
import csv
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'qa/issues.csv'
backup = ROOT / 'qa/issues-before-iteration08.csv'
if not backup.exists():
    backup.write_bytes(path.read_bytes())
rows = list(csv.DictReader(path.open(encoding='utf-8-sig', newline='')))
updates = {
 'FW-001': dict(scene_version='iteration08', description='Source-corrected07 graph passed 60/60. New08 retaining wall affects two old approach routes; current fresh adjacency is 58 PASS and 2 FAIL. Replanning within real north approach in progress.', evidence_path='project/qa/iteration08-integration-decisions.md', required_retest='Fresh full08 graph and independently reopened complete routes; never remove true wall to restore old path'),
 'FW-002': dict(scene_version='iteration08', description='Full08 actual120 saved poses and support/body geometry PASS. Seven new actual focus images:3 readable,4 limited. Previous07 full120 visual ledger81 readable29 limited10 fail. New poses do not close structural seams or final room photography.', evidence_path='project/qa/camera08-review.md'),
 'FW-003': dict(scene_version='hybrid07; static08', description='Actual36-frame1.5s sequence still FAIL: smooth narrow band and disk foam. Static24 control loses47.91% mesh volume and32cm head; FLIP envelope confirms true sinking. Frozen155-point variant removes reversed faces but reduces one local water thickness59%; rejected.', evidence_path='project/qa/water08-static-head24-review.md'),
 'FW-006': dict(scene_version='window08-preview', result='INCOMPLETE', description='One-window weak noncamera World plus20W AREA improves brown wood/readability without VOLUME lobes; actual image still has hard ceiling light boundary and grain. PARTIAL candidate not integrated. Local Cycles restore fresh-reopen PASS; full preview/FPS pending.', evidence_path='project/qa/eevee-iteration08-window-preview-review.md'),
 'FW-009': dict(scene_version='iteration08', description='Central ledger independently measures saved evaluated meshes:44 rows,23 numeric matches,21 blank. Thirty independent saved-scene/nominal guards including 50mm wrong-wall negative control PASS. GEO02 category and source precision acceptance remain separate.', evidence_path='project/qa/dimensions-iteration08-verification.json'),
 'FW-013': dict(scene_version='iteration08', description='07 independent7584 integer frames PASS but no full film. New08 all-frame regression in progress after new physical retaining wall; two adjacency approaches currently fail and require true-route repair. Final2-4minute1080p film and remaining room supplements NOT_RUN.', evidence_path='project/qa/iteration08-integration-decisions.md'),
 'FW-015': dict(scene_version='iteration08', description='23 numeric agreements:15 nominal-standard passes,8 unresolved source/endpoint precision limits;21 unmeasured remain blank. New laundry stair visible-face anchor covers connections; cantilever/openings remain missing and site has pool-only coverage.', evidence_path='project/qa/dimensions-build-20260920-154629.json'),
 'FW-016': dict(scene_version='iteration08', description='Core v3 frozen; rock/forest/water visual quality still FAIL. Bank08 geometry-only path-boundary repair integrated and actual three focus views inspected; soil/path contact improves. Candidate grey tint and07b added leaf scatter rejected.', evidence_path='project/qa/iteration08-integration-decisions.md'),
 'FW-020': dict(scene_version='iteration08', description='Source-supported rounded laundry-stair wall integrated. Three freshly measured visible-face stations meet2ft5in nominal within original20mm; local diagnostic images reviewed. Height/material and rough-face placement C. New wall blocks two old approaches; issue remains open pending full corrected-route check.', evidence_path='project/qa/guest-stair-wall08-review.md'),
}
for row in rows:
    row.update(updates.get(row['issue_id'], {}))
if not any(r['issue_id'] == 'FW-021' for r in rows):
    rows.append(dict(issue_id='FW-021', severity='P1', test_id='GEO-06;VIS-03', scene_version='iteration08',
        room_or_asset_id='Main floor/wall/ceiling interfaces', issue_state='OPEN', result='FAIL',
        description='08 closes multiple floor/ceiling seams. Actual new images still show Loggia L-pier corner missing solids/entry-coat floor overlap, Master floor overlap/ceiling gap, and L3 Bath A wall-foot gaps. Source-bound09 local repair in progress; new camera angles do not hide or close defects.',
        evidence_path='project/qa/structure08b-remaining-review.md',
        required_retest='Actual same-camera09 images plus explicit mesh/real-opening controls and full integrated support/route regression'))
with path.open('w', encoding='utf-8', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print({'rows': len(rows), 'updated': list(updates), 'new': 'FW-021'})
