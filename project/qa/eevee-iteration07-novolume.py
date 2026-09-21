"""Stage one: actual zero-VOLUME 07 preview, no bake and no artificial fill."""
import ast, hashlib, itertools, json, sys, time
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import eevee_preview
import eevee_glass
SOURCE = ROOT / 'scene/Fallingwater_iteration07.blend'
EXPECTED = 'bf50530009e4a93315915815473188c91d891272ef2d8e9e0169b704bd2e2f16'
OUT = ROOT / 'qa/eevee-iteration07-novolume'
OUT.mkdir(exist_ok=True)
PNG = OUT / 'CAM_MAIN_L3_STUDY_B_NO_VOLUME_EV2p4.png'
BLEND = OUT / 'Fallingwater_preview_iteration07_no_volume.blend'
REPORT = OUT / 'baseline-report.json'
tree = ast.parse((ROOT / 'qa/eevee-iteration06-coverage.py').read_text(encoding='utf-8'))
names = {'sha', 'properties', 'light_state', 'probe_state', 'object_state', 'bounds'}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names], type_ignores=[]), 'inspection_helpers', 'exec'))
assert sha(SOURCE) == EXPECTED and not PNG.exists() and not BLEND.exists()
report = {'status': 'OPENING', 'source_scene': str(SOURCE), 'source_sha256': EXPECTED,
    'production_saved': False, 'stage': 'NO_VOLUME_BASELINE', 'bake_count': 0, 'fill_lights_added': [],
    'helper_hashes': {n: sha(ROOT / 'scripts' / n) for n in ('eevee_preview.py', 'eevee_glass.py')}}

def checkpoint(status):
    report['status'] = status
    REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('NO_VOLUME_' + status, flush=True)

checkpoint('OPENING')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s = bpy.context.scene
s.frame_set(48)
s.render.threads_mode = 'FIXED'
s.render.threads = 4
bpy.context.view_layer.update()
before_lights = light_state(s)
before_objects = object_state(s)
before_world = {n.name: n.inputs['Strength'].default_value for n in s.world.node_tree.nodes if n.type == 'BACKGROUND'}
before_cycles = eevee_glass.cycles_signature()
before_geometry = eevee_glass.geometry_signature(s)
report['settings'] = eevee_preview.configure(s, 32, fast_gi=False)
report['glass_preview'] = eevee_glass.apply(s)
volume_objects = [o for o in bpy.data.objects if o.type == 'LIGHT_PROBE' and o.data.type == 'VOLUME']
report['candidate_volume_objects_removed'] = [o.name for o in volume_objects]
for obj in volume_objects:
    bpy.data.objects.remove(obj, do_unlink=True)
unused_volume_data = [d for d in bpy.data.lightprobes if d.type == 'VOLUME' and d.users == 0]
report['orphan_volume_datablocks_removed'] = [d.name for d in unused_volume_data]
for data in unused_volume_data:
    bpy.data.lightprobes.remove(data)
assert not any(o.type == 'LIGHT_PROBE' and o.data.type == 'VOLUME' for o in bpy.data.objects)
assert not any(d.type == 'VOLUME' for d in bpy.data.lightprobes)
report['actual_volume_object_count'] = 0
report['actual_volume_datablock_count'] = 0
report['source_had_no_volumes'] = not volume_objects and not unused_volume_data
s.camera = s.objects['CAM_MAIN_L3_STUDY_B']
s.view_settings.exposure = 2.4
s.render.resolution_x, s.render.resolution_y, s.render.resolution_percentage = 960, 540, 100
s.render.image_settings.file_format = 'PNG'
s.render.image_settings.color_mode = 'RGBA'
s.render.image_settings.color_depth = '8'
bpy.context.view_layer.update()
after_objects = object_state(s)
assert all(after_objects[n] == v for n, v in before_objects.items() if n not in report['candidate_volume_objects_removed'])
assert light_state(s) == before_lights
assert {n.name: n.inputs['Strength'].default_value for n in s.world.node_tree.nodes if n.type == 'BACKGROUND'} == before_world
assert eevee_glass.cycles_signature() == before_cycles
assert eevee_glass.geometry_signature(s) == before_geometry
report.update(camera=s.camera.name, camera_location=list(s.camera.location), camera_rotation=list(s.camera.rotation_euler),
    camera_matrix=[list(row) for row in s.camera.matrix_world], lens=s.camera.data.lens,
    frame=48, exposure=2.4, resolution=[960, 540], samples=32, cpu_preparation_threads=4,
    view_transform=s.view_settings.view_transform, look=s.view_settings.look, gamma=s.view_settings.gamma,
    raytracing=s.eevee.use_raytracing, fast_gi=s.eevee.use_fast_gi, world_background_strengths=before_world,
    original_light_state=before_lights, light_settings_and_links_unchanged=True,
    original_objects_unchanged_except_removed_volumes=True,
    cycles_glass_surface_hash_preserved=before_cycles, glazing_geometry_hash_preserved=before_geometry,
    candidate_probe_state=probe_state(s), added_objects=sorted(set(after_objects)-set(before_objects)),
    scope='Independent zero-VOLUME EEVEE baseline. World/distant fallback still exists. Not equivalent to previously setting volume intensity to zero. No indirect fill or light/shadow changes.')
s['fw_eevee_indirect_mode'] = 'NO_VOLUME_WORLD_ONLY_BASELINE'
s['fw_eevee_candidate_scope'] = report['scope']
s['eevee_probe_bake_json'] = '[]'
s['eevee_probe_bake_limitations'] = 'No VOLUME objects or caches. All levels NOT_BAKED. World/distant fallback remains.'
s['fw_eevee_level_status_json'] = json.dumps({n: 'NOT_BAKED' for n in ('MAIN_B', 'MAIN_L1', 'MAIN_L2', 'MAIN_L3', 'GUEST_L1', 'GUEST_B1', 'GUEST_L2')})
checkpoint('RENDERING')
s.render.filepath = str(PNG)
start = time.perf_counter()
bpy.ops.render.render(write_still=True)
report.update(render_seconds=time.perf_counter()-start, png=str(PNG), png_sha256=sha(PNG), visual_acceptance='NOT_REVIEWED')
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
report.update(candidate_blend=str(BLEND), candidate_sha256=sha(BLEND), source_unchanged=sha(SOURCE) == EXPECTED)
assert report['source_unchanged']
assert report['helper_hashes'] == {n: sha(ROOT / 'scripts' / n) for n in report['helper_hashes']}
checkpoint('RENDERED_SAVED')
print('NO_VOLUME_COMPLETE ' + json.dumps({k: report[k] for k in ('render_seconds', 'png_sha256', 'candidate_sha256')}), flush=True)
