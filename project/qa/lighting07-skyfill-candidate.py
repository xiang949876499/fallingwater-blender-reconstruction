"""Isolate an artistic daylight sky/Sun ratio comparison on frozen iteration06."""
import hashlib
import json
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'scene/Fallingwater_iteration06.blend'
output = ROOT / 'scene/Fallingwater_lighting_candidate07.blend'
sha_before = hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
scene = bpy.context.scene
backgrounds = [n for n in scene.world.node_tree.nodes if n.type == 'BACKGROUND']
assert len(backgrounds) == 1
background = backgrounds[0]
old = float(background.inputs['Strength'].default_value)
assert abs(old - .12) < 1e-6, old
lights_before = {o.name: [o.data.energy, list(o.data.color), list(o.matrix_world)]
                 for o in scene.objects if o.type == 'LIGHT'}
background.inputs['Strength'].default_value = .36
settings = json.loads(scene['lighting_settings_json'])
settings['sky_strength'] = .36
scene['lighting_settings_json'] = json.dumps(settings)
scene['fw_lighting07_scope'] = ('Candidate only: sky strength .12 to .36; same Sun, '
    'visible practical fixtures, geometry, materials, camera poses and exposure defaults. '
    'Artistic daylight ratio, not measured weather or illuminance. Visual acceptance pending.')
bpy.ops.wm.save_as_mainfile(filepath=str(output))
lights_after = {o.name: [o.data.energy, list(o.data.color), list(o.matrix_world)]
                for o in scene.objects if o.type == 'LIGHT'}
assert lights_before == lights_after
assert hashlib.sha256(source.read_bytes()).hexdigest() == sha_before
report = {'source': str(source.relative_to(ROOT)), 'source_sha256': sha_before,
          'candidate': str(output.relative_to(ROOT)),
          'candidate_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
          'sky_strength_before': old, 'sky_strength_after': .36,
          'light_count': len(lights_before), 'all_light_values_unchanged': True,
          'source_file_unchanged': True, 'visual_status': 'NOT_RUN'}
(ROOT / 'qa/lighting07-skyfill-candidate.json').write_text(
    json.dumps(report, indent=2), encoding='utf8')
print(json.dumps(report))
