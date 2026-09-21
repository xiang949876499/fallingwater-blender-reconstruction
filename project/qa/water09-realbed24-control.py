"""One authorized real-bed/default-primary-physics24 control. Never production."""
import sys,json,hashlib,time,math
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import hybrid_water as h
SOURCE=ROOT/'scene/Fallingwater_water08_static_head24.blend';SOURCE_SHA='c108949a959351a2f0219a1f457b235b34903d9efb50dade5ab533a525d7ef2e'
OLD_CACHE=ROOT/'caches/fluid_water08/static_head24';PILOT=ROOT/'scene/Fallingwater_water09_real_bed_default24.blend';CACHE=ROOT/'caches/fluid_water09/real_bed_default24';REPORT=ROOT/'qa/water09-realbed24-control.json'
DOMAIN='WATER08_Static_Head_Control_Domain';INIT='WATER08_Complete_Connected_Initial_Pool';HEAD=-5.771274
TARGET={'use_fractions':False,'delete_in_obstacle':False,'flip_ratio':.97,'timesteps_min':1,'timesteps_max':4}
KEYS=['domain_type','resolution_max','simulation_method','flip_ratio','use_adaptive_timesteps','cfl_condition','timesteps_min','timesteps_max','particle_radius','particle_number','particle_min','particle_max','particle_randomness','particle_band_width','sys_particle_maximum','use_fractions','fractions_distance','fractions_threshold','delete_in_obstacle','use_flip_particles','use_foam_particles','use_spray_particles','use_bubble_particles','use_tracer_particles','use_guide','use_diffusion','use_viscosity','surface_tension','time_scale','use_mesh','mesh_scale','mesh_particle_radius','mesh_generator','mesh_smoothen_pos','mesh_smoothen_neg']+['use_collision_border_'+s for s in ('front','back','left','right','top','bottom')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(r):REPORT.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
def manifest():return [{'path':str(p.relative_to(OLD_CACHE)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(OLD_CACHE.rglob('*')) if p.is_file()]
def get():
 s=bpy.context.scene;o=s.objects[DOMAIN];d=next(m.domain_settings for m in o.modifiers if m.type=='FLUID');initial=s.objects[INIT];f=next(m.flow_settings for m in initial.modifiers if m.type=='FLUID');return s,o,d,initial,f
def source_state():
 s,o,d,initial,f=get();objects={x.name:{'geometry_world_sha256':h.shape_hash(x),'scale':list(x.scale),'parent':x.parent.name if x.parent else None,'animation':bool(x.animation_data),'topology':h.topology(x)} for x in s.objects}
 return {'domain':{k:getattr(d,k) for k in KEYS},'objects':objects,'flow':{k:(list(getattr(f,k)) if k=='velocity_coord' else getattr(f,k)) for k in ['flow_type','flow_behavior','use_initial_velocity','velocity_coord','velocity_normal','velocity_random','surface_distance','subframes']},'gravity':list(s.gravity),'unit_scale_length':s.unit_settings.scale_length,'fps':s.render.fps,'fluid_group':d.fluid_group.name,'effector_group':d.effector_group.name}
def validate(r):
 actual=source_state();before=r['source_state'];assert actual['objects']==before['objects'],'Physical geometry, topology, transforms or object inventory changed'
 assert actual['flow']==before['flow'] and actual['gravity']==before['gravity'] and actual['unit_scale_length']==before['unit_scale_length'] and actual['fps']==24
 assert actual['fluid_group']==before['fluid_group'] and actual['effector_group']==before['effector_group']
 differences=[]
 for key,value in actual['domain'].items():
  target=TARGET.get(key,False if key in ['use_foam_particles','use_spray_particles','use_bubble_particles'] else before['domain'][key])
  equal=abs(value-target)<1e-6 if isinstance(value,float) else value==target
  assert equal,(key,value,target)
  if value!=before['domain'][key]:differences.append({'property':key,'before':before['domain'][key],'after':value})
 s,o,d,initial,f=get();assert Path(bpy.path.abspath(d.cache_directory)).resolve()==CACHE.resolve() and d.cache_type=='ALL' and d.cache_resumable
 assert d.cache_frame_start==1 and d.cache_frame_end==24 and d.resolution_max==96
 assert [p.settings.type for p in o.particle_systems]==['FLIP']
 return {'passed':True,'actual_domain':actual['domain'],'actual_flow':actual['flow'],'physics_differences':differences,'geometry_unchanged':True,'only_particle_system':'FLIP','resumable':True}
def prepare():
 assert not PILOT.exists() and not CACHE.exists(),'Single new control only';assert sha(SOURCE)==SOURCE_SHA
 original_manifest=manifest();bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s,o,d,initial,f=get();before=source_state()
 # Switch to a fresh cache path BEFORE any parameter callback can invalidate files.
 CACHE.mkdir(parents=True);d.cache_directory=str(CACHE)
 for key,value in TARGET.items():
  if getattr(d,key)!=value:setattr(d,key,value)
 switches=[]
 for key in ('use_foam_particles','use_spray_particles','use_bubble_particles'):
  prev=bool(getattr(d,key))
  if prev:setattr(d,key,False)
  switches.append({'property':key,'before':prev,'assigned':prev,'after':bool(getattr(d,key))})
 d.cache_resumable=True;s.frame_start=1;s.frame_end=24;s.frame_set(1);s.render.threads_mode='FIXED';s.render.threads=8
 s['water09_status']='REAL_BED_DEFAULT_PRIMARY_PHYSICS_CONTROL_NOT_PRODUCTION';bpy.context.view_layer.update()
 r={'status':'PREPARED_REOPEN_ASSERT_REQUIRED','source':str(SOURCE),'source_sha256':SOURCE_SHA,'candidate':str(PILOT),'source_state':before,'original_cache_manifest':original_manifest,
  'source_cache_untouched_after_prepare':manifest()==original_manifest,'only_requested_physics_changes':TARGET,'secondary_setter':switches,
  'frame_range':[1,24],'fps':24,'threads':8,'resolution':96,'head_z_m':HEAD,'cell_m':.025,'domain_aabb_m':[[-.4026584744,1.9973415256],[-3.2114176750,-1.2114176750],[-6.56,-5.55]],
  'production_installed':False,'render_run':False,'comparison_scope':'Multiple primary physics defaults plus secondary-off on identical real bed; not single-variable causal isolation','hard_stop_seconds':180,'resumable':True,'no_automatic_extension':True}
 assert r['source_cache_untouched_after_prepare'];r['pre_save_assertions']=validate(r);bpy.ops.wm.save_as_mainfile(filepath=str(PILOT));r['prepared_sha256']=sha(PILOT);write(r);print('REALBED24_PREPARED',json.dumps(r['pre_save_assertions']),flush=True)
def bake():
 r=json.loads(REPORT.read_text(encoding='utf-8'));assert r['status']=='PREPARED_REOPEN_ASSERT_REQUIRED';assert sha(PILOT)==r['prepared_sha256'];assert not list(CACHE.rglob('*.bobj.gz'))
 bpy.ops.wm.open_mainfile(filepath=str(PILOT));s,o,d,initial,f=get();s.render.threads_mode='FIXED';s.render.threads=8;r['reopened_assertions']=validate(r);r['status']='REOPEN_ASSERT_PASS_BAKING_ONCE';write(r);print('REALBED24_REOPEN_ASSERT_PASS',flush=True)
 for ob in bpy.context.selected_objects:ob.select_set(False)
 o.select_set(True);bpy.context.view_layer.objects.active=o;t=time.perf_counter();done=bpy.ops.fluid.bake_all();r['bake_seconds']=time.perf_counter()-t;r['bake_result']=list(done)
 s.frame_set(24);bpy.ops.wm.save_as_mainfile(filepath=str(PILOT));files=[p for p in CACHE.rglob('*') if p.is_file()];r['cache_files']=len(files);r['cache_bytes']=sum(p.stat().st_size for p in files);r['baked_sha256']=sha(PILOT);r['status']='BAKED24_RAW_CHECK_PENDING';write(r);print('REALBED24_BAKED',r['bake_seconds'],r['cache_bytes'],flush=True)
def check():
 r=json.loads(REPORT.read_text(encoding='utf-8'));assert r['status']=='BAKED24_RAW_CHECK_PENDING';assert sha(PILOT)==r['baked_sha256'];bpy.ops.wm.open_mainfile(filepath=str(PILOT));s,o,d,initial,f=get();s.render.threads_mode='FIXED';s.render.threads=4;r['post_bake_assertions']=validate(r)
 roi=r['domain_aabb_m'];xy=np.array([(x,y) for y in np.linspace(roi[1][0]+.1,roi[1][1]-.1,55) for x in np.linspace(roi[0][0]+.1,roi[0][1]-.1,65)]);frames=[];heights=[];envelopes=[]
 for frame in range(1,25):
  s.frame_set(frame);bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();vv=np.array([tuple(o.matrix_world@v.co) for v in me.vertices],np.float64);ff=np.array([tuple(t.vertices) for t in me.loop_triangles],np.int32);tt=(vv-np.array([0,0,-6]))[ff]
  volume=float(np.einsum('ij,ij->i',tt[:,0],np.cross(tt[:,1],tt[:,2])).sum()/6);tree=BVHTree.FromPolygons(vv,ff,all_triangles=True);z=[];nz=[]
  for x,y in xy:
   hit=tree.ray_cast(Vector((x,y,HEAD+.18)),Vector((0,0,-1)),1.2);z.append(hit[0].z if hit[0] else np.nan);nz.append(hit[1].z if hit[0] else 0)
  z=np.asarray(z);valid=np.isfinite(z)&(np.array(nz)>.3);edges=np.concatenate((ff[:,[0,1]],ff[:,[1,2]],ff[:,[2,0]]));edges.sort(axis=1);_,counts=np.unique(edges,axis=0,return_counts=True)
  ps=next(ps for ps in ev.particle_systems if ps.settings.type=='FLIP');a=np.empty(len(ps.particles)*3,np.float32);ps.particles.foreach_get('location',a);a=a.reshape(-1,3);mins=np.array([p[0] for p in roi]);maxs=np.array([p[1] for p in roi]);idx=np.floor((a[:,:2]-mins[:2])/.025).astype(int);inside=np.all((idx>=0)&(idx<np.array([96,80])),axis=1);flat=idx[inside,0]*80+idx[inside,1];top=np.full(96*80,-np.inf,np.float32);np.maximum.at(top,flat,a[inside,2]);top=top.reshape(96,80);envelopes.append(top);env=top[4:92,4:76];env=env[np.isfinite(env)]
  row={'frame':frame,'vertices':len(vv),'triangles':len(ff),'mesh_volume_m3':volume,'boundary_edges':int((counts==1).sum()),'nonmanifold_edges':int((counts!=2).sum()),'height_samples':len(z),'height_missing_or_steep':int((~valid).sum()),'mesh_median_head_m':float(np.median(z[valid])),'median_error_from_original_head_m':float(np.median(z[valid]-HEAD)),'mesh_p95_abs_head_error_m':float(np.quantile(abs(z[valid]-HEAD),.95)),'mesh_minmax_head_m':[float(np.min(z[valid])),float(np.max(z[valid]))],
   'FLIP_count':len(ps.particles),'particle_systems':[{'type':p.settings.type,'count':len(p.particles)} for p in ev.particle_systems],'FLIP_world_bounds_m':[[float(a[:,k].min()),float(a[:,k].max())] for k in range(3)],'FLIP_top_envelope_interior_columns':len(env),'FLIP_top_envelope_median_m':float(np.median(env)),'FLIP_top_envelope_p05_p95_m':np.quantile(env,[.05,.95]).tolist(),'FLIP_z_quantiles_m':np.quantile(a[:,2],[0,.25,.5,.75,1]).tolist(),'FLIP_outside_domain_points':int(np.any((a<mins-1e-5)|(a>maxs+1e-5),axis=1).sum())}
  frames.append(row);heights.append(z);print('REALBED24_FRAME',json.dumps(row),flush=True);ev.to_mesh_clear()
 v1=frames[0]['mesh_volume_m3'];a=np.asarray(heights);delta=a-a[0];vd=max(abs(f['mesh_volume_m3']/v1-1) for f in frames);hd=max(abs(f['mesh_median_head_m']-frames[0]['mesh_median_head_m']) for f in frames);p95=max(float(np.quantile(abs(row),.95)) for row in delta);ed=max(abs(f['FLIP_top_envelope_median_m']-frames[0]['FLIP_top_envelope_median_m']) for f in frames)
 h_abs=max(abs(f['median_error_from_original_head_m']) for f in frames[4:]);p_abs=max(f['mesh_p95_abs_head_error_m'] for f in frames[4:]);passed=vd<=.03 and h_abs<=.025 and p_abs<=.05 and ed<=.025 and all(f['height_missing_or_steep']==0 and f['boundary_edges']==f['nonmanifold_edges']==0 for f in frames)
 r['frames']=frames;r['check_summary']={'initial_geometric_volume_m3':r['source_state']['objects'][INIT]['topology']['signed_volume_m3'],'frame1_mesh_volume_m3':v1,'frame1_relative_initial_volume_error':v1/r['source_state']['objects'][INIT]['topology']['signed_volume_m3']-1,'max_relative_volume_drift_from_f1':vd,'max_median_dynamic_height_drift_m':hd,'max_p95_dynamic_height_drift_m':p95,'max_particle_envelope_median_drift_m':ed,'max_frame5_24_median_error_from_original_head_m':h_abs,'max_frame5_24_p95_error_from_original_head_m':p_abs,'particle_envelope_is_geometry_proxy_not_conserved_mass':True}
 import openvdb
 audits=[]
 for frame in (1,12,24):
  path=str(CACHE/'data'/f'fluid_data_{frame:04}.vdb');meta=openvdb.readAllGridMetadata(path);names=[g.name for g in meta];sample={'frame':frame,'grids':[{'name':g.name,'type':g.valueTypeName} for g in meta],'pressure_available':'pressure' in names}
  arrays={}
  for name,dtype in [('phi',np.float32),('phi_obstacle',np.float32),('flags',np.int32)]:
   if name not in names:continue
   g=openvdb.read(path,name);aa=np.empty((96,80,41),dtype);g.copyToArray(aa,(0,0,0));arrays[name]=aa;sample[name]={'active_bbox':g.evalActiveVoxelBoundingBox(),'background':g.background,'min':float(aa.min()),'max':float(aa.max())}
   if name=='flags':values,cnt=np.unique(aa,return_counts=True);sample[name]['value_counts']={str(v):int(n) for v,n in zip(values,cnt)}
   else:sample[name]['negative_cell_count']=int((aa<0).sum())
  if 'phi' in arrays:
   mask=arrays['phi']<0;sample['negative_phi_volume_proxy_m3']=int(mask.sum())*.025**3
   if 'phi_obstacle' in arrays:sample['negative_phi_and_nonnegative_obstacle_volume_proxy_m3']=int((mask&(arrays['phi_obstacle']>=0)).sum())*.025**3
  sample['grid_volume_limit']='Cell-center sign count over96x80x41 box; no subcell integration; original phi/obstacle signs are reported, not claimed exact conserved mass'
  audits.append(sample)
 r['vdb_state_audits']=audits;r['source_cache_untouched_after_run']=manifest()==r['original_cache_manifest'];assert r['source_cache_untouched_after_run'];r['source_sha256_after']=sha(SOURCE);assert r['source_sha256_after']==SOURCE_SHA
 r['status']='REAL_BED_DEFAULT_PRIMARY_STATIC_PASS_NOT_SINGLE_CAUSE_OR_VISUAL_PROOF' if passed else 'REAL_BED_DEFAULT_PRIMARY_STATIC_FAIL_NO_AUTO_REPEAT';r['checked_scene_sha256']=sha(PILOT);r['mesh_hashes']=[{'name':p.name,'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(CACHE.rglob('*.bobj.gz'))]
 np.savez_compressed(ROOT/'qa/water09-realbed24-control-heights.npz',xy=xy,height=a,FLIP_envelope=np.asarray(envelopes));write(r);print('REALBED24_CHECK_RESULT',r['status'],json.dumps(r['check_summary']),flush=True)
if __name__=='__main__':
 assert bpy.app.background
 action=sys.argv[sys.argv.index('--')+1];{'prepare':prepare,'bake':bake,'check':check}[action]()
