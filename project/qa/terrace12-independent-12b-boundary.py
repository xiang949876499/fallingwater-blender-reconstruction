"""Double-precision actual-triangle boundary and thin-piece point checks.

No normal-sign assumption at a nearest edge and no iterative ray advance that
could step across the very thin matching wedges produced by the Boolean.
"""
import json,math,time
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]
A=json.loads((R/'qa/terrace12-independent-12b-before-geometry.json').read_text());B=json.loads((R/'qa/terrace12-independent-12b-after-geometry.json').read_text())
class Mesh:
    def __init__(self,g):
        self.g=g;self.v=np.array(g['vertices'],dtype=np.float64);self.t=self.v[np.array(g['triangles'])]
        self.a=self.t[:,0];self.e1=self.t[:,1]-self.a;self.e2=self.t[:,2]-self.a
        self.n=np.cross(self.e1,self.e2);self.n/=np.sqrt(np.sum(self.n*self.n,axis=1))[:,None]
        self.d00=np.sum(self.e1*self.e1,axis=1);self.d01=np.sum(self.e1*self.e2,axis=1);self.d11=np.sum(self.e2*self.e2,axis=1);self.den=self.d00*self.d11-self.d01*self.d01
        self.rays={}
    def ray(self,p,d):
        key=tuple(d)
        if key not in self.rays:
            dd=np.array(d);dd=dd/np.linalg.norm(dd);h=np.cross(dd,self.e2);det=np.sum(self.e1*h,axis=1);valid=np.abs(det)>1e-13
            inv=np.zeros_like(det);inv[valid]=1/det[valid];self.rays[key]=(dd,h,valid,inv)
        dd,h,valid,inv=self.rays[key];s=np.array(p)-self.a;u=np.sum(s*h,axis=1)*inv;q=np.cross(s,self.e1);v=np.sum(dd*q,axis=1)*inv;dist=np.sum(self.e2*q,axis=1)*inv
        ids=np.where(valid&(u>=-1e-10)&(v>=-1e-10)&(u+v<=1+1e-10)&(dist>1e-9))[0];ids=sorted(ids,key=lambda i:dist[i]);hits=[]
        for i in ids:
            if not hits or dist[i]-hits[-1]['distance_m']>1e-8:hits.append({'triangle':int(i),'distance_m':float(dist[i])})
        return {'inside':bool(len(hits)%2),'hits':hits,'direction':list(dd)}
    def inside(self,p):return self.ray(p,(.17913,.41371,1))['inside']
    def verified(self,p):
        rr=[self.ray(p,d) for d in [(1,.38131,.18311),(.17213,1,.45131),(.38131,.16111,1)]]
        return {'inside':rr[0]['inside'] if len(set(r['inside'] for r in rr))==1 else None,'rays':rr}
    def closest(self,p):
        p=np.array(p);delta=p-self.a;dist=np.sum(delta*self.n,axis=1);proj=p-dist[:,None]*self.n;w=proj-self.a
        d20=np.sum(w*self.e1,axis=1);d21=np.sum(w*self.e2,axis=1);u=(self.d11*d20-self.d01*d21)/self.den;v=(self.d00*d21-self.d01*d20)/self.den
        good=(u>=-1e-12)&(v>=-1e-12)&(u+v<=1+1e-12);best=dist*dist;best[~good]=np.inf;points=proj.copy()
        for k in range(3):
            a=self.t[:,k];e=self.t[:,(k+1)%3]-a;s=np.clip(np.sum((p-a)*e,axis=1)/np.sum(e*e,axis=1),0,1);q=a+s[:,None]*e;dd=np.sum((p-q)**2,axis=1);replace=dd<best;best[replace]=dd[replace];points[replace]=q[replace]
        i=int(np.argmin(best));return {'triangle':i,'point':points[i].tolist(),'normal':self.n[i].tolist(),'distance_m':float(math.sqrt(best[i])),'signed_plane_distance_m':float(np.dot(p-points[i],self.n[i]))}
MA={n:Mesh(g) for n,g in A.items()};MB={n:Mesh(g) for n,g in B.items()}
def finish_samples(g,step=.15):
    from itertools import product
    out=set();top=g['bounds'][2][1]
    for face in g['polygons']:
        vv=[g['vertices'][i] for i in face]
        if not all(abs(v[2]-top)<1e-7 for v in vv):continue
        box=[(min(p[k] for p in vv),max(p[k] for p in vv)) for k in range(2)];axes=[]
        for a,b in box:
            n=max(1,math.ceil((b-a)/step));axes.append(sorted(set([a+.0001,b-.0001]+[a+(b-a)*(i+.5)/n for i in range(n)])))
        for x,y in product(*axes):out.add((x,y,top))
    return sorted(out)
start=time.monotonic();history=json.loads((R/'qa/terrace12-independent-witness.json').read_text());provisional=json.loads((R/'qa/terrace12-independent-12b-witness.json').read_text());rows=[]
for part,wall,threshold in [('W','MAIN_L2_west_parapet_0','MAIN_floor_threshold_dressing_terrace'),('S','MAIN_L2_south_parapet_0','MAIN_floor_threshold_master_terrace')]:
    slab='MAIN_L2_TERRACE_'+part+'_slab';finish='MAIN_L2_TERRACE_'+part+'_finish';m=MB[slab];w=MB[wall]
    interfaces=[];samples=[]
    for i,tri in enumerate(m.t):
        center=tri.mean(axis=0);near=w.closest(center)
        if near['distance_m']>5e-5 or np.dot(m.n[i],near['normal'])>-.5:continue
        # Reject a merely neighbouring exterior face: all three vertices must
        # also lie within50um of the actual opposite mating surface.
        if max(w.closest(p)['distance_m'] for p in tri)>5e-5:continue
        interfaces.append(i)
        for a in range(5):
            for b in range(5-a):
                c=4-a-b;p=(a*tri[0]+b*tri[1]+c*tri[2])/4;near=w.closest(p)
                samples.append({'slab_triangle':i,'point':p.tolist(),'wall_closest':near})
    worst=max(samples,key=lambda x:x['wall_closest']['distance_m']);regression=[]
    old=next(x for x in history['parts'] if x['part']==part)
    for q in old['overlap_witnesses']+old['loss_witnesses']:
        p=q['point'];sr=m.verified(p);wr=w.verified(p);isover='INSIDE_NEW_SLAB_AND' in q['kind']
        good=(sr['inside'] is False and wr['inside'] is True) if isover else (sr['inside'] is True and wr['inside'] is False)
        regression.append({'point':p,'old_failure_kind':q['kind'],'new_slab':sr,'unchanged_wall':wr,'status':'PASS' if good else 'FAIL'})
    # Recheck provisional near-edge classifications with all triangle hits.
    previous=next(x for x in provisional['parts'] if x['part']==part);edge_rechecks=[]
    for q in previous['loss_witnesses']:
        p=q['point'];sr=m.verified(p);wr=w.verified(p)
        edge_rechecks.append({'point':p,'new_slab':sr,'wall':wr,'actual_loss_confirmed':sr['inside'] is False and wr['inside'] is False})
    supports=[];excluded=0
    for p in finish_samples(B[finish]):
        if w.inside((p[0],p[1],p[2]+.05)):excluded+=1;continue
        bad=[]
        for z in [2.6249,2.635,2.72,2.84479]:
            q=(p[0],p[1],z);old=any(MA[n].inside(q) for n in [slab,wall,threshold]);new=any(MB[n].inside(q) for n in [slab,wall,threshold])
            if old and not new:bad.append(z)
        supports.append({'point':p,'new_missing_z':bad})
    row={'part':part,'actual_matching_triangle_count':len(interfaces),'interface_sample_count':len(samples),
         'maximum_sampled_boundary_distance_m':worst['wall_closest']['distance_m'],'worst_boundary_sample':worst,
         'signed_boundary_sample_range_m':[min(x['wall_closest']['signed_plane_distance_m'] for x in samples),max(x['wall_closest']['signed_plane_distance_m'] for x in samples)],
         'world_float32_coordinate_ULP_max_m':float(np.max(np.abs(np.spacing(m.v.astype(np.float32))))),
         'top_boundary_samples':sorted(samples,key=lambda x:x['wall_closest']['distance_m'],reverse=True)[:10],
         'negative12a_regression':regression,'near_edge_provisional_loss_rechecks':edge_rechecks,
         'finish_support_locations':len(supports),'finish_support_column_samples':len(supports)*4,'finish_inside_wall_exclusions':excluded,
         'introduced_missing_support':[x for x in supports if x['new_missing_z']],
         'boundary_limit_statement':'Reported maximum is a sampled actual point-to-triangle distance (15 barycentric locations per matching triangle), not an exact continuous Hausdorff bound.',
         'ray_method':'Double precision all evaluated loop triangles, deduplicate same crossing within1e-8m, no ray-origin stepping; three independent directions for every negative witness.'}
    rows.append(row);print('BOUNDARY12B',part,row['maximum_sampled_boundary_distance_m'],len(samples),len(row['introduced_missing_support']),flush=True)
out={'parts':rows,'seconds':time.monotonic()-start,'rendered':False,'scene_saved':False,'method':__doc__}
(R/'qa/terrace12-independent-12b-boundary.json').write_text(json.dumps(out,indent=2),encoding='utf8')
