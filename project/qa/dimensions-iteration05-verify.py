"""Run API against the frozen scene and verify audit/CSV failure boundaries."""
import bpy,sys,csv,json,hashlib
from pathlib import Path
P=Path('D:/zx/test/project');sys.path.insert(0,str(P/'scripts'))
from dimension_audit import audit_dimensions,MeshReader
S=P/'scene/Fallingwater_iteration05.blend'
SHA='6bcfee7841c22e8e2b636352cfca79ae94968afb4235fc20cdc57e250ae046ff'
bpy.ops.wm.open_mainfile(filepath=str(S))
report=audit_dimensions(P,scene_path=S,expected_sha256=SHA)
checks=[]
try:
 audit_dimensions(P,scene_path=S,expected_sha256='0'*64,write_csv=False)
 checks.append({'test':'wrong_scene_hash_rejected','pass':False})
except ValueError:
 checks.append({'test':'wrong_scene_hash_rejected','pass':True})
try:
 MeshReader().names(exact=['DIMENSION_NEGATIVE_MISSING_MESH'])
 checks.append({'test':'missing_mesh_selector_rejected','pass':False})
except ValueError:
 checks.append({'test':'missing_mesh_selector_rejected','pass':True})
with (P/'dimensions.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
with (P/'qa/dimensions-iteration05-previous.csv').open(encoding='utf-8-sig',newline='') as f:old={r['component_id']:r for r in csv.DictReader(f)}
current={r['component_id']:r for r in rows};notrun=[r for r in rows if r['numeric_result']=='NOT_RUN']
checks.extend([
 {'test':'21_not_run_actual_and_difference_blank','pass':len(notrun)==21 and all(r['model_m']==r['difference_m']=='' for r in notrun)},
 {'test':'22_numeric_pass_12_precision_qualified','pass':report['numeric_counts']=={'NOT_RUN':21,'PASS':22} and report['standard_counts']=={'NOT_RUN':21,'PASS':12,'SOURCE_PRECISION_LIMIT':10}},
 {'test':'old_bad_model_value_not_reused','pass':abs(float(old['MAIN_CHAIN_03']['model_m'])-float(current['MAIN_CHAIN_03']['model_m']))>.003,'old_m':old['MAIN_CHAIN_03']['model_m'],'actual_mesh_m':current['MAIN_CHAIN_03']['model_m']},
 {'test':'all_actual_rows_have_mesh_endpoint_evidence','pass':all(len(r['endpoints'])==2 and all(e.get('evaluated_vertex_ids') or e.get('evaluated_face_vertex_ids') for e in r['endpoints']) for r in report['measurements'] if r['actual_mesh_m'] is not None)},
 {'test':'frozen_scene_not_changed','pass':hashlib.sha256(S.read_bytes()).hexdigest()==SHA},
 {'test':'overall_incomplete_despite_numeric_count','pass':report['geo02_overall']=='INCOMPLETE' and all(report['category_coverage'][c]['coverage']=='MISSING' for c in ['cantilever','openings','connections'])}
])
out={'scene_sha256':SHA,'tests':checks,'status':'PASS' if all(t['pass'] for t in checks) else 'FAIL'}
(P/'qa/dimensions-iteration05-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
