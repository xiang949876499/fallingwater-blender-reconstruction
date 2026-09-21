"""Verify and record two actually viewed diagnostic images and exposure exports."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
qa=ROOT/'qa'
labels=[('study_raymodule_off','FAIL: black wall rectangle remains and becomes darker/sharper; do not adopt ray-module disabling'),
        ('laundry_own_filament_excluded','PASS_LOCAL_SYMPTOM: giant V-shaped door shadow disappears; real door-handle/fixture/wall shadows retained')]
records=[]
for label,finding in labels:
    path=qa/('eevee-iteration06-followup-'+label+'.json')
    report=json.loads(path.read_text(encoding='utf-8'))
    assert report['status']=='RENDERED' and report['source_unchanged'] and report['invariants_passed']
    img=Image.open(report['path']);assert img.size==(960,540)
    assert hashlib.sha256(Path(report['path']).read_bytes()).hexdigest()==report['sha256']
    report['visual_acceptance']=finding;report['viewed_native']=True
    for bracket in report['exposure_bracket']:
        assert Image.open(bracket['path']).size==(960,540)
        assert hashlib.sha256(Path(bracket['path']).read_bytes()).hexdigest()==bracket['sha256']
        bracket['viewed']=True;bracket['viewed_native']=True
    path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    records.append(report)
contact=Image.new('RGB',(1920,1140),(235,235,235));draw=ImageDraw.Draw(contact)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
for row,(camera,label) in enumerate([('CAM_MAIN_L3_STUDY_B','Study'),('CAM_GUEST_B1_LAUNDRY_B','Laundry')]):
    paths=[qa/'eevee-iteration06'/(camera+'_first.png'),Path(records[row]['path'])]
    captions=[label+' baseline EV +0.8',label+(' ray module off' if row==0 else ' own filament excluded')+' EV +0.8']
    for col,(p,caption) in enumerate(zip(paths,captions)):
        x=960*col;y=570*row
        contact.paste(Image.open(p).convert('RGB'),(x,y+30));draw.text((x+8,y+5),caption,fill=(20,20,20),font=font)
contact.save(qa/'eevee-iteration06-followup-contact.png')
source=ROOT/'scene/Fallingwater_preview_iteration06.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='e317241899808995f049e8d3343eac96c591cbecfddaa980949d6babb51ccce6'
summary={'status':'TWO_DIAGNOSTICS_COMPLETED_NOT_PRODUCTION_MERGED','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'render_count':2,'exposure_export_count':4,'all_six_images_viewed_native':True,
    'total_render_seconds':sum(r['seconds'] for r in records),
    'results':[{'variant':r['variant'],'finding':r['visual_acceptance'],'seconds':r['seconds'],'path':r['path'],'sha256':r['sha256']} for r in records],
    'source_saved':False,'gi_rebaked':False,'new_lights_added':False,'helper_source_modified':False,
    'study_conclusion':'Remaining rectangle is not removed by disabling the entire ray module. This experiment alone does not distinguish direct-light shadow, baked probe lighting, or other remaining shading terms.',
    'laundry_conclusion':'The point proxy shadowing its own emissive filament causes the giant V-shaped door shadow in this view. A single-light exclusion is sufficient; other lights and casters remain unchanged.',
    'scope':'Static per-view causal evidence only. No additional camera, global linking expansion, preview save, or full-scene setting change.'}
(qa/'eevee-iteration06-followup-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
