"""Select fixed existing roots by photo-located bank groups; reject unsafe swaps."""
import bpy,json,hashlib,sys,re,math,time
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
R=Path(__file__).resolve().parents[1];Q=R/'qa';sys.path[:0]=[str(R/'scripts'),str(Q)]
import understory_detail as accepted
import shrub08_auditlib as audit
P=R/'scene/Fallingwater_navigation_candidate11a.blend';SHA='d66ded0f23b7d19c20b81d2f59f94aa5aa77747be4568e85e1d105395fc219ff'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P)==SHA
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;s.frame_set(48);dep=bpy.context.evaluated_depsgraph_get()
start=time.monotonic()
site_path=Q/'bank08-frozen-context/data/site.json'
inputs={k.replace('\\','/'):v for k,v in json.loads(bpy.data.texts['FW_BUILD_INPUTS.json'].as_string()).items()}
assert sha(site_path)==inputs['data/site.json']
site=json.loads(site_path.read_text());exclusion=next(x for x in site['building_exclusions'] if x['name']=='main_plunge_and_stair')
route_raw=(Q/'integration11-navigation-workspace/data/tour-route.json').read_bytes();route=json.loads(route_raw)
(Q/'forest-undergrowth13-frozen-route.json').write_bytes(route_raw)
(Q/'forest-undergrowth13-frozen-site.json').write_bytes(site_path.read_bytes())
zones=[{'name':'hero_west_bank','center':[-15,3],'radii':[11,14]},
       {'name':'hero_south_bank','center':[8,-13],'radii':[10,13]},
       {'name':'loggia_east_bank','center':[28,13],'radii':[11,13]},
       {'name':'overview_near_slope','center':[15,22],'radii':[10,12]}]
protected={r['name'] for r in accepted.APPROVED['objects']}
original16={r['name']:{'matrix':[list(x) for x in s.objects[r['name']].matrix_world],'signature':accepted.mesh_signature(s.objects[r['name']].data)} for r in accepted.APPROVED['objects']}
for r in accepted.APPROVED['objects']:
 assert accepted._matrix_error(s.objects[r['name']].matrix_world,r['matrix'])<1e-6
 assert original16[r['name']]['signature']==r['new_signature']
def geometry(mesh,matrix):
 vv=[matrix@v.co for v in mesh.vertices];ff=[tuple(p.vertices) for p in mesh.polygons]
 return vv,ff,BVHTree.FromPolygons(vv,ff)
terrain,_=audit.world_bvh([s.objects['SITE_Continuous_BearRun_Terrain']],True)
paths=[o for o in s.objects if o.type=='MESH' and o.name.startswith(('SITE_Path_','SITE_Bridge'))]
path_tree,_=audit.world_bvh(paths,True)
edge_segments=[]
for ob in paths:
 vv=[ob.matrix_world@v.co for v in ob.data.vertices]
 counts=Counter(tuple(sorted((a,b))) for p in ob.data.polygons for a,b in zip(list(p.vertices),list(p.vertices)[1:]+list(p.vertices)[:1]))
 edge_segments.extend((ob.name,vv[a],vv[b]) for (a,b),n in counts.items() if n==1)
def boundary_gap(root):
 best=(float('inf'),None)
 for name,a,b in edge_segments:
  dx,dy=b.x-a.x,b.y-a.y;t=max(0,min(1,((root.x-a.x)*dx+(root.y-a.y)*dy)/max(1e-12,dx*dx+dy*dy)))
  distance=math.hypot(root.x-a.x-t*dx,root.y-a.y-t*dy)
  if distance<best[0]:best=(distance,name)
 return best
def ground_gap(point):
 hit=terrain.ray_cast(Vector((point.x,point.y,100)),Vector((0,0,-1)),250)[0]
 return point.z-hit.z if hit is not None else float('-inf')
hard=[o for o in s.objects if o.type=='MESH' and not o.hide_render and o.name.startswith(('MAIN_','GUEST_','FW_MASONRY_','MASONRY','SITE_','WATER_')) and o.name!='SITE_Continuous_BearRun_Terrain']
hard_bounds={o.name:audit.bounds(o) for o in hard};hard_cache={}
cameras=[o for o in s.objects if o.type=='CAMERA'];assert len(cameras)==131
positions=[];position_walk=[];position_labels=[]
for name,segs in ((route['main_camera'],route['main_segments']),(route['supplemental_camera'],route['supplemental_segments'])):
 cam=s.objects[name];assert not cam.parent and not cam.constraints and not cam.animation_data.drivers
 curves=[c for layer in cam.animation_data.action.layers for strip in layer.strips for bag in strip.channelbags for c in bag.fcurves]
 curve={(c.data_path,c.array_index):c for c in curves}
 assert all(k.interpolation=='LINEAR' for c in curves for k in c.keyframe_points)
 for seg in segs:
  walk=bool(seg.get('body_clearance_tested',seg['mode'].startswith('NORMAL')))
  for f in range(seg['start_frame'],seg['end_frame']+1):
   positions.append([curve['location',i].evaluate(f) for i in range(3)])
   position_walk.append(walk);position_labels.append([name,seg['id'],f])
assert len(positions)==7584
film=np.asarray(positions);film_walk=np.asarray(position_walk)
# Preserve coarse rays to currently visible architecture/rock. Extra foliage
# may fill bare terrain pixels but must not hide unfinished visible building.
overview=json.loads((Q/'forest-undergrowth13-source-probe.json').read_text())['overview_image_external_override']
viewrays=[];protected_prefix=('MAIN_','GUEST_','MASONRY','FW_MASONRY_','SITE_Core_','SITE_Cascade_','SITE_Bridge')
for name in ('CAM_HERO','CAM_MAIN_OVERVIEW','CAM_MAIN_L1_LOGGIA_B'):
 cam=s.objects[name]
 if name=='CAM_MAIN_OVERVIEW':
  eye=Vector(overview['location']);look=(Vector(overview['target'])-eye).normalized();right=look.cross(Vector((0,0,1))).normalized();up=right.cross(look).normalized()
  half=cam.data.sensor_width/(2*overview['lens']);vhalf=half*720/1280
  make_direction=lambda x,y:(look+right*((x/1280-.5)*2*half)+up*((.5-y/720)*2*vhalf)).normalized()
 else:
  eye=cam.matrix_world.translation.copy();corners=cam.data.view_frame(scene=s);mat=cam.matrix_world.to_3x3()
  make_direction=lambda x,y:(mat@(corners[3]+(corners[0]-corners[3])*(x/1280)+(corners[2]-corners[3])*(y/720))).normalized()
 for y in range(16,720,32):
  for x in range(16,1280,32):
   direction=make_direction(x,y);hit,point,normal,idx,ob,m=s.ray_cast(dep,eye,direction,distance=150)
   if hit and ob.name.startswith(protected_prefix):viewrays.append((name,[x,y],eye.copy(),direction.copy(),(point-eye).length-.02,ob.name))
print('UNDERGROWTH13 view_rays',len(viewrays),'hard_objects',len(hard),'film',len(film),flush=True)
asset_data={}
for index in (2,3):
 row=accepted.APPROVED['assets'][str(index)]
 branch=bpy.data.meshes[row['new_branch_mesh']];leaf=bpy.data.meshes[row['new_leaf_mesh']]
 assert accepted.mesh_signature(branch)==row['new_branch_signature'] and accepted.mesh_signature(leaf)==row['new_leaf_signature']
 local=BVHTree.FromPolygons([v.co for v in branch.vertices],[tuple(p.vertices) for p in branch.polygons])
 assert len(leaf.vertices)==row['leaf_count']*11
 contact=max(local.find_nearest(leaf.vertices[i].co)[3] for i in range(0,len(leaf.vertices),11));assert contact<1e-5
 asset_data[index]=(branch,leaf,row,contact)
candidates=[];not_selected=[]
for leaf in s.objects:
 match=re.fullmatch(r'TREE_Understory_(\d{4})_Leaves',leaf.name)
 if not match or leaf.name in protected or leaf.data.name not in ('TREE_Understory_2_Leaves','TREE_Understory_3_Leaves'):continue
 root=leaf.matrix_world.translation
 scores=[(1-((root.x-z['center'][0])/z['radii'][0])**2-((root.y-z['center'][1])/z['radii'][1])**2,z['name']) for z in zones]
 score,zone=max(scores)
 if score<=0:continue
 probability=.25+.75*min(1,score/.25)
 stable=int(hashlib.sha256(('FW13:'+leaf.name).encode()).hexdigest()[:8],16)/0xffffffff
 if stable>probability:not_selected.append({'object':leaf.name,'zone':zone,'reason':'SOFT_EDGE_RETAIN_OLD','score':score});continue
 candidates.append((score,zone,leaf.name))
candidates.sort(reverse=True)
selection=[];rejected=[];checks=[]
for index,(score,zone,name) in enumerate(candidates):
 leaf=s.objects[name];branch=s.objects[name.replace('_Leaves','_Branches')];root=leaf.matrix_world.translation
 asset=int(leaf.data.name.split('_')[2]);new_b,new_l,asset_meta,petiole_local=asset_data[asset]
 assert branch.matrix_world==leaf.matrix_world and not leaf.modifiers and not branch.modifiers
 assert branch.data.name==asset_meta['old_branch_mesh']
 vv_b,ff_b,b_tree=geometry(new_b,leaf.matrix_world);vv_l,ff_l,l_tree=geometry(new_l,leaf.matrix_world)
 vertices=vv_b+vv_l;bb=[f(v[i] for v in vertices) for i in range(3) for f in (min,max)]
 radial=max(math.hypot(v.x-root.x,v.y-root.y) for v in vertices)
 r={'leaf_object':name,'asset':asset,'root':list(root),'zone':zone,'score':score,'failures':[],'new_bounds':bb}
 rootgap=ground_gap(root);r['root_anchor_gap_m']=rootgap
 if abs(rootgap+.012)>.00005:r['failures'].append('EXISTING_ROOT_NOT_ON_ACTUAL_TERRAIN')
 x0,x1,y0,y1=exclusion['bbox']
 if bb[0]<=x1 and bb[1]>=x0 and bb[2]<=y1 and bb[3]>=y0:r['failures'].append('MAIN_PLUNGE_STAIR_EXCLUSION')
 edge,path_name=boundary_gap(root);r['nearest_path_boundary']=[path_name,edge];r['crown_radius_m']=radial
 if edge-radial<.15:r['failures'].append('PATH_BOUNDARY_CROWN_CLEARANCE')
 if path_tree.ray_cast(Vector((root.x,root.y,100)),Vector((0,0,-1)),250)[0] is not None:r['failures'].append('ROOT_IN_PATH_PROJECTION')
 # Every currently saved camera, plus exact film eye/body positions, gets a
 # local actual-mesh test. Fast world bounds only cull distant positions.
 vtree=BVHTree.FromPolygons(vertices,ff_b+[tuple(len(vv_b)+i for i in f) for f in ff_l])
 distances=[(c.name,vtree.find_nearest(c.matrix_world.translation)[3]) for c in cameras]
 r['nearest_saved_camera']=min(distances,key=lambda x:x[1])
 if r['nearest_saved_camera'][1]<.5:r['failures'].append('SAVED_CAMERA_CLEARANCE')
 near=np.flatnonzero((film[:,0]>bb[0]-.6)&(film[:,0]<bb[1]+.6)&(film[:,1]>bb[2]-.6)&(film[:,1]<bb[3]+.6)&(film[:,2]>bb[4]-.5)&(film[:,2]<bb[5]+2.2))
 film_bad=[];nearest_film=float('inf')
 for ix in near:
  point=Vector(film[ix]);distance=vtree.find_nearest(point)[3];nearest_film=min(nearest_film,distance)
  bad=distance<.3
  if film_walk[ix]:
   for dx,dy in ((0,0),(-.18,0),(.18,0),(0,-.18),(0,.18)):
    eye=point+Vector((dx,dy,-1.51))
    if vtree.ray_cast(eye,Vector((0,0,1)),1.62)[0] is not None:bad=True
  if bad:film_bad.append(position_labels[ix])
 r['near_film_samples_tested']=len(near);r['film_eye_min_near_m']=nearest_film if near.size else None;r['film_conflicts']=film_bad[:8]
 if film_bad:r['failures'].append('CURRENT_FILM_EYE_OR_BODY_CLEARANCE')
 # Rejecting a root leaves its old shape; no per-instance trimming is allowed.
 if not r['failures']:
  gaps=[ground_gap(v) for v in vv_l]+[ground_gap(leaf.matrix_world@p.center) for p in new_l.polygons]
  r['leaf_terrain_gap_min_m']=min(gaps)
  if min(gaps)<.012:r['failures'].append('LEAF_TERRAIN_CLEARANCE')
  bs=[(v.co.z,ground_gap(leaf.matrix_world@v.co)) for v in new_b.vertices]
  bs += [(p.center.z,ground_gap(leaf.matrix_world@p.center)) for p in new_b.polygons]
  basal=[g for z,g in bs if z<=.080];above=[g for z,g in bs if z>.080]
  r['branch_basal_gap_minmax_m']=[min(basal),max(basal)];r['branch_above_basal_min_m']=min(above)
  if min(basal)<-.060 or min(basal)>.002:r['failures'].append('ROOT_BASE_CONTACT')
  if min(above)<.002:r['failures'].append('ABOVE_BASAL_BRANCH_BURIED')
  leaf_hits=terrain.overlap(l_tree);branch_hits=terrain.overlap(b_tree)
  nonbasal=[b for a,b in branch_hits if min(new_b.vertices[i].co.z for i in new_b.polygons[b].vertices)>.080]
  r['terrain_intersections']={'leaf':len(leaf_hits),'branch_nonbasal':len(nonbasal),'basal_allowed':len(branch_hits)-len(nonbasal)}
  if leaf_hits or nonbasal:r['failures'].append('ACTUAL_TERRAIN_INTERSECTION')
 if not r['failures']:
  tested=[];overlaps=[]
  for ob in hard:
   if not audit.box_overlap(bb,hard_bounds[ob.name],expand=.10):continue
   tree=hard_cache.get(ob.name)
   if tree is None:tree,_=audit.world_bvh([ob],True);hard_cache[ob.name]=tree
   tested.append(ob.name);hits=tree.overlap(vtree)
   if hits:overlaps.append([ob.name,len(hits)])
  r['hard_objects_tested']=tested;r['hard_overlaps']=overlaps
  if overlaps:r['failures'].append('HARD_BUILDING_ROCK_WATER_INTERSECTION')
 if not r['failures']:
  path_gap=min(path_tree.find_nearest(v)[3] for v in vertices);r['actual_path_vertex_clearance_m']=path_gap
  if path_gap<.15:r['failures'].append('PATH_ACTUAL_MESH_CLEARANCE')
 if not r['failures']:
  occluded=[]
  for cam,px,eye,direction,length,owner in viewrays:
   if vtree.ray_cast(eye,direction,length)[0] is not None:occluded.append([cam,px,owner])
  r['visible_building_or_rock_occlusions']=occluded[:8]
  if occluded:r['failures'].append('NEW_VISIBLE_BUILDING_OR_ROCK_OCCLUSION')
 r['leaf_petiole_contact_upper_bound_m']=petiole_local*max(leaf.scale)
 checks.append(r)
 if r['failures']:rejected.append(r)
 elif len(selection)>=240:rejected.append(dict(r,failures=['INSTANCE_BUDGET_RETAIN_OLD']))
 else:
  selection.append({'leaf_object':name,'branch_object':branch.name,'asset':asset,'root':list(root),'matrix':[list(a) for a in leaf.matrix_world],
     'scale':list(leaf.scale),'zone':zone,'selection_score':score,'branch_old_mesh':branch.data.name,'leaf_old_mesh':leaf.data.name,
     'branch_old_signature':accepted.mesh_signature(branch.data),'leaf_old_signature':accepted.mesh_signature(leaf.data)})
 if index%20==0:print('UNDERGROWTH13 preflight',index+1,'of',len(candidates),'accepted',len(selection),'rejected',len(rejected),flush=True)
triangles=sum(accepted.APPROVED['assets'][str(r['asset'])]['total_triangles'] for r in selection)
assert len(selection)>0 and len(selection)<=240 and triangles<=1200000
assert all([list(a) for a in s.objects[n].matrix_world]==r['matrix'] and accepted.mesh_signature(s.objects[n].data)==r['signature'] for n,r in original16.items())
out={'status':'PASS_PREFLIGHT_NATIVE_REPLACEMENT_PLAN','source':str(P),'source_sha256':SHA,'frame':48,'selection':selection,
     'candidate_root_count':len(candidates),'selected_root_count':len(selection),'rejected_root_count':len(rejected),
     'soft_edge_kept_old':not_selected,'zones':zones,'physical_checks':checks,'rejected':rejected,
     'rejection_counts':dict(Counter(reason for r in rejected for reason in r['failures'])),
     'selected_zone_counts':dict(Counter(r['zone'] for r in selection)),
     'instance_triangles_after':triangles,'instance_triangles_before':len(selection)*754,'net_instance_triangles_added':triangles-len(selection)*754,
     'camera_count':131,'movie_position_count':7584,'visible_architecture_rock_protection_rays':len(viewrays),
     'frozen_route_sha256':hashlib.sha256(route_raw).hexdigest(),'frozen_site_sha256':sha(site_path),
     'accepted16':original16,'source_terrain_material':[m.name for m in s.objects['SITE_Continuous_BearRun_Terrain'].data.materials],
     'source_current_saved_camera_matrices':{c.name:[list(r) for r in c.matrix_world] for c in cameras},
     'overview_external_comparison_settings':overview,'source_images':[
       'renders/previews/integration11a/CAM_HERO.png','renders/previews/integration11a/CAM_MAIN_OVERVIEW.png',
       'qa/forest-canopy11-source-official-classic.jpg','qa/forest-canopy11-source-official-east.jpg'],
     'scope':'C photographic-bank zones and exact authored root locations; cultivar U. No blanket forest/terrain/architecture change.',
     'seconds':time.monotonic()-start,'saved':False,'rendered':False,'source_unchanged':sha(P)==SHA}
(Q/'forest-undergrowth13-plan.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:out[k] for k in ('status','selected_root_count','candidate_root_count','selected_zone_counts','rejection_counts','instance_triangles_after','net_instance_triangles_added','seconds')},indent=2))
