"""Read accepted intermediate scene data without mutating or saving Blender."""
from pathlib import Path
import sys,json,hashlib
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'scene/Fallingwater_navigation_candidate10a.blend'
EXPECTED='1e7b17d9c2396513f005724e50788bf834097eedb401b91a7f1030825e2c4ed9'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
assert len(rooms)==60
out=ROOT/'qa/checkpoint10-capture'
out.mkdir(exist_ok=False)
(out/'rooms.json').write_text(json.dumps(rooms,ensure_ascii=False,indent=2),encoding='utf8')
original=json.loads((ROOT/'data/camera-settings-reviewed.json').read_text(encoding='utf8'))
configs={};changes=[]
for room in rooms:
    for name in room['qa_cameras']:
        ob=scene.objects[name]
        old=original[name]
        eye=list(ob.location)
        target=list(ob.location+ob.rotation_euler.to_quaternion()@Vector((0,0,-1)))
        values={'location':eye,'rotation_euler':list(ob.rotation_euler),'target':target,
                'lens':ob.data.lens,'shift_x':ob.data.shift_x,'shift_y':ob.data.shift_y,
                'exposure':float(ob.get('fw_exposure',0)),'room_id':room['id'],
                'saved_scene_sha256':EXPECTED,'render_reviewed':False,
                'scope':'Saved actual camera. New complete image review remains pending.'}
        configs[name]=values
        if max(abs(eye[i]-old['location'][i]) for i in range(3))>1e-5 or abs(values['lens']-old['lens'])>1e-5:
            changes.append(name)
assert len(configs)==120
(out/'camera-settings-actual.json').write_text(json.dumps(configs,indent=2),encoding='utf8')
report={'source_scene_sha256':EXPECTED,'room_count':60,'saved_room_cameras':120,
        'changed_pose_or_lens_vs09':changes,
        'all_camera_count':sum(o.type=='CAMERA' for o in scene.objects),
        'object_count':len(scene.objects),'no_scene_write':True,
        'next':'Actual geometry checks for 120 current poses; images do not inherit acceptance from09.'}
(out/'capture.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report),flush=True)
