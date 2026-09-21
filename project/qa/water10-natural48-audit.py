"""Read-only actual initialized geometry field audit. Never run the liquid solver."""
import sys, json, time
from pathlib import Path
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
import importlib.util
spec=importlib.util.spec_from_file_location('natural48',Path(__file__).with_name('water10-natural48.py'))
w=importlib.util.module_from_spec(spec); spec.loader.exec_module(w)
t=time.perf_counter(); r=json.loads(w.REPORT.read_text(encoding='utf-8'))
assert r['status']=='PREPARE_REOPEN_PASS_NOT_BAKED_GEOMETRY_FIELD_AUDIT_PENDING'
assert w.sha(w.PILOT)==r['prepared_sha256']; bpy.ops.wm.open_mainfile(filepath=str(w.PILOT))
s=bpy.context.scene; s.render.threads_mode='FIXED'; s.render.threads=8
w.validate(r); initial=s.objects[w.INIT]; tree=w.h.render_bvh(initial)
vv=[]; ff=[]; solid_trees=[]
for ob in bpy.data.collections[w.COLL].objects:
    a,b=w.arrays(ob); ff.extend((b+len(vv)).tolist()); vv.extend(a.tolist())
    solid_trees.append((ob.name,BVHTree.FromPolygons(a,b,all_triangles=True),np.stack((a.min(0),a.max(0)),1)))
rock=BVHTree.FromPolygons(vv,ff,all_triangles=True)
def ray(tree,x,y,z=8.,distance=25.):
    hit=tree.ray_cast(Vector((float(x),float(y),float(z))),Vector((0,0,-1)),distance)
    return (float(hit[0].z),float(hit[1].z)) if hit[0] is not None else (float('nan'),float('nan'))
xs=np.arange(w.ROI[0,0]+.075,w.ROI[0,1],.15); ys=np.arange(w.ROI[1,0]+.075,w.ROI[1,1],.15)
xx,yy=np.meshgrid(xs,ys); analytic_stage=w.stage(xx,yy); stage=np.full(xx.shape,np.nan); bed=stage.copy(); top=bed.copy(); bottom=bed.copy(); normals=bed.copy(); column_depth=bed.copy()
# Compare actual initialization to its exact finite triangle stage. Comparing a
# 15cm triangulated heightfield to the untriangulated nearest-segment function at
# 30 micrometres confused interpolation difference with holes; retain that failed
# audit separately, and continue reporting its full height error distribution.
rx=np.linspace(w.ROI[0,0],w.ROI[0,1],161); ry=np.linspace(w.ROI[1,0],w.ROI[1,1],155)
rxx,ryy=np.meshgrid(rx,ry); rz=w.stage(rxx,ryy); rv=np.column_stack((rxx.ravel(),ryy.ravel(),rz.ravel())); rf=[]
for j in range(len(ry)-1):
    for i in range(len(rx)-1):
        a=j*len(rx)+i; b=a+1; c=b+len(rx); d=a+len(rx); rf.extend([(a,b,c),(a,c,d)])
stage_tree=BVHTree.FromPolygons(rv,rf,all_triangles=True)
for j,y in enumerate(ys):
    for i,x in enumerate(xs):
        bed[j,i],_=ray(rock,x,y); stage[j,i],_=ray(stage_tree,x,y)
        z,n=ray(tree,x,y); top[j,i]=z; normals[j,i]=n
        if np.isfinite(z):
            bottom[j,i],_=ray(tree,x,y,z-.0002,5)
            hits=[z]; cursor=z-.00002
            for step in range(20):
                h,_=ray(tree,x,y,cursor,5)
                if not np.isfinite(h):break
                hits.append(h); cursor=h-.00002
            column_depth[j,i]=sum(max(0,a-b) for a,b in zip(hits[::2],hits[1::2])) if len(hits)%2==0 else np.nan
        else: column_depth[j,i]=0
expected_wet=np.isfinite(bed)&(bed<stage-.03)
height_match=np.isfinite(top)&(abs(top-stage)<.00003)
surface=height_match&(normals>.5)
missing=expected_wet&~height_match
steep=expected_wet&height_match&(normals<=.5)
dryrock=np.isfinite(bed)&(bed>stage+.03)
water_below_higher_rock=dryrock&surface
midpoint=np.stack((xx,yy,(stage+bed)*.5),axis=-1)
# Finite inside-voxel probes use real solid parity; they are not a full analytical
# Boolean intersection proof. Exact Boolean topology is recorded independently.
penetration=[]; probes=0
interior_samples=np.argwhere(surface & (stage-bed>.05))[::7].tolist()+np.argwhere(water_below_higher_rock).tolist()
for j,i in interior_samples:
    z=(top[j,i]+bottom[j,i])*.5 if water_below_higher_rock[j,i] else midpoint[j,i,2]
    p=Vector((xx[j,i],yy[j,i],z)); probes+=1
    for name,solid,box in solid_trees:
        if np.all(np.array(p)>=box[:,0]) and np.all(np.array(p)<=box[:,1]):
            counts=w.h.parity(solid,p)
            if sum(n%2 for n in counts)>=2: penetration.append({'solid':name,'xy':[float(xx[j,i]),float(yy[j,i])],'z':float(p.z),'counts':counts})
vertex,face=w.arrays(initial); tris=vertex[face]
e=np.concatenate((face[:,[0,1]],face[:,[1,2]],face[:,[2,0]])); e.sort(1); unique=np.unique(e,axis=0)
chi=len(vertex)-len(unique)+len(face); genus=(2-chi)/2
volume=float(np.einsum('ij,ij->i',tris[:,0]-np.array([0,0,-6]),np.cross(tris[:,1]-np.array([0,0,-6]),tris[:,2]-np.array([0,0,-6]))).sum()/6)
# Closed-cap contact at the real outlet: line integrals of actual top/bottom,
# sampled immediately inside the two domain faces. Dry guards should have no water.
outlets=[]
for axis,coordinate,name,offset in [(0,-16,'x_min',.0025),(0,8,'x_max',-.0025),(1,-17,'y_min',.0025),(1,6,'y_max',-.0025)]:
    tangent=1-axis; values=np.arange(w.ROI[tangent,0]+.01875,w.ROI[tangent,1],.0375)
    segments=[]; row=[]
    for a in values:
        xy=[0.,0.]; xy[axis]=coordinate+offset; xy[tangent]=float(a)
        z,n=ray(tree,*xy); depth=0.
        if np.isfinite(z):
            low,ln=ray(tree,*xy,z-.0002,5)
            if np.isfinite(low): depth=max(0.,z-low)
        row.append({'xy':xy,'water_top_m':z if np.isfinite(z) else None,'depth_m':depth})
    depth=np.array([q['depth_m'] for q in row]); wet=depth>1e-5
    outlets.append({'boundary':name,'actual_inside_offset_m':abs(offset),'sample_step_m':.0375,
                    'sampled_wet_width_m':float(wet.sum()*.0375),'actual_volume_cross_section_proxy_m2':float(depth.sum()*.0375),
                    'minmax_depth_m':[float(depth[wet].min()),float(depth.max())] if wet.any() else None,
                    'samples':row})
initial_box=np.array(w.bounds(initial)); contain=bool(np.all(initial_box[:,0]>=w.ROI[:,0]-2e-5) and np.all(initial_box[:,1]<=w.ROI[:,1]+2e-5))
bad=np.argwhere(missing)
coverage={'grid_shape':list(xx.shape),'probe_spacing_m':.15,'expected_wet_samples_bed_3cm_below_head':int(expected_wet.sum()),
          'actual_surface_samples':int(surface.sum()),'expected_wet_missing_surface_count':int(missing.sum()),
          'expected_wet_matching_head_but_normal_z_le_0_5_count':int(steep.sum()),
          'steep_initial_stage_samples':[{'xy':[float(xx[j,i]),float(yy[j,i])],'head_m':float(top[j,i]),'normal_z':float(normals[j,i])} for j,i in np.argwhere(steep)],
          'missing_samples':[{'xy':[float(xx[j,i]),float(yy[j,i])],'bed_m':float(bed[j,i]),'head_m':float(stage[j,i]),'actual_top_m':float(top[j,i]) if np.isfinite(top[j,i]) else None} for j,i in bad],
          'higher_rock_samples_3cm_above_head':int(dryrock.sum()),'water_head_below_higher_rock_count':int(water_below_higher_rock.sum()),
          'under_higher_rock_points_are_tested_inside_each_solid_not_declared_dry_by_highest_hit':True,
          'surface_stage_max_abs_error_m':float(abs(top[surface]-stage[surface]).max()) if surface.any() else None,
          'free_water_interior_solid_parity_probes':probes,'inside_solid_counterexamples':penetration,
          'analytic_vs_finite_triangle_stage_max_abs_m':float(np.max(abs(stage-analytic_stage))),
          'analytic_vs_finite_triangle_stage_p50_p95_p99_m':np.quantile(abs(stage-analytic_stage),[.5,.95,.99]).tolist(),
          'analytic_vs_finite_triangle_stage_max_abs_in_deep_wet_m':float(abs(stage-analytic_stage)[expected_wet].max()),
          'limits':'Uniform 15cm sample can miss thin branches. Stage comparison is against actual 15cm initial-prism triangulation; analytic stage error reported separately. Exact frozen rock undersides may allow water below higher rock. Authored C stage, not stationary head proof.'}
result={'status':'ACTUAL_PREBAKE_GEOMETRY_FIELD_CHECK_COMPLETE','candidate_sha256':r['prepared_sha256'],
        'actual_initial_volume_m3_triangle_integral':volume,'initial_actual_aabb_m':initial_box.tolist(),'initial_fully_inside_domain':contain,
        'connected_closed_topology':w.h.topology(initial),'euler_characteristic':int(chi),'closed_main_component_genus':genus,
        'rock_islands_do_not_require_fullwidth_water':True,'coverage':coverage,'actual_outlet_sections':outlets,
        'source_real_clearance_min_m':min(a['min_sample_clearance_m'] for a in r['source_collision_checks']),
        'source_section_Q_range_m3_s':[min(q['area_normal_dot_velocity_Q_m3_s'] for q in r['source_actual_ring_sections']),max(q['area_normal_dot_velocity_Q_m3_s'] for q in r['source_actual_ring_sections'])],
        'volume_reconciliation_15cm_column_integral':{'total_actual_multiple_interval_volume_proxy_m3':float(np.nansum(column_depth)*.15**2),
            'highest_bed_only_visible_free_column_volume_proxy_m3':float(np.maximum(stage-bed,0).sum()*.15**2),
            'water_in_columns_where_highest_solid_above_stage_m3':float(np.nansum(column_depth[bed>=stage])*.15**2),
            'under_higher_rock_free_surface_column_volume_proxy_m3':float(np.nansum(column_depth[water_below_higher_rock])*.15**2),
            'odd_vertical_intersection_columns':int((~np.isfinite(column_depth)).sum())},
        'x_max_dry_guard_design_assumption_pass':outlets[1]['actual_volume_cross_section_proxy_m2']<1e-6,
        'initial_stage_has_steep_discontinuity_ramps':bool(steep.any()),
        'head_at_original_impact_reference_xy_m':ray(tree,.797341526,-2.211417675)[0],
        'wet_voxel_equivalent_rough':volume/w.CELL**3,'per_frame_particle_count_NOT_MEASURED':True,'simulation_status':'NOT_RUN',
        'new_cache_files':len([p for p in w.CACHE.rglob('*') if p.is_file()]),'resources':w.resources(),'seconds':time.perf_counter()-t}
w.dump(w.P/'water10-natural48-field-audit.json',result)
np.savez_compressed(w.P/'water10-natural48-initial-field.npz',x=xs,y=ys,stage=stage,analytic_stage=analytic_stage,bed=bed,actual_top=top,actual_bottom=bottom,column_depth=column_depth,expected_wet=expected_wet,actual_surface=surface)
assert contain and not penetration
# Missing deep wet samples are not silently discarded: a full connected volume is
# required. All exceptions need a geometric reason before the preparation passes.
assert missing.sum()==0,coverage
assert w.sha(w.PILOT)==r['prepared_sha256'] and w.sha(w.SOURCE)==r['source_sha256']
assert result['new_cache_files']==0
r['field_audit']='qa/water10-natural48-field-audit.json'
r['x_max_dry_guard_design_assumption_pass']=result['x_max_dry_guard_design_assumption_pass']
r['hydraulic_preflight_failures']=[]
if not result['x_max_dry_guard_design_assumption_pass']:r['hydraulic_preflight_failures'].append('X+ dry-guard assumption false: original frozen rock undersides allow a wet connected section behind higher rocks')
if steep.any():r['hydraulic_preflight_failures'].append('Authored nearest-segment initial stage produces seven steep wet samples from discontinuous segment selection; not a settled water head')
r['status']='PREPARED_REOPEN_GEOMETRY_PASS_HYDRAULIC_PREFLIGHT_FAIL_NOT_BAKED' if r['hydraulic_preflight_failures'] else 'PREPARED_REOPEN_GEOMETRY_PASS_NOT_BAKED_JOIN_VISUAL_UNVERIFIED'
w.dump(w.REPORT,r)
print('W10_FIELD_AUDIT_PASS',json.dumps({k:v for k,v in result.items() if k not in ('coverage','actual_outlet_sections')}),flush=True)
