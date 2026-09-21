"""Reconcile this read-only source review; no Blender or production mutations."""
from pathlib import Path
import csv, hashlib, json
import numpy as np
from PIL import Image

Q = Path(__file__).resolve().parent
R = Q.parents[1]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

crops_path = Q / 'tower-height12-source-crops.json'
crops = json.loads(crops_path.read_text(encoding='utf-8'))
for row in crops['crops']:
    assert sha(R / row['path']) == row['sha256']
    row['viewed'] = True
    row['viewed_by'] = '/root/site_visual'
    row['viewed_note'] = 'Actual image tool inspection; date is not inferred from this flag.'
crops['interpretation_review'] = 'tower-height12-source-review.md'
crops_path.write_text(json.dumps(crops, indent=2), encoding='utf-8')

# This only finds ink within already visually read narrow windows. It does not
# turn pixels into a surveyed dimension; the dimension is the printed label.
by_crop = {r['name']: r for r in crops['crops']}
windows = [
    ('continuous_coping_top', 'tower-top-native', (400, 290, 2600, 360)),
    ('tower_witness_middle', 'tower-line-middle-native', (300, 80, 3500, 210)),
    ('main_terrace_zero_line', 'main-zero-label-native', (50, 260, 1350, 375)),
]
ink = []
for name, crop_name, window in windows:
    row = by_crop[crop_name]
    im = np.asarray(Image.open(R / row['path']).convert('L'))
    x0, y0, x1, y1 = window
    counts = (im[y0:y1, x0:x1] < 128).sum(axis=1)
    maximum = int(counts.max())
    best = np.flatnonzero(counts >= maximum * .95) + y0
    offset = row['oriented_native_crop_xyxy']
    ink.append({'role': name, 'crop': row['path'], 'window_in_crop_xyxy': window,
                'black_pixel_peak': maximum, 'peak95_native_y_rows': [int(y + offset[1]) for y in best],
                'native_x_range': [x0 + offset[0], x1 + offset[0]],
                'use': 'Reproducible visual locator only, not metric survey.'})

probe = json.loads((Q / 'tower-height12-source-mesh-probe.json').read_text(encoding='utf-8'))
objects = {r['object']: r for r in probe['objects']}
def top(name):
    return max(objects[name]['horizontal_upward_surfaces'], key=lambda s: s['z_m'])
nominal = (32 * 12 + 9.5) * .0254
upper = top('MAIN_chimney_cap')
datum_options = []
for name, rationale in [
    ('MAIN_L1_TERRACE_W_finish', 'Preferred visible terrace-surface correspondence; C, consistent with MAIN_LEVEL_2.'),
    ('MAIN_L1_TERRACE_W_slab', 'Existing structural-datum convention used by MAIN_LEVEL_3 and MAIN_ROOF_WEST; C.')]:
    face = top(name)
    actual = upper['z_m'] - face['z_m']
    datum_options.append({'object': name, 'face': face, 'rationale': rationale,
                          'actual_relative_height_m': actual, 'error_m': actual - nominal})
dimensions_path = R / 'project/dimensions.csv'
dimensions = list(csv.DictReader(dimensions_path.open(encoding='utf-8-sig')))
existing_ids = [r.get('id', r.get('dimension_id')) for r in dimensions]
proposal_id = 'MAIN_TOWER_CONTINUOUS_COPING_RELATIVE_MAIN_TERRACE'
assert proposal_id not in existing_ids
out = {
    'status': 'PROPOSED_ONE_NEW_ANCHOR_NOT_ADDED_TO_CENTRAL_TABLE',
    'anchor_id': proposal_id,
    'source': {'sheet': 'HABS PA-5346, sheet 10, Section Looking West',
               'path': crops['source'], 'sha256': crops['source_sha256'],
               'archive_url': 'https://www.loc.gov/pictures/item/pa1690.sheet.00010a/',
               'original_url': 'https://tile.loc.gov/storage-services/master/pnp/habshaer/pa/pa1600/pa1690/sheet/00010a.tif',
               'nominal_label': 'MAIN TOWER 32 feet 9 1/2 inches',
               'datum_label': 'MAIN LEVEL TERRACE 0 feet 0 inches',
               'nominal_m': nominal, 'label_evidence': 'A: directly read printed label',
               'graphic_endpoint_evidence': 'C: witness aligns continuous masonry/coping upper silhouette; raised outlets above it are excluded',
               'exact_sheet_survey_date': 'UNKNOWN',
               'collection_date': 'circa 2010, official museum collection-level description, independently reopened 2026-09-21',
               'date_url': 'https://fallingwater.org/learn/preservation-and-collections/research-resources/architectural-drawings/',
               'retrieval_date': '2026-09-20; not a survey date'},
    'mesh_probe': {'source_blend': probe['source'], 'source_sha256': probe['source_sha256'],
                   'frame': 48, 'upper_object': 'MAIN_chimney_cap', 'upper_face': upper,
                   'nominal_endpoint_role': 'continuous tower masonry/coping upper finished silhouette',
                   'component_name_mapping': 'C; source does not name a model component or a separate slab construction'},
    'datum_options': datum_options,
    'datum_decision': 'Do not silently reconcile the current 22mm mixed table convention. Both explicit options fail the nominal target.',
    'nominal_comparison_tolerance_m': max(.02, .005 * nominal),
    'numeric_status_both_datums': 'FAIL', 'absolute_survey_accuracy': 'UNKNOWN',
    'source_pixel_locator': ink,
    'central_dimensions_sha256_read': sha(dimensions_path),
    'repeat_checks_count_as_additional_anchors': False,
    'prohibited_substitutions': ['MAIN_chimney_flue top', 'MAIN_chimney_flue.001 top', 'MAIN_stone_tower_west structural top', 'MAIN_stone_tower_north structural top'],
    'scope': {'source_blend_changed': False, 'tower_candidate_changed': False, 'production_changed': False, 'rendered': False},
}
(Q / 'tower-height12-source-anchor-proposal.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
print(json.dumps({'datum_options': datum_options, 'source_pixel_locator': ink,
                  'tolerance_m': out['nominal_comparison_tolerance_m']}, indent=2))
