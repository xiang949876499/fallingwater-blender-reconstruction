"""Independently reopen12, check all connections and existing saved film keys."""
from pathlib import Path
import bpy,json,hashlib,shutil,sys,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
SOURCE=ROOT/'scene/Fallingwater_integration_candidate12a.blend'
SHA='50e0a8fc0bab10fdec0e0b9d26c4ef4a4c71fa56aea6401e75197787c8c0e75a'
WORK=ROOT/'qa/integration12-full-check-workspace'
assert not WORK.exists() and hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
shutil.copytree(ROOT/'qa/integration11-navigation-workspace',WORK)
started=time.monotonic();bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene
scene.render.threads_mode='FIXED';scene.render.threads=4
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
import guest_circulation10_routes as guest,master_navigation10 as master,master_navigation11 as nav
tour,rooms,gs=guest.prepare(WORK,scene,rooms,read_only=True)
master.apply(tour,scene,rooms,WORK)
nav.apply(tour,scene,rooms,WORK,reference_route=ROOT/'qa/integration10-navigation-workspace/data/tour-route.json')
route=json.loads((WORK/'data/tour-route.json').read_text(encoding='utf8'))
def keys():
    rows=[]
    for name in ('CAM_TOUR','CAM_TOUR_SUPPLEMENTAL'):
        o=scene.objects[name];curves=[]
        for layer in o.animation_data.action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for c in bag.fcurves:
                        curves.append([c.data_path,c.array_index,[[list(p.co),list(p.handle_left),list(p.handle_right),p.interpolation] for p in c.keyframe_points]])
        rows.append([name,curves])
    return hashlib.sha256(json.dumps(rows).encode()).hexdigest()
before=keys()
xs=[p[0] for r in rooms for p in r['polygon']]+[-28,35]
ys=[p[1] for r in rooms for p in r['polygon']]+[-40,-25]
bounds=[(min(xs)-3,max(xs)+3),(min(ys)-3,max(ys)+3),(min(r['z'] for r in rooms)-2,max(44,max(r['z']+r['height'] for r in rooms))+2)]
probe=tour.Probe(scene,bounds)
candidates={r['id']:tour.room_candidates(r,probe,True) for r in rooms}
graph=tour.all_adjacency_checks(scene,rooms,probe,candidates)
print('GRAPH12 '+json.dumps(graph['counts']),flush=True)
coverage=tour.camera_evidence(scene,rooms,route,probe)
frames=sum(s['frames_checked'] for s in coverage['segment_checks'])
failures=sum(s.get('geometry_failure_frame_count',0) for s in coverage['segment_checks'])
after=keys()
passed=(graph['counts']=={'PASS':60,'FAIL':0,'NOT_RUN':0} and frames==7584 and failures==0 and
        coverage['status']=='PASS_CAMERA_VALUES_AND_COVERAGE' and before==after)
report={'status':'PASS_FULL_GRAPH_AND_SAVED_FRAMES' if passed else 'FAIL_RETAINED',
        'scene':str(SOURCE),'scene_sha256':SHA,'source_unchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA,
        'graph_counts':graph['counts'],'frames':frames,'geometry_failure_frames':failures,
        'covered_rooms':coverage['covered_room_count'],'key_sha_before':before,'key_sha_after':after,
        'camera_keys_rebuilt':False,'saved':False,'seconds':time.monotonic()-started,
        'limits':['Global legacy1.71m body columns and19cm tread-ground tolerance; strict changed regions separately tested1.95m/.18m/4mm',
                  'Sampled model geometry only; no GUI/FPS or final photographic/film acceptance']}
(ROOT/'qa/integration12-full-check.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report),flush=True)
assert passed and report['source_unchanged']
