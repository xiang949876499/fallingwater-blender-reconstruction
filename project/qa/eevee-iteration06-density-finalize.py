"""Record the inspected density candidate; no new Blender work."""
import hashlib,json
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];QA=ROOT/'qa'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,indent=2),encoding='utf-8')
path=QA/'eevee-iteration06-density/report.json';d=load(path)
assert d['status']=='RENDERED'
assert sha(ROOT/'scene/Fallingwater_preview_iteration06.blend')==d['source_sha256']
assert sha(ROOT/'scene/Fallingwater_iteration06.blend')=='172b76340d1224a2b98f415b21042d19ad7fba4d849543d7156beb17e5fcf055'
assert sha(Path(d['candidate_blend']))==d['candidate_sha256']
assert sha(Path(d['png']))==d['png_sha256']
assert sha(ROOT/'scripts/eevee_preview.py')=='f68abbfde2ff6164618486a0df078bb144311e78482bfd794d15568d3b6803cd'
assert sha(ROOT/'scripts/eevee_glass.py')=='5ccc9326bc33bac735e76cf6a85051f7da31f86a7243e1979052c6710654a476'
files={'baseline':QA/'eevee-iteration06/CAM_MAIN_L3_STUDY_B_EV2p4.png',
    'candidate':Path(d['png']), 'cycles':ROOT/'renders/previews/iteration06-cycles-lighting-reference/CAM_MAIN_L3_STUDY_B.png'}
arrays={k:np.asarray(Image.open(v).convert('RGB')).astype(np.int16) for k,v in files.items()}
assert all(v.shape==(540,960,3) for v in arrays.values())
d['viewed_images']=[{'role':k,'path':str(v),'sha256':sha(v),'viewed_native':True} for k,v in files.items()]
d['pixel_evidence']=[{'pixel':list(p),'display_rgb':{k:v[p[1],p[0]].tolist() for k,v in arrays.items()}}
    for p in [(720,275),(720,125),(710,454),(600,60),(350,230)]]
d['mean_absolute_display_rgb_difference']=float(np.abs(arrays['candidate']-arrays['baseline']).mean())
d.update(status='REVIEWED',visual_acceptance='FAIL_RECTANGLE_AND_WORLD_BRIGHT_REGIONS_REMAIN',viewed_native=True,
    process_exit_code=0,gpu_released=True,source_unchanged=True,helper_sources_unchanged_by_density_test=True)
d['findings']=['Captured middle wall modestly brighter and furniture shadows change.',
    'Large rectangle boundary and upper/lower/left overbrightness remain in their original positions.',
    'Density32 alone does not resolve the dominant defect; does not establish corrupted cached normals.',
    'Separate narrow bottom strip persists in physical Cycles and was not geometrically diagnosed.']
d['process_memory_observation']=load(QA/'eevee-iteration06-density/process-memory-observation.json')
d['report']=str(QA/'eevee-iteration06-density-review.md');save(path,d)
whole_path=QA/'eevee-iteration06-summary.json';whole=load(whole_path)
whole['density_diagnostic']={k:d[k] for k in ['status','visual_acceptance','source_sha256','bake_seconds','render_seconds','candidate_blend','candidate_sha256','png','png_sha256','report']}
save(whole_path,whole)
earlier_path=QA/'eevee-iteration06-volume-summary.json';earlier=load(earlier_path)
earlier['subsequent_controlled_candidates']=[
    {'change':'MAIN_L3 Z bounds only, with coupled nominal lattice/scale-relative offset changes',
     'result':'FAIL','report':str(QA/'eevee-iteration06-coverage-review.md')},
    {'change':'Original bounds, MAIN_L3 surfel density8 to32 only',
     'result':'FAIL','report':str(QA/'eevee-iteration06-density-review.md')}]
earlier['recommended_next_single_variable']='Previous coverage recommendation has now been tested and failed independently, as has density32. No combined candidate or new default adopted.'
save(earlier_path,earlier)
print(json.dumps({'status':d['status'],'visual_acceptance':d['visual_acceptance'],
    'source_unchanged':True,'candidate_sha256':d['candidate_sha256'],'new_bakes':1,'new_renders':1}))
