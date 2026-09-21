"""Frozen 07 integration check: one MAIN_L3 cache and one matched Study frame."""
import ast, ctypes, hashlib, itertools, json, math, sys, time
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import eevee_glass
import eevee_preview
SOURCE = ROOT / 'scene/Fallingwater_iteration07.blend'
EXPECTED = 'bf50530009e4a93315915815473188c91d891272ef2d8e9e0169b704bd2e2f16'
OUT = ROOT / 'qa/eevee-iteration07-study'
OUT.mkdir(exist_ok=True)
REPORT = OUT / 'report.json'
PNG = OUT / 'CAM_MAIN_L3_STUDY_B_EV2p4.png'
BLEND = OUT / 'Fallingwater_preview_iteration07_study.blend'
TARGET = 'FW_PROBE_MAIN_L3'
tree = ast.parse((ROOT / 'qa/eevee-iteration06-coverage.py').read_text(encoding='utf-8'))
names = {'sha', 'properties', 'light_state', 'probe_state', 'object_state', 'bounds'}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names], type_ignores=[]), 'inspection_helpers', 'exec'))
tree = ast.parse((ROOT / 'qa/eevee-iteration06-density.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'MemoryStatus'], type_ignores=[]), 'memory_inspection', 'exec'))

assert sha(SOURCE) == EXPECTED
assert not PNG.exists() and not BLEND.exists(), 'Preserve existing evidence'
report = {'status': 'STARTED', 'source_scene': str(SOURCE), 'source_sha256': EXPECTED,
    'production_saved': False, 'visual_acceptance': 'NOT_RUN',
    'scope': '07 structural/sky integration check; one MAIN_L3 cache versus previous seven-volume 06 preview. Not a single-variable causal test.',
    'helper_hashes': {name: sha(ROOT / 'scripts' / name) for name in ('eevee_preview.py', 'eevee_glass.py')}}

def checkpoint(status):
    report['status'] = status
    REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('STUDY07_' + status, flush=True)

checkpoint('OPENING')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s = bpy.context.scene
s.frame_set(48)
s.render.threads_mode = 'FIXED'
s.render.threads = 4
bpy.context.view_layer.update()
before_lights = light_state(s)
before_objects = object_state(s)
before_probes = probe_state(s)
assert not any(o.type == 'LIGHT_PROBE' and o.data.type == 'VOLUME' for o in s.objects), 'Source must have no pre-existing irradiance cache'
before_cycles = eevee_glass.cycles_signature()
before_glass_geometry = eevee_glass.geometry_signature(s)
report['settings'] = eevee_preview.configure(s, 32, fast_gi=False)
report['glass_preview'] = eevee_glass.apply(s)
assert eevee_glass.cycles_signature() == before_cycles
assert eevee_glass.geometry_signature(s) == before_glass_geometry
s.camera = s.objects['CAM_MAIN_L3_STUDY_B']
s.view_settings.exposure = 2.4
s.render.resolution_x, s.render.resolution_y, s.render.resolution_percentage = 960, 540, 100
s.render.image_settings.file_format = 'PNG'
s.render.image_settings.color_mode = 'RGBA'
s.render.image_settings.color_depth = '8'
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()
rooms = json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
groups = {}
for r in rooms:
    if any(k in str(r.get('kind', '')).lower() for k in ('terrace', 'pool', 'foundation', 'exterior', 'outdoor', 'path', 'balcony', 'roof')):
        continue
    groups.setdefault(r['building'] + '_' + r['level'], []).append(r)
assert len(groups) == 7 and 'MAIN_L3' in groups
room_ids = {r['id'] for r in rooms if r['building'] == 'MAIN' and r['level'] == 'L3'}
slab = s.objects['MAIN_L3_STUDY_slab'].evaluated_get(deps)
floor = bounds(slab, list(slab.bound_box))[0][2]
geometry = []
for original in s.objects:
    if original.type != 'MESH' or original.hide_render:
        continue
    if not (original.name.startswith('MAIN_L3') or original.get('room_id') in room_ids):
        continue
    obj = original.evaluated_get(deps)
    bb = bounds(obj, list(obj.bound_box))
    if bb[1][2] < floor - .001:
        continue
    old_low = bb[0][2]
    bb[0][2] = max(bb[0][2], floor)
    geometry.append({'object': original.name, 'bounds': bb, 'room_id': original.get('room_id'),
        'cross_level_geometry_clipped_to_actual_slab_bottom': old_low < floor - .001})
assert len(geometry) > 20
base_low = [min(g['bounds'][0][i] for g in geometry) for i in range(3)]
base_high = [max(g['bounds'][1][i] for g in geometry) for i in range(3)]
coords = [p for room in groups['MAIN_L3'] for p in room['polygon']]
room_xy = [[min(p[i] for p in coords) - .15 for i in range(2)], [max(p[i] for p in coords) + .15 for i in range(2)]]
for i in range(2):
    base_low[i] = min(base_low[i], room_xy[0][i])
    base_high[i] = max(base_high[i], room_xy[1][i])
for i in range(3):
    base_low[i] = min(base_low[i], s.camera.matrix_world.translation[i])
    base_high[i] = max(base_high[i], s.camera.matrix_world.translation[i])
target_spacing = [.8, .8, .32]
margin = [1.35 * v + .05 for v in target_spacing]
low = [v - m for v, m in zip(base_low, margin)]
high = [v + m for v, m in zip(base_high, margin)]
scale = [(b - a) / 2 for a, b in zip(low, high)]
resolution = [max(4, math.ceil((b - a) / h) - 1) for a, b, h in zip(low, high, target_spacing)]
spacing = [(b - a) / (r + 1) for a, b, r in zip(low, high, resolution)]
assert all(a <= b + 1e-7 for a, b in zip(spacing, target_spacing))
assert max(resolution) <= 64 and math.prod(resolution) <= 40000
normal_bias, view_bias = .3, 0.
required = [(1 + normal_bias + view_bias) * d for d in spacing]
assert all(m > r + .04 for m, r in zip(margin, required))
points = []
inv = s.camera.calc_matrix_camera(deps, x=960, y=540).inverted()
for label, (x, y) in [('wall_middle', (720, 275)), ('wall_upper', (720, 125)), ('wall_lower', (710, 454))]:
    v = inv @ Vector((x * 2 / 960 - 1, 1 - y * 2 / 540, -1, 1))
    d = (s.camera.matrix_world.to_3x3() @ Vector((v.x / v.w, v.y / v.w, v.z / v.w))).normalized()
    hit, location, normal, index, obj, matrix = s.ray_cast(deps, s.camera.matrix_world.translation, d, distance=100)
    assert hit
    points.append({'label': label, 'pixel': [x, y], 'world': list(location), 'object': obj.name, 'face': index, 'normal': list(normal)})
points.append({'label': 'StudyB_camera', 'world': list(s.camera.matrix_world.translation)})
for p in points:
    p['distance_to_nearest_bound_in_cells'] = [min(v-a, b-v) / d for v, a, b, d in zip(p['world'], low, high, spacing)]
    assert min(p['distance_to_nearest_bound_in_cells']) > 1 + normal_bias + view_bias
profile = {'schema': 'fw.eeveel3.practical.v2', 'source_sha256': EXPECTED, 'probe': TARGET,
    'frame': 48, 'base_actual_geometry_bounds': [base_low, base_high], 'bounds': [low, high],
    'resolution': resolution, 'nominal_spacing_m': spacing, 'surfel_density': 32,
    'surfel_spacing_m': max(scale) / 32, 'requested_max_spacing_m': target_spacing,
    'margin_m': margin, 'minimum_bias_safe_margin_m': required,
    'coverage_rule': 'margin > (1 + abs(normal_bias) + abs(view_bias)) * spacing; nominal samples use resolution + 1 denominator; padding samples contain distant/world light.',
    'world_padding_source': 'https://raw.githubusercontent.com/blender/blender/v5.2.1/source/blender/draw/engines/eevee/shaders/eevee_lightprobe_volume_load.bsl.hh',
    'sampling_source': 'https://raw.githubusercontent.com/blender/blender/v5.2.1/source/blender/draw/engines/eevee/shaders/eevee_lightprobe_volume.bsl.hh',
    'geometry_selection': 'Actual renderable MAIN_L3-prefixed or L3-room-tagged meshes, clipped below actual evaluated Study slab bottom; union with embedded L3 interior room XY domain and saved camera.',
    'actual_floor_slab_bottom_z': floor, 'embedded_interior_room_xy_bounds': room_xy,
    'selected_geometry': geometry, 'critical_point_margin_checks': points,
    'production_adopted': False, 'visual_acceptance': 'NOT_REVIEWED'}
(OUT / 'profile.json').write_text(json.dumps(profile, indent=2), encoding='utf-8')
report['profile'] = profile
checkpoint('PREFLIGHT')
cap_low, cap_high = np.asarray(low) - 20, np.asarray(high) + 20
rows = []
for original in s.objects:
    if original.type != 'MESH' or original.hide_render:
        continue
    obj = original.evaluated_get(deps)
    bb = np.asarray([obj.matrix_world @ Vector(p) for p in obj.bound_box])
    if np.any(bb.max(axis=0) < cap_low) or np.any(bb.min(axis=0) > cap_high):
        continue
    mesh = obj.data
    if not mesh.polygons:
        continue
    mesh.calc_loop_triangles()
    v = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
    mesh.vertices.foreach_get('co', v)
    m = np.asarray(obj.matrix_world, dtype=np.float64)
    v = v.reshape(-1, 3) @ m[:3, :3].T + m[:3, 3]
    idx = np.empty(len(mesh.loop_triangles) * 3, dtype=np.int32)
    mesh.loop_triangles.foreach_get('vertices', idx)
    tri = v[idx.reshape(-1, 3)]
    mask = np.all(tri.max(axis=1) >= cap_low, axis=1) & np.all(tri.min(axis=1) <= cap_high, axis=1)
    tri = tri[mask]
    projected = float(np.abs(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])).sum() * .5) if len(tri) else 0
    rows.append({'object': original.name, 'vertices': len(mesh.vertices), 'triangles': len(mesh.loop_triangles),
        'overlapping_triangles': int(mask.sum()), 'projected_area_m2': projected})
converted_density = 32 / max(scale)
projected = sum(r['projected_area_m2'] for r in rows)
count = math.ceil(projected * converted_density ** 2)
allowance = count * 224 * 6 + math.prod(resolution) * 1024
memory = MemoryStatus()
memory.length = ctypes.sizeof(memory)
assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory))
guard = min(8 * 1024 ** 3, int(memory.available * .35))
budget = {'mesh_count': len(rows), 'vertices': sum(r['vertices'] for r in rows),
    'triangles': sum(r['triangles'] for r in rows), 'overlapping_triangles': sum(r['overlapping_triangles'] for r in rows),
    'projected_area_m2': projected, 'density32_per_m': converted_density, 'estimated_surfels': count,
    'surfel_bytes': 224, 'planning_allowance_bytes': allowance, 'guard_bytes': guard,
    'available_physical_bytes': memory.available, 'grid_sample_count': math.prod(resolution),
    'method': 'World triangle projection, capture AABB culling; 6x main surfel buffer + 1024B per grid sample. Estimate, not measured GPU peak.'}
(OUT / 'preflight.json').write_text(json.dumps(budget, indent=2), encoding='utf-8')
report['resource_preflight'] = budget
print('STUDY07_BUDGET ' + json.dumps(budget), flush=True)
if allowance > guard:
    checkpoint('RESOURCE_PREFLIGHT_REJECTED')
    raise RuntimeError('Budget guard exceeded; no bake performed')
collection = bpy.data.collections.new('75_IRRADIANCE_PROBES')
s.collection.children.link(collection)
data = bpy.data.lightprobes.new(TARGET, 'VOLUME')
probe = bpy.data.objects.new(TARGET, data)
collection.objects.link(probe)
probe.location = [(a + b) / 2 for a, b in zip(low, high)]
probe.scale = scale
data.resolution_x, data.resolution_y, data.resolution_z = resolution
for name, value in {'normal_bias': .3, 'view_bias': 0., 'facing_bias': .5, 'validity_threshold': .4,
    'dilation_threshold': .5, 'dilation_radius': 1, 'surface_bias': .05, 'escape_bias': .1,
    'bake_samples': 64, 'surfel_density': 32, 'capture_distance': 20., 'capture_world': True,
    'capture_indirect': True, 'capture_emission': True, 'intensity': 1.}.items():
    setattr(data, name, value)
probe['room_ids'] = json.dumps([r['id'] for r in groups['MAIN_L3']])
bpy.context.view_layer.update()
after_objects = object_state(s)
assert all(after_objects[name] == value for name, value in before_objects.items())
assert light_state(s) == before_lights
assert eevee_glass.cycles_signature() == before_cycles
assert eevee_glass.geometry_signature(s) == before_glass_geometry
assert [o.name for o in s.objects if o.type == 'LIGHT_PROBE' and o.data.type == 'VOLUME'] == [TARGET]
levels = {level: 'READY_TO_BAKE' if level == 'MAIN_L3' else 'NOT_BAKED' for level in groups}
report.update(camera=s.camera.name, camera_location=list(s.camera.location), camera_rotation=list(s.camera.rotation_euler),
    lens=s.camera.data.lens, camera_matrix=[list(row) for row in s.camera.matrix_world], frame=48,
    exposure=2.4, resolution=[960, 540], samples=32, cpu_preparation_threads=4,
    view_transform=s.view_settings.view_transform, look=s.view_settings.look, gamma=s.view_settings.gamma,
    raytracing=s.eevee.use_raytracing, fast_gi=s.eevee.use_fast_gi,
    world_background_strengths={n.name: n.inputs['Strength'].default_value for n in s.world.node_tree.nodes if n.type == 'BACKGROUND'},
    before_light_state=before_lights, light_settings_and_links_unchanged=True,
    source_object_transforms_and_visibility_unchanged=True, added_objects=sorted(set(after_objects)-set(before_objects)),
    source_probe_state=before_probes, candidate_probe_state=probe_state(s), level_status=levels,
    cycles_glass_surface_hash_preserved=before_cycles, glazing_geometry_hash_preserved=before_glass_geometry,
    cycles_scope='Original glass Cycles shader branch and geometry preserved. No self-emitter shadow exclusions applied; all original lights and shadow links retained.',
    actual_surface_bias_m=data.surface_bias * min(v/r for v, r in zip(probe.scale, resolution)),
    actual_escape_bias_m=data.escape_bias * min(v/r for v, r in zip(probe.scale, resolution)))
for obj in bpy.context.selected_objects:
    obj.select_set(False)
probe.select_set(True)
bpy.context.view_layer.objects.active = probe
assert bpy.context.selected_objects == [probe]
checkpoint('BAKING')
start = time.perf_counter()
result = bpy.ops.object.lightprobe_cache_bake(subset='ACTIVE')
report['bake_seconds'] = time.perf_counter() - start
report['bake_operator_result'] = sorted(result)
assert result == {'FINISHED'}
levels['MAIN_L3'] = 'BAKED_VISUAL_NOT_REVIEWED'
assert light_state(s) == before_lights
assert probe_state(s) == report['candidate_probe_state']
s['eevee_probe_bake_json'] = json.dumps([{'name': TARGET, 'status': 'PASS', 'frame': 48,
    'bounds': [low, high], 'resolution': resolution, 'actual_grid_spacing_m': spacing,
    'bake_samples': 64, 'surfel_density': 32, 'seconds': report['bake_seconds'], 'visual_acceptance': 'NOT_REVIEWED'}])
s['fw_eevee_level_status_json'] = json.dumps(levels)
s['eevee_probe_bake_limitations'] = 'Only MAIN_L3 baked at frame 48. Other six interior levels NOT_BAKED. This is not a complete building preview.'
s['fw_eevee_coverage_profile_json'] = json.dumps({k: v for k, v in profile.items() if k != 'selected_geometry'})
s['fw_eevee_candidate_scope'] = report['scope']
checkpoint('RENDERING')
s.render.filepath = str(PNG)
start = time.perf_counter()
bpy.ops.render.render(write_still=True)
report.update(render_seconds=time.perf_counter()-start, png=str(PNG), png_sha256=sha(PNG), visual_acceptance='NOT_REVIEWED')
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
report.update(candidate_blend=str(BLEND), candidate_sha256=sha(BLEND), source_unchanged=sha(SOURCE) == EXPECTED)
assert report['source_unchanged']
assert report['helper_hashes'] == {name: sha(ROOT / 'scripts' / name) for name in report['helper_hashes']}
checkpoint('RENDERED_SAVED')
print('STUDY07_COMPLETE ' + json.dumps({k: report[k] for k in ('bake_seconds', 'render_seconds', 'png_sha256', 'candidate_sha256')}), flush=True)
