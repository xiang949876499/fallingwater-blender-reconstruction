"""Fresh-process readback of the saved candidate; no helper apply/save/render."""
import bpy,sys,json,hashlib,array,collections,math,ast
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];Q=R/'qa'
report=json.loads((Q/'main-terrace11-attempt02-check.json').read_text(encoding='utf-8'))
p=Path(report['candidate']);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
before=sha(p);assert before==report['candidate_sha256']
bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene
# Reuse independently written BVH/RNA comparison functions only; do not execute
# the builder or import the geometry helper. The data source is saved meshes.
tree=ast.parse((Q/'main-terrace11-build-check.py').read_text(encoding='utf-8'))
selected={'settings','prop_state','fingerprint','materials','bbox','local_trees','hit','dimension','dimensions','topology'}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in selected],type_ignores=[]),'<read-only mesh verification functions>','exec'))
fp=fingerprint();mats=materials();trees=local_trees();dims=dimensions(trees,True)
mesh=[topology(n) for n in report['manifest']['changed']]
cam_names=[o.name for o in s.objects if o.type=='CAMERA']
result={'candidate':str(p),'candidate_sha256':before,'helper_sha256':report['helper_sha256'],'saved_object_fingerprints_match':fp==report['object_fingerprints_after'],'material_content_match':mats==report['material_fingerprints_after'],'saved_settings_match':settings()==report['settings'],'camera_count':len(cam_names),'all_original_camera_fingerprints_match':all(fp[n]==report['object_fingerprints_before'][n] for n in cam_names),'dimensions':dims,'mesh_checks':mesh,'rendered':False,'saved':False,'candidate_hash_unchanged':sha(p)==before}
result['pass']=all(result[k] for k in ('saved_object_fingerprints_match','material_content_match','saved_settings_match','all_original_camera_fingerprints_match','candidate_hash_unchanged')) and all(r['pass'] for r in dims+mesh)
(Q/'main-terrace11-reopen.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2));assert result['pass']
