"""Record inspected evidence; no Blender render or image modification."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / 'qa'
def read(path):
    return json.loads(path.read_text(encoding='utf-8'))
def write(path, data):
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

inspection = read(QA / 'eevee-iteration06-volume-inspect.json')
record_path = QA / 'eevee-iteration06-volume-zero-study.json'
record = read(record_path)
assert record['status'] == 'RENDERED'
baseline = QA / 'eevee-iteration06/CAM_MAIN_L3_STUDY_B_EV2p4.png'
candidate = Path(record['path'])
reference_folder = ROOT / 'renders/previews/iteration06-cycles-lighting-reference'
physical = ROOT / 'scene/Fallingwater_iteration06.blend'
preview = ROOT / 'scene/Fallingwater_preview_iteration06.blend'
assert sha(preview) == record['source_sha256']
assert sha(physical) == '172b76340d1224a2b98f415b21042d19ad7fba4d849543d7156beb17e5fcf055'
arrays = {label: np.asarray(Image.open(path).convert('RGB')).astype(np.int16)
    for label, path in [('baseline', baseline), ('candidate', candidate),
                        ('cycles', reference_folder / 'CAM_MAIN_L3_STUDY_B.png')]}
assert all(array.shape == (540, 960, 3) for array in arrays.values())
difference = np.abs(arrays['baseline'] - arrays['candidate'])
metrics = {'mean_absolute_rgb_code_difference': float(difference.mean()),
           'maximum_absolute_channel_difference': int(difference.max()),
           'identical_pixel_fraction': float(np.all(difference == 0, axis=2).mean()),
           'unit': '8-bit display RGB, not linear irradiance'}
pixels = []
for value in inspection['study_pixels']:
    x, y = value['pixel']
    pixels.append({'label': value['label'], 'pixel': [x, y],
        'wall_hit': value['camera_hit'],
        'display_rgb': {k: a[y,x].tolist() for k,a in arrays.items()}})
probes = []
for p in inspection['probes']:
    low, high = np.array(p['bounds'][0]), np.array(p['bounds'][1])
    scale = (high-low)/2
    density = p['properties']['surfel_density']['value']
    probes.append({'name': p['name'], 'bounds': p['bounds'], 'resolution': p['resolution'],
        'nominal_spacing_m': ((high-low)/(np.array(p['resolution'])+1)).tolist(),
        'old_reported_spacing_m': ((high-low)/(np.array(p['resolution'])-1)).tolist(),
        'rna_surfel_density': density, 'converted_surfel_density_per_m': float(density/max(scale)),
        'surfel_spacing_m': float(max(scale)/density), 'surfel_radius_m': float(max(scale)/(2*density))})
rooms = []
for room in inspection['room_checks']:
    values = room['nominal_samples_inside_room_polygon']
    suspects = [s for s in values if s['backface_first_hits'] > 0]
    rooms.append({'room': room['room'], 'nominal_centers_in_polygon': len(values),
        'nominal_centers_with_backface_first_hits': len(suspects),
        'suspect_centers': [{'index': p['index'], 'world': p['world'],
            'backface_first_hits': p['backface_first_hits']} for p in suspects],
        'baked_validity_read': False})
record.update(status='REVIEWED', visual_acceptance='FAIL_RECTANGLE_REMAINS',
    viewed_native=True, source_unchanged=True, process_exit_code=0,
    finding='Rectangle position and soft boundary persist; intensity zero slightly darkens the middle without removing the overly bright surroundings.',
    comparison_metrics=metrics)
write(record_path, record)
helper_sha = {name: sha(ROOT / 'scripts' / name) for name in ['eevee_glass.py','eevee_preview.py']}
assert helper_sha == {
    'eevee_glass.py':'5ccc9326bc33bac735e76cf6a85051f7da31f86a7243e1979052c6710654a476',
    'eevee_preview.py':'eab1810e58b0708196d0028d283068deb174bdf2871c3ee22ba6da4be7ddc149'}
summary = {'status':'COMPLETE_BOUNDED_DIAGNOSIS', 'visual_acceptance':'FAIL',
    'physical_source_sha256':sha(physical), 'preview_source_sha256':sha(preview),
    'helper_sha256': helper_sha, 'helpers_modified':False,
    'new_render_count':1, 'rebake_count':0, 'source_saved':False, 'gpu_released':True,
    'render':record, 'baseline':{'path':str(baseline),'sha256':sha(baseline),'viewed_native':True},
    'cycles_references':[{'camera':camera,'path':str(reference_folder/(camera+'.png')),
        'sha256':sha(reference_folder/(camera+'.png')),'viewed_native':True,
        'parent_render_settings':{'exposure':2.4,'resolution':[960,540],'samples':32,'frame':1}}
        for camera in ['CAM_MAIN_L3_STUDY_B','CAM_MAIN_L1_KITCHEN_B','CAM_GUEST_L2_BEDROOM_NORTH_B']],
    'pixel_evidence':pixels, 'probe_scale_calculations':probes, 'nominal_geometry_checks':rooms,
    'established':['Intensity zero does not remove Study rectangle.',
        'Upper and lower sampled bright wall points lie outside MAIN_L3 volume; central dark point lies inside.',
        'Uniform RNA density8 is scaled by volume extent; Study surfel spacing approximately0.823m.',
        'Old spacing metadata denominator resolution-1 differs from actual resolution+1.'],
    'not_established':['No baked SH/validity/virtual-offset data extracted.',
        'No corrected-coverage or scale-aware density bake tested.',
        'No whole-scene visual acceptance or motion test.'],
    'recommended_next_single_variable':'Separate MAIN_L3 coverage correction and one-volume rebake, retaining density and all light parameters; do not combine density changes.',
    'report':str(QA/'eevee-iteration06-volume-review.md')}
write(QA/'eevee-iteration06-volume-summary.json', summary)
whole_path = QA/'eevee-iteration06-summary.json'
whole = read(whole_path)
whole['volume_diagnostic'] = {'summary':str(QA/'eevee-iteration06-volume-summary.json'),
    'report':str(QA/'eevee-iteration06-volume-review.md'), 'new_render_count':1,
    'result':'FAIL_RECTANGLE_REMAINS', 'preview_saved':False,
    'hypotheses':'Coverage/world fallback and coarse scale-dependent surfel capture; not proven corrupted cached normals.',
    'metadata_correction':'Old actual_grid_spacing_m uses resolution-1; actual nominal sample interval uses resolution+1. Existing bake geometry unaffected.'}
write(whole_path, whole)
print(json.dumps({'status':summary['status'], 'render_sha256':record['sha256'],
    'preview_sha256':summary['preview_source_sha256'], 'metrics':metrics,
    'probes':probes, 'room_counts':[(r['room'],r['nominal_centers_in_polygon'],r['nominal_centers_with_backface_first_hits']) for r in rooms]},indent=2))
