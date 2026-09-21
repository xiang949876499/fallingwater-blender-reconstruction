"""Read-only Bezier, evaluated-mesh and camera identification diagnostics."""
import bpy,json,sys,hashlib,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import tour

def bounds(points):
    return [[min(p[k] for p in points),max(p[k] for p in points)] for k in range(3)]

def outside_bbox(box,reference):
    return [max(0.,reference[k][0]-box[k][0],box[k][1]-reference[k][1]) for k in range(3)]

def cubic(points,t):
    p,q,r,s=points
    return p*((1-t)**3)+q*(3*(1-t)**2*t)+r*(3*(1-t)*t*t)+s*(t**3)

def curve_record(obj,deps):
    records=[];centers=[];knots=[]
    for spline in obj.data.splines:
        if spline.type!='BEZIER':continue
        knots.extend(p.co.copy() for p in spline.bezier_points)
        for index,(a,b) in enumerate(zip(spline.bezier_points,spline.bezier_points[1:])):
            control=[a.co.copy(),a.handle_right.copy(),b.handle_left.copy(),b.co.copy()]
            samples=[cubic(control,i/200) for i in range(201)];centers.extend(samples)
            knot_box=bounds([a.co,b.co]);hull_box=bounds(control);sample_box=bounds(samples)
            records.append({'index':index,'knots':[list(a.co),list(b.co)],
                'cubic_control_hull_vertices':[list(p) for p in control],
                'control_hull_bbox':hull_box,'sampled_centerline_bbox':sample_box,
                'centerline_overshoot_vs_segment_knot_bbox_m':outside_bbox(sample_box,knot_box),
                'centerline_outside_control_hull_bbox_m':outside_bbox(sample_box,hull_box),
                'handle_types':[a.handle_right_type,b.handle_left_type],
                'handle_lengths_m':[(control[1]-control[0]).length,(control[3]-control[2]).length],
                'knot_distance_m':(a.co-b.co).length})
    if not centers:return None
    evaluated=obj.evaluated_get(deps);mesh=evaluated.to_mesh()
    local=[v.co.copy() for v in mesh.vertices];world=[obj.matrix_world@p for p in local]
    record={'name':obj.name,'room_id':obj.get('room_id'),'asset_type':obj.get('asset_type'),
            'tube_radius_m':obj.data.bevel_depth,'knots_bbox':bounds(knots),
            'centerline_bbox':bounds(centers),'evaluated_mesh_local_bbox':bounds(local),
            'evaluated_mesh_world_bbox':bounds(world),'evaluated_vertices':len(local),
            'whole_centerline_overshoot_vs_knot_bbox_m':outside_bbox(bounds(centers),bounds(knots)),
            'segments':records,'source_reference':obj.get('reference'),'evidence':obj.get('evidence')}
    evaluated.to_mesh_clear()
    return record

scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
curves=[o for o in scene.objects if o.type=='CURVE' and 'BATH' in o.get('room_id','') and o.name.startswith('FW_FURN_')]
records=[curve_record(o,deps) for o in curves]
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string());room=next(r for r in rooms if r['id']=='MAIN_B_BATH')
xs=[p[0] for p in room['polygon']];ys=[p[1] for p in room['polygon']]
probe=tour.Probe(scene,((min(xs)-.5,max(xs)+.5),(min(ys)-.5,max(ys)+.5),(room['z']-.3,room['z']+room['height']+.3)))
targets=[o for o in curves if o.get('room_id')=='MAIN_B_BATH']
projections=[]
for camera_name,width,height in [('CAM_MAIN_B_BATH_A',960,540),('CAM_MAIN_B_BATH_B',384,216)]:
    camera=bpy.data.objects[camera_name]
    camera_rows=[]
    for obj in targets:
        evaluated=obj.evaluated_get(deps);mesh=evaluated.to_mesh()
        projected=[world_to_camera_view(scene,camera,obj.matrix_world@v.co) for v in mesh.vertices]
        camera_rows.append({'object':obj.name,'projected_mesh_pixel_bbox':[
            [min(p.x for p in projected)*width,max(p.x for p in projected)*width],
            [(1-max(p.y for p in projected))*height,(1-min(p.y for p in projected))*height]],
            'direct_visible_centerline_samples':[]})
        evaluated.to_mesh_clear()
        for spline in obj.data.splines:
            if spline.type!='BEZIER':continue
            for seg,(a,b) in enumerate(zip(spline.bezier_points,spline.bezier_points[1:])):
                control=[a.co,a.handle_right,b.handle_left,b.co]
                for i in range(21):
                    world=obj.matrix_world@cubic(control,i/20)
                    screen=world_to_camera_view(scene,camera,world)
                    delta=world-camera.matrix_world.translation
                    hit=probe.ray(camera.matrix_world.translation,delta.normalized(),delta.length+.04)
                    if hit and hit['object']==obj.name and 0<=screen.x<=1 and 0<=screen.y<=1:
                        camera_rows[-1]['direct_visible_centerline_samples'].append({
                            'segment':seg,'t':i/20,'pixel':[screen.x*width,(1-screen.y)*height],'first_hit':hit})
    projections.append({'camera':camera_name,'camera_location':list(camera.matrix_world.translation),
                        'resolution':[width,height],'objects':camera_rows})
result={'source_scene':bpy.data.filepath,'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
        'status':'READ_ONLY_DIAGNOSTICS_NO_SCENE_MUTATION','all_bath_curve_records':records,
        'main_basement_bath_camera_projections':projections,
        'quantification_note':'Centerline excess is measured separately from the physical bevel radius. Cubic handles define the segment convex hull; sampling tests its bounding box, not a fitted interpretation of the image.',
        'code_source_sha256':hashlib.sha256((ROOT/'scripts/furnishings.py').read_bytes()).hexdigest()}
output=ROOT/'qa/bath-fixtures-iteration06-probe.json'
if '--output-json' in sys.argv:output=Path(sys.argv[sys.argv.index('--output-json')+1])
output.write_text(json.dumps(result,indent=2),encoding='utf-8')
print('BATH_FIXTURE_PROBE',json.dumps({'curve_count':len(records),'main_bath':[
    {k:r[k] for k in ('name','knots_bbox','centerline_bbox','evaluated_mesh_local_bbox','whole_centerline_overshoot_vs_knot_bbox_m')}
    for r in records if r['room_id']=='MAIN_B_BATH'],
    'maximum_curve_overshoots':sorted([{'name':r['name'],'meters':max(r['whole_centerline_overshoot_vs_knot_bbox_m'])}
       for r in records],key=lambda r:-r['meters'])[:8],
    'camera_hits':[{'camera':c['camera'],'objects':[{'name':o['object'],'bbox':o['projected_mesh_pixel_bbox'],'direct_hits':len(o['direct_visible_centerline_samples'])} for o in c['objects']]} for c in projections]}),flush=True)
