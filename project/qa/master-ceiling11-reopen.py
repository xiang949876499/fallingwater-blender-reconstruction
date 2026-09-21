"""Fresh saved11b readback; independent seam/volume/film checks, no save/render."""
import bpy,sys,json,hashlib,array,collections,math,ast
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];Q=R/'qa';sys.path.insert(0,str(R/'scripts'))
import master_navigation10 as nav
report=json.loads((Q/'master-ceiling11-build-check.json').read_text(encoding='utf-8'))
SRC=Path(report['source']);OUT=Path(report['candidate']);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(OUT)==report['candidate_sha256']
tree=ast.parse((Q/'master-ceiling11-build-check.py').read_text(encoding='utf-8'))
fn={'prop_state','fingerprint','materials','settings','evaluated','mesh_metrics'}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in fn],type_ignores=[]),'<saved mesh audit utilities>','exec'))

def keys():
    out=[]
    for o in s.objects:
        if o.type!='CAMERA' or not o.animation_data or not o.animation_data.action:continue
        curves=[]
        for l in o.animation_data.action.layers:
            for st in l.strips:
                for b in st.channelbags:
                    for c in b.fcurves:curves.append((c.data_path,c.array_index,[(list(p.co),p.interpolation,list(p.handle_left),list(p.handle_right)) for p in c.keyframe_points]))
        out.append((o.name,curves))
    return hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()

def films():
    # Actual saved poses in the two affected original film segments. Their
    # transitions are cuts; neither segment embeds the separate graph gait.
    p=nav.StrictProbe(s);rows=[]
    for name,a,b in [('CAM_TOUR',1441,1608),('CAM_TOUR_SUPPLEMENTAL',5089,5184)]:
        previous=None
        for frame in range(a,b+1):
            s.frame_set(frame);eye=s.objects[name].matrix_world.translation.copy()
            failure=p.point(eye,True)
            if failure is None and previous is not None:failure=p.segment(previous,eye,True)
            rows.append({'camera':name,'frame':frame,'eye':list(eye),'failure':failure});previous=eye
    return rows

bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene
fp0=fingerprint();m0=materials();set0=settings();keys0=keys();films0=films()
bpy.ops.wm.open_mainfile(filepath=str(OUT));s=bpy.context.scene;initial_frame=s.frame_current
fp1=fingerprint();m1=materials();set1=settings();keys1=keys()
cam_names=[o.name for o in s.objects if o.type=='CAMERA']
protected=[n for n in fp0 if n not in report['manifest']['changed']+report['manifest']['removed']]
scope=all(fp0[n]==fp1.get(n) for n in protected) and set(fp1)==set(fp0)-set(report['manifest']['removed'])
metrics=[mesh_metrics(n) for n in report['manifest']['changed']]
v,f=evaluated('MAIN_L2_MASTER_ceiling');t=BVHTree.FromPolygons(v,f)

low_faces=[(i,p) for i,p in enumerate(f) if all(abs(v[k].z-4.8468)<2e-6 for k in p)]
edgefaces=collections.defaultdict(set)
for i,p in low_faces:
    for k in range(len(p)):edgefaces[tuple(sorted((p[k],p[(k+1)%len(p)])))].add(i)
adj=collections.defaultdict(set)
for ids in edgefaces.values():
    for i in ids:adj[i].update(ids)
rem={i for i,p in low_faces};components=[]
while rem:
    todo=[rem.pop()];group=[]
    while todo:
        a=todo.pop();group.append(a)
        for b in adj[a]&rem:rem.remove(b);todo.append(b)
    components.append(group)

# Every new surface-contact pair is tested as an actual Boolean intersection.
# Temporary objects exist only in this unsaved fresh process and are removed.
intersections=[]
for r in report['new_surface_contacts']:
    a=s.objects[r['a']];tmp=bpy.data.objects.new('QA_CEILING11_INTERSECTION',a.data.copy());s.collection.objects.link(tmp);tmp.matrix_world=a.matrix_world.copy()
    mod=tmp.modifiers.new('actual_intersection','BOOLEAN');mod.solver='EXACT';mod.operation='INTERSECT';mod.object=s.objects[r['b']]
    dg=bpy.context.evaluated_depsgraph_get();eo=tmp.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles()
    vv=[eo.matrix_world@q.co for q in me.vertices];center=sum(vv,Vector())/len(vv) if vv else Vector();vv=[q-center for q in vv]
    volume=abs(sum(vv[tri.vertices[0]].cross(vv[tri.vertices[1]]).dot(vv[tri.vertices[2]])/6 for tri in me.loop_triangles))
    intersections.append({**r,'intersection_volume_m3':volume,'intersection_faces':len(me.polygons),'pass_no_positive_volume':volume<1e-7})
    eo.to_mesh_clear();data=tmp.data;bpy.data.objects.remove(tmp,do_unlink=True);bpy.data.meshes.remove(data)

dg=bpy.context.evaluated_depsgraph_get();seams=[]
def up(label,x,y,z=4.70):
    hit,p,n,face,o,m=s.ray_cast(dg,Vector((x,y,z)),Vector((0,0,1)),distance=.40)
    seams.append({'label':label,'origin':[x,y,z],'object':o.name if hit else None,'point':list(p) if hit else None,'normal':list(n) if hit else None,'enclosed':bool(hit)})
# Bath seam sides at the same low plane; south/west reveals terminate on the
# unchanged higher window heads, with their original5mm ceiling lap retained.
for y in (7.25,7.55,7.85):
    for dx in (-.001,.001):up('BATH_FLUSH',4.7358+dx,y)
for x in (-.1,.8,1.8,2.62,3.5,4.4):
    for dy in (-.001,.001):up('SOUTH_HEAD_REVEAL',x,6.8749+dy)
for y in (7.1,7.5,8.0):
    for dx in (-.001,.001):up('WEST_HEAD_REVEAL',-.499+dx,y)
for x,y in [(-.55,8.5),(-.55,9.3),(-.02,9.7),(.05,9.7),(.5,9.8756),(.5,9.8776),(3,9.8756),(3,9.8776)]:up('STONE_OR_STEP',x,y)
films1=films();s.frame_set(initial_frame)
newfilm=[{'before':a,'after':b} for a,b in zip(films0,films1) if b['failure'] and not a['failure']]
out={'source':str(SRC),'source_sha256':sha(SRC),'candidate':str(OUT),'candidate_sha256':sha(OUT),'reopened_actual_mesh':True,
     'scope_pass':scope,'protected_object_count':len(protected),'camera_count':len(cam_names),'all_camera_fingerprints_unchanged':all(fp0[n]==fp1[n] for n in cam_names),'all_camera_keys_unchanged':keys0==keys1,'camera_key_hash':keys1,
     'materials_unchanged':m0==m1,'settings_unchanged':set0==set1,'metrics':metrics,'single_low_face_component':len(components)==1,'low_face_component_sizes':[len(p) for p in components],
     'new_surface_contacts_actual_volume':intersections,'boundary_rays':seams,'boundary_enclosure_count':sum(r['enclosed'] for r in seams),'films_before':films0,'films_after':films1,'actual_saved_frames_checked_per_scene':len(films1),'baseline_film_failures':sum(bool(r['failure']) for r in films0),'candidate_film_failures':sum(bool(r['failure']) for r in films1),'new_film_failures':newfilm,
     'film_scope':'Actual CAM_TOUR frames1441..1608 and CAM_TOUR_SUPPLEMENTAL5089..5184 at original keys, with full strict foot/body/head and adjacent-frame sweeps. Not all7584 frames.',
     'graph_gait_limit':'Original raised-torso sill gait FAIL is separate from these cut film segments; fixed-torso C gait still QA-only, not installed.',
     'saved':False,'rendered':False,'GEO07':'NOT_RUN','source_height_discrepancy':'OPEN','candidate_file_unchanged':sha(OUT)==report['candidate_sha256']}
out['pass']=scope and m0==m1 and set0==set1 and keys0==keys1 and len(components)==1 and all(r['pass'] for r in metrics) and all(r['pass_no_positive_volume'] for r in intersections) and all(r['enclosed'] for r in seams) and not newfilm
(Q/'master-ceiling11-reopen.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k not in ('films_before','films_after','boundary_rays')},indent=2),flush=True)
assert out['pass']
