"""Read native36 cache: no bake/render/save, no de-drift or geometry mapping."""
import sys,json,hashlib,time,gzip,struct,importlib.util
from pathlib import Path
import bpy,numpy as np,openvdb
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('impact09',ROOT/'qa/water09-impact36.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
r=json.loads(w.REPORT.read_text(encoding='utf-8'));assert r['status']=='BAKED36_RAW_CHECK_PENDING';assert w.sha(w.PILOT)==r['baked_sha256']
bpy.ops.wm.open_mainfile(filepath=str(w.PILOT));s,o,d=w.get();s.render.threads_mode='FIXED';s.render.threads=4;r['post_bake_assertions']=w.validate(r)
def bobj(frame):
 raw=gzip.open(w.CACHE/'mesh'/f'fluid_mesh_{frame:04}.bobj.gz','rb').read();n=struct.unpack_from('<i',raw,0)[0];a=np.frombuffer(raw,'<f4',count=n*3,offset=4).reshape(-1,3).astype(np.float64);off=4+n*12;nn=struct.unpack_from('<i',raw,off)[0];off+=4+nn*12;nt=struct.unpack_from('<i',raw,off)[0];off+=4;f=np.frombuffer(raw,'<i4',count=nt*3,offset=off).reshape(-1,3);assert off+nt*12==len(raw);return a,f
s.frame_set(1);bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();actual=np.array([tuple(o.matrix_world@v.co) for v in me.vertices]);raw,ff=bobj(1);assert len(raw)==len(actual)
affine=np.linalg.lstsq(np.column_stack((raw,np.ones(len(raw)))),actual,rcond=None)[0];err=np.linalg.norm(np.column_stack((raw,np.ones(len(raw))))@affine-actual,axis=1);assert err.max()<2e-6;ev.to_mesh_clear()
# BOBJ coordinates are centered and normalized, not raw solver-cell coordinates.
# Verify their actual affine map; VDB metadata independently supplies cell and resolution.
meta=openvdb.readAllGridMetadata(str(w.CACHE/'data/fluid_data_0001.vdb'));phi_meta=openvdb.read(str(w.CACHE/'data/fluid_data_0001.vdb'),'phi')
res=tuple(int(v) for v in phi_meta.metadata['file_base_resolution']);cell=float(phi_meta.metadata['file_voxel_size'])
assert abs(cell-.025)<1e-6 and np.max(abs(affine[:3]-np.eye(3)*cell*max(res)))<1e-6
origin=affine[3]-.5*cell*np.array(res)
assert res[:2]==(96,80);centers=[origin[i]+(np.arange(res[i])+.5)*cell for i in range(3)]
roi=np.array(w.ROI);xy=np.array([(x,y) for y in np.linspace(roi[1,0]+.1,roi[1,1]-.1,55) for x in np.linspace(roi[0,0]+.1,roi[0,1]-.1,65)]);impact=np.array([.797341526,-2.211417675]);dist=np.linalg.norm(xy-impact,axis=1)
jetxy=(centers[0][:,None]>.73)&(centers[0][:,None]<1.14)&(centers[1][None,:]>-2.36)&(centers[1][None,:]<-1.88)
jetverts=np.array([tuple(s.objects[w.JET].matrix_world@v.co) for v in s.objects[w.JET].data.vertices]);jet_tree=w.h.render_bvh(s.objects[w.JET]);src_mask=np.zeros(res,bool)
for i,x in enumerate(centers[0]):
 if not jetverts[:,0].min()<x<jetverts[:,0].max():continue
 for j,y in enumerate(centers[1]):
  if not jetverts[:,1].min()<y<jetverts[:,1].max():continue
  for k,z in enumerate(centers[2]):
   if not jetverts[:,2].min()<z<jetverts[:,2].max():continue
   parity=w.h.parity(jet_tree,Vector((x,y,z)))
   if all(v%2 for v in parity):src_mask[i,j,k]=True
def array(path,name,dtype):
 g=openvdb.read(path,name);shape=res+((3,) if name=='velocity' else ());a=np.empty(shape,dtype);g.copyToArray(a,(0,0,0));return a
def zinterp(a,k):
 lower=int(np.floor(k));t=k-lower;assert 0<=lower and lower+1<a.shape[2],(k,res)
 return a[:,:,lower]*(1-t)+a[:,:,lower+1]*t
def flux(phi,velocity,z):
 k=(z-origin[2])/cell;ph=zinterp(phi,k-.5);vz=zinterp(velocity[:,:,:,2],k)*cell*2.5;wet=np.clip(.5-ph,0,1)
 down=wet*np.maximum(-vz,0)*cell**2;up=wet*np.maximum(vz,0)*cell**2
 return {'z_m':z,'MAC_k':float(k),'positive_down_m3_s':float(down.sum()),'positive_up_m3_s':float(up.sum()),'net_down_m3_s':float(down.sum()-up.sum()),'jet_window_net_down_m3_s':float((down-up)[jetxy].sum()),'jet_window_down_m3_s':float(down[jetxy].sum()),'jet_window_wet_area_m2':float(wet[jetxy].sum()*cell**2)}
def sliced_segments(v,f,z):
 tt=v[f];mask=(tt[:,:,2].min(1)<z)&(tt[:,:,2].max(1)>z);out=[]
 for tri in tt[mask]:
  hits=[]
  for i,j in [(0,1),(1,2),(2,0)]:
   a,b=tri[i],tri[j]
   if (a[2]-z)*(b[2]-z)<0:hits.append(a+(b-a)*((z-a[2])/(b[2]-a[2])))
  if len(hits)==2:out.append(hits)
 return np.array(out)
source_me=s.objects[w.JET].data;source_me.calc_loop_triangles();src_faces=np.array([tuple(t.vertices) for t in source_me.loop_triangles]);src_segments=sliced_segments(jetverts,src_faces,-5.35)
def distance_segments(points,segs):
 a=segs[:,0,:2];dlt=segs[:,1,:2]-a;dd=np.sum(dlt*dlt,1);p=points[:,:2,None].transpose(0,2,1);diff=p-a[None];t=np.clip(np.sum(diff*dlt[None],2)/dd[None],0,1);return np.sqrt(np.min(np.sum((diff-t[:,:,None]*dlt[None])**2,2),1))
r['raw_mapping']={'mesh_to_world_affine':affine.tolist(),'max_fit_error_m':float(err.max()),'cell_m':cell,'solver_origin_world_m':origin.tolist(),'actual_base_resolution':list(res),'metadata_grid_names':[g.name for g in meta],'VDB_velocity_to_m_s':cell*2.5,'velocity_conversion_evidence':'Blender5.2 fluid.cc internal_time=1/(25*DT_DEFAULT),DT_DEFAULT=.1; saved MAC units converted world=raw*cell*2.5. Independently check source cells below.','source_interior_grid_cell_count':int(src_mask.sum()),'pressure_available':any(g.name=='pressure' for g in meta)}
frames=[];heights=[]
for frame in range(1,37):
 s.frame_set(frame);bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());raw,ff=bobj(frame);vv=np.column_stack((raw,np.ones(len(raw))))@affine;tt=(vv-vv.mean(0))[ff];volume=float(np.einsum('ij,ij->i',tt[:,0],np.cross(tt[:,1],tt[:,2])).sum()/6)
 edges=np.concatenate((ff[:,[0,1]],ff[:,[1,2]],ff[:,[2,0]]));edges.sort(axis=1);_,count=np.unique(edges,axis=0,return_counts=True);tree=BVHTree.FromPolygons(vv,ff,all_triangles=True);hh=[];nn=[]
 for x,y in xy:
  hit=tree.ray_cast(Vector((x,y,w.HEAD+.25)),Vector((0,0,-1)),1.2);hh.append(hit[0].z if hit[0] else np.nan);nn.append(hit[1].z if hit[0] else 0)
 hh=np.array(hh);valid=np.isfinite(hh)&(np.array(nn)>.3);far=valid&(dist>.45);heights.append(hh)
 row={'frame':frame,'mesh_volume_m3':volume,'mesh_vertices':len(vv),'mesh_triangles':len(ff),'mesh_boundary_edges':int((count==1).sum()),'mesh_nonmanifold_edges':int((count!=2).sum()),'height_valid_count':int(valid.sum()),'height_missing_or_steep_count':int((~valid).sum()),'pool_far_median_head_m':float(np.median(hh[far])),'pool_far_p05_p95_head_m':np.quantile(hh[far],[.05,.95]).tolist(),'all_valid_head_minmax_m':[float(hh[valid].min()),float(hh[valid].max())],'particle_systems':[]}
 for ps in ev.particle_systems:
  a=np.empty(len(ps.particles)*3,np.float32);ps.particles.foreach_get('location',a);a=a.reshape(-1,3);info={'type':ps.settings.type,'count':len(a)}
  if len(a):info.update({'bounds_m':np.stack((a.min(0),a.max(0)),1).tolist(),'outside_authored_domain_count':int(np.any((a<roi[:,0]-1e-5)|(a>roi[:,1]+1e-5),1).sum()),'above_authored_top_count':int((a[:,2]>roi[2,1]).sum())})
  if ps.settings.type=='FLIP':
   idx=np.floor((a[:,:2]-origin[:2])/cell).astype(int);good=np.all((idx>=0)&(idx<np.array(res[:2])),1);top=np.full(res[0]*res[1],-np.inf,np.float32);np.maximum.at(top,idx[good,0]*res[1]+idx[good,1],a[good,2]);top=top.reshape(res[:2]);env=top[4:-4,4:-4];env=env[np.isfinite(env)];info['interior_top_envelope_median_m']=float(np.median(env));info['interior_top_envelope_p05_p95_m']=np.quantile(env,[.05,.95]).tolist()
  row['particle_systems'].append(info)
 path=str(w.CACHE/'data'/f'fluid_data_{frame:04}.vdb');phi=array(path,'phi',np.float32);obstacle=array(path,'phi_obstacle',np.float32);vel=array(path,'velocity',np.float32)
 row['phi_negative_volume_proxy_m3']=float((phi<0).sum()*cell**3);row['phi_negative_excluding_obstacle_proxy_m3']=float(((phi<0)&(obstacle>=0)).sum()*cell**3)
 row['flux_z_minus5_50']=flux(phi,vel,-5.50);row['flux_inside_source_z_minus5_35']=flux(phi,vel,-5.35);row['flux_near_top']=flux(phi,vel,float(origin[2]+(res[2]-2)*cell))
 cv=vel.copy()
 for axis in range(3):
  nxt=np.roll(vel[:,:,:,axis],-1,axis=axis);cv[:,:,:,axis]=.5*(vel[:,:,:,axis]+nxt)
 src=cv[src_mask&(phi<0)]*cell*2.5;row['source_cell_velocity_median_m_s']=np.median(src,0).tolist() if len(src) else None;row['source_cell_wet_count']=len(src)
 segments=sliced_segments(vv,ff,-5.35)
 if len(segments):
  mids=segments.mean(1);distances=distance_segments(mids,src_segments);row['source_join']={'cache_slice_segment_count':len(segments),'distance_to_authored_ring_p50_p95_max_m':np.quantile(distances,[.5,.95,1]).tolist(),'all_segments_in_jet_xy_window':bool(np.all((mids[:,:2]>jetverts[:,:2].min(0)-.1)&(mids[:,:2]<jetverts[:,:2].max(0)+.1))),'status':'MEASURABLE_NOT_JOINED_NORMALS_OR_MANIFOLD_COMPOSITE_UNVERIFIED'}
 else:row['source_join']={'cache_slice_segment_count':0,'status':'NO_RING_JOIN_FAIL'}
 frames.append(row);print('IMPACT09_RAW_FRAME',json.dumps(row),flush=True)
r['frames']=frames
v=np.array([x['mesh_volume_m3'] for x in frames]);q=np.array([x['flux_z_minus5_50']['jet_window_net_down_m3_s'] for x in frames]);qt=np.array([-x['flux_near_top']['net_down_m3_s'] for x in frames]);integ=np.concatenate(([0],np.cumsum((q[1:]+q[:-1])*.5/24)));out=np.concatenate(([0],np.cumsum((qt[1:]+qt[:-1])*.5/24)));residual=v-v[0]-integ+out
r['summary']={'frame1_mesh_minus_initial_pool_m3':float(v[0]-r['initial_pool_volume_m3']),'mesh_volume_change_f1_f36_m3':float(v[-1]-v[0]),'nominal_injection_f1_f36_m3':r['nominal_Q_m3_s']*35/24,'measured_jet_plane_net_flux_integral_f1_f36_m3':float(integ[-1]),'near_top_flux_integral_f1_f36_m3':float(out[-1]),'mesh_minus_jet_plane_flux_residual_f1_f36_m3':float(residual[-1]),'max_abs_mesh_minus_jet_plane_flux_residual_m3':float(abs(residual).max()),'jet_plane_median_Q_f5_f36_m3_s':float(np.median(q[4:])),'jet_plane_median_Q_relative_nominal_error':float(np.median(q[4:])/r['nominal_Q_m3_s']-1),'pool_far_median_head_change_f1_f36_m':frames[-1]['pool_far_median_head_m']-frames[0]['pool_far_median_head_m'],'max_far_median_error_from_original_head_m':max(abs(x['pool_far_median_head_m']-w.HEAD) for x in frames),'all_meshes_closed_manifold':all(x['mesh_boundary_edges']==x['mesh_nonmanifold_edges']==0 for x in frames),'flux_limit':'MAC field converted by verified source code; linearphi face occupancy and frame snapshots are approximate flux quadrature, jet plane excludes changing air-volume above plane; report source-cell agreement before interpreting','boundary_limit':'closed side walls; wave reflection expected after approximately0.77s; source initial head not held after injection','join_status':'RING_DISTANCE_ONLY_NO_COMPOSITE_JOIN_PROOF; external pool join not installed or forced','visual_status':'NOT_RENDERED_PREVIOUS_WATER_VISUAL_FAIL_UNCHANGED'}
r['preserved_caches_unchanged_after_check']=w.manifest()==r['preserved_cache_manifest'];assert r['preserved_caches_unchanged_after_check'];assert w.sha(w.PILOT)==r['baked_sha256']
r['status']='NATIVE36_RAW_DIAGNOSTIC_REVIEW_REQUIRED';r['check_scene_sha256']=w.sha(w.PILOT);w.write(r);np.savez_compressed(ROOT/'qa/water09-impact36-heights.npz',xy=xy,height=np.array(heights),mesh_flux_residual=residual)
print('IMPACT09_CHECK_DONE',json.dumps(r['summary']),flush=True)
