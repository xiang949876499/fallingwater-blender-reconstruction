"""One authorized water09 native impact diagnostic. Fresh background, never production."""
import sys,json,hashlib,time,math
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import hybrid_water as h
SOURCE=ROOT/'scene/Fallingwater_water09_real_bed_default24.blend';SOURCE_SHA='9a227354cea628f1d310283d558530105780a247fd93825466a9a3262687dc6f'
JETFILE=ROOT/'scene/Fallingwater_hybrid07_impact36.blend';JET_SHA='7093200e28e1c135e559ccc8605fad04e14de7cf92399baef3151f5523f7537e'
PILOT=ROOT/'scene/Fallingwater_water09_impact36.blend';CACHE=ROOT/'caches/fluid_water09/impact36';REPORT=ROOT/'qa/water09-impact36.json'
DOMAIN='WATER08_Static_Head_Control_Domain';INIT='WATER08_Complete_Connected_Initial_Pool';JET='HYBRID07_Branch_Exact_Source';HEAD=-5.771274
ROI=[[-.4026584744,1.9973415256],[-3.2114176750,-1.2114176750],[-6.56,-5.05]]
CONTROL=json.loads((ROOT/'qa/water09-realbed24-control.json').read_text(encoding='utf-8'))
KEYS=list(CONTROL['post_bake_assertions']['actual_domain'])
EXTRA=['sndparticle_sampling_wavecrest','sndparticle_sampling_trappedair','sndparticle_life_min','sndparticle_life_max','sndparticle_combined_export','sndparticle_boundary']
SECONDARY_TARGET={'sndparticle_sampling_wavecrest':8,'sndparticle_sampling_trappedair':8,'sndparticle_life_min':.25,'sndparticle_life_max':1.2}
FLOWKEYS=['flow_type','flow_behavior','flow_source','use_initial_velocity','velocity_factor','velocity_coord','velocity_normal','velocity_random','surface_distance','subframes','use_inflow','use_plane_init','use_texture']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(r):REPORT.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
def manifest():
 bases=['fluid_water08/static_head24','fluid_water09/real_bed_default24','fluid_hybrid07/impact36']
 return [{'path':str(p.relative_to(ROOT/'caches')),'bytes':p.stat().st_size,'sha256':sha(p)} for name in bases for p in sorted((ROOT/'caches'/name).rglob('*')) if p.is_file()]
def flow(o):
 f=next(m.flow_settings for m in o.modifiers if m.type=='FLUID');return {k:(list(getattr(f,k)) if k=='velocity_coord' else getattr(f,k)) for k in FLOWKEYS}
def get():
 s=bpy.context.scene;o=s.objects[DOMAIN];d=next(m.domain_settings for m in o.modifiers if m.type=='FLUID');return s,o,d
def raw_aabb(o):
 a=np.array([tuple(o.matrix_world@v.co) for v in o.data.vertices]);return np.stack((a.min(0),a.max(0)),1).tolist()
def validate(r):
 s,o,d=get();assert sha(SOURCE)==SOURCE_SHA and sha(JETFILE)==JET_SHA
 assert np.max(abs(np.array(raw_aabb(o))-np.array(ROI)))<2e-6
 assert len(s.objects)==5 and list(o.scale)==[1,1,1] and not o.animation_data
 for name,signature in r['preserved_objects'].items():assert h.shape_hash(s.objects[name])==signature,name
 assert h.shape_hash(s.objects[JET])==r['jet_world_geometry_sha256']
 assert flow(s.objects[INIT])==r['initial_flow'] and flow(s.objects[JET])==r['jet_flow']
 diffs=[]
 for key in KEYS+EXTRA:
  value=getattr(d,key);before=r['base_settings'][key]
  target=SECONDARY_TARGET.get(key,8 if key=='timesteps_max' else True if key in ('use_foam_particles','use_spray_particles') else before)
  equal=abs(value-target)<1e-6 if isinstance(value,float) else value==target
  assert equal,(key,value,target)
  if value!=before:diffs.append({'property':key,'before':before,'after':value})
 systems=sorted(p.settings.type for p in o.particle_systems);assert systems==['FLIP','FOAM','SPRAY'],systems
 assert Path(bpy.path.abspath(d.cache_directory)).resolve()==CACHE.resolve() and d.cache_resumable and d.cache_type=='ALL'
 assert d.cache_frame_start==1 and d.cache_frame_end==36 and s.render.fps==24 and d.resolution_max==96
 assert set(x.name for x in d.fluid_group.objects)=={INIT,JET}
 assert s.gravity.z<-9.8099 and s.unit_settings.scale_length==1
 return {'passed':True,'settings_differences':diffs,'all_settings':{k:getattr(d,k) for k in KEYS+EXTRA},'particle_systems':systems,'domain_raw_aabb':raw_aabb(o),'fluid_sources':list(d.fluid_group.objects.keys()),'jet_actual_flow':flow(s.objects[JET]),'preserved_geometry_verified':True}
def prepare():
 assert not PILOT.exists() and not CACHE.exists(),'Single candidate only; inspect failures instead of replacing'
 assert sha(SOURCE)==SOURCE_SHA and sha(JETFILE)==JET_SHA
 old=manifest();bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s,o,d=get()
 before={k:getattr(d,k) for k in KEYS+EXTRA};preserved={x.name:h.shape_hash(x) for x in s.objects if x!=o};initial_flow=flow(s.objects[INIT])
 # Change cache path before triggering any parameter callback. Existing caches stay immutable.
 CACHE.mkdir(parents=True);d.cache_directory=str(CACHE);s.frame_set(1)
 with bpy.data.libraries.load(str(JETFILE),link=False) as (src,dst):
  assert JET in src.objects;dst.objects=[JET]
 jet=dst.objects[0];d.fluid_group.objects.link(jet);bpy.context.view_layer.update()
 expected=json.loads((ROOT/'qa/water-hybrid07-impact36.json').read_text(encoding='utf-8'))['source_encoding']
 verts=np.array([tuple(jet.matrix_world@v.co) for v in jet.data.vertices]);assert np.max(abs(verts-np.array(expected['vertices'])))<1e-6
 assert np.max(abs(np.array(flow(jet)['velocity_coord'])-np.array(expected['velocity_world_m_s'])))<1e-6
 assert h.topology(jet)['nonmanifold_edges']==0 and flow(jet)['flow_behavior']=='INFLOW'
 inverse=o.matrix_world.inverted()
 for v in o.data.vertices:
  p=o.matrix_world@v.co
  if p.z>-6:p.z=-5.05
  v.co=inverse@p
 o.data.update();bpy.context.view_layer.update()
 assert np.all(verts>np.array([p[0] for p in ROI])+.025) and np.all(verts<np.array([p[1] for p in ROI])-.025)
 jet_tree=h.render_bvh(jet);contacts=[]
 for rock in d.effector_group.objects:
  tree=h.render_bvh(rock);pairs=jet_tree.overlap(tree);near=[tree.find_nearest(Vector(v))[3] for v in verts]
  contacts.append({'object':rock.name,'geometry_world_sha256':h.shape_hash(rock),'triangle_overlap_pairs':len(pairs),'source_vertex_min_clearance_m':min(near)})
  assert not pairs and min(near)>.025
 d.timesteps_max=8;switches=[]
 for key,target in [('use_foam_particles',True),('use_spray_particles',True),('use_bubble_particles',False),('use_tracer_particles',False)]:
  prev=bool(getattr(d,key))
  if prev!=target:setattr(d,key,target)
  switches.append({'key':key,'before':prev,'assigned':prev!=target,'after':bool(getattr(d,key))});assert bool(getattr(d,key))==target
 # Keep fresh reproduction aligned with the approved secondary budget, not inherited defaults.
 for key,target in SECONDARY_TARGET.items():
  if getattr(d,key)!=target:setattr(d,key,target)
 d.cache_frame_end=36;s.frame_end=36;s.frame_start=1;s.render.threads_mode='FIXED';s.render.threads=8
 s['water09_status']='IMPACT36_CLOSED_SIDE_DIAGNOSTIC_NOT_PRODUCTION';bpy.context.view_layer.update()
 r={'status':'PREPARED_REOPEN_ASSERT_REQUIRED','source':str(SOURCE),'source_sha256':SOURCE_SHA,'jet_source':str(JETFILE),'jet_source_sha256':JET_SHA,'preserved_cache_manifest':old,'base_settings':before,'preserved_objects':preserved,'initial_flow':initial_flow,'jet_flow':flow(jet),'jet_world_geometry_sha256':h.shape_hash(jet),'jet_source_geometry':h.topology(jet),'jet_source_aabb_m':raw_aabb(jet),'jet_contact_checks':contacts,'source_report_velocity_and_vertices_match':True,'secondary_setter':switches,'domain_aabb_m':ROI,'domain_cell_m':.025,'estimated_grid':[96,80,61],'frame_range':[1,36],'fps':24,'threads':8,'nominal_Q_m3_s':expected['modeled_flow_m3_s'],'head_initial_m':HEAD,'initial_pool_volume_m3':3.2648255419114713,'boundary':'Artificial closed sides and bottom; top open. Not a constant-head or natural-river boundary','hard_stop_seconds':360,'production_install':False,'renders':0,'no_automatic_extension':True}
 r['pre_save_assertions']=validate(r);assert manifest()==old;r['old_caches_unchanged_after_prepare']=True
 bpy.ops.wm.save_as_mainfile(filepath=str(PILOT));r['prepared_sha256']=sha(PILOT);write(r);print('IMPACT09_PREPARED',json.dumps(r['pre_save_assertions']),flush=True)
def bake():
 r=json.loads(REPORT.read_text(encoding='utf-8'));assert r['status']=='PREPARED_REOPEN_ASSERT_REQUIRED';assert sha(PILOT)==r['prepared_sha256'];assert not list(CACHE.rglob('*.bobj.gz'))
 bpy.ops.wm.open_mainfile(filepath=str(PILOT));s,o,d=get();s.render.threads_mode='FIXED';s.render.threads=8;r['reopened_assertions']=validate(r);r['status']='REOPEN_ASSERT_PASS_BAKING_ONCE';write(r);print('IMPACT09_REOPEN_ASSERT_PASS',flush=True)
 for ob in bpy.context.selected_objects:ob.select_set(False)
 o.select_set(True);bpy.context.view_layer.objects.active=o;t=time.perf_counter();done=bpy.ops.fluid.bake_all();r['bake_seconds']=time.perf_counter()-t;r['bake_result']=list(done)
 s.frame_set(36);bpy.ops.wm.save_as_mainfile(filepath=str(PILOT));files=[p for p in CACHE.rglob('*') if p.is_file()];r['cache_files']=len(files);r['cache_bytes']=sum(p.stat().st_size for p in files);r['baked_sha256']=sha(PILOT);r['status']='BAKED36_RAW_CHECK_PENDING';write(r);print('IMPACT09_BAKED',r['bake_seconds'],r['cache_bytes'],flush=True)
def align_secondary():
 r=json.loads(REPORT.read_text(encoding='utf-8'));assert r['status']=='PREPARED_REOPEN_ASSERT_REQUIRED' and not list(CACHE.rglob('*.bobj.gz'))
 assert sha(PILOT)==r['prepared_sha256'];prior=ROOT/'qa/water09-impact36-prepare-secondary-mismatch.json';assert not prior.exists();prior.write_bytes(REPORT.read_bytes())
 bpy.ops.wm.open_mainfile(filepath=str(PILOT));s,o,d=get();changes=[]
 for key,target in SECONDARY_TARGET.items():
  before=getattr(d,key)
  if before!=target:setattr(d,key,target)
  changes.append({'property':key,'before':before,'after':getattr(d,key)})
 r['secondary_plan_alignment']={'prior_prepared_sha256':r['prepared_sha256'],'preserved_prior_report':str(prior),'changes':changes,'reason':'Saved stable09 inherits factory200/40 sampling and10-25s life; align to explicitly proposed8/8 and.25-1.2s before any bake','bakes_before_alignment':0}
 r['pre_save_assertions']=validate(r);assert manifest()==r['preserved_cache_manifest'];bpy.ops.wm.save_as_mainfile(filepath=str(PILOT));r['prepared_sha256']=sha(PILOT);write(r);print('IMPACT09_SECONDARY_ALIGNED',json.dumps(changes),flush=True)
if __name__=='__main__':
 assert bpy.app.background
 action=sys.argv[sys.argv.index('--')+1];{'prepare':prepare,'align_secondary':align_secondary,'bake':bake}[action]()
