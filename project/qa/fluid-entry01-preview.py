"""One actual Cycles view of the entry calibration, no scene overwrite."""
import json
import sys
import time
from pathlib import Path
import bpy
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import fluid_water
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'scene/Fallingwater_fluid_entry01.blend'))
scene = bpy.context.scene
scene.frame_set(36)
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.threads_mode = 'FIXED'
scene.render.threads = 8
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
lip = Vector((2.4, -2.83, 0))
down = Vector((-.882352948, -.470588356, 0))
across = Vector((.470588356, -.882352948, 0))
target = lip - down * 1.35 + across * .9
target.z = -3.055
eye = target + down * 2.05 - across * 2.25 + Vector((0, 0, 2.0))
scene.camera = fluid_water._camera('CAM_ENTRY01_REVIEW', eye, target, 52)
scene.render.filepath = str(ROOT / 'qa/fluid-entry01-frame036.png')
started = time.perf_counter()
bpy.ops.render.render(write_still=True)
fluid_water._write(ROOT / 'qa/fluid-entry01-render.json', {
    'frame': 36, 'path': scene.render.filepath, 'camera_position': list(eye),
    'camera_target': list(target), 'width': 960, 'height': 540, 'samples': 24,
    'device': 'CPU8', 'seconds': time.perf_counter() - started,
    'scope': 'Actual local inlet cache view only; open domain edges remain visible, no seam acceptance'})
