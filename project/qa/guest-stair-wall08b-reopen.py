"""Independent saved-candidate face/door and manifold checks, no render/save."""
import bpy,json,sys,hashlib,collections
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
data=json.loads((ROOT/'data/guest_house.json').read_text(encoding='utf-8'))
cfg=json.loads((ROOT/'config.json').read_text(encoding='utf-8'));reg={**data['registration'],**cfg.get('guest_registration',{})}
sx,sy=reg['meters_per_pixel'];ox,oy=reg['origin_px'];wx,wy,gz=reg['world_origin']
def world(p):return Vector((wx+(p[0]-ox)*sx,wy+(oy-p[1])*sy))
wall=bpy.data.objects['GUEST_LAUNDRY_DESCENT_outer_retaining_wall']
core=bpy.data.objects['GUEST_B1_BASE_EAST_pier_end']
station=Vector((1.7759,world((285,390)).y,gz-.35))
def ray(origin,direction,distance):
    found,point,normal,index,obj,matrix=scene.ray_cast(deps,Vector(origin),Vector(direction),distance=distance)
    return {'object':obj.name,'point':list(point),'normal':list(normal),'face':index} if found else None
finish=[ray(station,d,2) for d in ((-1,0,0),(1,0,0))]
finish_width=finish[1]['point'][0]-finish[0]['point'][0] if all(finish) else None
# Visible finish is a separate endpoint audit; never substitute a hidden core
# when the decorative sandstone projects into the documented clear opening.
core_top=max((core.matrix_world@Vector(v)).z for v in core.bound_box)
finish_samples=[]
for j in range(101):
    yy=38.27+j*.02
    support=ray((station.x,yy,gz+.12),(0,0,-1),3.1)
    if not support or not support['object'].startswith('GUEST_LAUNDRY_DESCENT_tread_'):
        finish_samples.append({'y':yy,'status':'EXCLUDED_NOT_TREAD_SUPPORTED','support':support});continue
    for height in [0.12+k*.02 for k in range(94)]:
        zz=support['point'][2]+height
        if zz>core_top-.035:continue
        origin=Vector((station.x,yy,zz));hits=[ray(origin,d,2) for d in ((-1,0,0),(1,0,0))]
        identified=all(hits) and hits[0]['object'] in ('GUEST_LAYERED_SANDSTONE_COURSES',core.name) and hits[1]['object']==wall.name
        clearance=hits[1]['point'][0]-hits[0]['point'][0] if identified else None
        finish_samples.append({'origin':list(origin),'height_above_measured_tread':height,'support':support,'hits':hits,
            'status':'MEASURED_OPPOSING_FINISHED_FACES' if identified else 'EXCLUDED_DIFFERENT_FIRST_HIT',
            'clearance_m':clearance,'deviation_m':clearance-.7366 if clearance is not None else None})
widths=[s['clearance_m'] for s in finish_samples if s.get('clearance_m') is not None]
finish_range=[min(widths),max(widths)] if widths else None
finish_pass=bool(widths) and max(abs(w-.7366) for w in widths)<=.020
def object_hit(obj,direction):
    ev=obj.evaluated_get(deps);inverse=ev.matrix_world.inverted()
    found,p,n,i=ev.ray_cast(inverse@station,(inverse.to_3x3()@Vector(direction)).normalized(),distance=2)
    return {'object':obj.name,'point':list(ev.matrix_world@p),'normal':list((ev.matrix_world.to_3x3().inverted().transposed()@n).normalized()),'face':i} if found else None
structural=[object_hit(core,(-1,0,0)),object_hit(wall,(1,0,0))]
width=structural[1]['point'][0]-structural[0]['point'][0] if all(structural) else None
east=next(w for w in data['walls'] if w['id']=='GUEST_B1_BASE_EAST');op=next(o for o in east['openings'] if o['type']=='door')
a,b=world(east['a']),world(east['b']);tangent=(b-a).normalized();normal=Vector((-tangent.y,tangent.x));center=a+(b-a)*sum(op['span'])/2
floor=gz+data['levels']['B1']['offset'];samples=[]
for side in (-.24,0,.24):
    for h in (.3,.72,.9,1.13,1.6,1.94):
        p=center+tangent*side-normal*(east['thickness']/2+.05)
        hit=ray((p.x,p.y,floor+h),(normal.x,normal.y,0),east['thickness']+.10)
        samples.append({'side_m':side,'height_m':h,'hit':hit})
edges=collections.Counter()
for face in wall.data.polygons:
    ids=list(face.vertices)
    for a,b in zip(ids,ids[1:]+ids[:1]):edges[tuple(sorted((a,b)))]+=1
nonmanifold=[list(e) for e,n in edges.items() if n!=2]
result={'status':'PASS' if width is not None and abs(width-.7366)<=.02 and finish_pass and not nonmanifold and all(s['hit'] is None for s in samples) else 'REQUIRES_REVIEW',
    'scene':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
    'independently_reopened':True,'actual_evaluated_object_ray_hits':structural,'structural_width_m':width,
    'actual_first_scene_hits':finish,'finish_clearance_at_station_m':finish_width,
    'finish_samples':finish_samples,'measured_finish_sample_count':len(widths),'finish_clearance_range_m':finish_range,
    'finish_nominal_target_status':'PASS_SAMPLED_FINISHED_FACES' if finish_pass else 'FAIL_FINISH_RANGE_OR_NO_IDENTIFIED_PAIR',
    'door_center_world':[center.x,center.y,floor],'door_cross_section_width_m':.48,'door_samples':samples,
    'nonmanifold_edges':nonmanifold,'height_finish_status':'C, not a measured elevation claim'}
(ROOT/'qa/guest-stair-wall08b-reopen.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('WALL_REOPEN',json.dumps(result),flush=True)
