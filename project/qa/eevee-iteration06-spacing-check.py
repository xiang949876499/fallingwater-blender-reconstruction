"""Check metadata against nominal centers inspected via Blender's matrix API."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
helper = ROOT/'scripts/eevee_preview.py'
tree = ast.parse(helper.read_text(encoding='utf-8'))
node = next(n for n in ast.walk(tree) if isinstance(n,ast.Assign)
            and len(n.targets)==1 and isinstance(n.targets[0],ast.Subscript)
            and isinstance(n.targets[0].slice,ast.Constant)
            and n.targets[0].slice.value=='actual_grid_spacing_m')
statement = compile(ast.Module(body=[node],type_ignores=[]),str(helper),'exec')
inspection=json.loads((ROOT/'qa/eevee-iteration06-volume-inspect.json').read_text())
rows=[]
for probe in inspection['probes']:
    record={'resolution':probe['resolution']}
    values={'record':record,'low':probe['bounds'][0],'high':probe['bounds'][1]}
    exec(statement,values)
    centers={tuple(p['index']):p['world'] for p in probe['nominal_unshifted_world_centers']}
    measured=[]
    for axis in range(3):
        index=[0,0,0]; index[axis]=1
        measured.append(centers[tuple(index)][axis]-centers[(0,0,0)][axis])
    error=max(abs(a-b) for a,b in zip(record['actual_grid_spacing_m'],measured))
    assert error < 5e-6,(probe['name'],error)
    rows.append({'probe':probe['name'],'reported_m':record['actual_grid_spacing_m'],
                 'inspected_adjacent_center_deltas_m':measured,'maximum_error_m':error})
result={'status':'PASS','helper_sha256':hashlib.sha256(helper.read_bytes()).hexdigest(),
    'scope':'Only report assignment changed; actual probe transforms/resolutions/bake settings untouched.',
    'formula_source':'https://raw.githubusercontent.com/blender/blender/v5.2.1/source/blender/draw/engines/eevee/shaders/eevee_lightprobe_volume.bsl.hh',
    'formula':'local=-1+2*(index+1)/(resolution+1)', 'comparisons':rows}
(ROOT/'qa/eevee-iteration06-spacing-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'status':result['status'],'probes':len(rows),'helper_sha256':result['helper_sha256']}))
