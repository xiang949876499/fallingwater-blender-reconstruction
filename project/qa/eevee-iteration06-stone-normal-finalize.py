"""Finalize the actually viewed one-image material discriminant."""
import hashlib,json
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];QA=ROOT/'qa'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,indent=2),encoding='utf-8')
p=QA/'eevee-iteration06-stone-normal-zero.json';d=load(p)
assert d['status']=='RENDERED' and sha(Path(d['source']))==d['source_sha256']
assert sha(ROOT/'scene/Fallingwater_preview_iteration06.blend')=='e317241899808995f049e8d3343eac96c591cbecfddaa980949d6babb51ccce6'
assert sha(ROOT/'scene/Fallingwater_iteration06.blend')=='172b76340d1224a2b98f415b21042d19ad7fba4d849543d7156beb17e5fcf055'
assert sha(ROOT/'scripts/eevee_preview.py')=='f68abbfde2ff6164618486a0df078bb144311e78482bfd794d15568d3b6803cd'
assert sha(ROOT/'scripts/eevee_glass.py')=='5ccc9326bc33bac735e76cf6a85051f7da31f86a7243e1979052c6710654a476'
base=QA/'eevee-iteration06-practical/CAM_MAIN_L3_STUDY_B_EV2p4.png';candidate=Path(d['png'])
assert sha(candidate)==d['png_sha256']
images={k:np.asarray(Image.open(v).convert('RGB')).astype(np.int16) for k,v in [('baseline',base),('candidate',candidate)]}
assert all(v.shape==(540,960,3) for v in images.values())
d.update(status='REVIEWED',visual_acceptance='FAIL_LARGE_DARK_PATTERN_UNCHANGED',viewed_native=True,
    process_exit_code=0,gpu_released=True,source_unchanged=True,production_adopted=False)
d['baseline']={'path':str(base),'sha256':sha(base),'viewed_native':True}
d['mean_absolute_display_rgb_difference']=float(np.abs(images['candidate']-images['baseline']).mean())
d['pixel_evidence']=[{'pixel':list(p),'display_rgb':{k:v[p[1],p[0]].tolist() for k,v in images.items()}}
    for p in [(720,275),(720,125),(710,454),(600,60),(350,230)]]
d['finding']='Strength zero leaves large wall lobes/ceiling bands effectively unchanged. Do not adopt bump disabling; does not test capture normals because GI was not rebaked.'
d['report']=str(QA/'eevee-iteration06-stone-normal-review.md');save(p,d)
whole_path=QA/'eevee-iteration06-summary.json';whole=load(whole_path)
whole['stone_shading_normal_diagnostic']={k:d[k] for k in ['status','visual_acceptance','source_sha256','render_seconds','png','png_sha256','report','gi_rebaked','production_saved']}
save(whole_path,whole)
print(json.dumps({'status':d['status'],'result':d['visual_acceptance'],
    'mean_absolute_RGB_difference':d['mean_absolute_display_rgb_difference'],'new_renders':1,'bakes':0,'source_unchanged':True}))
