"""Independent read-only topology interfaces and actual solid contact audit."""
import sys,json,hashlib,time
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import water_surface12 as g
import hybrid_water as h
version=sys.argv[sys.argv.index('--version')+1] if '--version' in sys.argv else '04'
src=ROOT/f'scene/Fallingwater_water12_surface{version}.blend';sha=hashlib.sha256(src.read_bytes()).hexdigest();start=time.perf_counter()
bpy.ops.wm.open_mainfile(filepath=str(src));assert not any(m.type=='FLUID' for ob in bpy.data.objects for m in ob.modifiers)
o=bpy.data.objects['WATER12_Continuous_Upper_9Branches_Pool_OuterRiver'];mesh=o.data
v=np.array([tuple(q.co) for q in mesh.vertices]);f=np.array([tuple(p.vertices) for p in mesh.polygons]);tri=v[f];cent=tri.mean(1)
names=json.loads(o['water12_tag_names']);tags=np.array([names[q.value] for q in mesh.attributes['water12_part'].data]);branch=np.array([t.startswith('branch') for t in tags]);ss=(cent-np.array(h.LIP))@np.array(h.DOWN)
terrain=h.render_bvh(bpy.data.objects['SITE_Continuous_BearRun_Terrain']);solids=[];bounds=[];rock_names=[];hashes={}
for ob in bpy.context.scene.objects:
    if ob.type!='MESH' or not ob.name.startswith(g.PREFIX):continue
    hashes[ob.name]=h.shape_hash(ob)
    if ob.name.startswith('SITE_Continuous_'):continue
    vv,ff=g.geometry(ob);solids.append(BVHTree.FromPolygons(vv,ff,all_triangles=True));bounds.append(h.aabb(ob));rock_names.append(ob.name)
bounds=np.array(bounds)
def count_hits(tree,p):
    origin=Vector(p);count=0
    for _ in range(64):
        hit=tree.ray_cast(origin,Vector((0,0,-1)),40)
        if hit[0] is None:break
        count+=1;origin=hit[0]+Vector((0,0,-.00001))
    return count
def contact(points):
    under=[];inside=[]
    for p in points:
        hit=terrain.ray_cast(Vector((p[0],p[1],30)),Vector((0,0,-1)),80)
        if hit[0] is not None and hit[0].z-p[2]>.0005:
            under.append({'point':p.tolist(),'terrain_penetration_vertical_m':float(hit[0].z-p[2])})
        eligible=np.where(((p>=bounds[:,:,0])&(p<=bounds[:,:,1])).all(1))[0]
        for k in eligible:
            nh=count_hits(solids[k],p)
            if nh%2:
                near=solids[k].find_nearest(Vector(p))
                if near[3]>.0005:inside.append({'point':p.tolist(),'solid':rock_names[k],'distance_to_surface_m':float(near[3]),'vertical_crossings':nh,'solid_index':int(k)})
    under.sort(key=lambda q:q['terrain_penetration_vertical_m'],reverse=True);inside.sort(key=lambda q:q['distance_to_surface_m'],reverse=True)
    for q in inside[:12]:q['independent_three_direction_counts']=h.parity(solids[q.pop('solid_index')],Vector(q['point']))
    for q in inside[12:]:q.pop('solid_index')
    return {'tested_points':len(points),'terrain_below_over_05mm':len(under),'terrain_max_penetration_m':under[0]['terrain_penetration_vertical_m'] if under else 0,
            'solid_vertical_parity_inside_over_05mm':len(inside),'solid_max_distance_m':inside[0]['distance_to_surface_m'] if inside else 0,
            'terrain_examples':under[:12],'solid_examples':inside[:12]}
near=(ss>-12)&(ss<30)
free=np.isin(tags,['upper_top','pool_top']);bottom=np.isin(tags,['upper_bottom','pool_bottom']);shore=np.isin(tags,['upper_shore_side','pool_shore_side'])
shore_edges=set()
for face in f[shore&near]:
    for a,b in zip(face,np.roll(face,-1)):shore_edges.add(tuple(sorted((int(a),int(b)))))
top_shore_edges=set()
for face in f[free&near]:
    for a,b in zip(face,np.roll(face,-1)):
        edge=tuple(sorted((int(a),int(b))))
        if edge in shore_edges:top_shore_edges.add(edge)
top_shore_points=np.array([(v[a]+v[b])*.5 for a,b in sorted(top_shore_edges)])
groups={'all_branch_vertices':v[np.unique(f[branch])],'all_branch_triangle_centroids':cent[branch],
        'near_free_surface_all_triangle_centroids':cent[free&near],
        'near_shore_actual_top_edge_midpoints':top_shore_points,
        'near_shore_side_all_triangle_centroids':cent[shore&near],
        'near_C_closure_bottom_triangle_centroids_every_third':cent[bottom&near][::3]}
results={}
for label,p in groups.items():
    results[label]=contact(p);print('W12_FINAL_CONTACT',label,{k:q for k,q in results[label].items() if not k.endswith('examples')},flush=True)
# Each connected component is found from real stored triangle edges.
parent=np.arange(len(v),dtype=np.int32)
def find(i):
    while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
    return i
for face in f:
    a=find(int(face[0]))
    for b in face[1:]:
        b=find(int(b))
        if a!=b:parent[b]=a
labels=np.array([find(i) for i in range(len(v))]);unique,counts=np.unique(labels,return_counts=True)
branch_labels={tag:sorted(map(int,set(labels[np.unique(f[tags==tag])])) ) for tag in names if tag.startswith('branch')}
# A shared ring is an edge with one branch face and one layer face.
interfaces={}
for ids,tag in zip(f,tags):
    if tag.startswith('branch'):
        for a,b in zip(ids,np.roll(ids,-1)):interfaces.setdefault(tuple(sorted((int(a),int(b)))),[]).append(tag)
boundary={e:uses for e,uses in interfaces.items() if len(uses)==1}
for ids,tag in zip(f,tags):
    if not tag.startswith('branch'):
        for a,b in zip(ids,np.roll(ids,-1)):
            e=tuple(sorted((int(a),int(b))))
            if e in boundary:boundary[e].append(tag)
interface_report={}
for tag in branch_labels:
    edges={e:uses for e,uses in boundary.items() if tag in uses};upper=[e for e,u in edges.items() if any(t.startswith('upper') for t in u)];pool=[e for e,u in edges.items() if any(t.startswith('pool') for t in u)]
    interface_report[tag]={'upper_shared_edges':len(upper),'pool_shared_edges':len(pool),'unpaired_edges':sum(len(u)!=2 for u in edges.values()),
        'all_join_edges_have_two_actual_faces':all(len(u)==2 for u in edges.values())}
report={'source':str(src),'source_sha256':sha,'topology':h.topology(o),'contact':results,'rock_hashes':hashes,
        'connected_components':len(unique),'component_vertex_counts_desc':sorted(map(int,counts),reverse=True)[:20],
        'branch_component_labels':branch_labels,'all_nine_branches_share_single_component':len(set(x for vv in branch_labels.values() for x in vv))==1,
        'actual_shared_interfaces':interface_report,'cameras':[ob.name for ob in bpy.context.scene.objects if ob.type=='CAMERA'],
        'remote_upstream_water_retained':bool(bpy.context.scene.objects.get('SITE_Remote_Upstream_Creek_Continuation')),
        'remote_upstream_interface_not_certified':True,'no_bake_or_render':True,'source_unchanged':hashlib.sha256(src.read_bytes()).hexdigest()==sha,
        'elapsed_s':time.perf_counter()-start,'limitations':'Triangle centroid sampling is explicit, not full analytical collider intersection. A 0.5 mm reporting cutoff filters mere contact and numerical roundoff; true counterexamples are retained. Component connectivity does not establish hydrodynamics. Bottom caps are C optical closure approximations, not CFD bed boundaries; signed mesh volume is not measured water quantity.'}
order=np.argsort(counts)[::-1][:10]
report['largest_component_bounds']=[{'label':int(unique[k]),'vertices':int(counts[k]),'aabb_m':np.stack((v[labels==unique[k]].min(0),v[labels==unique[k]].max(0)),1).tolist()} for k in order]
(ROOT/f'qa/water12-surface{version}-final-audit.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('W12_FINAL_AUDIT_DONE',report['connected_components'],report['all_nine_branches_share_single_component'],flush=True)
