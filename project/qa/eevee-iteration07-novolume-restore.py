"""Read-only fresh reopen and Cycles switch; no render, bake, save or new lights."""
import ast, hashlib, json, sys
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import eevee_glass
import render_views
OUT = ROOT / 'qa/eevee-iteration07-novolume'
report = json.loads((OUT / 'baseline-report.json').read_text(encoding='utf-8'))
tree = ast.parse((ROOT / 'qa/eevee-iteration06-coverage.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in {'sha', 'properties', 'light_state'}], type_ignores=[]), 'inspection_helpers', 'exec'))
candidate = Path(report['candidate_blend'])
assert sha(candidate) == report['candidate_sha256']
bpy.ops.wm.open_mainfile(filepath=str(candidate))
s = bpy.context.scene
s.render.threads_mode = 'FIXED'
s.render.threads = 4
s.frame_set(48)
bpy.context.view_layer.update()
assert s.render.engine == 'BLENDER_EEVEE'
assert not s.eevee.use_fast_gi and s.eevee.use_raytracing
assert not any(o.type == 'LIGHT_PROBE' and o.data.type == 'VOLUME' for o in bpy.data.objects)
assert not any(d.type == 'VOLUME' for d in bpy.data.lightprobes)
current = light_state(s)
original_physical = json.loads(json.dumps(report['original_light_state']))
# ID.session_uid identifies a datablock in the current Blender session. It is
# not a saved physical light parameter; the failed raw comparison is retained.
for state in (current, original_physical):
    for value in state.values():
        value['properties'].pop('session_uid', None)
differences = {}
for name in set(current) | set(original_physical):
    old = original_physical.get(name)
    new = current.get(name)
    if old != new:
        differences[name] = {'before': old, 'after': new}
(OUT / 'fresh-reopen-physical-light-differences.json').write_text(json.dumps(differences, indent=2), encoding='utf-8')
assert not differences
assert eevee_glass.cycles_signature() == report['cycles_glass_surface_hash_preserved']
selected = render_views.configure_engine(s, 'CYCLES', 32, 'CPU')
assert s.render.engine == 'CYCLES' and s.cycles.device == 'CPU'
after_switch = light_state(s)
for value in after_switch.values():
    value['properties'].pop('session_uid', None)
assert after_switch == original_physical
assert eevee_glass.cycles_signature() == report['cycles_glass_surface_hash_preserved']
assert eevee_glass.geometry_signature(s) == report['glazing_geometry_hash_preserved']
assert sha(candidate) == report['candidate_sha256']
assert sha(Path(report['source_scene'])) == report['source_sha256']
result = {'status': 'PASS', 'candidate_sha256': report['candidate_sha256'], 'fresh_reopen_zero_volumes': True,
    'after_switch_engine': s.render.engine, 'device': selected,
    'original_light_names_parameters_shadow_links_equal_before_and_after_switch': True,
    'ignored_cross_session_metadata': ['ID.session_uid'],
    'cycles_glass_surface_hash_preserved': True, 'glazing_geometry_hash_preserved': True,
    'fill_restore_test': 'NOT_APPLICABLE: conditional fill stage was not entered; no added fill light exists to hide or remove.',
    'source_and_candidate_files_unchanged': True, 'renders': 0, 'bakes': 0, 'saves': 0}
(OUT / 'cycles-switch-check.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2), flush=True)
