"""Read actual rotation modes/quaternions, preserving the Euler-only mistake."""
from pathlib import Path
import bpy,json,hashlib,shutil
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'scene/Fallingwater_iteration10.blend'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='1e7b17d9c2396513f005724e50788bf834097eedb401b91a7f1030825e2c4ed9'
bpy.ops.wm.open_mainfile(filepath=str(SRC));scene=bpy.context.scene
names=json.loads((ROOT/'qa/checkpoint10-capture/capture.json').read_text())['changed_pose_or_lens_vs09']
data={}
for name in names:
    ob=scene.objects[name];q=ob.matrix_world.to_quaternion();eye=ob.matrix_world.translation
    data[name]={'location':list(ob.location),'rotation_mode':ob.rotation_mode,
                'rotation_euler':list(ob.rotation_euler),'rotation_quaternion':list(ob.rotation_quaternion),
                'target':list(eye+q@Vector((0,0,-1))),'lens':ob.data.lens,
                'shift_x':ob.data.shift_x,'shift_y':ob.data.shift_y,
                'clip_start':ob.data.clip_start,'clip_end':ob.data.clip_end,
                'exposure':float(ob.get('fw_exposure',0)),'room_id':ob['room_id'],
                'scope':'Actual saved10 rotation mode. Photography still pending.'}
target=ROOT/'data/camera-settings-iteration10-overrides.json'
backup=ROOT/'qa/camera-settings-iteration10-euler-only-failed.json';assert not backup.exists()
shutil.copy2(target,backup)
target.write_text(json.dumps(data,indent=2),encoding='utf8')
(ROOT/'qa/checkpoint10-capture-rotation-fix.json').write_text(json.dumps({'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),
 'camera_modes':{n:v['rotation_mode'] for n,v in data.items()},'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
 'reason':'Four master/bath cameras use QUATERNION; their inactive Euler channels do not represent their visible pose',
 'source_scene_changed':False},indent=2),encoding='utf8')
print(json.dumps({n:v['rotation_mode'] for n,v in data.items()}),flush=True)
