import bpy,sys,json,math,hashlib
from pathlib import Path
from types import SimpleNamespace
from mathutils import Vector
root=Path('D:/zx/test/project');sys.path.insert(0,str(root/'scripts'))
from fwlib import collection
from materials import build_materials
import guest_house
bpy.ops.wm.read_factory_settings(use_empty=True)
ctx=SimpleNamespace(root=root,mats=build_materials(),collection=collection,config=json.loads((root/'config.json').read_text(encoding='utf-8')))
rooms=guest_house.build(ctx);bpy.context.view_layer.update()
scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=4
source=root/'qa/guest-iteration05-module.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(source))
(root/'qa/guest-iteration05-rooms.json').write_text(json.dumps(rooms,ensure_ascii=False,indent=2),encoding='utf-8')
s=(root/'qa/guest-dimensions-measured-extract.py').read_text(encoding='utf-8').replace("root/'scene/Fallingwater_working.blend'","root/'qa/guest-iteration05-module.blend'").replace('guest-dimensions-measured-projection.json','guest-iteration05-projection.json').replace('guest-dimensions-measured.json','guest-iteration05-dimensions.json').replace('saved iteration03','fresh iteration05 module')
exec(compile(s,'guest-iteration05-dimension-regression','exec'),{})
s=(root/'qa/guest-geometry-clearance-check.py').read_text(encoding='utf-8').replace('guest-geometry-clearance-report.json','guest-iteration05-upper-clearance.json')
exec(compile(s,'guest-iteration05-upper-clearance','exec'),{})
data=json.loads((root/'data/guest_house.json').read_text(encoding='utf-8'));reg=ctx.config['guest_actual_registration'];sx,sy=reg['meters_per_pixel'];ox,oy=reg['origin_px'];wx,wy,gz=reg['world_origin']
def p(x,y):return Vector((wx+(x-ox)*sx,wy+(oy-y)*sy))
scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
def ray(q,v,length):
    hit,loc,normal,idx,obj,mat=scene.ray_cast(deps,Vector(q),Vector(v),distance=length)
    return {'hit':obj.name if hit else None,'point':list(loc) if hit else None,'distance':(loc-Vector(q)).length if hit else None}
doors=[]
ids=['GUEST_L1_CHAUFFEUR_EAST','GUEST_L2_UPPER_ROOM_EAST','GUEST_L1_BED_EAST','GUEST_L1_BOILER_WEST','GUEST_B1_BASE_EAST','GUEST_B1_BASE_BATH_EAST','GUEST_L1_BATH_NORTH_TUB']
for wall in data['walls']:
    if wall['id'] not in ids:continue
    a,b=p(*wall['a']),p(*wall['b']);d=b-a;v=d.normalized();n=Vector((-v.y,v.x));z=gz+data['levels'][wall['level']]['offset'];thick=wall.get('thickness',.29)
    for i,op in enumerate(wall.get('openings',[])):
        if op['type']!='door' or (wall['id']=='GUEST_L2_UPPER_ROOM_EAST' and i!=0):continue
        mid=a+d*sum(op['span'])/2;body=[];ground=[]
        for side in [-.24,0,.24]:
            for h in [.3,.9,1.70,1.94]:
                q=mid+v*side-n*(thick/2+.035);r=ray((*q,z+h),(*n,0),thick+.07);r.update(lateral=side,height=h,status='PASS' if not r['hit'] else 'FAIL');body.append(r)
        if wall['id'] in ids[:2]:
            for advance in [-.38,0,.38]:
                for side in [-.18,0,.18]:
                    q=mid+n*advance+v*side;r=ray((*q,z+.06),(0,0,-1),.15);r.update(xy=list(q),status='PASS' if r['hit'] and abs(r['point'][2]-z)<.025 else 'FAIL');ground.append(r)
        doors.append({'wall':wall['id'],'opening':i,'center':[*mid,z],'body':body,'ground':ground,'status':'PASS' if all(t['status']=='PASS' for t in body+ground) else 'FAIL'})
# Existing descent now has an accurately restored upper vestibule overhead.
stair=[]
for i in range(14):
    y=402+(366-402)*(i+.5)/14;z=gz-2.36*(i+1)/14
    for side in [-.25,0,.25]:
        q=p(294+side/sx,y);down=ray((*q,z+.035),(0,0,-1),.1);up=ray((*q,z+.035),(0,0,1),5)
        clear=up['point'][2]-z if up['hit'] else None
        stair.append({'tread':i,'side':side,'xy':list(q),'ground':down,'overhead':up,'clearance_m':clear,'status':'PASS' if down['hit'] and (clear is None or clear>=1.95) else 'FAIL'})
pool=[]
for o in scene.objects:
    if not o.name.startswith('GUEST_POOL_coping_ascent_tread_'):continue
    coords=[o.matrix_world@v.co for v in o.data.vertices];lo=Vector(tuple(min(v[k] for v in coords) for k in range(3)));hi=Vector(tuple(max(v[k] for v in coords) for k in range(3)))
    for side in [-.3,0,.3]:
        q=((lo.x+hi.x)/2,(lo.y+hi.y)/2+side,hi.z+.04);hit=ray(q,(0,0,-1),.1)
        pool.append({'tread':o.name,'side':side,'expected_z':hi.z,'first_surface':hit,'status':'PASS' if hit['hit']==o.name and abs(hit['point'][2]-hi.z)<.01 else 'FAIL'})
f=data['fireplace_detail'];x0,y0,x1,y1=f['source_bounds_px'];z=gz+(f['hearth_top_m']+f['opening_head_m'])/2
west,east=p(x0,(y0+y1)/2),p(x1,(y0+y1)/2);north,south=p((x0+x1)/2,y0),p((x0+x1)/2,y1)
fire=[]
for label,q,v,limit in [('east_open_to_west_back',(east.x+.10,east.y,z),(-1,0,0),1.5),('south_open_to_north_back',(south.x,south.y-.10,z),(0,1,0),1.5)]:
    r=ray(q,v,limit);r.update(test=label,origin=q,status='PASS' if r['hit'] and ('firebrick' in r['hit'] or '_back' in r['hit'] or 'north_mass' in r['hit']) and r['distance']>.55 else 'FAIL');fire.append(r)
center=p((x0+x1)/2,(y0+y1)/2)
for label,v,name in [('hearth',(0,0,-1),'GUEST_FIREPLACE_hearth'),('hood',(0,0,1),'GUEST_FIREPLACE_corner_hood')]:
    r=ray((*center,z),v,1.5);r.update(test=label,status='PASS' if r['hit']==name else 'FAIL');fire.append(r)
report={'scope':'Fresh guest-only module. Full iteration05 integrated 61 adjacency and 120 cameras require retest.','scene_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'doors':doors,'laundry_descent':stair,'pool_dry_stairs':pool,'fireplace_real_cavity':fire,'counts':{'door_pass':sum(r['status']=='PASS' for r in doors),'door_total':len(doors),'laundry_pass':sum(r['status']=='PASS' for r in stair),'pool_pass':sum(r['status']=='PASS' for r in pool),'fireplace_pass':sum(r['status']=='PASS' for r in fire)}}
(root/'qa/guest-iteration05-geometry.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('ITERATION05_GEOMETRY',json.dumps(report['counts']))
for k in ['doors','laundry_descent','pool_dry_stairs','fireplace_real_cavity']:
    for r in report[k]:
        if r['status']=='FAIL':print('FAIL',k,json.dumps(r))
