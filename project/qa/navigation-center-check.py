"""Check free-view aim against Blender's independent camera projection API."""
import hashlib
import json
import sys
from pathlib import Path
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import navigation
source=ROOT/'scene/Fallingwater_iteration05.blend'
before=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
original=scene.objects['CAM_MAIN_B_BATH_B']
camera=original.copy();camera.data=original.data.copy()
scene.collection.objects.link(camera)
tests=[]
for shift_x,shift_y in [(0,0),(0,-.58),(.20,.35),(-.15,-.44966)]:
    camera.data.shift_x=shift_x;camera.data.shift_y=shift_y
    rotation=navigation.exploration_rotation(camera,scene)
    forward=rotation@Vector((0,0,-1))
    target=camera.matrix_world.translation+forward*2
    projected=world_to_camera_view(scene,camera,target)
    # Independent project-to-film API must put the new exploration ray at center.
    error=max(abs(projected.x-.5),abs(projected.y-.5))
    tests.append({'shift':[shift_x,shift_y],'projected_center':list(projected),
                  'maximum_center_error':error,'status':'PASS' if error<1e-6 else 'FAIL'})
    if error>=1e-6:raise AssertionError(tests[-1])
after=hashlib.sha256(source.read_bytes()).hexdigest()
assert before==after
report={'scene_sha256':before,'tests':tests,'source_scene_unchanged':True,
        'status':'PASS_API_MATH_ONLY','GUI_status':'NOT_RUN',
        'scope':'Free-view central direction tested against actual Blender camera projection. Does not reproduce optical shift across the full frame or certify GUI controls.'}
(ROOT/'qa/navigation-center-check.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(report)
