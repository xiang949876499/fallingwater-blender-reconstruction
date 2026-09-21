"""Local old-leaf contact correction; preserves original07b candidate evidence."""
import bpy,json,hashlib,struct,sys
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import near_terrain_detail as near
base=json.loads((ROOT/'qa/near-terrain07b-candidate-check.json').read_text(encoding='utf8'))
source=Path(base['candidate']);assert hashlib.sha256(source.read_bytes()).hexdigest()==base['candidate_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.scene.frame_set(48)
def snapshot():
    hashes={}
    for mesh in bpy.data.meshes:
        if not mesh.users:continue
        h=hashlib.sha256()
        for v in mesh.vertices:h.update(struct.pack('<3f',*v.co))
        for p in mesh.polygons:
            h.update(struct.pack('<I',len(p.vertices)))
            for i in p.vertices:h.update(struct.pack('<I',i))
        hashes[mesh.name]=h.hexdigest()
    return {o.name:([list(r) for r in o.matrix_world],o.hide_render,hashes[o.data.name] if o.type=='MESH' else None) for o in bpy.context.scene.objects}
before=snapshot()
ctx=SimpleNamespace(root=ROOT,config=json.loads((ROOT/'config.json').read_text(encoding='utf8')))
surf=near.Terrain(ctx,base['result']['options'])
repairs=near.repair_old_leaf_creases(surf,base['result']['vegetation'])
after=snapshot();changed=[name for name,v in before.items() if after.get(name)!=v]
assert changed==['TREE_Fallen_Leaves_Ground_Litter'],changed
destination=ROOT/'scene/Fallingwater_near_terrain_candidate07b_contacts.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(destination),compress=True)
result={'status':'PASS_LOCAL_OLD_LEAF_CONTACT_REPAIR_VISUAL_NOT_RUN','candidate':str(destination),'candidate_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
        'source':str(source),'source_sha256':base['candidate_sha256'],'changed_objects':changed,'repairs':repairs,'updated_vegetation_records':base['result']['vegetation'],
        'helper_sha256':hashlib.sha256((ROOT/'scripts/near_terrain_detail.py').read_bytes()).hexdigest(),
        'scope':'Only failing old leaf components locally re-seat. Original seven-vertex leaf topology, terrain/core/trees/new99,942leaves/material/cameras/water/buildings unchanged.'}
(ROOT/'qa/near-terrain07b-contact-repair.json').write_text(json.dumps(result,indent=2),encoding='utf8')
assert hashlib.sha256(source.read_bytes()).hexdigest()==base['candidate_sha256']
print('NEAR07B_CONTACT_REPAIR',json.dumps({k:v for k,v in result.items() if k not in ('updated_vegetation_records',)}),flush=True)
