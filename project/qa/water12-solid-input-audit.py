"""Read-only diagnosis of the failed static inputs; no saved scene or simulation."""
import sys,json,hashlib,time
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import water12_complete_geometry as g
import hybrid_water as h
P=ROOT/'qa';SCENE=ROOT/'scene/Fallingwater_water12_near_failed.blend'
before=hashlib.sha256(SCENE.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(SCENE))
assert not any(m.type=='FLUID' for o in bpy.data.objects for m in o.modifiers)
terrain=h.render_bvh(bpy.data.objects['SITE_Continuous_BearRun_Terrain'])
temp=bpy.data.collections.new('READONLY_AUDIT_MEMORY_ONLY');bpy.context.scene.collection.children.link(temp)
body,rec=g.body_from_top(bpy.data.objects['W12_Near_Top'],terrain,temp)
assert abs(rec['initial_topology']['signed_volume_m3']-563.7572365436401)<1e-4
def audit(o):
    o.data.calc_loop_triangles();v=np.array([tuple(o.matrix_world@p.co) for p in o.data.vertices]);f=np.array([tuple(t.vertices) for t in o.data.loop_triangles]);tri=v[f]
    area=.5*np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)
    labels=np.array(g.components(o));records=[]
    for label in sorted(set(labels)):
        ff=f[labels[f[:,0]]==label];vv=v[ff];center=vv.reshape(-1,3).mean(0);tt=vv-center
        volume=float(np.einsum('ij,ij->i',tt[:,0],np.cross(tt[:,1],tt[:,2])).sum()/6)
        records.append({'label':int(label),'triangles':len(ff),'signed_volume_m3':volume})
    bvh=BVHTree.FromPolygons(v,f,all_triangles=True);candidates=bvh.overlap(bvh);crossings=[];tested=0;raw_unshared=0
    for a,b in candidates:
        if a>=b or set(f[a])&set(f[b]):continue
        raw_unshared+=1
        if area[a]<1e-12 or area[b]<1e-12:continue
        tested+=1;hit=None
        for ia,ib in [(a,b),(b,a)]:
            t=[Vector(q) for q in tri[ib]]
            for e0,e1 in zip(tri[ia],np.roll(tri[ia],-1,axis=0)):
                start=Vector(e0);direction=Vector(e1-e0)
                if direction.length<1e-8:continue
                p=intersect_ray_tri(t[0],t[1],t[2],direction,start,True)
                if p is not None:
                    u=(p-start).dot(direction)/direction.length_squared
                    if 1e-5<u<1-1e-5:hit={'triangle_pair':[int(a),int(b)],'point':list(p),'segment_fraction':u};break
            if hit:break
        if hit:
            def skin(k):
                return 'top' if (f[k]<len(v)//2).all() else ('bottom' if (f[k]>=len(v)//2).all() else 'side')
            hit['skin_pair']=[skin(a),skin(b)] if o==body else ['NOT_APPLICABLE','NOT_APPLICABLE'];crossings.append(hit)
    return {'object':o.name,'topology':h.topology(o),'components':records,'triangle_count':len(f),'degenerate_triangles_below1e12_m2':int((area<1e-12).sum()),'minimum_triangle_area_m2':float(area.min()),
      'nonadjacent_BVH_candidate_pairs':raw_unshared,'segment_triangle_pairs_tested':tested,'confirmed_nonadjacent_segment_triangle_crossings':len(crossings),'crossing_examples':crossings[:40],
      'crossing_point_bounds_m':np.stack((np.array([q['point'] for q in crossings]).min(0),np.array([q['point'] for q in crossings]).max(0)),1).tolist() if crossings else None,
      'crossings_inside_current_contact_ROI':sum(-33<=q['point'][0]<=20 and -32<=q['point'][1]<=10 for q in crossings),
      'crossings_in_water10_XY_domain':sum(-16<=q['point'][0]<=8 and -17<=q['point'][1]<=6 for q in crossings),
      'crossings_above_minus4m':sum(q['point'][2]>-4 for q in crossings),
      'crossing_examples_in_current_contact_ROI':[q for q in crossings if -33<=q['point'][0]<=20 and -32<=q['point'][1]<=10][:30],
      'skin_pair_counts':{pair:sum('/'.join(sorted(q['skin_pair']))==pair for q in crossings) for pair in sorted({'/'.join(sorted(q['skin_pair'])) for q in crossings})},
      'limitations':'Pairs sharing mesh vertices and strictly coplanar overlaps not tested; zero crossings is not a full self-intersection certificate.'}
r={'status':'FAILED_STATIC_INPUTS_READONLY_AUDIT','failed_scene_sha256':before,'reconstructed_near_body_matches_preunion_volume':True,
   'near_river':audit(body),'branch1':audit(bpy.data.objects['W12_C_Branch_Region_01']),'new_bake':False,'new_render':False,'new_scene_save':False}
assert hashlib.sha256(SCENE.read_bytes()).hexdigest()==before;r['failed_scene_file_unchanged']=True
(P/'water12-solid-input-audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
print('WATER12_INPUT_AUDIT',[(key,r[key]['confirmed_nonadjacent_segment_triangle_crossings'],r[key]['degenerate_triangles_below1e12_m2']) for key in ['near_river','branch1']],flush=True)
