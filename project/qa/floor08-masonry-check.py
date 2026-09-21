"""Source-based stepped core backing on the validated floor candidate, no render."""
import bpy,sys,json,hashlib,array,ast,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));import main_house
from fwlib import collection,poly_prism,box
SRC=R/'scene/Fallingwater_floor_candidate08.blend';OUT=R/'scene/Fallingwater_floor_core_candidate08.blend'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='95b3c1bc5cb6b8e1b98850c348fb522623bd8336c0dbeecf3d72c6951914b552'
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4
def fingerprints():
    out={};shared={}
    for ob in s.objects:
        h=hashlib.sha256(str(tuple(tuple(row) for row in ob.matrix_world)).encode())
        if ob.type=='MESH':
            ptr=ob.data.as_pointer()
            if ptr not in shared:
                a=array.array('f',[0.])*(len(ob.data.vertices)*3);ob.data.vertices.foreach_get('co',a);b=array.array('i',[0])*len(ob.data.loops);ob.data.loops.foreach_get('vertex_index',b);shared[ptr]=hashlib.sha256(a.tobytes()+b.tobytes()).digest()
            h.update(shared[ptr])
        h.update(str(tuple(m.name if m else None for m in getattr(ob.data,'materials',[]))).encode());out[ob.name]=h.hexdigest()
    return out
def world(ob):return [list(ob.matrix_world@v.co) for v in ob.data.vertices]
def bounds(ob):
    vs=world(ob);return [[min(v[k] for v in vs),max(v[k] for v in vs)] for k in range(3)]
before=fingerprints();oldnames=[n for n in before if n.startswith('MAIN_L2_core_course')];old_bounds={n:bounds(s.objects[n]) for n in oldnames};old_hearth=before['MAIN_L2_master_hearth']
coll=collection('QA_MASONRY08_REBUILD');material=s.objects[oldnames[0]].data.materials[0];generated={}
def rebuild_box(name,center,size,mat,unused_coll,bevel):
    ob=box('QA_REBUILD_'+name,center,size,mat,coll,bevel);generated[name]=ob;return ob
tree=ast.parse((R/'scripts/main_house.py').read_text(encoding='utf-8'));build=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='build');fn=next(n for n in build.body if isinstance(n,ast.FunctionDef) and n.name=='stone_courses')
env={'xy':main_house.xy,'math':math,'box':rebuild_box,'mats':{'stone':material},'masonry':coll}
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<main_house actual stone_courses>','exec'),env)
env['stone_courses']('MAIN_L2_core',(316,305),(316,381),2.8448,5.22,.62,clip_start=20*main_house.SY)
bpy.context.view_layer.update();expected={n:world(ob) for n,ob in generated.items()};deleted=[];replaced=[]
for n in oldnames:
    old=s.objects[n]
    if n not in generated:
        assert old_bounds[n][1][0]>=main_house.xy((316,325))[1]-.041
        deleted.append(n);bpy.data.objects.remove(old,do_unlink=True)
    else:
        temp=generated[n]
        if world(old)!=world(temp):
            old.data=temp.data.copy();old.matrix_world=temp.matrix_world.copy();replaced.append(n)
        bpy.data.objects.remove(temp,do_unlink=True)
bpy.data.collections.remove(coll)
back=poly_prism('MAIN_L2_core_north_backing',[main_house.xy(p) for p in main_house.core_north_backing_source_polygon()],2.8448,5.21,material,s.objects['MAIN_L2_master_hearth'].users_collection[0]);back['reference']='HABS PA-5346 sheet05 source stepped hatched core';back['evidence']='C';back['component_type']='architecture';expected[back.name]=world(back)
bpy.context.view_layer.update();after=fingerprints();changed=sorted(n for n in before if n in after and before[n]!=after[n]);removed=sorted(set(before)-set(after));added=sorted(set(after)-set(before))
assert all(n.startswith('MAIN_L2_core_course') for n in changed+removed);assert added==['MAIN_L2_core_north_backing'];assert before['MAIN_L2_master_hearth']==after['MAIN_L2_master_hearth']
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));bpy.ops.wm.open_mainfile(filepath=str(OUT));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
errors={n:max(abs(a[k]-b[k]) for a,b in zip(world(s.objects[n]),vv) for k in range(3)) for n,vv in expected.items()};assert max(errors.values())<1e-6
verts=[];faces=[]
for n in changed+added:
    ob=s.objects[n].evaluated_get(dg);m=ob.to_mesh();off=len(verts);verts.extend(ob.matrix_world@v.co for v in m.vertices);faces.extend(tuple(off+i for i in f.vertices) for f in m.polygons);ob.to_mesh_clear()
bvh=BVHTree.FromPolygons(verts,faces);s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100
cam=s.objects['CAM_MAIN_L2_CLOSET_M_B'];co=cam.data.view_frame(scene=s);xlo,xhi=min(v.x for v in co),max(v.x for v in co);ylo,yhi=min(v.y for v in co),max(v.y for v in co);pixels=[]
for x,y in [(552,166),(543,111),(538,169),(550,201),(590,93),(570,190),(510,190)]:
    d=(cam.matrix_world.to_quaternion()@Vector((xlo+(x+.5)/640*(xhi-xlo),yhi-(y+.5)/360*(yhi-ylo),co[0].z))).normalized();hit,p,n,face,ob,_=s.ray_cast(dg,cam.matrix_world.translation,d,distance=100)
    pixels.append({'pixel':[x,y],'hit':ob.name if hit else None,'point':list(p) if hit else None,'closed':hit and ob.name.startswith(('MAIN_L2_core','MAIN_L2_master_hearth'))})
# The west-facing recess remains empty until its east back, at source x325.
recess=[]
for py in (305,310,315,320):
    for z in (3.1,4.6):
        q=Vector((*main_house.xy((309,py)),z));stop=Vector((*main_house.xy((324.8,py)),z));short=bvh.ray_cast(q,Vector((1,0,0)),(stop-q).length);backhit=bvh.ray_cast(q,Vector((1,0,0)),2)
        recess.append({'source_py':py,'z':z,'mouth_clear':short[0] is None,'back_point':list(backhit[0]) if backhit[0] is not None else None,'back_at_source325':backhit[0] is not None and abs(backhit[0].x-main_house.xy((325,py))[0])<.002})
route=json.loads((R/'data/tour-route.json').read_text());body_n=0;collisions=[]
def body(q,label):
    global body_n
    for dz in (0,-.65,-1.3):
        p=Vector(q)+Vector((0,0,dz));h=bvh.find_nearest(p,.18);body_n+=1
        if h[0] is not None:collisions.append({'label':label,'point':list(p),'distance':h[3]})
for ob in s.objects:
    if ob.type=='CAMERA':body(ob.matrix_world.translation,ob.name)
for seg in route['main_segments']+route['supplemental_segments']:
    for i,(a,b) in enumerate(zip(seg['points'],seg['points'][1:])):
        a,b=Vector(a),Vector(b);n=max(2,math.ceil((b-a).length/.1))
        for k in range(n+1):body(a.lerp(b,k/n),f"{seg['id']}:{i}:{k}")
report={'status':'PASS_LOCAL_CORE08_NOT_VISUAL_ACCEPTANCE' if all(p['closed'] for p in pixels) and all(p['mouth_clear'] and p['back_at_source325'] for p in recess) and not collisions else 'FAIL_LOCAL_CORE08','source_scene_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'candidate':str(OUT),'candidate_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'source_script_sha256':hashlib.sha256((R/'scripts/main_house.py').read_bytes()).hexdigest(),'added':added,'changed':changed,'removed':removed,'changed_old_bounds':{n:old_bounds[n] for n in changed+removed},'backing_source_polygon':main_house.core_north_backing_source_polygon(),'backing_world_bounds':bounds(s.objects[added[0]]),'all_non_targets_identical':all(before[n]==after[n] for n in before if n not in changed+removed),'source_rebuild_max_error_m':max(errors.values()),'pixels':pixels,'recess':recess,'body_samples':body_n,'body_collisions':collisions,'route_source_sha256':hashlib.sha256((R/'data/tour-route.json').read_bytes()).hexdigest(),'limits':['C trace at approximately one to three source pixels; Z follows existing core and is not independently surveyed.','Masonry detail is intentionally removed only where its former straight north extension crossed the source recess.','No door/window/light/furniture/camera/route changes; full08 scene and visual acceptance remain separate.']}
(R/'qa/floor08-masonry-check.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:report[k] for k in ('status','candidate_sha256','source_script_sha256','added','changed','removed','pixels','body_samples','body_collisions')},indent=2))
