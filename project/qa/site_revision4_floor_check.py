import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(r'D:\zx\test\project')
terrain=bpy.data.objects['SITE_Continuous_BearRun_Terrain']
bvh=BVHTree.FromObject(terrain,bpy.context.evaluated_depsgraph_get())
main=json.loads((root/'data'/'main_house.json').read_text(encoding='utf8'))
guest=json.loads((root/'data'/'guest_house.json').read_text(encoding='utf8'))
config=json.loads((root/'config.json').read_text(encoding='utf8'))
reg=dict(guest['registration']);reg.update(config.get('guest_registration',{}))
ox,oy,oz=reg['world_origin'];px,py=reg['origin_px'];sx,sy=reg['meters_per_pixel']
rooms=[{'id':r['id'],'polygon':r['polygon'],'floor_z':r['z']} for r in main['rooms']]
for room in guest['rooms']:
    points=[(ox+(x-px)*sx,oy+(py-y)*sy) for x,y in room['polygon']]
    z=oz+guest['levels'][room['level']]['offset']
    rooms.append({'id':room['id'],'polygon':points,'floor_z':z})
def inside(x,y,poly):
    hit=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
    return hit
report=[]
for room in rooms:
    poly=room['polygon'];xs=[p[0] for p in poly];ys=[p[1] for p in poly];samples=[]
    for i in range(7):
        for j in range(7):
            x=min(xs)+(max(xs)-min(xs))*(.06+i*.88/6)
            y=min(ys)+(max(ys)-min(ys))*(.06+j*.88/6)
            if not inside(x,y,poly):continue
            loc,_,_,_=bvh.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),400)
            samples.append({'xy':[x,y],'clearance_m':room['floor_z']-loc.z if loc else None})
    values=[s['clearance_m'] for s in samples if s['clearance_m'] is not None]
    report.append({'id':room['id'],'samples':len(samples),'minimum_soil_below_floor_m':min(values) if values else None,
                   'soil_above_floor_samples':sum(v<0 for v in values)})
result={'method':'49-point grid clipped to actual room polygon; vertical ray against generated site triangles; new dimensions from final main/guest JSON',
        'rooms':report,'soil_above_floor_samples':sum(r['soil_above_floor_samples'] for r in report),
        'minimum_clearance_m':min(r['minimum_soil_below_floor_m'] for r in report if r['minimum_soil_below_floor_m'] is not None),
        'source_blend':bpy.data.filepath,'visual_status':'NOT_RUN; geometrical terrain-to-floor clearance only'}
(root/'qa'/'site_revision4_floor_clearance.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print('SITE_REV4_FLOOR',json.dumps(result))
