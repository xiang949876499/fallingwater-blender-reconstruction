"""Compose both route adapters and validate the complete saved physical10a."""
from pathlib import Path
import bpy,json,sys,hashlib,shutil,time
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import guest_circulation10_routes as guest
import master_navigation10 as master
SOURCE=ROOT/'scene/Fallingwater_integration_candidate10a.blend'
SHA='dc7594d60b68effaf10b85dd1804827fc9cb16dd786656daa4da16c761b33518'
WORK=ROOT/'qa/integration10-navigation-workspace'
OUT=ROOT/'scene/Fallingwater_navigation_candidate10a.blend'
REPORT=ROOT/'qa/integration10-navigation-result.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(SOURCE)==SHA and not WORK.exists() and not OUT.exists() and not REPORT.exists()
assert sha(ROOT/'scripts/master_navigation10.py')=='dafbd4ded6c14112e8d07292ada5bb880eb65433b81e507a87afeb4661eb6e9a'
assert sha(ROOT/'scripts/guest_circulation10_routes.py')=='a9298ba4f340eb91c461988f6ff19698e49153742e6b08b376af9b8e3f173412'
started=time.monotonic()
for folder in ('data','qa','scripts','scene'):(WORK/folder).mkdir(parents=True,exist_ok=True)
inputs=['data/main_house.json','data/guest_house.json','config.json','adjacency.csv']
protected=inputs+['data/tour-route.json','data/camera-settings-reviewed.json','scripts/tour.py','scripts/main_house.py','scripts/guest_house.py','scripts/furnishings.py']
before={p:sha(ROOT/p) for p in protected}
for name in inputs:shutil.copy2(ROOT/name,WORK/name)
for name in ('tour.py','guest_circulation10_routes.py','master_navigation10.py'):shutil.copy2(ROOT/'scripts'/name,WORK/'scripts'/name)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene
scene.render.threads_mode='FIXED';scene.render.threads=4
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
tour,rooms,guest_spec=guest.prepare(WORK,scene,rooms)
master_spec=master.apply(tour,scene,rooms,WORK)
master.apply_cameras(scene)
guest_cameras=json.loads((ROOT/'qa/guest-circulation10-navigation-camera-overrides.json').read_text(encoding='utf8'))
guest_cameras.update(json.loads((ROOT/'qa/guest-circulation10-navigation-entry-camera-retreat.json').read_text(encoding='utf8')))
for name,values in guest_cameras.items():
    ob=scene.objects[name]
    ob.location=values['location']
    ob.rotation_euler=(Vector(values['target'])-ob.location).to_track_quat('-Z','Y').to_euler()
    ob.data.lens=values['lens']
    for key in ('shift_x','shift_y'):
        if key in values:setattr(ob.data,key,values[key])
    if 'exposure' in values:ob['fw_exposure']=values['exposure']
assert len(rooms)==60
tour.install(scene,rooms)
graph=json.loads((WORK/'qa/tour-path-all-adjacency.json').read_text(encoding='utf8'))
coverage=json.loads((WORK/'qa/tour-path-camera-coverage.json').read_text(encoding='utf8'))
route=json.loads((WORK/'data/tour-route.json').read_text(encoding='utf8'))
frames=sum(s['frames_checked'] for s in coverage['segment_checks'])
failures=sum(s.get('geometry_failure_frame_count',0) for s in coverage['segment_checks'])
graph_pass=graph['counts']=={'PASS':60,'FAIL':0,'NOT_RUN':0}
frame_pass=frames==7584 and failures==0 and coverage['status']=='PASS_CAMERA_VALUES_AND_COVERAGE' and coverage['covered_room_count']==60 and not route['uncovered_room_ids'] and not route['excluded_requested_segments']
record={'source_scene':str(SOURCE),'source_sha256':SHA,'status':'PASS_GEOMETRY_REOPEN_PENDING' if graph_pass and frame_pass else 'FAIL_RETAINED',
        'graph_counts':graph['counts'],'normal_walk_pass':graph['normal_walk_edge_pass_count'],
        'inspection_pass':graph['inspection_edge_pass_count'],'frames':frames,'frame_failures':failures,
        'camera_coverage_status':coverage['status'],'rooms_covered':coverage['covered_room_count'],
        'main_segments':len(route['main_segments']),'supplemental_segments':len(route['supplemental_segments']),
        'adapter_inputs':{n:sha(WORK/'scripts'/n) for n in ('tour.py','guest_circulation10_routes.py','master_navigation10.py')},
        'graph_pass':graph_pass,'frame_pass':frame_pass,'source_unchanged':sha(SOURCE)==SHA,
        'protected_files_unchanged':{p:sha(ROOT/p)==h for p,h in before.items()},
        'limits':['Legacy global body-column top1.71m; changed Master/Guest zones have separate strict1.95m checks',
                  'Explicit Master terrace two-foot step proof does not lower flat-ground tolerance',
                  'Not a GUI or visual-film acceptance','No final room photography acceptance'],
        'elapsed_seconds':time.monotonic()-started,'checked_scene_saved':False}
if graph_pass and frame_pass:
    txt=bpy.data.texts['FW_ROOMS.json'];txt.clear();txt.write(json.dumps(rooms,ensure_ascii=False,indent=2))
    for name,content in [('FW_GUEST_CIRCULATION10_ROUTES.json',guest_spec),('FW_MASTER_NAVIGATION10.json',master_spec),('FW_GUEST_CAMERA10_OVERRIDES.json',guest_cameras)]:
        text=bpy.data.texts.new(name);text.write(json.dumps(content,indent=2))
    scene['navigation_revision10']='Full graph and integer-frame geometric checks; GUI/visual acceptance pending'
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
    record.update(checked_scene_saved=True,checked_scene=str(OUT),checked_scene_sha256=sha(OUT),independent_reopen='PENDING')
REPORT.write_text(json.dumps(record,indent=2),encoding='utf8');print(json.dumps(record),flush=True)
assert record['source_unchanged'] and all(record['protected_files_unchanged'].values())
if not graph_pass or not frame_pass:raise RuntimeError('Combined navigation did not pass; retain full evidence')
