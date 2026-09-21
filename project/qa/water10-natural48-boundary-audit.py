"""Existing initial water graph and frozen original geometry beyond the X+ face."""
import json, sys, heapq, math, time, importlib.util
from pathlib import Path
import bpy, numpy as np
from mathutils import Vector
spec=importlib.util.spec_from_file_location('natural48',Path(__file__).with_name('water10-natural48.py'))
w=importlib.util.module_from_spec(spec); spec.loader.exec_module(w)
t=time.perf_counter(); r=json.loads(w.REPORT.read_text(encoding='utf-8'))
field=np.load(w.P/'water10-natural48-initial-field.npz'); x,y=field['x'],field['y']; depth=field['column_depth']; ztop=field['actual_top']; wet=depth>1e-5
audit=json.loads((w.P/'water10-natural48-field-audit.json').read_text(encoding='utf-8'))
edge=[p for p in audit['actual_outlet_sections'][1]['samples'] if p['depth_m']>1e-5]
edge_xy=np.array([p['xy'] for p in edge]); edge_xy[:,0]=8.
speed=np.sqrt(9.81*np.maximum(depth,0))
dist=np.full(depth.shape,np.inf); pending=[]
for row in edge:
    j=int(np.argmin(abs(y-row['xy'][1]))); i=len(x)-1
    if not wet[j,i]:continue
    initial=(8-x[i])/max(speed[j,i],math.sqrt(9.81*row['depth_m']))
    if initial<dist[j,i]: dist[j,i]=initial; heapq.heappush(pending,(initial,j,i))
steps=[(a,b) for a in [-1,0,1] for b in [-1,0,1] if a or b]
while pending:
    d,j,i=heapq.heappop(pending)
    if d!=dist[j,i]:continue
    for dj,di in steps:
        jj,ii=j+dj,i+di
        if jj<0 or ii<0 or jj>=len(y) or ii>=len(x) or not wet[jj,ii]:continue
        cost=math.hypot(y[jj]-y[j],x[ii]-x[i])/max(speed[j,i],speed[jj,ii])
        candidate=d+cost
        if candidate<dist[jj,ii]:dist[jj,ii]=candidate;heapq.heappush(pending,(candidate,jj,ii))
maxspeed=float(speed.max()); probe=json.loads((w.P/'water10-domain-probe.json').read_text(encoding='utf-8'))
targets=[]
def query_point(p):
    j=int(np.argmin(abs(y-p[1]))); i=int(np.argmin(abs(x-p[0])))
    distance=float(np.linalg.norm(edge_xy-np.array(p[:2]),axis=1).min())
    return {'xy':list(p[:2]),'nearest_sample_xy':[float(x[i]),float(y[j])],'nearest_sample_wet':bool(wet[j,i]),
            'euclidean_distance_to_Xmax_wet_face_m':distance,'distance_over_global_max_c_seconds':distance/maxspeed,
            'depth_weighted_8neighbor_fastest_oneway_seconds':float(dist[j,i]) if np.isfinite(dist[j,i]) else None}
impact=query_point((.797341526,-2.211417675)); impact['approx_outgoing_then_reflected_roundtrip_seconds']=2*impact['depth_weighted_8neighbor_fastest_oneway_seconds']
for camera in probe['cameras']:
    samples=[query_point(p) for p in camera['visible_samples']]
    rows=[p for p in samples if p['depth_weighted_8neighbor_fastest_oneway_seconds'] is not None]
    targets.append({'camera':camera['name'],'original_geometry_unoccluded_count':len(samples),'samples':samples,
                    'samples_on_current_initialized_water':sum(p['nearest_sample_wet'] for p in samples),
                    'minimum_euclidean_distance_m':min(p['euclidean_distance_to_Xmax_wet_face_m'] for p in samples),
                    'minimum_euclidean_global_c_oneway_seconds':min(p['distance_over_global_max_c_seconds'] for p in samples),
                    'minimum_depth_weighted_oneway_seconds':min(p['depth_weighted_8neighbor_fastest_oneway_seconds'] for p in rows),
                    'minimum_reflected_trip_from_impact_via_boundary_seconds':impact['depth_weighted_8neighbor_fastest_oneway_seconds']+min(p['depth_weighted_8neighbor_fastest_oneway_seconds'] for p in rows)})
print('W10_XMAX_TRAVEL',json.dumps({'impact':impact,'cameras':[{k:v for k,v in a.items() if k!='samples'} for a in targets]}),flush=True)
# Original evaluated terrain and rocks outside the proposed domain, no collision
# closure copies. The frozen scene is only read and no scene is saved here.
assert w.sha(w.SOURCE)==w.CONFIG['source_sha256']; bpy.ops.wm.open_mainfile(filepath=str(w.SOURCE)); s=bpy.context.scene
s.render.threads_mode='FIXED';s.render.threads=8;s.frame_set(48)
terrain=w.h.render_bvh(s.objects['SITE_Continuous_BearRun_Terrain']); rocks=[]
prefix=('SITE_Core_Continuous','SITE_Cascade_Shoulder','SITE_Secondary_Sandstone','SITE_Split_Talus','SITE_Bank_')
ylo=float(edge_xy[:,1].min()); yhi=float(edge_xy[:,1].max())
for o in s.objects:
    if o.type!='MESH' or not o.name.startswith(prefix):continue
    box=np.array(w.h.aabb(o))
    if box[0,1]<7.5 or box[0,0]>20 or box[1,1]<ylo-.2 or box[1,0]>yhi+.2:continue
    rocks.append((o.name,w.h.render_bvh(o),box))
def terrain_z(x,y):
    hit=terrain.ray_cast(Vector((float(x),float(y),10)),Vector((0,0,-1)),30)
    return float(hit[0].z) if hit[0] else None
def water_intervals_at(x,y,head):
    bed=terrain_z(x,y)
    if bed is None or bed>=head:return [],bed,[]
    events=[bed,head]; above=[]
    for name,tree,box in rocks:
        if not(box[0,0]-.001<=x<=box[0,1]+.001 and box[1,0]-.001<=y<=box[1,1]+.001):continue
        hit=tree.ray_cast(Vector((x,y,10)),Vector((0,0,-1)),30)
        if hit[0] is not None and hit[0].z>head:above.append({'name':name,'top_z':float(hit[0].z)})
        origin=Vector((x,y,head+.00001))
        for _ in range(30):
            q=tree.ray_cast(origin,Vector((0,0,-1)),max(0,origin.z-bed))
            if q[0] is None:break
            if bed<q[0].z<head:events.append(float(q[0].z))
            origin=q[0]-Vector((0,0,.00002))
    events=sorted(events); intervals=[]
    for a,b in zip(events[:-1],events[1:]):
        if b-a<1e-5:continue
        p=Vector((x,y,(a+b)*.5)); solid=False
        for _,tree,box in rocks:
            if np.all(np.array(p)>=box[:,0]) and np.all(np.array(p)<=box[:,1]):
                if sum(n%2 for n in w.h.parity(tree,p))>=2:solid=True;break
        if not solid:intervals.append([a,b])
    return intervals,bed,above
sections=[]
for atx in [7.9,8.0,8.25,8.5,9.,10.,12.,14.,16.,20.]:
    rows=[]
    for aty in np.arange(ylo,yhi+.001,.15):
        head=float(w.stage(np.array([atx]),np.array([aty]))[0]); intervals,bed,above=water_intervals_at(float(atx),float(aty),head)
        rows.append({'xy':[float(atx),float(aty)],'C_extended_head_m':head,'terrain_z_m':bed,'water_intervals_m':intervals,'total_water_depth_m':sum(b-a for a,b in intervals),'higher_original_rock':above})
    sections.append({'x_m':atx,'sample_step_y_m':.15,'same_Y_span_as_Xmax_outlet':[ylo,yhi],
                     'wet_width_proxy_m':sum(q['total_water_depth_m']>1e-5 for q in rows)*.15,
                     'cross_section_water_area_proxy_m2':sum(q['total_water_depth_m'] for q in rows)*.15,'samples':rows})
result={'status':'XMAX_EXISTING_GEOMETRY_AND_LINEAR_SHALLOW_WAVE_DIAGNOSTIC_NOT_BAKED',
        'source_sha256':w.sha(w.SOURCE),'candidate_sha256':w.sha(w.PILOT),'initial_zero_velocity':True,
        'depth_15cm_max_m':float(depth.max()),'sqrt_gH_max_m_s':maxspeed,'impact':impact,'camera_targets':targets,
        'outside_Xmax_frozen_geometry_sections':sections,
        'propagation_limits':['Approximate gravity-wave travel, not strict Mantaflow pressure-support bound. Incompressible projection and submerged connected cavities do not guarantee finite causal isolation.',
                              '15cm horizontal graph sums wet vertical intervals, uses faster neighboring c and permits diagonal steps; no damping/under-rock drag assumed. Exact acoustic pipe behavior not modeled.',
                              'Source initial jet6.93m/s is mostly vertical and excluded from initial resting-pool shallow-water c. Subsequent fast horizontal advection must be checked in native frames.',
                              'Open X+ is an explicit C numerical-pressure boundary, not a claim that the real bank is an open outlet.',
                              '48frames span frame1-to48 1.95833s at24fps; full48 nominal2s. Compare raw native boundary/target head curves after any authorized bake.'],
        'seconds':time.perf_counter()-t,'new_bakes':0,'new_renders':0}
w.dump(w.P/'water10-natural48-boundary-audit.json',result)
np.savez_compressed(w.P/'water10-natural48-boundary-wave-time.npz',x=x,y=y,depth=depth,fastest_time_seconds=dist)
assert w.sha(w.SOURCE)==w.CONFIG['source_sha256'];print('W10_BOUNDARY_AUDIT_DONE',json.dumps([{k:v for k,v in a.items() if k!='samples'} for a in sections]),flush=True)
