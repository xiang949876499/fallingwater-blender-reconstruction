"""Post-supervisor read-only native source audit. Never bake, render or save a scene."""
import sys,json,gzip,struct,math,hashlib
from pathlib import Path
import bpy,numpy as np,openvdb
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;ROOT=P.parent;PLANES=[-5.35,-5.58,-5.64,-5.68]

def dump(path,value):
 Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2,default=lambda v:v.item() if isinstance(v,np.generic) else v.tolist()),encoding='utf8')

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  while b:=f.read(8*1024*1024):h.update(b)
 return h.hexdigest()

def config(path):
 raw=gzip.decompress(Path(path).read_bytes());assert len(raw)==204 and raw[-4:]==b'C01\0'
 return {'res':list(struct.unpack_from('<3i',raw,4)),'dx':struct.unpack_from('<f',raw,16)[0],
  'last_dt':struct.unpack_from('<f',raw,20)[0],'T':struct.unpack_from('<f',raw,196)[0]}

def rawmesh(path):
 raw=gzip.decompress(Path(path).read_bytes());n=struct.unpack_from('<i',raw,0)[0];v=np.frombuffer(raw,'<f4',count=n*3,offset=4).reshape(-1,3).astype(float)
 offset=4+12*n;nn=struct.unpack_from('<i',raw,offset)[0];offset+=4+12*nn;nf=struct.unpack_from('<i',raw,offset)[0];offset+=4
 f=np.frombuffer(raw,'<i4',count=nf*3,offset=offset).reshape(-1,3).copy();assert offset+nf*12==len(raw);return v,f

def section(v,f,z):
 if not len(f):return {'area_m2':None,'segments':0,'bad_degree_vertices':0,'status':'NO_MESH'}
 t=v[f];mask=(t[:,:,2].min(1)<z)&(t[:,:,2].max(1)>z);signed=0.;segments=[];degree={};tiny=0
 # Use original mesh-edge identity, not rounded coordinates: nearby but distinct
 # intersections must remain distinct even when a segment is sub-micrometre.
 for ids in f[mask]:
  tri=v[ids];pp=[];keys=[]
  for ia,ib in zip(ids,np.roll(ids,-1)):
   a,b=v[ia],v[ib]
   if (a[2]-z)*(b[2]-z)<0:
    pp.append(a+(b-a)*(z-a[2])/(b[2]-a[2]));keys.append(tuple(sorted((int(ia),int(ib)))))
  if len(pp)!=2:continue
  a,b=pp;normal=np.cross(tri[1]-tri[0],tri[2]-tri[0])
  if np.dot(b-a,np.cross(normal,[0,0,1]))<0:a,b=b,a
  signed+=a[0]*b[1]-a[1]*b[0];segments.append([a.tolist(),b.tolist()]);tiny+=int(np.linalg.norm(b-a)<1e-6)
  for key in keys:degree[key]=degree.get(key,0)+1
 bad=sum(x!=2 for x in degree.values())
 return {'area_m2':float(abs(signed)*.5) if not bad else None,'oriented_area_raw_m2':float(signed*.5),
  'segments':len(segments),'bad_degree_vertices':bad,'submicrometre_segments_retained':tiny,'connectivity_method':'original mesh-edge indices; no coordinate merging',
  'status':'CLOSED_SECTION' if segments and not bad else 'EMPTY' if not segments else 'OPEN_OR_PRECISION_AMBIGUOUS',
  'segment_coordinates_m':segments}

def interp(a,k,axis):
 low=math.floor(k);t=k-low;assert 0<=low and low+1<a.shape[axis],(k,axis,a.shape)
 return np.take(a,low,axis)*(1-t)+np.take(a,low+1,axis)*t

def plane(phi,velocity,origin,cell,scale,z):
 k=(z-origin[2])/cell;ph=interp(phi,k-.5,2);raw=-interp(velocity[:,:,:,2],k,2)
 sums={'full':[0.,0.,0.],'fixed_jet_window':[0.,0.,0.]};xx=origin[0]+(np.arange(ph.shape[0]-1)+.5)*cell;yy=origin[1]+(np.arange(ph.shape[1]-1)+.5)*cell
 for i in range(8):
  u=(i+.5)/8
  for j in range(8):
   v=(j+.5)/8
   def bil(a):return (1-u)*(1-v)*a[:-1,:-1]+u*(1-v)*a[1:,:-1]+(1-u)*v*a[:-1,1:]+u*v*a[1:,1:]
   wet=bil(ph)<0;vv=bil(raw);window=(xx[:,None]+u*cell>.3)&(xx[:,None]+u*cell<1.5)&(yy[None,:]+v*cell>-2.7)&(yy[None,:]+v*cell<-1.65)
   for name,mask in [('full',wet),('fixed_jet_window',wet&window)]:
    factor=cell**2/64;sums[name][0]+=int(mask.sum())*factor;sums[name][1]+=float(np.maximum(vv[mask],0).sum())*factor;sums[name][2]+=float(np.minimum(vv[mask],0).sum())*factor
 out={}
 for name,(area,pos,neg) in sums.items():
  out[name]={'phi_wet_area_m2':area,'raw_signed_MAC_area_integral':pos+neg,
   'Q_net_down_m3_s':(pos+neg)*scale if scale is not None else None,
   'Q_positive_down_m3_s':pos*scale if scale is not None else None,
   'Q_negative_down_m3_s':neg*scale if scale is not None else None,
   'wet_area_mean_down_velocity_m_s':(pos+neg)*scale/area if scale is not None and area>0 else None}
 return out

def array(path,name,res):
 g=openvdb.read(str(path),name);a=np.empty(tuple(res)+((3,) if name=='velocity' else ()),np.int32 if name=='flags' else np.float32);g.copyToArray(a,(0,0,0));return a

def topology(v,f):
 if not len(f):return {'status':'EMPTY_NOT_CLOSED_PASS','volume_m3':None}
 tri=(v-v.mean(0))[f];e=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);e.sort(1);_,n=np.unique(e,axis=0,return_counts=True)
 return {'vertices':len(v),'triangles':len(f),'volume_m3':float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6),'boundary_edges':int((n==1).sum()),'nonmanifold_edges':int((n!=2).sum())}

def run(arm):
 prep_path=P/('water11-source-reproduction-prepare.json' if arm=='S48_reproduction01' else ('water11-source-r075-prepare.json' if arm=='S48_R075' else 'water11-source-prepare.json'))
 prep=json.loads(prep_path.read_text(encoding='utf8'));a=prep['arms'][arm];cache=Path(a['cache']);process=P/f'water11-source-{arm}-process.json'
 assert process.exists(),'Audit only after supervisor finishes, never read an active producer'
 files=[f for f in cache.rglob('*') if f.is_file()];before={str(f):(f.stat().st_size,f.stat().st_mtime_ns) for f in files}
 cache_hashes_before={str(f):sha(f) for f in files}
 eligible={};missing={}
 for frame in range(1,13):
  paths={'config':cache/'config'/f'config_{frame:04}.uni','data':cache/'data'/f'fluid_data_{frame:04}.vdb','mesh':cache/'mesh'/f'fluid_mesh_{frame:04}.bobj.gz'}
  if not paths['config'].exists() or not paths['data'].exists():missing[str(frame)]={'status':'CONFIG_OR_VOLUME_DATA_NOT_AVAILABLE','files':{k:p.exists() for k,p in paths.items()}};continue
  try:
   cfg=config(paths['config']);openvdb.readAllGridMetadata(str(paths['data']))
   eligible[frame]={'paths':paths,'config':cfg}
  except Exception as e:missing[str(frame)]={'status':'INCOMPLETE_OR_CORRUPT_DATA','error':repr(e)}
 out={'arm':arm,'status':'RAW_SOURCE_AUDIT_IN_PROGRESS','supervisor':json.loads(process.read_text(encoding='utf-8-sig')),'missing_frames':missing,'frames':[],
  'true_t0':'NOT_SAVED_FIRST_FRAME_IS_POST_STEP','author_source_volume_m3':a['source_topology']['signed_volume_m3'],
  'author_normal_area_m2':.04317591235110372,'author_Q_m3_s':.2994137004643072,'author_Q_never_used_to_scale_measurements':True,
  'new_bakes':0,'new_renders':0,'source_geometry_sha256':a['source_geometry_sha256']}
 if not eligible:
  out['status']='NO_COMPLETE_VOLUME_FRAME_AVAILABLE';dump(P/f'water11-source-{arm}-audit.json',out);return
 frames=sorted(eligible);meta=openvdb.read(str(eligible[frames[0]]['paths']['data']),'phi');res=tuple(meta.metadata['file_base_resolution']);cell=float(meta.metadata['file_voxel_size'])
 out['actual_grid']=list(res);out['actual_cell_m']=cell;out['expected_grid_match']=list(res)==a['expected_grid'];out['expected_cell_match']=abs(cell-a['cell_m'])<1e-6
 scene=Path(a['scene']);assert sha(scene)==a['scene_sha256'];bpy.ops.wm.open_mainfile(filepath=str(scene));s=bpy.context.scene;obj=s.objects['WATER11_Source_Domain'];s.render.threads_mode='FIXED';s.render.threads=4
 coords=np.array([tuple(obj.matrix_world@v.co) for v in obj.data.vertices]);center=(coords.min(0)+coords.max(0))*.5;origin=center-np.array(res)*cell*.5
 scale=None
 if len(frames)>1:
  internal_ratio=(eligible[frames[-1]]['config']['T']-eligible[frames[0]]['config']['T'])/((frames[-1]-frames[0])/24);scale=cell*internal_ratio
  out['actual_time_units']={'internal_time_per_scene_second':internal_ratio,'m_s_per_raw_MAC_unit':scale,'basis':'actual config T differences / actual scene frame time; source velocity checked independently'}
 else:out['actual_time_units']={'status':'ONLY_ONE_CONFIG_NO_DIFFERENCE_BASED_CALIBRATION','raw_velocity_only':True}
 affine=None
 for frame in frames:
  mp=eligible[frame]['paths']['mesh']
  if not mp.exists():continue
  try:
   rv,rf=rawmesh(mp)
   if len(rv)<4:continue
   s.frame_set(frame);ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();actual=np.array([tuple(obj.matrix_world@v.co) for v in me.vertices]);ev.to_mesh_clear();assert len(actual)==len(rv)
   affine=np.linalg.lstsq(np.column_stack((rv,np.ones(len(rv)))),actual,rcond=None)[0];err=float(np.linalg.norm(np.column_stack((rv,np.ones(len(rv))))@affine-actual,axis=1).max());assert err<3e-6
   out['raw_mesh_world_mapping']={'affine':affine.tolist(),'max_error_m':err,'frame':frame};break
  except Exception as e:out.setdefault('mesh_mapping_failures',[]).append({'frame':frame,'error':repr(e)})
 out['actual_origin_world_m']=origin.tolist();out['lattice_phase_expected_error_m']=np.max(abs(origin-np.array(a['domain_aabb_m'])[:,0]));out['mapping_available']=affine is not None
 src=s.objects['WATER11_Exact_Frozen_Inflow'];src.data.calc_loop_triangles();sv=np.array([tuple(src.matrix_world@v.co) for v in src.data.vertices]);sf=np.array([list(t.vertices) for t in src.data.loop_triangles]);tree=BVHTree.FromPolygons(sv,sf,all_triangles=True)
 source_indices=[];lo=np.maximum(np.floor((sv.min(0)-origin)/cell).astype(int)-1,0);hi=np.minimum(np.ceil((sv.max(0)-origin)/cell).astype(int)+1,np.array(res)-2)
 def inside(p):
  count=0;direction=Vector((1,.317,.173)).normalized();pt=Vector(p)
  for _ in range(32):
   hit=tree.ray_cast(pt,direction,10)
   if hit[0] is None:break
   count+=1;pt=hit[0]+direction*1e-5
  return count%2==1
 for i in range(lo[0],hi[0]+1):
  for j in range(lo[1],hi[1]+1):
   for k in range(lo[2],hi[2]+1):
    if inside(origin+(np.array([i,j,k])+.5)*cell):source_indices.append((i,j,k))
 author={str(z):section(sv,sf,z) for z in PLANES};out['author_horizontal_sections']=author
 encoded=np.array(a['source_flow']['velocity_coord'])
 for frame in frames:
  pp=eligible[frame]['paths'];phi=array(pp['data'],'phi',res);velocity=array(pp['data'],'velocity',res);flags=array(pp['data'],'flags',res)
  assert np.isfinite(phi).all() and np.isfinite(velocity).all()
  row={'frame':frame,'first_solved_frame_not_t0':frame==1,'config':eligible[frame]['config'],'source_interior_geometric_cells':len(source_indices),
    'phi_volume_center_proxy_m3':int((phi<0).sum())*cell**3,'Fluid_flag_volume_proxy_m3':int(((flags&1)!=0).sum())*cell**3,'planes':{},'mesh_status':'NOT_AVAILABLE'}
  vv=ff=None
  if pp['mesh'].exists() and affine is not None:
   try:
    rv,ff=rawmesh(pp['mesh']);vv=np.column_stack((rv,np.ones(len(rv))))@affine;row['mesh_status']='AVAILABLE';row['mesh']=topology(vv,ff)
   except Exception as e:row['mesh_status']='UNREADABLE';row['mesh_error']=repr(e)
  sample=[]
  for i,j,k in source_indices:
   if phi[i,j,k]<0:sample.append([.5*(velocity[i,j,k,0]+velocity[i+1,j,k,0]),.5*(velocity[i,j,k,1]+velocity[i,j+1,k,1]),.5*(velocity[i,j,k,2]+velocity[i,j,k+1,2])])
  row['source_interior_wet_cells']=len(sample)
  if sample:
   med=np.median(sample,axis=0);row['source_interior_raw_median_velocity']=med.tolist()
   if scale is not None:
    row['source_interior_median_velocity_m_s']=(med*scale).tolist();row['source_velocity_encoded_relative_error']=float(np.linalg.norm(med*scale-encoded)/np.linalg.norm(encoded))
  for z in PLANES:
   measurement=plane(phi,velocity,origin,cell,scale,z);measurement['native_mesh_section']=section(vv,ff,z) if vv is not None else {'status':'MESH_NOT_AVAILABLE'}
   aa=author[str(z)]['area_m2'];measurement['author_stationary_source_horizontal_area_m2']=aa
   measurement['phi_to_author_stationary_source_area_ratio']=measurement['full']['phi_wet_area_m2']/aa if aa else None
   measurement['comparison_note']='Below finite source geometry area is zero; compare transported flux, not area/zero. f1 remains recorded even before arrival.'
   row['planes'][str(z)]=measurement
  s.frame_set(frame);ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());ps=next((p for p in ev.particle_systems if p.settings.type=='FLIP'),None)
  if ps is not None:
   row['FLIP_count_not_mass']=len(ps.particles)
   if len(ps.particles):
    particles=np.empty(len(ps.particles)*3,np.float32);ps.particles.foreach_get('location',particles);particles=particles.reshape(-1,3);row['FLIP_bounds_world_m']=np.stack((particles.min(0),particles.max(0)),1).tolist()
  out['frames'].append(row);dump(P/f'water11-source-{arm}-frame{frame:04}.json',row)
 q=[r['planes']['-5.64']['fixed_jet_window']['Q_net_down_m3_s'] for r in out['frames'] if r['frame']>=5];q=[x for x in q if x is not None]
 out['summary']={'available_frames':len(out['frames']),'frame1_volume_data_available':1 in eligible,'frame1_mesh_available':any(r['frame']==1 and r['mesh_status']=='AVAILABLE' for r in out['frames']),
   'Q_f5plus_median_m3_s':float(np.median(q)) if q else None,'Q_f5plus_relative_design_error':float(np.median(q)/out['author_Q_m3_s']-1) if q else None,
   'Q_f5plus_CV':float(np.std(q)/abs(np.mean(q))) if q and np.mean(q)!=0 else None,
   'not_terminal_only':True,'no_automatic_pass_from_summary':True}
 assert before=={str(f):(f.stat().st_size,f.stat().st_mtime_ns) for f in files},'Producer/files changed during audit'
 assert cache_hashes_before=={str(f):sha(f) for f in files},'Cache hash changed during read-only audit'
 out['native_cache_hashes_unchanged']=True;out['native_cache_hashes']=cache_hashes_before
 manifest_path=P/('water11-source-r075-preserved-cache-manifest.json' if arm=='S48_R075' else 'water11-source-preserved-cache-manifest.json')
 manifest=json.loads((P/'water11-source-cache-incident.json').read_text(encoding='utf8'))['all_current_remaining_cache_hashes'] if arm=='S48_reproduction01' else json.loads(manifest_path.read_text(encoding='utf8'));changed=[]
 for f in manifest:
  if not Path(f['path']).exists() or Path(f['path']).stat().st_size!=f['bytes'] or sha(f['path'])!=f['sha256']:changed.append(f['path'])
 out['old_cache_hash_changes']=changed;out['cache_readonly_check_pass']=True;assert not changed,changed
 out['status']='RAW_ALL12_COMPLETE_REVIEW_REQUIRED' if len(out['frames'])==12 else 'RAW_PARTIAL_PRESERVED_REVIEW_REQUIRED'
 dump(P/f'water11-source-{arm}-audit.json',out);print('WATER11_SOURCE_AUDIT_DONE',arm,json.dumps(out['summary']),flush=True)

def selfcheck():
 v=np.array([[0,0,0],[2,0,0],[2,3,0],[0,3,0],[0,0,4],[2,0,4],[2,3,4],[0,3,4]],float)
 faces=[[3,2,1,0],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7],[4,5,6,7]];f=np.array([tri for q in faces for tri in [[q[0],q[1],q[2]],[q[0],q[2],q[3]]]])
 a=section(v,f,1.3);assert abs(a['area_m2']-6)<1e-12 and a['bad_degree_vertices']==0,a
 assert abs(topology(v,f)['volume_m3']-24)<1e-12
 phi=np.full((8,8,8),-1.,np.float32);velocity=np.zeros((8,8,8,3),np.float32);velocity[:,:,:,2]=-2
 m=plane(phi,velocity,np.zeros(3),.1,.3,.35)['full'];assert abs(m['phi_wet_area_m2']-.49)<1e-12 and abs(m['Q_net_down_m3_s']-.294)<1e-6,m
 print('WATER11_AUDIT_ANALYTIC_SELF_CHECK_PASS',flush=True)

if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:]
 if args==['selfcheck']:selfcheck()
 elif len(args)==1 and args[0] in ['S24','S48','S48_R075','S48_reproduction01']:run(args[0])
 else:raise ValueError('Use selfcheck or S24/S48 after supervised bake; no bake/render function')
