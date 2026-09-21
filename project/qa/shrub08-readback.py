"""Fresh CPU4 process: saved candidate fingerprint, contacts, and frozen route."""
import bpy,sys,json,hashlib,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'qa'))
import shrub08_auditlib as audit
report=json.loads((ROOT/'qa/shrub08-candidate-check.json').read_text())
assert report['status']=='PASS_ISOLATED_16_SHRUB_PHYSICAL_CHECKS_VISUAL_NOT_RUN'
candidate=Path(report['candidate'])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(candidate)==report['candidate_sha256']
assert sha(ROOT/'scripts/understory_detail08.py')==report['helper_sha256']
assert sha(ROOT/'qa/shrub08_auditlib.py')==report['audit_helper_sha256']
start=time.monotonic()
result={'status':'RUNNING','candidate_sha256':report['candidate_sha256'],'fresh_process':True,'rendered':False,'saved':False}
try:
    bpy.ops.wm.open_mainfile(filepath=str(candidate));scene=bpy.context.scene
    frame=scene.frame_current;scene.frame_set(frame);bpy.context.view_layer.update()
    actual=audit.snapshot()
    result['snapshot_sha256']=audit.digest(actual)
    expected=json.loads((ROOT/'qa/shrub08-candidate-snapshot.json').read_text())
    if result['snapshot_sha256']!=report['candidate_snapshot_sha256']:
        canonical=json.loads(json.dumps(actual))
        result['object_differences']=[k for k in set(expected['objects'])|set(canonical['objects']) if expected['objects'].get(k)!=canonical['objects'].get(k)]
        result['global_differences']=[k for k in set(expected['global'])|set(canonical['global']) if expected['global'].get(k)!=canonical['global'].get(k)]
        result['mesh_differences']=[k for k in set(expected['meshes'])|set(canonical['meshes']) if expected['meshes'].get(k)!=canonical['meshes'].get(k)]
        raise AssertionError('Saved fingerprint differs; see explicit difference lists')
    result['compared_objects']=len(actual['objects'])
    result['all_object_data_material_camera_light_config_fingerprints_equal']=True
    scene.frame_set(48);bpy.context.view_layer.update()
    physics={name:audit.physical_hash(scene.objects[name]) for name in report['frozen_physics']}
    assert physics==report['frozen_physics']
    result['frozen_evaluated_core_shoulder_water_equal']=True
    site=json.loads((ROOT/'qa/bank08-frozen-context/data/site.json').read_text())
    exclusion=next(z for z in site['building_exclusions'] if z['name']=='main_plunge_and_stair')
    contacts=audit.contact_checks(report['selection'],report['assets'],exclusion)
    assert not any(r['failures'] for r in contacts),[(r['object'],r['failures']) for r in contacts if r['failures']]
    result['contact_checks']=contacts
    targets=[scene.objects[n] for n in report['changed_objects']]
    target_bvh,owners=audit.world_bvh(targets,True)
    route=json.loads((ROOT/'qa/shrub08-frozen-route.json').read_text())
    nav=audit.route_regression(route,target_bvh,owners,target_bvh,owners)
    assert nav['candidate_target_hits']==0
    result['saved_candidate_route_regression']=nav
    result['source_terrain_material']=[m.name for m in scene.objects['SITE_Continuous_BearRun_Terrain'].data.materials]
    assert result['source_terrain_material']==['FW_Continuous_Forest_Floor']
    assert sha(candidate)==report['candidate_sha256']
    assert sha(ROOT/'scene/Fallingwater_iteration08.blend')==report['source_sha256']
    result['status']='PASS_FRESH_READBACK_FINGERPRINT_CONTACTS_ROUTE_VISUAL_NOT_RUN'
except Exception as error:
    result['status']='FAILED_READBACK_NO_ACCEPTANCE';result['exception']=repr(error)
    raise
finally:
    result['elapsed_s']=time.monotonic()-start
    (ROOT/'qa/shrub08-readback.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print('SHRUB08_READBACK',json.dumps({k:v for k,v in result.items() if k not in ('contact_checks','saved_candidate_route_regression')}),flush=True)
