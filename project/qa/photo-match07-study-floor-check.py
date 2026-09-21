"""Only replace Study slab/finish in the frozen west-band candidate; CPU4, no render."""
import bpy,sys,json,hashlib,array,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import main_house
from fwlib import collection,poly_prism
source=R/'scene/Fallingwater_west_band_candidate07.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='e16bd51e05bae48ad26b7c902a2e8a8be8617bbea8b7be273005a1d1d149c4be'
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4
names=['MAIN_L3_STUDY_slab','MAIN_L3_STUDY_finish']
def fingerprints():
    out={};shared={}
    for ob in s.objects:
        h=hashlib.sha256(str(tuple(tuple(r) for r in ob.matrix_world)).encode())
        if ob.type=='MESH':
            key=ob.data.as_pointer()
            if key not in shared:
                c=array.array('f',[0.])*(len(ob.data.vertices)*3);ob.data.vertices.foreach_get('co',c)
                p=array.array('i',[0])*len(ob.data.loops);ob.data.loops.foreach_get('vertex_index',p)
                shared[key]=hashlib.sha256(c.tobytes()+p.tobytes()).digest()
            h.update(shared[key])
        h.update(str(tuple(m.name if m else None for m in getattr(ob.data,'materials',[]))).encode());out[ob.name]=h.hexdigest()
    return out
def world(o):return [list(o.matrix_world@v.co) for v in o.data.vertices]
def bounds(o):
    vv=world(o);return [[min(v[k] for v in vv),max(v[k] for v in vv)] for k in range(3)]
def area(poly):return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1])))/2
def inside(x,y,poly):
    odd=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:odd=not odd
    return odd
before=fingerprints();old={n:{'vertices':world(bpy.data.objects[n]),'bounds':bounds(bpy.data.objects[n])} for n in names}
poly=[main_house.xy(p) for p in main_house.study_floor_source_polygon()]
old_poly=[main_house.xy(p) for p in next(r for r in main_house.ROOM_SPECS if r[0]=='MAIN_L3_STUDY')[3]]
target=(R/'scene/Fallingwater_study_floor_candidate07.blend')
z=main_house.LEVELS['L3'];rebuild={}
for n,z0,z1 in [(names[0],z-.22,z),(names[1],z,z+.022)]:
    ob=bpy.data.objects[n];temp=poly_prism('QA_Study_source_rebuild',poly,z0,z1,ob.data.materials[0],collection('QA_STUDY_TRANSIENT'))
    bpy.context.view_layer.update();rebuild[n]=world(temp);ob.data=temp.data.copy();ob.matrix_world=temp.matrix_world.copy()
    ob['physical_floor_revision']='07 actual inner wall faces + stepped chimney and window return; semantic polygon remains inset'
    bpy.data.objects.remove(temp,do_unlink=True)
bpy.data.collections.remove(bpy.data.collections['QA_STUDY_TRANSIENT'])
bpy.context.view_layer.update();after=fingerprints();changed=sorted(n for n in before if before[n]!=after.get(n));assert changed==sorted(names),changed
bpy.ops.wm.save_as_mainfile(filepath=str(target));bpy.ops.wm.open_mainfile(filepath=str(target));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
rebuild_errors={n:max(abs(a[k]-b[k]) for a,b in zip(world(bpy.data.objects[n]),rebuild[n]) for k in range(3)) for n in names}
assert max(rebuild_errors.values())<1.e-6
def ray(origin,direction=(0,0,-1),distance=1.):
    hit,p,n,face,ob,_=s.ray_cast(dg,Vector(origin),Vector(direction),distance=distance)
    return {'hit':ob.name if hit else None,'point':list(p) if hit else None,'normal':list(n) if hit else None,'face':face if hit else None}

# Sample the new polygon's interior side every <=0.15m, plus interior grid.
# Overlap slivers inside walls are not falsely tested as occupied floor.
perimeter=[]
signed=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))
for edge,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
    v=Vector((b[0]-a[0],b[1]-a[1]));length=v.length;normal=Vector((-v.y,v.x)).normalized()*(1 if signed>0 else -1)
    for j in range(max(2,math.ceil(length/.15))):
        t=(j+.5)/max(2,math.ceil(length/.15));q=Vector(a)+v*t+normal*.025
        if not inside(q.x,q.y,poly):continue
        r=ray((q.x,q.y,z+.07),distance=.5);r.update(edge=edge,xy=list(q),status='PASS' if r['hit']=='MAIN_L3_STUDY_finish' and abs(r['point'][2]-(z+.022))<.001 else 'FAIL');perimeter.append(r)
grid=[]
for ix in range(1,21):
    for iy in range(1,29):
        x=-3.987+ix*(3.6772/21);y=11.2822+iy*(5.1331/29)
        if not inside(x,y,poly):continue
        r=ray((x,y,z+.06),distance=.4)
        if r['hit'] and abs(r['point'][2]-(z+.022))<.001:grid.append({'xy':[x,y],'status':'PASS','hit':r['hit']})
        else:grid.append({'xy':[x,y],'status':'FAIL',**r})

# Source camera's exact prior bad pixel; use its physical ray to meet the new
# floor, not the old below-floor hit's different XY coordinate.
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
cam=s.objects['CAM_MAIN_L3_STUDY_B'];frame=cam.data.view_frame(scene=s);xlo,xhi=min(p.x for p in frame),max(p.x for p in frame);ylo,yhi=min(p.y for p in frame),max(p.y for p in frame)
pixel=(850,507);direction=cam.matrix_world.to_quaternion()@Vector((xlo+(pixel[0]+.5)/960*(xhi-xlo),yhi-(pixel[1]+.5)/540*(yhi-ylo),frame[0].z))
bad_pixel=ray(cam.matrix_world.translation,direction.normalized(),100);bad_pixel['pixel']=list(pixel);bad_pixel['status']='PASS' if bad_pixel['hit']==names[1] and abs(bad_pixel['point'][2]-(z+.022))<.001 else 'FAIL'

# The single room access joins its unchanged gallery threshold without level
# jumps. Test floor on both sides, with no sample placed inside a wall.
door=[]
for py in (282,291,300):
    for px in [315+i*.5 for i in range(45)]:
        x,y=main_house.xy((px,py));r=ray((x,y,z+.10),distance=.4)
        r.update(source_px=[px,py],status='PASS' if r['hit'] and abs(r['point'][2]-(z+.022))<.002 else 'FAIL');door.append(r)

# Prove two unchanged pre-existing true voids outside this bounded Study have
# not acquired a Study floor: gallery stair and external spiral/roof area.
outside=[]
for px,py in [(370,280),(397,280),(425,280),(235,280),(230,300)]:
    x,y=main_house.xy((px,py));r=ray((x,y,z+.1),distance=.5);r.update(source_px=[px,py],not_filled_by_study=r['hit'] not in names);outside.append(r)
report={'status':'PASS_LOCAL_FLOOR_CLOSURE_NOT_VISUAL_ACCEPTANCE' if all(r['status']=='PASS' for r in perimeter+grid+door+[bad_pixel]) and all(r['not_filled_by_study'] for r in outside) else 'FAIL_LOCAL_FLOOR_CLOSURE','source_scene':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidate':str(target),'candidate_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'source_script_sha256':hashlib.sha256((R/'scripts/main_house.py').read_bytes()).hexdigest(),'physical_source_polygon':main_house.study_floor_source_polygon(),'physical_world_polygon':poly,'semantic_room_polygon_retained':old_poly,'area_before_m2':area(old_poly),'area_after_m2':area(poly),'changed_objects':changed,'non_target_fingerprints_identical':set(before)==set(after) and changed==sorted(names),'source_rebuild_error_m':rebuild_errors,'old':old,'new':{n:{'vertices':world(bpy.data.objects[n]),'bounds':bounds(bpy.data.objects[n])} for n in names},'counts':{'perimeter':len(perimeter),'perimeter_fail':sum(r['status']=='FAIL' for r in perimeter),'interior_grid':len(grid),'interior_grid_fail':sum(r['status']=='FAIL' for r in grid),'door_floor':len(door),'door_floor_fail':sum(r['status']=='FAIL' for r in door)},'perimeter':perimeter,'grid':grid,'door_floor':door,'prior_bad_pixel':bad_pixel,'outside_void_checks':outside,'limitations':['Only floor geometry changed; no wall, door, furniture, source camera or lighting edits.','Floor visibility/bright strips need actual render; most prior strip pixels already hit cork, so this does not claim all brightness fixed.','Semantic census floor remains inset and is explicitly distinguished from physical slab/finish.']}
(R/'qa/photo-match07-study-floor-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ('status','candidate_sha256','area_before_m2','area_after_m2','changed_objects','non_target_fingerprints_identical','counts','prior_bad_pixel')},indent=2))
