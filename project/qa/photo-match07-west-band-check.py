"""Source-derived three-object candidate, fresh background process only; no render."""
import bpy,sys,json,hashlib,ast,math,array,os
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
import main_house
from fwlib import segment,collection
print('OWNED_CHECK_PID',os.getpid(),flush=True)
source=R/'scene/Fallingwater_iteration06.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='172b76340d1224a2b98f415b21042d19ad7fba4d849543d7156beb17e5fcf055'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=4
target_names=['MAIN_L1_west_parapet_0','MAIN_L1_west_parapet_1','MAIN_L1_south_fascia_0']

def baseworld(ob):return [list(ob.matrix_world@v.co) for v in ob.data.vertices]
def bounds(ob,evaluated=False):
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()) if evaluated else ob
    vv=[ev.matrix_world@v.co for v in ev.data.vertices]
    return [[min(p[i] for p in vv),max(p[i] for p in vv)] for i in range(3)]
def fingerprints():
    result={};shared={}
    for ob in scene.objects:
        h=hashlib.sha256();h.update(str(tuple(tuple(r) for r in ob.matrix_world)).encode())
        if ob.type=='MESH':
            key=ob.data.as_pointer()
            if key not in shared:
                mh=hashlib.sha256()
                co=array.array('f',[0.])*(len(ob.data.vertices)*3);ob.data.vertices.foreach_get('co',co)
                loops=array.array('i',[0])*len(ob.data.loops);ob.data.loops.foreach_get('vertex_index',loops)
                mh.update(co.tobytes());mh.update(loops.tobytes());shared[key]=mh.digest()
            h.update(shared[key])
        h.update(str(tuple(m.name if m else None for m in getattr(ob.data,'materials',[]))).encode())
        result[ob.name]=h.hexdigest()
    return result
before_fingerprint=fingerprints()
print('BEFORE_FINGERPRINT_DONE',len(before_fingerprint),flush=True)
before={n:{'base':baseworld(bpy.data.objects[n]),'bounds':bounds(bpy.data.objects[n],True),'modifiers':[(m.type,getattr(m,'width',None),getattr(m,'segments',None)) for m in bpy.data.objects[n].modifiers]} for n in target_names}

# Take the exact authored chain calls from the changed source, rather than
# duplicating manually guessed coordinates in this candidate builder.
tree=ast.parse((R/'scripts/main_house.py').read_text(encoding='utf-8'))
calls={}
for node in ast.walk(tree):
    if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='chain' and node.args:
        try:args=[ast.literal_eval(a) for a in node.args]
        except (ValueError,TypeError):continue
        if args[0] in ('MAIN_L1_west_parapet','MAIN_L1_south_fascia'):calls[args[0]]=args
assert len(calls)==2
rebuild_witness={}
for args in calls.values():
    name,points,z0,z1,thickness,mat_key=args
    for i,(a,b) in enumerate(zip(points,points[1:])):
        n=f'{name}_{i}';old=bpy.data.objects[n]
        tmp=segment('QA_WEST_BAND_REBUILD',main_house.xy(a),main_house.xy(b),z0,z1,thickness,old.data.materials[0],collection('QA_WEST_BAND_TRANSIENT'))
        bpy.context.view_layer.update()
        desired=baseworld(tmp)
        assert max(abs(p[k]-q[k]) for p,q in zip(before[n]['base'],desired) for k in (0,1))<1.e-6
        old.data=tmp.data.copy();old.matrix_world=tmp.matrix_world.copy()
        old['band_revision']='07 source main07/08/10: actual exposed band; no camera fit'
        old['band_source_uncertainty_m']=.055
        bpy.data.objects.remove(tmp,do_unlink=True)
        rebuild_witness[n]=desired
empty=bpy.data.collections.get('QA_WEST_BAND_TRANSIENT')
if empty:bpy.data.collections.remove(empty)
bpy.context.view_layer.update()
after_fingerprint=fingerprints();changed=sorted(n for n in before_fingerprint if before_fingerprint[n]!=after_fingerprint.get(n))
assert changed==sorted(target_names),(changed,target_names)
candidate=R/'scene/Fallingwater_west_band_candidate07.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(candidate))
bpy.ops.wm.open_mainfile(filepath=str(candidate));scene=bpy.context.scene
errors={n:max(abs(p[k]-q[k]) for p,q in zip(baseworld(bpy.data.objects[n]),rebuild_witness[n]) for k in range(3)) for n in target_names}
assert max(errors.values())<1.e-6
after={n:{'bounds':bounds(bpy.data.objects[n],True),'modifiers':[(m.type,getattr(m,'width',None),getattr(m,'segments',None)) for m in bpy.data.objects[n].modifiers]} for n in target_names}
assert all(after[n]['modifiers']==before[n]['modifiers'] for n in target_names)

# Geometry-only local passage checks use original physical architecture and
# furniture, excluding decorative foliage. They are not full navigation QA.
verts=[];faces=[]
for ob in scene.objects:
    if ob.type!='MESH' or not (ob.name.startswith(('MAIN_','FW_DETAIL_MAIN_','FW_FURN_MAIN_'))):continue
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();base=len(verts)
    verts.extend(ev.matrix_world@v.co for v in me.vertices);faces.extend(tuple(base+j for j in p.vertices) for p in me.polygons);ev.to_mesh_clear()
arch=BVHTree.FromPolygons(verts,faces,all_triangles=False)
paths=[]
for y in (1.30,3.65):
    rows=[]
    for i in range(21):
        x=-4.25+i*3.75/20
        ground=arch.ray_cast(Vector((x,y,.10)),Vector((0,0,-1)),.22)
        support=ground[0] is not None and abs(ground[0].z-.022)<.04
        blocked=[]
        for z in (.25,1.,1.80):
            for vx,vy in ((1,0),(-1,0),(0,1),(0,-1)):
                hit=arch.ray_cast(Vector((x,y,z)),Vector((vx,vy,0)),.18)
                if hit[0] is not None:blocked.append({'point':list(hit[0]),'z':z})
        rows.append({'point':[x,y,.022],'floor_support':support,'body_blockers':blocked,'status':'PASS' if support and not blocked else 'FAIL'})
    paths.append({'y':y,'scope':'Inside West terrace, not entire glazed doorway','samples':rows,'status':'PASS' if all(q['status']=='PASS' for q in rows) else 'FAIL'})
# Camera body cannot newly intersect the changed exterior band without being
# within 0.18m of one of these evaluated surfaces; each existing view is checked.
newv=[];newf=[]
for n in target_names:
    ev=bpy.data.objects[n].evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();base=len(newv)
    newv.extend(ev.matrix_world@v.co for v in me.vertices);newf.extend(tuple(base+j for j in p.vertices) for p in me.polygons);ev.to_mesh_clear()
changed_bvh=BVHTree.FromPolygons(newv,newf,all_triangles=False)
cam_hits=[];camera_count=0
for ob in scene.objects:
    if ob.type!='CAMERA':continue
    camera_count+=1
    for dz in (0,-.65,-1.3):
        p=ob.matrix_world.translation+Vector((0,0,dz));hit=changed_bvh.find_nearest(p,.18)
        if hit[0] is not None:cam_hits.append({'camera':ob.name,'body_dz':dz,'distance':hit[3]})
report={'status':'LOCAL_GEOMETRY_PASS_NOT_VISUAL_ACCEPTANCE' if all(p['status']=='PASS' for p in paths) and not cam_hits else 'LOCAL_GEOMETRY_REVIEW_REQUIRED','source_scene':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidate_scene':str(candidate),'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'source_script_sha256':hashlib.sha256((R/'scripts/main_house.py').read_bytes()).hexdigest(),'exact_source_calls':calls,'changed_objects':changed,'object_count_before':len(before_fingerprint),'object_count_after':len(after_fingerprint),'non_target_objects_unchanged':set(before_fingerprint)==set(after_fingerprint) and changed==sorted(target_names),'base_xy_preserved':True,'rounded_edge_modifiers_preserved':True,'before':before,'after':after,'saved_reopened_source_rebuild_max_world_error_m':errors,'west_terrace_local_paths':paths,'existing_camera_body_checks':{'cameras':camera_count,'samples_per_camera':3,'radius_m':.18,'hits':cam_hits},'limits':['No scene render. No source camera promoted. Prior two photo diagnostics remain unverified/failing.','Central living-window upstand height/footprint still separate unresolved component; no tall wall across entire south frontage.','Other 07 modifications live in source modules; this frozen06-derived candidate changes only these 3 objects.']}
(R/'qa/photo-match07-west-band-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ('status','candidate_sha256','changed_objects','non_target_objects_unchanged','saved_reopened_source_rebuild_max_world_error_m','existing_camera_body_checks')},indent=2))
