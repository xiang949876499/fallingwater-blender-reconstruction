"""Furnishings-only Blender smoke test; avoids architecture/landscape rebuild."""
import sys,json,math
from pathlib import Path
from types import SimpleNamespace
import bpy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import fwlib,materials,furnishings

for obj in list(bpy.data.objects): bpy.data.objects.remove(obj,do_unlink=True)
main=json.loads((ROOT/'data/main_house.json').read_text(encoding='utf-8'))['rooms']
data=json.loads((ROOT/'data/guest_house.json').read_text(encoding='utf-8'))
reg=data['registration']; origin=reg['origin_px']; scale=reg['meters_per_pixel']; world=reg['world_origin']
def xy(p): return [world[0]+(p[0]-origin[0])*scale[0],world[1]+(origin[1]-p[1])*scale[1]]
guest=[]
for src in data['rooms']:
    r=dict(src);r['building']='GUEST';r['z']=world[2]+data['levels'][r['level']]['offset']
    r['height']=data['levels'][r['level']]['height'];r['polygon']=[xy(p) for p in r['polygon']]
    r['center']=[*xy(src['center']),r['z']];r['entry']=[*xy(src['entry']),r['z']]
    r['furniture']=[dict(p,center=[*xy(p['center']),r['z']+p.get('z_offset',0)]) for p in src.get('furniture',[])]
    guest.append(r)
ctx=SimpleNamespace(root=ROOT,mats=materials.build_materials(),config={},collection=fwlib.collection)
objects=furnishings.build(ctx,main+guest)
bpy.context.view_layer.update()
stats={'status':'PASS_BUILD_NOT_VISUAL_ACCEPTANCE','objects':len(objects),'rooms':len(main+guest),
       'meshes':sum(o.type=='MESH' for o in objects),'curves':sum(o.type=='CURVE' for o in objects),
       'untagged':[o.name for o in objects if not o.get('room_id') or not o.get('reference')],
       'nonfinite':[],'materialless':[]}
for o in objects:
    if not all(math.isfinite(v) for row in o.matrix_world for v in row): stats['nonfinite'].append(o.name)
    if o.type in ('MESH','CURVE') and not len(o.data.materials): stats['materialless'].append(o.name)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'qa/interiors-smoke.blend'))
(ROOT/'qa/interiors-smoke-result.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
assert not stats['untagged'] and not stats['nonfinite'] and not stats['materialless'],stats
print(json.dumps(stats))
