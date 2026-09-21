"""Full09 independent application, negative guards, contacts and current route."""
import bpy,sys,json,hashlib,time
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'qa'))
import understory_detail as entry
import shrub08_auditlib as audit
SOURCE=ROOT/'scene/Fallingwater_iteration09.blend'
TARGET=ROOT/'scene/Fallingwater_shrub_integration09.blend'
SOURCE_SHA='489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE)==SOURCE_SHA
assert not TARGET.exists(),'Preserve previous candidates'
route_raw=(ROOT/'qa/tour-path-route-iteration09-attempt01.json').read_bytes();route=json.loads(route_raw)
assert route['source_scene_sha256']==SOURCE_SHA
(ROOT/'qa/shrub09-integration-route.json').write_bytes(route_raw)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;frame=scene.frame_current
scene.frame_set(frame);bpy.context.view_layer.update()
source_inputs={k.replace('\\','/'):v for k,v in json.loads(bpy.data.texts['FW_BUILD_INPUTS.json'].as_string()).items()}
site_path=ROOT/'qa/bank08-frozen-context/data/site.json';assert sha(site_path)==source_inputs['data/site.json']
exclusion=next(z for z in json.loads(site_path.read_text())['building_exclusions'] if z['name']=='main_plunge_and_stair')
source08_check=json.loads((ROOT/'qa/shrub08-candidate-check.json').read_text())
selection=source08_check['selection'];targets={r['name'] for r in entry.APPROVED['objects']}
report={'status':'RUNNING','source_sha256':SOURCE_SHA,'candidate':str(TARGET),'source_frame':frame,'comparison_frame':48,
        'entry_sha256':sha(ROOT/'scripts/understory_detail.py'),'generator_sha256':sha(ROOT/'scripts/understory_detail08.py'),
        'audit_helper_sha256':sha(ROOT/'qa/shrub08_auditlib.py'),
        'frozen_route_sha256':hashlib.sha256(route_raw).hexdigest(),'frozen_site_sha256':sha(site_path),
        'rendered':False,'production_wiring_changed':False}
start=time.monotonic()
try:
    print('SHRUB09 before fingerprint',flush=True)
    before=audit.snapshot()
    ctx=SimpleNamespace(root=ROOT)
    original_names=set(bpy.data.meshes.keys())
    report['disabled_guard']=entry.build(ctx,{})
    assert report['disabled_guard']['status']=='NOT_RUN_DISABLED'
    first=scene.objects[entry.APPROVED['objects'][0]['name']]
    saved_location=first.location.copy()
    first.location.x+=.05;bpy.context.view_layer.update()
    try:
        entry.build(ctx,{'enabled':True})
        raise AssertionError('Wrong root was accepted')
    except ValueError as error:
        report['wrong_root_rejected']=str(error)
    finally:
        first.location=saved_location;bpy.context.view_layer.update()
    assert set(bpy.data.meshes.keys())==original_names
    saved_data=first.data
    first.data=bpy.data.meshes['TREE_Understory_3_Stems' if entry.APPROVED['objects'][0]['asset']==2 else 'TREE_Understory_2_Stems']
    try:
        entry.build(ctx,{'enabled':True})
        raise AssertionError('Wrong original data was accepted')
    except ValueError as error:
        report['wrong_data_rejected']=str(error)
    finally:
        first.data=saved_data;bpy.context.view_layer.update()
    assert set(bpy.data.meshes.keys())==original_names
    scene.frame_set(48);bpy.context.view_layer.update()
    physics_names=[o.name for o in scene.objects if o.type=='MESH' and o.name.startswith(('SITE_Core_','SITE_Cascade_Shoulder_Continuous','WATER_'))]
    physics_before={name:audit.physical_hash(scene.objects[name]) for name in physics_names}
    old_bvh,old_owners=audit.world_bvh([scene.objects[n] for n in sorted(targets)],True)
    print('SHRUB09 apply',flush=True)
    application=entry.build(ctx,{'enabled':True});report['application']=application
    assert application['status']=='APPLIED_ACCEPTED_16_SHRUB_SHAPES_VISUAL_SCOPE_ONLY'
    report['repeat_guard']=entry.build(ctx,{'enabled':True})
    assert report['repeat_guard']['status']=='SKIPPED_ALREADY_APPLIED'
    report['exact_accepted_asset_signatures']={r['new_mesh']:entry.mesh_signature(scene.objects[r['name']].data) for r in entry.APPROVED['objects']}
    assert all(entry.mesh_signature(scene.objects[r['name']].data)==r['new_signature'] for r in entry.APPROVED['objects'])
    print('SHRUB09 actual contacts and current09 route',flush=True)
    contacts=audit.contact_checks(selection,application['assets'],exclusion);report['contact_checks']=contacts
    assert not any(r['failures'] for r in contacts),[(r['object'],r['failures']) for r in contacts if r['failures']]
    new_bvh,new_owners=audit.world_bvh([scene.objects[n] for n in sorted(targets)],True)
    nav=audit.route_regression(route,old_bvh,old_owners,new_bvh,new_owners);report['route_regression']=nav
    assert not nav['new_obstacles'] and nav['candidate_target_hits']==0,nav
    physics_after={name:audit.physical_hash(scene.objects[name]) for name in physics_names}
    assert physics_before==physics_after
    report['frozen_physics']=physics_after
    scene.frame_set(frame);bpy.context.view_layer.update()
    print('SHRUB09 after fingerprint',flush=True)
    after=audit.snapshot();changed=audit.compare_snapshots(before,after,targets)
    assert set(changed)==targets
    compact={'scene_snapshot_sha256':audit.digest(after),'objects':{k:audit.digest(v) for k,v in after['objects'].items()},
             'global':audit.digest(after['global']),'meshes':after['meshes']}
    (ROOT/'qa/shrub09-integration-fingerprint.json').write_text(json.dumps(compact,separators=(',',':')),encoding='utf8')
    report.update({'status':'PASS_FULL09_ENTRY_AND_PHYSICAL_REGRESSION_NO_RENDER','changed_objects':sorted(changed),
                   'compared_objects':len(before['objects']),'snapshot_sha256':audit.digest(after),'object_mutation_whitelist':['data'],
                   'all_non_target_fingerprints_unchanged':True,'labels_changed':False,'selection':selection,
                   'terrain_material':[m.name for m in scene.objects['SITE_Continuous_BearRun_Terrain'].data.materials]})
    assert sha(SOURCE)==SOURCE_SHA
    bpy.ops.wm.save_as_mainfile(filepath=str(TARGET),compress=True)
    report['candidate_sha256']=sha(TARGET)
except Exception as error:
    report['status']='FAILED_NO_PRODUCTION_INTEGRATION';report['exception']=repr(error)
    raise
finally:
    report['elapsed_s']=time.monotonic()-start
    (ROOT/'qa/shrub09-integration-check.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print('SHRUB09_RESULT',json.dumps({k:report[k] for k in ('status','candidate','source_frame','elapsed_s')}),flush=True)
