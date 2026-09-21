"""Bounded saved-key pre/post check on physical ceiling11b; no render."""
import bpy,sys,json,hashlib,shutil,time,copy,ast,array,collections,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];Q=R/'qa';sys.path.insert(0,str(R/'scripts'))
import guest_circulation10_routes as guest
import master_navigation10 as m10
import master_navigation11 as m11
SRC=R/'scene/Fallingwater_master_ceiling_candidate11b.blend'
SHA='c0d71ca14782c8af5a5b6593336cd4f652c4808da7f824405538a159280ddcde'
WORK=Q/'master-navigation11-workspace';OUT=WORK/'scene/Fallingwater_navigation11a.blend'
REF=Q/'integration10-navigation-workspace/data/tour-route.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(SRC)==SHA and not OUT.exists()
for d in ('data','qa','scene'):(WORK/d).mkdir(parents=True,exist_ok=True)
protected=['scripts/master_navigation10.py','scripts/guest_circulation10_routes.py','scripts/tour.py','scripts/main_house.py','data/tour-route.json','data/main_house.json','data/guest_house.json','data/guest_circulation10.json','config.json','adjacency.csv']
protected0={n:sha(R/n) for n in protected}
for n in ('data/main_house.json','data/guest_house.json','data/guest_circulation10.json','config.json','adjacency.csv'):shutil.copy2(R/n,WORK/n)
started=time.monotonic();bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene
# Use audit utility definitions only, never execute the prior geometry builder.
tree=ast.parse((Q/'master-ceiling11-build-check.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'prop_state','fingerprint','materials','settings'}],type_ignores=[]),'<read-only fingerprint utilities>','exec'))

def key_records():
    out={}
    for o in s.objects:
        if o.type!='CAMERA' or not o.animation_data or not o.animation_data.action:continue
        for li,l in enumerate(o.animation_data.action.layers):
            for si,st in enumerate(l.strips):
                for bi,b in enumerate(st.channelbags):
                    for c in b.fcurves:
                        for p in c.keyframe_points:
                            key=f'{o.name}|{li}/{si}/{bi}|{c.data_path}|{c.array_index}|{p.co.x}'
                            out[key]={'co':list(p.co),'interpolation':p.interpolation,'handle_left':list(p.handle_left),'handle_right':list(p.handle_right),'handle_left_type':p.handle_left_type,'handle_right_type':p.handle_right_type}
    return out

def film(probe,camera,a,b):
    rows=[];last=None
    for f in range(a,b+1):
        s.frame_set(f);eye=s.objects[camera].matrix_world.translation.copy()
        failure=probe.point(eye,True)
        if failure is None and last is not None:failure=probe.segment(last,eye,True)
        rows.append({'camera':camera,'frame':f,'eye':list(eye),'failure':failure});last=eye
    return rows

def key_diff(a,b):return [{'key':k,'before':a.get(k),'after':b.get(k)} for k in sorted(set(a)|set(b)) if a.get(k)!=b.get(k)]

def route_diff(a,b):
    aa=copy.deepcopy(a);bb=copy.deepcopy(b)
    aa['supplemental_segments']=[v for v in aa['supplemental_segments'] if v['id']!=m11.TERRACE]
    bb['supplemental_segments']=[v for v in bb['supplemental_segments'] if v['id']!=m11.TERRACE]
    return aa==bb

initial_frame=s.frame_current;fp0=fingerprint();mat0=materials();set0=settings();keys0=key_records()
texts0={t.name:t.as_string() for t in bpy.data.texts};embedded0=json.loads(texts0['FW_ROOMS.json'])
route0=json.loads(REF.read_text(encoding='utf-8'));route=copy.deepcopy(route0)
tour,rooms,guest_spec=guest.prepare(WORK,s,embedded0,read_only=True)
m10.apply(tour,s,rooms,WORK)
byid={r['id']:r for r in rooms}
other_before=tour.connection(byid[m10.MASTER],byid[m10.BATH],None,{})
old_edge=tour.connection(byid[m10.MASTER],byid[m11.TERRACE],None,{})
rooms_before=copy.deepcopy(rooms)
delegated={n:getattr(tour,n) for n in ('Probe','stair_connection','storage_inspection','connector_shot','stair_space_anchors')}
spec=m11.apply(tour,s,rooms,WORK,reference_route=route0);p=tour.master_navigation11_probe
print('ADAPTER11_CHECKED',spec['outward_step_status'],spec['inward_step_status'],flush=True)
films0=film(p,'CAM_TOUR_SUPPLEMENTAL',5089,5184)
neighbors={}
for frame in (5088,5185):
    s.frame_set(frame);neighbors[str(frame)]=list(s.objects['CAM_TOUR_SUPPLEMENTAL'].matrix_world.translation)
# Wrong route must reject before touching either camera keys or route.
bad=copy.deepcopy(route0);next(v for v in bad['supplemental_segments'] if v['id']==m11.TERRACE)['points'][0][0]+=.1
bad_before=copy.deepcopy(bad)
try:m11.patch_saved_terrace_keys(s,bad,spec);raise AssertionError('Wrong-route guard did not reject')
except ValueError as e:negative={'message':str(e),'keys_unchanged':key_records()==keys0,'route_unchanged':bad==bad_before}
assert negative['keys_unchanged'] and negative['route_unchanged']
patch=m11.patch_saved_terrace_keys(s,route,spec)
films1=film(p,'CAM_TOUR_SUPPLEMENTAL',5089,5184)
master_film=film(p,'CAM_TOUR',1441,1608)
neighbor_after={}
for frame in (5088,5185):
    s.frame_set(frame);neighbor_after[str(frame)]=list(s.objects['CAM_TOUR_SUPPLEMENTAL'].matrix_world.translation)
edges=[]
for a,b in ((m10.MASTER,m11.TERRACE),(m11.TERRACE,m10.MASTER)):
    direct=tour.connection(byid[a],byid[b],None,{})
    hint=tour.hinted_connection(byid[a],byid[b],None,{}, {})
    edges.append({'direct':direct,'hinted_identical':direct==hint})
other_after=tour.connection(byid[m10.MASTER],byid[m10.BATH],None,{})
room_shot,failure=tour.room_shot(byid[m11.TERRACE],None,{})
assert failure is None and room_shot['points']==spec['corrected_terrace_segment']['points']
m11.embed_metadata(s,rooms,spec)
embedded1=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
room_diffs=[{'id':a['id'],'before':a,'after':b} for a,b in zip(embedded0,embedded1) if a!=b]
s.frame_set(initial_frame);fp1=fingerprint();mat1=materials();set1=settings();keys1=key_records();diff=key_diff(keys0,keys1)
outside_room_equal=all(a==b for a,b in zip(rooms_before,rooms) if a['id'] not in (m11.MASTER,m11.TERRACE))
text_scope=all(bpy.data.texts[n].as_string()==v for n,v in texts0.items() if n!='FW_ROOMS.json') and set(t.name for t in bpy.data.texts)==set(texts0)|{'FW_MASTER_NAVIGATION11.json'}
only_two_z=(len(diff)==2 and all(v['key'].startswith('CAM_TOUR_SUPPLEMENTAL|') and '|location|2|' in v['key'] and v['after']['co'][0] in (5089,5184) for v in diff))
scope={'all_object_fingerprints_unchanged':fp0==fp1,'object_count':len(fp0),'materials_unchanged':mat0==mat1,'material_count':len(mat0),'settings_unchanged':set0==set1,'only_two_terrace_z_keys_changed':only_two_z,'key_count':len(keys0),'neighbor_saved_frames_unchanged':neighbors==neighbor_after,'all_other_route_data_unchanged':route_diff(route0,route),'other_room_records_unchanged':outside_room_equal,'embedded_room_change_ids':[v['id'] for v in room_diffs],'embedded_text_scope_pass':text_scope,'unrelated_dispatch_identity_unchanged':all(getattr(tour,n) is f for n,f in delegated.items()),'actual_master_bath_result_unchanged':other_before==other_after}
passed=all(v for k,v in scope.items() if isinstance(v,bool)) and set(scope['embedded_room_change_ids'])=={m11.MASTER,m11.TERRACE} and all(v['direct']['status']=='PASS_MESH_AND_GROUND' and v['hinted_identical'] for v in edges) and not any(v['failure'] for v in films1+master_film) and all(v['failure'] for v in films0)
report={'source':str(SRC),'source_sha256':SHA,'helper_sha256':sha(R/'scripts/master_navigation11.py'),'reference_route':str(REF),'reference_route_sha256':sha(REF),'candidate':str(OUT),'pass':passed,'scope':scope,'key_changes':diff,'wrong_route_guard':negative,'old_edge':old_edge,'new_edges':edges,'before_actual_terrace_frames':films0,'after_actual_terrace_frames':films1,'unchanged_master_frames':master_film,'before_terrace_failures':sum(bool(v['failure']) for v in films0),'after_terrace_failures':sum(bool(v['failure']) for v in films1),'master_frame_failures':sum(bool(v['failure']) for v in master_film),'room_metadata_changes':room_diffs,'saved_key_patch':patch,'source_height_status':spec['source_height_status'],'GEO07':'NOT_RUN','rendered':False,'elapsed_seconds':time.monotonic()-started,'protected_file_hashes':protected0}
if passed:
    (WORK/'data/tour-route.json').write_text(json.dumps(route,indent=2),encoding='utf-8')
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True);report['candidate_sha256']=sha(OUT)
report['protected_files_unchanged']={n:sha(R/n)==h for n,h in protected0.items()};report['source_unchanged']=sha(SRC)==SHA
(Q/'master-navigation11-build-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('old_edge','new_edges','before_actual_terrace_frames','after_actual_terrace_frames','unchanged_master_frames','room_metadata_changes','protected_file_hashes')},indent=2),flush=True)
assert passed and report['source_unchanged'] and all(report['protected_files_unchanged'].values())
