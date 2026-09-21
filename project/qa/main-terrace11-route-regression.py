"""Changed-volume sweep for every stored tour path and original camera.

This complements the detailed local foot/cylinder/head tests; it is a before/
after regression test, not a substitute for the full tour acceptance audit.
"""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];Q=R/'qa'
r=json.loads((Q/'main-terrace11-attempt02-check.json').read_text(encoding='utf-8'))
route=json.loads((R/'qa/tour-path-route-iteration09-attempt01.json').read_text(encoding='utf-8'))
def read(path,names):
    bpy.ops.wm.open_mainfile(filepath=str(path));dep=bpy.context.evaluated_depsgraph_get();out={}
    for name in names:
        o=bpy.data.objects[name].evaluated_get(dep);m=o.to_mesh()
        try:out[name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(f.vertices) for f in m.polygons])
        finally:o.to_mesh_clear()
    return out
old=read(r['source'],r['manifest']['changed']+r['manifest']['removed'])
points=[]
for o in bpy.context.scene.objects:
    if o.type=='CAMERA':points.append((o.name,Vector(o.matrix_world.translation)))
camera_count=len(points)
for seg in route['main_segments']+route['supplemental_segments']:
    for j,(a,b) in enumerate(zip(seg['points'],seg['points'][1:])):
        aa,bb=Vector(a),Vector(b);n=max(2,math.ceil((bb-aa).length/.05))
        for i in range(n+1):points.append((f"{seg['id']}:{j}:{i}",aa.lerp(bb,i/n)))
new=read(r['candidate'],r['manifest']['changed'])
def nearest(trees,p):
    hits=[]
    for name,t in trees.items():
        q,n,f,d=t.find_nearest(p,.18)
        if q is not None:hits.append({'object':name,'distance_m':d,'point':list(q),'normal':list(n),'face':f})
    return min(hits,key=lambda h:h['distance_m']) if hits else None
regress=[];old_near=0;new_near=0;sampled=0
for label,eye in points:
    for dz in (0,-.65,-1.3,.35):
        p=eye+Vector((0,0,dz));a=nearest(old,p);b=nearest(new,p);sampled+=1
        old_near+=bool(a);new_near+=bool(b)
        if b and not a:regress.append({'id':label,'eye_z_offset_m':dz,'point':list(p),'candidate_hit':b})
out={'status':'PASS_NO_NEW_CHANGED_VOLUME_NEAR_HITS' if not regress else 'FAIL_NEW_PROXIMITY','source':r['source'],'candidate':r['candidate'],'candidate_sha256':r['candidate_sha256'],'camera_count':camera_count,'camera_and_route_center_points':len(points),'body_height_sphere_samples':sampled,'sample_step_m':.05,'radius_m':.18,'baseline_near_count':old_near,'candidate_near_count':new_near,'new_near_hits':regress,'method':'All stored paths at <=50mm spacing, four heights relative to existing eye path. Sphere proximity only to whitelisted before/after volumes. Existing near hits do not become PASS.','limits':'Separate local report records strict sole normal/support and 1.95m head tests, including 30 unchanged old failures. No claim about unrelated scene geometry, all movie frames, or source doorway identities.','rendered':False,'saved':False,'candidate_hash_unchanged':hashlib.sha256(Path(r['candidate']).read_bytes()).hexdigest()==r['candidate_sha256']}
(Q/'main-terrace11-route-regression.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2));assert not regress
