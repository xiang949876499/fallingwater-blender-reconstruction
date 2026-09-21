"""Read-only navigation regression against the two changed physical surfaces."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
candidate_path=R/'scene/Fallingwater_study_floor_candidate07.blend'
assert hashlib.sha256(candidate_path.read_bytes()).hexdigest()=='89b6d6b4f10f9bdadfe7cb4f564d4e8daa7b92d99b84cccb506cafa0b6e85968'
bpy.ops.wm.open_mainfile(filepath=str(candidate_path));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4
dg=bpy.context.evaluated_depsgraph_get();verts=[];faces=[]
for name in ('MAIN_L3_STUDY_slab','MAIN_L3_STUDY_finish'):
    ob=s.objects[name].evaluated_get(dg);m=ob.to_mesh();start=len(verts)
    verts.extend(ob.matrix_world@v.co for v in m.vertices)
    faces.extend(tuple(start+i for i in f.vertices) for f in m.polygons);ob.to_mesh_clear()
bvh=BVHTree.FromPolygons(verts,faces,all_triangles=False)
route=json.loads((R/'data/tour-route.json').read_text())
body_hits=[];body_count=0
def body(point,label):
    global body_count
    for dz in (0,-.65,-1.3):
        p=Vector(point)+Vector((0,0,dz));r=bvh.find_nearest(p,.18);body_count+=1
        if r[0] is not None:body_hits.append({'label':label,'center':list(p),'distance_m':r[3]})
for ob in s.objects:
    if ob.type=='CAMERA':body(ob.matrix_world.translation,ob.name)
study_floor=[];segments=route['main_segments']+route['supplemental_segments']
for seg in segments:
    for i,(a,b) in enumerate(zip(seg['points'],seg['points'][1:])):
        a=Vector(a);b=Vector(b);n=max(2,math.ceil((b-a).length/.10))
        for k in range(n+1):
            q=a.lerp(b,k/n);body(q,f"{seg['id']}:{i}:{k}")
            if 'MAIN_L3_STUDY' in seg.get('room_ids',[]):
                hit,p,norm,face,ob,_=s.ray_cast(dg,Vector((q.x,q.y,5.35415)),Vector((0,0,-1)),distance=.5)
                study_floor.append({'xyz':list(q),'hit':ob.name if hit else None,'floor_z':p.z if hit else None,'pass':hit and abs(p.z-5.28615)<.001})
j={'status':'PASS_CHANGED_FLOOR_ROUTE_REGRESSION' if not body_hits and all(x['pass'] for x in study_floor) else 'FAIL_CHANGED_FLOOR_ROUTE_REGRESSION','candidate_sha256':hashlib.sha256(candidate_path.read_bytes()).hexdigest(),'route_source_sha256':hashlib.sha256((R/'data/tour-route.json').read_bytes()).hexdigest(),'body_centers_tested_against_changed_floor_only':body_count,'body_radius_m':.18,'body_hits':body_hits,'study_route_floor_samples':len(study_floor),'study_route_floor_fails':sum(not x['pass'] for x in study_floor),'study_floor_samples':study_floor,'limitations':['Tests collision introduced by the two changed floor meshes, not complete scene collision or new route acceptance.','All other walls/doors remain fingerprint-identical to the West candidate; complete 07 route QA is owned by the integrator.']}
(R/'qa/photo-match07-study-floor-route-check.json').write_text(json.dumps(j,indent=2))
print(json.dumps({k:v for k,v in j.items() if k!='study_floor_samples'},indent=2))
