"""Apply one checked native replacement plan to an independent combined11 copy."""
import bpy,sys,json,hashlib,time,re
from pathlib import Path
from types import SimpleNamespace
from mathutils import Vector
R=Path(__file__).resolve().parents[1];Q=R/'qa';sys.path[:0]=[str(R/'scripts'),str(Q)]
import forest_undergrowth13 as entry
import understory_detail as accepted
import shrub08_auditlib as audit
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw=(Q/'forest-undergrowth13-plan.json').read_bytes();plan=json.loads(raw)
P=Path(plan['source']);TARGET=R/'scene/Fallingwater_forest_undergrowth_candidate13a.blend'
assert plan['status']=='PASS_PREFLIGHT_NATIVE_REPLACEMENT_PLAN' and sha(P)==plan['source_sha256']
assert not TARGET.exists(),'Preserve earlier candidates'
route_path=Q/'forest-undergrowth13-frozen-route.json';assert sha(route_path)==plan['frozen_route_sha256']
route=json.loads(route_path.read_text())
report={'status':'RUNNING','source':str(P),'source_sha256':sha(P),'candidate':str(TARGET),'plan_sha256':hashlib.sha256(raw).hexdigest(),
        'helper_sha256':sha(R/'scripts/forest_undergrowth13.py'),'audit_helper_sha256':sha(Q/'shrub08_auditlib.py'),
        'frame':48,'rendered':False,'new_meshes':0,'new_materials':0,'new_objects':0}
start=time.monotonic()
try:
 bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;s.frame_set(48);bpy.context.view_layer.update()
 print('UNDERGROWTH13 source snapshot',flush=True);before=audit.snapshot()
 targets={r[k] for r in plan['selection'] for k in ('branch_object','leaf_object')}
 physics=[o.name for o in s.objects if o.type=='MESH' and o.name.startswith(('SITE_Core_','SITE_Cascade_Shoulder_Continuous','WATER_','SITE_Bridge','SITE_Path_','SITE_Continuous_BearRun_Terrain'))]
 protected16=[r['name'] for r in accepted.APPROVED['objects']]
 physical={n:audit.physical_hash(s.objects[n]) for n in physics+protected16}
 old,oldowners=audit.world_bvh([s.objects[n] for n in sorted(targets)],True)
 original_ids={'meshes':set(bpy.data.meshes.keys()),'materials':set(bpy.data.materials.keys()),'objects':set(bpy.data.objects.keys())}
 report['disabled_check']=entry.build(SimpleNamespace(root=R),plan)
 assert report['disabled_check']['status']=='NOT_RUN_DISABLED'
 print('UNDERGROWTH13 apply native shared mesh pointers',len(targets),flush=True)
 application=entry.build(SimpleNamespace(root=R),plan,enabled=True);report['application']=application
 report['repeat']=entry.build(SimpleNamespace(root=R),plan,enabled=True);assert report['repeat']['status']=='SKIPPED_ALREADY_APPLIED'
 assert all(set(getattr(bpy.data,k).keys())==v for k,v in original_ids.items())
 new,newowners=audit.world_bvh([s.objects[n] for n in sorted(targets)],True)
 nav=audit.route_regression(route,old,oldowners,new,newowners);report['current_route_regression']=nav
 assert not nav['new_obstacles'] and nav['candidate_target_hits']==0
 cameras=[]
 for cam in [o for o in s.objects if o.type=='CAMERA']:
  point=cam.matrix_world.translation;hit,n,index,distance=new.find_nearest(point)
  cameras.append({'name':cam.name,'nearest_new_mesh_m':distance,'object':newowners[index]})
 assert len(cameras)==131 and min(r['nearest_new_mesh_m'] for r in cameras)>.3
 report['saved_camera_clearance']=cameras
 movies=[]
 for name,segs in ((route['main_camera'],route['main_segments']),(route['supplemental_camera'],route['supplemental_segments'])):
  cam=s.objects[name];assert not cam.parent and not cam.constraints and not cam.animation_data.drivers
  curves=[c for layer in cam.animation_data.action.layers for strip in layer.strips for bag in strip.channelbags for c in bag.fcurves]
  indexed={(c.data_path,c.array_index):c for c in curves};assert all(k.interpolation=='LINEAR' for c in curves for k in c.keyframe_points)
  minimum=1e10;count=0;nearest=None;matrix_error=0
  for seg in segs:
   for f in range(seg['start_frame'],seg['end_frame']+1):
    point=Vector([indexed['location',i].evaluate(f) for i in range(3)]);hit,n,index,distance=new.find_nearest(point);count+=1
    if distance<minimum:minimum=distance;nearest={'frame':f,'segment':seg['id'],'object':newowners[index],'point':list(point)}
   for f in (seg['start_frame'],(seg['start_frame']+seg['end_frame'])//2,seg['end_frame']):
    s.frame_set(f);point=Vector([indexed['location',i].evaluate(f) for i in range(3)])
    matrix_error=max(matrix_error,(cam.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation-point).length)
  assert minimum>.3 and matrix_error<1e-5
  movies.append({'camera':name,'samples':count,'minimum_clearance_m':minimum,'nearest':nearest,'evaluated_matrix_max_error':matrix_error})
 assert sum(r['samples'] for r in movies)==7584;report['movie_positions']=movies
 s.frame_set(48);bpy.context.view_layer.update();assert physical=={n:audit.physical_hash(s.objects[n]) for n in physics+protected16}
 report['protected_physics']=physical
 print('UNDERGROWTH13 final whole-source snapshot',flush=True);after=audit.snapshot()
 changed=audit.compare_snapshots(before,after,targets);assert set(changed)==targets
 assert all(after['objects'][n]==before['objects'][n] for n in protected16)
 assert sum(bool(re.fullmatch(r'TREE_Understory_\d{4}_Leaves',o.name)) for o in s.objects)==2400
 compact={'snapshot_sha256':audit.digest(after),'objects':{k:audit.digest(v) for k,v in after['objects'].items()},'global':audit.digest(after['global']),'meshes':after['meshes']}
 (Q/'forest-undergrowth13-fingerprint.json').write_text(json.dumps(compact,separators=(',',':')),encoding='utf-8')
 report.update({'status':'PASS_NATIVE_REPLACEMENT_CANDIDATE_NO_RENDER','instances':len(plan['selection']),'changed_objects':sorted(changed),
   'non_target_objects_unchanged':len(before['objects'])-len(changed),'source_understory_population_before_after':[2400,2400],
   'accepted16_unchanged':True,'all_existing_shared_meshes_materials_unchanged':True,'root_matrices_and_labels_unchanged':True,
   'source_terrain_material':[m.name for m in s.objects['SITE_Continuous_BearRun_Terrain'].data.materials],
   'plan_selected_zone_counts':plan['selected_zone_counts'],'plan_rejections':plan['rejection_counts'],
   'instance_triangles_after':plan['instance_triangles_after'],'net_instance_triangles_added':plan['net_instance_triangles_added']})
 assert sha(P)==plan['source_sha256']
 bpy.ops.wm.save_as_mainfile(filepath=str(TARGET),compress=True);report['candidate_sha256']=sha(TARGET)
except Exception as error:
 report['status']='FAILED_UNSAVED_NO_PRODUCTION_CHANGE';report['exception']=repr(error);raise
finally:
 report['seconds']=time.monotonic()-start
 (Q/'forest-undergrowth13-build.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 print('UNDERGROWTH13_RESULT',report['status'],report.get('exception'),report['seconds'],flush=True)
