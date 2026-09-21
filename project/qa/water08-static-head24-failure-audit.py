"""Existing failed static cache diagnostics. No bake/render/save."""
import sys,json,hashlib
from pathlib import Path
import bpy,numpy as np,openvdb
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import hybrid_water as h
PILOT=ROOT/'scene/Fallingwater_water08_static_head24.blend';CACHE=ROOT/'caches/fluid_water08/static_head24'
bpy.ops.wm.open_mainfile(filepath=str(PILOT));scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=4
domain=scene.objects['WATER08_Static_Head_Control_Domain'];d=next(m.domain_settings for m in domain.modifiers if m.type=='FLUID')
init=scene.objects['WATER08_Complete_Connected_Initial_Pool'];flow=next(m.flow_settings for m in init.modifiers if m.type=='FLUID')
settings={}
for k in ['domain_type','resolution_max','time_scale','simulation_method','flip_ratio','use_fractions','fractions_distance','fractions_threshold','delete_in_obstacle','timesteps_min','timesteps_max','cfl_condition','particle_radius','particle_number','particle_min','particle_max','particle_randomness','particle_band_width','use_mesh','mesh_scale','mesh_particle_radius','mesh_smoothen_pos','mesh_smoothen_neg','use_collision_border_bottom','use_collision_border_top','use_collision_border_front','use_collision_border_back','use_collision_border_left','use_collision_border_right','use_viscosity','use_diffusion','cache_frame_start','cache_frame_end','use_foam_particles','use_spray_particles','use_bubble_particles','use_flip_particles','use_guiding','cache_directory','cache_frame_pause_particles']:
 if hasattr(d,k):settings[k]=getattr(d,k)
settings['actual_grid_resolution']=list(d.grid_resolution) if hasattr(d,'grid_resolution') else None
settings['scene_unit_scale_length']=scene.unit_settings.scale_length
colliders=list(d.effector_group.objects);trees={o.name:h.render_bvh(o) for o in colliders}
effects=[]
for o in colliders:
 for m in o.modifiers:
  if m.type=='FLUID' and m.fluid_type=='EFFECTOR':
   e=m.effector_settings;effects.append({'name':o.name,'world_geometry_sha256':h.shape_hash(o),'topology':h.topology(o),'settings':{k:getattr(e,k) for k in ['effector_type','use_effector','surface_distance','use_plane_init','subframes'] if hasattr(e,k)}})
r={'status':'READ_ONLY_EXISTING_FAILED_CONTROL_DIAGNOSIS','candidate_sha256':hashlib.sha256(PILOT.read_bytes()).hexdigest(),'saved_domain_settings':settings,'gravity_m_s2':list(scene.gravity),
 'flow':{k:(list(getattr(flow,k)) if k=='velocity_coord' else getattr(flow,k)) for k in ['flow_type','flow_behavior','use_inflow','use_initial_velocity','velocity_coord','velocity_normal','surface_distance','subframes','use_plane_init']},'effectors':effects,'frames':[],'velocity_grids':[]}
roi=json.loads((ROOT/'qa/water08-static-head24.json').read_text(encoding='utf-8'))['domain_aabb_m'];mins=np.array([a for a,b in roi]);maxs=np.array([b for a,b in roi]);dims=np.array([96,80,41])
for frame in range(1,25):
 scene.frame_set(frame);bpy.context.view_layer.update();ev=domain.evaluated_get(bpy.context.evaluated_depsgraph_get())
 row={'frame':frame,'particle_systems':[{'type':ps.settings.type,'count':len(ps.particles)} for ps in ev.particle_systems]}
 if frame in (1,12,24):
  ps=next(ps for ps in ev.particle_systems if ps.settings.type=='FLIP');aa=np.empty(len(ps.particles)*3,np.float32);ps.particles.foreach_get('location',aa);a=aa.reshape(-1,3)
  rows={'world_bounds_m':[[float(a[:,k].min()),float(a[:,k].max())] for k in range(3)],'z_quantiles_m':np.quantile(a[:,2],[0,.05,.25,.5,.75,.95,1]).tolist(),'outside_domain_points':int(np.any((a<mins-1e-5)|(a>maxs+1e-5),axis=1).sum())}
  indices=np.floor((a-mins)/.025).astype(np.int32);valid=np.all((indices>=0)&(indices<dims),axis=1);ids=np.ravel_multi_index(indices[valid].T,dims);uid,counts=np.unique(ids,return_counts=True)
  rows['occupied_2p5cm_cells']=len(uid);rows['cell_occupancy_proxy_volume_m3']=len(uid)*.025**3;rows['points_per_occupied_cell_quantiles']=np.quantile(counts,[0,.25,.5,.75,.95,1]).tolist()
  # Observe the actual particle free-surface envelope, independent of generated surface mesh.
  xyindex=indices[valid,0]*dims[1]+indices[valid,1];top=np.full(dims[0]*dims[1],-np.inf,np.float32);np.maximum.at(top,xyindex,a[valid,2]);finite=top[np.isfinite(top)]
  rows['per_column_particle_top_quantiles_m']=np.quantile(finite,[.05,.25,.5,.75,.95]).tolist()
  # Fixed-stride point sample tests whether particles are visibly entering unchanged solids.
  sample=a[np.linspace(0,len(a)-1,min(800,len(a)),dtype=int)];inside={};near={}
  for name,tree in trees.items():
   depths=[];nears=0
   for p in sample:
    q=Vector(p);hit=tree.find_nearest(q)
    if hit[3]<.001:nears+=1
    elif (q-hit[0]).dot(hit[1])<0 and all(x%2 for x in h.parity(tree,q)):depths.append(hit[3])
   inside[name]=h.stats(depths);near[name]=nears
  rows['particle_inside_exact_solid_sample']={'sample_count':len(sample),'inside_depths_m':inside,'within1mm_surface_counts':near,'sampling_limit':'Fixed stride800 points; not all particles or all triangle interiors'}
  row['particle_geometry']=rows
 r['frames'].append(row);print('STATIC_FAILURE_PARTICLES',json.dumps(row),flush=True)
for frame in (1,12,24):
 filename=str(CACHE/'data'/f'fluid_data_{frame:04}.vdb');metadata=openvdb.readAllGridMetadata(filename)
 g=openvdb.read(filename,'velocity');lo,hi=g.evalActiveVoxelBoundingBox();shape=tuple(hi[k]-lo[k]+1 for k in range(3))+(3,);aa=np.empty(shape,np.float32);g.copyToArray(aa,lo)
 q={'frame':frame,'available_grids':[{'name':m.name,'type':m.valueTypeName} for m in metadata],'velocity_active_voxel_bbox':[lo,hi],
  'transform_index0_world':g.transform.indexToWorld((0,0,0)),'transform_index111_world':g.transform.indexToWorld((1,1,1)),
  'raw_velocity_units':'Stored grid velocity units not independently converted to world m/s here','raw_vector_component_min':aa.reshape(-1,3).min(0).tolist(),'raw_vector_component_max':aa.reshape(-1,3).max(0).tolist(),
  'raw_component_median':np.median(aa.reshape(-1,3),axis=0).tolist(),'nonzero_vectors':int((np.linalg.norm(aa,axis=-1)>1e-8).sum())}
 # Sample velocity in grid cells known to be well inside the wet pool (away from all edges).
 vals=[]
 for x in range(20,76):
  for y in range(16,64):
   for z in range(10,18):
    idx=np.array([x,y,z])-np.array(lo)
    if np.all(idx>=0) and np.all(idx<aa.shape[:3]):vals.append(aa[tuple(idx)])
 vals=np.asarray(vals);q['interior_raw_velocity_mean']=vals.mean(0).tolist();q['interior_raw_vertical_quantiles']=np.quantile(vals[:,2],[0,.05,.5,.95,1]).tolist()
 r['velocity_grids'].append(q);print('STATIC_FAILURE_VELOCITY',json.dumps(q),flush=True)
r['interpretation_limits']=['FLIP particle count changes with reseeding/narrow-band behavior and is not conserved mass','Point occupancy/top envelope is a particle-based geometry proxy, not solver level-set integral','Cache is non-resumable and includes particles+velocity only; phi/pressure/flags/obstacle grids unavailable','Generic OpenVDB readAll failed on custom int32_trnc point attribute; read named velocity grid succeeded without changing cache','No step-level CFL/substep execution telemetry exists; only configured limits are verified']
h.write(ROOT/'qa/water08-static-head24-failure-audit.json',r)
print('STATIC_FAILURE_AUDIT_DONE',flush=True)
