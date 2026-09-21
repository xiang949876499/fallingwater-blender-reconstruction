"""Additional read-only metrics for one finite natural-channel domain."""
import sys,json,hashlib,math,time
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'qa';sys.path.insert(0,str(ROOT/'scripts'));import hybrid_water as h
base=json.loads((P/'water10-domain-probe.json').read_text(encoding='utf-8'));cfg=json.loads((ROOT/'data/site.json').read_text(encoding='utf-8'));g=np.load(P/'water10-domain-probe-grid.npz');x,y,bed=g['x'],g['y'],g['bed'];xx,yy=np.meshgrid(x,y)
river=np.array(cfg['river_path'][9:17],float);river[0,2]=-5.771274;best=np.full(xx.shape,np.inf);head=best.copy();along=head.copy();arc=0
for a,b in zip(river[:-1],river[1:]):
 delta=b[:2]-a[:2];length=np.linalg.norm(delta);u=np.clip(((xx-a[0])*delta[0]+(yy-a[1])*delta[1])/length**2,0,1);dist=np.sqrt((xx-a[0]-u*delta[0])**2+(yy-a[1]-u*delta[1])**2);pick=dist<best
 head[pick]=(a[2]+u*(b[2]-a[2]))[pick];along[pick]=(arc+u*length)[pick];best=np.minimum(best,dist);arc+=length
inbox=(xx>=-16)&(xx<=8)&(yy>=-17)&(yy<=6);wet=inbox&np.isfinite(bed)&(bed<head);seed=(int(np.argmin(abs(y+2.211417675))),int(np.argmin(abs(x-.797341526))));stack=[seed];connected=np.zeros(wet.shape,bool)
while stack:
 j,i=stack.pop()
 if j<0 or i<0 or j>=len(y) or i>=len(x) or connected[j,i] or not wet[j,i]:continue
 connected[j,i]=True;stack.extend([(j-1,i),(j+1,i),(j,i-1),(j,i+1)])
depth=np.maximum(head-bed,0);out={'domain_aabb_m':[[-16,8],[-17,6],[-7.70,-4.95]],'head_definition':'Authored path9-16 stage, firstpool head-5.771274; nearest segment. Measured stage is not hydraulic equilibrium.','grid_step_m':.25,'connected_wet_area_proxy_m2':float(connected.sum()*.25**2),'connected_volume_proxy_m3':float(depth[connected].sum()*.25**2),'connected_bed_min_m':float(bed[connected].min()),'connected_head_minmax_m':[float(head[connected].min()),float(head[connected].max())],'connected_depth_p05_p50_p95_m':np.quantile(depth[connected],[.05,.5,.95]).tolist(),'connected_wet_aabb_xy_m':[[float(xx[connected].min()),float(xx[connected].max())],[float(yy[connected].min()),float(yy[connected].max())]],'grid_connectivity_limit':'Quarter-meter 4-neighbor diagnostic, not a Boolean volume or thin-gap proof. Must build actual complete closed liquid volume and verify before bake.','boundary_sections':[]}
for axis,coord,sign,name in [(0,-16,-1,'x_min'),(0,8,1,'x_max'),(1,-17,-1,'y_min'),(1,6,1,'y_max')]:
 select=connected&(abs((xx if axis==0 else yy)-coord)<1e-8);v=np.array([xx[select],yy[select]]).T
 out['boundary_sections'].append({'face':name,'wet_grid_points':int(select.sum()),'wet_width_proxy_m':float(select.sum()*.25),'wet_area_proxy_m2':float(depth[select].sum()*.25),'bed_min_m':float(bed[select].min()) if select.any() else None,'head_minmax_m':[float(head[select].min()),float(head[select].max())] if select.any() else None,'minimum_distance_to_impact_m':float(np.linalg.norm(v-np.array([.797341526,-2.211417675]),axis=1).min()) if len(v) else None,'wet_xy':v.tolist()})
# Actual source lead-in hydraulic room, using frozen rendered triangles and unchanged authored water.
bpy.ops.wm.open_mainfile(filepath=base['source']);s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.frame_set(48);water=h.render_bvh(s.objects['WATER_BearRun_Continuous_Upstream_Downstream']);tree=BVHTree.FromPolygons(g['vertices'],g['faces'],all_triangles=True)
lead=[]
for distance in [-.8,-.5,-.2]:
 rows=[]
 for c in np.arange(-4.0,1.2001,.025):
  p=h.point(distance,c,10);b=tree.ray_cast(p,Vector((0,0,-1)),20);w=water.ray_cast(p,Vector((0,0,-1)),20);depth0=max(0,w[0].z-b[0].z) if b[0] is not None and w[0] is not None else 0
  rows.append({'cross_m':float(c),'xy':[p.x,p.y],'bed_m':b[0].z if b[0] is not None else None,'water_m':w[0].z if w[0] is not None else None,'available_water_depth_m':depth0})
 a=np.array([r['available_water_depth_m'] for r in rows]);candidate=np.array([abs(v['cross_m']+1.4)<2.30391 for v in rows]);lead.append({'along_m':distance,'sampled_available_area_m2':float(np.trapezoid(a,dx=.025)),'within_proposed4_60782m_width_area_m2':float(np.sum(a[candidate])*.025),'max_depth_m':float(a.max()),'candidate_points_at_least6cm_fraction':float((a[candidate]>=.06).mean()),'flow_at_original1_80604m_s_using_actual_available_area':float(np.sum(a[candidate])*.025*1.806041),'rows':rows})
out['actual_upstream_lead_samples']=lead
np.savez_compressed(P/'water10-domain-proposed-head-grid.npz',x=x,y=y,head=head,bed=bed,connected=connected,along_from_path9=along)
(P/'water10-domain-metrics.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print('WATER10_METRICS',json.dumps({k:v for k,v in out.items() if k!='actual_upstream_lead_samples'}),flush=True);print('WATER10_UPSTREAM',json.dumps([{k:v for k,v in a.items() if k!='rows'} for a in lead]),flush=True)
