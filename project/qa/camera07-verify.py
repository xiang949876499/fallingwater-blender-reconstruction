"""Read-only full07 camera geometry and persisted configuration check."""
import hashlib
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import camera_review

scene_path = ROOT/'scene/Fallingwater_iteration07.blend'
config_path = ROOT/'qa/camera07e-settings-frozen.json'
active_path = ROOT/'data/camera-settings-reviewed.json'
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
scene_sha = sha(scene_path)
config_sha = sha(config_path)
assert scene_sha == 'bf50530009e4a93315915815473188c91d891272ef2d8e9e0169b704bd2e2f16'
assert config_sha == sha(active_path) == '4def78dcbae91f3292562f41796adec71c4680b64e04301f051fdc1833ce8666'
bpy.ops.wm.open_mainfile(filepath=str(scene_path))
scene = bpy.context.scene
scene.render.threads_mode = 'FIXED'
scene.render.threads = 4
rooms = json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
config = json.loads(config_path.read_text(encoding='utf-8'))
saved_rows = []
for name, expected in config.items():
    obj = scene.objects.get(name)
    if obj is None or obj.type != 'CAMERA':
        saved_rows.append({'camera': name, 'status': 'FAIL', 'reason': 'MISSING_SAVED_CAMERA'})
        continue
    actual_location = obj.matrix_world.translation
    wanted_quat = (Vector(expected['target'])-Vector(expected['location'])).to_track_quat('-Z','Y')
    actual_quat = obj.matrix_world.to_quaternion()
    errors = {
        'position_m': (actual_location-Vector(expected['location'])).length,
        'rotation_radians': actual_quat.rotation_difference(wanted_quat).angle,
        'lens_mm': abs(obj.data.lens-expected['lens']),
        'shift_x': abs(obj.data.shift_x-expected.get('shift_x',0)),
        'shift_y': abs(obj.data.shift_y-expected.get('shift_y',0)),
        'exposure_ev': abs(float(obj['fw_exposure'])-expected['exposure']) if 'fw_exposure' in obj else None,
    }
    matches = all(value is not None and value < .0001 for value in errors.values())
    saved_rows.append({'camera': name, 'status': 'SAVED_SETTINGS_MATCH' if matches else 'FAIL',
        'errors': errors,
        'actual': {'location': list(actual_location), 'quaternion': list(actual_quat), 'lens': obj.data.lens,
                   'shift_x': obj.data.shift_x, 'shift_y': obj.data.shift_y, 'exposure': obj.get('fw_exposure')},
        'expected': {k:expected.get(k,0) for k in ('location','target','lens','shift_x','shift_y','exposure')}})
saved_report = {
    'scene': str(scene_path), 'scene_sha256': scene_sha,
    'settings': str(config_path), 'settings_sha256': config_sha,
    'active_settings_same_bytes': sha(active_path)==config_sha,
    'blender_version': bpy.app.version_string, 'camera_count': len(saved_rows),
    'status': 'SAVED_SETTINGS_MATCH' if all(r['status']=='SAVED_SETTINGS_MATCH' for r in saved_rows) else 'FAIL',
    'scope': 'Read actual persisted camera world position, full rotation, lens, shift_x, shift_y and fw_exposure without applying settings or saving scene. Per-field tolerance 0.0001. No visual acceptance.',
    'cameras': saved_rows,
}
camera_review.write_json(ROOT/'qa/camera07-saved-settings-check.json', saved_report)
geometry_report = camera_review.verify(scene, rooms, config_path, ROOT/'qa/camera07-verification.json')
summary = {
    'scene_sha256': scene_sha, 'settings_sha256': config_sha,
    'saved_settings_status': saved_report['status'], 'saved_settings_rows':len(saved_rows),
    'geometry_status':geometry_report['status'], 'geometry_rows':len(geometry_report['cameras']),
    'rays_cast': geometry_report['rays_cast'], 'blender_version':bpy.app.version_string, 'threads':4,
    'scope':'Full integrated07 independently checked. Does not validate all120 framing, exposure, navigation or final visual quality.',
}
camera_review.write_json(ROOT/'qa/camera07-validation-summary.json', summary)
print('CAMERA07_VALIDATED '+json.dumps(summary), flush=True)
assert saved_report['status']=='SAVED_SETTINGS_MATCH'
assert geometry_report['status']=='GEOMETRY_ONLY_PASS'
assert len(saved_rows)==len(geometry_report['cameras'])==120
