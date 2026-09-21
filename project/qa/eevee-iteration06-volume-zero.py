"""One bounded Study B radiance ablation; no bake, source save or other lighting edits."""
import hashlib
import json
import sys
import time
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import eevee_glass

SOURCE = ROOT / 'scene/Fallingwater_preview_iteration06.blend'
EXPECTED = 'e317241899808995f049e8d3343eac96c591cbecfddaa980949d6babb51ccce6'
OUTPUT = ROOT / 'qa/eevee-iteration06-volume-zero-study.png'
REPORT = OUTPUT.with_suffix('.json')

def light_state(scene):
    return {o.name: {'matrix': [list(r) for r in o.matrix_world],
            'energy': o.data.energy, 'color': list(o.data.color),
            'type': o.data.type, 'shadow': o.data.use_shadow,
            'blocker_collection': o.light_linking.blocker_collection.name
                if o.light_linking.blocker_collection else None}
            for o in scene.objects if o.type == 'LIGHT'}

def volume_state(scene):
    result = {}
    for o in scene.objects:
        if o.type != 'LIGHT_PROBE' or o.data.type != 'VOLUME':
            continue
        props = {}
        for p in o.data.bl_rna.properties:
            if p.type not in {'BOOLEAN', 'INT', 'FLOAT', 'STRING', 'ENUM'}:
                continue
            value = getattr(o.data, p.identifier)
            props[p.identifier] = list(value) if getattr(p, 'is_array', False) else value
        result[o.name] = {'matrix': [list(r) for r in o.matrix_world], 'properties': props}
    return result

assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
assert not OUTPUT.exists(), 'Preserve prior evidence'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s = bpy.context.scene
s.frame_set(1)
assert s.render.engine == 'BLENDER_EEVEE' and s.eevee.use_raytracing and not s.eevee.use_fast_gi
s.camera = s.objects['CAM_MAIN_L3_STUDY_B']
s.view_settings.exposure = 2.4
s.eevee.taa_render_samples = 32
s.render.threads_mode = 'FIXED'
s.render.threads = 4
s.render.resolution_x, s.render.resolution_y, s.render.resolution_percentage = 960, 540, 100
s.render.image_settings.file_format = 'PNG'
s.render.image_settings.color_mode = 'RGBA'
s.render.image_settings.color_depth = '8'
before_lights = light_state(s)
before_volumes = volume_state(s)
assert len(before_volumes) == 7
assert all(v['properties']['intensity'] == 1.0 for v in before_volumes.values())
before_cycles = eevee_glass.cycles_signature()
before_geometry = eevee_glass.geometry_signature(s)
for name in before_volumes:
    s.objects[name].data.intensity = 0.0
after_volumes = volume_state(s)
for name, state in before_volumes.items():
    after = after_volumes[name]
    assert after['properties']['intensity'] == 0.0
    after['properties']['intensity'] = state['properties']['intensity']
    assert state == after, 'Unexpected probe mutation: ' + name
    after['properties']['intensity'] = 0.0
assert light_state(s) == before_lights
assert eevee_glass.cycles_signature() == before_cycles
assert eevee_glass.geometry_signature(s) == before_geometry
report = {
    'status': 'RUNNING', 'source_sha256': EXPECTED,
    'variant': 'all_seven_volume_intensity_zero_only',
    'camera': s.camera.name, 'camera_location': list(s.camera.location),
    'camera_rotation': list(s.camera.rotation_euler), 'lens': s.camera.data.lens,
    'frame': s.frame_current, 'exposure': s.view_settings.exposure,
    'view_transform': s.view_settings.view_transform, 'look': s.view_settings.look,
    'resolution': [960, 540], 'samples': 32, 'cpu_preparation_threads': 4,
    'raytracing': s.eevee.use_raytracing, 'fast_gi': s.eevee.use_fast_gi,
    'before_lights': before_lights, 'lights_unchanged': True,
    'before_volumes': before_volumes, 'after_volumes': after_volumes,
    'cycles_glass_signature': before_cycles, 'glazing_geometry_signature': before_geometry,
    'invariants_passed': True, 'gi_rebaked': False, 'production_saved': False,
    'interpretation_limit': 'Intensity scales cached radiance but leaves volume bounds, validity, visibility and selection intact.'}
REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
s.render.filepath = str(OUTPUT)
print('STUDY_VOLUME_ZERO_START', flush=True)
started = time.perf_counter()
bpy.ops.render.render(write_still=True)
report.update(status='RENDERED', seconds=time.perf_counter()-started,
    path=str(OUTPUT), sha256=hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
    visual_acceptance='NOT_REVIEWED')
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
report['source_unchanged'] = True
REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
print('STUDY_VOLUME_ZERO_COMPLETE ' + json.dumps({'seconds': report['seconds'], 'sha256': report['sha256']}), flush=True)
