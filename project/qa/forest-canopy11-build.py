import bpy,sys,json,hashlib,time,math
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
ROOT=Path(__file__).resolve().parents[1];Q=ROOT/'qa';sys.path[:0]=[str(ROOT/'scripts'),str(Q)]
import forest_canopy11 as entry
import shrub08_auditlib as audit
SOURCE=ROOT/'scene/Fallingwater_bridge10_endfix.blend';TARGET=ROOT/'scene/Fallingwater_forest_canopy_candidate11a.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE)==entry.SOURCE_SHA256;assert not TARGET.exists()
route_raw=(Q/'bridge10-frozen-route09.json').read_bytes();route=json.loads(route_raw)
(Q/'forest-canopy11-frozen-route.json').write_bytes(route_raw)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;stored=scene.frame_current
report={'status':'RUNNING','source_sha256':sha(SOURCE),'source_frame':stored,'comparison_frame':48,'candidate':str(TARGET),
        'helper_sha256':sha(ROOT/'scripts/forest_canopy11.py'),'route_sha256':hashlib.sha256(route_raw).hexdigest(),'rendered':False,'production_modified':False}
start=time.monotonic()

def new_bvh(asset,matrix,excluded=()):
 v,f,owners=entry.added_geometry(asset,excluded)
 return BVHTree.FromPolygons([matrix@Vector(p) for p in v],f,all_triangles=True),owners

try:
 print('FOREST11 fingerprint before',flush=True);before=audit.snapshot();scene.frame_set(48)
 targetnames={s+suffix for names in entry.SELECTION.values() for s in names for suffix in ('_Branches','_Leaves')}
 assert len(targetnames)==36
 selection=[]
 for i,names in entry.SELECTION.items():
  for name in names:
   leaf=scene.objects[name+'_Leaves'];branch=scene.objects[name+'_Branches'];assert leaf.matrix_world==branch.matrix_world
   assert leaf.data.name==f'TREE_Asset_{i}_Individual_Leaves'
   selection.append({'stem':name,'asset':i,'root':list(leaf.matrix_world.translation),'matrix':[list(r) for r in leaf.matrix_world],
                     'leaf_bounds':audit.bounds(leaf),'branch_bounds':audit.bounds(branch),'leaf_data':leaf.data.name,'branch_data':branch.data.name})
 report['selection']=selection
 physics=[o.name for o in scene.objects if o.type=='MESH' and o.name.startswith(('SITE_Core_','SITE_Cascade_Shoulder_Continuous','WATER_','SITE_Bridge10_','SITE_Path_'))]
 physical_before={n:audit.physical_hash(scene.objects[n]) for n in physics}
 hard=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and o.name.startswith(('MAIN_','GUEST_','SITE_Path_','SITE_Bridge_','SITE_Bridge10_','SITE_Core_','SITE_Cascade_Shoulder_Continuous','SITE_Continuous_BearRun_Terrain'))]
 print('FOREST11 hard BVH',len(hard),flush=True);hardb,hardowners=audit.world_bvh(hard,True)
 tb,_=audit.world_bvh([scene.objects['SITE_Continuous_BearRun_Terrain']],True)
 cameras=[o for o in scene.objects if o.type=='CAMERA']
 # No QA camera is created in the scene. These matrices support the same three
 # proposed render views; every existing scene camera also gets clearance QA.
 axis=Vector((-1,-1.4,1)).normalized();target=Vector((-4,-5.5,-6.325))
 views=[('NATIVE_OVERVIEW',target+axis*45,target,40),('BRIDGE_APPROACH',Vector((27.45,-10.5,1.8)),Vector((27.45,2,.25)),28)]
 loggia=scene.objects['CAM_MAIN_L1_LOGGIA_B']
 viewdefs=[]
 for name,eye,aim,lens in views:viewdefs.append((name,eye,(aim-eye).to_track_quat('-Z','Y'),lens,36))
 viewdefs.append(('CAM_MAIN_L1_LOGGIA_B',loggia.matrix_world.translation.copy(),loggia.matrix_world.to_quaternion(),loggia.data.lens,loggia.data.sensor_width))
 protected=[]
 for name,eye,rot,lens,sensor in viewdefs:
  for y in range(36):
   for x in range(64):
    direction=(rot@Vector((((x+.5)/64-.5)*sensor/lens,((y+.5)/36-.5)*sensor/lens*9/16,-1))).normalized()
    hit,normal,ix,dist=hardb.ray_cast(eye,direction,180)
    if hit is not None and hardowners[ix].startswith('MAIN_'):protected.append((eye,direction,dist,name,x,y,hardowners[ix]))
 report['protected_house_sightlines']={'count':len(protected),'method':'64x36 hard-scene first-hit MAIN rays per specified QA view; conservatively protect even if an unchanged tree might also occlude them','view_counts':dict(Counter(r[3] for r in protected))}
 print('FOREST11 generate',flush=True);assets=[entry.generate(i) for i in entry.SELECTION]
 print('FOREST11 groups',[(a['index'],len(a['groups']),a['rejected_envelope']) for a in assets],flush=True)
 excluded={a['index']:set() for a in assets};reasons=[];empty=BVHTree.FromPolygons([],[])
 for a in assets:
  for name in entry.SELECTION[a['index']]:
   obj=scene.objects[name+'_Leaves'];nb,owners=new_bvh(a,obj.matrix_world)
   # Exact triangle crossings against buildings, terrain, routes and bridge.
   crossed={owners[newface] for oldface,newface in hardb.overlap(nb)}
   for gid in crossed:excluded[a['index']].add(gid);reasons.append([a['index'],gid,name,'HARD_SURFACE_CROSSING'])
   nav=audit.route_regression(route,empty,[],nb,owners)
   for h in nav['new_obstacles']:excluded[a['index']].add(h['after']);reasons.append([a['index'],h['after'],name,'ROUTE_CLEARANCE'])
   for cam in cameras:
    for hit,n,ix,dist in nb.find_nearest_range(cam.matrix_world.translation,.40001):
     excluded[a['index']].add(owners[ix]);reasons.append([a['index'],owners[ix],name,'CAMERA_0_40M'])
   # Also reject a whole added group inside terrain without a surface crossing.
   for g in a['groups']:
    if g['id'] in excluded[a['index']]:continue
    for point in g['branch_v']+g['leaf_v']:
     p=obj.matrix_world@Vector(point);ground=tb.ray_cast(Vector((p.x,p.y,80)),Vector((0,0,-1)),180)[0]
     if ground is not None and p.z-ground.z<=.02001:
      excluded[a['index']].add(g['id']);reasons.append([a['index'],g['id'],name,'NEW_GEOMETRY_TERRAIN_20MM']);break
   for eye,d,length,view,x,y,owner in protected:
    hit,n,ix,dist=nb.ray_cast(eye,d,length-.02)
    if hit is not None:excluded[a['index']].add(owners[ix]);reasons.append([a['index'],owners[ix],name,'PROTECTED_HOUSE_SIGHTLINE'])
  print('FOREST11 pruning',a['index'],len(excluded[a['index']]),flush=True)
 # A first-hit ray can hide further added groups. Iterate only deterministic
 # constraint pruning, without changing the design, seed, density or root.
 for iteration in range(12):
  extra=0
  for a in assets:
   for name in entry.SELECTION[a['index']]:
    nb,owners=new_bvh(a,scene.objects[name+'_Leaves'].matrix_world,excluded[a['index']])
    for eye,d,length,view,x,y,owner in protected:
     hit,n,ix,dist=nb.ray_cast(eye,d,length-.02)
     if hit is not None:
      gid=owners[ix]
      if gid not in excluded[a['index']]:excluded[a['index']].add(gid);extra+=1;reasons.append([a['index'],gid,name,'PROTECTED_HOUSE_SIGHTLINE_LAYER'])
  if not extra:break
 assert not extra,'Sightline pruning did not converge'
 report['pruning']={'excluded_by_asset':{str(k):sorted(v) for k,v in excluded.items()},'events':reasons,'visibility_peel_passes':iteration+1}
 report['application']=entry.apply(assets,excluded)
 print('FOREST11 verify',flush=True);contacts=[];meshchecks=[]
 for a in assets:
  i=a['index'];newleaf=bpy.data.meshes[f'TREE_Forest11_{i}_Individual_Leaves'];newbranch=bpy.data.meshes[f'TREE_Forest11_{i}_Woody_Branches']
  for old,new in ((a['old_leaf'],newleaf),(a['old_branch'],newbranch)):
   assert all(v.co==new.vertices[j].co for j,v in enumerate(old.vertices))
   assert all(tuple(p.vertices)==tuple(new.polygons[j].vertices) for j,p in enumerate(old.polygons))
   new.calc_loop_triangles();assert all(t.area>1e-13 for t in new.loop_triangles)
   meshchecks.append({'mesh':new.name,'source':old.name,'vertices':len(new.vertices),'polygons':len(new.polygons),'triangles':len(new.loop_triangles),
                      'original_vertex_count_unchanged':len(old.vertices),'original_face_count_unchanged':len(old.polygons),'mesh_fingerprint':audit.mesh_fingerprint(new),
                      'one_sided_area_m2':sum(t.area for t in new.loop_triangles)})
  groups=[g for g in a['groups'] if g['id'] not in excluded[i]]
  bv=entry.mesh_bvh(newbranch);anchor_distances=[bv.find_nearest(Vector(g['leaf_v'][k]))[3] for g in groups for k in g['leaf_anchor_indices']]
  assert max(anchor_distances,default=0)<.00001
  for name in entry.SELECTION[i]:
   leaf=scene.objects[name+'_Leaves'];branch=scene.objects[name+'_Branches'];row=next(r for r in selection if r['stem']==name)
   assert [list(r) for r in leaf.matrix_world]==row['matrix'];assert audit.bounds(leaf)==row['leaf_bounds']
   nb,owners=new_bvh(a,leaf.matrix_world,excluded[i]);crossing=hardb.overlap(nb);assert not crossing
   nav=audit.route_regression(route,empty,[],nb,owners);assert not nav['new_obstacles']
   camdist=min(nb.find_nearest(c.matrix_world.translation)[3] for c in cameras);assert camdist>=.4
   assert not any(nb.ray_cast(eye,d,length-.02)[0] is not None for eye,d,length,*_ in protected)
   root=leaf.matrix_world.translation;hit=tb.ray_cast(Vector((root.x,root.y,80)),Vector((0,0,-1)),180)[0];assert hit is not None
   actual_v,_,_=entry.added_geometry(a,excluded[i]);gaps=[]
   for point in actual_v:
    p=leaf.matrix_world@Vector(point);ground=tb.ray_cast(Vector((p.x,p.y,80)),Vector((0,0,-1)),180)[0]
    if ground is not None:gaps.append(p.z-ground.z)
   # Existing rooted geometry is unchanged; new crown elements must stay above ground.
   assert min(gaps)>.02,(name,min(gaps))
   contacts.append({'name':name,'root':list(root),'root_to_actual_terrain_m':root.z-hit.z,'new_vertices_terrain_gap_min_m':min(gaps),
                    'new_leaf_anchor_to_branch_max_local_m':max(anchor_distances,default=0),'nearest_existing_camera_m':camdist,
                    'route_rays':nav['ray_count'],'new_route_hits':0,'hard_intersection_pairs':0,'protected_house_sightline_new_hits':0,'leaf_world_bounds_unchanged':True})
  print('FOREST11 verified asset',i,flush=True)
 report['mesh_checks']=meshchecks;report['contacts']=contacts;report['protected_physics']=physical_before
 assert physical_before=={n:audit.physical_hash(scene.objects[n]) for n in physics}
 scene.frame_set(stored);print('FOREST11 fingerprint after',flush=True);after=audit.snapshot();changed=audit.compare_snapshots(before,after,targetnames);assert set(changed)==targetnames
 report.update({'status':'PHYSICAL_PASS_VISUAL_NOT_RUN','all_non_targets_unchanged':True,'target_objects':sorted(targetnames),'changed_count':len(changed),'object_count':len(before['objects']),
                'global_fingerprint_unchanged':True,'old_meshes_unchanged':True,'root_transforms_unchanged':True,'tree_count_unchanged':True,'material_changes':False,'camera_changes':False})
 compact={'snapshot_sha256':audit.digest(after),'objects':{k:audit.digest(v) for k,v in after['objects'].items()},'global':audit.digest(after['global']),'meshes':after['meshes']}
 (Q/'forest-canopy11-fingerprint.json').write_text(json.dumps(compact,separators=(',',':')),encoding='utf-8')
 (Q/'forest-canopy11-approved-groups.json').write_text(json.dumps({'source_sha256':entry.SOURCE_SHA256,'selection':selection,'excluded_by_asset':{str(k):sorted(v) for k,v in excluded.items()}},indent=2),encoding='utf-8')
 assert sha(SOURCE)==entry.SOURCE_SHA256;bpy.ops.wm.save_as_mainfile(filepath=str(TARGET),compress=True);report['candidate_sha256']=sha(TARGET)
except Exception as e:report['status']='FAILED_NO_PRODUCTION_INTEGRATION';report['exception']=repr(e);raise
finally:
 report['elapsed_s']=time.monotonic()-start;(Q/'forest-canopy11-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('FOREST11_RESULT',report['status'],report.get('exception'),report['elapsed_s'],flush=True)
