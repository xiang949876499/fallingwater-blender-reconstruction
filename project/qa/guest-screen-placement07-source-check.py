"""Reopen the accepted local candidate and compare a fresh source-only lounge build."""
import bpy,json,sys,hashlib
from pathlib import Path
from types import SimpleNamespace
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import furnishings,fwlib
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
room=next(r for r in rooms if r['id']=='GUEST_L1_LOUNGE')
kinds=('walnut_vertical_screen','walnut_armchair')
def signature(root):
    pts=sorted(tuple(o.matrix_world@v.co) for o in root.children if o.type=='MESH' for v in o.data.vertices)
    return {'matrix':[list(row) for row in root.matrix_world],'vertices':pts,
            'member_count':len(root.children)}
expected={k:signature(next(o for o in bpy.context.scene.objects if o.type=='EMPTY' and o.get('room_id')==room['id'] and o.get('asset_type')==k)) for k in kinds}
ctx=SimpleNamespace(root=ROOT,config={},mats={m.name[3:]:m for m in bpy.data.materials if m.name.startswith('FW_')},collection=lambda name:fwlib.collection('QA_SOURCE_'+name))
owner=furnishings.Room(ctx,room)
furnishings.room_living(owner,guest=True)
bpy.context.view_layer.update()
checks=[]
for k in kinds:
    root=next(a.root for a in owner.assets if a.kind==k);got=signature(root);want=expected[k]
    same_count=len(got['vertices'])==len(want['vertices']) and got['member_count']==want['member_count']
    error=max((Vector(a)-Vector(b)).length for a,b in zip(got['vertices'],want['vertices'])) if same_count else None
    matrix_error=max(abs(a-b) for ra,rb in zip(got['matrix'],want['matrix']) for a,b in zip(ra,rb))
    checks.append({'asset':k,'root_location':list(root.location),'member_count':got['member_count'],
                   'vertex_count':len(got['vertices']),'same_count':same_count,'max_world_vertex_error_m':error,
                   'max_matrix_error':matrix_error,'pass':same_count and error<1.e-5 and matrix_error<1.e-5})
result={'source_candidate':bpy.data.filepath,'candidate_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
        'furnishings_sha256':hashlib.sha256((ROOT/'scripts/furnishings.py').read_bytes()).hexdigest(),
        'checks':checks,'status':'PASS' if all(c['pass'] for c in checks) else 'FAIL',
        'scope':'Fresh source lounge build compared against independently reopened local candidate; no saved file mutation and no render.'}
(ROOT/'qa/guest-screen-placement07-source-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('SOURCE_CHECK',json.dumps(result),flush=True)
assert result['status']=='PASS'
