"""Read-only material diagnosis of frozen integration12; no render/save."""
import bpy,json,sys,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'qa'))
import shrub08_auditlib as audit
p=R/'scene/Fallingwater_integration_candidate12a.blend';expected='50e0a8fc0bab10fdec0e0b9d26c4ef4a4c71fa56aea6401e75197787c8c0e75a'
assert hashlib.sha256(p.read_bytes()).hexdigest()==expected
bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.view_layer.update()
objects={};mats=set()
for o in bpy.context.scene.objects:
    if o.type!='MESH' or not ('MASTER' in o.name or 'master' in o.name or 'MasterSource10' in o.name):continue
    slots=[m.name if m else None for m in o.data.materials];mats.update(m for m in slots if m)
    objects[o.name]={'materials':slots,'matrix_world':[list(r) for r in o.matrix_world],'bounds':audit.bounds(o),
                     'vertices':len(o.data.vertices),'room_id':o.get('room_id'),'custom':audit.plain(dict(o.items()))}
out={'source':str(p),'sha256':expected,'objects':objects,
     'materials':{n:{'diffuse':list(bpy.data.materials[n].diffuse_color),'state':audit.node_tree_state(bpy.data.materials[n].node_tree),'custom':audit.plain(dict(bpy.data.materials[n].items()))} for n in sorted(mats)},
     'source_unchanged':hashlib.sha256(p.read_bytes()).hexdigest()==expected,'saved':False,'rendered':False}
(R/'qa/master-material13-inspect.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('MASTER13_INSPECT',len(objects),sorted(mats),flush=True)
