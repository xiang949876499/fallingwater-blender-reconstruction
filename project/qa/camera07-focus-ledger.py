"""Record images actually opened by camera04; recommendations only."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
folder = ROOT/'renders/previews/iteration07-focus'
benchmark = json.loads((folder/'render-benchmark.json').read_text(encoding='utf-8'))
expected_scene = 'bf50530009e4a93315915815473188c91d891272ef2d8e9e0169b704bd2e2f16'
assert benchmark['scene_sha256'] == expected_scene
config_path = ROOT/'data/camera-settings-reviewed.json'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(config_path) == '4def78dcbae91f3292562f41796adec71c4680b64e04301f051fdc1833ce8666'

notes = {
 'CAM_GUEST_L1_LOUNGE_A': {
  'status':'STAGED_COMPOSITION_ACCEPTED', 'opened_brackets':[1.6,2.4,3.2], 'recommended_ev':3.6,
  'observation':'Seating-side broad view retains left windows and sofa, glass door, table edge, fireplace opening/hearth at right and bookcase edge. Large bookcase no longer blocks the firebox bottom. A and B together explain complementary room relationships.',
  'remaining':'Firebox interior is dark; table is cropped and large central stone pier occupies substantial frame. Materials and final photoreal lighting are not accepted.',
  'exposure_reason':'Current3.6 is not materially overbright. EV3.2 is slightly moodier and2.4/1.6 lose stone and seating shadow detail. Keep3.6; do not force dark unlit firebrick bright through global exposure.'},
 'CAM_GUEST_L1_LOUNGE_B': {
  'status':'READABLE_SECONDARY_VIEW', 'opened_brackets':[1.6,2.4,3.2,3.6], 'recommended_ev':3.0,
  'observation':'Bookcase, armchair, correct southeast screen/cabinet, and window-side bench are readable; screen sits in the room rather than filling the lens with foreground slats. Complements A, without claiming this view shows the fireplace.',
  'remaining':'Central screen/cabinet occupies much of the view; foreground floor is dark and table partly cropped. Generic furniture and materials need refinement.',
  'exposure_reason':'Current3.0 is readable and not materially underexposed for diagnostic use.3.2 gives a small shadow improvement and3.6 is brighter but changes mood;2.4/1.6 are weaker. No necessary config change.'},
 'CAM_MAIN_L3_STUDY_B': {
  'status':'LIMITED_DESK_VIEW_LOCAL_FLOOR_STRIP_RESOLVED', 'opened_brackets':[2.4,3.2,3.6], 'recommended_ev':3.0,
  'observation':'The bright white horizontal strip under the desk visible in the earlier skyfill candidate is absent in integrated07 at the same camera and matching3.2EV bracket. The observed area is now continuous dark floor. Desk, chair and bookcase remain recognizable.',
  'remaining':'Chair feet and desk base are cropped; only a limited portion of the floor is visible. Whole-room floor, final composition and all source dimensions cannot be accepted from this image.',
  'exposure_reason':'Current3.0 is somewhat dark but readable.3.2 modestly improves detail;3.6 lifts the stone wall further, and2.4 is darker. Keep existing3.0 at this stage; raising exposure does not fix cropped framing.',
  'local_defect_status':'OBSERVED_BRIGHT_FLOOR_STRIP_ABSENT_IN_NEW_RENDER'},
 'CAM_MAIN_B_BATH_A': {
  'status':'LIMITED_FIXTURE_VIEW_LOCAL_CURVE_FIX_VISIBLE', 'opened_brackets':[2.4], 'recommended_ev':1.6,
  'observation':'No previous giant pipe/ring crosses the room. Narrow bent metal fixture/rail segments stay around the sink; WC seat and tank, sink and floor are readable.',
  'remaining':'WC pedestal/base is cut off by the lower edge, right sink is cropped and the room is not shown in full. Fixture shape/source fidelity and final materials still need refinement.',
  'exposure_reason':'Current1.6 retains ceramic shape and warm wall texture.2.4 is brighter without resolving framing or fixture fidelity; retain1.6.',
  'local_defect_status':'GIANT_CURVE_OVERSHOOT_NOT_VISIBLE'},
 'CAM_MAIN_L1_LIVING_A': {
  'status':'STAGED_COMPOSITION_EXPOSURE_ACCEPTED', 'opened_brackets':[1.6,3.2], 'recommended_ev':2.4,
  'observation':'Living room structure, desk/chair, glass openings and creek stair relationship are readable in the current2.4EV image with sky strength0.36. Terrace framing remains clear.',
  'remaining':'Large central column obscures part of the room by design of this view. Exterior is bright, glass edges/black lines and simplified material/furniture quality remain visibly synthetic.',
  'exposure_reason':'1.6 dims the interior;3.2 washes out more terrace/forest detail. Current2.4 is the preferred balance among the actually opened brackets.'},
 'CAM_HERO': {
  'status':'READABLE_ARCHITECTURE_WATER_VISUAL_FAIL', 'opened_brackets':[1.6], 'recommended_ev':0.8,
  'observation':'Exterior house and terrace massing readable. Current procedural waterfall is visibly segmented into parallel pale strips with artificial-looking perforation/foam. This is not the separate07a water prototype.',
  'remaining':'Water visual failure; overly smooth pale terrain and stepped geology, synthetic vegetation and overall photoreal quality remain unresolved. Composition/brightness cannot turn this into final visual acceptance.',
  'exposure_reason':'Current0.8 keeps exterior tonal detail.1.6 is brighter and flatter; no exposure increase recommended.'},
}
records=[]
for run in benchmark['runs']:
 name=run['camera'];note=notes[name]
 paths=[Path(run['png'])]
 for ev in note['opened_brackets']:
  paths.append(folder/(name+'_EV'+str(ev).replace('.','p')+'.png'))
 images=[{'path':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':sha(p),'actually_opened_by':'camera04'} for p in paths]
 # Record aliases only when byte-identical to opened image content.
 aliases=[{'path':str(Path(b['path']).relative_to(ROOT)).replace('\\','/'),'sha256':sha(Path(b['path'])),'viewed_as_identical_content':True}
          for b in run['exposure_bracket'] if Path(b['path']) not in paths and sha(Path(b['path'])) in {x['sha256'] for x in images}]
 records.append({'camera':name,'room_id':run['room_id'],'current_ev':run['exposure'],**note,
                 'actually_opened_images':images,'identical_content_aliases':aliases,
                 'final_quality_accepted':False,'config_change_made':False})
previous=ROOT/'renders/previews/iteration07-lighting-skyfill/CAM_MAIN_L3_STUDY_B_EV3p2.png'
ledger={
 'scene':benchmark['scene'],'scene_sha256':expected_scene,'config_sha256':sha(config_path),
 'render_benchmark_sha256':sha(folder/'render-benchmark.json'),
 'resolution':benchmark['resolution'],'samples':benchmark['max_samples'],'engine':benchmark['engine'],'device':benchmark['device']['device'],
 'reviewed_camera_count':6,'room_camera_count_in_120':5,'distinct_room_records':4,
 'actually_opened_current_png_count':sum(len(r['actually_opened_images']) for r in records),
 'previous_comparison':{'path':str(previous.relative_to(ROOT)).replace('\\','/'),'sha256':sha(previous),'scene_sha256':'682db2912eeb0cac78709f0bb17253c3691bd4ffd331021a0f2ab55e06db5d69','actually_opened_by':'camera04','purpose':'SameStudyB3.2EV before/after bright strip comparison; not a current07 image.'},
 'scope':'Actual visual review of six cameras and the explicitly listed same-EXR brackets only. All24 bracket filenames were not automatically counted as reviewed. Five room camera views are part of the120, HERO is separate. No full120 visual, photo-match, navigation, final-water or final-quality acceptance.',
 'production_config_unchanged':True,'final_quality_accepted':False,'cameras':records,
}
(ROOT/'qa/camera07-focus-visual-ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summary_path=ROOT/'qa/camera07-validation-summary.json'
summary=json.loads(summary_path.read_text(encoding='utf-8'))
summary['visual_review_status']='SIX_FOCUS_VIEWS_ACTUALLY_REVIEWED_WITH_EXPLICIT_BRACKETS_NOT_FULL120'
summary['visual_ledger']='qa/camera07-focus-visual-ledger.json'
summary['visual_ledger_sha256']=sha(ROOT/summary['visual_ledger'])
summary_path.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'cameras':6,'opened_current_pngs':ledger['actually_opened_current_png_count'],'current_config_sha256':sha(config_path),'recommendation':'Keep existing exposures; stage composition and local defects recorded, no final visual pass.'}))
