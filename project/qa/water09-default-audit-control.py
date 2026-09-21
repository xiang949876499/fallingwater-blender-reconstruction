"""Authorized once: factory-default cube liquid12, CPU4. No render/production."""
import sys,json,hashlib,time,math
from pathlib import Path
import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
PILOT=ROOT/'scene/Fallingwater_water09_factory_default12.blend'
CACHE=ROOT/'caches/fluid_water09/factory12'
REPORT=ROOT/'qa/water09-default-audit-control.json'
DOMAIN='WATER09_Factory_Default_Domain';LIQUID='WATER09_Factory_Default_Initial_Liquid'
KEYS=['domain_type','resolution_max','simulation_method','flip_ratio','use_adaptive_timesteps','cfl_condition','timesteps_min','timesteps_max','particle_radius','particle_number','particle_min','particle_max','particle_randomness','particle_band_width','sys_particle_maximum','use_fractions','fractions_distance','fractions_threshold','delete_in_obstacle','use_flip_particles','use_foam_particles','use_spray_particles','use_bubble_particles','use_tracer_particles','use_guide','use_diffusion','use_viscosity','surface_tension','time_scale','use_mesh','mesh_scale','mesh_particle_radius','mesh_generator','mesh_smoothen_pos','mesh_smoothen_neg']+['use_collision_border_'+s for s in ('front','back','left','right','top','bottom')]
FLOW=['flow_type','flow_behavior','flow_source','use_initial_velocity','velocity_factor','velocity_normal','velocity_random','volume_density','surface_distance','use_plane_init','use_inflow','subframes']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(r):REPORT.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
def cube(name,lo,hi):
 p=[(lo[0],lo[1],lo[2]),(hi[0],lo[1],lo[2]),(hi[0],hi[1],lo[2]),(lo[0],hi[1],lo[2]),(lo[0],lo[1],hi[2]),(hi[0],lo[1],hi[2]),(hi[0],hi[1],hi[2]),(lo[0],hi[1],hi[2])]
 me=bpy.data.meshes.new(name);me.from_pydata(p,[],[(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]);me.update();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);return o
def get():
 s=bpy.context.scene;o=s.objects[DOMAIN];d=next(m.domain_settings for m in o.modifiers if m.type=='FLUID');initial=s.objects[LIQUID];f=next(m.flow_settings for m in initial.modifiers if m.type=='FLUID');return s,o,d,initial,f
def validate():
 s,o,d,initial,f=get();expected=json.loads((ROOT/'qa/water09-default-audit.json').read_text(encoding='utf-8'))['factory'];actual={k:getattr(d,k) for k in KEYS};flow={k:getattr(f,k) for k in FLOW};mismatch=[]
 for k,v in actual.items():
  target=expected['domain']['properties'][k]
  if isinstance(v,float):same=abs(v-target)<1e-6
  else:same=v==target
  if not same:mismatch.append([k,v,target])
 for k,v in flow.items():
  if v!=expected['flow']['properties'][k]:mismatch.append(['flow.'+k,v,expected['flow']['properties'][k]])
 assert not mismatch,mismatch
 assert list(f.velocity_coord)==[0,0,0] and not f.use_initial_velocity
 assert len(s.objects)==2 and set(s.objects.keys())=={DOMAIN,LIQUID}
 assert d.fluid_group is None and d.effector_group is None and d.use_guide is False
 assert not any(getattr(d,k) for k in ('use_foam_particles','use_spray_particles','use_bubble_particles','use_tracer_particles'))
 systems=[ps.settings.type for ps in o.particle_systems];assert systems==['FLIP'],systems
 cachecheck={'cache_type':d.cache_type,'cache_resumable':d.cache_resumable,'cache_directory_saved':d.cache_directory,'cache_directory_resolved':bpy.path.abspath(d.cache_directory)}
 assert d.cache_type=='ALL' and d.cache_resumable is True and Path(bpy.path.abspath(d.cache_directory)).resolve()==CACHE.resolve(),cachecheck
 assert d.cache_frame_start==1 and d.cache_frame_end==12
 assert s.render.fps==24 and abs(s.unit_settings.scale_length-1)<1e-6 and s.use_gravity and abs(s.gravity.z+9.81)<1e-5
 for obj,size in ((o,(2,2,2)),(initial,(2,2,1))):
  a=np.array([tuple(v.co) for v in obj.data.vertices]);assert np.max(np.abs(a.max(0)-a.min(0)-np.array(size)))<1e-6
  assert list(obj.scale)==[1,1,1] and obj.parent is None and not obj.animation_data
 bm=bmesh.new();bm.from_mesh(initial.data);vol=bm.calc_volume(signed=True);boundary=sum(not e.is_manifold for e in bm.edges);bm.free();assert abs(vol-4)<1e-6 and boundary==0
 return {'domain_actual':actual,'flow_actual':flow,'initial_world_velocity':[0,0,0],'particle_systems':systems,'initial_volume_m3':vol,'nonmanifold_edges':boundary,'objects':len(s.objects),'all_assertions_passed':True,'cache_resumable':True}
def prepare():
 assert not PILOT.exists() and not CACHE.exists(),'One authorized new control only'
 bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
 o=cube(DOMAIN,(-1,-1,-1),(1,1,1));m=o.modifiers.new('Default liquid domain','FLUID');m.fluid_type='DOMAIN';d=m.domain_settings;d.domain_type='LIQUID'
 initial=cube(LIQUID,(-1,-1,-1),(1,1,0));m=initial.modifiers.new('Default geometry liquid','FLUID');m.fluid_type='FLOW';f=m.flow_settings;f.flow_type='LIQUID';f.flow_behavior='GEOMETRY'
 switchlog=[]
 for key in ('use_foam_particles','use_spray_particles','use_bubble_particles'):
  before=bool(getattr(d,key))
  if before:setattr(d,key,False)
  switchlog.append({'property':key,'before':before,'assigned':before,'after':bool(getattr(d,key))})
 d.cache_type='ALL';d.cache_directory=str(CACHE);d.cache_frame_start=1;d.cache_frame_end=12;d.cache_resumable=True
 s.frame_start=1;s.frame_end=12;s.render.threads_mode='FIXED';s.render.threads=4;s.frame_set(1)
 s['water09_status']='FACTORY_DEFAULT_STATIC_CONTROL_NOT_PRODUCTION';bpy.context.view_layer.update();v=validate()
 r={'status':'PREPARED_REOPEN_ASSERT_REQUIRED','candidate':str(PILOT),'source':'Independent factory startup; no project helper or existing scene imported','frame_range':[1,12],'fps':24,'threads':4,'resolution':32,'grid_cells':32768,'cell_m':.0625,'domain_bounds_m':[[-1,1]]*3,'initial_liquid_bounds_m':[[-1,1],[-1,1],[-1,0]],'initial_head_z_m':0,'initial_volume_m3':4,'expected_control':'Factory static liquid in closed cube; not real river','production_installed':False,'render_run':False,'secondary_setter_log':switchlog,'pre_save_assertions':v,'hard_stop_seconds':90,'cost_estimate_seconds':[15,60],'cost_estimate_bytes':[10000000,60000000],'root_cache_expected_under_bytes':100000000,'no_automatic_extension':True}
 CACHE.mkdir(parents=True);bpy.ops.wm.save_as_mainfile(filepath=str(PILOT));r['prepared_sha256']=sha(PILOT);write(r);print('FACTORY12_PREPARED',json.dumps(v),flush=True)
def bake():
 r=json.loads(REPORT.read_text(encoding='utf-8'));assert r['status']=='PREPARED_REOPEN_ASSERT_REQUIRED';assert sha(PILOT)==r['prepared_sha256'];assert not list(CACHE.rglob('*.bobj.gz'))
 bpy.ops.wm.open_mainfile(filepath=str(PILOT));s,o,d,initial,f=get();s.render.threads_mode='FIXED';s.render.threads=4
 r['reopened_assertions']=validate();r['status']='REOPEN_ASSERT_PASS_BAKING_ONCE';write(r);print('FACTORY12_REOPEN_ASSERT_PASS',flush=True)
 for ob in bpy.context.selected_objects:ob.select_set(False)
 o.select_set(True);bpy.context.view_layer.objects.active=o;t=time.perf_counter();result=bpy.ops.fluid.bake_all();r['bake_seconds']=time.perf_counter()-t;r['bake_result']=list(result)
 s.frame_set(12);bpy.ops.wm.save_as_mainfile(filepath=str(PILOT));r['baked_sha256']=sha(PILOT);files=[p for p in CACHE.rglob('*') if p.is_file()];r['cache_files']=len(files);r['cache_bytes']=sum(p.stat().st_size for p in files);r['status']='BAKED12_RAW_CHECK_PENDING';write(r);print('FACTORY12_BAKED',r['bake_seconds'],r['cache_bytes'],flush=True)
def check():
 r=json.loads(REPORT.read_text(encoding='utf-8'));assert r['status']=='BAKED12_RAW_CHECK_PENDING';assert sha(PILOT)==r['baked_sha256'];bpy.ops.wm.open_mainfile(filepath=str(PILOT));s,o,d,initial,f=get();s.render.threads_mode='FIXED';s.render.threads=4
 r['post_bake_secondary_flags']={k:bool(getattr(d,k)) for k in ('use_foam_particles','use_spray_particles','use_bubble_particles')};assert not any(r['post_bake_secondary_flags'].values())
 xy=np.array([(x,y) for y in np.linspace(-.75,.75,25) for x in np.linspace(-.75,.75,25)]);frames=[];heights=[];envelopes=[]
 for frame in range(1,13):
  s.frame_set(frame);bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();vv=np.array([tuple(o.matrix_world@v.co) for v in me.vertices],np.float64);ff=np.array([tuple(t.vertices) for t in me.loop_triangles],np.int32);tt=vv[ff]
  volume=float(np.einsum('ij,ij->i',tt[:,0],np.cross(tt[:,1],tt[:,2])).sum()/6);tree=BVHTree.FromPolygons(vv,ff,all_triangles=True);z=[]
  for x,y in xy:
   hit=tree.ray_cast(Vector((x,y,.8)),Vector((0,0,-1)),2);z.append(hit[0].z if hit[0] else np.nan)
  z=np.asarray(z);edges=np.concatenate((ff[:,[0,1]],ff[:,[1,2]],ff[:,[2,0]]));edges.sort(axis=1);_,counts=np.unique(edges,axis=0,return_counts=True)
  ps=next(ps for ps in ev.particle_systems if ps.settings.type=='FLIP');a=np.empty(len(ps.particles)*3,np.float32);ps.particles.foreach_get('location',a);a=a.reshape(-1,3);idx=np.floor((a[:,:2]+1)/.0625).astype(int);valid=np.all((idx>=0)&(idx<32),axis=1);flat=idx[valid,0]*32+idx[valid,1];top=np.full(32*32,-np.inf,np.float32);np.maximum.at(top,flat,a[valid,2]);top=top.reshape(32,32)
  inside=top[4:28,4:28];env=inside[np.isfinite(inside)];envelopes.append(top)
  row={'frame':frame,'vertices':len(vv),'triangles':len(ff),'mesh_volume_m3':volume,'boundary_edges':int((counts==1).sum()),'nonmanifold_edges':int((counts!=2).sum()),'height_samples':len(z),'height_missing':int((~np.isfinite(z)).sum()),'mesh_median_head_m':float(np.nanmedian(z)),'mesh_p95_abs_head_m':float(np.nanquantile(abs(z),.95)),'mesh_minmax_head_m':[float(np.nanmin(z)),float(np.nanmax(z))],
  'FLIP_count':len(ps.particles),'particle_systems':[{'type':p.settings.type,'count':len(p.particles)} for p in ev.particle_systems],'FLIP_world_bounds_m':[[float(a[:,k].min()),float(a[:,k].max())] for k in range(3)],'FLIP_top_envelope_interior_columns':len(env),'FLIP_top_envelope_median_m':float(np.median(env)),'FLIP_top_envelope_p05_p95_m':np.quantile(env,[.05,.95]).tolist(),'FLIP_z_quantiles_m':np.quantile(a[:,2],[0,.25,.5,.75,1]).tolist(),'FLIP_outside_domain_points':int(np.any((a< -1-1e-5)|(a>1+1e-5),axis=1).sum())}
  frames.append(row);heights.append(z);print('FACTORY12_FRAME',json.dumps(row),flush=True);ev.to_mesh_clear()
 v1=frames[0]['mesh_volume_m3'];a=np.asarray(heights);delta=a-a[0];volumedrift=max(abs(f['mesh_volume_m3']/v1-1) for f in frames);head=max(abs(f['mesh_median_head_m']-frames[0]['mesh_median_head_m']) for f in frames);pointmedian=max(abs(np.median(row)) for row in delta[1:]);p95=max(np.quantile(abs(row),.95) for row in delta[1:]);envdrift=max(abs(f['FLIP_top_envelope_median_m']-frames[0]['FLIP_top_envelope_median_m']) for f in frames)
 passed=volumedrift<=.03 and head<=.0625 and p95<=.125 and envdrift<=.0625 and all(f['height_missing']==0 and f['boundary_edges']==f['nonmanifold_edges']==0 for f in frames)
 r['frames']=frames;r['check_summary']={'frame1_relative_initial_volume_error':v1/4-1,'max_relative_volume_drift_from_f1':volumedrift,'max_median_dynamic_height_drift_m':float(head),'max_pointwise_height_difference_median_m':float(pointmedian),'max_p95_dynamic_height_drift_m':float(p95),'max_particle_envelope_median_drift_m':envdrift,'particle_envelope_is_geometry_proxy_not_conserved_mass':True};r['status']='FACTORY_MINIMAL_STATIC_PASS_NOT_COMPLEX_SCENE_PROOF' if passed else 'FACTORY_MINIMAL_STATIC_FAIL_NO_AUTO_REPEAT'
 r['mesh_hashes']=[{'name':p.name,'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(CACHE.rglob('*.bobj.gz'))];r['checked_scene_sha256']=sha(PILOT)
 try:
  import openvdb
  r['actual_data_vdb_grids']=[{'name':g.name,'type':g.valueTypeName} for g in openvdb.readAllGridMetadata(str(CACHE/'data/fluid_data_0012.vdb'))]
 except Exception as e:r['actual_data_vdb_grids_error']=repr(e)
 np.savez_compressed(ROOT/'qa/water09-default-audit-control-heights.npz',xy=xy,height=a,FLIP_envelope=np.asarray(envelopes));write(r);print('FACTORY12_CHECK_RESULT',r['status'],json.dumps(r['check_summary']),flush=True)
if __name__=='__main__':
 assert bpy.app.background
 action=sys.argv[sys.argv.index('--')+1];{'prepare':prepare,'bake':bake,'check':check}[action]()
