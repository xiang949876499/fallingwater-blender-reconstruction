import bpy,sys,json,hashlib,time
from pathlib import Path
from types import SimpleNamespace
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];Q=ROOT/'qa';sys.path[:0]=[str(ROOT/'scripts'),str(Q)]
import forest_canopy_detail11 as entry
import shrub08_auditlib as audit
SOURCE=ROOT/'scene/Fallingwater_navigation_candidate10a.blend';SHA='1e7b17d9c2396513f005724e50788bf834097eedb401b91a7f1030825e2c4ed9'
TARGET=ROOT/'scene/Fallingwater_forest_canopy_integration11.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE)==SHA and not TARGET.exists()
manifest=entry.load_manifest(ROOT);route_raw=(Q/'integration10-navigation-workspace/data/tour-route.json').read_bytes();route=json.loads(route_raw)
(Q/'forest-canopy11-integration-route.json').write_bytes(route_raw)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;stored=scene.frame_current;ctx=SimpleNamespace(root=ROOT)
report={'status':'RUNNING','source_sha256':SHA,'source':str(SOURCE),'candidate':str(TARGET),'source_frame':stored,'physical_comparison_frame':48,
        'dependencies':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'scripts/forest_canopy_detail11.py',ROOT/'data/forest_canopy11.json',ROOT/'assets/models/site_canopy18.blend']},
        'route_sha256':hashlib.sha256(route_raw).hexdigest(),'rendered':False,'production_wiring_changed':False}
start=time.monotonic()
try:
 print('CANOPY_INTEGRATION fingerprint before',flush=True);before=audit.snapshot();meshes_before=set(bpy.data.meshes)
 report['disabled']=entry.build(ctx,{})
 first=scene.objects[manifest['objects'][0]['name']];location=first.location.copy();original_data=first.data
 try:
  first.location.x+=.05;bpy.context.view_layer.update();entry.build(ctx,{'enabled':True});raise AssertionError('Changed root accepted')
 except ValueError as e:report['wrong_root_rejected']=str(e)
 finally:first.location=location;bpy.context.view_layer.update()
 try:
  first.data=bpy.data.meshes[manifest['objects'][2]['old_mesh']] if manifest['objects'][2]['old_mesh']!=original_data.name else bpy.data.meshes['TREE_Asset_7_Woody_Branches']
  entry.build(ctx,{'enabled':True});raise AssertionError('Changed data accepted')
 except ValueError as e:report['wrong_data_rejected']=str(e)
 finally:first.data=original_data;bpy.context.view_layer.update()
 assert set(bpy.data.meshes)==meshes_before
 scene.frame_set(48);physics=[o.name for o in scene.objects if o.type=='MESH' and o.name.startswith(('SITE_Core_','SITE_Cascade_Shoulder_Continuous','WATER_','SITE_Bridge10_','SITE_Path_','SITE_Continuous_BearRun_Terrain'))]
 physical_before={n:audit.physical_hash(scene.objects[n]) for n in physics}
 report['source_original_signatures']={r['old_mesh']:entry.mesh_signature(bpy.data.meshes[r['old_mesh']]) for r in manifest['objects']}
 print('CANOPY_INTEGRATION apply native library',flush=True);report['application']=entry.build(ctx,{'enabled':True})
 assert report['application']['status']=='APPLIED_ACCEPTED_18_ROOT_CANOPY_VISUAL_SCOPE_ONLY'
 report['repeat']=entry.build(ctx,{'enabled':True});assert report['repeat']['status']=='SKIPPED_ALREADY_APPLIED'
 accepted_data=first.data
 try:
  first.data=original_data;entry.build(ctx,{'enabled':True});raise AssertionError('Partial state accepted')
 except ValueError as e:report['partial_state_rejected']=str(e)
 finally:first.data=accepted_data;bpy.context.view_layer.update()
 # Native library completeness/material indices and original geometry prefix.
 records={r['name']:r for r in manifest['meshes']};material_counts={}
 for r in manifest['meshes']:
  old=bpy.data.meshes[r['old_mesh']];new=bpy.data.meshes[r['name']]
  assert entry.mesh_signature(new)==r['signature']
  assert all(v.co==new.vertices[i].co for i,v in enumerate(old.vertices))
  assert all(tuple(p.vertices)==tuple(new.polygons[i].vertices) for i,p in enumerate(old.polygons))
  counts={str(i):sum(p.material_index==i for p in new.polygons) for i in range(len(new.materials))}
  assert counts==r['polygon_material_counts'];material_counts[new.name]=counts
 report['per_face_material_indices_exact']=material_counts
 # Aggregate ONLY added faces: original foliage contacts remain unchanged and
 # cannot be mislabeled as a new collision. Face owner identifies exact target.
 vertices=[];faces=[];owners=[]
 for r in manifest['objects']:
  obj=scene.objects[r['name']];rec=records[r['new_mesh']];nv=rec['original_vertices'];np=rec['original_polygons'];off=len(vertices)
  vertices.extend(obj.matrix_world@v.co for v in list(obj.data.vertices)[nv:])
  for poly in list(obj.data.polygons)[np:]:
   assert min(poly.vertices)>=nv;faces.append(tuple(off+i-nv for i in poly.vertices));owners.append(obj.name)
 added=BVHTree.FromPolygons(vertices,faces,all_triangles=True);empty=BVHTree.FromPolygons([],[])
 nav=audit.route_regression(route,empty,[],added,owners);assert not nav['new_obstacles'];report['current_route_regression']=nav
 cameras=[]
 for cam in [o for o in scene.objects if o.type=='CAMERA']:
  hit,n,ix,d=added.find_nearest(cam.matrix_world.translation)
  cameras.append({'name':cam.name,'frame':48,'nearest_added_geometry_m':d,'nearest_owner':owners[ix],'pass_0_40m':d>=.40})
 assert all(r['pass_0_40m'] for r in cameras);report['all_current_cameras']=cameras
 # Root has evaluated all7584 movie transforms. This independent regression
 # reads exact linear location fcurves (unparented, no constraints/drivers) and
 # tests all delivered integer samples against new canopy triangles. Sparse
 # depsgraph samples independently verify equality to actual world matrices.
 movies=[]
 for camera_name,segments in ((route['main_camera'],route['main_segments']),(route['supplemental_camera'],route['supplemental_segments'])):
  cam=scene.objects[camera_name];assert cam.parent is None and not cam.constraints and not cam.animation_data.drivers
  action=cam.animation_data.action;curves=[c for layer in action.layers for strip in layer.strips for bag in strip.channelbags for c in bag.fcurves]
  indexed={(c.data_path,c.array_index):c for c in curves};assert all(k.interpolation=='LINEAR' for c in curves for k in c.keyframe_points)
  count=0;minimum=1e10;closest=None;failed=[];matrix_error=0
  for seg in segments:
   for frame in range(seg['start_frame'],seg['end_frame']+1):
    point=Vector([indexed['location',i].evaluate(frame) for i in range(3)]);hit,n,ix,d=added.find_nearest(point);count+=1
    if d<minimum:minimum=d;closest={'frame':frame,'segment':seg['id'],'owner':owners[ix],'point':list(point)}
    if d<.13:failed.append({'frame':frame,'segment':seg['id'],'distance':d})
   for frame in (seg['start_frame'],(seg['start_frame']+seg['end_frame'])//2,seg['end_frame']):
    scene.frame_set(frame);actual=cam.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation
    point=Vector([indexed['location',i].evaluate(frame) for i in range(3)]);matrix_error=max(matrix_error,(actual-point).length)
  assert not failed and matrix_error<.00001
  movies.append({'camera':camera_name,'integer_frames':count,'closest_added_canopy_m':minimum,'closest':closest,'failures':failed,
                 'camera_clearance_threshold_m':.13,'direct_evaluated_matrix_sample_max_error_m':matrix_error})
 report['movie_added_canopy_clearance']=movies;assert sum(r['integer_frames'] for r in movies)==7584
 scene.frame_set(48);bpy.context.view_layer.update()
 hard=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and o.name.startswith(('MAIN_','GUEST_','SITE_Path_','SITE_Bridge_','SITE_Bridge10_','SITE_Core_','SITE_Cascade_Shoulder_Continuous','SITE_Continuous_BearRun_Terrain'))]
 hb,ho=audit.world_bvh(hard,True);pairs=hb.overlap(added);assert not pairs;report['hard_added_intersection_pairs']=len(pairs)
 terrain,_=audit.world_bvh([scene.objects['SITE_Continuous_BearRun_Terrain']],True)
 roots=[]
 for r in manifest['objects']:
  if r['part']!='leaf':continue
  obj=scene.objects[r['name']];point=obj.matrix_world.translation;hit=terrain.ray_cast(Vector((point.x,point.y,80)),Vector((0,0,-1)),180)[0]
  roots.append({'name':obj.name,'matrix_error':entry._matrix_error(obj.matrix_world,r['matrix']),'actual_terrain_root_gap_m':point.z-hit.z})
 report['root_checks']=roots
 assert physical_before=={n:audit.physical_hash(scene.objects[n]) for n in physics};report['protected_physics']=physical_before
 scene.frame_set(stored);print('CANOPY_INTEGRATION fingerprint after',flush=True);after=audit.snapshot();changed=audit.compare_snapshots(before,after,entry.TARGETS);assert set(changed)==entry.TARGETS
 shrub_names=[n for n in before['objects'] if n.startswith('TREE_Understory_')];assert all(before['objects'][n]==after['objects'][n] for n in shrub_names)
 report.update({'status':'PASS_NATIVE_LIBRARY_FULL_NAV10A_REGRESSION_NO_RENDER','changed_objects':sorted(changed),'non_target_count_unchanged':len(before['objects'])-36,
                'all_original_meshes_unchanged':True,'all_understory_objects_unchanged':len(shrub_names),'all_globals_unchanged':True,'source_unchanged':sha(SOURCE)==SHA})
 compact={'snapshot_sha256':audit.digest(after),'objects':{k:audit.digest(v) for k,v in after['objects'].items()},'global':audit.digest(after['global']),'meshes':after['meshes']}
 (Q/'forest-canopy11-integration-fingerprint.json').write_text(json.dumps(compact,separators=(',',':')),encoding='utf-8')
 bpy.ops.wm.save_as_mainfile(filepath=str(TARGET),compress=True);report['candidate_sha256']=sha(TARGET)
except Exception as e:report['status']='FAILED_NO_PRODUCTION_INTEGRATION';report['exception']=repr(e);raise
finally:
 report['elapsed_s']=time.monotonic()-start;(Q/'forest-canopy11-integration-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('CANOPY_INTEGRATION_RESULT',report['status'],report.get('exception'),report['elapsed_s'],flush=True)
