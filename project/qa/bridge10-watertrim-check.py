"""Animated bridge10 trim candidate from end-fixed source, CPU4 and no render."""
import bpy,sys,json,time,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];Q=ROOT/'qa'
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(Q))
import bridge_watertrim10 as entry
import shrub08_auditlib as audit
import bridge10_watertrim_auditlib as test
SOURCE=ROOT/'scene/Fallingwater_bridge10_endfix.blend'
TARGET=ROOT/'scene/Fallingwater_bridge10_watertrim.blend'
FRAMES=(1,24,48,120,240,241)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE)==entry.SOURCE_SHA256
assert not TARGET.exists(),'Preserve all previous scene candidates'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;original_frame=scene.frame_current
water=scene.objects[entry.WATER_NAME]
report={'status':'RUNNING','source_sha256':sha(SOURCE),'candidate':str(TARGET),'source_frame':original_frame,'test_frames':FRAMES,
        'dependencies':{str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'scripts/bridge_watertrim10.py',ROOT/'scripts/bridge_detail10.py',Q/'bridge10_watertrim_auditlib.py',Q/'shrub08_auditlib.py')},
        'rendered':False,'production_changed':False}
start=time.monotonic()
try:
    print('WATERTRIM before full fingerprint',flush=True)
    before=audit.snapshot();keys_before=test.key_state(water.data)
    cores={s:test.exact_core(scene.objects['SITE_Bridge10_Stone_Return_'+s],n) for s,n in [('SW',58),('SE',54)]}
    baseline={}
    for frame in FRAMES:
        scene.frame_set(frame);bpy.context.view_layer.update();t=time.monotonic()
        data=test.evaluate(water)
        baseline[frame]={'quality':data['quality'],'far_vertices':data['far_vertices'],'shore':test.shore_samples(data,cores)}
        print('WATERTRIM baseline',frame,json.dumps(data['quality']),flush=True)
        del data
    scene.frame_set(48);bpy.context.view_layer.update()
    protected=[o.name for o in scene.objects if o.type=='MESH' and o.name.startswith(('SITE_Core_','SITE_Cascade_Shoulder_Continuous','WATER_')) and o.name!=entry.WATER_NAME]
    physics_before={n:audit.physical_hash(scene.objects[n]) for n in protected}
    print('WATERTRIM apply static true-solid masks and dynamic differences',flush=True)
    report['application']=entry.apply()
    masks=[scene.objects[n] for n in entry.MASK_NAMES]
    report['mask_quality']=[{'name':o.name,**test.evaluate(o)['quality']} for o in masks]
    report['frames']=[]
    for frame in FRAMES:
        t=time.monotonic();scene.frame_set(frame);bpy.context.view_layer.update()
        data=test.evaluate(water)
        old=baseline[frame]
        missing=old['far_vertices']-data['far_vertices'];new=data['far_vertices']-old['far_vertices']
        shore=test.shore_compare(old['shore'],data)
        row={'frame':frame,'evaluation_and_audit_s':time.monotonic()-t,'baseline_quality':old['quality'],
             'candidate_quality':data['quality'],'missing_far_vertex_positions':len(missing),'new_far_vertex_positions':len(new),
             'shore':shore}
        report['frames'].append(row)
        print('WATERTRIM candidate',frame,json.dumps({'quality':data['quality'],'missing_far':len(missing),'new_far':len(new),'shore_failures':len(shore['failures']),'seconds':row['evaluation_and_audit_s']}),flush=True)
        del data
    scene.frame_set(48);bpy.context.view_layer.update()
    assert physics_before=={n:audit.physical_hash(scene.objects[n]) for n in protected}
    report['protected_physics']=physics_before
    report['end_face_check']=test.endpoint_faces([(scene.objects['SITE_Bridge10_Stone_Return_'+s],x,n) for s,x,n in [('SW',25.43044,58),('SE',29.46904,54),('NW',25.38,54),('NE',29.46904,54)]])
    scene.frame_set(original_frame);bpy.context.view_layer.update()
    assert test.key_state(water.data)==keys_before,'Original shape-key animation changed'
    report['shape_key_animation']=keys_before
    print('WATERTRIM after full fingerprint',flush=True)
    after=audit.snapshot()
    assert set(after['objects'])-set(before['objects'])==set(entry.MASK_NAMES)
    assert not set(before['objects'])-set(after['objects'])
    changed=[n for n in before['objects'] if before['objects'][n]!=after['objects'][n]]
    assert changed==[entry.WATER_NAME],changed
    a,b=before['objects'][entry.WATER_NAME],after['objects'][entry.WATER_NAME]
    assert {k:v for k,v in a.items() if k!='modifiers'}=={k:v for k,v in b.items() if k!='modifiers'},'Water properties or base animated mesh changed'
    assert b['modifiers'][:len(a['modifiers'])]==a['modifiers'],'Original Solidify changed'
    assert [v[0] for v in b['modifiers'][len(a['modifiers']):]]==list(entry.MODIFIERS)
    assert before['global']==after['global'],'Original global state changed'
    assert all(after['meshes'].get(n)==h for n,h in before['meshes'].items()),'Original mesh/shape key changed'
    report['fingerprint']={'unchanged_original_objects':len(before['objects'])-1,'only_changed_original':entry.WATER_NAME,
                           'only_changed_original_attribute':'append two Boolean modifiers','new_hidden_masks':list(entry.MASK_NAMES),
                           'global_equal':True,'base_meshes_and_animation_equal':True}
    report['loop_1_equals_241']=report['frames'][0]['candidate_quality']['physical_triangles_sha256']==report['frames'][-1]['candidate_quality']['physical_triangles_sha256']
    report['animation_changes_across_frames']=len({r['candidate_quality']['physical_triangles_sha256'] for r in report['frames'][:-1]})>1
    issues=[]
    for row in report['frames']:
        q=row['candidate_quality']
        if q['nonmanifold_edges'] or q['zero_area_triangles'] or not q['finite']:issues.append('WATER_MESH_QUALITY_FRAME_'+str(row['frame']))
        if row['missing_far_vertex_positions'] or row['new_far_vertex_positions']:issues.append('OUTSIDE_LOCAL_REGION_VERTEX_CHANGE_'+str(row['frame']))
        if row['shore']['failures']:issues.append('SHORE_SAMPLES_'+str(row['frame']))
    if any(r['nonmanifold_edges'] or r['zero_area_triangles'] or not r['finite'] for r in report['mask_quality']):issues.append('STATIC_MASK_MESH_QUALITY')
    if not report['loop_1_equals_241'] or not report['animation_changes_across_frames']:issues.append('ANIMATION_LOOP_OR_FROZEN')
    if not all(r['pass'] for r in report['end_face_check']):issues.append('BRIDGE_END_DUPLICATE_FACE')
    report['issues']=issues
    report['status']='CANDIDATE_VALIDATION_ISSUES_NO_INTEGRATION' if issues else 'PASS_ANIMATED_LOCAL_TRIM_PHYSICAL_NO_VISUAL_ACCEPTANCE'
    compact={'snapshot_sha256':audit.digest(after),'objects':{n:audit.digest(v) for n,v in after['objects'].items()},'global':audit.digest(after['global']),'meshes':after['meshes']}
    (Q/'bridge10-watertrim-fingerprint.json').write_text(json.dumps(compact,separators=(',',':')),encoding='utf8')
    assert sha(SOURCE)==entry.SOURCE_SHA256
    bpy.ops.wm.save_as_mainfile(filepath=str(TARGET),compress=True);report['candidate_sha256']=sha(TARGET)
except Exception as error:
    report['status']='FAILED_NO_PRODUCTION_INTEGRATION';report['exception']=repr(error)
    raise
finally:
    report['elapsed_s']=time.monotonic()-start
    (Q/'bridge10-watertrim-check.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print('WATERTRIM_RESULT',json.dumps({k:report.get(k) for k in ['status','candidate','candidate_sha256','issues','elapsed_s']}),flush=True)
