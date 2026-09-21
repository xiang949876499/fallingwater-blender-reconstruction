"""Bounded saved08-derived geometry correction and CPU-only regressions."""
import bpy, json, sys, hashlib, array, math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import main_house as mh
from fwlib import poly_prism, collection, tag
SRC=R/'scene/Fallingwater_iteration08.blend'
OUT=R/'scene/Fallingwater_structure_candidate09.blend'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
assert sha(SRC)=='c5cd501e4c8ae0205ecb2437cd2d06d0c92bcc9a87e7d93d3986aeef976070d7'
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene
def settings():
 return {'resolution':list((s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage)),
 'threads_mode':s.render.threads_mode,'threads':s.render.threads,'camera':s.camera.name if s.camera else None,
 'engine':s.render.engine,'frame':s.frame_current,'frame_start':s.frame_start,'frame_end':s.frame_end,
 'world':s.world.name if s.world else None,'filepath':s.render.filepath,'cycles_device':s.cycles.device,
 'samples':s.cycles.samples,'exposure':s.view_settings.exposure}
original_settings=settings();s.render.threads_mode='FIXED';s.render.threads=4
def fingerprints():
 out={};shared={}
 for ob in s.objects:
  h=hashlib.sha256(str(tuple(tuple(row) for row in ob.matrix_world)).encode())
  if ob.type=='MESH':
   ptr=ob.data.as_pointer()
   if ptr not in shared:
    a=array.array('f',[0.])*(len(ob.data.vertices)*3);ob.data.vertices.foreach_get('co',a)
    b=array.array('i',[0])*len(ob.data.loops);ob.data.loops.foreach_get('vertex_index',b)
    shared[ptr]=hashlib.sha256(a.tobytes()+b.tobytes()).digest()
   h.update(shared[ptr])
  if ob.type=='CAMERA':h.update(str((ob.data.lens,ob.data.sensor_width,ob.data.sensor_height,ob.data.shift_x,ob.data.shift_y,ob.data.clip_start,ob.data.clip_end,ob.data.type)).encode())
  if ob.type=='LIGHT':h.update(str((ob.data.type,ob.data.energy,tuple(ob.data.color))).encode())
  h.update(str(tuple(m.name if m else None for m in getattr(ob.data,'materials',[]))).encode())
  h.update(str((ob.hide_render,ob.hide_viewport)).encode());out[ob.name]=h.hexdigest()
 return out
def verts(ob):return [list(ob.matrix_world@v.co) for v in ob.data.vertices]
def area(p):return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1])))*.5
def inside(x,y,p):
 yes=False
 for a,b in zip(p,p[1:]+p[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:yes=not yes
 return yes
def make_bvhs():
 dg=bpy.context.evaluated_depsgraph_get();out={}
 for ob in s.objects:
  if ob.type!='MESH' or not ob.name.startswith('MAIN_') or len(ob.data.vertices)>500:continue
  e=ob.evaluated_get(dg);m=e.to_mesh()
  out[ob.name]=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(f.vertices) for f in m.polygons]);e.to_mesh_clear()
 return out
def cast(o,d,dist=100):
 hit,p,n,f,ob,_=s.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector(o),Vector(d),distance=dist)
 return {'object':ob.name if hit else None,'point':list(p) if hit else None}
def layers(bvhs,q,z,ceil=False):
 out=[];dire=Vector((0,0,1 if ceil else -1));origin=Vector((q[0],q[1],z))+dire*-.08
 for n,t in bvhs.items():
  if ('ceiling' not in n) if ceil else (not n.endswith('_finish')):continue
  p,no,f,d=t.ray_cast(origin,dire,.16)
  if p is not None and abs(p.z-z)<.0001:out.append(n)
 return out
before=fingerprints();old_bvhs=make_bvhs()
prior=json.loads((R/'qa/structure08b-remaining-review.json').read_text())
extra=json.loads((R/'qa/structure09-extra-probe.json').read_text())
pixel_records=prior['results']+extra['results']
for r in pixel_records:r['baseline08']=cast(r['camera_origin'],r['ray_direction'])
controls=[('L3_stair_west',(400,280),5.28615),('L3_stair_east',(420,280),5.28615),('Alcove_lower_west_not_extended',(433,265),5.28615)]
control_before=[{'id':n,'source_px':p,'z':z,'hit':cast((*mh.xy(p),z+.1),(0,0,-1),4),'finish_layers':layers(old_bvhs,mh.xy(p),z)} for n,p,z in controls]
route_bytes=(R/'data/tour-route.json').read_bytes();route=json.loads(route_bytes)
route_sha=hashlib.sha256(route_bytes).hexdigest();(R/'qa/structure09-route-snapshot.json').write_bytes(route_bytes)
specs=[]
for rid in ('MAIN_L2_CLOSET_M','MAIN_L3_BATH','MAIN_L3_ALCOVE'):
 z=mh.LEVELS['L2' if '_L2_' in rid else 'L3'];p=mh.closed_floor_source_polygon(rid)
 specs += [(rid+'_slab',p,z-.22,z),(rid+'_finish',p,z,z+.022)]
rr=next(t[2] for t in mh.THRESHOLDS if t[0]=='entry_coat');p=mh.physical_threshold_source_polygon('entry_coat',rr)
specs += [('MAIN_floor_threshold_entry_coat',p,-.08,.1),('MAIN_floor_threshold_entry_coat_finish',p,.1,.122),('MAIN_L2_CLOSET_M_ceiling',mh.closed_ceiling_source_polygon('MAIN_L2_CLOSET_M'),5.,5.018)]
rr=next(t[2] for t in mh.THRESHOLDS if t[0]=='gallery_alcove');p=mh.physical_threshold_source_polygon('gallery_alcove',rr)
specs += [('MAIN_floor_threshold_gallery_alcove',p,5.08415,5.26415),('MAIN_floor_threshold_gallery_alcove_finish',p,5.26415,5.28615)]
old={};expected={};polygons={}
for name,p,z0,z1 in specs:
 ob=s.objects[name];old[name]=verts(ob);wp=[mh.xy(v) for v in p]
 oldp=[tuple(v[:2]) for v in old[name][:len(old[name])//2]]
 polygons[name]={'source':p,'world':wp,'old_world':oldp,'old_area_m2':area(oldp),'new_area_m2':area(wp),'z_range':[z0,z1]}
 tmp=poly_prism('QA09_temp',wp,z0,z1,ob.data.materials[0],collection('QA09_transient'));bpy.context.view_layer.update()
 expected[name]=verts(tmp);ob.data=tmp.data.copy();ob.matrix_world=tmp.matrix_world.copy();ob['physical_revision']='09 source-constrained closure/shared edge';bpy.data.objects.remove(tmp,do_unlink=True)
bpy.data.collections.remove(bpy.data.collections['QA09_transient'])
new_name='MAIN_L1_entry_east_corner_core';assert new_name not in s.objects
p=mh.entry_east_corner_source_polygon();wp=[mh.xy(v) for v in p]
ob=poly_prism(new_name,wp,.1,2.58,s.objects['MAIN_L1_entry_east_1'].data.materials[0],collection('MAIN_Architecture'))
tag(ob,reference='HABS PA-5346 sheet04 continuous hatched L-core; C trace',evidence='C',role='wall');ob['component_type']='wall';ob['physical_revision']='09 L-core outside corner joins butt-ended legs'
polygons[new_name]={'source':p,'world':wp,'old_area_m2':0,'new_area_m2':area(wp),'z_range':[.1,2.58]}
bpy.context.view_layer.update();expected[new_name]=verts(ob)
after=fingerprints();changed=sorted(n for n in before if before[n]!=after[n]);added=sorted(set(after)-set(before))
assert changed==sorted(x[0] for x in specs);assert added==[new_name];assert set(before)<=set(after)
assert all(before[n]==after[n] for n in before if n not in changed)
# Keep input render, route-animation, camera and lighting settings in the saved candidate.
s.render.threads_mode=original_settings['threads_mode'];s.render.threads=original_settings['threads'];assert settings()==original_settings
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));bpy.ops.wm.open_mainfile(filepath=str(OUT));s=bpy.context.scene
saved_settings=settings();assert saved_settings==original_settings;s.render.threads_mode='FIXED';s.render.threads=4
repro=max(abs(a[k]-b[k]) for name,v in expected.items() for a,b in zip(v,verts(s.objects[name])) for k in range(3));assert repro<1e-6
bvhs=make_bvhs();pixels=[]
for r in pixel_records:
 hit=cast(r['camera_origin'],r['ray_direction']);q=r['expected_plane_point'];z=r['expected_z'];surface=layers(bvhs,q,z,z==5.)
 key=(r['camera'],tuple(r['pixel']))
 unresolved=key==('CAM_MAIN_L1_LOGGIA_A',(638,373))
 stone_control=key in [('CAM_MAIN_L1_LOGGIA_A',(270,429)),('CAM_MAIN_L1_LOGGIA_A',(615,359))]
 core_fix=key==('CAM_MAIN_L1_LOGGIA_A',(289,409))
 if unresolved:ok=hit['object']==r['baseline08']['object']
 elif stone_control:ok=hit['object']==r['baseline08']['object']
 elif core_fix:ok=hit['object']==new_name
 elif key==('CAM_MAIN_L3_BATH_A',(163,318)):ok=len(surface)==1
 else:ok=len(surface)==1 and hit['point'] is not None and abs(hit['point'][2]-z)<.001
 pixels.append({'camera':r['camera'],'pixel':r['pixel'],'source_px':r['source_px'],'baseline08':r['baseline08'],'after':hit,'expected_z':z,'finish_or_ceiling_layers':surface,'unresolved_preserved_not_passed':unresolved,'pass_local_regression':ok})
neighborhood=[]
for r in prior['doorway_neighborhoods']:
 p=mh.xy(r['floor_source_px']);now=layers(bvhs,p,.122);nprev=len(r['finish_layers_at_expected_floor'])
 neighborhood.append({'pixel':r['pixel'],'source_px':r['floor_source_px'],'before':r['finish_layers_at_expected_floor'],'after':now,'pass_':len(now)==1 if nprev else len(now)==0})
grid=[]
for name in [n for n in changed if n.endswith('_finish') or 'ceiling' in n]:
 pp=polygons[name];p=pp['world'];oldp=pp['old_world'];both=p+oldp;xlo,xhi=min(v[0] for v in both),max(v[0] for v in both);ylo,yhi=min(v[1] for v in both),max(v[1] for v in both)
 z=pp['z_range'][0] if 'ceiling' in name else pp['z_range'][1]
 for ix in range(37):
  for iy in range(37):
   x=xlo+(xhi-xlo)*(ix+.47)/37;y=ylo+(yhi-ylo)*(iy+.43)/37
   if not inside(x,y,p) and not inside(x,y,oldp):continue
   ll=layers(bvhs,(x,y),z,'ceiling' in name)
   grid.append({'owner':name,'point':[x,y,z],'layers':ll,'pass_':len(ll)==1})
core_grid=[]
for ix in range(7):
 for iy in range(7):
  p=polygons[new_name]['world'];x=min(v[0] for v in p)+(.25)*(ix+.5)/7;y=min(v[1] for v in p)+(.25)*(iy+.5)/7
  for z in (.13,1.35,2.54):
   hits=[]
   for direction in (Vector((1,0,0)),Vector((-1,0,0)),Vector((0,1,0)),Vector((0,-1,0))):
    q,no,face,dist=bvhs[new_name].ray_cast(Vector((x,y,z)),direction,.4)
    hits.append({'point':list(q) if q is not None else None,'distance':dist})
   core_grid.append({'xyz':[x,y,z],'four_side_intersections':hits,'pass_':all(h['point'] is not None for h in hits)})
control_after=[]
for r in control_before:
 h=cast((*mh.xy(r['source_px']),r['z']+.1),(0,0,-1),4);ll=layers(bvhs,mh.xy(r['source_px']),r['z'])
 err=0 if h['point'] is None and r['hit']['point'] is None else (math.dist(h['point'],r['hit']['point']) if h['point'] and r['hit']['point'] else 999)
 control_after.append(dict(r,after=h,after_layers=ll,pass_=h['object']==r['hit']['object'] and err<1e-5 and ll==r['finish_layers']))
# Control the previously retained narrow source opening through the original 07 rays.
oldprobe=json.loads((R/'qa/structure08b-probe.json').read_text())
opening_controls=[]
for r in oldprobe['pixels']:
 if r['camera']=='CAM_MAIN_L1_SERVANT_B' and r['pixel'][1]<50:
  opening_controls.append({'camera':r['camera'],'pixel':r['pixel'],'note':'Existing opening objects and all source walls unchanged by scoped fingerprint; retained prior evidence.'})
cv=[];cf=[]
for name in changed+added:
 ob=s.objects[name];e=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();off=len(cv);cv.extend(e.matrix_world@v.co for v in m.vertices);cf.extend(tuple(off+i for i in f.vertices) for f in m.polygons);e.to_mesh_clear()
body_tree=BVHTree.FromPolygons(cv,cf);body_n=0;body_hits=[];route_floor=[]
def body(q,label):
 global body_n
 for dz in (0,-.65,-1.3):
  p=Vector(q)+Vector((0,0,dz));h=body_tree.find_nearest(p,.18);body_n+=1
  if h[0] is not None:body_hits.append({'label':label,'point':list(p),'distance':h[3]})
for ob in s.objects:
 if ob.type=='CAMERA':body(ob.matrix_world.translation,ob.name)
for seg in route['main_segments']+route['supplemental_segments']:
 rel=next((rid for rid in seg.get('room_ids',[]) if rid in ('MAIN_L1_LOGGIA','MAIN_L1_COAT','MAIN_L2_MASTER','MAIN_L2_CLOSET_M','MAIN_L3_BATH','MAIN_L3_ALCOVE')),None)
 for i,(a,b) in enumerate(zip(seg['points'],seg['points'][1:])):
  a,b=Vector(a),Vector(b);n=max(2,math.ceil((b-a).length/.1))
  for k in range(n+1):
   q=a.lerp(b,k/n);body(q,f"{seg['id']}:{i}:{k}")
   if rel:
    floorz=.122 if '_L1_' in rel else (2.8668 if '_L2_' in rel else 5.28615)
    r=cast((q.x,q.y,floorz+.1),(0,0,-1),.5);r.update(segment=seg['id'],point_on_route=list(q),pass_=r['point'] is not None and abs(r['point'][2]-floorz)<.08);route_floor.append(r)
thresholds=[]
for tid,rid,rr,lev,mat,path in mh.THRESHOLDS:
 z=mh.LEVELS[lev]+.022;a,b=map(Vector,map(mh.xy,path))
 for i in range(31):
  p=a.lerp(b,i/30);oldlayers=layers(old_bvhs,p,z);newlayers=layers(bvhs,p,z)
  # An existing threshold remains supported; this stage does not assert global prior gaps passed.
  thresholds.append({'threshold':tid,'xyz':[p.x,p.y,z],'before':oldlayers,'after':newlayers,'pass_':not oldlayers or bool(newlayers)})
counts={'changed':len(changed),'added':len(added),'original_pixels':len(pixels),'pixel_regression_fails':sum(not r['pass_local_regression'] for r in pixels),'unresolved_original_pixels':sum(r['unresolved_preserved_not_passed'] for r in pixels),'door_neighbors':len(neighborhood),'door_neighbor_fails':sum(not r['pass_'] for r in neighborhood),'old_and_new_surface_grid':len(grid),'surface_grid_fails':sum(not r['pass_'] for r in grid),'core_volume_samples':len(core_grid),'core_fails':sum(not r['pass_'] for r in core_grid),'opening_controls':len(control_after),'opening_control_fails':sum(not r['pass_'] for r in control_after),'body_samples':body_n,'body_hits':len(body_hits),'route_floor_samples':len(route_floor),'route_floor_fails':sum(not r['pass_'] for r in route_floor),'all_threshold_samples':len(thresholds),'threshold_regression_fails':sum(not r['pass_'] for r in thresholds)}
report={'status':'PASS_SCOPED_STRUCTURE09_ONE_KNOWN_LOGGIA_BOUNDARY_UNRESOLVED_VISUAL_NOT_RUN' if not any(v for k,v in counts.items() if k.endswith(('_fails','_hits'))) else 'FAIL_LOCAL_STRUCTURE09','source':str(SRC),'source_sha256':sha(SRC),'candidate':str(OUT),'candidate_sha256':sha(OUT),'source_script_sha256':sha(R/'scripts/main_house.py'),'changed':changed,'added':added,'all_non_targets_identical':all(before[n]==after[n] for n in before if n not in changed),'saved_settings_identical':saved_settings==original_settings,'saved_settings':saved_settings,'rebuild_max_error_m':repro,'polygons':polygons,'old_vertices':old,'counts':counts,'pixels':pixels,'door_neighbors':neighborhood,'surface_grid':grid,'core_volume':core_grid,'opening_controls':control_after,'prior_source_opening_controls':opening_controls,'body_hits':body_hits,'route_floor':route_floor,'all_thresholds':thresholds,'route_sha256_used':route_sha,'route_sha256_at_end':sha(R/'data/tour-route.json'),'limits':['Right Loggia pixel638,373 lacks support but stone versus pavement boundary remains C-level trace uncertainty; deliberately not claimed fixed.','No camera/light/furnishing/door/stair edits; source08 remains frozen.','Local body and sampled floor regressions do not replace the integrator full candidate tour acceptance.','Exact Bath pixels270275,384229,411195 and Stair625327 originally had floors; they remain positive controls, not preexisting holes.']}
(R/'qa/structure09-candidate-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
mh.export_data(R/'qa/structure09-main-house-data.json')
print(json.dumps({k:report[k] for k in ('status','candidate_sha256','source_script_sha256','counts')},indent=2))
