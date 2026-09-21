"""Single-light self-emitter exclusion; diagnostic scene is never saved."""
import hashlib, json, sys, time
from pathlib import Path
import bpy
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import eevee_glass
SOURCE = ROOT / 'scene/Fallingwater_preview_iteration05.blend'
EXPECTED = 'b855de89492af8ae31ae4d53bb2674f518ea13cf2e8f1585b2b9a31b35511939'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s = bpy.context.scene
s.frame_set(1)
light = next(o for o in s.objects if o.type == 'LIGHT' and 'MAIN_B_BATH' in o.name)
filament = next(o for o in s.objects if 'MAIN_B_BATH' in o.name and o.name.endswith('_visible_emissive_filament'))
before = {k: getattr(light.data, k) for k in ['use_shadow', 'use_shadow_jitter', 'shadow_jitter_overblur', 'shadow_buffer_clip_start', 'shadow_soft_size', 'energy']}
before['location'] = list(light.matrix_world.translation)
before['blocker_collection'] = light.light_linking.blocker_collection.name if light.light_linking.blocker_collection else None
geometry_before, cycles_before = eevee_glass.geometry_signature(s), eevee_glass.cycles_signature()
assert light.light_linking.blocker_collection is None
blockers = bpy.data.collections.new('FW_DIAG_BATH_SELF_EMITTER_EXCLUSION')
blockers.objects.link(filament)
blockers.collection_objects[0].light_linking.link_state = 'EXCLUDE'
light.light_linking.blocker_collection = blockers
bpy.context.view_layer.update()
assert light.light_linking.blocker_collection == blockers
assert blockers.collection_objects[0].light_linking.link_state == 'EXCLUDE'
s.camera = s.objects['CAM_MAIN_B_BATH_B']
s.view_settings.exposure = .8
s.render.engine = 'BLENDER_EEVEE'
s.eevee.taa_render_samples = 32
s.render.threads_mode = 'FIXED'
s.render.threads = 4
s.render.resolution_x, s.render.resolution_y, s.render.resolution_percentage = 960, 540, 100
s.render.image_settings.file_format = 'PNG'
s.render.image_settings.color_mode = 'RGBA'
s.render.image_settings.color_depth = '8'
output = ROOT / 'qa/eevee-iteration05-shadow-own-filament-excluded'
assert not output.with_suffix('.png').exists(), 'Existing output preserved'
s.render.filepath = str(output.with_suffix('.png'))
report = {'source_sha256': EXPECTED, 'variant': 'single_bath_light_own_filament_shadow_excluded',
    'light': light.name, 'before': before, 'excluded_object': filament.name,
    'blocker_link_state': blockers.collection_objects[0].light_linking.link_state,
    'other_casters_preserved': True, 'light_energy_radius_position_unchanged': True,
    'glass_bulb_and_cage_preserved': True, 'geometry_hash_before': geometry_before,
    'cycles_original_surface_hash_before': cycles_before,
    'all_shadows_still_enabled': all(o.data.use_shadow for o in s.objects if o.type == 'LIGHT' and not o.hide_render),
    'exposure': .8, 'camera': s.camera.name, 'status': 'RUNNING',
    'production_saved': False, 'gi_rebaked': False,
    'scope': 'Diagnostic only. Shadow linking would also affect Cycles if persisted; no scene saved.'}
output.with_suffix('.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
start = time.perf_counter()
bpy.ops.render.render(write_still=True)
report.update(status='RENDERED', seconds=time.perf_counter()-start, path=s.render.filepath,
    sha256=hashlib.sha256(Path(s.render.filepath).read_bytes()).hexdigest(), visual_acceptance='NOT_REVIEWED',
    geometry_hash_after=eevee_glass.geometry_signature(s), cycles_original_surface_hash_after=eevee_glass.cycles_signature())
assert report['geometry_hash_after'] == geometry_before
assert report['cycles_original_surface_hash_after'] == cycles_before
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
output.with_suffix('.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('SHADOW_LINK_CANDIDATE ' + json.dumps(report), flush=True)
