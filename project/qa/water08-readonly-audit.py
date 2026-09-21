"""Read-only inspection/counterfactual arrays. Never bake, render, or save a blend."""
import sys,json,hashlib,time,gzip,struct
from pathlib import Path
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import hybrid_water as h
import hybrid_impact as hi
import hybrid_motion as hm

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def coords(data):
 a=np.empty(len(data)*3,np.float32);data.foreach_get('co',a);return a.reshape((-1,3)).astype(np.float64)
def bounds(a):return [[float(a[:,k].min()),float(a[:,k].max())] for k in range(3)] if len(a) else None
result={'read_only':True,'saved_scenes':False,'bake_run':False,'render_run':False}
bpy.ops.wm.open_mainfile(filepath=str(hi.PILOT));scene=bpy.context.scene
scene.render.threads_mode='FIXED';scene.render.threads=4
domain=scene.objects[hi.DOMAIN];d=next(m.domain_settings for m in domain.modifiers if m.type=='FLUID')
domain_basis=np.array([tuple(domain.matrix_world@v.co) for v in domain.data.vertices]);domain_aabb=bounds(domain_basis)
fields=['resolution_max','cache_type','cache_directory','cache_frame_start','cache_frame_end','simulation_method','flip_ratio','use_fractions','delete_in_obstacle','timesteps_min','timesteps_max','cfl_condition','time_scale','use_collision_border_bottom','use_collision_border_top','use_collision_border_front','use_collision_border_back','use_collision_border_left','use_collision_border_right']
pilot={'source':str(hi.PILOT),'sha256':digest(hi.PILOT),'settings':{k:getattr(d,k) for k in fields},'matrix_world':[list(row) for row in domain.matrix_world],'basis_domain_aabb_m':domain_aabb,'evaluated_frame36_mesh_dimensions_not_domain_size':list(domain.dimensions),'sources':[]}
for obj in scene.objects:
 for mod in obj.modifiers:
  if mod.type!='FLUID' or mod.fluid_type!='FLOW':continue
  f=mod.flow_settings
  info={'name':obj.name,'settings':{},'bounds':h.aabb(obj),'topology':h.topology(obj)}
  for k in ['flow_type','flow_behavior','flow_source','use_initial_velocity','velocity_normal','surface_distance','use_inflow','subframes','volume_density']:
   if hasattr(f,k):info['settings'][k]=getattr(f,k)
  info['settings']['velocity_coord']=list(f.velocity_coord)
  a=np.array([tuple(obj.matrix_world@v.co) for v in obj.data.vertices])
  if 'Pool' in obj.name:
   cols=a.reshape((-1,8,3));foot=(cols[:,1,0]-cols[:,0,0])*(cols[:,2,1]-cols[:,1,1]);depth=cols[:,4:,2].mean(axis=1)-cols[:,0,2]
   info['column_count']=len(cols);info['footprint_area_m2']=float(foot.sum());info['column_volume_m3']=float((foot*depth).sum());info['depth_m']=h.stats(depth.tolist())
   np.savez_compressed(ROOT/'qa'/('water08-'+obj.name+'.npz'),columns=cols)
   cross=[]
   aabb=domain_aabb
   for axis,k,side,sgn in [('x',0,'min',-1),('x',0,'max',1),('y',1,'min',-1),('y',1,'max',1)]:
    facecoord=aabb[k][0 if sgn<0 else 1]
    selected=cols[np.any(np.abs(cols[:,:4,k]-facecoord)<1e-5,axis=1)]
    edges=[]
    for col in selected:
     ids=np.where(np.abs(col[:4,k]-facecoord)<1e-5)[0]
     if len(ids)!=2:continue
     width=abs(col[ids[1],1-k]-col[ids[0],1-k]);dep=col[ids+4,2].mean()-col[0,2]
     edges.append((float(width),float(dep)))
    area=sum(w*dep for w,dep in edges);outvel=float(f.velocity_coord[k])*sgn
    cross.append({'side':axis+'_'+side,'wet_edge_length_m':sum(w for w,dep in edges),'wet_cross_section_m2':area,'velocity_outward_m_s':outvel,'kinematic_Q_outward_m3_s':area*outvel,'free_outfall_scale_m3_s':sum(w*1.705*max(dep,0)**1.5 for w,dep in edges),'edge_depths':edges})
   info['boundary_cross_sections']=cross
  pilot['sources'].append(info)
result['pilot']=pilot
print('WATER08 pilot audited',flush=True)
def read_bobj(frame):
 p=hi.CACHE/'mesh'/f'fluid_mesh_{frame:04}.bobj.gz';raw=gzip.open(p,'rb').read();n=struct.unpack_from('<i',raw,0)[0]
 a=np.frombuffer(raw,'<f4',count=n*3,offset=4).reshape(-1,3).astype(np.float64);off=4+n*12
 nn=struct.unpack_from('<i',raw,off)[0];off+=4+nn*12;nt=struct.unpack_from('<i',raw,off)[0];off+=4
 f=np.frombuffer(raw,'<i4',count=nt*3,offset=off).reshape(-1,3)
 assert off+nt*12==len(raw)
 return a,f
scene.frame_set(1);bpy.context.view_layer.update();ev=domain.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
actual=coords(mesh.vertices);actual=np.array([tuple(domain.matrix_world@__import__('mathutils').Vector(p)) for p in actual]);raw,ff=read_bobj(1)
assert len(raw)==len(actual)
affine=np.linalg.lstsq(np.column_stack((raw,np.ones(len(raw)))),actual,rcond=None)[0]
err=np.linalg.norm(np.column_stack((raw,np.ones(len(raw))))@affine-actual,axis=1);ev.to_mesh_clear()
assert err.max()<2e-6,'Raw bobj to world mapping must match evaluated data'
mass=[]
for frame in range(1,37):
 v,f=read_bobj(frame);v=np.column_stack((v,np.ones(len(v))))@affine;stable=v-v.mean(axis=0);t=stable[f]
 vol=float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6)
 edges=np.concatenate((f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]));edges.sort(axis=1);_,counts=np.unique(edges,axis=0,return_counts=True)
 mass.append({'frame':frame,'vertices':len(v),'triangles':len(f),'signed_closed_mesh_volume_m3':vol,'boundary_edges':int((counts==1).sum()),'nonmanifold_edges':int((counts!=2).sum()),'world_bounds_m':bounds(v)})
 print('WATER08 mesh volume',frame,vol,flush=True)
result['cache_mesh_volume']={'method':'Float64 closed render triangle integral after raw bobj affine mapping validated against actual evaluated frame1; mesh reconstruction volume is proxy, not solver phi volume or exact conserved particle mass','raw_to_world_affine':affine.tolist(),'frame1_affine_max_error_m':float(err.max()),'frames':mass}
bpy.ops.wm.open_mainfile(filepath=str(hm.OUTPUT));scene=bpy.context.scene
obj=scene.objects['WATER_Hybrid07a_Continuous_River_Branch_Pool'];me=obj.data;me.calc_loop_triangles()
faces=np.array([tuple(t.vertices) for t in me.loop_triangles],np.int32)
base=coords(me.shape_keys.key_blocks[0].data)
tri=base[faces];normal0=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length0=np.linalg.norm(normal0,axis=1);valid=length0>1e-9
fall=np.array([a.value for a in me.attributes['H07_fall'].data]);pond=np.array([a.value for a in me.attributes['H07_pond'].data]);active=(fall>0)|(pond>0)
def bad(vv):
 t=vv[faces];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);dot=np.einsum('ij,ij->i',normal0,n)
 return np.where(valid&(dot<0))[0]
allbad=[];framebad=[]
for frame in range(1,37):
 vv=coords(me.shape_keys.key_blocks[frame].data);indices=bad(vv);allbad.extend(indices.tolist());framebad.append(indices.tolist())
badtri=np.unique(allbad);badverts=np.unique(faces[badtri].ravel());ringmask=np.zeros(len(base),bool);ringmask[badverts]=True
# Triangulated render edges are the relevant local neighborhood, including diagonals.
touch=np.any(ringmask[faces],axis=1);ring=np.unique(faces[touch].ravel());ringmask[ring]=True
counter=[];newunion=[];dmax=0
for frame in range(1,37):
 vv=coords(me.shape_keys.key_blocks[frame].data);dmax=max(dmax,float(np.linalg.norm(vv[ring]-base[ring],axis=1).max()))
 vv[ring]=base[ring];after=bad(vv);new=np.setdiff1d(after,badtri);newunion.extend(new.tolist())
 counter.append({'frame':frame,'before_bad_triangles':framebad[frame-1],'after_freeze_bad_triangles':after.tolist(),'new_bad_triangles':new.tolist()})
np.savez_compressed(ROOT/'qa/water08-normal-freeze-arrays.npz',bad_triangles=badtri,bad_vertices=badverts,ring_vertices=ring,ring_base_coordinates=base[ring])
relative=base[ring]-np.array([2.4,-2.83,0]);sc=np.column_stack((relative@np.array(h.DOWN),relative@np.array(h.CROSS),base[ring,2]))
check=json.loads((ROOT/'qa/water-hybrid07-motion-check.json').read_text(encoding='utf-8'))
result['normals']={'source':str(hm.OUTPUT),'sha256':digest(hm.OUTPUT),'vertices':len(base),'render_triangles':len(faces),'active_vertices':int(active.sum()),'unchanged_base_cross_magnitude_threshold':1e-9,'bad_union_triangles':len(badtri),'bad_union_vertices':len(badverts),'bad_active_vertices':int(active[badverts].sum()),'one_ring_vertices':len(ring),'one_ring_active_vertices':int(active[ring].sum()),'one_ring_active_fraction':float(active[ring].sum()/active.sum()),'one_ring_world_bounds_m':bounds(base[ring]),'one_ring_along_cross_z_bounds_m':bounds(sc),'fall_weight_nonzero_in_ring':int((fall[ring]>0).sum()),'pond_weight_nonzero_in_ring':int((pond[ring]>0).sum()),'max_frozen_original_displacement_m':dmax,'bad_base_triangle_area_m2':h.stats((length0[badtri]*.5).tolist()),'all_adjacent_triangle_area_m2':float((length0[touch]*.5).sum()),'new_bad_union_count':len(set(newunion)),'matches_existing_evaluated_frame_failure_counts':all(len(framebad[i])==check['frames'][i]['flipped_nondegenerate_triangles'] for i in range(36)),'counterfactual_frames':counter,'counterfactual_only':'Coordinates changed only in NumPy arrays; no object/key/topology or scene files changed; intermediate subframes and new face-interior collision are not tested'}
(ROOT/'qa/water08-readonly-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('WATER08 NORMAL RESULT',json.dumps({k:v for k,v in result['normals'].items() if k!='counterfactual_frames'}),flush=True)
