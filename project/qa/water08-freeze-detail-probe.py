"""Read-only interpretation of steep rays and shortest chord; not a new candidate."""
import bpy, numpy as np, json, sys, importlib.util
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location('freezer',Path(__file__).parent/'water08-freeze-helper.py')
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
old=json.loads(m.REPORT.read_text(encoding='utf-8'))
xy=np.load(ROOT/'qa/water08-freeze-thickness-sampling.npz')['probe_xy_m']
ring=np.load(m.NPZ)['ring_vertices'].astype(int)
result={'read_only':True,'bake':False,'render':False,'scene_saved':False,'frames':[]}
bpy.ops.wm.open_mainfile(filepath=str(m.OUTPUT));scene=bpy.context.scene;o=scene.objects[m.NAME]
base=m.world(m.coords(o.data.shape_keys.key_blocks[0].data),o.matrix_world)
ringmask=np.zeros(len(base),bool);ringmask[ring]=True
def hits_at(tree,p):
    origin=Vector((float(p[0]),float(p[1]),-5.4));direction=Vector((0,0,-1));hits=[]
    for _ in range(16):
        hit=tree.ray_cast(origin,direction,max(0,float(origin.z+6.4)))
        if hit[0] is None:break
        hits.append({'z':float(hit[0].z),'normalz':float(hit[1].z),'triangle':int(hit[2])})
        origin=hit[0]+direction*.000002
    return hits
def pairs(hits,threshold):
    return [(hits[j],hits[j+1]) for j in range(len(hits)-1)
            if hits[j]['normalz']>threshold and hits[j+1]['normalz']<-threshold
            and -5.95<hits[j]['z']<-5.48 and hits[j]['z']>hits[j+1]['z']]
def normal_records(v,f,tree,indices):
    records=[];ns=m.normals(v,f[indices]);length=np.linalg.norm(ns,axis=1);cent=v[f[indices]].mean(axis=1)
    for j,tid in enumerate(indices):
        direction=Vector(-ns[j]/length[j]);p=Vector(cent[j])+direction*.000002
        hit=tree.ray_cast(p,direction,1.5)
        if hit[0] is None or hit[1].dot(direction)<=0:continue
        records.append({'triangle':int(tid),'vertices':f[tid].tolist(),'frozen_vertices_in_triangle':ringmask[f[tid]].tolist(),
                        'centroid_m':cent[j].tolist(),'source_normal':(-direction).to_tuple(),
                        'hit_triangle':int(hit[2]),'hit_vertices':f[hit[2]].tolist(),
                        'hit_point_m':list(hit[0]),'hit_normal':list(hit[1]),'exit_dot':float(hit[1].dot(direction)),
                        'chord_length_m':float(hit[3]+.000002),'area_m2':float(length[j]/2)})
    return sorted(records,key=lambda q:q['chord_length_m'])
candidate_targets={}
for frame in range(1,37):
    scene.frame_set(frame);bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    v=m.world(m.coords(mesh.vertices),o.matrix_world);f=m.faces_of(mesh);tree=m.tree_for(v,f)
    strict_missing=[];sign_missing=[];lowest=None
    for i,p in enumerate(xy):
        hits=hits_at(tree,p);strict=pairs(hits,.2);sign=pairs(hits,0)
        if not strict:strict_missing.append({'probe':i,'xy_m':p.tolist(),'hits':hits,'ordered_sign_pair':bool(sign)})
        if not sign:sign_missing.append({'probe':i,'xy_m':p.tolist(),'hits':hits})
        elif lowest is None or sign[-1][0]['z']-sign[-1][1]['z']<lowest['thickness_m']:
            lowest={'probe':i,'xy_m':p.tolist(),'thickness_m':sign[-1][0]['z']-sign[-1][1]['z'],'pair':sign[-1]}
    info={'frame':frame,'strict_nz_02_missing':len(strict_missing),'strict_missing_all_details':strict_missing,
          'sign_only_ordered_pair_missing':len(sign_missing),'sign_only_missing_all_details':sign_missing,
          'sign_only_minimum_vertical_pair':lowest}
    if frame in (11,36):
        ns0=m.normals(base,f);adj=np.flatnonzero(np.any(ringmask[f],axis=1)&(np.linalg.norm(ns0,axis=1)>1e-9))
        records=normal_records(v,f,tree,adj)
        info['five_shortest_inward_chords']=records[:5]
        tids=np.array([q['triangle'] for q in records[:5]],int)
        info['same_triangles_at_basis']=normal_records(base,f,m.tree_for(base,f),tids)
        candidate_targets[frame]={'triangle_vertices':[(q['triangle'],q['vertices']) for q in records[:5]],'vertical':lowest}
    result['frames'].append(info);ev.to_mesh_clear()
    print('FREEZE08_DETAIL',frame,'strict_missing',len(strict_missing),'sign_missing',len(sign_missing),flush=True)

# Compare the same physical vertices and XY against the existing motion source.
# No vertices, keys, flags, or files are modified by this crosscheck.
bpy.ops.wm.open_mainfile(filepath=str(m.SOURCE));scene=bpy.context.scene;o=scene.objects[m.NAME]
result['source_frame_crosschecks']=[]
for frame,target in candidate_targets.items():
    scene.frame_set(frame);bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    v=m.world(m.coords(mesh.vertices),o.matrix_world);f=m.faces_of(mesh);tree=m.tree_for(v,f)
    points=[]
    for tid,vids in target['triangle_vertices']:
        tri=v[vids];n=np.cross(tri[1]-tri[0],tri[2]-tri[0]);n/=np.linalg.norm(n)
        direction=Vector(-n);origin=Vector(tri.mean(axis=0))+direction*.000002;hit=tree.ray_cast(origin,direction,1.5)
        points.append({'candidate_triangle':tid,'same_vertex_indices':vids,'source_triangle_centroid_m':tri.mean(axis=0).tolist(),
                       'source_inward_chord_m':float(hit[3]+.000002) if hit[0] else None,
                       'source_hit_exit_dot':float(hit[1].dot(direction)) if hit[0] else None,
                       'source_hit_point_m':list(hit[0]) if hit[0] else None,
                       'source_normal':n.tolist()})
    source_hits=hits_at(tree,target['vertical']['xy_m']);source_pairs=pairs(source_hits,0)
    result['source_frame_crosschecks'].append({'frame':frame,'inward_chords':points,
        'same_vertical_xy_m':target['vertical']['xy_m'],'source_vertical_hits':source_hits,
        'source_vertical_thickness_m':source_pairs[-1][0]['z']-source_pairs[-1][1]['z'] if source_pairs else None,
        'frozen_vertical_thickness_m':target['vertical']['thickness_m']})
    ev.to_mesh_clear()
result['source_hash_unchanged']=m.digest(m.SOURCE)==m.SOURCE_SHA
result['candidate_hash_unchanged']=m.digest(m.OUTPUT)==old['candidate_sha256']
(ROOT/'qa/water08-freeze-detail-probe.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('FREEZE08_DETAIL_COMPLETE',flush=True)
