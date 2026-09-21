"""Build only five floors and six connecting thresholds on frozen07; CPU4."""
import bpy,sys,json,hashlib,array,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import main_house
from fwlib import collection,poly_prism
SOURCE=R/'scene/Fallingwater_iteration07.blend';CANDIDATE=R/'scene/Fallingwater_floor_candidate08.blend'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='bf50530009e4a93315915815473188c91d891272ef2d8e9e0169b704bd2e2f16'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4
rooms=['MAIN_L2_BATH_N','MAIN_L2_BATH_G','MAIN_L2_BATH_M','MAIN_L2_DRESSING','MAIN_L3_GALLERY']
tids=['guest_bath','master_bath','dressing_bath','hall_dressing','dressing_terrace','gallery_bath']
def fingerprints():
    out={};shared={}
    for ob in s.objects:
        h=hashlib.sha256(str(tuple(tuple(row) for row in ob.matrix_world)).encode())
        if ob.type=='MESH':
            ptr=ob.data.as_pointer()
            if ptr not in shared:
                vv=array.array('f',[0.])*(len(ob.data.vertices)*3);ob.data.vertices.foreach_get('co',vv)
                ii=array.array('i',[0])*len(ob.data.loops);ob.data.loops.foreach_get('vertex_index',ii)
                shared[ptr]=hashlib.sha256(vv.tobytes()+ii.tobytes()).digest()
            h.update(shared[ptr])
        h.update(str(tuple(m.name if m else None for m in getattr(ob.data,'materials',[]))).encode())
        out[ob.name]=h.hexdigest()
    return out
def world(ob):return [list(ob.matrix_world@v.co) for v in ob.data.vertices]
def bounds(ob):
    v=world(ob);return [[min(p[k] for p in v),max(p[k] for p in v)] for k in range(3)]
def area(p):return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1])))*.5
def inside(x,y,p):
    yes=False
    for a,b in zip(p,p[1:]+p[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:yes=not yes
    return yes
dg=bpy.context.evaluated_depsgraph_get()
def ray(p,d=(0,0,-1),distance=.5):
    hit,q,n,face,ob,_=s.ray_cast(dg,Vector(p),Vector(d),distance=distance)
    return {'hit':ob.name if hit else None,'point':list(q) if hit else None}
before=fingerprints();records=main_house.room_records();specs=[];areas={}
for rid in rooms:
    rec=next(r for r in records if r['id']==rid);p=rec['physical_floor_polygon'];old=rec['polygon'];z=rec['z']
    areas[rid]={'old_m2':area(old),'new_m2':area(p),'source_polygon':rec['physical_floor_source_polygon'],'world_polygon':p}
    specs.extend([(rid+'_slab',p,z-.22,z),(rid+'_finish',p,z,z+.022)])
for tid in tids:
    tn,rid,rr,lev,mat,probe=next(t for t in main_house.THRESHOLDS if t[0]==tid);new_rr=main_house.physical_threshold_source_rect(tid,rr)
    p=[main_house.xy(a) for a in main_house.rect(*new_rr)];z=main_house.LEVELS[lev]
    areas['threshold_'+tid]={'old_m2':area([main_house.xy(a) for a in main_house.rect(*rr)]),'new_m2':area(p),'source_rect':list(new_rr),'world_polygon':p}
    specs.extend([('MAIN_floor_threshold_'+tid,p,z-.18,z),('MAIN_floor_threshold_'+tid+'_finish',p,z,z+.022)])
names=[a[0] for a in specs];old={n:{'bounds':bounds(s.objects[n]),'vertices':world(s.objects[n])} for n in names}
door_probes=[]
for tid,rid,rr,lev,mat,path in main_house.THRESHOLDS:
    a,b=map(Vector,[main_house.xy(x) for x in path]);v=b-a;normal=Vector((-v.y,v.x)).normalized();z=main_house.LEVELS[lev]
    for off in (-.15,0,.15):
        for k in range(25):
            q=a.lerp(b,k/24)+normal*off;p=(q.x,q.y,z+.12)
            door_probes.append({'id':tid,'origin':p,'z':z,'before':ray(p)})
rebuild={}
for n,p,z0,z1 in specs:
    ob=s.objects[n];temp=poly_prism('QA_floor08_transient',p,z0,z1,ob.data.materials[0],collection('QA_FLOOR08_TRANSIENT'))
    bpy.context.view_layer.update();rebuild[n]=world(temp);ob.data=temp.data.copy();ob.matrix_world=temp.matrix_world.copy()
    ob['physical_floor_revision']='08 source-constrained closed-room perimeter and nonoverlapping doorway finish'
    bpy.data.objects.remove(temp,do_unlink=True)
bpy.data.collections.remove(bpy.data.collections['QA_FLOOR08_TRANSIENT']);bpy.context.view_layer.update()
after=fingerprints();changed=sorted(n for n in before if before[n]!=after.get(n));assert changed==sorted(names),changed
bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE));bpy.ops.wm.open_mainfile(filepath=str(CANDIDATE));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
errors={n:max(abs(a[k]-b[k]) for a,b in zip(world(s.objects[n]),rebuild[n]) for k in range(3)) for n in names};assert max(errors.values())<1e-6
for d in door_probes:
    d['after']=ray(d['origin']);oldz=d['before']['point'][2] if d['before']['point'] else None;newz=d['after']['point'][2] if d['after']['point'] else None
    old_ok=oldz is not None and abs(oldz-(d['z']+.022))<.08;new_ok=newz is not None and abs(newz-(d['z']+.022))<.08
    d['regression']=old_ok and not new_ok
perimeter=[];grid=[]
for rid in rooms:
    p=areas[rid]['world_polygon'];z=next(r['z'] for r in records if r['id']==rid);sgn=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1]))
    for edge,(a,b) in enumerate(zip(p,p[1:]+p[:1])):
        a,b=Vector(a),Vector(b);v=b-a;nn=Vector((-v.y,v.x)).normalized()*(1 if sgn>0 else -1);count=max(2,math.ceil(v.length/.15))
        for i in range(count):
            q=a+v*((i+.5)/count)+nn*.025
            if not inside(q.x,q.y,p):continue
            r=ray((q.x,q.y,z+.07));r.update(room=rid,edge=edge,xy=list(q),pass_=bool(r['point']) and abs(r['point'][2]-(z+.022))<.001);perimeter.append(r)
    xlo,xhi=min(a[0] for a in p),max(a[0] for a in p);ylo,yhi=min(a[1] for a in p),max(a[1] for a in p)
    for ix in range(1,19):
        for iy in range(1,25):
            q=(xlo+(xhi-xlo)*ix/19,ylo+(yhi-ylo)*iy/25)
            if not inside(*q,p):continue
            r=ray((*q,z+.07));r.update(room=rid,xy=q,pass_=bool(r['point']) and abs(r['point'][2]-(z+.022))<.001);grid.append(r)
# Evaluated existing finishes demonstrate uniqueness at the exact defect rays.
finish_bvhs={};changed_verts=[];changed_faces=[]
for ob in s.objects:
    if ob.type!='MESH' or not (ob.name in names or (ob.name.startswith('MAIN_') and ob.name.endswith('_finish'))):continue
    e=ob.evaluated_get(dg);m=e.to_mesh();vv=[e.matrix_world@v.co for v in m.vertices];ff=[tuple(f.vertices) for f in m.polygons]
    if ob.name.endswith('_finish'):finish_bvhs[ob.name]=BVHTree.FromPolygons(vv,ff)
    if ob.name in names:
        offset=len(changed_verts);changed_verts+=vv;changed_faces.extend(tuple(offset+i for i in f) for f in ff)
    e.to_mesh_clear()
s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100
probe=json.loads((R/'qa/floor08-probe.json').read_text());pixel_results=[]
for oldp in probe['pixels']:
    name=oldp['camera'];px,py=oldp['pixel'];cam=s.objects[name];co=cam.data.view_frame(scene=s);xmin,xmax=min(v.x for v in co),max(v.x for v in co);ymin,ymax=min(v.y for v in co),max(v.y for v in co)
    d=(cam.matrix_world.to_quaternion()@Vector((xmin+(px+.5)/640*(xmax-xmin),ymax-(py+.5)/360*(ymax-ymin),co[0].z))).normalized()
    result=ray(cam.matrix_world.translation,d,100);ideal=oldp['floor_intersection'];surfaces=[]
    for nm,bvh in finish_bvhs.items():
        p,n,f,dist=bvh.ray_cast(Vector((ideal[0],ideal[1],ideal[2]+.08)),Vector((0,0,-1)),.16)
        if p is not None and abs(p.z-ideal[2])<.001:surfaces.append(nm)
    control=(name=='CAM_MAIN_L2_BATH_N_A' and (px,py)==(182,261)) or (name=='CAM_MAIN_L3_GALLERY_B' and (px,py)==(395,277))
    pixel_results.append({'camera':name,'pixel':[px,py],'before':oldp['first'],'after':result,'floor_surfaces':surfaces,'control_only':control,'pass_':control or (len(surfaces)==1 and result['hit'] in surfaces)})
# Main and supplemental routes stay frozen. Only collision introduced by the
# modified surfaces is checked here; full scene traversal remains separate.
bvh=BVHTree.FromPolygons(changed_verts,changed_faces);route=json.loads((R/'data/tour-route.json').read_text());body_count=0;body_hits=[];route_floors=[]
def body(q,label):
    global body_count
    for dz in (0,-.65,-1.3):
        p=Vector(q)+Vector((0,0,dz));hit=bvh.find_nearest(p,.18);body_count+=1
        if hit[0] is not None:body_hits.append({'label':label,'xyz':list(p),'distance':hit[3]})
for ob in s.objects:
    if ob.type=='CAMERA':body(ob.matrix_world.translation,ob.name)
for seg in route['main_segments']+route['supplemental_segments']:
    relevant=next((r for r in seg.get('room_ids',[]) if r in rooms),None)
    for i,(a,b) in enumerate(zip(seg['points'],seg['points'][1:])):
        a,b=Vector(a),Vector(b);count=max(2,math.ceil((b-a).length/.1))
        for k in range(count+1):
            q=a.lerp(b,k/count);body(q,f"{seg['id']}:{i}:{k}")
            if relevant:
                z=next(r['z'] for r in records if r['id']==relevant);r=ray((q.x,q.y,z+.1));r.update(segment=seg['id'],xyz=list(q),pass_=bool(r['point']) and abs(r['point'][2]-(z+.022))<.08);route_floors.append(r)
outside=[]
for px,py,z in [(370,280,5.26415),(397,280,5.26415),(425,280,5.26415),(277,218,2.8448),(248,225,2.8448),(235,316,2.8448),(445,345,2.8448)]:
    q=main_house.xy((px,py));r=ray((*q,z+.10));r.update(source_px=[px,py],not_added=r['hit'] not in names);outside.append(r)
report={'status':'PENDING','source_scene':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'candidate':str(CANDIDATE),'candidate_sha256':hashlib.sha256(CANDIDATE.read_bytes()).hexdigest(),'source_script_sha256':hashlib.sha256((R/'scripts/main_house.py').read_bytes()).hexdigest(),'changed_objects':changed,'all_non_targets_identical':set(before)==set(after) and changed==sorted(names),'source_rebuild_error_m':errors,'areas':areas,'old':old,'new_bounds':{n:bounds(s.objects[n]) for n in names},'perimeter':perimeter,'grid':grid,'doors':door_probes,'pixels':pixel_results,'body_samples':body_count,'body_hits':body_hits,'route_floor':route_floors,'route_source_sha256':hashlib.sha256((R/'data/tour-route.json').read_bytes()).hexdigest(),'outside':outside}
counts={'perimeter':len(perimeter),'perimeter_fail':sum(not r['pass_'] for r in perimeter),'grid':len(grid),'grid_fail':sum(not r['pass_'] for r in grid),'door_points':len(door_probes),'door_regressions':sum(r['regression'] for r in door_probes),'pixel_defects':sum(not r['control_only'] for r in pixel_results),'pixel_fails':sum(not r['pass_'] for r in pixel_results),'route_floor_samples':len(route_floors),'route_floor_fails':sum(not r['pass_'] for r in route_floors),'body_hits':len(body_hits),'outside_fails':sum(not r['not_added'] for r in outside)}
report['counts']=counts;report['status']='PASS_LOCAL_FLOOR08_NOT_VISUAL_ACCEPTANCE' if not any(v for k,v in counts.items() if k.endswith(('_fail','_fails','_regressions','_hits'))) else 'FAIL_LOCAL_FLOOR08'
(R/'qa/floor08-candidate-check.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:report[k] for k in ('status','candidate_sha256','source_script_sha256','counts','body_samples')},indent=2))
