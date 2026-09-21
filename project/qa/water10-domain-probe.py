"""Read-only real mesh bathymetry/shore/profile and camera sampling. No model change or render."""
import sys,json,hashlib,math,time
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));import hybrid_water as h
SOURCE=ROOT/'scene/Fallingwater_iteration09.blend';P=ROOT/'qa';started=time.perf_counter();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(SOURCE)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.frame_set(48);dep=bpy.context.evaluated_depsgraph_get();cfg=json.loads((ROOT/'data/site.json').read_text(encoding='utf-8'))
ROI=[[-32,10],[-28,8]];prefix=('SITE_Continuous_BearRun_Terrain','SITE_Core_Continuous','SITE_Cascade_Shoulder','SITE_Secondary_Sandstone','SITE_Split_Talus','SITE_Bank_');VV=[];FF=[];owners=[];objects=[]
for o in s.objects:
 if o.type!='MESH' or not o.name.startswith(prefix):continue
 ev=o.evaluated_get(dep);me=ev.to_mesh();me.calc_loop_triangles();v=np.array([tuple(o.matrix_world@p.co) for p in me.vertices]);a=np.stack((v.min(0),v.max(0)),1)
 if any(a[k,1]<ROI[k][0] or a[k,0]>ROI[k][1] for k in (0,1)):ev.to_mesh_clear();continue
 triangles=np.array([tuple(t.vertices) for t in me.loop_triangles]);tt=v[triangles];keep=np.ones(len(tt),bool)
 for k in (0,1):keep&=(tt[:,:,k].max(1)>=ROI[k][0])&(tt[:,:,k].min(1)<=ROI[k][1])
 chosen=triangles[keep];ids=np.unique(chosen);mapping={int(old):i+len(VV) for i,old in enumerate(ids)};VV.extend(v[ids]);FF.extend([tuple(mapping[int(k)] for k in tri) for tri in chosen]);owners.extend([o.name]*len(chosen))
 objects.append({'name':o.name,'world_geometry_sha256':h.shape_hash(o),'raw_aabb':a.tolist(),'triangles_in_probe':len(chosen),'hide_render':o.hide_render});ev.to_mesh_clear()
tree=BVHTree.FromPolygons(VV,FF,all_triangles=True);terrain_obj=s.objects['SITE_Continuous_BearRun_Terrain'];terrain=h.render_bvh(terrain_obj);water_obj=s.objects['WATER_BearRun_Continuous_Upstream_Downstream'];water=h.render_bvh(water_obj)
def ray(tree,x,y):
 q=tree.ray_cast(Vector((float(x),float(y),10)),Vector((0,0,-1)),30);return (float(q[0].z),int(q[2]),float(q[1].z)) if q[0] is not None else (None,None,None)
xs=np.arange(-32,10.001,.25);ys=np.arange(-28,8.001,.25);bed=np.full((len(ys),len(xs)),np.nan);wz=bed.copy();soil=bed.copy();owner=np.full(bed.shape,-1,int);nn=bed.copy()
for j,y in enumerate(ys):
 for i,x in enumerate(xs):
  z,face,n=ray(tree,x,y);bed[j,i]=z if z is not None else np.nan;owner[j,i]=face if face is not None else -1;nn[j,i]=n if n is not None else np.nan
  z,_,_=ray(water,x,y);wz[j,i]=z if z is not None else np.nan;z,_,_=ray(terrain,x,y);soil[j,i]=z if z is not None else np.nan
print('WATER10_GRID_DONE',len(xs)*len(ys),flush=True)
river=cfg['river_path'];profiles=[];arc=0
for idx in range(8,16):
 a=np.array(river[idx][:2]);b=np.array(river[idx+1][:2]);length=float(np.linalg.norm(b-a));down=(b-a)/length;cross=np.array([-down[1],down[0]])
 for u in np.linspace(0,1,max(2,int(math.ceil(length/.5))+1))[:-1]:
  pos=a*(1-u)+b*u;head=river[idx][2]*(1-u)+river[idx+1][2]*u;width=river[idx][3]*(1-u)+river[idx+1][3]*u;row=[]
  for c in np.arange(-12,12.0001,.25):
   xy=pos+cross*c;zz,face,n=ray(tree,*xy);ww,_,_=ray(water,*xy);row.append({'c_m':float(c),'xy':xy.tolist(),'bed_m':zz,'water_m':ww,'bed_owner':owners[face] if face is not None else None,'normal_z':n})
  wet=[x for x in row if x['bed_m'] is not None and x['bed_m']<head];depth=np.array([max(0,head-x['bed_m']) if x['bed_m'] is not None else 0 for x in row]);edge=[]
  for k in range(len(row)-1):
   if (depth[k]>0)!=(depth[k+1]>0):edge.append((row[k]['c_m']+row[k+1]['c_m'])*.5)
  profiles.append({'path_segment':idx,'distance_from_lip_m':arc+length*u,'xy':pos.tolist(),'authored_path_head_m':head,'authored_path_width_m':width,'sampled_wet_width_at_path_head_m':float((depth>0).sum()*.25),'cross_section_area_at_path_head_m2':float(np.trapezoid(depth,dx=.25)),'max_depth_m':float(depth.max()),'center_bed_m':row[48]['bed_m'],'crossing_banks_c_m':edge,'edge_depths_m':[float(depth[0]),float(depth[-1])],'samples':row})
 arc+=length
print('WATER10_PROFILES_DONE',len(profiles),flush=True)
visible=[];cameras=[]
for name in ('CAM_HERO','CAM_WATER_DETAIL','CAM_WATER_FOOT'):
 cam=s.objects.get(name)
 if cam is None:continue
 origin=cam.matrix_world.translation;seen=[];frustum=[];blocked={}
 for j in range(0,len(ys),2):
  for i in range(0,len(xs),2):
   z=wz[j,i]
   if not np.isfinite(z) or z>-5.40:continue
   p=Vector((float(xs[i]),float(ys[j]),float(z)));uv=world_to_camera_view(s,cam,p)
   if not (uv.z>0 and 0<=uv.x<=1 and 0<=uv.y<=1):continue
   frustum.append((float(p.x),float(p.y),float(p.z)));vec=p-origin;hit=s.ray_cast(dep,origin,vec.normalized(),distance=vec.length-.025)
   if not hit[0]:seen.append((float(p.x),float(p.y),float(p.z)))
   else:blocked[hit[4].name]=blocked.get(hit[4].name,0)+1
 def box(pts):
  a=np.array(pts);return np.stack((a.min(0),a.max(0)),1).tolist() if len(a) else None
 cameras.append({'name':name,'position':list(origin),'lens_mm':cam.data.lens,'matrix_world':[list(v) for v in cam.matrix_world],'sample_step_m':.5,'within_frustum_count':len(frustum),'geometrically_unoccluded_count':len(seen),'frustum_water_aabb':box(frustum),'unoccluded_water_aabb':box(seen),'blockers_top12':sorted(blocked.items(),key=lambda p:-p[1])[:12],'visibility_limit':'Actual mesh ray to authored water samples; no transparency/refraction shading simulation or image render','visible_samples':seen})
print('WATER10_VISIBILITY_DONE',flush=True)
r={'status':'READ_ONLY_GEOMETRY_PROBE_COMPLETE_DESIGN_PENDING','source':str(SOURCE),'source_sha256':before,'frame':48,'source_sha256_after':sha(SOURCE),'site_config_sha256':sha(ROOT/'data/site.json'),'frozen_visible_core_expected_sha256':'dd86ff944b6e264b542c77f2e8671a53524fc5092dedcfb6db61d697c7c52768','objects':objects,'world_grid_roi':ROI,'grid_step_m':.25,'grid_shape':list(bed.shape),'profiles':profiles,'cameras':cameras,'no_scenes_saved':True,'no_simulation_or_render':True,'seconds':time.perf_counter()-started}
assert before==r['source_sha256_after'];actual=next(o['world_geometry_sha256'] for o in objects if o['name']=='SITE_Core_Continuous_Fractured_Sandstone');assert actual==r['frozen_visible_core_expected_sha256'],actual
np.savez_compressed(P/'water10-domain-probe-grid.npz',x=xs,y=ys,bed=bed,soil=soil,authored_water=wz,face_index=owner,normal_z=nn,vertices=np.array(VV),faces=np.array(FF));r['face_owners']=owners
(P/'water10-domain-probe.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print('WATER10_PROBE_DONE',json.dumps({'seconds':r['seconds'],'objects':len(objects),'profiles':len(profiles),'cameras':[{k:c[k] for k in ['name','geometrically_unoccluded_count','unoccluded_water_aabb']} for c in cameras]}),flush=True)
