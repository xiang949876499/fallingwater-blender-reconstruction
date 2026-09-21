"""Probe finite coplanar face area and independently check volume arithmetic."""
import json,math,time
from pathlib import Path
R=Path(__file__).resolve().parents[1]
code=(R/'qa/terrace12-independent-12b-volume.py').read_text().split('start=time.monotonic();tests=lib')[0]
ns={'__file__':str(R/'qa/terrace12-independent-12b-volume.py')};exec(compile(code,'12b-volume:def-only','exec'),ns)
sub,cross,dot,mean=[ns[k] for k in ['sub','cross','dot','mean']]
def unit(v):
    l=math.sqrt(dot(v,v));return tuple(x/l for x in v)
def tri_state(g):
    v=g['vertices'];out=[]
    for ids in g['triangles']:
        p=[tuple(v[i]) for i in ids];n=unit(cross(sub(p[1],p[0]),sub(p[2],p[0])))
        out.append((p,n,dot(n,p[0])))
    return out
def area2(p):return abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(p,p[1:]+p[:1])))*.5 if len(p)>2 else 0.
def cross2(a,b):return a[0]*b[1]-a[1]*b[0]
def intersection_area(p,q):
    # Put both projected triangles in CCW order and clip p to q's three planes.
    if cross2(sub(q[1],q[0]),sub(q[2],q[0]))<0:q=list(reversed(q))
    for a,b in zip(q,q[1:]+q[:1]):
        out=[]
        for x,y in zip(p,p[1:]+p[:1]):
            dx=cross2(sub(b,a),sub(x,a));dy=cross2(sub(b,a),sub(y,a));ix=dx>=-1e-13;iy=dy>=-1e-13
            if ix:out.append(x)
            if ix!=iy:
                t=dx/(dx-dy);out.append(tuple(x[k]+t*(y[k]-x[k]) for k in range(2)))
        p=out
        if len(p)<3:return 0.
    return area2(p)
def surface_pairs(a,b):
    rows=[]
    for i,(p,n,c) in enumerate(tri_state(a)):
        k=max(range(3),key=lambda k:abs(n[k]));axes=[j for j in range(3) if j!=k]
        pp=[tuple(v[j] for j in axes) for v in p]
        for j,(q,m,d) in enumerate(tri_state(b)):
            alignment=dot(n,m)
            # Normals must point the same way. Opposite normals are a valid
            # internal mating interface, not two outward render surfaces.
            if alignment<1-1e-10 or max(abs(dot(n,x)-c) for x in q)>1e-8:continue
            qq=[tuple(v[h] for h in axes) for v in q]
            area=intersection_area(pp,qq)/abs(n[k])
            if area>1e-12:rows.append({'slab_triangle':i,'parapet_triangle':j,'overlap_area_m2':area,'normal_alignment':alignment})
    return rows
start=time.monotonic();A=json.loads((R/'qa/terrace12-independent-12b-before-geometry.json').read_text());B=json.loads((R/'qa/terrace12-independent-12b-after-geometry.json').read_text());rows=[]
for part,wall in [('W','MAIN_L2_west_parapet_0'),('S','MAIN_L2_south_parapet_0')]:
    slab='MAIN_L2_TERRACE_'+part+'_slab';oldpairs=surface_pairs(A[slab],A[wall]);newpairs=surface_pairs(B[slab],B[wall]);origin=mean(B[wall]['vertices'])
    shifted={n:g|{'vertices':[sub(v,origin) for v in g['vertices']]} for n,g in B.items() if n in [slab,wall]}
    sa=ns['prepared'](shifted[slab]);wa=ns['prepared'](shifted[wall])
    print('PRECISION12B_SHIFTED_SWAP',part,flush=True)
    value=math.fsum(a[0]*b[0]*ns['pair_intersect'](b,a) for a in sa for b in wa)
    row={'part':part,'before_same_direction_coplanar_area_m2':sum(p['overlap_area_m2'] for p in oldpairs),
         'after_same_direction_coplanar_area_m2':sum(p['overlap_area_m2'] for p in newpairs),'after_coplanar_pairs':newpairs,
         'plane_matching_tolerance_m':1e-8,'area_reporting_threshold_m2':1e-12,
         'shifted_world_origin':origin,'reverse_order_and_shifted_overlap_m3':value}
    rows.append(row);print('PRECISION12B',json.dumps(row),flush=True)
out={'parts':rows,'seconds':time.monotonic()-start,'rendered':False,'scene_mutated':False}
(R/'qa/terrace12-independent-12b-precision.json').write_text(json.dumps(out,indent=2),encoding='utf8')
