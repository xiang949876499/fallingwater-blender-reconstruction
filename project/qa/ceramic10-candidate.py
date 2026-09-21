"""One L3 toilet surface candidate from frozen09; no production change."""
from pathlib import Path
import sys, json, hashlib, time, struct
import bpy
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'scripts'))
import furnishing_ceramic10
source=root/'scene/Fallingwater_iteration09.blend'
out=root/'scene/Fallingwater_ceramic_candidate10.blend'
report_path=root/'qa/ceramic10-candidate.json'
assert not out.exists() and not report_path.exists()
expected='489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
bpy.ops.wm.open_mainfile(filepath=str(source))
t=time.monotonic()
assembly=next(o for o in bpy.data.objects if o.type=='EMPTY' and o.get('room_id')=='MAIN_L3_BATH' and o.get('asset_type')=='water_closet')
targets={assembly.name+'_'+label for label in furnishing_ceramic10.PROFILES}

def fingerprint(obj,mesh_cache):
    h=hashlib.sha256()
    h.update(repr((obj.type,list(obj.location),list(obj.rotation_euler),list(obj.scale),obj.parent.name if obj.parent else None,sorted((str(k),repr(v)) for k,v in obj.items()))).encode())
    if obj.type=='MESH':
        key=obj.data.as_pointer()
        if key not in mesh_cache:
            m=hashlib.sha256()
            for v in obj.data.vertices:m.update(struct.pack('<3f',*v.co))
            for p in obj.data.polygons:
                m.update(struct.pack('<IIB',len(p.vertices),p.material_index,p.use_smooth))
                m.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
            m.update(repr([mat.name if mat else None for mat in obj.data.materials]).encode())
            mesh_cache[key]=m.digest()
        h.update(mesh_cache[key])
    return h.hexdigest()

before_cache={}
before={o.name:fingerprint(o,before_cache) for o in bpy.data.objects if o.name not in targets}
print('CERAMIC10 original unique meshes fingerprinted',len(before_cache),flush=True)
result=furnishing_ceramic10.replace_assembly(assembly)
after_cache={}
after={o.name:fingerprint(o,after_cache) for o in bpy.data.objects if o.name not in targets}
assert before==after,'Non-target object changed'
assert len(bpy.data.objects)==23385
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
record={'status':'ONE_ASSEMBLY_GEOMETRY_PASS_VISUAL_NOT_RUN','source_sha256':expected,
        'candidate':str(out),'candidate_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
        'assembly':assembly.name,'changed_objects':sorted(targets),'checks':result,
        'unchanged_non_target_objects':len(before),'seconds':time.monotonic()-t,
        'limits':'Only bounded C ceramic surface smoothing/closed shell. Existing furniture position/materials/other objects unchanged. No real fixture identity or whole-room realism claimed.'}
report_path.write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({k:record[k] for k in ('status','candidate_sha256','seconds')},indent=2))
