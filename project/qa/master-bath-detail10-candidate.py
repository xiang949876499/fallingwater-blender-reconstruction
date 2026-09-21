"""Independent candidate and strict local tests; no production installation."""
from pathlib import Path
import sys,json,hashlib,struct,math,time
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'scripts'))
import master_bath_detail10 as detail
source=root/'scene/Fallingwater_iteration09.blend'
out=root/'scene/Fallingwater_master_bath_candidate10e.blend'
report=root/'qa/master-bath-detail10-candidate-e.json'
assert not out.exists() and not report.exists()
expected='489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.scene.render.threads_mode='FIXED';bpy.context.scene.render.threads=4
t=time.monotonic()

def fingerprint(o,cache):
    h=hashlib.sha256()
    h.update(repr((o.type,[list(row) for row in o.matrix_world],o.parent.name if o.parent else None,
        sorted((str(k),repr(v)) for k,v in o.items()))).encode())
    if o.type=='MESH':
        key=o.data.as_pointer()
        if key not in cache:
            d=hashlib.sha256()
            for v in o.data.vertices:d.update(struct.pack('<3f',*v.co))
            for p in o.data.polygons:
                d.update(struct.pack('<IIB',len(p.vertices),p.material_index,p.use_smooth))
                d.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
            d.update(repr([m.name if m else None for m in o.data.materials]).encode());cache[key]=d.digest()
        h.update(cache[key])
    return h.hexdigest()

excluded=set(detail.targets())|set(detail.CHANGED)
cache={};before={o.name:fingerprint(o,cache) for o in bpy.context.scene.objects if o.name not in excluded}
change=detail.apply()
cache={};after={o.name:fingerprint(o,cache) for o in bpy.context.scene.objects if o.name not in set(change['added'])|set(change['changed'])}
assert before==after,'Non-target object fingerprint difference'
mesh_rows=[]
for name in change['added']+change['changed']:
    ob=bpy.data.objects[name]
    if ob.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(ob.data)
    row={'name':name,'vertices':len(bm.verts),'faces':len(bm.faces),
      'boundary':sum(e.is_boundary for e in bm.edges),'nonmanifold':sum(not e.is_manifold for e in bm.edges),
      'zero_area_faces':sum(f.calc_area()<1e-12 for f in bm.faces),
      'finite':all(math.isfinite(v) for p in bm.verts for v in p.co),'volume_m3':bm.calc_volume(signed=True)}
    mesh_rows.append(row);bm.free()
bad_mesh=[r for r in mesh_rows if r['boundary'] or r['nonmanifold'] or r['zero_area_faces'] or not r['finite'] or r['volume_m3']<=0]
# Actual evaluated meshes include bevels. No geometry is hidden for the test.
deps=bpy.context.evaluated_depsgraph_get();verts=[];faces=[];owners=[]
for ob in bpy.context.scene.objects:
    if ob.type not in ('MESH','CURVE') or ob.hide_render or ob.name.startswith(('QA_','REF_')):continue
    corners=[ob.matrix_world@Vector(v) for v in ob.bound_box]
    if any(max(p[k] for p in corners)<lo or min(p[k] for p in corners)>hi for k,(lo,hi) in enumerate(((3.8,7.7),(6.4,10.5),(2.5,5.1)))):continue
    ev=ob.evaluated_get(deps);m=ev.to_mesh();offset=len(verts)
    verts.extend(ob.matrix_world@v.co for v in m.vertices)
    faces.extend(tuple(offset+i for i in f.vertices) for f in m.polygons);owners.extend([ob.name]*len(m.polygons));ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(verts,faces,epsilon=0)
def ray(p,d,dist):
    hit,n,ix,dd=bvh.ray_cast(Vector(p),Vector(d),dist)
    return {'object':owners[ix],'point':list(hit),'normal':list(n),'distance':dd} if hit is not None else None
points=[Vector((*detail.mh.xy(p),detail.Z)) for p in change['walking_probe_source']]
samples=[]
for a,b in zip(points,points[1:]):
    count=math.ceil((b-a).length/.035)
    samples.extend(a+(b-a)*i/count for i in range(count+1))
issues=[]
for i,p in enumerate(samples):
    for dx,dy in ((0,0),(-.10,0),(.10,0),(0,-.10),(0,.10)):
        h=ray(p+Vector((dx,dy,.205)),(0,0,-1),.215)
        if not h or abs(h['point'][2]-detail.Z)>.004 or h['normal'][2]<.9:
            issues.append({'sample':i,'reason':'STRICT_GROUND_4MM','hit':h,'point':list(p)});break
    for j in range(17):
        dx=0 if j==16 else .18*math.cos(math.tau*j/16);dy=0 if j==16 else .18*math.sin(math.tau*j/16)
        h=ray(p+Vector((dx,dy,.045)),(0,0,1),1.905)
        if h:issues.append({'sample':i,'reason':'BODY_HEAD_1_95M','hit':h,'point':list(p)});break
# Candidate-only diagnostic cameras leave all existing120 views untouched.
cam_specs={'CAM_MB10_SOUTH':((6.03,7.50,4.40),(6.10,9.36,3.86),24),
           'CAM_MB10_ENTRY':((4.50,7.57,4.38),(6.29,8.91,3.87),24)}
from fwlib import collection
for name,(loc,target,lens) in cam_specs.items():
    d=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,d);collection('80_CAMERAS').objects.link(ob)
    ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.02
    ob['exposure']=1.2;ob['qa_diagnostic_only']=True;ob['room_id']=detail.RID
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
rec={'status':'CANDIDATE_LOCAL_GEOMETRY_PASS_VISUAL_NOT_RUN' if not bad_mesh and not issues else 'CANDIDATE_LOCAL_QA_FAIL_RETAINED',
 'source_sha256':expected,'candidate_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
 'helper_sha256':hashlib.sha256((root/'scripts/master_bath_detail10.py').read_bytes()).hexdigest(),
 'candidate':str(out),'changes':change,'unchanged_objects':len(before),'mesh_checks':mesh_rows,'bad_mesh':bad_mesh,
 'strict_path_samples':len(samples),'path_issues':issues,'camera_specs':cam_specs,'seconds':time.monotonic()-t}
report.write_text(json.dumps(rec,indent=2),encoding='utf-8')
print(json.dumps({k:rec[k] for k in ('status','candidate_sha256','unchanged_objects','strict_path_samples','seconds')}))
print('BAD_MESH',json.dumps(bad_mesh));print('PATH_ISSUES',json.dumps(issues[:10]))
