"""Select diagnostic cameras by actual scene witnesses, without rendering/saving."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import tour
scene=bpy.context.scene;scene.render.resolution_x=960;scene.render.resolution_y=540;scene.render.resolution_percentage=100
probe=tour.Probe(scene,((-5,9),(32,45),(3,15)))
wall=bpy.data.objects['GUEST_LAUNDRY_DESCENT_outer_retaining_wall']
def verts(obj):return [obj.matrix_world@v.co for v in obj.data.vertices]
witnesses=[]
for obj in scene.objects:
    if obj.name.startswith('GUEST_LAUNDRY_DESCENT_tread_'):
        vv=verts(obj);pp=Vector((sum(v.x for v in vv)/len(vv),sum(v.y for v in vv)/len(vv),max(v.z for v in vv)))
        witnesses.append({'part':'tread','name':obj.name,'point':pp})
wv=verts(wall)
for poly in wall.data.polygons:
    pp=sum((wv[i] for i in poly.vertices),Vector())/len(poly.vertices)
    if len(poly.vertices)==4:
        category='rounded_tip' if pp.y<38.36 else ('north_return' if pp.y>40.40 else 'straight_wall')
        witnesses.append({'part':category,'name':wall.name,'point':pp})
        witnesses.append({'part':category+'_top','name':wall.name,'point':Vector((pp.x,pp.y,9.20))})
# The target passes into the real laundry doorway; visibility of this point
# proves an unobstructed sightline through the opening, not bodily passage.
witnesses.append({'part':'laundry_door_opening','name':None,'point':Vector((1.08,40.05,7.05))})
base_names=['CAM_GUEST_B1_STAIR_A','CAM_GUEST_B1_STAIR_B']
camera=bpy.data.objects[base_names[0]].copy();camera.data=camera.data.copy();scene.collection.objects.link(camera)
camera.name='QA_DIAGNOSTIC_STAIR_WALL_TEMP'
def record(name,location,rotation=None,target=None,lens=28):
    camera.location=location
    camera.rotation_euler=rotation if rotation is not None else (Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.lens=lens;camera.data.shift_x=0;camera.data.shift_y=0
    bpy.context.view_layer.update()
    result={'id':name,'location':list(camera.location),'rotation_euler':list(camera.rotation_euler),'target':target,'lens':lens,
            'camera_clearance_failure':probe.point(camera.location,False),'witnesses':[]}
    direction=camera.rotation_euler.to_quaternion()@Vector((0,0,-1))
    result['center_ray_first_hit']=probe.ray(camera.location,direction,30)
    for w in witnesses:
        pp=w['point'];proj=world_to_camera_view(scene,camera,pp);delta=pp-camera.location
        first=probe.ray(camera.location,delta.normalized(),delta.length+.003)
        visible=(first is None or first['distance']>=delta.length-.012)
        framed=proj.z>0 and .025<=proj.x<=.975 and .025<=proj.y<=.975
        result['witnesses'].append({'part':w['part'],'name':w['name'],'point':list(pp),'projected':list(proj),'framed':framed,'unoccluded':visible,'first_hit':first})
    from collections import Counter
    result['visible_counts']=dict(Counter(w['part'] for w in result['witnesses'] if w['framed'] and w['unoccluded']))
    return result
records=[]
for name in base_names:
    obj=bpy.data.objects[name]
    records.append(record(name,list(obj.matrix_world.translation),rotation=obj.matrix_world.to_euler(),lens=obj.data.lens))
choices=[
    ('south_high',[1.86,37.40,10.25],[1.84,39.35,7.65],24),
    ('south_east_high',[2.85,37.3,10.45],[1.83,39.30,7.72],24),
    ('south_east_outer',[3.2,36.8,10.8],[1.90,39.2,8.12],28),
    ('south_high_overview',[2.25,36.65,11.25],[1.8,39.20,8.0],28),
    ('north_low_door',[1.85,39.43,8.26],[1.12,40.03,7.15],22),
    ('north_door_stairs',[1.92,40.23,7.64],[1.40,39.75,7.50],18),
    ('north_door_stairs_wide',[1.92,40.23,7.64],[1.40,39.75,7.50],16),
    ('mid_stair_door',[1.85,39.43,8.26],[1.50,40.05,7.40],18),
    ('mid_stair_door_low',[1.85,39.65,7.91],[1.50,40.05,7.18],18),
    ('north_upper_door',[1.87,39.03,8.63],[1.25,40.18,7.25],24),
    ('lower_well',[1.92,40.23,7.64],[1.78,38.8,8.3],24),
    ('north_high_overview',[1.84,40.12,10.05],[1.83,38.85,8.15],24),
]
records.extend(record(*c[:2],target=c[2],lens=c[3]) for c in choices)
result={'scene':bpy.data.filepath,'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
        'purpose':'ADDITIONAL_DIAGNOSTICS_NOT_A_REPLACEMENT_FOR_ROOM120_OR_VISUAL_ACCEPTANCE','records':records}
(ROOT/'qa/guest-stair-wall08b-camera-probe2.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
for r in records:print('CAM_DIAGNOSTIC',r['id'],r['camera_clearance_failure'],r['visible_counts'],r['center_ray_first_hit'],flush=True)
