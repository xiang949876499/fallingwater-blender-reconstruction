"""General evaluated-mesh volume and Boolean-result QA for candidate12b.

Signed triangle tetrahedra are integrated by exact half-space polyhedral clipping
(double precision). No source builder boxes or Boolean modifier calls. This
supports the non-orthogonal curved matching surfaces introduced in candidate12b.
"""
import json,math,time,runpy
from pathlib import Path
R=Path(__file__).resolve().parents[1]
# Execute only reusable definitions from the frozen orthogonal checker, never
# its source-specific data analysis or writes.
code=(R/'qa/terrace12-independent-volume.py').read_text().split('start=time.monotonic();tests=selftests()')[0]
lib={'__file__':str(R/'qa/terrace12-independent-volume.py')};exec(compile(code,'terrace12-independent-volume.py:def-only','exec'),lib)
sub,cross,dot,mean,bounds=[lib[k] for k in ['sub','cross','dot','mean','bounds']]
tetra_faces=lib['tetra_faces'];mesh_volume=lib['mesh_volume'];tetra_decomposition=lib['tetra_decomposition']
def clip_plane(faces,n,c):
    out=[];cut=[]
    for face in faces:
        q=[]
        for a,b in zip(face,face[1:]+face[:1]):
            da=dot(n,a)-c;db=dot(n,b)-c;ia=da<=1e-12;ib=db<=1e-12
            if ia:q.append(a)
            if ia!=ib:
                s=da/(da-db);p=tuple(a[k]+s*(b[k]-a[k]) for k in range(3));q.append(p);cut.append(p)
        if len(q)>=3:out.append(q)
    cut=list({tuple(round(x,10) for x in p):p for p in cut}.values())
    if len(cut)>=3:
        p=mean(cut);k=min(range(3),key=lambda k:abs(n[k]));e=tuple(1. if i==k else 0. for i in range(3))
        u=cross(e,n);u=tuple(x/math.sqrt(dot(u,u)) for x in u);v=cross(n,u)
        cut.sort(key=lambda a:math.atan2(dot(sub(a,p),v),dot(sub(a,p),u)))
        out.append(cut)
    return out
def polyvolume(faces):
    if not faces:return 0.
    o=mean([p for f in faces for p in f])
    v=math.fsum(dot(sub(f[0],o),cross(sub(f[i],o),sub(f[i+1],o)))/6 for f in faces for i in range(1,len(f)-1))
    assert v>=-1e-8,v
    return max(v,0.)
def prepared(g):
    out=[]
    for sign,t,bb in tetra_decomposition(g):
        faces=tetra_faces(t);planes=[]
        for f in faces:
            n=cross(sub(f[1],f[0]),sub(f[2],f[0]));length=math.sqrt(dot(n,n))
            if length<1e-13:continue
            n=tuple(x/length for x in n);planes.append((n,dot(n,f[0])))
        assert len(planes)==4
        out.append((sign,t,bb,faces,planes))
    return out
def pair_intersect(a,b):
    _,t,bb,faces,_=a;_,u,cc,_,planes=b
    if any(bb[k][1]<=cc[k][0]+1e-12 or cc[k][1]<=bb[k][0]+1e-12 for k in range(3)):return 0.
    for n,c in planes:
        ds=[dot(n,p)-c for p in t]
        if min(ds)>-1e-12:return 0.
        if max(ds)>1e-12:faces=clip_plane(faces,n,c)
        if not faces:return 0.
    return polyvolume(faces)
def test_tetra():
    t=((0.,0.,0.),(1.,0.,0.),(0.,1.,0.),(0.,0.,1.));faces=tetra_faces(t)
    def state(t):
        f=tetra_faces(t);planes=[]
        for x in f:
            n=cross(sub(x[1],x[0]),sub(x[2],x[0]));n=tuple(k/math.sqrt(dot(n,n)) for k in n);planes.append((n,dot(n,x[0])))
        return (1,t,bounds(t),f,planes)
    a=state(t);rows=[]
    for u,expected in [(t,1/6),(tuple(tuple(p[k]+(.5 if k==0 else 0) for k in range(3)) for p in t),1/48),(tuple(tuple(p[k]+2 for k in range(3)) for p in t),0.)]:
        v=pair_intersect(a,state(u));assert abs(v-expected)<1e-11,(v,expected);rows.append([v,expected])
    return rows
start=time.monotonic();tests=lib['selftests']()+test_tetra()
A=json.loads((R/'qa/terrace12-independent-12b-before-geometry.json').read_text());B=json.loads((R/'qa/terrace12-independent-12b-after-geometry.json').read_text())
history=json.loads((R/'qa/terrace12-independent-volume.json').read_text())
rows=[]
for part,wall in [('W','MAIN_L2_west_parapet_0'),('S','MAIN_L2_south_parapet_0')]:
    slab='MAIN_L2_TERRACE_'+part+'_slab';old,new=A[slab],B[slab];assert A[wall]==B[wall]
    cells=lib['grid_cells'](old,old)[0];nv=mesh_volume(new);inside_old=lib['intersection'](cells,tetra_decomposition(new))
    sa,wa=prepared(new),prepared(B[wall]);print('12B_PAIRS',part,len(sa),len(wa),flush=True)
    overlap=math.fsum(a[0]*b[0]*pair_intersect(a,b) for a in sa for b in wa)
    previous=next(x for x in history['parts'] if x['part']==part)
    before_union=previous['before_slab_m3']+previous['actual_parapet_m3']-previous['before_slab_actual_parapet_overlap_m3']
    after_union=nv+mesh_volume(B[wall])-overlap
    row={'part':part,'actual_slab_volume_m3':nv,'actual_slab_inside_original_slab_volume_m3':inside_old,
         'new_slab_volume_outside_original_slab_m3':nv-inside_old,'actual_parapet_volume_m3':mesh_volume(B[wall]),
         'actual_slab_parapet_overlap_m3':overlap,'before_union_volume_m3':before_union,'after_union_volume_m3':after_union,
         'lost_union_volume_m3':before_union-after_union,'edge_degree_counts':new['edge_degree_counts'],
         'degenerate_triangles':new['degenerate_triangle_count'],'slab_modifier_stack':new['modifiers'],
         'closed_positive_status':'PASS' if set(new['edge_degree_counts'])=={'2'} and nv>0 and new['degenerate_triangle_count']==0 else 'FAIL',
         'zero_intersection_status':'PASS' if abs(overlap)<1e-8 else 'FAIL',
         'same_union_status':'PASS' if abs(before_union-after_union)<1e-8 and abs(nv-inside_old)<1e-8 else 'FAIL'}
    print('12B_VOLUME',json.dumps(row),flush=True);rows.append(row)
out={'method':__doc__,'parts':rows,'analytic_clipping_tests':tests,'volume_numerical_tolerance_m3':1e-8,'seconds':time.monotonic()-start,'scene_mutated':False,'rendered':False}
(R/'qa/terrace12-independent-12b-volume.json').write_text(json.dumps(out,indent=2),encoding='utf8')
