"""Fresh-process exact candidate readback, native signatures and no-op repeat."""
import bpy,json,sys,hashlib,time
from pathlib import Path
from types import SimpleNamespace
R=Path(__file__).resolve().parents[1];Q=R/'qa';sys.path[:0]=[str(R/'scripts'),str(Q)]
import forest_undergrowth13 as entry
import understory_detail as accepted
import shrub08_auditlib as audit
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record=json.loads((Q/'forest-undergrowth13-build.json').read_text());expected=json.loads((Q/'forest-undergrowth13-fingerprint.json').read_text())
plan_path=Q/'forest-undergrowth13-plan.json';plan=json.loads(plan_path.read_text())
assert record['status']=='PASS_NATIVE_REPLACEMENT_CANDIDATE_NO_RENDER' and sha(plan_path)==record['plan_sha256']
P=Path(record['candidate']);assert sha(P)==record['candidate_sha256']
assert sha(R/'scripts/forest_undergrowth13.py')==record['helper_sha256']
start=time.monotonic();bpy.ops.wm.open_mainfile(filepath=str(P));bpy.context.scene.frame_set(48)
before=audit.snapshot();assert audit.digest(before)==expected['snapshot_sha256']
assert all(audit.physical_hash(bpy.context.scene.objects[n])==v for n,v in record['protected_physics'].items())
signatures={}
for asset in accepted.APPROVED['assets'].values():
 for part in ('branch','leaf'):
  name=asset['new_'+part+'_mesh'];signatures[name]=accepted.mesh_signature(bpy.data.meshes[name])
  assert signatures[name]==asset['new_'+part+'_signature']
repeat=entry.build(SimpleNamespace(root=R),plan,enabled=True);assert repeat['status']=='SKIPPED_ALREADY_APPLIED'
after=audit.snapshot();assert before==after
out={'status':'PASS_FRESH_PROCESS_EXACT_REOPEN','candidate_sha256':record['candidate_sha256'],'helper_sha256':record['helper_sha256'],
     'candidate':str(P),'instances':record['instances'],'target_objects':len(record['changed_objects']),'snapshot_exact':True,
     'repeat_no_mutation':True,'native_shared_signatures':signatures,'protected_physics_count':len(record['protected_physics']),
     'source_unchanged':sha(Path(record['source']))==record['source_sha256'],'saved':False,'rendered':False,'seconds':time.monotonic()-start}
(Q/'forest-undergrowth13-readback.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
