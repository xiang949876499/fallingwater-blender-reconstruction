"""Independent exact piecewise-polyhedral volume audit from evaluated triangles.

No construction boxes, Boolean helper, or saved-scene mutation. Each slab is
partitioned at its actual evaluated vertex coordinates. Wall intersection uses
the signed tetrahedron integral of its closed oriented evaluated triangle mesh;
tetrahedra are clipped against the independent slab cells with double precision.
"""
import json, math, time
from pathlib import Path
from itertools import product
R=Path(__file__).resolve().parents[1]
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def mean(v):return tuple(sum(p[k] for p in v)/len(v) for k in range(3))
def bounds(v):return [(min(p[k] for p in v),max(p[k] for p in v)) for k in range(3)]
def mesh_volume(g):
    v=g['vertices'];o=mean(v)
    return math.fsum(dot(sub(v[a],o),cross(sub(v[b],o),sub(v[c],o)))/6 for a,b,c in g['triangles'])
def tetra_faces(t):
    c=mean(t);out=[]
    for inds in [(0,1,2),(0,1,3),(0,2,3),(1,2,3)]:
        face=[t[i] for i in inds]
        if dot(cross(sub(face[1],face[0]),sub(face[2],face[0])),sub(mean(face),c))<0:face.reverse()
        out.append(face)
    return out
def clip_faces(faces,axis,bound,sign):
    out=[];cut=[]
    for face in faces:
        q=[]
        for a,b in zip(face,face[1:]+face[:1]):
            da=sign*(a[axis]-bound);db=sign*(b[axis]-bound)
            ia=da<=1e-12;ib=db<=1e-12
            if ia:q.append(a)
            if ia!=ib:
                t=da/(da-db);p=tuple(a[k]+t*(b[k]-a[k]) for k in range(3));q.append(p);cut.append(p)
        if len(q)>=3:out.append(q)
    unique={tuple(round(x,10) for x in p):p for p in cut};cut=list(unique.values())
    if len(cut)>=3:
        c=mean(cut);a=(axis+1)%3;b=(axis+2)%3
        cut.sort(key=lambda p:math.atan2(p[b]-c[b],p[a]-c[a]),reverse=sign<0)
        out.append(cut)
    return out
def clipped_tetra_volume(t,bb,box):
    if any(bb[k][1]<=box[k][0] or bb[k][0]>=box[k][1] for k in range(3)):return 0.
    faces=tetra_faces(t)
    for k in range(3):
        if bb[k][0]<box[k][0]:faces=clip_faces(faces,k,box[k][0],-1)
        if bb[k][1]>box[k][1]:faces=clip_faces(faces,k,box[k][1],1)
        if not faces:return 0.
    o=mean([p for f in faces for p in f]);volume=math.fsum(dot(sub(f[0],o),cross(sub(f[i],o),sub(f[i+1],o)))/6 for f in faces for i in range(1,len(f)-1))
    assert volume>=-1e-10,volume
    return max(0.,volume)
def cell_volume(box):return math.prod(b-a for a,b in box)
def cell_center(box):return tuple((a+b)*.5 for a,b in box)
def rect_faces(g):
    faces=[]
    for p in g['polygons']:
        v=[g['vertices'][i] for i in p];bb=bounds(v);axes=[k for k in range(3) if bb[k][1]-bb[k][0]<1e-10]
        assert len(axes)==1,('Non-orthogonal slab face',v)
        faces.append((axes[0],bb))
    return faces
def rect_contains(faces,p):
    xs=set()
    for axis,bb in faces:
        if axis==0 and bb[0][0]>p[0]+1e-10 and bb[1][0]-1e-10<p[1]<bb[1][1]+1e-10 and bb[2][0]-1e-10<p[2]<bb[2][1]+1e-10:
            xs.add(bb[0][0])
    return len(xs)%2==1
def grid_cells(a,b):
    coords=[sorted(set(p[k] for g in [a,b] for p in g['vertices'])) for k in range(3)]
    fa,fb=rect_faces(a),rect_faces(b);before=[];after=[];removed=[];added=[]
    for i,j,k in product(*(range(len(c)-1) for c in coords)):
        box=tuple((coords[n][ii],coords[n][ii+1]) for n,ii in enumerate((i,j,k)))
        p=cell_center(box);old=rect_contains(fa,p);new=rect_contains(fb,p)
        if old:before.append(box)
        if new:after.append(box)
        if old and not new:removed.append(box)
        if new and not old:added.append(box)
    return before,after,removed,added
def tetra_decomposition(g):
    v=g['vertices'];o=mean(v);out=[]
    for a,b,c in g['triangles']:
        sv=dot(sub(v[a],o),cross(sub(v[b],o),sub(v[c],o)))/6
        if abs(sv)<1e-15:continue
        t=(o,tuple(v[a]),tuple(v[b]),tuple(v[c]));out.append((1 if sv>0 else -1,t,bounds(t)))
    return out
def intersection(cells,tetras):
    return math.fsum(sign*clipped_tetra_volume(t,bb,box) for box in cells for sign,t,bb in tetras)
def selftests():
    t=((0.,0.,0.),(1.,0.,0.),(0.,1.,0.),(0.,0.,1.));bb=bounds(t)
    rows=[]
    for box,expected in [(((-1,2),(-1,2),(-1,2)),1/6),(((0,.5),(0,1),(0,1)),7/48),(((0,.1),(0,.1),(0,.1)),.001),(((2,3),(2,3),(2,3)),0)]:
        actual=clipped_tetra_volume(t,bb,box);assert abs(actual-expected)<1e-12,(actual,expected);rows.append([actual,expected])
    return rows
start=time.monotonic();tests=selftests()
before=json.loads((R/'qa/terrace12-independent-before-geometry.json').read_text());after=json.loads((R/'qa/terrace12-independent-after-geometry.json').read_text())
rows=[]
for part,wall in [('W','MAIN_L2_west_parapet_0'),('S','MAIN_L2_south_parapet_0')]:
    name='MAIN_L2_TERRACE_'+part+'_slab';a,b=before[name],after[name];assert before[wall]==after[wall]
    old,new,removed,added=grid_cells(a,b)
    va,vb=mesh_volume(a),mesh_volume(b);ca,cb=sum(map(cell_volume,old)),sum(map(cell_volume,new))
    assert abs(va-ca)<1e-8 and abs(vb-cb)<1e-8,(va,ca,vb,cb)
    print('VOLUME12_START',part,len(old),len(new),len(removed),flush=True)
    tetras=tetra_decomposition(after[wall]);overlap=intersection(new,tetras);removed_overlap=intersection(removed,tetras)
    complete_wall_clip=intersection([bounds(after[wall]['vertices'])],tetras)
    assert abs(complete_wall_clip-mesh_volume(after[wall]))<1e-8
    overlap_cells=[{'bounds':box,'overlap_m3':intersection([box],tetras)} for box in new]
    overlap_cells=[x for x in overlap_cells if x['overlap_m3']>1e-8]
    lost_cells=[{'bounds':box,'lost_union_m3':cell_volume(box)-intersection([box],tetras)} for box in removed]
    lost_cells=[x for x in lost_cells if x['lost_union_m3']>1e-8]
    lost=math.fsum(map(cell_volume,removed))-removed_overlap
    row={'part':part,'slab':name,'parapet':wall,'before_slab_m3':va,'after_slab_m3':vb,'actual_parapet_m3':mesh_volume(after[wall]),
         'before_slab_cell_volume_m3':ca,'after_slab_cell_volume_m3':cb,'after_slab_cell_count':len(new),'removed_cell_count':len(removed),'added_cell_count':len(added),
         'removed_slab_volume_m3':va-vb,'removed_volume_already_occupied_by_actual_parapet_m3':removed_overlap,
         'after_slab_actual_parapet_overlap_m3':overlap,'before_slab_actual_parapet_overlap_m3':overlap+removed_overlap,
         'lost_slab_parapet_union_m3':lost,'lost_union_litres':lost*1000,
         'zero_overlap_status':'PASS' if abs(overlap)<1e-8 else 'FAIL',
         'exact_union_preserved_status':'PASS' if abs(lost)<1e-8 else 'FAIL',
         'closed_positive_status':'PASS' if b['edge_degree_counts']=={'2':sum(b['edge_degree_counts'].values())} and vb>0 and b['degenerate_triangle_count']==0 else 'FAIL',
         'complete_actual_wall_clip_matches_signed_mesh_volume_m3':complete_wall_clip,
         'overlap_cells':overlap_cells,'lost_union_cells':lost_cells,'removed_cells':removed}
    rows.append(row);print('VOLUME12_RESULT',json.dumps({k:v for k,v in row.items() if k!='removed_cells'}),flush=True)
out={'method':__doc__,'floating_volume_tolerance_m3':1e-8,'clipping_selftests':tests,'parts':rows,'seconds':time.monotonic()-start,'scene_mutated':False,'rendered':False}
(R/'qa/terrace12-independent-volume.json').write_text(json.dumps(out,indent=2),encoding='utf8')
