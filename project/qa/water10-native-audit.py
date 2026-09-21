"""Incremental read-only native cache audit. No bake/render/save/denoising.

Only a fully closed file set behind a later completed frame is eligible during
baking. After the monitored child exits, its final fully readable frame is also
eligible. A partial/corrupt final file set is recorded and skipped.
"""
import sys,json,gzip,struct,time,hashlib,math,importlib.util
from pathlib import Path
import bpy,numpy as np,openvdb
from mathutils import Vector
from mathutils.bvhtree import BVHTree
spec=importlib.util.spec_from_file_location('natural48',Path(__file__).with_name('water10-natural48.py'))
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
P=w.P;CACHE=w.CACHE;PREFIX='water10-native';OUT=P/(PREFIX+'-audit.json')
prepared=json.loads(w.REPORT.read_text(encoding='utf8'))
probe=json.loads((P/'water10-native-probe.json').read_text(encoding='utf8'))
affine=np.array(probe['affine']);assert probe['max_error']<2e-6
FPS=24;JET_Z=-5.64

def dump(path,data):
    Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2,default=lambda v:v.item() if isinstance(v,np.generic) else v.tolist()),encoding='utf8')
def stat(path):s=path.stat();return (s.st_size,s.st_mtime_ns)
def paths(frame):
    return {'config':CACHE/'config'/f'config_{frame:04}.uni','mesh':CACHE/'mesh'/f'fluid_mesh_{frame:04}.bobj.gz',
            'data':CACHE/'data'/f'fluid_data_{frame:04}.vdb','secondary':CACHE/'particles'/f'fluid_particles_{frame:04}.vdb'}
def completed_candidates():
    finished=(P/'water10-natural48-bake-process.json').exists()
    rows=[];latest=0
    for f in range(1,49):
        pp=paths(f)
        if all(p.exists() and p.stat().st_size>0 for p in pp.values()): latest=f
    for f in range(1,latest+1):
        pp=paths(f)
        if not all(p.exists() and p.stat().st_size>0 for p in pp.values()):continue
        if f==latest and not finished:continue
        if any(time.time()-p.stat().st_mtime<8 for p in pp.values()):continue
        rows.append(f)
    return rows,{'monitored_process_finished':finished,'latest_file_set_seen':latest,'eligible_frames':rows,
                 'rule':'Each config+data+mesh+secondary exists and is at least8s old; while baking require a higher frame with all4files; gzip CRC/length/VDB read and size+mtime rechecked. No last actively written frame consumed.'}
def config(path):
    raw=gzip.decompress(path.read_bytes()); assert len(raw)==204 and raw[-4:]==b'C01\0'
    return {'resolution':list(struct.unpack_from('<3i',raw,4)),'dx_internal':struct.unpack_from('<f',raw,16)[0],
            'last_substep_dt_internal':struct.unpack_from('<f',raw,20)[0],'T_internal':struct.unpack_from('<f',raw,196)[0]}
def bobj(path):
    raw=gzip.decompress(path.read_bytes());n=struct.unpack_from('<i',raw,0)[0];v=np.frombuffer(raw,'<f4',count=n*3,offset=4).reshape(-1,3).astype(float)
    offset=4+n*12;nn=struct.unpack_from('<i',raw,offset)[0];offset+=4+nn*12;nf=struct.unpack_from('<i',raw,offset)[0];offset+=4
    f=np.frombuffer(raw,'<i4',count=nf*3,offset=offset).reshape(-1,3).copy();assert offset+nf*12==len(raw)
    return np.column_stack((v,np.ones(n)))@affine,f
def array(path,name,res,dtype):
    g=openvdb.read(str(path),name);a=np.empty(tuple(res)+((3,) if name=='velocity' else ()),dtype);g.copyToArray(a,(0,0,0));return a
def volume(v,f):
    tri=(v-v.mean(0))[f]; return float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6)
def clipped_volume(v,f,zcut,xybox=None):
    # Divergence field F=(0,0,z-zcut) has divergence1. Added vertical clipping
    # caps have nz=0 and the upper zcut cap has Fz=0, so no fictitious cap mesh.
    tri=v[f]; planes=[(2,zcut,-1)]
    if xybox is not None: planes += [(0,xybox[0,0],1),(0,xybox[0,1],-1),(1,xybox[1,0],1),(1,xybox[1,1],-1)]
    allin=np.ones(len(f),bool);allout=np.zeros(len(f),bool)
    for axis,pos,sgn in planes:
        inside=(tri[:,:,axis]-pos)*sgn>=0;allin&=inside.all(1);allout|=(~inside).all(1)
    def contribution(tt):
        return float(((tt[:,:,2].mean(1)-zcut)*np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0])[:,2]*.5).sum())
    total=contribution(tri[allin]); crossing=tri[~allin&~allout]
    for face in crossing:
        polygon=list(face)
        for axis,pos,sgn in planes:
            new=[]
            for a,b in zip(polygon,polygon[1:]+polygon[:1]):
                ia=(a[axis]-pos)*sgn>=0;ib=(b[axis]-pos)*sgn>=0
                if ia:new.append(a)
                if ia!=ib:new.append(a+(b-a)*((pos-a[axis])/(b[axis]-a[axis])))
            polygon=new
            if len(polygon)<3:break
        if len(polygon)>=3:total+=contribution(np.array([[polygon[0],polygon[k],polygon[k+1]] for k in range(1,len(polygon)-1)]))
    return total
def slice_interp(a,k,axis):
    low=int(math.floor(k));t=k-low;assert 0<=low and low+1<a.shape[axis],(k,axis,a.shape)
    return np.take(a,low,axis=axis)*(1-t)+np.take(a,low+1,axis=axis)*t
def integrate(phi,vn,cell,gate=None,sub=4,extent_gate=None):
    out=inn=area=0.
    for i in range(sub):
        u=(i+.5)/sub
        for j in range(sub):
            v=(j+.5)/sub
            def bilinear(a):return (1-u)*(1-v)*a[:-1,:-1]+u*(1-v)*a[1:,:-1]+(1-u)*v*a[:-1,1:]+u*v*a[1:,1:]
            pp=bilinear(phi);vv=bilinear(vn);mask=pp<0
            if gate is not None:
                ii=0 if u<.5 else 1;jj=0 if v<.5 else 1
                mask &= gate[ii:gate.shape[0]-1+ii,jj:gate.shape[1]-1+jj]
            if extent_gate is not None:mask &= extent_gate(u,v)
            factor=cell**2/sub**2;out+=float(np.maximum(vv[mask],0).sum())*factor;inn+=float(np.maximum(-vv[mask],0).sum())*factor;area+=int(mask.sum())*factor
    return {'positive_out_m3_s':out,'negative_out_m3_s':inn,'net_out_m3_s':out-inn,'wet_area_m2':area}
def count_flags(a):
    v,n=np.unique(a,return_counts=True);return {str(int(k)):int(c) for k,c in zip(v,n)}
def source_flux(phi,vel,origin,cell,scale,z,sub=8):
    k=(z-origin[2])/cell;ph=slice_interp(phi,k-.5,2);vv=-slice_interp(vel[:,:,:,2],k,2)*scale
    full=integrate(ph,vv,cell,sub=sub)
    xx=origin[0]+(np.arange(ph.shape[0]-1)+.5)*cell;yy=origin[1]+(np.arange(ph.shape[1]-1)+.5)*cell
    def gate(u,v):return (xx[:,None]+u*cell>.3)&(xx[:,None]+u*cell<1.5)&(yy[None,:]+v*cell>-2.7)&(yy[None,:]+v*cell<-1.65)
    window=integrate(ph,vv,cell,sub=sub,extent_gate=gate)
    return {'world_z_m':z,'subsamples':sub,'full_plane_down_positive':full,'jet_X03_15_Yminus27_minus165':window,
            'outside_jet_window_net_down_m3_s':full['net_out_m3_s']-window['net_out_m3_s']}
def boundary_flux(phi,vel,flags,origin,cell,scale,axis,sign):
    n=phi.shape[axis];p=1 if sign<0 else n-1;inner=1 if sign<0 else n-2;outer=0 if sign<0 else n-1;deeper=2 if sign<0 else n-3
    fi=np.take(flags,inner,axis);fo=np.take(flags,outer,axis);gate=((fo&16)!=0)&((fi&(16|2))==0)
    inn=np.take(phi,inner,axis);deep=np.take(phi,deeper,axis);reset=np.take(phi,outer,axis)
    vv=sign*np.take(vel[:,:,:,axis],p,axis)*scale
    tangents=[a for a in range(3) if a!=axis]
    # Limit removal interfaces to the same below-jet control volume.
    grids=[origin[a]+(np.arange(inn.shape[k]-1)+.5)*cell for k,a in enumerate(tangents)]
    def extent(u,v):
        if tangents[1]==2:return np.broadcast_to((grids[1][None,:]+v*cell<=JET_Z),(len(grids[0]),len(grids[1])))
        return np.ones((len(grids[0]),len(grids[1])),bool)
    methods={}
    for label,ph in [('inner_phi_constant',inn),('inner_phi_linear_extrapolated',1.5*inn-.5*deep),('post_delete_phi_blend_BIASED',.5*(inn+reset))]:
        methods[label]=integrate(ph,vv,cell,gate=gate,sub=4,extent_gate=extent)
    mask=gate&((fi&1)!=0)
    centerz=origin[2]+(np.arange(inn.shape[1])+.5)*cell;mask &= centerz[None,:]<=JET_Z
    methods['inner_Fluid_flag_binary']={'positive_out_m3_s':float(np.maximum(vv[mask],0).sum()*cell**2),
        'negative_out_m3_s':float(np.maximum(-vv[mask],0).sum()*cell**2),'net_out_m3_s':float(vv[mask].sum()*cell**2),'wet_area_m2':int(mask.sum())*cell**2}
    return {'axis':axis,'sign':sign,'MAC_index':p,'actual_removal_interface_world_m':float(origin[axis]+p*cell),
        'geometric_external_face_flux':'UNMEASURED_NOT_SAVED_FOR_XPLUS','interface_gate_cells':int(gate.sum()),
        'inner_flags':count_flags(fi),'outflow_layer_flags':count_flags(fo),'outflow_phi_half_count':int((reset==.5).sum()),
        'methods':methods,'interpretation':'POST_STEP_OUTFLOW_REMOVAL_INTERFACE_FLUX_PROXY; resetOutflow destroys pre-deletion phi/particles; negative outward velocity is not verified replenishment from an external reservoir.'}
def surface_hits(tree,x,y):
    p=Vector((float(x),float(y),-4.8)); hits=[]
    for _ in range(16):
        q=tree.ray_cast(p,Vector((0,0,-1)),4)
        if q[0] is None:break
        hits.append((float(q[0].z),float(q[1].z)));p=q[0]-Vector((0,0,.00002))
    upward=[z for z,n in hits if n>.3]; pool=[z for z,n in hits if n>.3 and z<JET_Z]
    return [hits[0][0] if hits else np.nan,hits[0][1] if hits else np.nan,max(upward) if upward else np.nan,max(pool) if pool else np.nan,len(upward),sum(z>=JET_Z for z in upward)]
def source_ring(v,f,z):
    tt=v[f];cross=tt[(tt[:,:,2].min(1)<z)&(tt[:,:,2].max(1)>z)];edges=[]
    for tri in cross:
        pp=[]
        for a,b in zip(tri,np.roll(tri,-1,axis=0)):
            if (a[2]-z)*(b[2]-z)<0:pp.append(a+(b-a)*((z-a[2])/(b[2]-a[2])))
        if len(pp)==2:edges.append(pp)
    adj={}
    for a,b in edges:
        aa=tuple(np.round(a,5));bb=tuple(np.round(b,5));adj.setdefault(aa,set()).add(bb);adj.setdefault(bb,set()).add(aa)
    remaining=set(adj);components=0
    while remaining:
        todo=[remaining.pop()];components+=1
        while todo:
            for q in adj[todo.pop()]:
                if q in remaining:remaining.remove(q);todo.append(q)
    return {'plane_z_m':z,'segments':len(edges),'components':components,'bad_degree_vertices':sum(len(v)!=2 for v in adj.values()),
        'assembled_upstream_join':False,'status':'NATIVE_CROSS_SECTION_ONLY_NOT_A_COMPOSITE_JOIN'}

frames,eligibility=completed_candidates();assert frames,'No finalized eligible frame yet; wait for the producer, never retry bake'
first_meta=openvdb.read(paths(frames[0])['data'].as_posix(),'phi');res=tuple(first_meta.metadata['file_base_resolution']);cell=float(first_meta.metadata['file_voxel_size'])
assert res==tuple(probe['config']['res']) and abs(cell-.075)<1e-6
origin=affine[3]-.5*cell*np.array(res);gridmax=origin+cell*np.array(res)
times={f:config(paths(f)['config']) for f in frames}
if len(frames)>1:factor=(times[frames[-1]]['T_internal']-times[frames[0]]['T_internal'])/((frames[-1]-frames[0])/FPS)
else:factor=times[frames[0]]['T_internal']/(frames[0]/FPS)
scale=cell*factor;assert 2.49<factor<2.51
bpy.ops.wm.open_mainfile(filepath=str(w.PILOT));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4
iv,iff=w.arrays(s.objects[w.INIT]);initial_tree=BVHTree.FromPolygons(iv,iff,all_triangles=True)
sv,sf=w.arrays(s.objects[w.JET]);src_tree=BVHTree.FromPolygons(sv,sf,all_triangles=True)
centers=[origin[k]+(np.arange(res[k])+.5)*cell for k in range(3)]
source_indices=[]
for i in np.flatnonzero((centers[0]>sv[:,0].min())&(centers[0]<sv[:,0].max())):
 for j in np.flatnonzero((centers[1]>sv[:,1].min())&(centers[1]<sv[:,1].max())):
  for k in np.flatnonzero((centers[2]>sv[:,2].min())&(centers[2]<sv[:,2].max())):
   if all(n%2 for n in w.h.parity(src_tree,Vector((centers[0][i],centers[1][j],centers[2][k])))):source_indices.append((i,j,k))
points=[];groups=[]
views=json.loads((P/'water10-domain-probe.json').read_text(encoding='utf8'))['cameras']
for c in views:
 for q in c['visible_samples']:points.append(q[:2]);groups.append(c['name'])
points.append([.797341526,-2.211417675]);groups.append('ORIGINAL_IMPACT_REFERENCE')
for y in np.arange(-13.4,-11.8,.075):
 for x in np.arange(-4.75,-3.3,.075):points.append([x,y]);groups.append('AUTHORED_INITIAL_STEEP_REGION')
base_initial=np.array([surface_hits(initial_tree,*p) for p in points]);points=np.array(points)
dump(P/'water10-native-head-targets.json',{'xy_m':points.tolist(),'groups':groups,'columns':['first_hit_z','first_hit_normal_z','highest_upward_z','highest_upward_below_source_plane_z','upward_hit_count','upward_hits_at_or_above_source_plane'],
       'initial_geometry_heads':np.where(np.isfinite(base_initial),base_initial,np.nan).tolist(),'not_all_high_hits_are_free_pool_surface':True})
cv=np.array([[origin[0]+cell,origin[0]+(res[0]-1)*cell],[origin[1]+cell,gridmax[1]]])
mapping={'actual_base_resolution':list(res),'cell_m':cell,'mesh_world_affine':affine.tolist(),'mapping_actual_max_error_m':probe['max_error'],
         'solver_origin_world_m':origin.tolist(),'solver_grid_max_world_m':gridmax.tolist(),'internal_time_per_scene_second':factor,'m_s_per_raw_MAC_unit':scale,
         'time_basis':'Actual CRC-validated config T difference across available frames / elapsed24fps scene time; no generic fixed2.5 assertion.',
         'source_interior_cell_indices':source_indices,'control_volume_XY_removal_interfaces_m':cv.tolist(),'source_cut_z_m':JET_Z}
dump(P/'water10-native-mapping.json',mapping)
skipped=[]
for frame in frames:
    dest=P/f'water10-native-frame{frame:04}.json'
    if dest.exists():continue
    pp=paths(frame);before={k:stat(p) for k,p in pp.items()};started=time.perf_counter()
    try:
        cf=config(pp['config']);v,f=bobj(pp['mesh']);ph=array(pp['data'],'phi',res,np.float32);vel=array(pp['data'],'velocity',res,np.float32);flags=array(pp['data'],'flags',res,np.int32)
        # Read metadata from the complete secondary file as a format/completion check;
        # RNA cache_particle_format=UNI did not mean this5.2 build wrote UNI here.
        secondary_meta=[{'name':g.name,'type':g.valueTypeName,'metadata':{k:str(v) for k,v in g.metadata.items()}} for g in openvdb.readAllGridMetadata(str(pp['secondary']))]
        edges=np.concatenate((f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]));edges.sort(1);_,counts=np.unique(edges,axis=0,return_counts=True)
        tree=BVHTree.FromPolygons(v,f,all_triangles=True);heads=np.array([surface_hits(tree,*p) for p in points])
        boundaries={name:boundary_flux(ph,vel,flags,origin,cell,scale,axis,sign) for name,axis,sign in [('Xminus',0,-1),('Yminus',1,-1),('Xplus',0,1)]}
        source_velocity=[]
        for i,j,k in source_indices:
            if ph[i,j,k]<0:
                source_velocity.append([.5*(vel[i,j,k,0]+vel[i+1,j,k,0])*scale,.5*(vel[i,j,k,1]+vel[i,j+1,k,1])*scale,.5*(vel[i,j,k,2]+vel[i,j,k+1,2])*scale])
        qs={str(z):source_flux(ph,vel,origin,cell,scale,z) for z in [-5.62,JET_Z,-5.68]}
        row={'frame':frame,'scene_time_from_frame1_s':(frame-1)/FPS,'native_config':cf,'mesh_vertices':len(v),'mesh_triangles':len(f),
             'mesh_volume_m3':volume(v,f),'mesh_volume_below_source_plane_m3':clipped_volume(v,f,JET_Z),
             'mesh_volume_inside_removal_interfaces_below_source_m3':clipped_volume(v,f,JET_Z,cv),
             'mesh_boundary_edges':int((counts==1).sum()),'mesh_nonmanifold_edges':int((counts!=2).sum()),
             'phi_negative_center_volume_proxy_m3':int((ph<0).sum())*cell**3,'Fluid_flag_center_volume_proxy_m3':int(((flags&1)!=0).sum())*cell**3,
             'source_planes':qs,'outflow_removal_interfaces':boundaries,'source_cell_wet_count':len(source_velocity),
             'source_cell_median_velocity_world_m_s':np.median(source_velocity,axis=0).tolist() if source_velocity else None,
             'source_C_design_velocity_world_m_s':prepared['source_flow']['velocity_coord'],'native_source_ring_at_minus5_35':source_ring(v,f,-5.35),
             'secondary_metadata':secondary_meta,'heads_npz':f'water10-native-heads{frame:04}.npz','groups':{},
             'unassembled_upstream_join':'SOURCE_FLOATING_PARTIAL_FALL_INJECTION; source top-5.176m, lip about-3.05m, no original continuous upstream branch in this scene; stability here cannot pass that join or10seconds',
             'audit_seconds':time.perf_counter()-started}
        for group in sorted(set(groups)):
            mask=np.array(groups)==group;a=heads[mask,3];valid=np.isfinite(a);init=base_initial[mask,3]
            row['groups'][group]={'points':int(mask.sum()),'head_valid_below_source_plane':int(valid.sum()),'head_missing':int((~valid).sum()),
                 'head_median_m':float(np.median(a[valid])) if valid.any() else None,'head_p05_p95_m':np.quantile(a[valid],[.05,.95]).tolist() if valid.any() else None,
                 'raw_delta_from_initial_geometry_median_m':float(np.nanmedian(a-init)) if valid.any() else None,
                 'raw_delta_from_initial_geometry_p05_p95_m':np.nanquantile(a-init,[.05,.95]).tolist() if valid.any() else None,
                 'higher_upward_hits_in_source_band_count':int(heads[mask,5].sum())}
        after={k:stat(p) for k,p in pp.items()};assert before==after,'Producer changed a file during audit'
        row['cache_file_provenance']={k:{'path':str(p.relative_to(w.ROOT)),'bytes':p.stat().st_size,'sha256':w.sha(p)} for k,p in pp.items()}
        assert before=={k:stat(p) for k,p in pp.items()}
        np.savez_compressed(P/row['heads_npz'],xy=points,head_columns=heads,initial_geometry_head_columns=base_initial)
        dump(dest,row);print('WATER10_NATIVE_FRAME',frame,row['mesh_volume_m3'],qs[str(JET_Z)]['full_plane_down_positive']['net_out_m3_s'],flush=True)
    except Exception as e:
        skipped.append({'frame':frame,'error':repr(e),'file_states_before':before});print('WATER10_NATIVE_SKIP',frame,repr(e),flush=True)
        break
rows=[json.loads(p.read_text(encoding='utf8')) for p in sorted(P.glob('water10-native-frame[0-9][0-9][0-9][0-9].json'))]
summary={}
if rows:
    tt=np.array([r['scene_time_from_frame1_s'] for r in rows]);V=np.array([r['mesh_volume_m3'] for r in rows]);CV=np.array([r['mesh_volume_inside_removal_interfaces_below_source_m3'] for r in rows]);qi=np.array([r['source_planes'][str(JET_Z)]['full_plane_down_positive']['net_out_m3_s'] for r in rows])
    integrate_time=lambda q:np.concatenate(([0],np.cumsum((q[1:]+q[:-1])*.5*np.diff(tt))))
    summaries={}
    for method in ['inner_phi_constant','inner_phi_linear_extrapolated','inner_Fluid_flag_binary','post_delete_phi_blend_BIASED']:
        out=np.array([sum(r['outflow_removal_interfaces'][name]['methods'][method]['net_out_m3_s'] for name in ('Xminus','Yminus','Xplus')) for r in rows])
        I=integrate_time(qi);O=integrate_time(out);residual=CV-CV[0]-I+O
        summaries[method]={'source_integral_m3':float(I[-1]),'outflow_proxy_integral_m3':float(O[-1]),'CV_change_m3':float(CV[-1]-CV[0]),'residual_last_m3':float(residual[-1]),'residual_max_abs_m3':float(abs(residual).max()),'NOT_EXACT_CONSERVED_MASS':True}
    summary={'frames':[r['frame'] for r in rows],'first_last_mesh_volume_m3':[float(V[0]),float(V[-1])],'mesh_volume_change_m3':float(V[-1]-V[0]),
        'initial_authored_volume_m3':prepared['initial_connected_topology']['signed_volume_m3'],'frame1_initial_representation_offset_m3':float(V[0]-prepared['initial_connected_topology']['signed_volume_m3']),
        'source_native_Q_f5plus_median_m3_s':float(np.median(qi[min(4,len(qi)-1):])),'source_C_Q_design_m3_s':prepared['source_Q_C_design_m3_s'],
        'all_observed_meshes_closed':all(r['mesh_boundary_edges']==r['mesh_nonmanifold_edges']==0 for r in rows),
        'mass_balance_sensitivities':summaries,'no_detrending_or_lowpass':True,'exact_external_face_flux_and_deleted_mass':'UNMEASURED',
        'native_upstream_join':'NOT_ASSEMBLED','visual_status':'NOT_RENDERED_NOT_PASS'}
out={'status':'PARTIAL_FINALIZED_NATIVE_FRAMES_AUDITED' if len(rows)<48 else 'NATIVE48_RAW_AUDIT_COMPLETE_REVIEW_REQUIRED',
     'eligibility':eligibility,'mapping':mapping,'skipped':skipped,'frame_reports':[f'water10-native-frame{r["frame"]:04}.json' for r in rows],'summary':summary,
     'limitations':['Flux from complete frame snapshots is temporal quadrature, not per-substep discharge.',
       'Outflow phi/particles already deleted at export; single-sided wet area proxies andFluid-bit alternatives bracket representation sensitivity but not exact loss.',
       'X+ geometric external face not stored. Interfaces are one cell inside solver domain, documented by actual flags.',
       'Native source-plane flux is independent of author Q. Whole mesh V and clipped below-source retained CV are separately measured.',
       'Original C initial-stage steep patch and unassembled upstream join remain present; no detrending/filtering or join claim.'],
     'source_links':['https://raw.githubusercontent.com/blender/blender/blender-v5.2-release/extern/mantaflow/preprocessed/grid.cpp',
                     'https://raw.githubusercontent.com/blender/blender/blender-v5.2-release/extern/mantaflow/preprocessed/grid.h',
                     'https://raw.githubusercontent.com/blender/blender/blender-v5.2-release/extern/mantaflow/preprocessed/plugin/extforces.cpp',
                     'https://raw.githubusercontent.com/blender/blender/blender-v5.2-release/intern/mantaflow/intern/strings/liquid_script.h'],
     'new_bakes_by_auditor':0,'renders':0,'production_changed':False}
dump(OUT,out);print('WATER10_NATIVE_BATCH_DONE',json.dumps(summary),flush=True)
