"""Fresh CPU4 readback of saved navigation11a; no key patch/save/render."""
import bpy,sys,json,hashlib,ast,array,collections,math,copy,time
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];Q=R/'qa';sys.path.insert(0,str(R/'scripts'))
import master_navigation11 as nav
import master_navigation10 as m10
import guest_circulation10_routes as guest
report=json.loads((Q/'master-navigation11-build-check.json').read_text(encoding='utf-8'))
SRC=Path(report['source']);OUT=Path(report['candidate']);WORK=Q/'master-navigation11-reopen-workspace'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert report['pass'] and sha(OUT)==report['candidate_sha256'] and sha(SRC)==report['source_sha256']
tree=ast.parse((Q/'master-ceiling11-build-check.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'prop_state','fingerprint','materials','settings'}],type_ignores=[]),'<fingerprint utilities>','exec'))
tree=ast.parse((Q/'master-navigation11-build-check.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'key_records','key_diff','film'}],type_ignores=[]),'<saved-key audit utilities>','exec'))
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene
fp0=fingerprint();keys0=key_records();mat0=materials();set0=settings()
boundary0={}
for f in (5088,5089,5184,5185):
    s.frame_set(f);boundary0[str(f)]=[list(r) for r in s.objects['CAM_TOUR_SUPPLEMENTAL'].matrix_world]
bpy.ops.wm.open_mainfile(filepath=str(OUT));s=bpy.context.scene;frame=s.frame_current
fp1=fingerprint();keys1=key_records();mat1=materials();set1=settings()
boundary1={}
for f in (5088,5089,5184,5185):
    s.frame_set(f);boundary1[str(f)]=[list(r) for r in s.objects['CAM_TOUR_SUPPLEMENTAL'].matrix_world]
p=nav.StrictProbe11(s);rows=film(p,'CAM_TOUR_SUPPLEMENTAL',5089,5184)
# Independently read actual finish at all96 saved positions, then cast the
# body columns DOWN from1.95m to8mm above that finish (opposite QA direction).
finish_rows=[]
for r in rows:
    eye=Vector(r['eye']);hit=nav.surface(s,'MAIN_L2_TERRACE_S_finish',eye[:2]);floor=hit['point'][2]
    body_hits=[]
    for k in range(17):
        dx=0 if k==16 else .18*math.cos(k*math.tau/16)
        dy=0 if k==16 else .18*math.sin(k*math.tau/16)
        obstacle=p.ray((eye.x+dx,eye.y+dy,floor+1.95),(0,0,-1),1.942)
        if obstacle:body_hits.append(obstacle)
    finish_rows.append({'frame':r['frame'],'actual_finish':hit,'eye_minus1_6_error_m':eye.z-1.6-floor,'reverse_full_body_column_hits':body_hits})
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string());byid={r['id']:r for r in rooms}
embedded=json.loads(bpy.data.texts['FW_MASTER_NAVIGATION11.json'].as_string())
finish=embedded['finish_measurements']['master']['point'][2]
out=nav.fixed_torso_step(p,finish,embedded['sill_rise_m'],True)
inc=nav.fixed_torso_step(p,finish,embedded['sill_rise_m'],False)
gaits={'outward':out,'inward':inc}
for d in ('data','qa'):(WORK/d).mkdir(parents=True,exist_ok=True)
(WORK/'data/guest_circulation10.json').write_bytes((R/'data/guest_circulation10.json').read_bytes())
tour,roomcopy,_=guest.prepare(WORK,s,rooms,read_only=True);m10.apply(tour,s,roomcopy,WORK)
spec=nav.apply(tour,s,roomcopy,WORK,reference_route=report['reference_route'])
updated={r['id']:r for r in roomcopy}
source_metadata={rid:{k:updated[rid][k] for k in ('source_level_datum_z','navigation_original_datum_z','navigation_finish_z','z')} for rid in (nav.MASTER,nav.TERRACE)}
fullpaths=[]
for a,b in ((nav.MASTER,nav.TERRACE),(nav.TERRACE,nav.MASTER)):
    fullpaths.append(tour.connection(updated[a],updated[b],None,{}))
s.frame_set(frame)
diff=key_diff(keys0,keys1)
outside_boundary=all(boundary0[str(f)]==boundary1[str(f)] for f in (5088,5185))
selected_boundary=all(all(abs(boundary1[str(f)][i][j]-boundary0[str(f)][i][j]-(spec['terrace_eye_delta_z_m'] if (i,j)==(2,3) else 0))<1e-6 for i in range(4) for j in range(4)) for f in (5089,5184))
result={'source':str(SRC),'candidate':str(OUT),'candidate_sha256':sha(OUT),'helper_sha256':sha(R/'scripts/master_navigation11.py'),'actual_saved_frame_rows':rows,'independent_actual_finish_and_reverse_body_columns':finish_rows,'frame_count':len(rows),'frame_failures':sum(bool(r['failure']) for r in rows),'actual_finish_max_error_m':max(abs(r['eye_minus1_6_error_m']) for r in finish_rows),'reverse_body_column_hits':sum(len(r['reverse_full_body_column_hits']) for r in finish_rows),'all_object_fingerprints_unchanged':fp0==fp1,'object_count':len(fp1),'materials_unchanged':mat0==mat1,'settings_unchanged':set0==set1,'key_changes_equal_build':diff==report['key_changes'],'key_changes':diff,'outside_boundary_matrices_unchanged':outside_boundary,'selected_boundary_only_z_changed':selected_boundary,'gait_summary':{d:{k:r[k] for k in ('status','support_samples','maximum_support_error_m','minimum_swing_sole_clearance_over_sill_m','torso_vertical_displacement_m','head_height_m','body_radius_m')} for d,r in gaits.items()},'reinstalled_paths':fullpaths,'source_metadata_after_reinstall':source_metadata,'actual_saved_keys_unchanged_by_reinstall':key_records()==keys1,'source_height_status':spec['source_height_status'],'GEO07':'NOT_RUN','rendered':False,'saved':False,'candidate_unchanged':sha(OUT)==report['candidate_sha256']}
result['pass']=all(result[k] for k in ('all_object_fingerprints_unchanged','materials_unchanged','settings_unchanged','key_changes_equal_build','outside_boundary_matrices_unchanged','selected_boundary_only_z_changed','actual_saved_keys_unchanged_by_reinstall','candidate_unchanged')) and result['frame_failures']==0 and result['actual_finish_max_error_m']<=.004 and result['reverse_body_column_hits']==0 and all(r['status']=='PASS_EXPLICIT_TWO_FOOT_STEP_OVER' for r in gaits.values()) and all(r['status']=='PASS_MESH_AND_GROUND' for r in fullpaths) and all(abs(r['source_level_datum_z']-2.8448)<1e-6 and abs(r['navigation_finish_z']-2.8668)<1e-6 for r in source_metadata.values())
(Q/'master-navigation11-reopen.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
for d,r in gaits.items():(Q/('master-navigation11-reopen-step-'+d+'.json')).write_text(json.dumps(r,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('actual_saved_frame_rows','independent_actual_finish_and_reverse_body_columns','reinstalled_paths')},indent=2),flush=True)
assert result['pass']
