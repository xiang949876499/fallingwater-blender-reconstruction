"""Verify unretouched diagnostic PNGs and record actual visual review."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
qa=ROOT/'qa'
entries=[
 ('Bath baseline','eevee-iteration05-additional/CAM_MAIN_B_BATH_B_first.png',None,'FAIL: enormous inverted dark triangle'),
 ('Bath: raytracing off','eevee-iteration05-dark-raytracing_off.png','eevee-iteration05-dark-raytracing_off.json','FAIL: inverted triangle remains'),
 ('Bath: volume intensity zero','eevee-iteration05-dark-volume_intensity_zero.png','eevee-iteration05-dark-volume_intensity_zero.json','FAIL: inverted triangle remains and deepens'),
 ('Bath: practical shadows off','eevee-iteration05-dark-practical_shadows_off.png','eevee-iteration05-dark-practical_shadows_off.json','DIAGNOSTIC_ONLY: triangle disappears; not an acceptable global fix'),
 ('Bath: own filament excluded','eevee-iteration05-shadow-own-filament-excluded.png','eevee-iteration05-shadow-own-filament-excluded.json','PASS_LOCAL_SYMPTOM: broad triangle removed; narrow corner shadow remains; no whole-scene acceptance'),
 ('Living baseline','eevee-iteration05/CAM_MAIN_L1_LIVING_B_first.png',None,'FAIL: broad horizontal dark band'),
 ('Living: Sun shadows off','eevee-iteration05-living-sun_shadows_off.png','eevee-iteration05-living-sun_shadows_off.json','FAIL: broad wall band remains despite brighter furnishings'),
 ('Living: volume intensity zero','eevee-iteration05-living-volume_intensity_zero.png','eevee-iteration05-living-volume_intensity_zero.json','FAIL: mid-wall darkens; bright upper strip and lower edge remain'),
 ('Living: Fast GI off','eevee-iteration05-living-fastgi_off.png','eevee-iteration05-living-fastgi_off.json','PASS_LOCAL_SYMPTOM: horizontal band removed; stone-joint detail weakens and image remains noisy/dim; not final acceptance'),
]
records=[]
for label,image_rel,json_rel,finding in entries:
    path=qa/image_rel
    img=Image.open(path).convert('RGB')
    assert img.size==(960,540)
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    item={'label':label,'path':str(path),'sha256':digest,'resolution':list(img.size),
          'viewed_native':True,'finding':finding}
    if json_rel:
        report_path=qa/json_rel
        report=json.loads(report_path.read_text(encoding='utf-8-sig'))
        assert report['status']=='RENDERED' and report['sha256']==digest
        report['visual_acceptance']=finding
        report['viewed_native']=True
        report_path.write_text(json.dumps(report,indent=2),encoding='utf-8')
        item['seconds']=report['seconds']
    if label.startswith('Bath'):
        pixels=np.asarray(img,dtype=float)
        item['dark_center_rgb_mean_20px']=pixels[315:335,495:515].mean(axis=(0,1)).round(3).tolist()
    records.append(item)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
for name,subset,cols in [('bath',records[:5],3),('living',records[5:],2)]:
    out=Image.new('RGB',(480*cols,300*((len(subset)+cols-1)//cols)),(235,235,235))
    draw=ImageDraw.Draw(out)
    for index,item in enumerate(subset):
        x=(index%cols)*480;y=(index//cols)*300
        image=Image.open(item['path']).convert('RGB').resize((480,270),Image.Resampling.LANCZOS)
        out.paste(image,(x,y+30));draw.text((x+8,y+7),item['label'],fill=(25,25,25),font=font)
    out.save(qa/('eevee-iteration05-shadow-'+name+'-contact.png'))
preview=ROOT/'scene/Fallingwater_preview_iteration05.blend'
assert hashlib.sha256(preview.read_bytes()).hexdigest()=='b855de89492af8ae31ae4d53bb2674f518ea13cf2e8f1585b2b9a31b35511939'
summary={'source_preview':str(preview),'source_preview_sha256':hashlib.sha256(preview.read_bytes()).hexdigest(),
    'all_diagnostic_scenes_unsaved':True,'gi_rebaked':False,'reviewed_images':records,
    'bath_causal_conclusion':'The point proxy shadowing its own emissive filament causes the giant inverted triangle. Single-light filament exclusion removes it while leaving all shadow flags and other casters unchanged.',
    'living_conclusion':'Disabling only Fast GI removes the broad horizontal wall band while retaining SCREEN ray tracing, all real shadows and all seven baked volume intensities. Stone-joint definition weakens; current image remains dim/noisy, so only symptom removal is accepted.',
    'candidate_scope':'One fixed Bath view and one fixed Living view only, no moving-camera or whole-scene acceptance; source preview not modified.',
    'cancelled_evidence':'eevee-iteration05-shadow-jittered.json is CANCELLED_BEFORE_PNG, not a completed candidate.'}
(qa/'eevee-iteration05-shadow-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps({'reviewed_images':len(records),'bath_rgb_samples':[(r['label'],r.get('dark_center_rgb_mean_20px')) for r in records[:5]],'source_unchanged':True},indent=2))
