"""Read saved tour, verify every delivered frame, measure named real collisions."""
import bpy
import json
import sys
import math
import hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import tour

rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
route=json.loads((ROOT/'data/tour-route.json').read_text(encoding='utf-8'))
check=tour.camera_evidence(bpy.context.scene,rooms,route)
check['saved_scene_reopened']=True
check['saved_scene']=bpy.data.filepath
check['saved_scene_sha256']=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
(ROOT/'qa/tour-path-camera-coverage.json').write_text(json.dumps(check,ensure_ascii=False,indent=2),encoding='utf-8')

def intrusion(name,prefix):
    obj=bpy.data.objects[name]
    vertices=[obj.matrix_world@v.co for v in obj.data.vertices]
    bvh=BVHTree.FromPolygons(vertices,[tuple(f.vertices) for f in obj.data.polygons],epsilon=.001)
    bounds=[[min(p[k] for p in vertices),max(p[k] for p in vertices)] for k in range(3)]
    points=tour.stair_mesh_points(bpy.context.scene,prefix)
    sampled=[]
    for edge,(a,b) in enumerate(zip(points,points[1:])):
        a,b=Vector(a),Vector(b)
        for i in range(max(1,math.ceil((b-a).length/.10))+1):
            count=max(1,math.ceil((b-a).length/.10))
            eye=a+(b-a)*(i/count)
            for dx,dy in ((0,0),(-.18,0),(.18,0),(0,-.18),(0,.18)):
                origin=eye+Vector((dx,dy,.24-tour.EYE))
                loc,normal,index,distance=bvh.ray_cast(origin,Vector((0,0,1)),1.47)
                if loc is not None:
                    sampled.append({'edge':edge,'eye':list(eye),'expected_floor':eye.z-tour.EYE,
                                    'body_offset':[dx,dy],'hit':list(loc),'face_normal':list(normal)})
    return {'object':name,'mesh_world_bounds':bounds,'stair_prefix':prefix,'sample_step_m':.10,
            'body_radius_m':.18,'interference_count':len(sampled),'actual_interference_samples':sampled,
            'claim':'Named obstacle intrusion diagnostic only; no other obstacles excluded from full adjacency evidence.'}

result={'source_saved_scene':bpy.data.filepath,'source_saved_scene_sha256':check['saved_scene_sha256'],
        'camera_status':check['status'],'interferences':[
            intrusion('SITE_Path_bridge_north_approach','MAIN_loggia_pool_stair_'),
            intrusion('GUEST_POOL_coping_16','GUEST_POOL_coping_ascent_tread_')]}
adj=json.loads((ROOT/'qa/tour-path-all-adjacency.json').read_text(encoding='utf-8'))
edge=next(e for e in adj['edges'] if e['id']=='ADJ_017')
probe=tour.Probe(bpy.context.scene,((10,21),(5,12),(-4,3)))
probe.step_mode=True
result['loggia_multiflight_diagnostic']={
    'edge_id':edge['id'],'claim':'All path pieces checked independently; any failures remain failures.',
    'waypoint_ground':[
        {'index':i,'eye':p,'expected_ground':p[2]-tour.EYE,
         'actual_ground_ray':probe.ray((p[0],p[1],p[2]-tour.EYE+.32),(0,0,-1),.90),
         'body_or_ground_failure':probe.point(p,True)} for i,p in enumerate(edge['points'])],
    'segment_results':[
        {'index':i,'from':a,'to':b,'failure':probe.segment(a,b,True)}
        for i,(a,b) in enumerate(zip(edge['points'],edge['points'][1:]))]
}
(ROOT/'qa/tour-path-iteration05-interference.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('SAVED_TOUR_REOPEN',json.dumps({'camera_status':check['status'],'sha256':check['saved_scene_sha256'],
      'interferences':[{k:v for k,v in r.items() if k!='actual_interference_samples'} for r in result['interferences']]}),flush=True)
