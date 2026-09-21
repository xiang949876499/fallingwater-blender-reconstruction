import bpy,sys,json,hashlib,time
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];Q=ROOT/'qa';sys.path[:0]=[str(ROOT/'scripts'),str(Q)]
import forest_canopy_detail11 as entry
import shrub08_auditlib as audit
check=json.loads((Q/'forest-canopy11-integration-check.json').read_text(encoding='utf-8'))
assert check['status']=='PASS_NATIVE_LIBRARY_FULL_NAV10A_REGRESSION_NO_RENDER'
target=Path(check['candidate']);assert hashlib.sha256(target.read_bytes()).hexdigest()==check['candidate_sha256']
for path,expected in check['dependencies'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected
bpy.ops.wm.open_mainfile(filepath=str(target));scene=bpy.context.scene;stored=scene.frame_current;start=time.monotonic()
report={'status':'RUNNING','candidate_sha256':check['candidate_sha256'],'rendered':False,'scene_saved_again':False}
try:
 expected=json.loads((Q/'forest-canopy11-integration-fingerprint.json').read_text(encoding='utf-8'));snapshot=audit.snapshot()
 assert audit.digest(snapshot)==expected['snapshot_sha256'];report['full_saved_snapshot_exact']=True
 with bpy.data.libraries.load(str(ROOT/'assets/models/site_canopy18.blend'),link=False) as (available,loaded):
  contents={key:list(getattr(available,key)) for key in ('meshes','materials','images','objects','scenes','texts','node_groups')}
 assert len(contents['meshes'])==6 and not contents['objects'] and not contents['scenes'] and not contents['texts'] and not contents['images']
 report['native_library_contents']=contents
 report['repeated_call']=entry.build(SimpleNamespace(root=ROOT),{'enabled':True});assert report['repeated_call']['status']=='SKIPPED_ALREADY_APPLIED'
 assert audit.digest(audit.snapshot())==expected['snapshot_sha256'];report['repeat_has_zero_mutation']=True
 scene.frame_set(48);assert check['protected_physics']=={n:audit.physical_hash(scene.objects[n]) for n in check['protected_physics']}
 manifest=entry.load_manifest(ROOT);report['strict_native_mesh_signatures']={r['name']:entry.mesh_signature(bpy.data.meshes[r['name']]) for r in manifest['meshes']}
 assert all(report['strict_native_mesh_signatures'][r['name']]==r['signature'] for r in manifest['meshes'])
 report['protected_physics_hash_count']=len(check['protected_physics']);report['status']='FRESH_REOPEN_NATIVE_WRAPPER_PASS'
except Exception as e:report['status']='FAILED';report['exception']=repr(e);raise
finally:
 report['elapsed_s']=time.monotonic()-start;(Q/'forest-canopy11-integration-readback.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('CANOPY_INTEGRATION_READBACK',report['status'],flush=True)
