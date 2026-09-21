"""Fresh main/guest/furnishing module regression; no site, rendering or working-scene writes."""
import sys,json,math,hashlib
from pathlib import Path
from types import SimpleNamespace
import bpy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import main_house,guest_house,furnishings,tour,fwlib,materials

if bpy.data.filepath:raise RuntimeError('Use a fresh factory-startup Blender process')
for obj in list(bpy.data.objects):bpy.data.objects.remove(obj,do_unlink=True)
config=json.loads((ROOT/'config.json').read_text(encoding='utf-8'))
ctx=SimpleNamespace(root=ROOT,config=config,mats=materials.build_materials(),collection=fwlib.collection)
rooms=main_house.build(ctx)+guest_house.build(ctx)
furnishings.build(ctx,rooms)
bpy.context.view_layer.update()
fixtures=json.loads((ROOT/'qa/interiors-practical-fixtures.json').read_text(encoding='utf-8'))
probe=tour.Probe(bpy.context.scene)
tests=[]
for i in range(5):
    y=13.6443+(14.127-13.6443)*i/4
    start=[-.524,y,1.70];end=[.3668,y,1.70]
    issue=probe.segment(start,end,True)
    tests.append({'id':f'KITCHEN_NEW_DOOR_BODY_{i}','start':start,'end':end,
                  'status':'PASS' if issue is None else 'FAIL','failure':issue})
start=[-2.30,13.88565,1.70];end=[.3668,13.88565,1.70]
issue=probe.segment(start,end,True)
tests.append({'id':'KITCHEN_FULL_APPROACH','start':start,'end':end,'status':'PASS' if issue is None else 'FAIL','failure':issue})
fixture_checks=[]
for f in fixtures['fixtures']:
    light=next((o for o in bpy.context.scene.objects if o.type=='LIGHT' and o.get('asset_id')==f.get('asset')),None)
    fixture_checks.append({'room_id':f['room_id'],'status':f['status'],'light_exists':bool(light),
        'light_at_visible_bulb':bool(light and math.dist(light.matrix_world.translation,f['bulb_world_center'])<.001),
        'ceiling_support':f.get('support_object'),'lowest_above_floor_m':f.get('lowest_fixture_z',0)-f.get('floor_z',0)})
passed=all(t['status']=='PASS' for t in tests) and len(fixture_checks)==len(furnishings.PRACTICAL_FIXTURES) and all(
    f['status']=='BUILT_C_SUBSTITUTE_GEOMETRIC_SUPPORT_CHECKED' and f['light_at_visible_bulb'] for f in fixture_checks)
report={'status':'PASS_MODULE_GEOMETRY_NOT_INTEGRATED_OR_VISUAL' if passed else 'FAIL_MODULE_CHECK',
        'room_count':len(rooms),'door_tests':tests,'fixture_checks':fixture_checks,
        'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'scripts/furnishings.py',ROOT/'scripts/main_house.py',ROOT/'scripts/guest_house.py',ROOT/'data/main_house.json',ROOT/'data/guest_house.json']},
        'scope':'Independent latest modules, 4 threads, no site/render. Integrated iteration04 and actual rendered fixture quality still required.'}
(ROOT/'qa/interiors-practical-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'qa/interiors-practical-check.blend'),compress=True)
print('PRACTICAL_CHECK',json.dumps(report,ensure_ascii=False),flush=True)
