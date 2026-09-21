"""Finalize inspected one-volume coverage evidence and metadata-only proof."""
import hashlib,json
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'qa'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,indent=2),encoding='utf-8')
p=QA/'eevee-iteration06-coverage/report.json';d=load(p)
assert d['status']=='RENDERED'
assert sha(ROOT/'scene/Fallingwater_preview_iteration06.blend')==d['source_sha256']
assert sha(ROOT/'scene/Fallingwater_iteration06.blend')=='172b76340d1224a2b98f415b21042d19ad7fba4d849543d7156beb17e5fcf055'
assert sha(Path(d['candidate_blend']))==d['candidate_sha256']
assert sha(Path(d['png']))==d['png_sha256']
files={'baseline':QA/'eevee-iteration06/CAM_MAIN_L3_STUDY_B_EV2p4.png',
    'candidate':Path(d['png']), 'cycles':ROOT/'renders/previews/iteration06-cycles-lighting-reference/CAM_MAIN_L3_STUDY_B.png'}
arrays={k:np.asarray(Image.open(v).convert('RGB')).astype(np.int16) for k,v in files.items()}
d['viewed_images']=[{'role':k,'path':str(v),'sha256':sha(v),'viewed_native':True} for k,v in files.items()]
d['pixel_evidence']=[{'pixel':list(p),'display_rgb':{k:v[p[1],p[0]].tolist() for k,v in arrays.items()}}
    for p in [(720,275),(720,125),(710,454),(600,60),(350,230)]]
d['mean_absolute_display_rgb_difference']=float(np.abs(arrays['candidate']-arrays['baseline']).mean())
d.update(status='REVIEWED',visual_acceptance='FAIL_LATERAL_BOUNDARY_AND_EXCESS_DARKNESS',viewed_native=True,process_exit_code=0,gpu_released=True)
scale_before=min(a/b for a,b in zip(d['before_scale'],d['grid_resolution']))
scale_after=min(a/b for a,b in zip(d['after_scale'],d['grid_resolution']))
d['derived_scale_changes']={
    'surface_bias_m':[.05*scale_before,.05*scale_after],
    'escape_bias_m':[.1*scale_before,.1*scale_after],
    'normal_bias_z_offset_m':[.3*d['before_nominal_spacing_m'][2],.3*d['after_nominal_spacing_m'][2]],
    'physical_surfel_density_unchanged':True,
    'MAIN_L2_bounds_z_overlap_m':4.894800186157227-d['after_bounds'][0][2]}
d['findings']=['Upper/lower wall and ceiling excessive brightness is reduced.',
    'Middle wall darker than Cycles; left-side bright/dark boundary remains.',
    'Bounds change couples to nominal Z lattice, dilation span and scale-relative capture offsets.',
    'Separate bottom narrow strip persists in physical Cycles; its geometric cause was not diagnosed here.']
d['report']=str(QA/'eevee-iteration06-coverage-review.md')
save(p,d)
helper=ROOT/'scripts/eevee_preview.py';b=helper.read_bytes()
old=b.replace(b'        # Blender 5.2 grid_sample_position uses (index+1)/(resolution+1):\n        # the object bounds include the runtime padding around nominal samples.\n',b'').replace(b"(record['resolution'][i]+1) for i in range(3)]",b"(record['resolution'][i]-1) for i in range(3)]")
old_sha=hashlib.sha256(old).hexdigest()
assert old_sha=='eab1810e58b0708196d0028d283068deb174bdf2871c3ee22ba6da4be7ddc149'
metadata_path=QA/'eevee-iteration06-spacing-check.json';metadata=load(metadata_path)
assert metadata['status']=='PASS' and metadata['helper_sha256']==sha(helper)
metadata['reconstructed_previous_helper_sha256']=old_sha
metadata['reconstruction_scope']='Only remove two explanatory comments and revert the denominator to recover byte-identical prior helper.'
save(metadata_path,metadata)
whole_path=QA/'eevee-iteration06-summary.json';whole=load(whole_path)
whole['coverage_diagnostic']={k:d[k] for k in ['status','visual_acceptance','source_sha256','bake_seconds','render_seconds','candidate_blend','candidate_sha256','png','png_sha256','report']}
whole['spacing_metadata_correction']={'status':'PASS','report':str(metadata_path),'helper_sha256':sha(helper),'rendering_defaults_unchanged':True}
save(whole_path,whole)
print(json.dumps({'status':d['status'],'visual_acceptance':d['visual_acceptance'],'source_unchanged':True,
    'helper_metadata_only_proof':'PASS','candidate_sha256':d['candidate_sha256']}))
