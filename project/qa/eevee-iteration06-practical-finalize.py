"""Finalize actual review and preserve the margin profile as unaccepted."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];QA=ROOT/'qa';OUT=QA/'eevee-iteration06-practical'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,indent=2),encoding='utf-8')
path=OUT/'report.json';d=load(path)
assert d['status']=='RENDERED'
assert sha(ROOT/'scene/Fallingwater_preview_iteration06.blend')==d['source_sha256']
assert sha(ROOT/'scene/Fallingwater_iteration06.blend')=='172b76340d1224a2b98f415b21042d19ad7fba4d849543d7156beb17e5fcf055'
assert sha(Path(d['candidate_blend']))==d['candidate_sha256'] and sha(Path(d['png']))==d['png_sha256']
assert sha(ROOT/'scripts/eevee_preview.py')=='f68abbfde2ff6164618486a0df078bb144311e78482bfd794d15568d3b6803cd'
assert sha(ROOT/'scripts/eevee_glass.py')=='5ccc9326bc33bac735e76cf6a85051f7da31f86a7243e1979052c6710654a476'
files={'baseline':QA/'eevee-iteration06/CAM_MAIN_L3_STUDY_B_EV2p4.png','candidate':Path(d['png']),
    'cycles':ROOT/'renders/previews/iteration06-cycles-lighting-reference/CAM_MAIN_L3_STUDY_B.png'}
images={k:np.asarray(Image.open(p).convert('RGB')).astype(np.int16) for k,p in files.items()}
assert all(v.shape==(540,960,3) for v in images.values())
d.update(status='REVIEWED',visual_acceptance='FAIL_INTERNAL_PATCHES_AND_EXCESS_DARKNESS',
    partial_result='Large unoccluded World overbrightness reduced; overall shading remains unaccepted.',
    viewed_native=True,process_exit_code=0,gpu_released=True,source_unchanged=True,helpers_unchanged=True)
d['viewed_images']=[{'role':k,'path':str(p),'sha256':sha(p),'viewed_native':True} for k,p in files.items()]
d['pixel_evidence']=[{'pixel':list(p),'display_rgb':{k:v[p[1],p[0]].tolist() for k,v in images.items()}}
    for p in [(720,275),(720,125),(710,454),(600,60),(350,230)]]
d['display_rgb_metrics']={
    'baseline_to_cycles_mean_abs':float(np.abs(images['baseline']-images['cycles']).mean()),
    'candidate_to_cycles_mean_abs':float(np.abs(images['candidate']-images['cycles']).mean()),
    'candidate_to_baseline_mean_abs':float(np.abs(images['candidate']-images['baseline']).mean()),
    'unit':'8-bit display RGB codes, not linear light or perceptual acceptance score'}
d['report']=str(QA/'eevee-iteration06-practical-review.md')
save(path,d)
profile_path=OUT/'profile.json';profile=load(profile_path)
profile['coverage_margin_check']='PASS_FOR_DEFINED_GEOMETRY_DOMAIN_AND_BIAS'
profile['visual_acceptance']=d['visual_acceptance']
profile['production_adopted']=False;profile['review_report']=d['report'];save(profile_path,profile)
whole_path=QA/'eevee-iteration06-summary.json';whole=load(whole_path)
whole['practical_coverage_diagnostic']={k:d[k] for k in ['status','visual_acceptance','partial_result','source_sha256','bake_seconds','render_seconds','candidate_blend','candidate_sha256','png','png_sha256','report']}
save(whole_path,whole)
earlier_path=QA/'eevee-iteration06-volume-summary.json';earlier=load(earlier_path)
earlier['subsequent_practical_candidate']={'result':d['visual_acceptance'],'partial_result':d['partial_result'],
    'report':d['report'],'profile':str(profile_path),'combined_configuration':True,'production_adopted':False}
earlier['recommended_next_single_variable']='Superseded by tested standalone coverage, density32, and combined coverage/lattice/density candidate; all visual FAIL. Do not repeat as unrun or adopt a new default from these results.'
save(earlier_path,earlier)
print(json.dumps({'status':d['status'],'visual_acceptance':d['visual_acceptance'],
    'margin_check':profile['coverage_margin_check'],'source_unchanged':True,'candidate_sha256':d['candidate_sha256']}))
