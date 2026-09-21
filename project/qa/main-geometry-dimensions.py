"""Read actual evaluated mesh vertices; never use dimension metadata as geometry."""
import bpy
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path('D:/zx/test/project')
SCENE = ROOT / 'qa/main-geometry-smoke.blend'
bpy.ops.wm.open_mainfile(filepath=str(SCENE))
dg = bpy.context.evaluated_depsgraph_get()
source = json.loads((ROOT / 'data/main_house.json').read_text(encoding='utf-8'))


def boundary(name, axis, side):
    """World extrema from actual evaluated mesh vertices, including modifiers."""
    ob = bpy.data.objects[name]
    eo = ob.evaluated_get(dg)
    mesh = eo.to_mesh()
    try:
        vertices = [(v.index, tuple(eo.matrix_world @ v.co)) for v in mesh.vertices]
        value = (min if side == 'min' else max)(p[axis] for _, p in vertices)
        chosen = [(i, list(p)) for i, p in vertices if abs(p[axis] - value) < 1e-6]
        return dict(object=name, axis='XYZ'[axis], boundary=side, world_coordinate_m=value,
                    evaluated_vertex_count=len(vertices), vertex_ids=[i for i, _ in chosen],
                    representative_vertex_world_m=chosen[0][1])
    finally:
        eo.to_mesh_clear()


def comparison(record, a, b, reason, accepted=True):
    actual = abs(b['world_coordinate_m'] - a['world_coordinate_m'])
    delta = actual - record['reference_m']
    geo_tolerance = max(.020, .005 * record['reference_m'])
    record.update(endpoints=[a, b], actual_mesh_m=actual, delta_m=delta,
                  tolerance_m=geo_tolerance, correspondence=reason,
                  within_source_reading_uncertainty=abs(delta) <= record['source_trace_uncertainty_m'],
                  source_uncertainty_exceeds_geo02=record['source_trace_uncertainty_m'] > geo_tolerance,
                  status=('PASS' if abs(delta) <= geo_tolerance else 'FAIL')
                  if accepted else 'NOT_RUN')
    if not accepted:
        record['not_run_reason'] = ('Actual mesh bounding span is diagnostic only. The original label '
            'has no extension lines resolving which stepped wall, cabinet recess or net/gross boundary '
            'it measures. No claim of label-to-mesh conformity is made from a bounding box.')


levels = {
    'MAIN_LEVEL_2': 'MAIN_L2_TERRACE_S_slab',
    'MAIN_LEVEL_3': 'MAIN_L3_TERRACE_slab',
    'MAIN_ROOF_EAST': 'MAIN_L3_gallery_roof',
    'MAIN_ROOF_WEST': 'MAIN_L3_study_roof',
}
room_bounds = {
    'MAIN_LIVING_NOMINAL_LENGTH': ('MAIN_L1_LIVING_slab', 1),
    'MAIN_LIVING_NOMINAL_WIDTH': ('MAIN_L1_LIVING_slab', 0),
    'MAIN_KITCHEN_NOMINAL_LENGTH': ('MAIN_L1_KITCHEN_slab', 1),
    'MAIN_KITCHEN_NOMINAL_WIDTH': ('MAIN_L1_KITCHEN_slab', 0),
    'MAIN_SERVANT_NOMINAL_LENGTH': ('MAIN_L1_SERVANT_slab', 0),
    'MAIN_SERVANT_NOMINAL_WIDTH': ('MAIN_L1_SERVANT_slab', 1),
}
unresolved = {
    'MAIN_CHAIN_TOTAL': 'The chain reaches the far bridge/retaining edge outside the main-house module; its westmost extension is an outside paving/rock station with no named matching main mesh.',
    'MAIN_CHAIN_01': 'The west pair of dimension extension lines refer to exterior paving/retaining stations; these are not explicit named main-house mesh boundaries.',
    'MAIN_CHAIN_02': 'The west extension station at source x=284 has no unambiguous named main-house boundary; cannot independently pair it with the spine face.',
    'MAIN_CHAIN_04': 'The east extension at source x=535 meets the loggia/entry terrace transition; the exact referenced face versus paving station is not established in the current main mesh.',
    'MAIN_CHAIN_05': 'The two loggia/paving extension stations are not independently mapped to modeled outer faces; the traced floor boundary alone cannot certify the label.',
    'MAIN_CHAIN_06': 'The dimension crosses the loggia/stair/retaining transition; top landing, retaining wall and paving have different physical ends and the label-to-face match is unresolved.',
    'MAIN_CHAIN_07': 'This span includes the bridge approach, built by the site module; main-only scene lacks the east surveyed station.',
    'MAIN_CHAIN_08': 'This bridge/site span is outside the main-house module; no actual main mesh can supply both ends.',
    'MAIN_CHAIN_09': 'The final bridge/retaining-edge span is outside the main-house module.',
    'MAIN_VERTICAL_TOTAL': 'South parapet exterior is modeled, but the north source y=229 extension face at the servant/service entry is not resolved between open entry paving, room floor and wall; do not substitute nearest vertices.',
}
rows = []
for dim in source['dimensions']:
    rid = dim['id']
    row = dict(id=rid, source=dim['source'], source_label=dim['raw'], reference_m=dim['meters'],
               source_axis=dim['axis'], source_pixels=dim['pixels'], label_evidence='A',
               source_trace_uncertainty_m=dim['uncertainty_m'], actual_mesh_m=None,
               delta_m=None, tolerance_m=max(.020,.005*dim['meters']), endpoints=[], status='NOT_RUN')
    if rid in levels:
        comparison(row, boundary('MAIN_L1_TERRACE_W_slab', 2, 'max'), boundary(levels[rid], 2, 'max'),
                   'Actual slab top Z relative to actual main-level west-terrace slab top. Separate interior finish is excluded.')
    elif rid == 'MAIN_CHAIN_03':
        comparison(row, boundary('MAIN_L1_north_spine_1', 0, 'max'), boundary('MAIN_L1_north_spine_3', 0, 'max'),
                   'East outer faces of the two successive north masonry returns. Original TIFF extension centers are source x=328.3714301872 and x=392.4184810270; the former rounded trace x=328..393 was corrected by 53.2 mm at the east return. Evaluated outer-face vertices measured independently; scan registration remains C.')
    elif rid in room_bounds:
        name, axis = room_bounds[rid]
        comparison(row, boundary(name, axis, 'min'), boundary(name, axis, 'max'),
                   'Actual complete floor-mesh bounding span, including stepped recesses; nominal label semantics unresolved.', False)
    else:
        row['not_run_reason'] = unresolved[rid]
    rows.append(row)

report = dict(schema_version=2, building='MAIN', scene=str(SCENE), scene_sha256=hashlib.sha256(SCENE.read_bytes()).hexdigest(),
              tolerance_standard='GEO-02: max(0.020 m,0.005*reference length). Source reading uncertainty is separate and never substitutes for this threshold.',
              scene_scope='Latest main-house-only CPU build. Integration scene not measured by this script.',
              method='Independent evaluated Blender mesh world vertices. Neither model_m nor reference_m is used to generate measured coordinates.',
              correspondence_rule='Only dimension lines with identified physical faces or section slab planes receive PASS/FAIL. Nominal room bounding spans remain diagnostic NOT_RUN.',
              precision_limit='PASS is numeric mesh-versus-label comparison only. Source uncertainty exceeding GEO-02 is flagged separately; actual mesh arithmetic does not upgrade traced C geometry to surveyed evidence.',
              counts=dict(Counter(r['status'] for r in rows)), measurements=rows)
(ROOT / 'qa/main-dimensions-measured.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({'counts': report['counts'], 'results': [{k:r[k] for k in ('id','actual_mesh_m','delta_m','status')} for r in rows]}, indent=2))
