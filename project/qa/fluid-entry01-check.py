"""Measure the one pre-registered entry01 cache; never rebake or edit source scenes."""
import hashlib
import json
import math
import sys
import time
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import water_integration as wi

reference = json.loads((ROOT / 'qa/fluid-entry01.json').read_text(encoding='utf-8'))
assert reference['status'].startswith('BAKED_')
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'scene/Fallingwater_fluid_entry01.blend'))
scene = bpy.context.scene
scene.render.threads_mode = 'FIXED'
scene.render.threads = 8
domain = scene.objects['WATER_Mantaflow_Local_Cascade']
core = scene.objects['SITE_Core_Continuous_Fractured_Sandstone']
rocks = [wi._bvh(o) for o in scene.objects if o.get('fluid_collision')]
source = ROOT / 'scene/Fallingwater_iteration04.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest() == wi.FROZEN04_SHA
with bpy.data.libraries.load(str(source), link=False) as (src, dst):
    dst.objects = [wi.SURFACE, 'SITE_Core_Continuous_Fractured_Sandstone']
for obj in dst.objects:
    scene.collection.objects.link(obj)
surface = next(o for o in dst.objects if o.name.startswith(wi.SURFACE))
original_core = next(o for o in dst.objects if o != surface)
wi.repair_surface_normals(scene)

def mesh_hash(obj):
    data = {'v': [list(obj.matrix_world @ v.co) for v in obj.data.vertices],
            'p': [list(p.vertices) for p in obj.data.polygons]}
    return hashlib.sha256(json.dumps(data, separators=(',', ':')).encode()).hexdigest()

lip = Vector((2.4, -2.83, 0))
down = Vector((-.882352948, -.470588356, 0))
across = Vector((.470588356, -.882352948, 0))
cell = reference['nominal_solver_cell_m']
bounds = reference['domain_aabb_m']

def point(s, c):
    return lip + down * s + across * c

def top(tree, p):
    result = tree.ray_cast(Vector((p.x, p.y, -2.4)), Vector((0, 0, -1)), 2)
    return result[0].z if result[0] is not None else None

def stats(values):
    values = [v for v in values if v is not None]
    return {'count': len(values), 'min': min(values) if values else None,
            'max': max(values) if values else None,
            'mean': sum(values) / len(values) if values else None}

positions = []
for s in (-2.0, -1.8, -1.7, -1.55, -1.4, -1.3, -1.2, -1.1, -.95, -.825, -.7, -.6):
    for c in (.35, .55, .725, .9, 1.075, 1.25, 1.45):
        p = point(s, c)
        edge = min(p[i] - bounds[i][0] for i in range(2))
        edge = min(edge, *(bounds[i][1] - p[i] for i in range(2)))
        bedtops = [v for t in rocks if (v := top(t, p)) is not None]
        positions.append({'s': s, 'c': c, 'xy': list(p.xy), 'boundary_clearance_m': edge,
                          'boundary_clearance_cells': edge / cell,
                          'bed_top_m': max(bedtops) if bedtops else None,
                          'target_outlet': -.951 < s < -.699 and .549 < c < 1.251,
                          'source_center': s == -1.55 and c == .9})

report = {'run': 'entry01', 'scope': 'One 36-frame inlet calibration; no waterfall/full-width seam/ten-second acceptance',
          'target_free_surface_z_m': -2.99, 'target_depth_m': [.05, .09],
          'cell_m': cell, 'physical_grid_estimate': [math.ceil(v / cell) for v in reference['domain_dimensions_m']],
          'core_sha256': mesh_hash(core), 'frozen04_core_sha256': mesh_hash(original_core),
          'core_geometry_matches_frozen04': mesh_hash(core) == mesh_hash(original_core),
          'positions': positions, 'frames': [],
          'interpretation': 'Top is highest cached mesh hit, including crests. Bottom contact is the first upward liquid hit from 0.10m below measured rock. Source head is measured separately from the downstream target.'}
started = time.perf_counter()
for frame in range(1, 37):
    scene.frame_set(frame)
    water = wi._bvh(domain)
    river = wi._bvh(surface)
    samples = []
    for pos in positions:
        p = Vector((*pos['xy'], 0))
        z = top(water, p) if pos['boundary_clearance_m'] >= 0 else None
        rock = pos['bed_top_m']
        bottom = None
        if z is not None and rock is not None:
            h = water.ray_cast(Vector((p.x, p.y, rock - .1)), Vector((0, 0, 1)), .7)
            bottom = h[0].z if h[0] is not None else None
        depth = z - rock if z is not None and rock is not None else None
        samples.append({'water_top_m': z, 'water_bottom_m': bottom,
                        'program_water_top_m': top(river, p), 'depth_above_rock_m': depth,
                        'depth_cells': depth / cell if depth is not None else None,
                        'bottom_minus_rock_m': bottom - rock if bottom is not None else None})
    report['frames'].append({'frame': frame, 'samples': samples})
    print('ENTRY_MEASURED', frame, flush=True)

target_ids = [i for i, p in enumerate(positions) if p['target_outlet']]
source_ids = [i for i, p in enumerate(positions) if p['source_center']]
late = report['frames'][19:]
target = [f['samples'][i] for f in late for i in target_ids]
source_samples = [f['samples'][i] for f in late for i in source_ids]
report['late_window'] = {'frames': [20, 36], 'outlet_positions': len(target_ids),
    'sample_count': len(target), 'missing': sum(v['water_top_m'] is None for v in target),
    'outlet_water_top_m': stats(v['water_top_m'] for v in target),
    'outlet_depth_m': stats(v['depth_above_rock_m'] for v in target),
    'outlet_depth_cells': stats(v['depth_cells'] for v in target),
    'outlet_bottom_minus_rock_m': stats(v['bottom_minus_rock_m'] for v in target),
    'outlet_program_water_top_m': stats(v['program_water_top_m'] for v in target),
    'source_water_top_m': stats(v['water_top_m'] for v in source_samples),
    'depth_5_to_9_cm_count': sum(v['depth_above_rock_m'] is not None and .05 <= v['depth_above_rock_m'] <= .09 for v in target),
    'depth_at_least_3_cells_count': sum(v['depth_cells'] is not None and v['depth_cells'] >= 3 for v in target),
    'top_within_2cm_of_target_count': sum(v['water_top_m'] is not None and abs(v['water_top_m'] + 2.99) <= .02 for v in target)}
report['outlet_positions_late'] = []
for i in target_ids:
    tops = [f['samples'][i]['water_top_m'] for f in late]
    st = stats(tops)
    report['outlet_positions_late'].append({'position': positions[i], 'top': st,
        'temporal_range_m': st['max'] - st['min'] if st['count'] else None,
        'depth': stats(f['samples'][i]['depth_above_rock_m'] for f in late)})
report['measure_seconds'] = time.perf_counter() - started
report['status'] = 'MEASURED_PENDING_INTERPRETATION'
wi._write(ROOT / 'qa/fluid-entry01-check.json', report)
print('ENTRY_CHECK_COMPLETE', json.dumps(report['late_window']), flush=True)
