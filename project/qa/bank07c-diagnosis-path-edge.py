"""Read-only actual path footprint distances for the five green-bank rays."""
import bpy,json,hashlib,sys,math
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import near_terrain_detail as near
candidate=ROOT/'scene/Fallingwater_near_terrain_candidate07b_contacts.blend'
expected=hashlib.sha256(candidate.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(candidate));bpy.context.scene.frame_set(48)
ob=bpy.data.objects['SITE_Path_bridge_north_approach']
vv=[ob.matrix_world@v.co for v in ob.data.vertices]
edgecount=Counter(tuple(sorted((a,b))) for p in ob.data.polygons for a,b in zip(list(p.vertices),list(p.vertices)[1:]+list(p.vertices)[:1]))
edges=[key for key,n in edgecount.items() if n==1]
bvh=BVHTree.FromObject(ob,bpy.context.evaluated_depsgraph_get())
terrain_bvh=BVHTree.FromObject(bpy.data.objects['SITE_Continuous_BearRun_Terrain'],bpy.context.evaluated_depsgraph_get())
pixels=json.loads((ROOT/'qa/bank07c-diagnosis-pixel-rays.json').read_text(encoding='utf8'))
rows=[]
for r in pixels['records']:
    x,y,z=r['world'];hit,_,_,_=bvh.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),130)
    distance,a,b,t=min((near.segment_distance(x,y,vv[a],vv[b])[0],a,b,near.segment_distance(x,y,vv[a],vv[b])[1]) for a,b in edges)
    edge_point=vv[a].lerp(vv[b],t)
    toward=Vector((x-edge_point.x,y-edge_point.y,0)).normalized()
    edge_samples=[]
    for offset in (-.15,-.05,0,.05,.15):
        q=edge_point+toward*offset
        ground,_,_,_=terrain_bvh.ray_cast(Vector((q.x,q.y,60)),Vector((0,0,-1)),130)
        paved,_,_,_=bvh.ray_cast(Vector((q.x,q.y,60)),Vector((0,0,-1)),130)
        edge_samples.append({'offset_toward_bank_m':offset,'xy':[q.x,q.y],'terrain_z':ground.z if ground else None,'actual_paving_z':paved.z if paved else None,'terrain_above_paving_m':ground.z-paved.z if ground and paved else None})
    rows.append({'label':r['label'],'world':r['world'],'inside_actual_path_mesh':hit is not None,
                 'distance_to_actual_path_boundary_m':distance,'nearest_actual_path_boundary_point':list(edge_point),
                 'height_above_nearest_path_boundary_m':z-edge_point.z,
                 'actual_path_edge_samples':edge_samples,
                 'main04_pixel_registration':[327+x/.0524,540-y/.0531],
                 'triangle_vertex_boundary_distances_m':[min(near.segment_distance(p[0],p[1],vv[a],vv[b])[0] for a,b in edges) for p in r['triangle_vertices']]})
result={'status':'READ_ONLY_ACTUAL_PATH_FOOTPRINT','source_sha256':expected,'path_object':ob.name,'path_vertices':[list(p) for p in vv],'path_faces':[list(p.vertices) for p in ob.data.polygons],
        'actual_boundary_edges':edges,'points':rows,'warning':'main04 XY registration is a reference mapping, not surveyed terrain height. No model changes or render.'}
(ROOT/'qa/bank07c-diagnosis-path-edge.json').write_text(json.dumps(result,indent=2),encoding='utf8')
assert hashlib.sha256(candidate.read_bytes()).hexdigest()==expected
for r in rows:print(json.dumps(r),flush=True)
