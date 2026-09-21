"""Fresh-process readback of the saved candidate; no helper apply/save/render."""
import bpy,sys,json,hashlib,array,collections,math,ast
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];Q=R/'qa'
report=json.loads((Q/'main-terrace11-attempt02-check.json').read_text(encoding='utf-8'))
p=Path(report['candidate']);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
before=sha(p);assert before==report['candidate_sha256']
# Reuse independently written BVH/RNA comparison functions only; do not execute
# the builder or import the geometry helper. The data source is saved meshes.
tree=ast.parse((Q/'main-terrace11-build-check.py').read_text(encoding='utf-8'))
selected={'settings','prop_state','fingerprint','materials','bbox','local_trees','hit','dimension','dimensions','topology'}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in selected],type_ignores=[]),'<read-only mesh verification functions>','exec'))
def prop_state(obj):
    out=[]
    for prop in obj.bl_rna.properties:
        if prop.identifier in ('rna_type','name','users') or prop.is_readonly:continue
        try:
            v=getattr(obj,prop.identifier)
            if isinstance(v,(str,int,float,bool)) or v is None:out.append((prop.identifier,v))
            elif isinstance(v,bpy.types.ID):out.append((prop.identifier,v.name))
            elif getattr(prop,'is_array',False):out.append((prop.identifier,list(v)))
        except Exception:pass
    return out
def actual_material_content():
    out={}
    def value(v):
        if isinstance(v,(str,int,float,bool)) or v is None:return v
        if isinstance(v,bpy.types.ID):return v.name
        try:return list(v)
        except TypeError:return str(v)
    for m in bpy.data.materials:
        rows=[prop_state(m)]
        if m.node_tree:
            for node in m.node_tree.nodes:rows.append((node.name,node.bl_idname,prop_state(node),[(i.name,value(i.default_value)) for i in node.inputs if hasattr(i,'default_value')]))
            rows.append([(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links])
        out[m.name]=hashlib.sha256(str(rows).encode()).hexdigest()
    return out
bpy.ops.wm.open_mainfile(filepath=report['source']);s=bpy.context.scene
source_fp=fingerprint();source_mats=actual_material_content();source_settings=settings()
bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene
fp=fingerprint();mats=actual_material_content();trees=local_trees();dims=dimensions(trees,True)
mesh=[topology(n) for n in report['manifest']['changed']]
cam_names=[o.name for o in s.objects if o.type=='CAMERA']
changed=sorted(n for n in fp if n in source_fp and fp[n]!=source_fp[n]);removed=sorted(set(source_fp)-set(fp));added=sorted(set(fp)-set(source_fp))
outside=sorted(n for n in changed if n not in report['manifest']['changed'])
result={'candidate':str(p),'candidate_sha256':before,'helper_sha256':report['helper_sha256'],'source':report['source'],'source_sha256':sha(report['source']),'comparison_note':'Both saved scenes freshly loaded in this process. Stable stored RNA/mesh/modifier content only; runtime readonly session IDs excluded. Socket default arrays compared as numerical values.','changed_names':changed,'removed_names':removed,'added_names':added,'outside_whitelist_changed':outside,'saved_object_fingerprints_match':not outside and changed==sorted(report['manifest']['changed']) and removed==sorted(report['manifest']['removed']) and not added,'material_content_match':mats==source_mats,'saved_settings_match':settings()==source_settings,'camera_count':len(cam_names),'all_original_camera_fingerprints_match':all(fp[n]==source_fp[n] for n in cam_names),'dimensions':dims,'mesh_checks':mesh,'rendered':False,'saved':False,'candidate_hash_unchanged':sha(p)==before,'stable_object_fingerprints_source':source_fp,'stable_object_fingerprints_candidate':fp,'stable_material_content_source':source_mats,'stable_material_content_candidate':mats}
result['pass']=all(result[k] for k in ('saved_object_fingerprints_match','material_content_match','saved_settings_match','all_original_camera_fingerprints_match','candidate_hash_unchanged')) and all(r['pass'] for r in dims+mesh)
(Q/'main-terrace11-reopen.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if not k.startswith('stable_')},indent=2));assert result['pass']
