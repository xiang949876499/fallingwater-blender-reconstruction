"""Independent interface10 candidate and scoped reopen regression, CPU4 only."""
import bpy,json,sys,hashlib,array,math,collections
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import main_house as mh
import main_interface10 as fix
SRC=R/'scene/Fallingwater_iteration09.blend';OUT=R/'scene/Fallingwater_main_interface_candidate10b.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC)=='489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331'
assert not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene
def settings():
 return dict(resolution=[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],
             threads_mode=s.render.threads_mode,threads=s.render.threads,camera=s.camera.name if s.camera else None,
             engine=s.render.engine,frame=s.frame_current,frame_start=s.frame_start,frame_end=s.frame_end,
             world=s.world.name if s.world else None,filepath=s.render.filepath,cycles_device=s.cycles.device,
             samples=s.cycles.samples,exposure=s.view_settings.exposure)
initial_settings=settings();s.render.threads_mode='FIXED';s.render.threads=4
def fingerprint():
 out={};cache={}
 for o in s.objects:
  h=hashlib.sha256(str(tuple(tuple(row) for row in o.matrix_world)).encode())
  if o.type=='MESH':
   ptr=o.data.as_pointer()
   if ptr not in cache:
    a=array.array('f',[0.])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a)
    b=array.array('i',[0])*len(o.data.loops);o.data.loops.foreach_get('vertex_index',b)
    cache[ptr]=hashlib.sha256(a.tobytes()+b.tobytes()).digest()
   h.update(cache[ptr])
  if o.type=='CAMERA':h.update(str((o.data.lens,o.data.sensor_width,o.data.sensor_height,o.data.shift_x,o.data.shift_y,o.data.clip_start,o.data.clip_end,o.data.type)).encode())
  if o.type=='LIGHT':h.update(str((o.data.type,o.data.energy,tuple(o.data.color))).encode())
  h.update(str(tuple(m.name if m else None for m in getattr(o.data,'materials',[]))).encode())
  h.update(str((o.hide_render,o.hide_viewport)).encode());out[o.name]=h.hexdigest()
 return out
def verts(o):return [list(o.matrix_world@v.co) for v in o.data.vertices]
def tree(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh()
 t=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(f.vertices) for f in m.polygons]);e.to_mesh_clear();return t
def main_trees():return {o.name:tree(o) for o in s.objects if o.type=='MESH' and o.name.startswith('MAIN_') and len(o.data.vertices)<1000}
def cast(p,d=(0,0,-1),dist=100):
 h,q,n,f,o,_=s.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector(p),Vector(d),distance=dist)
 return dict(object=o.name if h else None,point=list(q) if h else None,normal=list(n) if h else None)
def layers(trees,p,z):
 out=[]
 for name,t in trees.items():
  if not name.endswith('_finish'):continue
  q,n,f,d=t.ray_cast(Vector((p[0],p[1],z+.05)),Vector((0,0,-1)),.10)
  if q is not None and abs(q.z-z)<.0001:out.append(name)
 return out
def inside(p,poly):
 yes=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:yes=not yes
 return yes
def area(p):return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1])))/2
old_fingerprints=fingerprint();old_trees=main_trees()
protected=['scripts/main_house.py','scripts/furnishings.py','scripts/camera_review.py','scripts/tour.py','data/main_house.json','data/camera-settings-reviewed.json','data/tour-route.json','config.json']
protected_before={n:sha(R/n) for n in protected}
route_path=R/'qa/tour-path-route-iteration09-attempt01.json';route_bytes=route_path.read_bytes();route=json.loads(route_bytes)
(R/'qa/main-interface10-route-snapshot.json').write_bytes(route_bytes)
probe=json.loads((R/'qa/main-interface10-probe.json').read_text(encoding='utf-8'))
pixels=[]
for r in probe['results']:pixels.append(dict(camera=r['camera'],pixel=r['pixel'],origin=r['ray_origin'],direction=r['ray_direction'],before=cast(r['ray_origin'],r['ray_direction'])))
manifest=fix.apply();changed=manifest['changed'];removed=manifest['removed']
after_fingerprints=fingerprint()
assert sorted(set(old_fingerprints)-set(after_fingerprints))==sorted(removed)
assert set(after_fingerprints)-set(old_fingerprints)==set()
assert sorted(n for n in after_fingerprints if old_fingerprints[n]!=after_fingerprints[n])==sorted(changed)
assert all(old_fingerprints[n]==after_fingerprints[n] for n in after_fingerprints if n not in changed)
expected={n:verts(s.objects[n]) for n in changed}
s.render.threads_mode=initial_settings['threads_mode'];s.render.threads=initial_settings['threads'];assert settings()==initial_settings
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));bpy.ops.wm.open_mainfile(filepath=str(OUT));s=bpy.context.scene
assert settings()==initial_settings
assert fingerprint()==after_fingerprints
s.render.threads_mode='FIXED';s.render.threads=4
now_trees=main_trees()
for p in pixels:
 p['after']=cast(p['origin'],p['direction']);p['unchanged']=p['before']['object']==p['after']['object'] and (not p['after']['point'] or math.dist(p['before']['point'],p['after']['point'])<1e-5)
# Check each rebuilt mesh is a closed two-manifold prism with outward volume.
mesh_checks=[]
for n in changed:
 o=s.objects[n];counts=collections.Counter(tuple(sorted(e)) for f in o.data.polygons for e in f.edge_keys)
 o.data.calc_loop_triangles();volume=sum((o.data.vertices[t.vertices[0]].co.cross(o.data.vertices[t.vertices[1]].co)).dot(o.data.vertices[t.vertices[2]].co)/6 for t in o.data.loop_triangles)
 mesh_checks.append(dict(object=n,vertices=len(o.data.vertices),polygons=len(o.data.polygons),edge_multiplicity=dict(collections.Counter(counts.values())),signed_volume=volume,pass_=all(v==2 for v in counts.values()) and volume>0))
# Entire old/new floor extents, sampled inside actual polygons, keep one finish.
grid=[];polygons={}
for g in manifest['geometry']:
 n=g['name'];wp=[mh.xy(p) for p in g['source_polygon']];old=g['before_world_vertices'];op=[tuple(v[:2]) for v in old[:len(old)//2]]
 polygons[n]=dict(source=g['source_polygon'],world=wp,old_world=op,old_area=area(op),new_area=area(wp),z=g['z'])
 if not n.endswith('_finish'):continue
 xx=wp+op;x0,x1=min(p[0] for p in xx),max(p[0] for p in xx);y0,y1=min(p[1] for p in xx),max(p[1] for p in xx);z=g['z'][1]
 for ix in range(75):
  for iy in range(75):
   p=(x0+(x1-x0)*(ix+.371)/75,y0+(y1-y0)*(iy+.413)/75)
   if inside(p,wp) or inside(p,op):
    ll=layers(now_trees,p,z);grid.append(dict(owner=n,xy=p,layers=ll,pass_=len(ll)==1))
# Distinguish source stone from paving, and preserve already positive surfaces.
controls=[]
for label,px,z in [('Loggia_entry_paving',(523.24,305.97),.122),('Master_core_floor',(333.04,310.75),2.8668),('Master_north_floor',(350,306),2.8668),('Loggia_under_stair_unresolved',(486.4212583,296.6087008),.122),('L3_stair_opening',(420,280),5.28615),('L3_stair_west',(400,280),5.28615)]:
 p=mh.xy(px);origin=Vector((*p,z+.06));before_hits=[]
 for n,t in old_trees.items():
  q,no,face,d=t.ray_cast(origin,Vector((0,0,-1)),10)
  if q is not None:before_hits.append((d,n,list(q)))
 before_hits.sort();now=cast(origin)
 controls.append(dict(label=label,source_px=px,before=before_hits[0] if before_hits else None,after=now,expected_finish_z=z))
body=[]
def body_check(q,label):
 for dz in (0,-.65,-1.3):
  p=Vector(q)+Vector((0,0,dz));new=[];old=[]
  for n in changed:
   hn=now_trees[n].find_nearest(p,.18);ho=old_trees[n].find_nearest(p,.18)
   if hn[0] is not None:new.append((n,hn[3]))
   if ho[0] is not None:old.append((n,ho[3]))
  body.append(dict(label=label,point=list(p),new_near=new,old_near=old,new_collision=bool(new) and not bool(old)))
for o in s.objects:
 if o.type=='CAMERA':body_check(o.matrix_world.translation,o.name)
for seg in route['main_segments']+route['supplemental_segments']:
 for i,(a,b) in enumerate(zip(seg['points'],seg['points'][1:])):
  a,b=Vector(a),Vector(b);n=max(2,math.ceil((b-a).length/.10))
  for k in range(n+1):body_check(a.lerp(b,k/n),f"{seg['id']}:{i}:{k}")
# Actual nearby stair tread center/side support and headroom after reopen.
stairs=[]
for o in s.objects:
 if o.type!='MESH' or not o.name.startswith(('MAIN_stair1_','MAIN_stair2_')) or not o.name.rsplit('_',1)[-1].isdigit():continue
 vv=[o.matrix_world@Vector(v) for v in o.bound_box];x=(min(v.x for v in vv)+max(v.x for v in vv))/2;y=(min(v.y for v in vv)+max(v.y for v in vv))/2;z=max(v.z for v in vv)
 for dx in (-.18,0,.18):
  ground=cast((x,y+dx,z+.035),dist=.12);ceiling=cast((x,y+dx,z+.1),(0,0,1),5)
  head=ceiling['point'][2]-z if ceiling['point'] else None
  stairs.append(dict(object=o.name,xyz=[x,y+dx,z],ground=ground,ceiling=ceiling,headroom_m=head,pass_=ground['point'] is not None and abs(ground['point'][2]-z)<.02 and (head is None or head>=1.95)))
thresholds=[]
for tid,rid,rr,lev,mat,path in mh.THRESHOLDS:
 z=mh.LEVELS[lev]+.022;a,b=map(Vector,map(mh.xy,path))
 for i in range(31):
  p=a.lerp(b,i/30);was=layers(old_trees,p,z);now=layers(now_trees,p,z)
  thresholds.append(dict(threshold=tid,xyz=[p.x,p.y,z],before=was,after=now,pass_=not was or bool(now)))
counts=dict(changed=len(changed),removed=len(removed),added=0,unique_floor_grid=len(grid),unique_floor_fails=sum(not p['pass_'] for p in grid),body_points=len(body),new_body_hits=sum(p['new_collision'] for p in body),nearby_stair_samples=len(stairs),stair_fails=sum(not p['pass_'] for p in stairs),threshold_samples=len(thresholds),threshold_regression_fails=sum(not p['pass_'] for p in thresholds),mesh_manifold_fails=sum(not x['pass_'] for x in mesh_checks))
report=dict(status='SAVED_SCOPED_REGRESSION_RECORDED',source=str(SRC),source_sha256=sha(SRC),candidate=str(OUT),candidate_sha256=sha(OUT),helper_sha256=sha(R/'scripts/main_interface10.py'),source_script_sha256=sha(R/'scripts/main_house.py'),manifest=manifest,all_nontarget_fingerprints_identical=True,settings_identical=True,saved_settings=initial_settings,counts=counts,polygons=polygons,pixels=pixels,controls=controls,mesh_checks=mesh_checks,surface_grid=grid,body=body,stairs=stairs,thresholds=thresholds,route_sha256=hashlib.sha256(route_bytes).hexdigest(),production_unchanged={n:sha(R/n)==h for n,h in protected_before.items()},source_scene_unchanged=sha(SRC)=='489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331',limits=['No render or full60-edge/7584-frame revalidation.','Master door source registration and under-stair missing transverse-bar identity remain unresolved and unedited.','Merged L masonry replaces its separate east leg and removes that target leg7mm edge dressing; all other modifiers remain unchanged.'])
(R/'qa/main-interface10-candidate-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'counts':counts,'candidate_sha256':report['candidate_sha256'],'changed_pixels':[p for p in pixels if not p['unchanged']]},indent=2))
assert all(counts[k]==0 for k in ('unique_floor_fails','new_body_hits','stair_fails','threshold_regression_fails','mesh_manifold_fails'))
assert all(report['production_unchanged'].values()) and report['source_scene_unchanged']
for p in pixels:
 if p['camera'].endswith('MASTER_A') and p['pixel'] in [[503,183],[531,207],[460,152],[537,164]]:assert p['unchanged']
 if p['camera'].endswith('LOGGIA_A') and p['pixel'] in [[484,250],[500,255],[477,247],[494,275],[499,293]]:assert p['unchanged']
report['status']='PASS_SCOPED_INTERFACE10_GEOMETRY_VISUAL_NOT_RUN'
(R/'qa/main-interface10-candidate-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(report['status'])
