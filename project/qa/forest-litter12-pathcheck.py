"""Incremental passage regression against new ground-layer geometry only."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
record=json.loads((R/'qa/forest-litter12-check.json').read_text())
P=Path(record['candidate']);assert hashlib.sha256(P.read_bytes()).hexdigest()==record['candidate_sha256']
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene
verts=[];tris=[];owners=[]
for o in s.objects:
    if not o.name.startswith('LITTER12_') or o.type!='MESH':continue
    o.data.calc_loop_triangles();offset=len(verts)
    verts.extend(o.matrix_world@v.co for v in o.data.vertices)
    tris.extend(tuple(offset+i for i in t.vertices)for t in o.data.loop_triangles)
    owners.extend(o.name for _ in o.data.loop_triangles)
tree=BVHTree.FromPolygons(verts,tris,all_triangles=True)
fail=[];rays=0;positions=0;checked=[]
for o in s.objects:
    if not o.name.startswith('SITE_Path_') or o.type!='MESH':continue
    pts=[o.matrix_world@v.co for v in o.data.vertices];checked.append(o.name)
    for face in o.data.polygons:
        pp=[pts[i]for i in face.vertices];a=(pp[0]+pp[1])*.5;b=(pp[2]+pp[3])*.5
        across=(pp[1]-pp[0]).normalized();half=(pp[1]-pp[0]).length*.5
        for j in range(max(2,math.ceil((b-a).length/.25))+1):
            t=j/max(2,math.ceil((b-a).length/.25));center=a.lerp(b,t)
            for lane in (-1,0,1):
                foot=center+across*(half-.18)*lane;positions+=1
                # Actual path plane is fixed; check low foot and full standing body.
                for z in (.015,.25,.85,1.55,1.95):
                    origin=foot+Vector((0,0,z))
                    for k in range(8):
                        direction=Vector((math.cos(k*math.tau/8),math.sin(k*math.tau/8),0))
                        h,n,idx,d=tree.ray_cast(origin,direction,.18);rays+=1
                        if h is not None and len(fail)<30:fail.append({'path':o.name,'point':list(origin),'hit':list(h),'new_object':owners[idx]})
result={'status':'PASS_NO_NEW_PATH_OBSTRUCTION'if not fail else 'FAIL_NEW_PATH_OBSTRUCTION',
        'candidate_sha256':record['candidate_sha256'],'paths':checked,'positions':positions,'rays':rays,
        'body_radius_m':.18,'height_samples_m':[.015,.25,.85,1.55,1.95],'failures':fail,
        'method':'Real saved path strip centers and both edge lanes,250mm intervals; rays index only new actual LITTER12 triangles.',
        'scope':'Incremental local3site-path regression, not the full adjacency/tour audit for a future combined scene.',
        'saved':False,'rendered':False}
(R/'qa/forest-litter12-pathcheck.json').write_text(json.dumps(result,indent=2))
assert not fail,result
print('LITTER12_PATHCHECK',json.dumps(result),flush=True)
