"""Prepare/check the two approved source controls. No bake/render entry point."""
import sys,json,hashlib,time,importlib.util,math
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

P=Path(__file__).resolve().parent;ROOT=P.parent
spec=importlib.util.spec_from_file_location('water10_helpers',P/'water10-natural48.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
REPORT=P/'water11-source-prepare.json';DOMAIN='WATER11_Source_Domain';JET='WATER11_Exact_Frozen_Inflow'
PREPARED=ROOT/'scene/Fallingwater_water10_natural48.blend'
EXPECTED_SHA='00f0ae9a85655f0f64bc68cbe539fd04fc89024af920c610ee4a021d5adcdbdc'
MAPPING=json.loads((P/'water10-native-mapping.json').read_text(encoding='utf8'))
CELL=float(MAPPING['cell_m']);LO=np.array(MAPPING['solver_origin_world_m'])+CELL*np.array([210,186,21]);HI=LO+CELL*np.array([24,24,19])
SECONDARY=w.SECONDARY
KEYS=list(dict.fromkeys(w.KEYS+['particle_number','particle_min','particle_max','particle_randomness','particle_radius','particle_band_width','mesh_generator','mesh_smoothen_pos','mesh_smoothen_neg','domain_type']))

def dump(path,value):
 Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2,default=lambda v:v.item() if isinstance(v,np.generic) else v.tolist()),encoding='utf8')

def state(d):return {k:getattr(d,k) for k in KEYS}

def preserved_manifest():
 old=w.manifest();old=[dict(r,path=str(ROOT/'caches'/r['path'])) for r in old]
 old += [{'path':str(p),'bytes':p.stat().st_size,'sha256':w.sha(p)} for p in sorted((ROOT/'caches/fluid_water10/natural48').rglob('*')) if p.is_file()]
 return old

def geometry(obj):
 return np.array([tuple(obj.matrix_world@p.co) for p in obj.data.vertices]),[list(p.vertices) for p in obj.data.polygons]

def triangles(v,f):
 temp=w.mesh('WATER11_TEMP_GEOMETRY',v,f);vv,ff=w.arrays(temp);bpy.data.objects.remove(temp,do_unlink=True);return vv,ff

def arm_paths(arm):
 return ROOT/f'scene/Fallingwater_water11_source_{arm}.blend',ROOT/f'caches/fluid_water11/source_{arm}'

def validate(a):
 s=bpy.context.scene;obj=s.objects[DOMAIN];d=next(m.domain_settings for m in obj.modifiers if m.type=='FLUID')
 actual=state(d)
 for k,expected in a['actual_domain'].items():
  value=actual[k];assert abs(value-expected)<1e-6 if isinstance(value,float) else value==expected,(k,value,expected)
 assert np.max(abs(np.array(w.bounds(obj))-np.stack((LO,HI),1)))<2e-6
 assert s.render.threads==4 and s.render.fps==24 and s.frame_start==1 and s.frame_end==12
 assert s.use_gravity and abs(s.gravity.z+9.81)<1e-5 and s.unit_settings.scale_length==1
 assert d.fluid_group and set(d.fluid_group.objects.keys())=={JET}
 assert d.effector_group and set(d.effector_group.objects.keys())==set(a['collider_geometry_hashes'])
 for name,expected in {JET:a['source_geometry_sha256'],**a['collider_geometry_hashes']}.items():assert w.h.shape_hash(s.objects[name])==expected,name
 assert w.flow_state(s.objects[JET])==a['source_flow']
 assert all(not getattr(d,k) for k in SECONDARY)
 systems=[p.settings.type for p in obj.particle_systems];assert systems==['FLIP'],systems
 assert Path(bpy.path.abspath(d.cache_directory)).resolve()==Path(a['cache']).resolve()
 for coll in d.effector_group.objects:
  e=next(m.effector_settings for m in coll.modifiers if m.type=='FLUID')
  assert e.use_effector and e.effector_type=='COLLISION' and not e.use_plane_init and abs(e.surface_distance-.001)<1e-8
 return {'passed':True,'actual_domain':actual,'particle_systems':systems,'actual_source_flow':w.flow_state(s.objects[JET]),
   'geometry_hashes_verified':len(a['collider_geometry_hashes'])+1,'raw_domain_aabb_m':w.bounds(obj),
   'RNA_domain_resolution_before_bake':list(d.domain_resolution),'expected_grid_until_cache_exists':a['expected_grid'],
   'solver_grid_actual_observed':False,'no_cache_data_yet':not any(p.is_file() for p in Path(a['cache']).rglob('*'))}

def prepare():
 assert not REPORT.exists(),'Do not overwrite prepared controls'
 for arm in ['S24','S48']:
  scene,cache=arm_paths(arm);assert not scene.exists() and not cache.exists(),(scene,cache)
 assert w.sha(PREPARED)==EXPECTED_SHA and w.sha(w.SOURCE)==w.CONFIG['source_sha256']
 bpy.ops.wm.open_mainfile(filepath=str(PREPARED));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.frame_set(1)
 source=s.objects[w.JET];sv,sf=geometry(source);source_hash=w.h.shape_hash(source);source_flow=w.flow_state(source)
 original_domain=next(m.domain_settings for m in s.objects[w.DOMAIN].modifiers if m.type=='FLUID');base=state(original_domain)
 retained=[];rejected=[]
 for obj in original_domain.effector_group.objects:
  v,f=geometry(obj);box=np.stack((v.min(0),v.max(0)),1);hit=np.all(box[:,1]>=LO-.3) and np.all(box[:,0]<=HI+.3)
  record={'name':obj.name,'original_hash':w.h.shape_hash(obj),'aabb_m':box.tolist()}
  if hit:retained.append((record,v,f))
  else:rejected.append(record)
 assert np.max(abs(sv-np.array(json.loads((P/'water10-domain-source-probe.json').read_text(encoding='utf8'))['world_vertices'])))<1e-6
 manifests=preserved_manifest();dump(P/'water11-source-preserved-cache-manifest.json',manifests)
 r={'status':'PREPARING_TWO_SOURCE_CONTROLS_NO_BAKE','source_prepared_scene':str(PREPARED),'source_prepared_sha256':EXPECTED_SHA,
  'full_scene_sha256':w.CONFIG['source_sha256'],'frozen_core_sha256':w.CONFIG['frozen_core_sha256'],
  'source_hash':source_hash,'retained_collider_records':[q[0] for q in retained],'outside_local_collar_records':rejected,
  'old_cache_files':len(manifests),'old_cache_bytes':sum(q['bytes'] for q in manifests),'arms':{},'new_bakes':0,'new_renders':0,'production_changed':False,
  'first_frame_measurement_required':'Author mesh sections, phi area, native mesh section, velocity/Q at frame1 and all12. f1 is first solved frame, not true initialization t0.'}
 dump(REPORT,r)
 for arm,res in [('S24',24),('S48',48)]:
  started=time.perf_counter();bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
  flows=bpy.data.collections.new('WATER11_Exact_Flow_Group');s.collection.children.link(flows)
  colliders=bpy.data.collections.new('WATER11_Actual_Neighbor_Rocks');s.collection.children.link(colliders)
  src=w.mesh(JET,sv,sf,flows);w.flow(src,'INFLOW',source_flow['velocity_coord']);src.hide_render=True
  assert w.h.shape_hash(src)==source_hash
  src_tree=w.h.render_bvh(src);sample=np.vstack([sv,sv[np.array([p for p in sf if len(p)==3])].mean(1)])
  rings=sv.reshape(9,40,3);last=rings[-1];vel=np.array(source_flow['velocity_coord']);flight=[]
  for t in np.linspace(0,.09,19):
   vv=last+vel*t+np.array([0,0,-.5*9.81*t*t]);flight.extend(vv[np.all((vv>=LO+.02)&(vv<=HI-.02),axis=1)])
  flight=np.array(flight);assert len(flight)>100
  checks=[];hashes={}
  for record,v,f in retained:
   obj=w.mesh(record['name'],v,f,colliders);assert w.h.shape_hash(obj)==record['original_hash'];hashes[obj.name]=record['original_hash']
   obj.hide_render=True;obj.display_type='WIRE';m=obj.modifiers.new('Actual frozen collision','FLUID');m.fluid_type='EFFECTOR';e=m.effector_settings;e.effector_type='COLLISION';e.surface_distance=.001;e.use_plane_init=False
   tree=w.h.render_bvh(obj);overlaps=src_tree.overlap(tree)
   distance=min(tree.find_nearest(Vector(p))[3] for p in sample);flight_distance=min(tree.find_nearest(Vector(p))[3] for p in flight)
   inside_src=sum(any(n%2 for n in w.h.parity(tree,Vector(p))) for p in sample[::8]);inside_flight=sum(any(n%2 for n in w.h.parity(tree,Vector(p))) for p in flight[::4])
   checks.append({'name':obj.name,'source_triangle_overlaps':len(overlaps),'source_sample_min_clearance_m':distance,'flight_sample_min_clearance_m':flight_distance,'source_inside_samples':inside_src,'flight_inside_samples':inside_flight,'topology':w.h.topology(obj)})
   assert not overlaps and inside_src==inside_flight==0 and flight_distance>.03,checks[-1]
  domain=w.cube(DOMAIN,LO,HI);m=domain.modifiers.new('Independent source control','FLUID');m.fluid_type='DOMAIN';d=m.domain_settings;d.domain_type='LIQUID'
  scene,cache=arm_paths(arm);cache.mkdir(parents=True)
  target=dict(base);target.update(resolution_max=res,cache_frame_start=1,cache_frame_end=12)
  for k in SECONDARY:target[k]=False
  for side in ['left','right','front','back','top','bottom']:target['use_collision_border_'+side]=False
  setters=[]
  for key,value in target.items():
   before=getattr(d,key)
   if before!=value:setattr(d,key,value)
   if key in SECONDARY:setters.append({'key':key,'before':before,'assigned':before!=value,'after':getattr(d,key)})
  d.cache_directory=str(cache);d.fluid_group=flows;d.effector_group=colliders
  s.frame_start=1;s.frame_end=12;s.render.fps=24;s.render.threads_mode='FIXED';s.render.threads=4;s.use_gravity=True;s.gravity=(0,0,-9.81);s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.frame_set(1);bpy.context.view_layer.update()
  a={'scene':str(scene),'cache':str(cache),'resolution':res,'expected_grid':[res,res,19*(res//24)],'cell_m':CELL*24/res,
   'domain_aabb_m':np.stack((LO,HI),1).tolist(),'domain_source_lattice_phase':'Original water10 lower grid corner+[210,186,21]coarse cells',
   'actual_domain':state(d),'source_flow':w.flow_state(src),'source_geometry_sha256':source_hash,'source_topology':w.h.topology(src),
   'source_world_vertices':sv.tolist(),'source_polygons':sf,'collider_geometry_hashes':hashes,'collision_checks':checks,
   'ballistic_flight_samples':len(flight),'flight_test_scope':'Discrete source-end ring advection through local domain; no future liquid trajectory claimed',
   'source_width_cells':.24/(CELL*24/res),'source_thickness_cells':.23/(CELL*24/res),
   'secondary_idempotent_setters':setters,'frames':[1,12],'fps':24,'threads':4,'hard_stop_seconds':90,'new_cache_files':0}
  a['before_save_checks']=validate(a);s['water11_status']='SOURCE_CONTROL_PREPARED_NOT_BAKED_NOT_PRODUCTION'
  bpy.ops.wm.save_as_mainfile(filepath=str(scene));a['scene_sha256']=w.sha(scene);a['prepare_seconds']=time.perf_counter()-started
  r['arms'][arm]=a;dump(REPORT,r);print('WATER11_SOURCE_PREPARED',arm,len(retained),a['prepare_seconds'],flush=True)
 assert preserved_manifest()==manifests
 r['old_caches_unchanged']=True;r['status']='PREPARED_FRESH_PROCESS_REOPEN_REQUIRED_NO_BAKE';dump(REPORT,r)

def reopen(arm):
 r=json.loads(REPORT.read_text(encoding='utf8'));a=r['arms'][arm];assert w.sha(Path(a['scene']))==a['scene_sha256']
 bpy.ops.wm.open_mainfile(filepath=a['scene']);a['fresh_process_reopen_checks']=validate(a)
 assert not any(p.is_file() for p in Path(a['cache']).rglob('*'))
 r['arms'][arm]=a;r['status']='PREPARED_TWO_ARMS_REOPEN_PASS_NO_BAKE' if all('fresh_process_reopen_checks' in q for q in r['arms'].values()) else 'PREPARED_OTHER_ARM_REOPEN_REQUIRED_NO_BAKE'
 dump(REPORT,r);print('WATER11_REOPEN_PASS',arm,flush=True)

if __name__=='__main__':
 assert bpy.app.background
 args=sys.argv[sys.argv.index('--')+1:]
 if args==['prepare']:prepare()
 elif len(args)==2 and args[0]=='reopen' and args[1] in ['S24','S48']:reopen(args[1])
 else:raise ValueError('Only prepare or reopen S24/S48; no bake or render in this file')
