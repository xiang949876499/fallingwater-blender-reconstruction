"""Derive the immutable application manifest from the actually accepted08 file."""
import bpy,json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import understory_detail as entry
accepted=ROOT/'scene/Fallingwater_shrub_candidate08.blend'
sha=hashlib.sha256(accepted.read_bytes()).hexdigest()
assert sha=='7dc113c93cab8dfae0ea73f1c797f92849d9e183f00a697040cfed346c06dc97'
source_snapshot=json.loads((ROOT/'qa/shrub08-source-snapshot.json').read_text())
check=json.loads((ROOT/'qa/shrub08-candidate-check.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(accepted))
manifest={'accepted_candidate_sha256':sha,'generator_sha256':check['helper_sha256'],'assets':{},'objects':[]}
for key,info in check['assets'].items():
    old_b=f'TREE_Understory_{key}_Stems';old_l=f'TREE_Understory_{key}_Leaves'
    new_b=f'CANDIDATE08_RhododendronLike_{key}_Branches';new_l=f'CANDIDATE08_RhododendronLike_{key}_Leaves'
    manifest['assets'][key]={'old_branch_mesh':old_b,'old_leaf_mesh':old_l,
        'new_branch_mesh':new_b,'new_leaf_mesh':new_l,
        'new_branch_signature':entry.mesh_signature(bpy.data.meshes[new_b]),'new_leaf_signature':entry.mesh_signature(bpy.data.meshes[new_l]),
        'leaf_count':info['leaf_count'],'total_triangles':info['total_triangles'],'removed_design_leaf_ids':info['removed_design_leaf_ids']}
for selected in check['selection']:
    for part,suffix in [('branches','branch_object'),('leaves','leaf_object')]:
        name=selected[suffix];obj=bpy.data.objects[name];old=source_snapshot['objects'][name]
        old_mesh=old['properties']['data'][1]
        manifest['objects'].append({'name':name,'asset':selected['asset'],'part':part,
            'matrix':old['world_matrix'],'old_mesh':old_mesh,'old_signature':entry.mesh_signature(bpy.data.meshes[old_mesh]),
            'new_mesh':obj.data.name,'new_signature':entry.mesh_signature(obj.data)})
assert len(manifest['objects'])==32
(ROOT/'qa/shrub09-integration-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print('SHRUB09_MANIFEST',len(manifest['objects']),manifest['generator_sha256'],flush=True)
