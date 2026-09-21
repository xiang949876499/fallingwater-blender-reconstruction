"""Read-only refinement of native flux: sign-based area integration, actual time metadata."""
import json,gzip,struct,sys
from pathlib import Path
import numpy as np,openvdb
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'qa';r=json.loads((P/'water09-impact36.json').read_text(encoding='utf-8'));cache=ROOT/'caches/fluid_water09/impact36'
cell=r['raw_mapping']['cell_m'];origin=np.array(r['raw_mapping']['solver_origin_world_m']);res=tuple(r['raw_mapping']['actual_base_resolution'])
def arr(path,name,dtype):
 g=openvdb.read(path,name);a=np.empty(res+((3,) if name=='velocity' else ()),dtype);g.copyToArray(a,(0,0,0));return g,a
def zinterp(a,k):
 n=int(np.floor(k));t=k-n;return a[:,:,n]*(1-t)+a[:,:,n+1]*t
def flux_sign(ph,vz,sub=8):
 # Integrate bilinear phi<0, not a ramp that gives phi=0/background half occupancy.
 # Staggered Vz already sampled at same worldZ; both fields have same XY center positions.
 qdown=qup=wet=0.;vertex_source_window=0.
 for i in range(sub):
  u=(i+.5)/sub
  for j in range(sub):
   v=(j+.5)/sub
   pp=(1-u)*(1-v)*ph[:-1,:-1]+u*(1-v)*ph[1:,:-1]+(1-u)*v*ph[:-1,1:]+u*v*ph[1:,1:]
   vv=(1-u)*(1-v)*vz[:-1,:-1]+u*(1-v)*vz[1:,:-1]+(1-u)*v*vz[:-1,1:]+u*v*vz[1:,1:]
   mask=pp<0;factor=cell**2/sub**2
   qdown+=float(np.maximum(-vv[mask],0).sum())*factor;qup+=float(np.maximum(vv[mask],0).sum())*factor;wet+=int(mask.sum())*factor
 return {'down_m3_s':qdown,'up_m3_s':qup,'net_down_m3_s':qdown-qup,'wet_area_m2':wet}
rows=[];metadata=[]
for frame in range(1,37):
 path=str(cache/'data'/f'fluid_data_{frame:04}.vdb');pg,phi=arr(path,'phi',np.float32);vg,vel=arr(path,'velocity',np.float32)
 if frame in (1,18,36):metadata.append({'frame':frame,'phi_metadata':{k:str(v) for k,v in pg.metadata.items()},'velocity_metadata':{k:str(v) for k,v in vg.metadata.items()}})
 row={'frame':frame}
 for name,z in [('jet',-5.50),('source',-5.35),('near_top',origin[2]+(res[2]-2)*cell)]:
  k=(z-origin[2])/cell;ph=zinterp(phi,k-.5);vz=zinterp(vel[:,:,:,2],k)*cell*2.5
  row[name]=flux_sign(ph,vz);row[name]['phi_negative_center_count']=int((ph<0).sum());row[name]['phi_zero_center_count']=int((ph==0).sum());row[name]['max_abs_raw_vz']=float(abs(vz/(cell*2.5)).max())
 rows.append(row);print('FLUX09_SIGN_FRAME',json.dumps(row),flush=True)
q=np.array([f['jet']['net_down_m3_s'] for f in rows]);top=np.array([-f['near_top']['net_down_m3_s'] for f in rows]);V=np.array([f['mesh_volume_m3'] for f in r['frames']]);I=np.concatenate(([0],np.cumsum((q[1:]+q[:-1])*.5/24)));O=np.concatenate(([0],np.cumsum((top[1:]+top[:-1])*.5/24)));residual=V-V[0]-I+O
source=np.array([f['source_cell_velocity_median_m_s'] for f in r['frames']]);target=np.array(r['jet_flow']['velocity_coord']);sample=source[4:];errs=np.linalg.norm(sample-target,axis=1)/np.linalg.norm(target)
out={'status':'READ_ONLY_NATIVE_FLUX_AREA_REFINEMENT','method':'8x8 bilinear phi<0 subcell area integration at actual MAC worldZ; zero/background phi is not treated as half full. Velocity interpolated at same subcell. Full plane excludes outer half-cell ring. Time snapshot quadrature, not exact solver mass.','velocity_unit_sources':['https://raw.githubusercontent.com/blender/blender/blender-v5.2-release/source/blender/blenkernel/intern/fluid.cc','https://raw.githubusercontent.com/blender/blender/blender-v5.2-release/extern/mantaflow/preprocessed/fileio/iovdb.cpp','https://raw.githubusercontent.com/blender/blender/blender-v5.2-release/extern/mantaflow/preprocessed/grid.h','https://raw.githubusercontent.com/blender/blender/blender-v5.2-release/extern/mantaflow/preprocessed/fileio/iomeshes.cpp'],'time_factor_scope':{'Blender_version':'5.2.1','DT_DEFAULT':.1,'frame_normalization_fps':25,'scene_fps':24,'time_scale':r['post_bake_assertions']['all_settings']['time_scale'],'world_m_s_per_raw_unit':cell*2.5,'not_universal_without_verifying_engine_and_time_scale':True},'raw_mapping':r['raw_mapping'],'metadata_samples':metadata,'frames':rows,'summary':{'Q_f5_36_median_m3_s':float(np.median(q[4:])),'Q_f5_36_nominal_relative_error':float(np.median(q[4:])/r['nominal_Q_m3_s']-1),'integrated_jet_f1_f36_m3':float(I[-1]),'integrated_near_top_f1_f36_m3':float(O[-1]),'mesh_change_f1_f36_m3':float(V[-1]-V[0]),'residual_last_m3':float(residual[-1]),'residual_max_abs_m3':float(abs(residual).max()),'source_velocity_median_f5_36_m_s':np.median(sample,0).tolist(),'source_velocity_relative_error_max':float(errs.max()),'source_velocity_relative_error_median':float(np.median(errs))}}
(P/'water09-impact36-flux-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print('FLUX09_SIGN_DONE',json.dumps(out['summary']),flush=True)
