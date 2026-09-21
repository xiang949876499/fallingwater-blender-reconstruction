"""Compose locally reviewed details in an isolated copy; no production save."""
from pathlib import Path
from types import SimpleNamespace
import hashlib, json, sys, time, struct
import bpy

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
source=ROOT/'scene/Fallingwater_iteration09.blend'
output=ROOT/'scene/Fallingwater_integration_candidate10a.blend'
record=ROOT/'qa/integration10-candidate-a.json'
assert not output.exists() and not record.exists(), 'Preserve prior candidates'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
scene.render.threads_mode='FIXED';scene.render.threads=4

def snapshot():
    cache={};result={}
    for ob in scene.objects:
        h=hashlib.sha256()
        h.update(repr((ob.type,[list(r) for r in ob.matrix_world],ob.parent.name if ob.parent else None,
                       sorted((str(k),repr(v)) for k,v in ob.items()))).encode())
        if ob.type=='MESH':
            key=ob.data.as_pointer()
            if key not in cache:
                mh=hashlib.sha256()
                for v in ob.data.vertices:mh.update(struct.pack('<3f',*v.co))
                for p in ob.data.polygons:
                    mh.update(struct.pack('<IIB',len(p.vertices),p.material_index,p.use_smooth))
                    mh.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
                mh.update(repr([m.name if m else None for m in ob.data.materials]).encode())
                cache[key]=mh.digest()
            h.update(cache[key])
        result[ob.name]=h.hexdigest()
    return result

started=time.monotonic();before=snapshot();changes={}
import main_interface10, master_detail10, master_bath_detail10
import guest_circulation10, bridge_detail10, understory_detail
print('DETAIL interface',flush=True)
changes['main_interface10']=main_interface10.apply()
print('DETAIL master with final bath floor outline',flush=True)
changes['master_detail10']=master_detail10.apply(bath_source10=True)
print('DETAIL bath reads actual expanded master finish edge',flush=True)
changes['master_bath_detail10']=master_bath_detail10.apply()
print('DETAIL guest',flush=True)
changes['guest_circulation10']=guest_circulation10.apply()
print('DETAIL bridge',flush=True)
bridge_data=ROOT/'data/bridge_detail10.json'
if bridge_data.exists():
    names=json.loads(bridge_data.read_text(encoding='utf8'))['exact_replace_names']
else:
    bridge_data=ROOT/'qa/bridge10-source-probe.json'
    names=json.loads(bridge_data.read_text(encoding='utf8'))['exact_replace_names']
changes['bridge_detail10']=bridge_detail10.apply(names)
print('DETAIL accepted shrubs',flush=True)
changes['understory_detail']=understory_detail.build(SimpleNamespace(root=ROOT),{'enabled':True})
bpy.context.view_layer.update()
after=snapshot()
diff={'added':sorted(after.keys()-before.keys()),'removed':sorted(before.keys()-after.keys()),
      'changed':sorted(k for k in before.keys()&after.keys() if before[k]!=after[k]),
      'unchanged_count':sum(before[k]==after[k] for k in before.keys()&after.keys())}
inputs=[Path(m.__file__) for m in (main_interface10,master_detail10,master_bath_detail10,guest_circulation10,bridge_detail10,understory_detail)]
inputs += [ROOT/'scripts/understory_detail08.py',ROOT/'data/guest_house.json',
           ROOT/'data/guest_circulation10_design.json',bridge_data,ROOT/'assets/models/site_understory16.blend']
if (ROOT/'data/guest_circulation10.json').exists():inputs.append(ROOT/'data/guest_circulation10.json')
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
scene['iteration10_candidate_status']='DETAILS_COMPOSED; combined navigation/camera/visual QA NOT_RUN'
text=bpy.data.texts.new('FW_ITERATION10_CANDIDATE_INPUTS.json');text.write(json.dumps(hashes,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=True)
result={'status':'CANDIDATE_SAVED_COMBINED_QA_NOT_RUN','candidate':str(output),
        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'candidate_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
        'candidate_bytes':output.stat().st_size,'helper_inputs':hashes,
        'changes':changes,'object_diff':diff,'seconds':time.monotonic()-started,
        'limits':['No production file changed','Old routes/cameras require adaptation',
                  'Bridge internal water trim not installed','Native water10 failed and not installed',
                  'Local detail acceptance is not full photographic acceptance']}
record.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
(ROOT/'qa/integration10-candidate-a-fingerprints.json').write_text(json.dumps({'before':before,'after':after},indent=2),encoding='utf8')
print(json.dumps({k:result[k] for k in ('status','candidate_sha256','candidate_bytes','seconds')}),flush=True)
