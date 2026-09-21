"""Fit the complete main-house envelope into the reviewed eastern aerial view."""
from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'scene/Fallingwater_iteration10.blend'
bpy.ops.wm.open_mainfile(filepath=str(SRC));scene=bpy.context.scene;scene.frame_set(48)
source=json.loads((ROOT/'qa/overview12-camera-settings02.json').read_text())['CAM_MAIN_OVERVIEW']
target=Vector(source['target']);old_eye=Vector(source['location'])
forward=(target-old_eye).normalized();rotation=forward.to_track_quat('-Z','Y')
right=rotation@Vector((1,0,0));up=rotation@Vector((0,1,0))
points=[];owners=[]
for ob in scene.objects:
    if ob.type=='MESH' and ob.name.startswith('MAIN_') and not ob.hide_render:
        corners=[ob.matrix_world@Vector(p) for p in ob.bound_box]
        if max(p.z for p in corners)<-.25:continue
        points.extend(p for p in corners if p.z>=-.25);owners.append(ob.name)
tanx=18/35;tany=10.125/35;margin=.90
dist=max(max(abs((p-target).dot(right))/(tanx*margin),abs((p-target).dot(up))/(tany*margin))-(p-target).dot(forward) for p in points)
dist=max(dist,(target-old_eye).length)
eye=target-forward*dist
cam=scene.objects['CAM_MAIN_OVERVIEW'];cam.location=eye;cam.rotation_euler=rotation.to_euler();cam.data.lens=35;cam.data.shift_x=cam.data.shift_y=0
bpy.context.view_layer.update()
uv=[world_to_camera_view(scene,cam,p) for p in points]
deps=bpy.context.evaluated_depsgraph_get()
near=[]
for d in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
    result=scene.ray_cast(deps,eye,Vector(d),distance=.45)
    if result[0]:near.append(result[4].name)
terrain=scene.objects['SITE_Continuous_BearRun_Terrain'];inv=terrain.matrix_world.inverted()
hit=terrain.ray_cast(inv@Vector((eye.x,eye.y,100)),Vector((0,0,-1)),distance=200)
ground=(terrain.matrix_world@hit[1]).z if hit[0] else None
config={'CAM_MAIN_OVERVIEW':{'location':list(eye),'target':list(target),'lens':35,'exposure':.8,'shift_x':0,'shift_y':0}}
report={'source_scene_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),
        'covered_object_count':len(owners),'points':len(points),'distance':dist,
        'image_bounds':[min(p.x for p in uv),max(p.x for p in uv),min(p.y for p in uv),max(p.y for p in uv)],
        'near_geometry':near,'terrain_z':ground,'above_terrain_m':None if ground is None else eye.z-ground,
        'geometry_edited':False,'scope':'Fit main-house above-ground bounding corners. Flying overview, not source-photo registration.'}
assert not near and (ground is None or eye.z-ground>.6)
(ROOT/'qa/overview12-camera-fit.json').write_text(json.dumps(report,indent=2),encoding='utf8')
(ROOT/'qa/overview12-camera-settings03.json').write_text(json.dumps(config,indent=2),encoding='utf8')
print(json.dumps(report),flush=True)
