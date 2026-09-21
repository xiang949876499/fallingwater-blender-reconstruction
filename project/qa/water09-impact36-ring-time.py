"""Read-only actual timebase, ring connectivity/normal comparison, boundary-layer flux."""
import sys,json,gzip,struct,math,importlib.util
from pathlib import Path
import bpy,numpy as np,openvdb
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'qa';r=json.loads((P/'water09-impact36.json').read_text(encoding='utf-8'));CACHE=ROOT/'caches/fluid_water09/impact36'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene/Fallingwater_water09_impact36.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4
source=s.objects['HYBRID07_Branch_Exact_Source'];source.data.calc_loop_triangles();v=np.array([tuple(source.matrix_world@p.co) for p in source.data.vertices]);f=np.array([tuple(t.vertices) for t in source.data.loop_triangles]);tree=BVHTree.FromPolygons(v,f,all_triangles=True)
affine=np.array(r['raw_mapping']['mesh_to_world_affine']);res=tuple(r['raw_mapping']['actual_base_resolution']);cell=r['raw_mapping']['cell_m'];origin=np.array(r['raw_mapping']['solver_origin_world_m'])
def slice_ring(v,f):
 z=-5.35;tt=v[f];mask=(tt[:,:,2].min(1)<z)&(tt[:,:,2].max(1)>z);segments=[];normals=[]
 for tri in tt[mask]:
  hits=[]
  for i,j in [(0,1),(1,2),(2,0)]:
   a,b=tri[i],tri[j]
   if (a[2]-z)*(b[2]-z)<0:hits.append(a+(b-a)*((z-a[2])/(b[2]-a[2])))
  if len(hits)==2:
   segments.append(hits);nn=np.cross(tri[1]-tri[0],tri[2]-tri[0]);normals.append(nn/np.linalg.norm(nn))
 seg=np.array(segments);adj={};coords={}
 for a,b in seg:
  aa=tuple(np.round(a,6));bb=tuple(np.round(b,6));coords[aa]=a;coords[bb]=b;adj.setdefault(aa,[]).append(bb);adj.setdefault(bb,[]).append(aa)
 bad=sum(len(n)!=2 for n in adj.values());areas=[];remaining=set(adj);components=[]
 while remaining:
  first=next(iter(remaining));stack=[first];comp=set()
  while stack:
   key=stack.pop()
   if key in comp:continue
   comp.add(key);stack+=adj[key]
  remaining-=comp;components.append(len(comp))
  if any(len(adj[key])!=2 for key in comp):continue
  prev=None;key=first;cycle=[]
  for _ in range(len(comp)+1):
   cycle.append(coords[key]);nxt=next(k for k in adj[key] if k!=prev);prev,key=key,nxt
   if key==first:break
  a=np.array(cycle);areas.append(abs(float(np.sum(a[:,0]*np.roll(a[:,1],-1)-a[:,1]*np.roll(a[:,0],-1))/2)))
 return {'segments':len(seg),'component_nodes':components,'bad_degree_nodes':bad,'loop_areas_m2':areas,'total_closed_area_m2':sum(areas),'bbox_xy_m':np.stack((seg[:,:,:2].min((0,1)),seg[:,:,:2].max((0,1))),1).tolist()},seg,np.array(normals)
src,_,_=slice_ring(v,f);rows=[];times=[];top=[]
for frame in range(1,37):
 data=gzip.decompress((CACHE/'config'/f'config_{frame:04}.uni').read_bytes());assert len(data)==204 and data[200:204]==b'C01\0'
 times.append({'frame':frame,'resolution':list(struct.unpack_from('<3i',data,4)),'dx_internal':struct.unpack_from('<f',data,16)[0],'last_substep_dt_internal':struct.unpack_from('<f',data,20)[0],'time_total_internal':struct.unpack_from('<f',data,196)[0]})
 raw=gzip.decompress((CACHE/'mesh'/f'fluid_mesh_{frame:04}.bobj.gz').read_bytes());n=struct.unpack_from('<i',raw,0)[0];a=np.frombuffer(raw,'<f4',count=n*3,offset=4).reshape(-1,3).astype(float);off=4+n*12;nn=struct.unpack_from('<i',raw,off)[0];off+=4+nn*12;nf=struct.unpack_from('<i',raw,off)[0];off+=4;ff=np.frombuffer(raw,'<i4',count=nf*3,offset=off).reshape(-1,3);vv=np.column_stack((a,np.ones(len(a))))@affine
 ring,segs,normals=slice_ring(vv,ff);angles=[]
 for mid,normal in zip(segs.mean(1),normals):
  nearest=tree.find_nearest(Vector(mid));angles.append(math.degrees(math.acos(np.clip(np.dot(normal,nearest[1]),-1,1))))
 ring.update({'frame':frame,'outward_normal_angle_p50_p95_max_deg':np.quantile(angles,[.5,.95,1]).tolist(),'area_ratio_to_authored_source':ring['total_closed_area_m2']/src['total_closed_area_m2']});rows.append(ring)
 path=str(CACHE/'data'/f'fluid_data_{frame:04}.vdb');fg=openvdb.read(path,'flags');fl=np.empty(res,np.int32);fg.copyToArray(fl,(0,0,0));pg=openvdb.read(path,'phi');ph=np.empty(res,np.float32);pg.copyToArray(ph,(0,0,0));vg=openvdb.read(path,'velocity');vel=np.empty(res+(3,),np.float32);vg.copyToArray(vel,(0,0,0))
 flags,cnt=np.unique(fl[:,:,-1],return_counts=True);mask=.5*(ph[:,:,-2]+ph[:,:,-1])<0;vvz=vel[:,:,-1,2]*cell*2.5
 top.append({'frame':frame,'last_MAC_face_world_z_m':float(origin[2]+(res[2]-1)*cell),'last_phi_cell_world_z_m':float(origin[2]+(res[2]-.5)*cell),'last_layer_flags':{str(k):int(v) for k,v in zip(flags,cnt)},'last_layer_negative_phi_cells':int((ph[:,:,-1]<0).sum()),'last_stored_MAC_face_binary_phi_flux_up_m3_s':float(np.maximum(vvz[mask],0).sum()*cell**2),'not_exact_geometric_top_flux':'Last storedMAC face is one cell inside grid top, not a stored outside face; binaryphi area proxy. Deleted crossings cannot be reconstructed from survivingparticle counts.'})
T=np.array([t['time_total_internal'] for t in times]);ratio=(T[-1]-T[0])/(35/24)
out={'status':'READ_ONLY_RING_TIME_TOP_AUDIT','source_ring':src,'ring_frames':rows,'config_frames':times,'actual_time_conversion':{'internal_time_per_scene_second_from_f1_f36':float(ratio),'world_velocity_scale_from_config':float(cell*ratio),'frame_delta_internal_min_max':[float(np.diff(T).min()),float(np.diff(T).max())],'config_limit':'Onlylastdt andtotal; no actualsubstepcount or fullperstepdt list. Frame index fromfilename, fps24 andtime_scale1 fromsavedscene. No universalVDBunit assumption.'},'ring_summary':{'all36_single_closed_loops':all(x['bad_degree_nodes']==0 and len(x['component_nodes'])==1 for x in rows),'source_area_m2':src['total_closed_area_m2'],'cache_area_ratio_min_max':[min(x['area_ratio_to_authored_source'] for x in rows),max(x['area_ratio_to_authored_source'] for x in rows)],'max_normal_angle_deg':max(x['outward_normal_angle_p50_p95_max_deg'][-1] for x in rows),'composite_join_made':False},'top_boundary_frames':top,'source_links':['https://raw.githubusercontent.com/blender/blender/blender-v5.2-release/intern/mantaflow/intern/MANTA_main.cpp','https://raw.githubusercontent.com/blender/blender/blender-v5.2-release/source/blender/makesdna/DNA_fluid_types.h','https://raw.githubusercontent.com/blender/blender/blender-v5.2-release/extern/mantaflow/preprocessed/fluidsolver.cpp']}
(P/'water09-impact36-ring-time.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print('IMPACT09_RING_TIME_DONE',json.dumps({k:out[k] for k in ['actual_time_conversion','ring_summary']}),flush=True)
