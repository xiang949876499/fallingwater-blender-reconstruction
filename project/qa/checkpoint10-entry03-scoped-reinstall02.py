"""Diagnose search ordering; reinstall one frozen move on saved rebuilt02."""
import bpy,sys,json,hashlib,copy,shutil,ast,array,collections,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];Q=R/'qa';sys.path.insert(0,str(R/'scripts'))
import guest_circulation10_routes as guest
import master_navigation10 as m10
import build_iteration10 as entry
WORK=Q/'checkpoint10-entry03-scoped-workspace';OUT=WORK/'scene/Fallingwater_iteration10_rebuilt02_frozen_shot.blend'
assert not OUT.exists()
for d in ('data','qa','scene'):(WORK/d).mkdir(parents=True,exist_ok=True)
for n in ('data/main_house.json','data/guest_house.json','data/guest_circulation10.json','config.json'):shutil.copy2(R/n,WORK/n)
frozen=json.loads((R/'data/iteration10-room-shots-frozen.json').read_text(encoding='utf-8'));RID='MAIN_L1_SERVICE_STAIR';segment=frozen['room_shots'][RID]
inputs=[R/'scene/Fallingwater_iteration10.blend',R/'scene/Fallingwater_iteration10_rebuilt02.blend']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
expected=['1e7b17d9c2396513f005724e50788bf834097eedb401b91a7f1030825e2c4ed9','c2a7ebb018c2a1d3773298b736b6519cdd5b8a996e7f1966321ded8798959629']
assert [sha(p) for p in inputs]==expected
tree=ast.parse((Q/'master-ceiling11-build-check.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'prop_state','fingerprint','materials','settings'}],type_ignores=[]),'<read-only fingerprint utilities>','exec'))
tree=ast.parse((Q/'master-navigation11-build-check.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'key_records','key_diff'}],type_ignores=[]),'<read-only animation audit utilities>','exec'))

def reverse_bvh(probe):
    vertices=[];faces=[];owners=[];order=[];dep=bpy.context.evaluated_depsgraph_get()
    for ob in reversed(list(probe.scene.objects)):
        if ob.type not in ('MESH','CURVE','SURFACE','FONT') or ob.hide_render or ob.name.startswith(('REF_','QA_')):continue
        cc=[ob.matrix_world@Vector(v) for v in ob.bound_box]
        if any(max(v[i] for v in cc)<probe.bounds[i][0] or min(v[i] for v in cc)>probe.bounds[i][1] for i in range(3)):continue
        eo=ob.evaluated_get(dep);me=eo.to_mesh();offset=len(vertices)
        vertices.extend(eo.matrix_world@v.co for v in me.vertices)
        faces.extend(tuple(offset+i for i in f.vertices) for f in me.polygons)
        owners.extend([ob.name]*len(me.polygons));order.append(ob.name);eo.to_mesh_clear()
    probe.bvh=BVHTree.FromPolygons(vertices,faces,epsilon=.001);probe.face_owners=owners;probe.cache.clear()
    return hashlib.sha256(json.dumps(order).encode()).hexdigest()

diagnostics=[];source_keys=None
for path in inputs:
    bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
    if source_keys is None:source_keys=key_records()
    original_rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
    tour,rooms,_=guest.prepare(WORK,s,original_rooms,read_only=True)
    room=next(r for r in rooms if r['id']==RID)
    xs=[v[0] for v in room['polygon']];ys=[v[1] for v in room['polygon']]
    bounds=[(min(xs)-2,max(xs)+2),(min(ys)-2,max(ys)+2),(room['z']-1,room['z']+room['height']+2)]
    p=tour.Probe(s,bounds);trials=[]
    for order in ('saved_scene_order','reversed_scene_object_order'):
        if order.startswith('reversed'):reverse_bvh(p)
        p.cache.clear();c=tour.room_candidates(room,p,True)
        selected,issue=tour.room_shot(room,p,{RID:c})
        p.cache.clear();frozen_failure=p.segment(segment['points'][0],segment['points'][1],True,sample_step=.01)
        trials.append({'order':order,'candidates':[list(v) for v in c],'selected':selected,'selection_issue':issue,'frozen_polyline_failure':frozen_failure})
    diagnostics.append({'scene':str(path),'sha256':sha(path),'bounds':bounds,'probe_mesh_counts':p.mesh_counts,'trials':trials})
    print('SELECTION_DIAGNOSTIC',path.name,[(t['order'],t['selected']['points'] if t['selected'] else t['selection_issue'],t['frozen_polyline_failure']) for t in trials],flush=True)
# New scoped evidence uses the original dispatcher/probe/keying/camera_evidence
# functions. No full tour/install or geometry rebuild is needed for this repair.
initial=s.frame_current;fp0=fingerprint();mat0=materials();set0=settings();keys02=key_records();texts0={t.name:t.as_string() for t in bpy.data.texts}
original_shot=tour.room_shot
m10.apply(tour,s,rooms,WORK)
spec=entry.install_frozen_room_shots(tour)
p=tour.Probe(s,bounds)
c=tour.room_candidates(room,p,True);shot,issue=tour.room_shot(room,p,{RID:c})
print('FROZEN_DISPATCH',issue,shot==segment,flush=True)
assert issue is None and shot==segment
camera=s.objects[frozen['supplemental_camera']]
tour.set_keys(camera,shot)
route={'scene_file':str(inputs[1]),'main_camera':'CAM_TOUR','main_segments':[],'supplemental_camera':camera.name,'supplemental_segments':[copy.deepcopy(shot)]}
coverage=tour.camera_evidence(s,[room],route,p)
s.frame_set(initial);keys_after=key_records();fp1=fingerprint();mat1=materials();set1=settings()
key_changes=key_diff(keys02,keys_after);remaining=key_diff(source_keys,keys_after)
report={'source':str(inputs[0]),'source_sha256':expected[0],'rebuilt02':str(inputs[1]),'rebuilt02_sha256':expected[1],'output':str(OUT),'entry_sha256':sha(R/'scripts/build_iteration10.py'),'frozen_input':str(R/'data/iteration10-room-shots-frozen.json'),'frozen_input_sha256':sha(R/'data/iteration10-room-shots-frozen.json'),
        'diagnostic':diagnostics,'frozen_dispatch_actual_segment_equal':shot==segment,'coverage':coverage,'actual_frames_checked':sum(v['frames_checked'] for v in coverage['segment_checks']),
        'only_affected_camera_key_changes':key_changes,'remaining_differences_against_all_source_keys':remaining,'all_source_camera_keys_exactly_equal':not remaining,
        'all_static_object_fingerprints_unchanged_from02':fp0==fp1,'object_count':len(fp0),'materials_unchanged':mat0==mat1,'settings_unchanged':set0==set1,'all_embedded_texts_unchanged':texts0=={t.name:t.as_string() for t in bpy.data.texts},
        'production_tour_unchanged':sha(R/'scripts/tour.py')==json.loads((Q/'master-navigation11-build-check.json').read_text())['protected_file_hashes']['scripts/tour.py'],
        'source_files_unchanged':[sha(p)==e for p,e in zip(inputs,expected)],'rendered':False,'full_navigation_rerun':False,'geometry_rebuilt':False,
        'camera_evidence_scope_note':'Direct unchanged tour.camera_evidence, the same function called by tour.install, scoped to one96-frame service-stair segment. Its legacy main_frames=2880 field is a constant, not 2880 checks in this scoped call.'}
report['pass']=coverage['status']=='PASS_CAMERA_VALUES_AND_COVERAGE' and report['actual_frames_checked']==96 and not remaining and fp0==fp1 and mat0==mat1 and set0==set1 and report['all_embedded_texts_unchanged'] and all(report['source_files_unchanged'])
if report['pass']:
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True);report['output_sha256']=sha(OUT)
(Q/'checkpoint10-entry03-scoped-reinstall02.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('diagnostic','coverage','only_affected_camera_key_changes','remaining_differences_against_all_source_keys')},indent=2),flush=True)
assert report['pass']
