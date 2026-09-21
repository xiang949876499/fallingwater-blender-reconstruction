"""Reopen the independent06 tour and freeze exact saved-animation evidence."""
import bpy,json,sys,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import tour
source=ROOT/'scene/Fallingwater_iteration06.blend'
expected='172b76340d1224a2b98f415b21042d19ad7fba4d849543d7156beb17e5fcf055'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
assert Path(bpy.data.filepath).name=='Fallingwater_tour_checked_iteration06.blend'
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
route=json.loads((ROOT/'data/tour-route.json').read_text(encoding='utf-8'))
assert Path(route['scene_file']).resolve()==source.resolve()
check=tour.camera_evidence(bpy.context.scene,rooms,route)
check.update(saved_scene_reopened=True,saved_scene=bpy.data.filepath,checked_blend=bpy.data.filepath,
    saved_scene_sha256=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
    source_scene_sha256=expected,iteration=6)
(ROOT/'qa/tour-path-camera-coverage.json').write_text(json.dumps(check,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ('qa/tour-path-check.json','qa/tour-path-all-adjacency.json','data/tour-route.json'):
    f=ROOT/name;record=json.loads(f.read_text(encoding='utf-8'))
    record.update(source_scene_sha256=expected,iteration=6,checked_blend=bpy.data.filepath)
    f.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
for a,b in [('qa/tour-path-all-adjacency.json','qa/tour-path-all-adjacency-iteration06-final.json'),
            ('qa/tour-path-check.json','qa/tour-path-check-iteration06-final.json'),
            ('qa/tour-path-camera-coverage.json','qa/tour-path-camera-coverage-iteration06-final.json'),
            ('data/tour-route.json','qa/tour-path-route-iteration06-final.json')]:shutil.copy2(ROOT/a,ROOT/b)
adj=json.loads((ROOT/'qa/tour-path-all-adjacency.json').read_text(encoding='utf-8'))
inspection={'status':'EXECUTED_ON_ITERATION06','source_scene_sha256':expected,'space_count_preserved':len(rooms),
            'inspection_edges':[e for e in adj['edges'] if e.get('acceptance_type')],
            'additional_prior_not_run_edge':next(e for e in adj['edges'] if e['id']=='ADJ_017'),
            'claim':'Inspection-only relationships are distinct from walking edges; explicit failures stay failures.'}
(ROOT/'qa/tour-path-inspection-semantics.json').write_text(json.dumps(inspection,ensure_ascii=False,indent=2),encoding='utf-8')
print('TOUR06_REOPEN',json.dumps({'status':check['status'],'frames':sum(s['frames_checked'] for s in check['segment_checks']),
    'counts':adj['counts'],'walk_pass':adj.get('normal_walk_edge_pass_count'),
    'inspection_pass':adj.get('inspection_edge_pass_count'),'saved_sha256':check['saved_scene_sha256'],
    'max_camera_position_error_m':max(s['max_path_error_m'] for s in check['segment_checks'])}),flush=True)
