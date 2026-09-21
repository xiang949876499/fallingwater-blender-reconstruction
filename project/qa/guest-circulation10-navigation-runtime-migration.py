"""Move only runtime design reads; preserve immutable pre-migration sources."""
import json,hashlib
from pathlib import Path
R=Path('D:/zx/test/project');Q=R/'qa'
def sha(data):return hashlib.sha256(data).hexdigest()
result=json.loads((Q/'guest-circulation10-navigation-result-attempt04.json').read_text(encoding='utf-8'))
assert result['graph_pass'] and result['frame_pass'] and result['checked_scene_saved']
old_design=Q/'guest-circulation10-design.json';runtime=R/'data/guest_circulation10_design.json'
assert old_design.read_bytes()==runtime.read_bytes()
old=b'qa/guest-circulation10-design.json';new=b'data/guest_circulation10_design.json'
rows=[]
for filename in ('guest_circulation10.py','guest_circulation10_routes.py'):
    path=R/'scripts'/filename;before=path.read_bytes()
    assert before.count(old)==1,(filename,'Expected exactly one runtime read')
    if filename.endswith('_routes.py'):assert sha(before)==result['adapter_sha256']
    snapshot=Q/('guest-circulation10-navigation-runtime-before-'+filename)
    assert not snapshot.exists(),'Preserve an existing migration; do not repeat'
    snapshot.write_bytes(before)
    after=before.replace(old,new);path.write_bytes(after)
    rows.append({'file':str(path.relative_to(R)),'before_sha256':sha(before),'after_sha256':sha(after),
                 'archived_before':str(snapshot.relative_to(R)),
                 'only_expected_path_literal_changed':after.replace(new,old)==before})
spec_path=R/'data/guest_circulation10.json';spec=json.loads(spec_path.read_text(encoding='utf-8'))
spec['runtime_design_file']='data/guest_circulation10_design.json'
spec['runtime_design_sha256']=sha(runtime.read_bytes())
spec['runtime_adapter_sha256']=next(r['after_sha256'] for r in rows if r['file'].endswith('_routes.py'))
spec['runtime_migration_evidence']='qa/guest-circulation10-navigation-runtime-migration.json'
spec_path.write_text(json.dumps(spec,indent=2),encoding='utf-8')
report={'status':'RUNTIME_PATH_ONLY_DATA_IDENTICAL','canonical_design':str(runtime.relative_to(R)),
        'canonical_design_sha256':sha(runtime.read_bytes()),'archived_design':str(old_design.relative_to(R)),
        'design_bytes_identical':True,'physical_values_changed':False,'source_edits':rows,
        'validated_pre_migration_adapter_sha256':result['adapter_sha256'],
        'saved_tour_sha256':result['candidate_tour_sha256'],
        'note':'Frozen navigation and scene retain pre-migration source hashes; archived sources are used for independent reopen. Current helper reads canonical data. No geometry or production guest/main/tour module changed.'}
(Q/'guest-circulation10-navigation-runtime-migration.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
