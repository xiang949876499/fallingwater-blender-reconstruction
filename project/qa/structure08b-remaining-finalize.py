"""Read-only QA annotation/report metadata; never opens or saves Blender data."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
qa = ROOT / 'qa'
path = qa / 'structure08b-remaining-review.json'
data = json.loads(path.read_text(encoding='utf-8'))
scene = ROOT / 'scene/Fallingwater_structure_candidate08b.blend'
script = ROOT / 'scripts/main_house.py'
def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()
assert sha(scene) == data['source_sha256']
assert sha(script) == data['source_script_sha256']

classifications = [
    ('STONE_BASE_HIT_NOT_VOID_AT_EXACT_PIXEL',
     'First hit is the existing entry_east_1 stone side below the finish elevation. The expected finish-plane point has no floor, but is on/near the source hatched pier footprint; do not label this exact pixel terrain.',
     'Inspect together with the adjacent L-corner solid-footprint gap; do not blanket-fill as walkable floor.'),
    ('MISSING_L1_L_CORNER_SOLID_CLOSURE',
     'Ray first reaches a basement pier at Z -1.58126. Its L1-plane source point (529.3135,333.0027) lies in the hatched continuous L-pier mass. The two modeled butt-ended wall segments leave their outer quadrant uncovered.',
     'Future bounded correction should join the actual L-shaped stone core at the corner, preserving the source doorway. Floor extension alone would misclassify this source mass.'),
    ('STONE_BASE_HIT_NOT_VOID_AT_EXACT_PIXEL',
     'First hit is coat_1 stone at Z 0.12477, slightly above finish. The point is not a terrain ray despite nearby green appearance.',
     'Retain as a stone-edge control while diagnosing the adjacent coat-return boundary.'),
    ('MISSING_L1_SUPPORT_NEAR_COAT_OUTER_RETURN',
     'Ray reaches terrain at Z -3.25. The expected L1 source point (534.7675,300.7277) is beside the source hatched outer coat return/paving boundary. No true stair opening is shown there. Source tracing does not yet settle stone versus adjacent paving at this boundary.',
     'Reconcile the local solid return footprint and adjacent paving against original main04; then close only the demonstrated missing support. Exact outer face remains C-level trace uncertainty.'),
    ('FLOOR_PRESENT_NEAR_COPLANAR_REGION',
     'Exact point hits one entry_coat threshold finish at Z 0.122. Adjacent bounded samples prove overlapping threshold/room floor surfaces; darkness at this exact point is not a demonstrated hole.',
     'Remove independently proven threshold/room overlaps, preserve the narrow connection, then inspect the same image region again. Do not infer illumination-only cause from this ray.'),
    ('FLOOR_PRESENT_NEAR_COPLANAR_REGION',
     'Exact point hits one ENTRY finish at Z 0.122; the threshold lies behind along the ray, not coplanar at this XY. Nearby samples include genuine coplanar surfaces.',
     'Use the same bounded threshold de-overlap repair and later same-camera visual comparison; do not call this selected point a void.'),
    ('COPLANAR_MASTER_AND_CLOSET_FLOORS',
     'MASTER_finish and CLOSET_M_finish both occupy the target XY at Z 2.8668. Both underlying structural slabs also exist.',
     'Partition the two physical slab/finish footprints along a shared boundary while retaining semantic room polygons; do not move bed or lighting.'),
    ('SMALL_CEILING_CLOSURE_GAP',
     'The ray passes the Z 5.0 ceiling gap then hits master_entry_lintel at Z 5.02914. At the ceiling-plane XY, the existing L3 terrace slab starts at Z 5.04415 above. Closet ceiling ends at source x366 and the adjacent master ceiling starts x368 in this band.',
     'Future bounded ceiling closure should cover source x366..368, y308..312 where the existing upper slab already closes the room, without changing the actual doorway.'),
]
for r, (classification, evidence, action) in zip(data['results'], classifications):
    r['classification'] = classification
    r['diagnosis_evidence'] = evidence
    r['future_bounded_action_not_executed'] = action
    r['geometry_evidence'] = 'MEASURED_SAVED_MESH'
    r['source_registration_confidence'] = 'C_TRACE_NOT_SURVEY_PRECISION'
    im = Image.open(ROOT / 'renders/previews/iteration08b-structure' / (r['camera'] + '.png')).convert('RGB')
    r['actual_image_rgb'] = list(im.getpixel(tuple(r['pixel'])))

im = Image.open(ROOT / 'renders/previews/iteration08b-structure/CAM_MAIN_L1_LOGGIA_A.png').convert('RGB')
draw = ImageDraw.Draw(im)
colors = ['#ff7b50', '#53e7ff']
for region, color in zip(data['entry_coat_coplanar_regions'], colors):
    p = [tuple(x) for x in region['projected_polygon_pixels']]
    draw.line(p + [p[0]], fill=color, width=2)
draw.rectangle((8, 8, 560, 75), fill='#101820')
draw.text((16, 15), 'Geometry projection only; hidden parts may be occluded.', fill='white')
draw.text((16, 33), 'Orange: COAT / threshold overlap 0.1892 m2', fill=colors[0])
draw.text((16, 51), 'Cyan: ENTRY / threshold overlap 0.1002 m2', fill=colors[1])
for i, (x, y) in enumerate([(494,275),(499,293)], 5):
    draw.line((x-5,y,x+5,y),fill='yellow',width=1)
    draw.line((x,y-5,x,y+5),fill='yellow',width=1)
    draw.text((x+7,y-5),str(i),fill='yellow')
overlay = qa / 'structure08b-remaining-door-overlap-overlay.png'
im.save(overlay)
neighborhood = data['doorway_neighborhoods']
data['status'] = 'READ_ONLY_DIAGNOSIS_COMPLETE_NOT_REPAIRED'
data['scope'] = {'production_source_modified': False, 'blend_saved': False, 'render_run': False,
                 'gpu_used': False, 'blender_probe_cpu_threads': 4,
                 'bounded_original_pixels': 8, 'door_neighbor_pixels': len(neighborhood)}
data['door_neighborhood_summary'] = {
    'coplanar_positions': sum(len(x['finish_layers_at_expected_floor']) > 1 for x in neighborhood),
    'single_finish_positions': sum(len(x['finish_layers_at_expected_floor']) == 1 for x in neighborhood),
    'no_finish_at_exact_expected_plane_positions': sum(len(x['finish_layers_at_expected_floor']) == 0 for x in neighborhood),
    'caveat': 'The two root-selected center pixels have single correct floors. An offset at (507,301) has no exact vertical finish-plane hit; raw evidence retained, not expanded into an unbounded new repair. Projection outlines may include occluded surfaces.'}
data['source_reference_evidence'] = {
    'actual_opened': ['structure08b-remaining-source-crop.png', 'structure08b-remaining-main04-original-crop.png'],
    'main04_original_crop_normalized_bounds': [487, 280, 546, 346],
    'interpretation': 'Continuous hatched stone L-returns at the two pier positions, with paved entry connection. Right outer return versus pavement requires C-level tracing; no whole-rectangle infill authorized.'}
data['report_artifacts'] = ['structure08b-remaining-review.md', overlay.name]
data['frozen_hash_verification'] = {'scene': sha(scene), 'main_house_source': sha(script), 'matched': True}
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': data['status'], 'neighbor_summary': data['door_neighborhood_summary'],
                  'scene_sha': data['source_sha256'], 'source_sha': data['source_script_sha256']}, ensure_ascii=False))
