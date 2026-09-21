"""Frozen read-only source cases; never apply a construction helper or save."""
import bpy,sys,json,hashlib,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'scripts'),str(R/'qa')]
import dimension_supplement12 as entry
import shrub08_auditlib as audit
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
cases=[('terrace11a',R/'scene/Fallingwater_main_terrace_candidate11a.blend','e856456005d3a4493e70122644d52192dd49c2d2ffc046248b1247484beb4750',{'PASS':4,'FAIL':0,'NOT_RUN':0}),
       ('bridge10_endfix',R/'scene/Fallingwater_bridge10_endfix.blend','2a7630b8024c37bd768e563236807f8049469172c7e44b03379a450f91637063',{'PASS':1,'FAIL':0,'NOT_RUN':3})]
protected=[R/'scripts/dimension_audit.py',R/'dimensions.csv'];original_files={str(p):sha(p) for p in protected}
reports=[];t=time.monotonic()
for name,path,expected,counts in cases:
    assert sha(path)==expected
    bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;bpy.context.view_layer.update()
    print('DIMSUP12_SOURCE',name,'SNAPSHOT',flush=True);before=audit.snapshot()
    actual=entry.measure(s);repeat=entry.measure(s)
    print('DIMSUP12_MEASURED',name,actual['counts'],flush=True);after=audit.snapshot()
    record={'case':name,'source_file':str(path),'source_sha256':expected,'helper_sha256':sha(R/'scripts/dimension_supplement12.py'),
            'result':actual,'repeat_identical':actual==repeat,'full_snapshot_unchanged':before==after,
            'source_hash_unchanged':sha(path)==expected,'saved':False,'rendered':False}
    (R/'qa'/f'dimension-supplement12-{name}.json').write_text(json.dumps(record,indent=2),encoding='utf8')
    assert actual['counts']==counts,(name,actual['counts'])
    assert actual==repeat and before==after and sha(path)==expected
    reports.append({k:v for k,v in record.items() if k!='result'}|{'counts':actual['counts'],
                  'measures':[{'id':r['id'],'status':r['status'],'actual_m':r.get('measured_m'),'max_error_m':r.get('maximum_absolute_error_m')} for r in actual['anchors']]})
assert original_files=={str(p):sha(p) for p in protected}
out={'status':'PASS_READ_ONLY_FROZEN_CASES','cases':reports,'protected_central_files_unchanged':original_files,
     'seconds':time.monotonic()-t,'independent_printed_anchors':4,'repeated_ray_stations_do_not_increase_anchor_count':True,
     'source_precision_not_survey_accuracy':True,'helper_runtime_qa_file_dependencies':False,'production_changes':False,'rendered':False}
(R/'qa/dimension-supplement12-check.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('DIMSUP12_RESULT',json.dumps(out),flush=True)
