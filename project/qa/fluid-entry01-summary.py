"""Summarize existing measured JSON only; no simulation or scene changes."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'qa/fluid-entry01-check.json').read_text(encoding='utf-8'))
ids = [i for i, p in enumerate(data['positions']) if p['target_outlet']]
def statistics(values):
    values = [v for v in values if v is not None]
    return {'count': len(values), 'min': min(values) if values else None,
            'max': max(values) if values else None,
            'mean': sum(values) / len(values) if values else None}
out = {'status': 'FAIL_INLET_DEPTH_AND_CONTINUOUS_COVERAGE', 'windows': {}}
for first, last in ((1, 36), (20, 36)):
    frames = [f for f in data['frames'] if first <= f['frame'] <= last]
    samples = [f['samples'][i] for f in frames for i in ids]
    thicknesses = [s['water_top_m'] - s['water_bottom_m'] for s in samples
                   if s['water_top_m'] is not None and s['water_bottom_m'] is not None]
    source = [s['water_top_m'] for f in frames for s, p in zip(f['samples'], data['positions']) if p['source_center']]
    out['windows'][f'{first}-{last}'] = {
        'sample_count': len(samples), 'hits': sum(s['water_top_m'] is not None for s in samples),
        'missing': sum(s['water_top_m'] is None for s in samples),
        'positions_present_every_frame': sum(all(f['samples'][i]['water_top_m'] is not None for f in frames) for i in ids),
        'source_top_m': statistics(source),
        'mesh_water_thickness_m': statistics(thicknesses),
        'mesh_water_thickness_cells': statistics(t / data['cell_m'] for t in thicknesses),
        'mesh_water_thickness_at_least_3_cells_count': sum(t >= 3 * data['cell_m'] for t in thicknesses),
        'note': 'Thickness is cached mesh vertical extent / nominal solver cell, not a direct VDB occupancy-cell count.'}
out['final_frame_outlet_hits'] = sum(data['frames'][-1]['samples'][i]['water_top_m'] is not None for i in ids)
out['visual_review'] = {'path': 'qa/fluid-entry01-frame036.png', 'viewed': True,
    'result': 'FAIL: inlet supports a local sheet, with strong thinning, interrupted patches and exposed bed downstream. Hard source/domain footprint visible. No full-scene or photographic acceptance.'}
(ROOT / 'qa/fluid-entry01-summary.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(out, ensure_ascii=False))
