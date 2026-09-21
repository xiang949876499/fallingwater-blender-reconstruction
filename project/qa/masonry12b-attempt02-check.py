import bpy,sys,json,hashlib,time,math
from pathlib import Path
from types import SimpleNamespace
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];Q=R/'qa';sys.path[:0]=[str(R/'scripts'),str(Q)]
import masonry_tower12b as entry
import masonry_tower12 as base
import shrub08_auditlib as audit
SOURCE=R/'scene/Fallingwater_masonry_tower_candidate12a.blend';SHA='b267636a9cbbe297513968f08f3b85930c0302cae1ebb75ed775043250e11a48'
TARGET=R/'scene/Fallingwater_masonry_tower_candidate12b.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE)==SHA and not TARGET.exists()
raw=(Q/'masonry12-frozen-route.json').read_bytes();route=json.loads(raw)
(Q/'masonry12b-frozen-route.json').write_bytes(raw)
report={'status':'RUNNING','source':str(SOURCE),'source_sha256':SHA,'candidate':str(TARGET),'frame':48,'rendered':False,'route_sha256':hashlib.sha256(raw).hexdigest(),
        'helper_sha256':sha(R/'scripts/masonry_tower12b.py'),'auditlib_sha256':sha(Q/'shrub08_auditlib.py')}
start=time.monotonic()
try:
 bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;s.frame_set(48);bpy.context.view_layer.update()
 print('MASONRY12b snapshot source',flush=True);before=audit.snapshot();old,_oldowners=audit.world_bvh([s.objects[n] for n in entry.LOWER+entry.MODIFIED],True)
 physics=[o.name for o in s.objects if o.type=='MESH' and o.name.startswith(('SITE_Core_','SITE_Cascade_Shoulder_Continuous','WATER_','SITE_Bridge10_','SITE_Path_','SITE_Continuous_BearRun_Terrain'))]+list(entry.LOWER)
 physical_before={n:audit.physical_hash(s.objects[n]) for n in physics}
 report['application']=entry.build(SimpleNamespace(root=R));app=report['application'];print('MASONRY12b generated',app['component_count'],app['triangles'],flush=True)
 newobjects=[s.objects[n] for n in app['added']];new,newowners=audit.world_bvh(newobjects,True)
 changed=[s.objects[n] for n in app['added']+list(entry.MODIFIED)+list(entry.LOWER)];navigation_new,navigation_owners=audit.world_bvh(changed,True)
 report['repeat']=entry.build(SimpleNamespace(root=R));assert report['repeat']['status']=='SKIPPED_ALREADY_APPLIED'
 # Closed oriented native components, pairwise inter-component surface check.
 component_checks=[];allv=[];allf=[];face_components=[]
 substrate,_=audit.world_bvh([s.objects['MAIN_stone_tower_west']],True)
 for ob in newobjects:
  for c in app['components'][ob.name]:
   st,n=c['vertex_start'],c['vertex_count'];fs,fn=c['face_start'],c['face_count']
   vv=[ob.matrix_world@v.co for v in list(ob.data.vertices)[st:st+n]];ff=[tuple(i-st for i in p.vertices) for p in list(ob.data.polygons)[fs:fs+fn]]
   edges=Counter(tuple(sorted((a,b))) for f in ff for a,b in zip(f,f[1:]+f[:1]));bad=[k for k,v in edges.items() if v!=2]
   areas=[(vv[b]-vv[a]).cross(vv[d]-vv[a]).length*.5 for a,b,d in ff]
   volume=sum(vv[a].dot(vv[b].cross(vv[d]))/6 for a,b,d in ff)
   assert not bad and min(areas)>1e-10 and volume>1e-9,(ob.name,c['id'],bad,min(areas),volume)
   mids=[];ring=c['footprint'];mz=sum(c['z_interval'])/2
   for p,q in zip(ring,ring[1:]+ring[:1]):
    # Hidden backing segments sit just within the original substrate in XY.
    if all(entry.X0-1e-6<=a<=entry.X1+1e-6 and entry.Y0-1e-6<=b<=entry.Y1+1e-6 for a,b in (p,q)):
     point=Vector(((p[0]+q[0])/2,(p[1]+q[1])/2,mz));hit,normal,idx,d=substrate.find_nearest(point)
     mids.append({'point':list(point),'nearest_surface':list(hit),'signed_gap_m':(point-hit).dot(normal),'distance_m':d})
   assert mids and any(-.0011<x['signed_gap_m']<-.0005 for x in mids),(c['id'],'no actual substrate contact',mids)
   component_checks.append({'object':ob.name,'id':c['id'],'vertices':n,'triangles':fn,'bad_edges':len(bad),'min_area_m2':min(areas),'volume_m3':volume,'actual_back_contacts':mids})
   off=len(allv);allv+=vv;allf.extend(tuple(off+i for i in f) for f in ff);face_components += [c['id']+ob.name]*len(ff)
 whole=BVHTree.FromPolygons(allv,allf,all_triangles=True)
 pairs=whole.overlap(whole);cross=[(a,b) for a,b in pairs if a<b and face_components[a]!=face_components[b]]
 report['cross_component_intersections']=cross[:30];assert not cross
 # All original non-target nearby mesh triangles, including windows and roof.
 near=[s.objects[c['name']] for c in app['actual_source_constraints']]
 neighbors,owners=audit.world_bvh(near,True);cross=neighbors.overlap(new)
 report['neighbor_intersections']=[{'source':owners[a],'target':newowners[b]} for a,b in cross[:30]];assert not cross
 report['component_checks']=component_checks

 # Check actual new high-volume surfaces against every saved neighboring mesh,
 # including vegetation. Clip structural wall triangles above their old top;
 # old lower window/wall contacts are outside this newly extended volume.
 def clip_above(poly,z):
  out=[]
  for a,b in zip(poly,poly[1:]+poly[:1]):
   ina=a.z>=z;inb=b.z>=z
   if ina:out.append(a)
   if ina!=inb:out.append(a+(b-a)*((z-a.z)/(b.z-a.z)))
  return out
 highv=[];highf=[]
 dep=bpy.context.evaluated_depsgraph_get()
 for name in entry.MODIFIED:
  ob=s.objects[name];ev=ob.evaluated_get(dep);mesh=ev.to_mesh();mesh.calc_loop_triangles()
  verts=[ev.matrix_world@v.co for v in mesh.vertices]
  for tri in mesh.loop_triangles:
   polygon=[verts[i] for i in tri.vertices]
   if name.startswith('MAIN_stone_tower_'):polygon=clip_above(polygon,9.4601)
   if len(polygon)<3:continue
   off=len(highv);highv+=polygon
   highf.extend((off,off+i,off+i+1) for i in range(1,len(polygon)-1))
  ev.to_mesh_clear()
 high_tree=BVHTree.FromPolygons(highv,highf,all_triangles=True)
 extended_bounds=[[min(v[i] for v in highv),max(v[i] for v in highv)] for i in range(3)]
 allowed=set(entry.MODIFIED)|set(entry.LOWER)|set(app['added'])
 high_neighbors=[o for o in s.objects if o.type=='MESH' and not o.hide_render and o.name not in allowed and base.overlap(base.bounds(o),extended_bounds)]
 report['extended_volume_actual_neighbors']=[o.name for o in high_neighbors]
 if high_neighbors:
  hb,ho=audit.world_bvh(high_neighbors,True);hits=hb.overlap(high_tree)
  report['extended_volume_intersections']=[ho[a] for a,b in hits[:50]]
  assert not hits,('New high tower hits saved geometry',report['extended_volume_intersections'])
 else:report['extended_volume_intersections']=[]
 lower_delta=[]
 for record in app['changed_vertex_records']:
  ob=s.objects[record['object']]
  ids={v['id'] for v in record['changed_vertices']}
  if record['object'].startswith('MAIN_stone_tower_'):
   assert len(ids)==4
   assert all(abs(v['before'][2]-9.46)<1e-5 for v in record['changed_vertices'])
  for v in record['changed_vertices']:
   actual=ob.matrix_world@ob.data.vertices[v['id']].co
   assert abs(actual.x-v['before'][0])<1e-6 and abs(actual.y-v['before'][1])<1e-6
   assert abs(actual.z-v['before'][2]-app['correction_m'])<2e-6
  lower_delta.append({'object':record['object'],'changed_vertex_count':len(ids),'xy_unchanged':True})
 report['bounded_vertex_change_checks']=lower_delta
 actual_top=entry.top(s.objects['MAIN_chimney_cap'])
 actual_datum=entry.top(s.objects['MAIN_L1_TERRACE_W_finish'])
 report['actual_nominal_anchor']={'upper':actual_top,'lower':actual_datum,'relative':actual_top-actual_datum,'error_m':actual_top-actual_datum-entry.NOMINAL_M}
 assert abs(report['actual_nominal_anchor']['error_m'])<2e-6
 report['legacy_outlets_status']=app['outlet_status']
 report['legacy_cap_plan_status']=app['cap_status']
 report['current_route_regression']=audit.route_regression(route,old,_oldowners,navigation_new,navigation_owners)
 assert not report['current_route_regression']['new_obstacles']
 cameras=[]
 for c in [o for o in s.objects if o.type=='CAMERA']:
  pt=c.matrix_world.translation;hit,n,ix,d=navigation_new.find_nearest(pt)
  cameras.append({'name':c.name,'point':list(pt),'nearest_new_finish_m':d,'owner':navigation_owners[ix]})
 assert len(cameras)==131 and min(c['nearest_new_finish_m'] for c in cameras)>.18
 report['all_131_cameras']=cameras
 movies=[]
 for name,segs in ((route['main_camera'],route['main_segments']),(route['supplemental_camera'],route['supplemental_segments'])):
  cam=s.objects[name];assert cam.parent is None and not cam.constraints and not cam.animation_data.drivers
  curves=[c for l in cam.animation_data.action.layers for strip in l.strips for bag in strip.channelbags for c in bag.fcurves]
  indexed={(c.data_path,c.array_index):c for c in curves};assert all(k.interpolation=='LINEAR' for c in curves for k in c.keyframe_points)
  minimum=1e10;count=0;nearest=None;matrix_error=0
  for seg in segs:
   for frame in range(seg['start_frame'],seg['end_frame']+1):
    point=Vector([indexed['location',i].evaluate(frame) for i in range(3)]);hit,n,ix,d=navigation_new.find_nearest(point);count+=1
    if d<minimum:minimum=d;nearest={'frame':frame,'segment':seg['id'],'target':navigation_owners[ix],'point':list(point)}
   for frame in (seg['start_frame'],(seg['start_frame']+seg['end_frame'])//2,seg['end_frame']):
    s.frame_set(frame);point=Vector([indexed['location',i].evaluate(frame) for i in range(3)])
    matrix_error=max(matrix_error,(cam.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation-point).length)
  assert minimum>.18 and matrix_error<1e-5
  movies.append({'camera':name,'samples':count,'minimum_clearance_m':minimum,'nearest':nearest,'evaluated_matrix_max_error':matrix_error})
 report['movie_positions']=movies;assert sum(m['samples'] for m in movies)==7584
 s.frame_set(48);bpy.context.view_layer.update();after=audit.snapshot()
 removed=set(before['objects'])-set(after['objects']);added=set(after['objects'])-set(before['objects'])
 assert not removed and added==set(app['added'])
 assert all(v==after['objects'][n] for n,v in before['objects'].items() if n not in entry.MODIFIED)
 for name in entry.MODIFIED:
  a=before['objects'][name];b=after['objects'][name]
  assert all(v==b[k] for k,v in a.items() if k not in ('data_hash','properties')),name
  assert all(v==b['properties'][k] for k,v in a['properties'].items() if k!='data'),name
 for key,value in before['global'].items():
  if key in ('materials','collections'):assert all(after['global'][key].get(n)==v for n,v in value.items()),key
  else:assert value==after['global'][key],key
 for n,v in before['meshes'].items():
  if n in after['meshes']:assert after['meshes'][n]==v,n
 assert physical_before=={n:audit.physical_hash(s.objects[n]) for n in physics}
 report.update({'status':'PASS_PHYSICAL_CANDIDATE_NOT_VISUALLY_ACCEPTED','non_target_objects_unchanged':len(before['objects'])-len(entry.MODIFIED),'removed_exact_names':sorted(removed),'added_exact_names':sorted(added),
  'original_globals_unchanged':True,'original_shared_meshes_unchanged':True,'only_five_named_object_data_changes':list(entry.MODIFIED),'protected_physics':physical_before,'source_sha_still_same':sha(SOURCE)==SHA})
 compact={'snapshot_sha256':audit.digest(after),'objects':{k:audit.digest(v) for k,v in after['objects'].items()},'global':audit.digest(after['global']),'meshes':after['meshes']}
 (Q/'masonry12b-candidate-fingerprint.json').write_text(json.dumps(compact,separators=(',',':')),encoding='utf-8')
 bpy.ops.wm.save_as_mainfile(filepath=str(TARGET),compress=True);report['candidate_sha256']=sha(TARGET)
except Exception as e:report['status']='FAILED_UNSAVED_CANDIDATE';report['exception']=repr(e);raise
finally:
 report['seconds']=time.monotonic()-start;(Q/'masonry12b-build-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('MASONRY12b_RESULT',report['status'],report.get('exception'),report['seconds'],flush=True)
