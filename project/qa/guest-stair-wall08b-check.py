"""Add only the source-confirmed stair wall to immutable07 tour; real mesh QA."""
import bpy,json,sys,hashlib
from pathlib import Path
from types import SimpleNamespace
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import guest_house,fwlib,tour
source=Path(bpy.data.filepath)
expected='792882445860ae6a7bb37e3e03838d74a07647e89dbf5475a056125d6bac067e'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
scene=bpy.context.scene;data=json.loads((ROOT/'data/guest_house.json').read_text(encoding='utf-8'))
config=json.loads((ROOT/'config.json').read_text(encoding='utf-8'))
reg={**data['registration'],**config.get('guest_registration',{})}
sx,sy=reg['meters_per_pixel'];ox,oy=reg['origin_px'];wx,wy,gz=reg['world_origin']
def point(q):return (wx+(q[0]-ox)*sx,wy+(oy-q[1])*sy)
ctx=SimpleNamespace(root=ROOT,config=config,mats={m.name[3:]:m for m in bpy.data.materials if m.name.startswith('FW_')},collection=fwlib.collection)
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
byid={r['id']:r for r in rooms}
col=bpy.data.objects['GUEST_LAUNDRY_DESCENT_tread_00'].users_collection[0]
removed=[o for o in scene.objects if o.name=='GUEST_LAUNDRY_DESCENT_handrail_-1' or o.name.startswith('GUEST_LAUNDRY_DESCENT_baluster_-1_')]
def signature(o):return (o.data.as_pointer() if o.data else None,tuple(v for row in o.matrix_world for v in row))
unchanged={o.name:signature(o) for o in scene.objects if o not in removed}
def bounds(o):
    pp=[o.matrix_world@Vector(p) for p in o.bound_box]
    return [[min(p[k] for p in pp),max(p[k] for p in pp)] for k in range(3)]
before_geometry=[{'name':o.name,'bounds':bounds(o)} for o in scene.objects if o.name.startswith('GUEST_LAUNDRY_DESCENT') or o.name=='GUEST_B1_BASE_EAST_pier_end']
before=tour.Probe(scene,((-2,5),(36,43),(5,12)))
route=json.loads((ROOT/'qa/tour-path-route-iteration07-final.json').read_text(encoding='utf-8'))
adj=json.loads((ROOT/'qa/tour-path-all-adjacency-iteration07-final.json').read_text(encoding='utf-8'))
# Ground and 1.95m head clearance along actual steps and original local approaches.
stairs=tour.stair_mesh_points(scene,'GUEST_LAUNDRY_DESCENT_tread_',True)
before.step_mode=True;before_stair=before.path(stairs,True)
local_pairs=[frozenset(('GUEST_L1_STAIR_HALL','GUEST_B1_STAIR')),frozenset(('GUEST_B1_STAIR','GUEST_B1_LAUNDRY'))]
connections=[e for e in adj['edges'] if frozenset((e['from'],e['to'])) in local_pairs]
before_connections=[before.path(e['points'],True) for e in connections]
removed_names=[o.name for o in removed]
for obj in removed:bpy.data.objects.remove(obj,do_unlink=True)
new=guest_house.build_laundry_retaining_wall(ctx,data,point,gz,col)[0]
bpy.context.view_layer.update()
after=tour.Probe(scene,((-2,5),(36,43),(5,12)));after.step_mode=True
after_stair=after.path(stairs,True)
after_connections=[after.path(e['points'],True) for e in connections]
same=unchanged=={o.name:signature(o) for o in scene.objects if o.name!=new.name}
def mesh_tree(obj):
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
    vertices=[obj.matrix_world@v.co for v in mesh.vertices];faces=[tuple(p.vertices) for p in mesh.polygons]
    tree=BVHTree.FromPolygons(vertices,faces,all_triangles=False);evaluated.to_mesh_clear();return tree
left=bpy.data.objects['GUEST_B1_BASE_EAST_pier_end'];left_tree=mesh_tree(left);right_tree=mesh_tree(new)
station=Vector((1.7759,point((285,390))[1],gz-.35))
def hit(tree,direction):
    loc,normal,index,distance=tree.ray_cast(station,Vector(direction),2)
    return {'point':list(loc),'normal':list(normal),'face_index':index,'distance':distance} if loc is not None else None
left_hit=hit(left_tree,(-1,0,0));right_hit=hit(right_tree,(1,0,0))
measurement=(right_hit['point'][0]-left_hit['point'][0]) if left_hit and right_hit else None
nominal=.7366;dimension_ok=measurement is not None and abs(measurement-nominal)<=.020
finish_hits=[after.ray(station,d,2) for d in ((-1,0,0),(1,0,0))]
finish_clear=finish_hits[1]['location'][0]-finish_hits[0]['location'][0] if all(finish_hits) else None
body_samples=[]
for i,p in enumerate(stairs):
    floor=p[2]-tour.EYE
    for offset in (-.24,0,.24):
        location=Vector(p)+Vector((offset,0,0))
        ground=after.ground(location,floor)
        obstruction=after.ray((location.x,location.y,floor+.24),(0,0,1),1.95-.24)
        body_samples.append({'tread':i,'side_m':offset,'point':list(location),'ground_failure':ground,'head_body_hit':obstruction})
body_ok=all(not r['ground_failure'] and not r['head_body_hit'] for r in body_samples)
# Evaluate every saved integer-frame camera position. Only positions/sweeps
# whose body envelope can meet the changed volume need regional mesh replay.
wall_bounds=bounds(new);frame_total=0;affected=[];initial_frame=scene.frame_current
for camera_name,segments in ((route['main_camera'],route['main_segments']),(route['supplemental_camera'],route['supplemental_segments'])):
    camera=bpy.data.objects[camera_name];action=camera.animation_data.action
    curves=[curve for layer in action.layers for strip in layer.strips for bag in strip.channelbags for curve in bag.fcurves]
    indexed={(c.data_path,c.array_index):c for c in curves}
    for segment in segments:
        previous=None;walk=bool(segment.get('body_clearance_tested',segment['mode'].startswith('NORMAL')))
        before.step_mode=after.step_mode='STAIRS' in segment['mode']
        for frame in range(segment['start_frame'],segment['end_frame']+1):
            position=Vector([indexed['location',i].evaluate(frame) for i in range(3)]);frame_total+=1
            near=wall_bounds[0][0]-.40<=position.x<=wall_bounds[0][1]+.40 and wall_bounds[1][0]-.40<=position.y<=wall_bounds[1][1]+.40 and wall_bounds[2][0]-.3<=position.z<=wall_bounds[2][1]+tour.EYE+.3
            if near:
                scene.frame_set(frame);actual=camera.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation.copy()
                old=before.point(actual,walk);current=after.point(actual,walk)
                old_sweep=before.segment(previous,actual,walk) if previous is not None else None
                new_sweep=after.segment(previous,actual,walk) if previous is not None else None
                affected.append({'frame':frame,'segment':segment['id'],'camera':camera_name,'position':list(actual),
                    'matrix_error_m':(position-actual).length,'before':old,'after':current,'before_sweep':old_sweep,'after_sweep':new_sweep})
            previous=position
scene.frame_set(initial_frame)
new_frame_failures=[r for r in affected if (r['after'] and not r['before']) or (r['after_sweep'] and not r['before_sweep'])]
result={'status':'PASS_PATH_GEOMETRY_FINISHED_SURFACE_AUDIT_PENDING' if dimension_ok and body_ok and after_stair is None and not any(after_connections) and not new_frame_failures and same else 'REQUIRES_REVIEW',
    'source_scene':str(source),'source_sha256':expected,'source_07_tour_hash_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==expected,
    'new_wall':new.name,'wall_bounds':wall_bounds,'removed_inferred_outer_rail_components':removed_names,
    'before_stair_geometry':before_geometry,'all_other_objects_datablocks_and_matrices_unchanged':same,
    'nominal_width_m':nominal,'measurement_station':list(station),'actual_evaluated_core_faces':{'left_object':left.name,'left':left_hit,'right_object':new.name,'right':right_hit},
    'actual_core_face_clear_width_m':measurement,'nominal_deviation_m':measurement-nominal if measurement is not None else None,'tolerance_m':.020,'dimension_status':'CORE_ONLY_WITHIN_TOLERANCE_FINISH_AUDIT_REQUIRED' if dimension_ok else 'CORE_ONLY_FAIL',
    'nearest_visible_surface_hits':finish_hits,'nearest_surface_clear_width_m':finish_clear,
    'actual_stair_before_failure':before_stair,'actual_stair_after_failure':after_stair,
    'original_connections':[{'from':e['from'],'to':e['to'],'points':e['points'],'before_failure':a,'after_failure':b} for e,a,b in zip(connections,before_connections,after_connections)],
    'step_and_head_samples':body_samples,'body_width_m':.48,'head_height_m':1.95,'body_status':'PASS' if body_ok else 'FAIL',
    'saved_07_integer_frames_considered':frame_total,'changed_volume_relevant_frames':len(affected),'frame_checks':affected,'new_frame_failures':new_frame_failures,
    'height_and_finish_status':'C: top L1+0.80m, base B1-0.24m, concrete finish; no measured height/finish attribution',
    'source_interpretation':'Guest01 real opposing masonry faces and rounded south end; 2ft5in is not tread or railing width. guest03/04 rounded-wall clues are qualitative only.',
    'scope':'One wall added and four inferred east-rail parts replaced. No other geometry, furniture, cameras or paths moved. All nonlocal07 frames keep prior frozen-scene verification; direct new-volume tests cover all potentially affected frame envelopes.'}
candidate=ROOT/'scene/guest_stair_wall_candidate08b.blend'
assert not candidate.exists(),'Preserve prior candidate; use a new version.'
bpy.ops.wm.save_as_mainfile(filepath=str(candidate),compress=True)
result['candidate']=str(candidate);result['candidate_sha256']=hashlib.sha256(candidate.read_bytes()).hexdigest()
(ROOT/'qa/guest-stair-wall08b-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('STAIR_WALL08',json.dumps({k:v for k,v in result.items() if k not in ('frame_checks','step_and_head_samples','before_stair_geometry','original_connections','new_frame_failures')}),flush=True)
print('NEW_FRAME_FAILURES',json.dumps(new_frame_failures[:5]),flush=True)
