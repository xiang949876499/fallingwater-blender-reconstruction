"""Freeze exactly matching07 data and its embedded config before candidate08."""
import bpy,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'scene/Fallingwater_iteration07.blend'
sha=hashlib.sha256(source.read_bytes()).hexdigest()
assert sha=='bf50530009e4a93315915815473188c91d891272ef2d8e9e0169b704bd2e2f16'
bpy.ops.wm.open_mainfile(filepath=str(source))
inputs={k.replace('\\','/'):v for k,v in json.loads(bpy.data.texts['FW_BUILD_INPUTS.json'].as_string()).items()}
config=json.loads(bpy.data.texts['FW_CONFIG.json'].as_string())
folder=ROOT/'qa/bank08-frozen-context';records=[]
for name in ('scripts/site.py','scripts/fwlib.py','data/site.json','data/main_house.json','data/guest_house.json'):
    raw=(ROOT/name).read_bytes();actual=hashlib.sha256(raw).hexdigest()
    assert actual==inputs[name],(name,actual,inputs[name])
    destination=folder/name;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(raw)
    records.append({'file':name,'sha256':actual,'equal_to_07_embedded_input':True})
(folder/'config.json').write_text(json.dumps(config,indent=2),encoding='utf8')
record={'status':'PASS_FROZEN_INPUTS_MATCH_COMPLETE07','source_sha256':sha,'frozen_context':str(folder),
        'source_embedded_config':config,'dependencies':records,
        'exclusions_note':'main_house.py may be edited by another agent; it is neither imported nor read. Only matching07 JSON data and site resolver are copied once.'}
(ROOT/'qa/bank08-frozen-inputs.json').write_text(json.dumps(record,indent=2),encoding='utf8')
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
print('BANK08_FROZEN_INPUTS',json.dumps({k:v for k,v in record.items() if k!='source_embedded_config'}),flush=True)
