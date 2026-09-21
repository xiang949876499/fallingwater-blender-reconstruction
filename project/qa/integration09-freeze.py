"""Freeze reproducible build inputs, then preserve the completed09 checkpoint."""
import hashlib
import json
import shutil
import sys
from pathlib import Path
from datetime import datetime, timezone

root = Path(__file__).resolve().parents[1]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
record_path = root/'qa/integration09-freeze.json'
frozen = root/'scene/Fallingwater_iteration09.blend'
names = ['build_scene','main_house','guest_house','furnishings','furnishing_softgoods',
         'materials','architectural_detail','masonry_detail','site','water_integration',
         'asset_materials','camera_review','navigation','fwlib','near_terrain_detail',
         'dimension_audit','nominal_targets']
paths = [root/f'scripts/{n}.py' for n in names]
paths += [root/'config.json',root/'data/main_house.json',root/'data/guest_house.json',
          root/'data/site.json',root/'data/camera-settings-reviewed.json',
          root/'data/dimension-target-reviews.json',root/'data/dimension-anchors-extra.json']
if sys.argv[1] == 'prepare':
    assert not frozen.exists(), 'Do not overwrite a previous09 checkpoint'
    assert sha(root/'scene/Fallingwater_iteration08.blend') == 'c5cd501e4c8ae0205ecb2437cd2d06d0c92bcc9a87e7d93d3986aeef976070d7'
    assert sha(root/'scene/Fallingwater_working.blend') == sha(root/'scene/Fallingwater_iteration08.blend')
    expected = {'main_house':'d80558f5780773f8f3b2e8324dea32da616500958c83a70d7637a9e3fc180caf',
                'furnishings':'a6a632ea9d9486c10778f48f0bc6f707af244746731b09a257cd34cbd9d0a053',
                'furnishing_softgoods':'33ef2f96bc52383c26fe03547ef4cc6b9916417411f392e3cc9bfd5ae2e8c1b6'}
    for n, h in expected.items():
        assert sha(root/f'scripts/{n}.py') == h, n
    data = {'prepared_utc':datetime.now(timezone.utc).isoformat(), 'status':'INPUTS_FROZEN_NOT_BUILT',
            'inputs':{str(p.relative_to(root)):sha(p) for p in paths},
            'scope':'Structure09b and ten soft pillows; no guest stair, vegetation, water or preview candidate installed',
            'visual_reviews':['structure09b-root-visual.md','softgoods09-root-visual.md']}
    record_path.write_text(json.dumps(data,indent=2),encoding='utf-8')
    print(json.dumps({'status':data['status'],'inputs':len(data['inputs'])}))
elif sys.argv[1] == 'finalize':
    data=json.loads(record_path.read_text(encoding='utf-8'))
    assert data['status']=='INPUTS_FROZEN_NOT_BUILT'
    generated=json.loads((root/'qa/integration09-generated-data-check.json').read_text(encoding='utf-8'))
    assert generated['status']=='PASS' and not generated['differences']
    assert generated['before_build_sha256']==data['inputs']['data\\main_house.json']
    assert generated['actual_sha256']==sha(root/'data/main_house.json')
    for p,h in data['inputs'].items():
        if p!='data\\main_house.json':
            assert sha(root/p)==h, f'Build input changed: {p}'
    build=json.loads((root/'qa/integration-build.json').read_text(encoding='utf-8'))
    assert build['status'].startswith('BUILD_PASS') and build['rooms']==60
    working=root/'scene/Fallingwater_working.blend'
    assert sha(working) != sha(root/'scene/Fallingwater_iteration08.blend')
    assert not frozen.exists()
    shutil.copy2(working,frozen)
    shutil.copy2(root/'qa/integration-build.json',root/'qa/integration-build09.json')
    data.update(status='BUILD_SAVED_PENDING_INTEGRATED_QA', finalized_utc=datetime.now(timezone.utc).isoformat(),
                checkpoint=str(frozen.relative_to(root)),scene_sha256=sha(frozen),bytes=frozen.stat().st_size,build=build)
    data['generated_outputs']={'data/main_house.json':generated}
    data['snapshot_classification_correction']='main_house.build() exports data/main_house.json from source; its pre-build hash above is a prior-output snapshot. Fresh source-only export matched new output byte-for-byte with Windows CRLF. All other frozen input hashes are unchanged. Initial overbroad immutability and LF-only comparison failures retained in QA logs.'
    record_path.write_text(json.dumps(data,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in data.items() if k!='inputs'},indent=2))
else:
    raise ValueError('prepare or finalize required')
