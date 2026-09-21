"""Record the completed native visual review; no rendering or scene changes."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa/eevee-iteration07-study'
path = OUT / 'report.json'
report = json.loads(path.read_text(encoding='utf-8'))
assert report['status'] in ('RENDERED_SAVED', 'RENDERABLE_VISUAL_FAIL')
reference = ROOT / 'renders/previews/iteration07-focus/CAM_MAIN_L3_STUDY_B_EV2p4.png'
reference_benchmark = ROOT / 'renders/previews/iteration07-focus/render-benchmark.json'
benchmark = json.loads(reference_benchmark.read_text(encoding='utf-8'))
assert benchmark['scene_sha256'] == report['source_sha256']
assert benchmark['frame'] == report['frame'] == 48
assert benchmark['resolution'] == report['resolution'] == [960, 540]
assert benchmark['max_samples'] == report['samples'] == 32
run = next(r for r in benchmark['runs'] if r['camera'] == report['camera'])
assert run['camera_settings'] == {} and run['lens_mm'] == report['lens']
assert any(r['exposure'] == 2.4 and r['same_linear_render'] for r in run['exposure_bracket'])

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

assert sha(report['source_scene']) == report['source_sha256']
assert sha(report['candidate_blend']) == report['candidate_sha256']
assert sha(report['png']) == report['png_sha256']
assert report['helper_hashes'] == {n: sha(ROOT / 'scripts' / n) for n in report['helper_hashes']}
a = np.asarray(Image.open(report['png']).convert('RGB'))
b = np.asarray(Image.open(reference).convert('RGB'))
report.update(status='RENDERABLE_VISUAL_FAIL', visual_acceptance='FAIL', production_adopted=False,
    gpu_job_complete=True, process_exit_code=0, review_report=str(ROOT / 'qa/eevee-iteration07-study-review.md'),
    actual_native_images_opened=[report['png'], str(reference)],
    physical_reference={'png': str(reference), 'sha256': sha(reference), 'benchmark': str(reference_benchmark),
        'frame': 48, 'exposure': 2.4, 'same_saved_camera': True, 'selected_bracket_not_base_exposure': True},
    actual_findings=['Broad wall dark band persists relative to matched Cycles.',
        'Dark lobes behind chair and dark ceiling field persist.',
        'Upper wall is excessively bright relative to Cycles.',
        'Previous narrow floor-perimeter bright strip is absent in both current images.'],
    preview_readiness='FAIL: one-level renderable evidence only; six other levels NOT_BAKED.',
    display_mae_code_values=float(np.abs(a.astype(float)-b).mean()),
    metric_scope='Display RGB values support actual visual inspection; not photometric acceptance.',
    shutdown_warning='Unable to delete file; process exited 0 after confirmed PNG and scene saves.',
    saved_scene_status_note='Saved before visual review: embedded visual status is NOT_REVIEWED. This reviewed report records FAIL; no metadata-only re-save changed the candidate SHA.')
report['pixel_comparison'] = {label: {'pixel': [x,y], 'eevee': a[y,x].tolist(), 'cycles': b[y,x].tolist()}
    for label,x,y in [('wall_middle',720,275),('wall_upper',720,125),('wall_lower',710,454),('ceiling',480,50),('left_wall',320,280)]}
report['level_status']['MAIN_L3'] = 'BAKED_VISUAL_FAIL'
report['profile'].update(coverage_margin_check='PASS', visual_acceptance='FAIL', production_adopted=False)
path.write_text(json.dumps(report, indent=2), encoding='utf-8')
(OUT / 'profile.json').write_text(json.dumps(report['profile'], indent=2), encoding='utf-8')
summary = {k: report[k] for k in ('status','source_scene','source_sha256','candidate_blend','candidate_sha256',
    'png','png_sha256','physical_reference','level_status','frame','camera','exposure','resolution','samples',
    'bake_seconds','render_seconds','visual_acceptance','preview_readiness','actual_findings','review_report',
    'helper_hashes','production_adopted','gpu_job_complete','source_unchanged','scope')}
(ROOT / 'qa/eevee-iteration07-summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
print(json.dumps(summary, indent=2))
