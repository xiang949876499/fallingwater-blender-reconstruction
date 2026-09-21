"""Complete07 source, local actual-path terrain repair, independent mesh audit."""
import bpy,json,hashlib,struct,math,sys,time
from pathlib import Path
from types import SimpleNamespace
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
frozen=json.loads((ROOT/'qa/bank08-frozen-inputs.json').read_text(encoding='utf8'))
FROZEN=Path(frozen['frozen_context'])
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(FROZEN/'scripts'))
import near_terrain_detail as near
for r in frozen['dependencies']:assert hashlib.sha256((FROZEN/r['file']).read_bytes()).hexdigest()==r['sha256']
source=ROOT/'scene/Fallingwater_iteration07.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()==frozen['source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(48)
ctx=SimpleNamespace(root=FROZEN,config=frozen['source_embedded_config'])
route_raw=(ROOT/'qa/tour-path-route-iteration07-final.json').read_bytes();route=json.loads(route_raw)
assert route['source_scene_sha256']==frozen['source_sha256']
(ROOT/'qa/bank08-frozen-route07.json').write_bytes(route_raw)

def mesh_hash(m):
    h=hashlib.sha256()
    for v in m.vertices:h.update(struct.pack('<3f',*v.co))
    for p in m.polygons:
        h.update(struct.pack('<III',len(p.vertices),p.material_index,p.use_smooth))
        for i in p.vertices:h.update(struct.pack('<I',i))
    return h.hexdigest()
def snapshot():
    mh={m.name:mesh_hash(m) for m in bpy.data.meshes if m.users}
    return {o.name:{'matrix':[list(r) for r in o.matrix_world],'hide_render':o.hide_render,'type':o.type,
                    'mesh':mh[o.data.name] if o.type=='MESH' else None,
                    'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else None} for o in scene.objects}
def bvh_objects(names):
    vv=[];ff=[];owners=[]
    for name in sorted(names):
        o=scene.objects.get(name)
        if o is None or o.type!='MESH' or o.hide_render:continue
        start=len(vv);vv.extend(o.matrix_world@v.co for v in o.data.vertices)
        for p in o.data.polygons:ff.append(tuple(start+i for i in p.vertices));owners.append(name)
    return BVHTree.FromPolygons(vv,ff,all_triangles=False,epsilon=.001),owners
def ray(bvh,x,y):return bvh.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),130)[0]
def geometry_fingerprint_outside(mesh,bb):
    rows=[]
    for p in mesh.polygons:
        vv=[mesh.vertices[i].co for i in p.vertices]
        if any(near.box_outside(v.x,v.y,bb)<=.01 for v in vv):continue
        rows.append(tuple(sorted(tuple(round(float(a),6) for a in v) for v in vv)))
    return hashlib.sha256(repr(sorted(rows)).encode()).hexdigest(),len(rows)

before=snapshot();terrain=scene.objects['SITE_Continuous_BearRun_Terrain']
oldterrain=BVHTree.FromObject(terrain,bpy.context.evaluated_depsgraph_get())
outside_before=geometry_fingerprint_outside(terrain.data,near.BRIDGE08['bounds'])
target_names={terrain.name,'TREE_Forest_Floor_Moss_Patches','TREE_Fallen_Leaves_Ground_Litter'}
for o in scene.objects:
    if o.type=='MESH' and o.name.startswith('TREE_') and near.box_outside(o.location.x,o.location.y,near.BRIDGE08['bounds'])<1.5:target_names.add(o.name)
oldbvh,oldowners=bvh_objects(target_names)
start=time.monotonic();result=near.build_bridge_front08(ctx,{'enabled':True,'surface_tint':True})
after=snapshot();changed=[name for name,v in before.items() if after.get(name)!=v]
allow={terrain.name}|{r['object'] for r in result['vegetation']['tree_pairs']}|{r['paired_leaves'] for r in result['vegetation']['tree_pairs'] if r['paired_leaves']}|{r['object'] for r in result['vegetation']['aggregate_groundcover']}
assert not set(changed)-allow,set(changed)-allow
assert set(before)==set(after),'No new object/leaf/tree/rock is authorized'
outside_after=geometry_fingerprint_outside(terrain.data,near.BRIDGE08['bounds'])
assert outside_before==outside_after,(outside_before,outside_after)
surf=near.BridgeFront08(ctx,result['options'])
pathbvh=BVHTree.FromObject(surf.path,bpy.context.evaluated_depsgraph_get())
station_source=json.loads((ROOT/'qa/bank07c-diagnosis-path-edge.json').read_text(encoding='utf8'))
stations=[]
for r in station_source['points']:
    p=Vector(r['world']);edge=Vector(r['nearest_actual_path_boundary_point']);direction=p-edge;direction.z=0;direction.normalize()
    rows=[]
    for offset in (-.15,-.05,0,.05,.15,.40,.70,1.30,1.80):
        q=edge+direction*offset;old=ray(oldterrain,q.x,q.y);new=ray(surf.bvh,q.x,q.y);paved=ray(pathbvh,q.x,q.y)
        rows.append({'offset_from_actual_edge_m':offset,'xy':[q.x,q.y],'original_terrain_z':old.z,'candidate_terrain_z':new.z,'paving_z':paved.z if paved else surf.paving_z,
                     'inside_actual_paving_mesh':paved is not None,'soil_minus_paving_m':new.z-(paved.z if paved else surf.paving_z),'delta_m':new.z-old.z})
    stations.append({'label':r['label'],'nearest_edge':list(edge),'samples':rows})
inside=[s for r in stations for s in r['samples'] if s['offset_from_actual_edge_m']<0]
failed_inside=[s for s in inside if not s['inside_actual_paving_mesh'] or s['soil_minus_paving_m']>-.035]
# Save failed evidence before aborting rather than presenting an unchecked file.
(ROOT/'qa/bank08-cross-sections.json').write_text(json.dumps({'stations':stations,'failed_inside':failed_inside},indent=2),encoding='utf8')
assert not failed_inside,failed_inside
points=[];weights=terrain.data.attributes['bank08_litter_weight']
for r in station_source['points']:
    x,y,z=r['world'];new,normal,index,d=surf.bvh.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),130)
    ids=terrain.data.polygons[index].vertices;a,b,c=[terrain.data.vertices[i].co for i in ids]
    den=(b.y-c.y)*(a.x-c.x)+(c.x-b.x)*(a.y-c.y)
    u=((b.y-c.y)*(x-c.x)+(c.x-b.x)*(y-c.y))/den;v=((c.y-a.y)*(x-c.x)+(a.x-c.x)*(y-c.y))/den
    weight=sum(t*weights.data[i].value for t,i in zip((u,v,1-u-v),ids))
    points.append({'label':r['label'],'xy':[x,y],'old_z':ray(oldterrain,x,y).z,'new_z':new.z,'delta_m':new.z-ray(oldterrain,x,y).z,'material_weight':weight})
assert all(r['delta_m']<-.10 for r in points),points
assert all(r['material_weight']>.45 for r in points if r['label'] in ('A_crest','B_mid','D_left','E_right')),points

# Frozen original geometry objects include every core/water/path/bridge/building
# and camera. The target whitelist and unchanged-object hash check prove these.
camera_checks=[]
for name,cx,cy in surf.cameras:
    gaps=[]
    for radius in (0,.5,1,1.5,2):
        for j in range(16):
            x=cx+radius*math.cos(j*math.tau/16);y=cy+radius*math.sin(j*math.tau/16)
            a=ray(oldterrain,x,y);b=ray(surf.bvh,x,y)
            if a and b:gaps.append(abs(a.z-b.z))
    camera_checks.append({'camera':name,'samples':len(gaps),'max_terrain_change_m':max(gaps,default=0)})
assert max(r['max_terrain_change_m'] for r in camera_checks)<1e-5
newbvh,newowners=bvh_objects(target_names)
new_obstacles=[];ray_count=0
def compare(p,d,length,label):
    global ray_count
    ray_count+=1
    a,na,ia,ta=oldbvh.ray_cast(Vector(p),Vector(d),length);b,nb,ib,tb=newbvh.ray_cast(Vector(p),Vector(d),length)
    if b is not None and (a is None or tb<ta-.008):new_obstacles.append({'segment':label,'before':oldowners[ia] if a is not None else None,'after':newowners[ib],'point':list(b)})
route_records=[]
for seg in route['main_segments']+route['supplemental_segments']:
    n0=len(new_obstacles);walk=bool(seg.get('body_clearance_tested',seg['mode'].startswith('NORMAL')))
    for aa,bb in zip(seg['points'],seg['points'][1:]):
        a,b=Vector(aa),Vector(bb);delta=b-a;count=max(1,math.ceil(delta.length/.25))
        for j in range(count+1):
            p=a+delta*j/count
            for d in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):compare(p,d,.13,seg['id'])
            if walk:
                bottom=.24 if 'STAIRS' in seg['mode'] else .09
                for dx,dy in ((0,0),(-.18,0),(.18,0),(0,-.18),(0,.18)):compare((p.x+dx,p.y+dy,p.z-1.6+bottom),(0,0,1),1.71-bottom,seg['id'])
        if delta.length>.001:
            d=delta.normalized();cross=Vector((-d.y,d.x,0))
            if cross.length>.001:cross.normalize()
            offsets=[cross*s+Vector((0,0,h-1.6)) for s in (-.18,0,.18) for h in (.3,.72,1.13,1.6)] if walk else [Vector(),cross*.12,-cross*.12]
            for off in offsets:compare(a+off,d,delta.length,seg['id'])
    route_records.append({'id':seg['id'],'new_obstacle_count':len(new_obstacles)-n0})
assert not new_obstacles,new_obstacles[:8]
contact=[]
for r in result['vegetation']['tree_pairs']:
    o=scene.objects[r['object']];p=o.matrix_world.translation
    contact.append({'object':o.name,'actual_root_gap_m':p.z-ray(surf.bvh,p.x,p.y).z,'z_delta_m':r['delta_m']})
groundcover=[]
for r in result['vegetation']['aggregate_groundcover']:
    o=scene.objects[r['object']];ids={v['vertex'] for v in r['vertices']};vg=[];fg=[]
    for i in ids:
        p=o.matrix_world@o.data.vertices[i].co;vg.append(p.z-ray(surf.bvh,p.x,p.y).z)
    for f in o.data.polygons:
        if not any(i in ids for i in f.vertices):continue
        p=sum((o.matrix_world@o.data.vertices[i].co for i in f.vertices),Vector())/len(f.vertices);fg.append(p.z-ray(surf.bvh,p.x,p.y).z)
    groundcover.append({'object':o.name,'vertices':len(vg),'vertex_gap_minmax_m':[min(vg),max(vg)],'face_center_gap_minmax_m':[min(fg),max(fg)]})
    if 'Fallen_Leaves' in o.name:assert min(fg)>-.0011 and max(fg)<.0171,groundcover[-1]
candidate=ROOT/'scene/Fallingwater_bank_candidate08.blend'
scene['bank08_status']='INDEPENDENT_C_LOCAL_PATH_TERRAIN_CANDIDATE_VISUAL_PENDING'
bpy.ops.wm.save_as_mainfile(filepath=str(candidate),compress=True)
report={'status':'PASS_LOCAL_PHYSICAL_EDGE_AND_DELTA_REGRESSION_VISUAL_NOT_RUN','source_sha256':frozen['source_sha256'],
        'candidate':str(candidate),'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'frame':48,
        'helper_sha256':hashlib.sha256((ROOT/'scripts/near_terrain_detail.py').read_bytes()).hexdigest(),'frozen_dependencies':frozen['dependencies'],
        'result':result,'compared_objects':len(before),'changed_objects':changed,'outside_patch_terrain_triangle_hash_equal':outside_before==outside_after,
        'unchanged_outside_patch_triangles':outside_before[1],'five_diagnostic_world_points':points,'cross_sections':stations,
        'camera_ground_checks':camera_checks,'tree_contact':contact,'old_groundcover_contact':groundcover,
        'route_delta_regression':{'frozen_route_sha256':hashlib.sha256(route_raw).hexdigest(),'segments':route_records,'rays':ray_count,'new_obstacles':new_obstacles,
                                 'scope':'Complete07 frozen route against all possibly changed mesh objects, before/after; unchanged scene objects verified. Not a new full adjacency/animation validation.'},
        'no_new_objects_or_leaves':True,'production_integration':False,'rendered':False,'elapsed_s':time.monotonic()-start}
(ROOT/'qa/bank08-candidate-check.json').write_text(json.dumps(report,indent=2),encoding='utf8')
assert hashlib.sha256(source.read_bytes()).hexdigest()==frozen['source_sha256']
print('BANK08_RESULT',json.dumps({k:v for k,v in report.items() if k in ('status','candidate','candidate_sha256','changed_objects','elapsed_s')}),flush=True)
