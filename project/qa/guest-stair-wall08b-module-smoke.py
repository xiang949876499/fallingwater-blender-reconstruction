"""Fresh-process guest module integration smoke; no scene save/render."""
import bpy,json,sys,hashlib
from pathlib import Path
from types import SimpleNamespace
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import fwlib,materials,guest_house
bpy.ops.wm.read_factory_settings(use_empty=True)
ctx=SimpleNamespace(root=ROOT,config=json.loads((ROOT/'config.json').read_text(encoding='utf-8')),mats=materials.build_materials(),collection=fwlib.collection)
rooms=guest_house.build(ctx);bpy.context.view_layer.update()
wall=bpy.data.objects.get('GUEST_LAUNDRY_DESCENT_outer_retaining_wall')
assert wall is not None
vv=[wall.matrix_world@Vector(v) for v in wall.bound_box]
bounds=[[min(p[k] for p in vv),max(p[k] for p in vv)] for k in range(3)]
candidate=json.loads((ROOT/'qa/guest-stair-wall08b-check.json').read_text(encoding='utf-8'))
treads=[o.name for o in bpy.data.objects if o.name.startswith('GUEST_LAUNDRY_DESCENT_tread_')]
outer_rails=[o.name for o in bpy.data.objects if o.name=='GUEST_LAUNDRY_DESCENT_handrail_-1' or o.name.startswith('GUEST_LAUNDRY_DESCENT_baluster_-1_')]
inner_rails=[o.name for o in bpy.data.objects if o.name=='GUEST_LAUNDRY_DESCENT_handrail_1' or o.name.startswith('GUEST_LAUNDRY_DESCENT_baluster_1_')]
ok=bounds==candidate['wall_bounds'] and len(treads)==14 and not outer_rails and len(inner_rails)==4
result={'status':'PASS' if ok else 'FAIL','source_module_sha256':hashlib.sha256(Path(guest_house.__file__).read_bytes()).hexdigest(),
    'fresh_guest_build':True,'room_count':len(rooms),'object_count':len(bpy.data.objects),'wall_bounds':bounds,
    'candidate_bounds_match':bounds==candidate['wall_bounds'],'treads':treads,'outer_rails':outer_rails,'inner_rails':inner_rails,
    'wall_custom_properties':dict(wall.items()),'scope':'Module wiring only; does not replace complete-world navigation or visual evidence'}
(ROOT/'qa/guest-stair-wall08b-module-smoke.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('MODULE_SMOKE',json.dumps(result),flush=True)
assert ok,'Guest module integration failure'
