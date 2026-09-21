"""New CPU4 process, full09 independent candidate fingerprint and current route."""
import bpy,sys,json,hashlib,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'qa'))
import understory_detail as entry
import shrub08_auditlib as audit
check=json.loads((ROOT/'qa/shrub09-integration-check.json').read_text())
assert check['status']=='PASS_FULL09_ENTRY_AND_PHYSICAL_REGRESSION_NO_RENDER'
source=ROOT/'scene/Fallingwater_iteration09.blend';candidate=Path(check['candidate'])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(candidate)==check['candidate_sha256']
assert sha(ROOT/'scripts/understory_detail.py')==check['entry_sha256']
assert sha(ROOT/'scripts/understory_detail08.py')==check['generator_sha256']
result={'status':'RUNNING','candidate_sha256':check['candidate_sha256'],'rendered':False,'saved':False,'fresh_process':True}
start=time.monotonic()
try:
    bpy.ops.wm.open_mainfile(filepath=str(candidate));scene=bpy.context.scene
    scene.frame_set(scene.frame_current);bpy.context.view_layer.update()
    current=audit.snapshot();expected=json.loads((ROOT/'qa/shrub09-integration-fingerprint.json').read_text())
    assert audit.digest(current)==expected['scene_snapshot_sha256']
    assert all(entry.mesh_signature(scene.objects[r['name']].data)==r['new_signature'] for r in entry.APPROVED['objects'])
    result['full_snapshot_equal']=True;result['compared_objects']=len(current['objects'])
    scene.frame_set(48);bpy.context.view_layer.update()
    physics={name:audit.physical_hash(scene.objects[name]) for name in check['frozen_physics']}
    assert physics==check['frozen_physics'];result['core_shoulder_water_equal']=True
    site=json.loads((ROOT/'qa/bank08-frozen-context/data/site.json').read_text())
    exclusion=next(z for z in site['building_exclusions'] if z['name']=='main_plunge_and_stair')
    contacts=audit.contact_checks(check['selection'],check['application']['assets'],exclusion)
    assert not any(r['failures'] for r in contacts);result['contact_checks']=contacts
    targets=[scene.objects[n] for n in check['changed_objects']];bvh,owners=audit.world_bvh(targets,True)
    route=json.loads((ROOT/'qa/shrub09-integration-route.json').read_text())
    assert route['source_scene_sha256']==check['source_sha256']
    nav=audit.route_regression(route,bvh,owners,bvh,owners)
    assert nav['candidate_target_hits']==0;result['current09_route']=nav
    assert sha(source)==check['source_sha256'] and sha(candidate)==check['candidate_sha256']
    result['status']='PASS_FRESH_FULL09_INTEGRATION_READBACK_NO_RENDER'
except Exception as error:
    result['status']='FAILED_READBACK';result['exception']=repr(error)
    raise
finally:
    result['elapsed_s']=time.monotonic()-start
    (ROOT/'qa/shrub09-integration-readback.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print('SHRUB09_READBACK',json.dumps({k:v for k,v in result.items() if k not in ('contact_checks','current09_route')}),flush=True)
