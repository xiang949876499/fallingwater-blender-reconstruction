"""Frozen10f candidate navigation, isolated metadata and no production writes."""
import bpy,json,sys,hashlib,shutil,time
from pathlib import Path
R=Path('D:/zx/test/project');sys.path.insert(0,str(R/'scripts'))
import guest_circulation10_routes as adapter
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
attempt=args[args.index('--attempt')+1] if '--attempt' in args else '01'
assert attempt.isdigit()
do_full='--full' in args
source=Path(bpy.data.filepath);assert sha(source)==adapter.CANDIDATE_SHA
work=R/f'qa/guest-circulation10-navigation-attempt{attempt}-workspace'
assert not work.exists(),'Preserve previous attempts; choose a new number'
for folder in ('data','qa','scene'):(work/folder).mkdir(parents=True,exist_ok=True)
inputs=['data/main_house.json','data/guest_house.json','config.json','adjacency.csv']
protected_names=inputs+['data/tour-route.json','data/camera-settings-reviewed.json','scripts/tour.py','scripts/main_house.py','scripts/guest_house.py','scripts/furnishings.py','scripts/guest_circulation10.py','scripts/guest_circulation10_routes.py']
protected={n:sha(R/n) for n in protected_names}
for name in inputs:shutil.copy2(R/name,work/name)
(work/'scripts').mkdir()
for name in ('tour.py','guest_circulation10_routes.py'):
    shutil.copy2(R/'scripts'/name,work/'scripts'/name)
scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=4
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
original_poses={o.name:{'matrix':[list(row) for row in o.matrix_world],'lens':o.data.lens,
                       'shift':[o.data.shift_x,o.data.shift_y],'exposure':o.get('fw_exposure')} for o in scene.objects if o.type=='CAMERA'}
tour,rooms,spec=adapter.prepare(work,scene,rooms)
byid={r['id']:r for r in rooms}
local_probe=tour.Probe(scene,[(-5.5,25),(22,52),(4,14.5)])
candidates={rid:tour.room_candidates(byid[rid],local_probe,True) for rid in {r for p in spec['paths'].values() for r in (p['from'],p['to'])}}
checks=[]
for name,path in spec['paths'].items():
    result=tour.hinted_connection(byid[path['from']],byid[path['to']],local_probe,candidates,[])
    checks.append({'path_id':name,**result});print('C10_LOCAL_ROUTE',name,result['status'],result.get('failure'),flush=True)
local={'candidate_sha256':adapter.CANDIDATE_SHA,'attempt':attempt,'local_paths':checks,
       'counts':{k:sum(c['status'].startswith(k) for c in checks) for k in ('PASS','FAIL','NOT_RUN')},
       'thresholds':tour.circulation10_limits,'full_scope_requested':do_full}
(R/f'qa/guest-circulation10-navigation-local-attempt{attempt}.json').write_text(json.dumps(local,indent=2),encoding='utf-8')
result={'candidate_sha256':adapter.CANDIDATE_SHA,'attempt':attempt,'local_counts':local['counts'],
        'adapter_sha256':protected['scripts/guest_circulation10_routes.py'],
        'production_files_unchanged':{},'full_run':False,'checked_scene_saved':False,'accepted_for_delivery':False,
        'limits':tour.circulation10_limits}
if do_full and local['counts']['FAIL']==0 and local['counts']['NOT_RUN']==0:
    del local_probe
    graph=tour.adjacency_manifest(rooms);assert len(rooms)==60 and graph['edge_count']==60
    tour.install(scene,rooms)
    records={}
    for rel,label in [('qa/tour-path-all-adjacency.json','all-adjacency'),('qa/tour-path-check.json','check'),('qa/tour-path-camera-coverage.json','camera-coverage'),('data/tour-route.json','route')]:
        data=json.loads((work/rel).read_text(encoding='utf-8'))
        data.update(candidate_sha256=adapter.CANDIDATE_SHA,attempt=attempt,candidate_only=True,accepted_for_delivery=False)
        if label=='camera-coverage':data.update(checked_blend=None,checked_blend_note='Not saved unless all graph/frame gates pass; see candidate result.')
        if label=='route':data['delivery_status']='CANDIDATE10_PHYSICAL_AUDIT_NOT_VISUAL_ACCEPTANCE'
        (R/f'qa/guest-circulation10-navigation-{label}-attempt{attempt}.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
        records[label]=data
    graph=records['all-adjacency'];coverage=records['camera-coverage'];route=records['route']
    frames=sum(s['frames_checked'] for s in coverage['segment_checks'])
    failures=sum(s.get('geometry_failure_frame_count',0) for s in coverage['segment_checks'])
    graph_pass=graph['counts']=={'PASS':60,'FAIL':0,'NOT_RUN':0} and graph['normal_walk_edge_pass_count']==52 and graph['inspection_edge_pass_count']==8
    frame_pass=frames==7584 and failures==0 and coverage['status']=='PASS_CAMERA_VALUES_AND_COVERAGE' and coverage['covered_room_count']==60 and len(route['main_segments'])==10 and len(route['supplemental_segments'])==49 and not route['excluded_requested_segments'] and not route['uncovered_room_ids']
    result.update(full_run=True,counts=graph['counts'],normal_walk_pass=graph['normal_walk_edge_pass_count'],inspection_pass=graph['inspection_edge_pass_count'],
                  graph_pass=graph_pass,frame_count=frames,frame_geometry_failures=failures,frame_pass=frame_pass,
                  camera_status=coverage['status'],failed_edges=[e for e in graph['edges'] if not e['status'].startswith('PASS')],
                  full_status='PASS_CANDIDATE_GEOMETRY_ONLY' if graph_pass and frame_pass else 'FAIL_OR_INCOMPLETE_CANDIDATE_NAVIGATION')
    if graph_pass and frame_pass:
        dest=R/'scene'/f'Fallingwater_guest_circulation10_navigation_attempt{attempt}.blend'
        assert not dest.exists()
        bpy.data.texts['FW_ROOMS.json'].clear();bpy.data.texts['FW_ROOMS.json'].write(json.dumps(rooms,indent=2))
        txt=bpy.data.texts.new('FW_GUEST_CIRCULATION10_ROUTES.json');txt.write(json.dumps(spec,indent=2))
        bpy.ops.wm.save_as_mainfile(filepath=str(dest),check_existing=False)
        result.update(checked_scene_saved=True,candidate_tour_scene=str(dest),candidate_tour_sha256=sha(dest),independent_reopen='PENDING')
result['production_files_unchanged']={n:sha(R/n)==h for n,h in protected.items()}
result['source_scene_unchanged']=sha(source)==adapter.CANDIDATE_SHA
result['saved_room_camera_changes']=[]
for name,old in original_poses.items():
    if name in ('CAM_TOUR','CAM_TOUR_SUPPLEMENTAL'):continue
    o=scene.objects.get(name)
    now=None if o is None else {'matrix':[list(row) for row in o.matrix_world],'lens':o.data.lens,'shift':[o.data.shift_x,o.data.shift_y],'exposure':o.get('fw_exposure')}
    if now!=old:result['saved_room_camera_changes'].append(name)
(R/f'qa/guest-circulation10-navigation-result-attempt{attempt}.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('C10_NAV_RESULT',json.dumps({k:result[k] for k in result if k not in ('failed_edges','production_files_unchanged')}),flush=True)
assert all(result['production_files_unchanged'].values()) and result['source_scene_unchanged'] and not result['saved_room_camera_changes']
