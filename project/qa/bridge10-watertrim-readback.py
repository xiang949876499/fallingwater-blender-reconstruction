"""Fresh reopen of retained FAILED candidate; correct evaluated-triangle audit."""
import bpy,sys,json,hashlib,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];Q=ROOT/'qa';sys.path.insert(0,str(Q))
import shrub08_auditlib as shared
import bridge10_watertrim_auditlib as test
original=json.loads((Q/'bridge10-watertrim-check.json').read_text())
SOURCE=ROOT/'scene/Fallingwater_bridge10_endfix.blend';TARGET=Path(original['candidate'])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE)==original['source_sha256'];assert sha(TARGET)==original['candidate_sha256']
FRAMES=(1,24,48,120,240,241);name='WATER_BearRun_Continuous_Upstream_Downstream'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));baseline={}
cores={s:test.exact_core(bpy.data.objects['SITE_Bridge10_Stone_Return_'+s],n) for s,n in [('SW',58),('SE',54)]}
for f in FRAMES:
    bpy.context.scene.frame_set(f);bpy.context.view_layer.update();d=test.evaluate(bpy.data.objects[name])
    baseline[f]={'quality':d['quality'],'far':d['far_vertices'],'samples':test.shore_samples(d,cores)}
    del d
print('READBACK source animated samples complete',flush=True)
bpy.ops.wm.open_mainfile(filepath=str(TARGET));scene=bpy.context.scene;stored_frame=scene.frame_current
expected=json.loads((Q/'bridge10-watertrim-fingerprint.json').read_text());snap=shared.snapshot()
assert {n:shared.digest(v) for n,v in snap['objects'].items()}==expected['objects']
assert shared.digest(snap['global'])==expected['global'];assert snap['meshes']==expected['meshes']
report={'status':'FRESH_REOPEN_PASS_CANDIDATE_PHYSICAL_FAIL','source_sha256':sha(SOURCE),'candidate_sha256':sha(TARGET),
        'stored_frame':stored_frame,'full_snapshot_exact':True,'rendered':False,'saved_again':False,
        'audit_corrections':['Use actual evaluated loop triangles for ray geometry, not independent BVH polygon tessellation','Exclude vertices referenced by no actual triangle from exterior-surface preservation checks','Classify narrow terminal caps of perpendicular face stones separately from removed broad zero-projection end panels'],
        'frames':[],'deployment':'DO_NOT_INTEGRATE_WATERTRIM'}
for f in FRAMES:
    st=time.monotonic();scene.frame_set(f);bpy.context.view_layer.update();d=test.evaluate(scene.objects[name]);old=baseline[f]
    missing=old['far']-d['far_vertices'];new=d['far_vertices']-old['far']
    shore=test.shore_compare(old['samples'],d)
    row={'frame':f,'baseline_quality':old['quality'],'candidate_quality':d['quality'],
         'missing_used_far_vertex_positions':len(missing),'new_used_far_vertex_positions':len(new),
         'shore':shore,'evaluation_and_audit_s':time.monotonic()-st}
    assert d['quality']['physical_triangles_sha256']==next(r['candidate_quality']['physical_triangles_sha256'] for r in original['frames'] if r['frame']==f)
    report['frames'].append(row);del d
    print('READBACK_FRAME',f,json.dumps({'open_edges':row['candidate_quality']['open_edges'],'zero_triangles':row['candidate_quality']['zero_area_triangles'],'missing_used_far':len(missing),'shore_failures':len(shore['failures'])}),flush=True)
scene.frame_set(48);bpy.context.view_layer.update()
assert {n:shared.physical_hash(scene.objects[n]) for n in original['protected_physics']}==original['protected_physics']
report['protected_core_and_other_water_hash_count']=len(original['protected_physics'])
report['end_faces']=test.endpoint_faces([(scene.objects['SITE_Bridge10_Stone_Return_'+s],x,n) for s,x,n in [('SW',25.43044,58),('SE',29.46904,54),('NW',25.38,54),('NE',29.46904,54)]])
report['loop_1_equals_241']=report['frames'][0]['candidate_quality']['physical_triangles_sha256']==report['frames'][-1]['candidate_quality']['physical_triangles_sha256']
report['animation_varies']=len({r['candidate_quality']['physical_triangles_sha256'] for r in report['frames'][:-1]})>1
report['physical_failures_confirmed']=any(r['candidate_quality']['nonmanifold_edges'] or r['candidate_quality']['zero_area_triangles'] or r['shore']['failures'] for r in report['frames'])
assert report['physical_failures_confirmed']
(Q/'bridge10-watertrim-readback.json').write_text(json.dumps(report,indent=2),encoding='utf8')
assert sha(TARGET)==original['candidate_sha256']
print('READBACK_COMPLETE',report['status'],flush=True)
