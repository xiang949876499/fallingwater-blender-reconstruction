"""Read persisted full08 cameras before independently testing their actual poses.

This does not apply settings, render, save a scene, or edit production config.
"""
import copy
import hashlib
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import camera_review

SCENE_SHA = 'c5cd501e4c8ae0205ecb2437cd2d06d0c92bcc9a87e7d93d3986aeef976070d7'
SETTINGS_SHA = 'f011c9462431e12137a49d3829a85586da0804a5a934086e03d7143c7d5dc1d0'
scene_path = ROOT / 'scene/Fallingwater_iteration08.blend'
active_path = ROOT / 'data/camera-settings-reviewed.json'
frozen_path = ROOT / 'qa/camera08-settings-frozen.json'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

assert sha(scene_path) == SCENE_SHA
assert sha(active_path) == SETTINGS_SHA
frozen_path.write_bytes(active_path.read_bytes())
assert sha(frozen_path) == SETTINGS_SHA
bpy.ops.wm.open_mainfile(filepath=str(scene_path))
scene = bpy.context.scene
scene.render.threads_mode = 'FIXED'
scene.render.threads = 4
rooms = json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
config = json.loads(frozen_path.read_text(encoding='utf-8'))
assert len(config) == 120
saved_rows = []
actual_config = {}

# This loop only reads cameras. No integrate(), transform assignment or save.
for name, expected in config.items():
    obj = scene.objects.get(name)
    if obj is None or obj.type != 'CAMERA':
        saved_rows.append({'camera': name, 'status': 'FAIL', 'reason': 'MISSING_SAVED_CAMERA'})
        continue
    actual_location = obj.matrix_world.translation.copy()
    actual_quat = obj.matrix_world.to_quaternion()
    wanted_direction = Vector(expected['target']) - Vector(expected['location'])
    wanted_quat = wanted_direction.to_track_quat('-Z', 'Y')
    actual_exposure = float(obj['fw_exposure']) if 'fw_exposure' in obj else None
    errors = {
        'position_m': (actual_location - Vector(expected['location'])).length,
        'rotation_radians': actual_quat.rotation_difference(wanted_quat).angle,
        'lens_mm': abs(obj.data.lens - expected['lens']),
        'shift_x': abs(obj.data.shift_x - expected.get('shift_x', 0)),
        'shift_y': abs(obj.data.shift_y - expected.get('shift_y', 0)),
        'exposure_ev': abs(actual_exposure - expected['exposure']) if actual_exposure is not None else None,
    }
    matches = all(value is not None and value < .0001 for value in errors.values())
    actual = {
        'location': list(actual_location), 'quaternion': list(actual_quat),
        'lens': obj.data.lens, 'shift_x': obj.data.shift_x,
        'shift_y': obj.data.shift_y, 'exposure': actual_exposure,
    }
    saved_rows.append({
        'camera': name, 'status': 'SAVED_SETTINGS_MATCH' if matches else 'FAIL',
        'errors': errors, 'actual': actual,
        'expected': {k: expected.get(k, 0) for k in ('location', 'target', 'lens', 'shift_x', 'shift_y', 'exposure')},
    })
    # Geometry uses actual saved float poses, not a re-applied expected pose.
    # Stored ground is deliberately retained as a reference to detect floor changes.
    values = copy.deepcopy(expected)
    values.update({k: actual[k] for k in ('location', 'lens', 'shift_x', 'shift_y', 'exposure')})
    values['target'] = list(actual_location + (actual_quat @ Vector((0, 0, -1))) * wanted_direction.length)
    actual_config[name] = values

saved_report = {
    'scene': str(scene_path), 'scene_sha256': SCENE_SHA,
    'settings': str(frozen_path), 'settings_sha256': SETTINGS_SHA,
    'active_settings_same_bytes': sha(active_path) == SETTINGS_SHA,
    'blender_version': bpy.app.version_string, 'camera_count': len(saved_rows),
    'status': 'SAVED_SETTINGS_MATCH' if all(r['status'] == 'SAVED_SETTINGS_MATCH' for r in saved_rows) else 'FAIL',
    'scope': 'Actual persisted camera world position, full quaternion including roll, lens, shift_x, shift_y and fw_exposure read before any comparison. Per-field tolerance 0.0001. Never applied config or saved scene. No visual acceptance.',
    'cameras': saved_rows,
}
camera_review.write_json(ROOT / 'qa/camera08-saved-settings-check.json', saved_report)
print('CAMERA08_SAVED ' + json.dumps({'status': saved_report['status'], 'count': len(saved_rows)}), flush=True)
actual_path = ROOT / 'qa/camera08-saved-geometry-input.json'
camera_review.write_json(actual_path, actual_config)
geometry_report = camera_review.verify(scene, rooms, actual_path, ROOT / 'qa/camera08-verification.json')
geometry_report.update({
    'production_settings_sha256': SETTINGS_SHA,
    'frozen_settings': str(frozen_path),
    'geometry_pose_source': 'Actual persisted world pose/lens/shifts/exposure read first; target reconstructed along actual camera -Z at the expected target distance. Stored ground is the frozen reference. No camera mutation.',
    'saved_settings_status': saved_report['status'],
    'method_module_sha256': sha(ROOT / 'scripts/camera_review.py'),
})
camera_review.write_json(ROOT / 'qa/camera08-verification.json', geometry_report)
summary = {
    'scene_sha256': SCENE_SHA, 'settings_sha256': SETTINGS_SHA,
    'saved_settings_status': saved_report['status'], 'saved_settings_rows': len(saved_rows),
    'geometry_status': geometry_report['status'], 'geometry_rows': len(geometry_report['cameras']),
    'rays_cast': geometry_report['rays_cast'], 'geometry': geometry_report['geometry'],
    'blender_version': bpy.app.version_string, 'threads': 4,
    'outside_count': sum(r['outside_current_room_polygon'] for r in geometry_report['cameras']),
    'outside_flags_all_match': all(r['stored_outside_flag_matches'] for r in geometry_report['cameras']),
    'geometry_input_is_actual_saved_pose': True,
    'active_settings_unchanged': sha(active_path) == SETTINGS_SHA,
    'scene_unchanged': sha(scene_path) == SCENE_SHA,
    'scope': 'Full integrated08 checked independently. Room geometry excludes vegetation. Legacy 15-ray view diagnostic excludes shift, and is not visual acceptance. Does not validate navigation or full120 framing/exposure/photo quality.',
    'full08_visual_status': 'NOT_REVIEWED_BY_THIS_CHECK',
    'final_visual_quality_accepted': False,
}
camera_review.write_json(ROOT / 'qa/camera08-validation-summary.json', summary)
print('CAMERA08_VALIDATED ' + json.dumps(summary), flush=True)
assert saved_report['status'] == 'SAVED_SETTINGS_MATCH'
assert geometry_report['status'] == 'GEOMETRY_ONLY_PASS'
assert len(saved_rows) == len(geometry_report['cameras']) == 120
assert summary['active_settings_unchanged'] and summary['scene_unchanged']
