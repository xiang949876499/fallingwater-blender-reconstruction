"""Independent no-water candidate and actual bounded geometry/contact regression."""
import bpy,sys,json,hashlib,struct,math,time
from pathlib import Path
from types import SimpleNamespace
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import near_terrain_detail as near
source=ROOT/'scene/Fallingwater_geology_candidate07c.blend'
expected='24a2ca01d276cde137ff3e041ecbf5bdc028289f5b83e8be20167cb4a0c561f3'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(48)
terrain=scene.objects['SITE_Continuous_BearRun_Terrain']
assert all(abs(terrain.matrix_world[i][j]-(1 if i==j else 0))<1e-9 for i in range(4) for j in range(4))

def mesh_hash(m,topology=False):
    h=hashlib.sha256()
    if not topology:
        for v in m.vertices:h.update(struct.pack('<3f',*v.co))
    for p in m.polygons:
        h.update(struct.pack('<III',len(p.vertices),p.material_index,p.use_smooth))
        for i in p.vertices:h.update(struct.pack('<I',i))
    return h.hexdigest()

def snapshot():
    meshes={m.name:mesh_hash(m) for m in bpy.data.meshes if m.users}
    return {o.name:{'type':o.type,'matrix':[list(r) for r in o.matrix_world],'hide_render':o.hide_render,
                    'collections':sorted(c.name for c in o.users_collection),
                    'mesh':meshes[o.data.name] if o.type=='MESH' else None,
                    'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else None} for o in scene.objects}

def compact_bvh(names):
    vv=[];ff=[];owners=[]
    for name in sorted(names):
        o=scene.objects.get(name)
        if o is None or o.type!='MESH' or o.hide_render:continue
        start=len(vv);vv.extend(o.matrix_world@v.co for v in o.data.vertices)
        for p in o.data.polygons:ff.append(tuple(start+i for i in p.vertices));owners.append(name)
    return BVHTree.FromPolygons(vv,ff,all_triangles=False,epsilon=.001),owners

options=json.loads(json.dumps(near.DEFAULTS));options['enabled']=True
ctx=SimpleNamespace(root=ROOT,config=json.loads((ROOT/'config.json').read_text(encoding='utf8')))
before=snapshot();topology=mesh_hash(terrain.data,True);original_vertices=[tuple(v.co) for v in terrain.data.vertices]
oldterrain=BVHTree.FromObject(terrain,bpy.context.evaluated_depsgraph_get())
target_names={terrain.name,'TREE_Forest_Floor_Moss_Patches','TREE_Fallen_Leaves_Ground_Litter'}
for o in scene.objects:
    if o.type=='MESH' and o.name.startswith('TREE_') and any(near.box_outside(o.location.x,o.location.y,bb)<1.5 for bb in options['zones'].values()):target_names.add(o.name)
before_bvh,before_owners=compact_bvh(target_names)
started=time.monotonic()
result=near.build(ctx,{'enabled':True})
after=snapshot();changed=[name for name,v in before.items() if after.get(name)!=v]
allowed={terrain.name}|{r['object'] for r in result['vegetation']['tree_pairs']}|{r['paired_leaves'] for r in result['vegetation']['tree_pairs'] if r['paired_leaves']}|{r['object'] for r in result['vegetation']['aggregate_groundcover']}
unexpected=[name for name in changed if name not in allowed]
assert not unexpected,unexpected
assert topology==mesh_hash(terrain.data,True)
assert all(a[:2]==tuple(b.co)[:2] for a,b in zip(original_vertices,terrain.data.vertices))
surf=near.Terrain(ctx,options)
changed_indices={r['index'] for r in result['deformation']['vertices']}
freeze_bad=[];outside_bad=[]
for i in changed_indices:
    p=terrain.data.vertices[i].co
    if surf.clearance(p.x,p.y,geometry=True)<.959:freeze_bad.append(i)
    if not any(near.box_outside(p.x,p.y,bb)<-.959 for bb in options['zones'].values()):outside_bad.append(i)
assert not freeze_bad and not outside_bad
core=[]
for r in json.loads((ROOT/'qa/core-geology07c-fresh-module-reproduction.json').read_text())['objects']:
    o=scene.objects[r['object']];h=hashlib.sha256()
    for v in o.data.vertices:h.update(struct.pack('<3f',*(o.matrix_world@v.co)))
    for p in o.data.polygons:
        h.update(struct.pack('<I',len(p.vertices)))
        for i in p.vertices:h.update(struct.pack('<I',i))
    core.append({'object':o.name,'hash':h.hexdigest(),'equal':h.hexdigest()==r['world_geometry_sha256']})
assert all(r['equal'] for r in core)

def actual_gap(p,bvh):
    hit,n,i,d=bvh.ray_cast(Vector((p.x,p.y,60)),Vector((0,0,-1)),130)
    return p.z-hit.z

newleaves=scene.objects[result['leaves']['object']]
new_points=[newleaves.matrix_world@v.co for v in newleaves.data.vertices]
all_exclusion=[];gaps=[];leaf_area=0.0
for i,p in enumerate(new_points):
    if surf.clearance(p.x,p.y)<-.0001:all_exclusion.append(i)
    gaps.append(actual_gap(p,surf.bvh))
for face in newleaves.data.polygons:
    a,b,c=[new_points[i] for i in face.vertices]
    gaps.append(actual_gap((a+b+c)/3,surf.bvh));leaf_area+=(b-a).cross(c-a).length*.5
assert not all_exclusion,all_exclusion[:10]
assert min(gaps)>-.0011 and max(gaps)<.0171,(min(gaps),max(gaps))
contact={'new_leaf_vertices_checked':len(new_points),'vertex_and_face_center_samples':len(gaps),
         'actual_gap_min_m':min(gaps),'actual_gap_max_m':max(gaps),'actual_gap_mean_m':sum(gaps)/len(gaps),
         'exclusion_failures':all_exclusion,'leaf_surface_area_m2':leaf_area,
         'leaf_area_to_eligible_ground_area_ratio':leaf_area/max(result['leaves']['eligible_area_m2'],1)}

# A real spatial delta regression: every existing06 route is swept against all
# potentially changed objects before/after. Unchanged architecture is already
# hash-proven, so this avoids re-running/writing the root's full adjacency job.
after_bvh,after_owners=compact_bvh(target_names|{newleaves.name})
def ray(bvh,owners,p,d,length):
    hit,n,i,t=bvh.ray_cast(Vector(p),Vector(d),length)
    return None if hit is None else {'object':owners[i],'distance':t,'position':list(hit)}
new_obstructions=[];rays=0;ground_deltas=[];route_reports=[]
def compare_ray(p,d,length,where):
    global rays
    rays+=1;a=ray(before_bvh,before_owners,p,d,length);b=ray(after_bvh,after_owners,p,d,length)
    if b is not None and (a is None or b['distance']<a['distance']-.008):
        if len(new_obstructions)<100:new_obstructions.append({'where':where,'before':a,'after':b})
route=json.loads((ROOT/'qa/tour-path-route-iteration06-final.json').read_text(encoding='utf8'))
for seg in route['main_segments']+route['supplemental_segments']:
    walk=bool(seg.get('body_clearance_tested',seg['mode'].startswith('NORMAL')))
    count=0;before_fail=len(new_obstructions)
    for aa,bb in zip(seg['points'],seg['points'][1:]):
        a,b=Vector(aa),Vector(bb);diff=b-a;steps=max(1,math.ceil(diff.length/.25))
        for j in range(steps+1):
            p=a+diff*j/steps;count+=1
            for d in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):compare_ray(p,d,.13,seg['id'])
            if walk:
                bottom=.24 if 'STAIRS' in seg['mode'] else .09
                for dx,dy in ((0,0),(-.18,0),(.18,0),(0,-.18),(0,.18)):
                    compare_ray((p.x+dx,p.y+dy,p.z-1.6+bottom),(0,0,1),1.71-bottom,seg['id'])
        if diff.length>.001:
            d=diff.normalized();cross=Vector((-d.y,d.x,0))
            if cross.length>.001:cross.normalize()
            offsets=[cross*s+Vector((0,0,h-1.6)) for s in (-.18,0,.18) for h in (.3,.72,1.13,1.6)] if walk else [Vector(),cross*.12,-cross*.12]
            for off in offsets:compare_ray(a+off,d,diff.length,seg['id'])
    route_reports.append({'id':seg['id'],'mode':seg['mode'],'samples':count,'new_obstruction_records':len(new_obstructions)-before_fail})
for route_cfg in surf.cfg['paths']:
    for aa,bb in zip(route_cfg['points'],route_cfg['points'][1:]):
        a,b=Vector(aa),Vector(bb);delta=b-a;steps=max(1,math.ceil(delta.length/.25))
        normal=Vector((-delta.y,delta.x,0)).normalized()
        for j in range(steps+1):
            p=a+delta*j/steps
            for side in (0,-route_cfg['width']*.5,route_cfg['width']*.5):
                q=p+normal*side
                old,_,_,_=oldterrain.ray_cast(Vector((q.x,q.y,60)),Vector((0,0,-1)),130)
                new,_=surf.hit(q.x,q.y)
                if old is not None and new is not None:ground_deltas.append(abs(new.z-old.z))
assert max(ground_deltas,default=0)<1e-5,max(ground_deltas,default=0)
assert not new_obstructions,new_obstructions[:5]
camera_checks=[]
for name,cx,cy in surf.cameras:
    deltas=[]
    for radius in (0,.5,1,1.5,2):
        for j in range(16):
            x=cx+radius*math.cos(j*math.tau/16);y=cy+radius*math.sin(j*math.tau/16)
            old,_,_,_=oldterrain.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),130);new,_=surf.hit(x,y)
            if old is not None and new is not None:deltas.append(abs(new.z-old.z))
    camera_checks.append({'camera':name,'radius_m':2,'samples':len(deltas),'max_delta_m':max(deltas,default=0)})
assert max(r['max_delta_m'] for r in camera_checks)<1e-5
destination=ROOT/'scene/Fallingwater_near_terrain_candidate07b.blend'
scene['near_terrain_candidate']='07b C profile + original mesh material continuous litter; visual pending; not full07 integration'
bpy.ops.wm.save_as_mainfile(filepath=str(destination),compress=True)
report={'status':'PASS_BOUNDED_GEOMETRY_CONTACT_DELTA_REGRESSION_VISUAL_NOT_RUN','candidate':str(destination),'candidate_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
        'source_sha256':expected,'frame':48,'full07_integration':False,'module_enabled_by_default':False,
        'result':result,'original_compared_objects':len(before),'original_changed_objects':changed,'unexpected_changes':unexpected,
        'terrain_topology_preserved':True,'terrain_xy_preserved':True,'outside_zone_vertices_changed':outside_bad,'frozen_zone_vertices_changed':freeze_bad,
        'core_hashes':core,'new_leaf_contact':contact,'camera_ground_neighborhood_checks':camera_checks,
        'route_delta_regression':{'rays':rays,'segments':route_reports,'new_obstructions':new_obstructions,'path_ground_samples':len(ground_deltas),'max_path_ground_delta_m':max(ground_deltas,default=0),
                                  'scope':'All existing06 route body/head/camera point and segment rays against actual potentially changed objects; exact unchanged-object snapshot guards remaining scene. Not a new all-adjacency/animation acceptance on full07.'},
        'helper_sha256':hashlib.sha256((ROOT/'scripts/near_terrain_detail.py').read_bytes()).hexdigest(),'elapsed_s':time.monotonic()-started}
(ROOT/'qa/near-terrain07b-candidate-check.json').write_text(json.dumps(report,indent=2),encoding='utf8')
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
print('NEAR07B_RESULT',json.dumps({k:v for k,v in report.items() if k in ('status','candidate','candidate_sha256','elapsed_s','original_changed_objects')}),flush=True)
