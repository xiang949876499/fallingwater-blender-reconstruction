"""Read-only full-door framing after root inspected the first render."""
import bpy,sys,json,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path('D:/zx/test/project');sys.path.insert(0,str(R/'scripts'))
import guest_circulation10_routes as routes
spec=importlib.util.spec_from_file_location('local_check',R/'qa/guest-circulation10-check.py')
local=importlib.util.module_from_spec(spec);spec.loader.exec_module(local)
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==routes.CANDIDATE_SHA
probe=local.Actual();foot=routes.source((466,465,0));eye=Vector(foot)+Vector((0,0,1.6));target=Vector(routes.source((466,430,1.17)))
body,head=probe.check(foot,False)
settings={'CAM_GUEST_L1_LOUNGE_B':{'location':list(eye),'target':list(target),'lens':17,'shift_x':0,'shift_y':0,'exposure':2.2,
 'purpose':'Retreated normal-eye-height view of complete southeast door frame and threshold','mode':'GROUNDED_DIAGNOSTIC'}}
camdata=bpy.data.cameras.new('QA_C10_TEMP_PROJECTION');camdata.lens=17;camdata.sensor_width=36;camdata.sensor_fit='HORIZONTAL';camdata.clip_start=.02
cam=bpy.data.objects.new('QA_C10_TEMP_PROJECTION',camdata);bpy.context.scene.collection.objects.link(cam)
cam.location=eye;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
bpy.context.scene.render.resolution_x=960;bpy.context.scene.render.resolution_y=540;bpy.context.scene.render.resolution_percentage=100
projections=[]
for name in ('GUEST_C10_SOUTHEAST_ENTRY_JAMB_WEST','GUEST_C10_SOUTHEAST_ENTRY_JAMB_EAST','GUEST_C10_SOUTHEAST_ENTRY_HEAD'):
    ob=bpy.data.objects[name];eo=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=eo.to_mesh()
    points=[world_to_camera_view(bpy.context.scene,cam,eo.matrix_world@v.co) for v in mesh.vertices]
    bounds=[[min(p[i] for p in points),max(p[i] for p in points)]for i in range(3)]
    projections.append({'object':name,'normalized_frame_bounds':bounds,'fully_inside_frame':bounds[0][0]>=0 and bounds[0][1]<=1 and bounds[1][0]>=0 and bounds[1][1]<=1 and bounds[2][0]>0})
    eo.to_mesh_clear()
dir=target-eye;first=probe.ray(eye,dir.normalized(),dir.length)
eye_hits=[probe.ray(eye,d,.13)for d in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))]
bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(camdata)
passed=not body and not any(eye_hits) and all(p['fully_inside_frame']for p in projections)
result={'candidate_sha256':routes.CANDIDATE_SHA,'status':'PASS_GEOMETRY_AND_FRAME_PROJECTION' if passed else 'FAIL',
 'source_camera_px':[466,465],'normal_eye_height_m':1.6,'actual_foot_world':foot,'body_failures':body,'eye_hits':eye_hits,
 'lowest_overhead':head,'target_first_hit':first,'door_frame_projection':projections,'rendered':False,'scene_saved':False,
 'note':'Projection confirms complete frame inclusion, not unobstructed photorealistic appearance. Root will render.'}
(R/'qa/guest-circulation10-navigation-entry-camera-retreat-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
if passed:(R/'qa/guest-circulation10-navigation-entry-camera-retreat.json').write_text(json.dumps(settings,indent=2),encoding='utf-8')
print('C10_ENTRY_RETREAT',json.dumps(result),flush=True)
assert passed
