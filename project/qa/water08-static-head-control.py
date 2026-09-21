"""One authorized static24 control. Separate prepare, bake, check; never production."""
import argparse,hashlib,json,math,sys,time
from pathlib import Path
import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import hybrid_water as h
import fluid_water as fw
from fwlib import box,collection
SOURCE=ROOT/'scene/Fallingwater_hybrid07_impact36.blend'
SOURCE_SHA='7093200e28e1c135e559ccc8605fad04e14de7cf92399baef3151f5523f7537e'
PILOT=ROOT/'scene/Fallingwater_water08_static_head24.blend'
CACHE=ROOT/'caches/fluid_water08/static_head24'
REPORT=ROOT/'qa/water08-static-head24.json'
DOMAIN='WATER08_Static_Head_Control_Domain';INIT='WATER08_Complete_Connected_Initial_Pool'
ROI=[[-.4026584744,1.9973415256],[-3.2114176750,-1.2114176750],[-6.56,-5.55]]
HEAD=-5.771274;CELL=.025

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(r):h.write(REPORT,r)
def array(me):
 a=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',a);return a.reshape(-1,3).astype(np.float64)
def component_count(me):
 parent=list(range(len(me.vertices)))
 def root(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 for e in me.edges:
  a,b=map(root,e.vertices);parent[a]=b
 return len({root(i) for i in range(len(parent))})
def clip_xy(poly,k,value,keepgreater):
 if not poly:return []
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  insidea=(a[k]>=value) if keepgreater else (a[k]<=value);insideb=(b[k]>=value) if keepgreater else (b[k]<=value)
  if insidea:out.append(a)
  if insidea!=insideb:out.append(a+(b-a)*((value-a[k])/(b[k]-a[k])))
 return out

def prepare():
 assert not PILOT.exists() and not CACHE.exists(),'Do not overwrite or repeat authorized control'
 assert sha(SOURCE)==SOURCE_SHA
 bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene
 scene.render.threads_mode='FIXED';scene.render.threads=4
 keepcoll=bpy.data.collections['HYBRID07_IMPACT_COLLISIONS'];colliders=list(keepcoll.objects)
 olddomain=scene.objects['HYBRID07_Impact_Liquid_Domain'];mat=olddomain.data.materials[0]
 hashes={o.name:h.shape_hash(o) for o in colliders}
 bpy.data.batch_remove(ids=[o for o in bpy.data.objects if o not in colliders])
 scene.frame_start=1;scene.frame_end=24;scene.frame_set(1);scene.render.fps=24;scene.gravity=(0,0,-9.81)
 coll=collection('WATER08_STATIC_CONTROL');sources=collection('WATER08_STATIC_INITIAL_ONLY')
 init=box(INIT,((ROI[0][0]+ROI[0][1])/2,(ROI[1][0]+ROI[1][1])/2,(HEAD+ROI[2][0])/2),
  (2.4,2,HEAD-ROI[2][0]),mat,sources,0)
 # Difference against the exact frozen collision meshes, not a displayed water footprint.
 booleans=[]
 for o in colliders:
  before=h.topology(init);h.apply_boolean(init,o,'DIFFERENCE','Exact fluid space excluding '+o.name)
  booleans.append({'collider':o.name,'before':before,'after':h.topology(init)})
 bm=bmesh.new();bm.from_mesh(init.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(init.data);bm.free()
 topo=h.topology(init);components=component_count(init.data)
 assert topo['boundary_edges']==topo['nonmanifold_edges']==0 and topo['signed_volume_m3']>0
 assert components==1,('Initial fluid space is not one connected volume',components)
 bpy.context.view_layer.update();itree=h.render_bvh(init);trees={o.name:h.render_bvh(o) for o in colliders}
 terrain=next(o for o in colliders if 'Terrain_Top' in o.name);terrain.data.calc_loop_triangles()
 bed_min=[];clipped=0
 for tr in terrain.data.loop_triangles:
  if tr.normal.z<.01:continue
  poly=[terrain.matrix_world@terrain.data.vertices[i].co for i in tr.vertices]
  for k in (0,1):
   poly=clip_xy(poly,k,ROI[k][0],True);poly=clip_xy(poly,k,ROI[k][1],False)
  if len(poly)<3:continue
  clipped+=1;bed_min.extend(p.z for p in poly)
 assert bed_min and min(bed_min)>=ROI[2][0]+.04,'Exact clipped top bed is not vertically contained'
 # Cell-center coverage compares actual source against terrain/core visibility at the chosen head.
 xs=np.linspace(ROI[0][0]+CELL*.5,ROI[0][1]-CELL*.5,96);ys=np.linspace(ROI[1][0]+CELL*.5,ROI[1][1]-CELL*.5,80)
 coverage=[];depth=[];unfilled=[];above=[]
 for y in ys:
  for x in xs:
   origin=Vector((x,y,0));rockhits=[t.ray_cast(origin,Vector((0,0,-1)),20)[0] for t in trees.values()]
   top=max([p.z for p in rockhits if p is not None],default=ROI[2][0])
   hit=itree.ray_cast(origin,Vector((0,0,-1)),20)
   exposed=top<HEAD-CELL*.25;athead=hit[0] is not None and abs(hit[0].z-HEAD)<1e-5 and hit[1].z>.9
   if exposed:
    coverage.append(int(athead));depth.append(HEAD-top)
    if not athead:unfilled.append([x,y,top,hit[0].z if hit[0] else None])
   if hit[0] and hit[0].z>HEAD+1e-5:above.append([x,y,hit[0].z])
 assert coverage and not unfilled and not above,'Source does not cover all exposed connected pool cells at the intended head'
 assert hashes=={o.name:h.shape_hash(o) for o in colliders},'Frozen collision geometry mutated'
 np.savez_compressed(ROOT/'qa/water08-static-head24-preflight-grid.npz',xs=xs,ys=ys)
 fw._flow(init,'GEOMETRY',(0,0,0),0)
 domain=box(DOMAIN,tuple((a+b)/2 for a,b in ROI),tuple(b-a for a,b in ROI),mat,coll,0)
 m=domain.modifiers.new('One authorized closed static pool control','FLUID');m.fluid_type='DOMAIN';d=m.domain_settings;d.domain_type='LIQUID'
 d.resolution_max=96;d.cache_type='ALL';d.cache_directory=str(CACHE);d.cache_frame_start=1;d.cache_frame_end=24;d.cache_resumable=False
 d.simulation_method='FLIP';d.flip_ratio=.94;d.timesteps_min=2;d.timesteps_max=12;d.cfl_condition=2;d.time_scale=1
 d.use_mesh=True;d.mesh_scale=1;d.mesh_particle_radius=1.25;d.mesh_smoothen_pos=1;d.mesh_smoothen_neg=1
 d.use_fractions=True;d.delete_in_obstacle=True;d.use_foam_particles=False;d.use_spray_particles=False;d.use_bubble_particles=False
 for side in ('bottom','front','back','left','right'):setattr(d,'use_collision_border_'+side,True)
 d.use_collision_border_top=False;d.fluid_group=sources;d.effector_group=keepcoll
 scene['water08_status']='ARTIFICIAL_CLOSED_STATIC_HEAD_CONTROL_NOT_PRODUCTION';scene.render.threads=8
 report={'status':'PREPARED_PREFLIGHT_PASS_NOT_BAKED','source':str(SOURCE),'source_sha256':SOURCE_SHA,'candidate':str(PILOT),
  'evidence':'C closed static reservoir control on exact frozen terrain; not an open flowing river or visual acceptance',
  'production_install':False,'frame_range':[1,24],'fps':24,'threads':8,'resolution':96,'cell_m':CELL,'grid_estimate':[96,80,41],
  'domain_aabb_m':ROI,'initial_head_z_m':HEAD,'initial_topology':topo,'initial_connected_components':components,
  'collision_world_hashes':hashes,'collision_source_core_hash':'dd86ff944b6e264b542c77f2e8671a53524fc5092dedcfb6db61d697c7c52768',
  'exact_clipped_terrain_triangles':clipped,'exact_clipped_terrain_z_range_m':[min(bed_min),max(bed_min)],
  'minimum_floor_clearance_m':min(bed_min)-ROI[2][0],'exposed_pool_cell_center_count':len(coverage),'unfilled_exposed_pool_cells':unfilled,
  'source_above_head_samples':above,'exposed_pool_depth_m':h.stats(depth),'exposed_pool_area_proxy_m2':len(coverage)*CELL*CELL,
  'initialization':'Entire domain box below original head, exact Boolean subtraction of all unchanged colliders; one connected closed source; no river-display-mask clipping',
  'booleans':booleans,'flow_initial_velocity_m_s':[0,0,0],'sources_behavior':['GEOMETRY'],'inflows':0,'Qin_m3_s':0,'Qout_m3_s':0,
  'boundaries':'All sides/bottom closed, top open; artificial control only','secondary_particles':False,
  'budget_seconds_estimate':[120,300],'hard_stop_seconds':360,'budget_cache_GB_estimate':[.08,.30],
  'acceptance':{'frame5_24_median_drift_max_m':.025,'interior95percent_error_max_m':.05,'relative_mesh_volume_drift_max':.03},
  'no_automatic_extension':True}
 CACHE.mkdir(parents=True);write(report);fw._select(domain);bpy.ops.wm.save_as_mainfile(filepath=str(PILOT));report['prepared_scene_sha256']=sha(PILOT);write(report)
 print('WATER08_STATIC_PREPARED',json.dumps(report),flush=True)

def bake():
 r=json.loads(REPORT.read_text(encoding='utf-8'));assert r['status']=='PREPARED_PREFLIGHT_PASS_NOT_BAKED';assert sha(PILOT)==r['prepared_scene_sha256']
 assert not list(CACHE.rglob('*.bobj.gz')),'No second bake'
 bpy.ops.wm.open_mainfile(filepath=str(PILOT));scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=8;fw._select(scene.objects[DOMAIN])
 r['status']='BAKING_ONCE';write(r);start=time.perf_counter();done=bpy.ops.fluid.bake_all();elapsed=time.perf_counter()-start
 r['status']='BAKED24_RAW_CHECK_PENDING';r['bake_seconds']=elapsed;r['bake_result']=list(done);r['cache_stats']=fw._cache_stats(CACHE);scene.frame_set(24)
 bpy.ops.wm.save_as_mainfile(filepath=str(PILOT));r['baked_scene_sha256']=sha(PILOT);write(r);print('WATER08_STATIC_BAKED',elapsed,flush=True)

def check():
 r=json.loads(REPORT.read_text(encoding='utf-8'));assert r['status']=='BAKED24_RAW_CHECK_PENDING'
 bpy.ops.wm.open_mainfile(filepath=str(PILOT));scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=4
 init=scene.objects[INIT];domain=scene.objects[DOMAIN];itree=h.render_bvh(init)
 xx=np.linspace(ROI[0][0]+.1,ROI[0][1]-.1,65);yy=np.linspace(ROI[1][0]+.1,ROI[1][1]-.1,55)
 expected=[];xy=[]
 for y in yy:
  for x in xx:
   hit=itree.ray_cast(Vector((x,y,0)),Vector((0,0,-1)),20)
   if hit[0] and abs(hit[0].z-HEAD)<1e-5 and hit[1].z>.9:xy.append((x,y));expected.append(HEAD)
 frames=[];allheights=[]
 for frame in range(1,25):
  scene.frame_set(frame);bpy.context.view_layer.update();ev=domain.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles()
  vv=np.array([tuple(domain.matrix_world@v.co) for v in me.vertices],np.float64);ff=np.array([tuple(t.vertices) for t in me.loop_triangles],np.int32)
  tree=BVHTree.FromPolygons(vv,ff,all_triangles=True);height=[];nz=[]
  for x,y in xy:
   hit=tree.ray_cast(Vector((x,y,HEAD+.18)),Vector((0,0,-1)),1.2);height.append(hit[0].z if hit[0] else float('nan'));nz.append(hit[1].z if hit[0] else 0)
  zz=np.array(height);valid=np.isfinite(zz)&(np.array(nz)>.3);delta=zz[valid]-HEAD
  shifted=vv-np.array([0,0,-6]);tt=shifted[ff];volume=float(np.einsum('ij,ij->i',tt[:,0],np.cross(tt[:,1],tt[:,2])).sum()/6)
  edges=np.concatenate((ff[:,[0,1]],ff[:,[1,2]],ff[:,[2,0]]));edges.sort(axis=1);_,counts=np.unique(edges,axis=0,return_counts=True)
  info={'frame':frame,'vertices':len(vv),'triangles':len(ff),'mesh_volume_m3':volume,'boundary_edges':int((counts==1).sum()),'nonmanifold_edges':int((counts!=2).sum()),
   'expected_exposed_height_samples':len(xy),'valid_upward_height_samples':int(valid.sum()),'missing_or_steep_samples':int((~valid).sum()),'median_head_z_m':float(np.median(zz[valid])),
   'median_error_from_initial_head_m':float(np.median(delta)),'p95_abs_error_m':float(np.quantile(np.abs(delta),.95)), 'raw_error_m':h.stats(delta.tolist())}
  frames.append(info);allheights.append(zz);print('WATER08_STATIC_FRAME',json.dumps(info),flush=True);ev.to_mesh_clear()
 v1=frames[0]['mesh_volume_m3'];post=frames[4:]
 maxmed=max(abs(f['median_error_from_initial_head_m']) for f in post);maxp95=max(f['p95_abs_error_m'] for f in post);drift=max(abs(f['mesh_volume_m3']-v1)/v1 for f in frames)
 passed=maxmed<=.025 and maxp95<=.05 and drift<=.03 and all(f['missing_or_steep_samples']==0 and f['boundary_edges']==f['nonmanifold_edges']==0 for f in frames)
 r['status']='STATIC_CONTROL_NUMERIC_PASS_NOT_OPEN_RIVER_OR_VISUAL_PASS' if passed else 'STATIC_CONTROL_FAIL_KEEP_EVIDENCE'
 r['frames']=frames;r['check_summary']={'initial_geometric_volume_m3':r['initial_topology']['signed_volume_m3'],'frame1_mesh_volume_m3':v1,
  'frame1_relative_initial_volume_difference':(v1-r['initial_topology']['signed_volume_m3'])/r['initial_topology']['signed_volume_m3'],
  'max_frame5_24_median_error_m':maxmed,'max_frame5_24_p95_error_m':maxp95,'max_all_frame_relative_volume_drift':drift,
  'frame1_volume_comparison_not_exact_solver_mass':'Reconstructed mesh volume differs from Boolean geometry and solver level-set mass; report difference rather than suppress it'}
 r['checked_scene_sha256']=sha(PILOT);r['source_sha256_after']=sha(SOURCE);r['mesh_cache_sha256']=[{'file':p.name,'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(CACHE.rglob('*.bobj.gz'))]
 np.savez_compressed(ROOT/'qa/water08-static-head24-heights.npz',xy=np.asarray(xy),height=np.asarray(allheights),initial_head=HEAD)
 write(r);print('WATER08_STATIC_CHECK_RESULT',r['status'],json.dumps(r['check_summary']),flush=True)

if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','bake','check']);a=p.parse_args(args)
 {'prepare':prepare,'bake':bake,'check':check}[a.action]()
