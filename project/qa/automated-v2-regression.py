"""Small real-mesh regressions for the structural audit; no render or GPU use."""
import bpy
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import validate_scene as validator
from fwlib import box, collection

for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
mat = bpy.data.materials.new('Regression structural material')
col = collection('Regression shared geometry')

# Two spatially adjacent rooms share untagged real floor, ceiling and walls.
box('GUEST_SHARED_FLOOR', (2, 1, -.1), (4, 2, .2), mat, col, 0)
box('GUEST_SHARED_CEILING', (2, 1, 2.1), (4, 2, .2), mat, col, 0)
for name, center, size in [
    ('GUEST_NORTH_pier_end', (2, 2, 1), (4, .2, 2)),
    ('GUEST_SOUTH_pier_end', (2, 0, 1), (4, .2, 2)),
    ('GUEST_WEST_pier_end', (0, 1, 1), (.2, 2, 2)),
    ('GUEST_EAST_pier_end', (4, 1, 1), (.2, 2, 2)),
]:
    ob = box(name, center, size, mat, col, 0)
    ob['role'] = 'architecture'

rooms = []
for rid, x0, kind in [('SHARED_A', 0, 'living'), ('SHARED_B', 2, 'living'),
                      ('MISSING_FLOOR', 8, 'living'), ('STEPPED_ROUTE', 12, 'stair')]:
    room = dict(id=rid, label=rid, kind=kind, z=0, height=2,
                polygon=[[x0, 0], [x0+2, 0], [x0+2, 2], [x0, 2]], center=[x0+1, 1, 0])
    rooms.append(room)
    for suffix, x in [('A', x0+.5), ('B', x0+1.5)]:
        camera = bpy.data.objects.new('CAM_'+rid+'_'+suffix, bpy.data.cameras.new(rid+suffix))
        col.objects.link(camera)
        camera.location = (x, 1, 1.6)
        camera['room_id'] = rid
box('GUEST_ROUTE_tread_00', (12.5, 1, .1), (.5, 1, .2), mat, col, 0)
bpy.context.view_layer.update()
report = validator.audit(bpy.context.scene, rooms)
results = {r['room_id']: r for r in report['room_results']}
checks = {
    'guest_pier_semantics_recognized': validator.component(bpy.data.objects['GUEST_NORTH_pier_end']) == 'wall',
    'shared_floor_A_has_actual_evidence': results['SHARED_A']['status'] == 'PASS' and results['SHARED_A']['owned_meshes'] == 0 and bool(results['SHARED_A']['structurally_associated_meshes']),
    'shared_floor_B_has_actual_evidence': results['SHARED_B']['status'] == 'PASS' and results['SHARED_B']['owned_meshes'] == 0,
    'genuinely_missing_floor_still_fails': results['MISSING_FLOOR']['floor_sampling_status'] == 'FAIL' and results['MISSING_FLOOR']['status'] == 'FAIL',
    'stepped_route_is_not_silently_passed': results['STEPPED_ROUTE']['status'] == 'INCOMPLETE' and results['STEPPED_ROUTE']['floor_sampling_status'] == 'NOT_RUN',
}
output = {'checks': checks, 'status': 'PASS' if all(checks.values()) else 'FAIL', 'actual_mesh_room_results': report['room_results']}
(ROOT / 'qa/automated-v2-regression.json').write_text(json.dumps(output, indent=2), encoding='utf8')
print(json.dumps(checks), flush=True)
assert all(checks.values()), checks
