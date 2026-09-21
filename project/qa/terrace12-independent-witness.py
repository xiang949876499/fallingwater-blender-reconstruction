"""Actual evaluated mesh BVH witnesses and finish support; no saved-scene changes."""
import json,math,sys,time
from pathlib import Path
from itertools import product
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
CASE=args[0] if args else '12a';assert CASE in ('12a','12b')
PREFIX='terrace12-independent' if CASE=='12a' else 'terrace12-independent-12b'
A=json.loads((R/'qa'/f'{PREFIX}-before-geometry.json').read_text());B=json.loads((R/'qa'/f'{PREFIX}-after-geometry.json').read_text())
def tree(g):
    # Complex Boolean n-gons must use the exact evaluated loop triangles,
    # not an independent BVH ngon triangulation that may bridge concavities.
    return BVHTree.FromPolygons([Vector(v) for v in g['vertices']],g['triangles'],all_triangles=True)
TA={n:tree(g) for n,g in A.items()};TB={n:tree(g) for n,g in B.items()}
def contains(t,p):
    v,n,f,d=t.find_nearest(Vector(p))
    return (Vector(p)-v).dot(n)<-1e-7
def odd(t,p):
    out=[]
    for d in [(1,.38131,.18311),(.17213,1,.45131),(.38131,.16111,1)]:
        direction=Vector(d).normalized();o=Vector(p);hits=[]
        for k in range(100):
            v,n,f,t0=t.ray_cast(o,direction,100)
            if v is None:break
            # At |Y|~18m the BVH uses float32; 1um advances can round to the
            # same face and count it repeatedly. 0.1mm is below every witness
            # clearance but above the coordinate ULP. Preserve attempt01 log.
            hits.append({'point':list(v),'normal':list(n),'polygon':f});o=v+direction*.0001
        out.append({'direction':list(direction),'count':len(hits),'inside':len(hits)%2==1,'hits':hits})
    assert len(set(x['inside'] for x in out))==1,('Ambiguous witness',p,out)
    return out
def nearest(t,p):
    v,n,f,d=t.find_nearest(Vector(p));return {'point':list(v),'normal':list(n),'polygon':f,'distance_m':d}
def first(trees,o,d):
    hits=[]
    for name,t in trees:
        v,n,f,dist=t.ray_cast(Vector(o),Vector(d),80)
        if v is not None:hits.append({'object':name,'point':list(v),'normal':list(n),'polygon':f,'distance_m':dist})
    return min(hits,key=lambda x:x['distance_m']) if hits else None
def top_samples(g,step=.15):
    out=set();top=g['bounds'][2][1]
    for face in g['polygons']:
        vv=[g['vertices'][i] for i in face]
        if not all(abs(v[2]-top)<1e-7 for v in vv):continue
        box=[(min(p[k] for p in vv),max(p[k] for p in vv)) for k in range(2)]
        axes=[]
        for a,b in box:
            n=max(1,math.ceil((b-a)/step));axes.append(sorted(set([a+.0001,b-.0001]+[a+(b-a)*(i+.5)/n for i in range(n)])))
        for x,y in product(*axes):out.add((x,y,top))
    return sorted(out)
rows=[];start=time.monotonic()
for part,wall,threshold in [('W','MAIN_L2_west_parapet_0','MAIN_floor_threshold_dressing_terrace'),('S','MAIN_L2_south_parapet_0','MAIN_floor_threshold_master_terrace')]:
    slab='MAIN_L2_TERRACE_'+part+'_slab';finish='MAIN_L2_TERRACE_'+part+'_finish';tb=TB[wall]
    xy=sorted(set((v[0],v[1]) for name in [slab,finish] for g in [A[name],B[name]] for v in g['vertices']))
    overlap=[];loss=[]
    for (x,y),dx,dy,z in product(xy,[-.05,-.04,-.03,-.02,-.01,-.004,-.001,.001,.004,.01,.02,.03,.04,.05],[-.05,-.04,-.03,-.02,-.01,-.004,-.001,.001,.004,.01,.02,.03,.04,.05],[2.625,2.63,2.64,2.72,2.83]):
        p=(x+dx,y+dy,z)
        if not contains(TA[slab],p):continue
        new=contains(TB[slab],p);w=contains(tb,p)
        if new and w:overlap.append((min(nearest(tb,p)['distance_m'],nearest(TB[slab],p)['distance_m']),p))
        elif not new and not w:loss.append((nearest(tb,p)['distance_m'],p))
    def record(items,kind):
        result=[];selected=[]
        for depth,p in sorted(items,reverse=True):
            if any((Vector(p)-Vector(q)).length<.2 for q in selected):continue
            selected.append(p)
            oldr,newr,wallr=odd(TA[slab],p),odd(TB[slab],p),odd(tb,p)
            expected=(oldr[0]['inside'] and newr[0]['inside'] and wallr[0]['inside']) if kind=='INSIDE_NEW_SLAB_AND_PARAPET' else (oldr[0]['inside'] and not newr[0]['inside'] and not wallr[0]['inside'])
            if not expected:continue
            result.append({'point':p,'depth_metric_m':depth,'kind':kind,
                           'before_slab_inside_three_rays':oldr,
                           'after_slab_inside_three_rays':newr,'actual_parapet_inside_three_rays':wallr,
                           'after_slab_nearest':nearest(TB[slab],p),'parapet_nearest':nearest(tb,p)})
            if len(result)==6:break
        return result
    profile=[]
    # Dense only at actual corner coordinates, with ordinary bottom-arris checks in extraction.
    for x,y in xy:
        for axis,sgn,u,z in product([0,1],[-1,1],[-.05,-.04,-.03,-.02,-.01,-.005,-.001,.001,.005,.01,.02,.03,.04,.05],[2.625,2.63,2.64,2.72,2.83]):
            p=[x,y,z];p[1-axis]+=u;p[axis]+=sgn*.2;d=[0,0,0];d[axis]=-sgn
            a=first([(slab,TA[slab]),(wall,TA[wall])],p,d);b=first([(slab,TB[slab]),(wall,TB[wall])],p,d)
            if a and b and a['distance_m']<.201 and b['distance_m']-a['distance_m']>1e-5:
                profile.append({'origin':p,'direction':d,'before':a,'after':b,'retreat_m':b['distance_m']-a['distance_m']})
    supports=[];excluded=[]
    for p in top_samples(B[finish]):
        # A point occupied by the solid parapet above finish is not walkable finish.
        if contains(tb,(p[0],p[1],p[2]+.05)):
            excluded.append(p);continue
        tests=[]
        for z in [2.6249,2.635,2.72,2.84479]:
            q=(p[0],p[1],z)
            old=any(contains(TA[n],q) for n in [slab,wall,threshold]);new=any(contains(TB[n],q) for n in [slab,wall,threshold])
            tests.append({'z':z,'before_occupied':old,'after_occupied':new})
        h=first([(slab,TB[slab]),(wall,TB[wall]),(threshold,TB[threshold])],(p[0],p[1],2.8449),(0,0,-1))
        supports.append({'finish_point':p,'column_samples':tests,'first_below_finish':h,
                         'introduced_missing_support':any(t['before_occupied'] and not t['after_occupied'] for t in tests) or h is None or abs(h['point'][2]-2.8448)>.00002})
    bad=[x for x in supports if x['introduced_missing_support']]
    row={'part':part,'sample_overlap_witness_count':len(overlap),'sample_union_loss_witness_count':len(loss),
         'overlap_witnesses':record(overlap,'INSIDE_NEW_SLAB_AND_PARAPET'),
         'loss_witnesses':record(loss,'INSIDE_OLD_SLAB_OUTSIDE_NEW_SLAB_AND_PARAPET'),
         'corner_profile_changed_count':len(profile),'largest_corner_axis_ray_retreat':max(profile,key=lambda x:x['retreat_m']) if profile else None,
         'top_corner_profiles':sorted(profile,key=lambda x:x['retreat_m'],reverse=True)[:12],
         'finish_support_sample_count':len(supports),'excluded_finish_points_inside_wall_above_count':len(excluded),
         'column_occupied_tests':len(supports)*4,'introduced_support_failure_count':len(bad),'introduced_support_failures':bad[:40],
         'support_probe_definition':'Actual top-finish quad cells at <=150mm spacing plus100micron inset boundaries; four Z levels of unchanged concrete slab thickness; compare before/after with actual bevel and thresholds; no saved-scene mutation.',
         'support_status':'PASS_SAMPLED' if not bad else 'FAIL'}
    if CASE=='12b':
        old_report=json.loads((R/'qa/terrace12-independent-witness.json').read_text())
        old_row=next(x for x in old_report['parts'] if x['part']==part)
        regression=[]
        for w in old_row['overlap_witnesses']+old_row['loss_witnesses']:
            p=w['point'];new_inside=odd(TB[slab],p);wall_inside=odd(tb,p)
            is_overlap='INSIDE_NEW_SLAB_AND' in w['kind']
            passed=(not new_inside[0]['inside'] and wall_inside[0]['inside']) if is_overlap else (new_inside[0]['inside'] and not wall_inside[0]['inside'])
            regression.append({'point':p,'old_failure':w['kind'],'new_slab_rays':new_inside,'unchanged_wall_rays':wall_inside,'regression_status':'PASS' if passed else 'FAIL'})
        row['negative12a_witness_regression']=regression
    rows.append(row);print('WITNESS12_PART',part,len(overlap),len(loss),len(supports),len(bad),flush=True)
out={'parts':rows,'seconds':time.monotonic()-start,'rendered':False,'scene_saved':False,'sample_witnesses_do_not_prove_absence':True}
(R/'qa'/f'{PREFIX}-witness.json').write_text(json.dumps(out,indent=2),encoding='utf8')
