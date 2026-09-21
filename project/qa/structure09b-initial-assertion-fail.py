"""Two source-bounded repairs on frozen structure09. CPU geometry only."""
import bpy, json, sys, hashlib, array, math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import main_house as mh
from fwlib import poly_prism,collection
SRC=R/'scene/Fallingwater_structure_candidate09.blend'
OUT=R/'scene/Fallingwater_structure_candidate09b.blend'
SOURCE_SHA='4fa1fc1f56795a2da88c97bacc9bd3b2a0730d3d085076173425b00addd744a0'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC)==SOURCE_SHA
assert not OUT.exists(),'Preserve any existing candidate; use another explicit revision.'
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
route_path=R/'data/tour-route.json';route_bytes=route_path.read_bytes();route=json.loads(route_bytes)
(R/'qa/structure09b-route-snapshot.json').write_bytes(route_bytes)
source_records=json.loads((R/'qa/structure08b-remaining-review.json').read_text())['results']+json.loads((R/'qa/structure09-extra-probe.json').read_text())['results']
pixels=[]
for r in source_records:pixels.append(dict(camera=r['camera'],pixel=r['pixel'],origin=r['camera_origin'],direction=r['ray_direction'],before=cast(r['camera_origin'],r['ray_direction'])))
probe_points=[('Alcove_gap',(433,265),5.28615),('Alcove_west_stair',(431,280),5.28615),('Stair_mid',(400,280),5.28615),('Stair_east',(420,280),5.28615),('Loggia_corner',(534.767522972,300.727693806),.122),('Loggia_paving',(534,304),.122),('Loggia_north_wall_foot',(549,306.3),.122)]
controls=[]
for label,p,z in probe_points:
 xy=mh.xy(p);controls.append(dict(label=label,source_px=p,z=z,before=cast((*xy,z+.06)),ceiling_before=cast((*xy,z+.12),(0,0,1),5)))
specs=[]
for rid in ('MAIN_L1_LOGGIA','MAIN_L3_ALCOVE'):
 z=.1 if '_L1_' in rid else 5.26415;p=mh.closed_floor_source_polygon(rid)
 specs.extend([(rid+'_slab',p,z-.22,z),(rid+'_finish',p,z,z+.022)])
specs.append(('MAIN_L1_coat_1',mh.coat_east_source_polygon(),.1,2.5))
before_vertices={};expected={};polygons={}
for name,p,z0,z1 in specs:
 o=s.objects[name];old=verts(o);before_vertices[name]=old;wp=[mh.xy(v) for v in p]
 if name.endswith(('_slab','_finish')):op=[tuple(v[:2]) for v in old[:len(old)//2]]
 else:
  x0,x1=min(v[0] for v in old),max(v[0] for v in old);y0,y1=min(v[1] for v in old),max(v[1] for v in old);op=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
 polygons[name]=dict(source=p,world=wp,old_world=op,z_range=[z0,z1],old_area=area(op),new_area=area(wp))
 tmp=poly_prism('QA09b_transient',wp,z0,z1,o.data.materials[0],collection('QA09b_transient'))
 bpy.context.view_layer.update();expected[name]=verts(tmp);o.data=tmp.data.copy();o.matrix_world=tmp.matrix_world.copy()
 o['physical_revision']='09b source-bounded Coat/Loggia junction or Alcove west inner face'
 o['evidence']='C';bpy.data.objects.remove(tmp,do_unlink=True)
bpy.data.collections.remove(bpy.data.collections['QA09b_transient']);bpy.context.view_layer.update()
after_fingerprints=fingerprint();changed=sorted(n for n in old_fingerprints if old_fingerprints[n]!=after_fingerprints[n])
assert changed==sorted(n for n,*_ in specs)
assert old_fingerprints.keys()==after_fingerprints.keys()
assert all(old_fingerprints[n]==after_fingerprints[n] for n in old_fingerprints if n not in changed)
s.render.threads_mode=initial_settings['threads_mode'];s.render.threads=initial_settings['threads'];assert settings()==initial_settings
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));bpy.ops.wm.open_mainfile(filepath=str(OUT));s=bpy.context.scene
assert settings()==initial_settings;s.render.threads_mode='FIXED';s.render.threads=4
assert fingerprint()==after_fingerprints
rebuild_error=max(abs(a[k]-b[k]) for name,vs in expected.items() for a,b in zip(vs,verts(s.objects[name])) for k in range(3))
assert rebuild_error<1e-6
now_trees=main_trees()
for r in pixels:
 r['after']=cast(r['origin'],r['direction']);r['previous_hit_preserved']=r['after']['object']==r['before']['object'] and (not r['after']['point'] or math.dist(r['after']['point'],r['before']['point'])<1e-5)
 if r['camera']=='CAM_MAIN_L1_LOGGIA_A' and r['pixel']==[638,373]:r['fixed_target']=r['after']['object']=='MAIN_L1_coat_1'
for r in controls:
 p=mh.xy(r['source_px']);r['after']=cast((*p,r['z']+.06));r['ceiling_after']=cast((*p,r['z']+.12),(0,0,1),5)
 r['surface_layers_after']=layers(now_trees,p,r['z'])
 r['ceiling_unchanged']=r['ceiling_before']['object']==r['ceiling_after']['object'] and math.dist(r['ceiling_before']['point'],r['ceiling_after']['point'])<1e-5 if r['ceiling_before']['point'] and r['ceiling_after']['point'] else r['ceiling_before']['point']==r['ceiling_after']['point']
 r['source_opening_preserved']=r['after']['object']==r['before']['object'] and math.dist(r['after']['point'],r['before']['point'])<1e-5 if 'stair' in r['label'].lower() else None
# Dense unique finish counts over the union of each old and new polygon.
grid=[]
for name in ('MAIN_L1_LOGGIA_finish','MAIN_L3_ALCOVE_finish'):
 pp=polygons[name];allp=pp['world']+pp['old_world'];z=pp['z_range'][1]
 x0,x1=min(p[0] for p in allp),max(p[0] for p in allp);y0,y1=min(p[1] for p in allp),max(p[1] for p in allp)
 for ix in range(47):
  for iy in range(47):
   p=(x0+(x1-x0)*(ix+.37)/47,y0+(y1-y0)*(iy+.43)/47)
   if inside(p,pp['world']) or inside(p,pp['old_world']):
    ll=layers(now_trees,p,z);grid.append(dict(owner=name,xy=p,layers=ll,pass_=len(ll)==1))
# More precise grid inside each local added strip (not just whole-room density).
for rid,xx,yy,z in [('LOGGIA',[529+i*.2 for i in range(181)],[301.56+i*.15 for i in range(44)],.122),('ALCOVE',[432+i*.10 for i in range(31)],[259+i*.2 for i in range(161)],5.28615)]:
 pp=polygons['MAIN_L1_LOGGIA_finish' if rid=='LOGGIA' else 'MAIN_L3_ALCOVE_finish']
 for x in xx:
  for y in yy:
   p=mh.xy((x,y))
   if inside(p,pp['world']):
    ll=layers(now_trees,p,z);grid.append(dict(owner=rid,source_px=[x,y],layers=ll,pass_=len(ll)==1))
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
projections=[]
for camname,points in [('CAM_MAIN_L1_LOGGIA_A',[('stone corner',(534.767522972,300.727693806),.122),('paving',(534,304),.122)]),('CAM_MAIN_L3_ALCOVE_B',[('west floor',(433,265),5.28615),('stair void',(431,280),5.28615)])]:
 cam=s.objects[camname]
 for label,p,z in points:
  q=Vector(mh.xyz(p,z));uv=world_to_camera_view(s,cam,q);d=(q-cam.matrix_world.translation).normalized();hit=cast(cam.matrix_world.translation,d)
  projections.append(dict(camera=camname,label=label,source_px=p,world=list(q),pixel_960x540=[uv.x*960,(1-uv.y)*540],first_hit=hit,target_occluded=bool(hit['point']) and math.dist(hit['point'],q)>.04))
counts=dict(changed=len(changed),added=0,removed=0,unique_floor_grid=len(grid),unique_floor_fails=sum(not p['pass_'] for p in grid),body_points=len(body),new_body_hits=sum(p['new_collision'] for p in body),nearby_stair_samples=len(stairs),stair_fails=sum(not p['pass_'] for p in stairs),threshold_samples=len(thresholds),threshold_regression_fails=sum(not p['pass_'] for p in thresholds))
report=dict(status='CANDIDATE_REOPENED_VALIDATION_RECORDED',source=str(SRC),source_sha256=sha(SRC),candidate=str(OUT),candidate_sha256=sha(OUT),source_script_sha256=sha(R/'scripts/main_house.py'),changed=changed,all_nontarget_fingerprints_identical=True,settings_identical=True,saved_settings=initial_settings,rebuild_error_m=rebuild_error,counts=counts,polygons=polygons,old_vertices=before_vertices,pixels=pixels,controls=controls,surface_grid=grid,body=body,stairs=stairs,thresholds=thresholds,projections=projections,route_sha256=hashlib.sha256(route_bytes).hexdigest(),limitations=['No render or full navigation acceptance.','Main06 original TIFF returned403; JPEG inner-face trace retains about one source-pixel uncertainty.','Body comparison identifies newly introduced proximity at existing cameras and sampled paths, not7584 integer-frame full scene validation.','No guest/tour/furnishings source or frozen09 scene edited.'])
(R/'qa/structure09b-candidate-check.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'counts':counts,'pixels_changed':[p for p in pixels if not p['previous_hit_preserved']],'controls':controls,'candidate_sha256':report['candidate_sha256']},indent=2))
assert all(counts[k]==0 for k in ('unique_floor_fails','new_body_hits','stair_fails','threshold_regression_fails'))
assert next(p for p in pixels if p['camera']=='CAM_MAIN_L1_LOGGIA_A' and p['pixel']==[638,373])['fixed_target']
assert all(c['source_opening_preserved'] for c in controls if c['source_opening_preserved'] is not None)
assert next(c for c in controls if c['label']=='Alcove_gap')['surface_layers_after']==['MAIN_L3_ALCOVE_finish']
assert all(c['ceiling_unchanged'] for c in controls)
report['status']='PASS_SCOPED_STRUCTURE09B_GEOMETRY_VISUAL_NOT_RUN'
(R/'qa/structure09b-candidate-check.json').write_text(json.dumps(report,indent=2))
print(report['status'])
