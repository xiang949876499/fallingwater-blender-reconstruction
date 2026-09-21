"""Read-only integration12 pixel backprojection and pre-existing tree/floor overlap."""
import bpy, hashlib, json, math, sys, time
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

R = Path(__file__).resolve().parents[1]; Q = R/'qa'
P = R/'scene/Fallingwater_integration_candidate12a.blend'
SHA = '50e0a8fc0bab10fdec0e0b9d26c4ef4a4c71fa56aea6401e75197787c8c0e75a'
assert hashlib.sha256(P.read_bytes()).hexdigest() == SHA
start = time.monotonic(); bpy.ops.wm.open_mainfile(filepath=str(P))
s=bpy.context.scene; s.frame_set(48); bpy.context.view_layer.update()
dep=bpy.context.evaluated_depsgraph_get(); cam=s.objects['CAM_MAIN_OVERVIEW']
print('EXISTING_TREE12 source opened', flush=True)
W,H=1280,720; corners=cam.data.view_frame(scene=s); eye=cam.matrix_world.translation.copy()
def ray(x,y):
    local=corners[3]+(corners[0]-corners[3])*(x/W)+(corners[2]-corners[3])*(y/H)
    direction=(cam.matrix_world.to_3x3()@local).normalized()
    hit,point,normal,index,obj,matrix=s.ray_cast(dep,eye,direction,distance=150)
    return {'pixel':[x,y], 'object':obj.name if hit else None,'point':list(point) if hit else None,'normal':list(normal) if hit else None,'polygon':index if hit else None}
explicit=[ray(*p) for p in [(596,410),(510,510),(512,480),(508,430),(501,415),(488,390),(537,418),(550,390),(516,552)]]
grid=[ray(x,y) for x in range(450,623,4) for y in range(350,553,4)]
tree_hits=[r for r in grid if r['object'] and r['object'].startswith('TREE_')]
counts=Counter(r['object'] for r in tree_hits)
print('EXISTING_TREE12 hits', counts, flush=True)
names=set()
for name in counts:
    base=name.rsplit('_',1)[0]
    names.update(o.name for o in s.objects if o.name.startswith(base+'_'))
def mesh(ob):
    ev=ob.evaluated_get(dep);m=ev.to_mesh();m.calc_loop_triangles()
    verts=[ev.matrix_world@v.co for v in m.vertices]
    faces=[tuple(p.vertices) for p in m.loop_triangles]
    bounds=[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)]
    out=(verts,faces,BVHTree.FromPolygons(verts,faces,all_triangles=True),bounds)
    ev.to_mesh_clear();return out
def box_overlap(a,b):return all(a[i][1]>=b[i][0] and b[i][1]>=a[i][0] for i in range(3))
def corners_bounds(ob):
    vs=[ob.matrix_world@Vector(v) for v in ob.bound_box]
    return [[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)]
terrain=mesh(s.objects['SITE_Continuous_BearRun_Terrain'])
rows=[]; cache={}
for name in sorted(names):
    ob=s.objects[name]
    if ob.type!='MESH':continue
    verts,faces,bvh,bounds=mesh(ob)
    root=ob.matrix_world.translation.copy();hit=terrain[2].ray_cast(Vector((root.x,root.y,100)),Vector((0,0,-1)),200)
    projected=world_to_camera_view(s,cam,root)
    near=[]
    for other in s.objects:
        if other.type!='MESH' or other.hide_render or not other.name.startswith(('MAIN_','TERRACE12_','FW_FURN_MAIN')):continue
        if not box_overlap(bounds,corners_bounds(other)):continue
        if other.name not in cache:cache[other.name]=mesh(other)
        ov,of,obvh,obounds=cache[other.name]
        overlap=bvh.overlap(obvh)
        if not overlap:continue
        witnesses=[]
        for ti,oi in overlap[:24]:
            witnesses.append({'tree_triangle':ti,'building_triangle':oi,
               'tree_triangle_world':[list(verts[k]) for k in faces[ti]],
               'building_triangle_world':[list(ov[k]) for k in of[oi]]})
        near.append({'object':other.name,'actual_triangle_overlap_count':len(overlap),
             'building_bounds':obounds,'aabb_intersection':[[max(bounds[i][0],obounds[i][0]),min(bounds[i][1],obounds[i][1])] for i in range(3)],
             'witness_triangles':witnesses})
    rows.append({'name':name,'data':ob.data.name,'root':list(root),'matrix':[list(r) for r in ob.matrix_world],
        'projected_root_px':[projected.x*W,(1-projected.y)*H],'bounds':bounds,
        'terrain_under_root':list(hit[0]) if hit[0] is not None else None,
        'root_minus_terrain_m':root.z-hit[0].z if hit[0] is not None else None,
        'vertices':len(verts),'triangles':len(faces),'building_intersections':near})
    print('EXISTING_TREE12 check',name,[(r['object'],r['actual_triangle_overlap_count']) for r in near],flush=True)
out={'status':'READ_ONLY_PROBE_COMPLETE','source':str(P),'source_sha256':SHA,
     'image':'renders/previews/integration12a/CAM_MAIN_OVERVIEW.png','image_actually_viewed':True,'image_size':[W,H],
     'frame':48,'camera':cam.name,'camera_location':list(cam.matrix_world.translation),'camera_lens':cam.data.lens,
     'camera_matrix':[list(r) for r in cam.matrix_world],'explicit_pixels':explicit,
     'roi':[450,350,622,552],'roi_grid_step_px':4,'tree_hit_counts':dict(counts),
     'tree_pixel_hits':tree_hits,'objects':rows,'saved':False,'rendered':False,
     'source_unchanged':hashlib.sha256(P.read_bytes()).hexdigest()==SHA,'seconds':time.monotonic()-start}
(Q/'forest-undergrowth13-existing-tree-probe.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('EXISTING_TREE12 COMPLETE',out['seconds'],flush=True)
