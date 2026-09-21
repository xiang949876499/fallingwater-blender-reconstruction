"""Read the actual first-hit geometry below the Study desk, without scene edits."""
import hashlib
import json
from pathlib import Path
import bpy
from mathutils import Vector

root = Path(__file__).resolve().parents[1]
source = root / 'scene/Fallingwater_iteration06.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
s = bpy.context.scene
s.render.resolution_x, s.render.resolution_y = 960, 540
s.render.resolution_percentage = 100
cam = s.objects['CAM_MAIN_L3_STUDY_B']
corners = cam.data.view_frame(scene=s)
xlo, xhi = min(q.x for q in corners), max(q.x for q in corners)
ylo, yhi = min(q.y for q in corners), max(q.y for q in corners)
z = corners[0].z
deps = bpy.context.evaluated_depsgraph_get()
rows = []
for x, y in [(500, 465), (500, 478), (520, 479), (610, 485), (700, 493),
             (780, 498), (850, 507), (710, 454), (720, 275)]:
    direction = cam.matrix_world.to_quaternion() @ Vector((
        xlo + (x + .5) / 960 * (xhi - xlo),
        yhi - (y + .5) / 540 * (yhi - ylo), z))
    hit, point, normal, face, obj, _ = s.ray_cast(
        deps, cam.matrix_world.translation, direction.normalized(), distance=100)
    row = {'pixel': [x, y], 'hit': hit}
    if hit:
        row.update(object=obj.name, point=list(point), normal=list(normal), face=face)
        row['material_slots'] = [m.name if m else None for m in obj.data.materials]
    rows.append(row)
obj = s.objects['MAIN_L3_study_core_1']
mesh = obj.evaluated_get(deps).to_mesh()
coords = [obj.matrix_world @ v.co for v in mesh.vertices]
bounds = [[min(v[i] for v in coords) for i in range(3)],
          [max(v[i] for v in coords) for i in range(3)]]
obj.evaluated_get(deps).to_mesh_clear()
report = {'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'camera': cam.name, 'core_1_actual_bounds': bounds, 'pixels': rows,
          'scope': 'First opaque-or-transparent surface hit only, not light-path tracing. '
                   'A bright surface pixel is not automatically a geometric hole.'}
(root / 'qa/study-base-strip07-probe.json').write_text(json.dumps(report, indent=2), encoding='utf8')
print(json.dumps(report))
