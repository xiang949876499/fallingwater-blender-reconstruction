"""Compare regenerated foliage to the accepted saved mesh without weakening guards."""
from pathlib import Path
from types import SimpleNamespace
import bpy, sys, json, hashlib, math
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import main_interface10,master_detail10,master_bath_detail10,guest_circulation10,bridge_detail10
import understory_detail,understory_detail08
out=ROOT/'qa/shrub10-reproduction-diagnostic.json';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene/Fallingwater_iteration09.blend'))
bpy.context.scene.render.threads_mode='FIXED';bpy.context.scene.render.threads=4
for m in (main_interface10,):m.apply()
master_detail10.apply(bath_source10=True);master_bath_detail10.apply();guest_circulation10.apply()
bridge_detail10.apply(json.loads((ROOT/'data/bridge_detail10.json').read_text(encoding='utf8'))['exact_replace_names'])
source=ROOT/'scene/Fallingwater_shrub_integration09.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='3de043c500dc6735bcdefe8f4a5362d2afa65387a38b9f24768a2862fff5fa80'
rows=[]
for key,data in understory_detail.APPROVED['assets'].items():
    oldleaf=bpy.data.meshes[data['old_leaf_mesh']];oldbark=bpy.data.meshes[data['old_branch_mesh']]
    bark,leaf,rec=understory_detail08.make_asset(int(key),oldbark.materials[0],list(oldleaf.materials),data['removed_design_leaf_ids'])
    with bpy.data.libraries.load(str(source),link=False) as (frm,to):to.meshes=[data['new_leaf_mesh']]
    accepted=to.meshes[0]
    actual_names=[m.name if m else None for m in accepted.materials]
    accepted.materials.clear()
    for material in oldleaf.materials:accepted.materials.append(material)
    positions=[(a.co-b.co).length for a,b in zip(leaf.vertices,accepted.vertices)]
    edges=[tuple(e.vertices) for e in leaf.edges];expectededges=[tuple(e.vertices) for e in accepted.edges]
    faces=[(tuple(p.vertices),p.material_index,p.use_smooth) for p in leaf.polygons]
    expectedfaces=[(tuple(p.vertices),p.material_index,p.use_smooth) for p in accepted.polygons]
    uvdiff=[(a.uv-b.uv).length for a,b in zip(leaf.uv_layers[0].data,accepted.uv_layers[0].data)]
    rows.append({'asset':key,'regenerated_hash':understory_detail.mesh_signature(leaf),
      'accepted_hash':understory_detail.mesh_signature(accepted),'expected_hash':data['new_leaf_signature'],
      'vertex_counts':[len(leaf.vertices),len(accepted.vertices)],'max_vertex_delta_m':max(positions),
      'changed_vertex_count':sum(d!=0 for d in positions),'edge_order_equal':edges==expectededges,
      'edge_sets_equal':sorted(tuple(sorted(e)) for e in edges)==sorted(tuple(sorted(e)) for e in expectededges),
      'polygon_identity_equal':faces==expectedfaces,'max_uv_delta':max(uvdiff),
      'library_material_names_before_rebind':actual_names})
    # Remove only this diagnostic's newly loaded meshes so subsequent asset
    # generation still receives an unambiguous fresh name.
    bpy.data.meshes.remove(accepted)
out.write_text(json.dumps({'status':'DIAGNOSTIC_ONLY_NO_SAVED_SCENE','rows':rows},indent=2),encoding='utf8')
print(json.dumps(rows),flush=True)
