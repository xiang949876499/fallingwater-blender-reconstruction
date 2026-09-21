"""Read-only mesh2/3 morphology, sampled visibility and local design envelope."""
import bpy,json,hashlib,math,re
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'scene/Fallingwater_iteration08.blend';SHA='c5cd501e4c8ae0205ecb2437cd2d06d0c92bcc9a87e7d93d3986aeef976070d7'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;scene.frame_set(48)
scene.render.resolution_x=960;scene.render.resolution_y=540;scene.render.resolution_percentage=100
dg=bpy.context.evaluated_depsgraph_get()
terrain=scene.objects['SITE_Continuous_BearRun_Terrain'];tbvh=BVHTree.FromObject(terrain,dg)
cameras=[scene.objects[n] for n in ('CAM_HERO','CAM_MAIN_L1_LOGGIA_B','CAM_MAIN_L1_LIVING_A')]
def world_bounds(objects):
    p=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box]
    return [min(v.x for v in p),max(v.x for v in p),min(v.y for v in p),max(v.y for v in p),min(v.z for v in p),max(v.z for v in p)]
def components(mesh):
    adjacent=[set() for _ in mesh.vertices]
    for e in mesh.edges:
        a,b=e.vertices;adjacent[a].add(b);adjacent[b].add(a)
    remaining=set(range(len(adjacent)));groups=[]
    while remaining:
        todo=[remaining.pop()];group=[]
        while todo:
            i=todo.pop();group.append(i)
            for j in adjacent[i]:
                if j in remaining:remaining.remove(j);todo.append(j)
        groups.append(group)
    return groups
def length_stats(values):return {'min':min(values),'max':max(values),'mean':sum(values)/len(values)}
assets=[]
for index in (2,3):
    stem=bpy.data.meshes[f'TREE_Understory_{index}_Stems'];leaf=bpy.data.meshes[f'TREE_Understory_{index}_Leaves']
    stem.calc_loop_triangles();leaf.calc_loop_triangles();gc=components(leaf);sc=components(stem)
    lengths=[];widths=[];leaf_z=[]
    for first in range(0,len(leaf.vertices),7):
        vv=[leaf.vertices[first+j].co for j in range(7)]
        lengths.append((vv[3]-vv[0]).length);widths.append((vv[5]-vv[1]).length);leaf_z.append(sum(v.z for v in vv)/7)
    vv=[v.co for m in (stem,leaf) for v in m.vertices]
    bb=[min(v[a] for v in vv) for a in range(3)]+[max(v[a] for v in vv) for a in range(3)]
    assets.append({'index':index,'stem_mesh':stem.name,'leaf_mesh':leaf.name,
                   'stem_vertices':len(stem.vertices),'stem_faces':len(stem.polygons),'stem_triangles':len(stem.loop_triangles),
                   'leaf_vertices':len(leaf.vertices),'leaf_faces':len(leaf.polygons),'leaf_triangles':len(leaf.loop_triangles),
                   'stem_components':len(sc),'stem_component_vertex_counts':dict(Counter(len(g) for g in sc)),
                   'leaf_components':len(gc),'leaf_component_vertex_counts':dict(Counter(len(g) for g in gc)),
                   'leaf_length_m':length_stats(lengths),'actual_outline_width_m':length_stats(widths),
                   'one_sided_leaf_mesh_area_m2':sum(p.area for p in leaf.polygons),
                   'local_bounds_xyz_min_then_max':bb,'local_dimensions':[bb[a+3]-bb[a] for a in range(3)],
                   'leaf_center_z_m':length_stats(leaf_z),
                   'branching_evidence':'13 disconnected 10-vertex two-ring tubes; no lateral forks. Exact code at site.py::_plant_asset confirms 13 stems x 7 distributed leaves.'})

paths=[]
for o in scene.objects:
    if o.type!='MESH' or not o.name.startswith(('SITE_Path_','SITE_Bridge_')):continue
    coords=[o.matrix_world@v.co for v in o.data.vertices]
    counts=Counter(tuple(sorted((a,b))) for p in o.data.polygons for a,b in zip(list(p.vertices),list(p.vertices)[1:]+list(p.vertices)[:1]))
    edges=[(coords[a],coords[b]) for (a,b),count in counts.items() if count==1]
    if edges:paths.append((o.name,edges))
def seg_dist(x,y,a,b):
    dx=b.x-a.x;dy=b.y-a.y;t=max(0,min(1,((x-a.x)*dx+(y-a.y)*dy)/max(1e-12,dx*dx+dy*dy)))
    return math.hypot(x-a.x-t*dx,y-a.y-t*dy)
def aabb_intersects(a,b):return all(a[2*i]<=b[2*i+1] and a[2*i+1]>=b[2*i] for i in range(3))
hard=[]
for o in scene.objects:
    if o.type=='MESH' and not o.hide_render and o.name.startswith(('MAIN_','GUEST_','SITE_Core_','SITE_Cascade_Shoulder_Continuous','SITE_Bridge_','WATER_')):
        bb=world_bounds([o])
        if bb[0]<50 and bb[1]>-35 and bb[2]<35 and bb[3]>-20:hard.append((o.name,bb))
def constraints(root,radius=.85,height=1.8):
    envelope=[root.x-radius,root.x+radius,root.y-radius,root.y+radius,root.z+.10,root.z+height]
    edge_distances=[(name,min(seg_dist(root.x,root.y,a,b) for a,b in edges)) for name,edges in paths]
    camera=min((math.hypot(root.x-c.matrix_world.translation.x,root.y-c.matrix_world.translation.y),c.name) for c in scene.objects if c.type=='CAMERA')
    intersect=[name for name,bb in hard if aabb_intersects(envelope,bb)]
    return {'proposal_crown_radius_m':radius,'proposal_height_m':height,'envelope_xyz_pairs':envelope,
            'nearest_actual_path_boundary':sorted(edge_distances,key=lambda t:t[1])[:2],
            'nearest_camera_xy':[camera[1],camera[0]],'hard_object_aabb_intersections':intersect,
            'preliminary_envelope_clear':not intersect and all(d>radius+.15 for _,d in edge_distances) and camera[0]>radius+.5}
def visibility(leaf,cam):
    names={leaf.name,leaf.name.replace('_Leaves','_Branches')};origin=cam.matrix_world.translation
    samples=[]
    for j in range(0,len(leaf.data.polygons),30):
        target=leaf.matrix_world@leaf.data.polygons[j].center;p=world_to_camera_view(scene,cam,target)
        if p.z<=0 or not 0<p.x<1 or not 0<p.y<1:continue
        direction=(target-origin).normalized();start=origin.copy();distance=(target-origin).length
        first=[];kind='occluded'
        for attempt in range(5):
            ok,hit,normal,face,obj,matrix=scene.ray_cast(dg,start,direction,distance=(target-start).length+.03)
            if not ok:break
            first.append(obj.name)
            if obj.name in names:
                kind='direct' if attempt==0 else 'through_glass';break
            if 'glass' not in obj.name.lower():break
            start=hit+direction*.003
        samples.append({'pixel':[p.x*960,(1-p.y)*540],'kind':kind,'first_hits':first})
    return {'tested_leaf_surface_samples':len(samples),'direct_samples':sum(s['kind']=='direct' for s in samples),
            'through_glass_samples':sum(s['kind']=='through_glass' for s in samples),'samples':samples}

allplants=[];counts=Counter();near=[]
for o in scene.objects:
    if o.type!='MESH' or not re.fullmatch(r'TREE_Understory_\d{4}_Leaves',o.name):continue
    match=re.fullmatch(r'TREE_Understory_([0-3])_Leaves',o.data.name)
    if not match:continue
    index=int(match.group(1));counts[index]+=1
    if index not in (2,3):continue
    branch=scene.objects[o.name.replace('_Leaves','_Branches')];root=o.matrix_world.translation
    distance=math.hypot(root.x-5,root.y-5)
    if distance>35:continue
    bb=world_bounds([o,branch]);ground,_,_,_=tbvh.ray_cast(Vector((root.x,root.y,60)),Vector((0,0,-1)),130)
    row={'leaf_object':o.name,'branch_object':branch.name,'asset':index,'root':list(root),
         'distance_to_house_reference_xy_m':distance,'scale':list(o.scale),'bounds_world_xyz_pairs':bb,
         'dimensions_world':[bb[1]-bb[0],bb[3]-bb[2],bb[5]-bb[4]],'ground_anchor_gap_m':root.z-ground.z if ground else None,
         'leaf_count':91,'cameras':{},'design_envelope':constraints(root)}
    for cam in cameras:
        corners=[Vector((x,y,z)) for x in bb[:2] for y in bb[2:4] for z in bb[4:6]]
        pp=[world_to_camera_view(scene,cam,p) for p in corners];front=[p for p in pp if p.z>0]
        if not front:continue
        rect=[min(p.x for p in front)*960,max(p.x for p in front)*960,(1-max(p.y for p in front))*540,(1-min(p.y for p in front))*540]
        if rect[1]<0 or rect[0]>960 or rect[3]<0 or rect[2]>540:continue
        v=visibility(o,cam);v['projected_bound_px_xy_pairs']=rect;row['cameras'][cam.name]=v
    near.append(row)
summary={}
for cam in cameras:
    potential=[r for r in near if cam.name in r['cameras']]
    direct=[r for r in potential if r['cameras'][cam.name]['direct_samples']>0]
    glass=[r for r in potential if r['cameras'][cam.name]['through_glass_samples']>0]
    summary[cam.name]={'bbox_intersects_frame_near35m':len(potential),'sample_confirmed_direct_instances':len(direct),
                       'sample_confirmed_through_glass_instances':len(glass),
                       'direct_leaf_count_in_entire_instances_not_visible_leaf_count':91*len(direct),
                       'direct_instances':[r['leaf_object'] for r in direct],
                       'tested_leaf_surface_rays':sum(r['cameras'][cam.name]['tested_leaf_surface_samples'] for r in potential)}
eligible=[]
for r in near:
    score=sum(v['direct_samples'] for name,v in r['cameras'].items() if name in ('CAM_HERO','CAM_MAIN_L1_LOGGIA_B'))
    x,y,_=r['root'];inbank=(-25<x<-6 and -8<y<18) or (23<x<36 and 7<y<24)
    if score>0 and inbank and r['design_envelope']['preliminary_envelope_clear']:
        eligible.append((score,r))
eligible.sort(key=lambda t:(-t[0],t[1]['leaf_object']))
out={'status':'READ_ONLY_ASSET_AND_VISIBILITY_DIAGNOSIS_PROPOSAL_ONLY','source_sha256':SHA,'frame':48,
     'near_radius_reference_xy':[5,5],'near_radius_m':35,'full_understory_counts_by_asset':dict(counts),
     'asset_meshes':assets,'near_instances':near,'camera_summary':summary,
     'candidate_design_limit':20,'preliminary_eligible_count':len(eligible),
     'preliminary_replacement_shortlist':[{'score':score,**r} for score,r in eligible[:20]],
     'rendered':False,'scene_saved':False,'built_prototype':False,
     'limits':'Visibility uses 19 triangle-center samples per plant, not full pixel coverage. Glass skip does not model refraction. AABB envelope/path boundary filtering is conservative pre-design only; actual future prototype must pass BVH contacts and complete route/camera regressions before local adoption.'}
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
(ROOT/'qa/terrain-material08-shrub-probe.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('SHRUB08',json.dumps({'counts':out['full_understory_counts_by_asset'],'asset_meshes':assets,'camera_summary':summary,'near_count':len(near),'eligible_count':len(eligible),'shortlist':[(s,r['leaf_object'],r['root']) for s,r in eligible[:20]]}),flush=True)
