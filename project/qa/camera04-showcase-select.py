"""Tree-aware guest showcase camera candidates; no scene or geometry mutation."""
import sys,json,math,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import bpy
from mathutils import Vector
import camera_review as cr
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene/Fallingwater_iteration04.blend'))
scene=bpy.context.scene
pool_near='--pool-near' in sys.argv
ray_bounds=(-8,12,-4,55,56,32) if pool_near else None
geo=cr.Geometry(scene,exclude_vegetation=False,bounds=ray_bounds)
if ray_bounds:
    original_ray=geo.ray
    def bounded_ray(origin,direction,length):
        a=Vector(origin);b=a+Vector(direction).normalized()*length
        if any(min(a[k],b[k])<ray_bounds[k] or max(a[k],b[k])>ray_bounds[k+3] for k in range(3)):
            raise ValueError('Requested ray exits conservative evaluated-object culling bounds')
        return original_ray(origin,direction,length)
    geo.ray=bounded_ray
d=json.loads((ROOT/'data/guest_house.json').read_text(encoding='utf-8'))
def p(q,z):return Vector((3.4+(q[0]-325)*.05256,37.1+(422-q[1])*.05272,z))
roof_groups={r['id']:[p(q,8.4+d['levels'][r['level']]['offset']+r['height']+.19) for q in r['polygon']] for r in d['roofs']}
roof_points=sum(roof_groups.values(),[])
front=[]
for w in d['walls']:
    base=8.4+d['levels'][w['level']]['offset'];a=p(w['a'],base+1.2);b=p(w['b'],base+1.2)
    for t in (.1,.5,.9):front.append(a.lerp(b,t))
poolcenter=p(d['pool']['center'],8.96485)
pool=[poolcenter+Vector((x*d['pool']['size_m'][0]*.48,y*d['pool']['size_m'][1]*.46,0)) for x,y in ((-1,-1),(-1,1),(1,1),(1,-1),(0,0))]
if pool_near:
    # A pool detail need not include the far service-wing roof. Keep the entire
    # basin plus its immediate east living-wing roof, explicitly recorded below.
    roof_points=[q for q in roof_groups['GUEST_LOW_ARM_ROOF'] if q.x>9]
    front=[q for q in front if q.x>9 and q.z<11]
all_targets=roof_points+front+pool
veg_names={o.name for o in geo.objects.values() if any(c.name=='50_VEGETATION' for c in o.users_collection)}
def assess(eye,target,lens,required):
    eye=Vector(eye);target=Vector(target);fwd=(target-eye).normalized();right=fwd.cross(Vector((0,0,1))).normalized();up=right.cross(fwd).normalized()
    # 36mm horizontal sensor, 16:9 image. All required roof/pool corner points fit.
    frame=[]
    for q in required:
        v=q-eye;depth=v.dot(fwd)
        if depth<=0:return None
        frame.append((.5+v.dot(right)*lens/(36*depth),.5+v.dot(up)*lens/(20.25*depth)))
    xmin,xmax=min(q[0] for q in frame),max(q[0] for q in frame);ymin,ymax=min(q[1] for q in frame),max(q[1] for q in frame)
    if xmin<.035 or xmax>.965 or ymin<.045 or ymax>.955:return None
    near=[geo.ray(eye,v,.3) for v in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))]
    if any(near):return None
    hits=[];counts=collections.Counter();by_group=collections.defaultdict(collections.Counter)
    for i,q in enumerate(all_targets):
        ray=q-eye;hit=geo.ray(eye,ray,ray.length+.3)
        group='roof' if i<len(roof_points) else ('pool' if i>=len(roof_points)+len(front) else 'facade')
        ob=hit['object'] if hit else 'NONE'
        cls='architecture' if ob.startswith(('GUEST','FW_FURN_GUEST')) else ('vegetation' if ob in veg_names else 'other')
        counts[cls]+=1;by_group[group][cls]+=1
        hits.append({'target':cr.plain(q),'group':group,'hit':hit,'class':cls})
    grid=collections.Counter()
    for ux in range(11):
        for vy in range(7):
            u=(ux/10-.5)*36/lens;v=(vy/6-.5)*20.25/lens
            hit=geo.ray(eye,fwd+right*u+up*v,14 if pool_near else 90)
            if hit and hit['object'] in veg_names and hit['distance']<14:grid['foreground_vegetation']+=1
            elif hit and hit['object'].startswith(('GUEST','FW_FURN_GUEST')):grid['guest_architecture']+=1
            else:grid['other']+=1
    tilt=math.degrees(math.asin(abs(fwd.z)))
    visibility=counts['architecture']/len(all_targets)
    width=xmax-xmin
    score=visibility*12+grid['guest_architecture']*.025-grid['foreground_vegetation']*.10+width*1.2-abs(tilt-14)*.015
    return {'location':cr.plain(eye),'target':cr.plain(target),'lens':lens,'score':score,'structure_ray_visibility':visibility,
            'structure_rays':dict(counts),'groups':{k:dict(v) for k,v in by_group.items()},'frame_grid':dict(grid),
            'required_projection_bounds':[xmin,ymin,xmax,ymax],'tilt_degrees':tilt,'rays':hits}
settings=json.loads((ROOT/'qa/camera04-showcase-settings.json').read_text()) if pool_near else {}
report={'scene':bpy.data.filepath,'geometry':geo.counts,'vegetation_included':True,'vegetation_objects':len(veg_names),'conservative_ray_bounds':ray_bounds,
 'scope':'Geometric candidate selection only. Required visible-footprint points checked in 16:9 camera frame; rays include every rendered leaf and trunk. Structure rays count a nearer guest-house surface as architecture, so this is not endpoint photo matching. Image review required.', 'cameras':{}}
for name in (('CAM_GUEST_POOL',) if pool_near else ('CAM_GUEST_OVERVIEW','CAM_GUEST_POOL')):
    if name.endswith('OVERVIEW'):
        positions=[(x,y,z) for x in (28,34,40,46,52) for y in (-4,3,10,17,24) for z in (13,16,19,22)]
        target=(12.5,39.5,10);required=roof_points+pool
    elif not pool_near:
        positions=[(x,y,z) for x in (30,34,38,42,46) for y in (12,17,22,27) for z in (10.7,12.5,14.5,16.5)]
        target=(19,37,9.6);required=roof_groups['GUEST_LOW_ARM_ROOF']+pool
    else:
        positions=[(x,y,z) for x in (36.5,37,37.5,38,39,40,41) for y in (31,32,33,34,35,36,37) for z in (11,12,13,14)]
        target=(22,37,9.6);required=roof_points+pool
    candidates=[]
    for eye in positions:
        for lens in (35,38,42,45):
            result=assess(eye,target,lens,required)
            if result:candidates.append(result)
    if not candidates:raise RuntimeError('No framed clear candidate for '+name)
    if pool_near:
        for c in candidates:
            c['score']-=c['frame_grid'].get('foreground_vegetation',0)*.20
    candidates.sort(key=lambda r:-r['score']);chosen=candidates[0]
    settings[name]={k:chosen[k] for k in ('location','target','lens')}
    settings[name].update(exposure=.8,evidence='Iteration04 tree-aware geometry candidate; actual rendered image review pending.',render_reviewed=False)
    original=scene.objects[name]
    originaltarget=original.location+(original.rotation_euler.to_matrix()@Vector((0,0,-1)))*40
    report['cameras'][name]={'original':{'location':cr.plain(original.location),'target':cr.plain(originaltarget),'lens':original.data.lens},
                           'valid_candidates':len(candidates),'selected':chosen,'alternatives':candidates[1:4]}
    print('SHOWCASE_CANDIDATE '+json.dumps({'name':name,'settings':settings[name],'counts':chosen['structure_rays'],'grid':chosen['frame_grid']}),flush=True)
report['rays_cast']=geo.calls
cr.write_json(ROOT/('qa/camera04-showcase-near-settings.json' if pool_near else 'qa/camera04-showcase-settings.json'),settings)
cr.write_json(ROOT/('qa/camera04-showcase-near-geometry.json' if pool_near else 'qa/camera04-showcase-geometry.json'),report)
