"""Read-only frozen-bed contact and tiny-triangle diagnostics for surface12."""
import sys,json,time,hashlib
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import water_surface12 as g
import hybrid_water as h
version=sys.argv[sys.argv.index('--version')+1] if '--version' in sys.argv else '02'
src=ROOT/f'scene/Fallingwater_water12_surface{version}.blend';source_sha=hashlib.sha256(src.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(src));assert not any(m.type=='FLUID' for o in bpy.data.objects for m in o.modifiers)
rock_v=[];rock_f=[];names=[];trees={}
for o in bpy.context.scene.objects:
    if o.type!='MESH' or not o.name.startswith(g.PREFIX):continue
    vv,ff=g.geometry(o);offset=len(rock_v);rock_v.extend(vv);rock_f.extend([tuple(q+offset for q in f) for f in ff]);names.extend([o.name]*len(ff))
    if o.name.startswith('SITE_Core_'):trees[o.name]=BVHTree.FromPolygons(vv,ff,all_triangles=True)
rocks=BVHTree.FromPolygons(rock_v,rock_f,all_triangles=True)
o=bpy.data.objects['WATER12_Continuous_Upper_9Branches_Pool_OuterRiver'];v=np.array([tuple(q.co) for q in o.data.vertices]);f=np.array([tuple(p.vertices) for p in o.data.polygons]);tri=v[f]
ar=.5*np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)
s=(v-np.array(h.LIP))@np.array(h.DOWN)
cent=tri.mean(1);sc=(cent-np.array(h.LIP))@np.array(h.DOWN)
report={'source':str(src),'source_sha256':source_sha,'tiny_triangles':[{'id':int(i),'area_m2':float(ar[i]),'vertices':v[f[i]].tolist(),'indices':f[i].tolist()} for i in np.where(ar<1e-12)[0]],'groups':{}}
groups={'falling_vertices':v[(v[:,2]<-3.03)&(v[:,2]>-5.7)&(s>-.6)&(s<2.)],
        'falling_triangle_centroids':cent[(cent[:,2]<-3.03)&(cent[:,2]>-5.7)&(sc>-.6)&(sc<2.)],
        'near_layer_centroids':cent[(sc>-12)&(sc<30)&((cent[:,2]>-3.03)|(cent[:,2]<-5.7))][::3]}
for kind,pp in groups.items():
    records=[];nearest_dist=[];nearneg=0
    for p in pp:
        hit=rocks.find_nearest(Vector(p))
        if hit[0] is None:continue
        d=float((Vector(p)-hit[0]).dot(hit[1]));nearest_dist.append(d)
        if d<-.0005 and hit[3]<.4:
            nearneg+=1;records.append({'point':p.tolist(),'signed_nearest_distance_m':d,'euclidean_distance_m':float(hit[3]),'rock':names[hit[2]]})
    records.sort(key=lambda q:q['signed_nearest_distance_m'])
    for q in records[:20]:
        if q['rock'] in trees:q['core_ray_parity_counts']=h.parity(trees[q['rock']],Vector(q['point']))
    report['groups'][kind]={'tested':len(pp),'nearest_normal_inside_over_05mm':nearneg,'signed_nearest_min_m':min(nearest_dist),'worst_examples':records[:20]}
    print('CONTACT',kind,len(pp),nearneg,min(nearest_dist),flush=True)
report['limitations']='Nearest normal signs are contact diagnostics, not a complete inside predicate for open terrain. Worst core examples have independent three-ray parity counts. Layer centroid sampling is every third eligible triangle; all falling vertex/centroid points tested.'
report['source_unchanged']=hashlib.sha256(src.read_bytes()).hexdigest()==source_sha
(ROOT/f'qa/water12-surface{version}-contact.json').write_text(json.dumps(report,indent=2),encoding='utf8')
