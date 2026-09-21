"""Update live issues from actual checkpoint evidence, retaining prior ledger."""
from pathlib import Path
import csv,io,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'qa/issues.csv';before=path.read_bytes()
backup=ROOT/'qa/issues-before-checkpoint10.csv';assert not backup.exists()
reader=csv.DictReader(io.StringIO(before.decode('utf-8-sig')));fields=reader.fieldnames;rows=list(reader)
updates={
'FW-001':('iteration10','RESOLVED','PASS','Full10 actual graph60/60 (52walk8inspection),7584 saved frames and independent unchanged-key reopen PASS. Scope sampled modeled geometry; GUI separate.','project/qa/integration10-navigation-reopen.json'),
'FW-002':('iteration10','OPEN','INCOMPLETE','Current120 actual saved camera poses pass sampled geometry3720 rays;10 poses changed. Under24mm views remain diagnostic; full current120 complementary actual images pending.','project/qa/camera10-actual-check.json'),
'FW-003':('water10;water11','OPEN','FAIL','Native48 six actual images show isolated source and cropped pool boundaries. S24/S48 diagnostic flux2.03/1.56x C target, bothFAIL. Native candidates not installed; source/cache incident tracked separately.','project/qa/water10-root-visual.md'),
'FW-009':('iteration10','RESOLVED','PASS','Current44 measured rows all reference frozen10 SHA;23numeric matches,15nominal passes,8source precision limits,21NOT_RUN. Actual retained north/east0 slab selectors and72width stations remeasured after deleted old slab/tread selectors failed; originals preserved. Overall category gate remainsFW015.','project/qa/dimensions-iteration10c.json'),
'FW-013':('iteration10','OPEN','NOT_RUN','Saved10 graph60/60 and7584 frames pass twice;10 main segments49supplemental. Final2-4minute1080p movie and actual room supplement films NOT_RUN.','project/qa/integration10-navigation-reopen.json'),
'FW-015':('iteration10;candidate11','OPEN','INCOMPLETE','Current44:15standard,8precision-limited,21unmeasured. Four new printed terrace/bay targets failed prior shape; terrace11 repaired locally, guestbay11 in progress. Final same-scene20nominal plus category coverage remains incomplete.','project/qa/dimensions10-source-review.md'),
'FW-016':('iteration10;candidate11/12','OPEN','INCOMPLETE','10 has16accepted shrubs.18tree native canopy candidate passed local actual images/reopen; floor11 soil direction accepted only. Smooth bare terrain/sparse brush stillFAIL; litter12 and full-water contact pending.','project/qa/forest-floor11-root-visual.md'),
'FW-020':('iteration10','RESOLVED','PASS','Corrected guest two-flight circulation/source outer wall integrated;72actual finished-face width stations meet2ft5in nominal within20mm, full routes/reopen pass. C south datum/shape labels remain disclosed.','project/qa/dimensions-iteration10c.json'),
'FW-021':('iteration10','OPEN','INCOMPLETE','Loggia/Master/Bath interfaces corrected and local images viewed; combined1178floor samples pass. Whole-room photography and ceiling source correction remain incomplete.','project/qa/integration10a-root-review.md'),
'FW-022':('iteration10','RESOLVED','PASS','Guest source six flights and lowered south arrival, fixed west glazing and true southeast door integrated.3503local strict samples and full60/7584 saved-reopen pass; overall photo realism remains separate.','project/qa/guest-circulation10-root-visual.md'),
}
for row in rows:
    if row['issue_id'] in updates:
        v=updates[row['issue_id']]
        for key,value in zip(('scene_version','issue_state','result','description','evidence_path'),v):row[key]=value
        if row['issue_id']=='FW-001':row['required_retest']='Rerun affected true openings and full graph after relevant geometry changes; GUI/performance separate'
new=[
('FW-023','P1','GEO-01;VIS-02','iteration10','Main Master ceiling','OPEN','FAIL','SourceHABS/photos show continuous south low ceiling;10 narrow box is unsupported. C height/level break unresolved, continuous field/window interfaces candidate11 in progress.','project/qa/master-ceiling11-source-review.md','Source-supported ceiling continuity, true window/door interfaces and strict actual-route regression'),
('FW-024','P1','PKG-01;QA-EVIDENCE','water11-S48','Native cache provenance','OPEN','ORIGINAL_CACHE_MISSING','Preparation changed fluid setting while still linked to oldS48 cache;36files7.75MB were cleared.684others hash unchanged. Isolated reproduction complete but comparison/re-audit pending; old path remains missing.','project/qa/water11-source-cache-incident.md','New cache byte/decoded comparison and full12frame re-audit; retain incident and old missing-file evidence'),
('FW-025','P1','VIS-01','iteration10','CAM_MAIN_OVERVIEW','OPEN','FAIL','Root actually opened current exterior1280x720:overview largely blocked by near tree canopy. HERO reveals synthetic masonry/water. Trees preserved; alternative overview camera search running.','project/renders/previews/checkpoint10-exterior/render-benchmark.json','New camera physical clearance and actual image review without removing trees or altering building'),
]
assert not {x[0] for x in new}&{r['issue_id'] for r in rows}
rows.extend(dict(zip(fields,row)) for row in new)
backup.write_bytes(before)
with path.open('w',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
print(json.dumps({'issues':len(rows),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}))
