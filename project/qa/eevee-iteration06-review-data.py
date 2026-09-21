"""Merge preserved/resumed actual outputs and assemble exposure review sheets."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
qa=ROOT/'qa'
folder=qa/'eevee-iteration06'
reports=[json.loads((folder/n).read_text(encoding='utf-8-sig')) for n in ['eevee-iteration06-setup.json','eevee-iteration06-resume-setup.json']]
findings={
 'CAM_MAIN_B_BATH_B':('PARTIAL_LOCAL_FIX','Washbasin and doorway are readable; no giant dark triangle in this new pose. Close composition does not show the whole room.'),
 'CAM_MAIN_L1_LIVING_B':('PARTIAL_LOCAL_FIX','Former broad horizontal band removed, but stone joints weaken and surfaces look soft/flat. No final material/lighting acceptance.'),
 'CAM_MAIN_L1_KITCHEN_B':('FAIL_LIGHTING','Broad black area remains above back counter and across lower halves of upper cupboards; scene is dim.'),
 'CAM_MAIN_L3_STUDY_B':('FAIL_LIGHTING','Large blurred dark rectangle remains on the wall; strong spatial shading discontinuity and lower bright gap require further diagnosis.'),
 'CAM_GUEST_B1_LAUNDRY_B':('FAIL_LIGHTING','Large V-shaped shadow persists on left door. Only Bath was opted into self-filament exclusion; no global fixture claim.'),
 'CAM_GUEST_L2_BEDROOM_NORTH_B':('FAIL_LIGHTING','Window and furniture readable, but large dark rectangle/halo remains on left wall and cupboard.'),
 'CAM_GUEST_L2_BATH_B':('PARTIAL_COMPOSITION','Toilet and walls readable; dark patch enters the upper-left edge, so lighting is not fully accepted.'),
 'CAM_HERO':('PARTIAL_EXTERIOR','Building and glazing are visible at base exposure. Forest/water/material detail remains stylized; no photorealistic acceptance.'),
 'CAM_GUEST_POOL':('FAIL_WINDOW_REGION','Corrected external pose shows guest house/pool, but a blurred dark patch remains in the central window/interior region; pool reflection is very soft.'),
}
views=[]
for report in reports:
    for view in report['first_views']:
        img=Image.open(view['path']);assert img.size==(960,540)
        assert hashlib.sha256(Path(view['path']).read_bytes()).hexdigest()==view['sha256']
        status,finding=findings[view['camera']]
        item=dict(view,visual_acceptance=status,visual_finding=finding,viewed_native=True)
        for bracket in item.get('exposure_bracket',[]):
            image=Image.open(bracket['path']);assert image.size==(960,540)
            bracket['sha256']=hashlib.sha256(Path(bracket['path']).read_bytes()).hexdigest()
            bracket['viewed_contact']=False
            bracket['viewed_native']=bool(view['camera'] in ['CAM_MAIN_B_BATH_B','CAM_MAIN_L1_LIVING_B'] and bracket['exposure']==2.4)
        views.append(item)
assert len(views)==9 and len({v['camera'] for v in views})==9
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
contacts=[]
for block in range(3):
    sheet=Image.new('RGB',(1440,900),(235,235,235));draw=ImageDraw.Draw(sheet)
    for row,view in enumerate(views[block*3:block*3+3]):
        for col,bracket in enumerate(view['exposure_bracket']):
            x=480*col;y=300*row
            image=Image.open(bracket['path']).convert('RGB').resize((480,270),Image.Resampling.LANCZOS)
            sheet.paste(image,(x,y+30))
            draw.text((x+7,y+7),view['camera'].replace('CAM_','')+' EV '+str(bracket['exposure']),font=font,fill=(20,20,20))
    path=qa/('eevee-iteration06-exposure-contact-'+str(block+1)+'.png');sheet.save(path);contacts.append(str(path))
source=ROOT/'scene/Fallingwater_iteration06.blend';preview=ROOT/'scene/Fallingwater_preview_iteration06.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='172b76340d1224a2b98f415b21042d19ad7fba4d849543d7156beb17e5fcf055'
assert hashlib.sha256(preview.read_bytes()).hexdigest()=='e317241899808995f049e8d3343eac96c591cbecfddaa980949d6babb51ccce6'
summary={'status':'RENDERABLE_VISUAL_FAIL','source_scene':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'preview_scene':str(preview),'preview_sha256':hashlib.sha256(preview.read_bytes()).hexdigest(),
 'resume_cache_sha256':reports[1]['source_sha256'],'bakes':reports[0]['probe_bakes'],
 'bake_seconds':round(sum(x['seconds'] for x in reports[0]['probe_bakes']),3),
 'render_seconds':round(sum(x['seconds'] for x in views),3),'views':views,'contacts':contacts,
 'contacts_viewed':False,'settings':reports[1]['final_eevee_settings'],
 'glass_invariants':reports[1]['glass_invariants'],'camera_overrides':reports[1]['camera_overrides'],
 'reopen_check':json.loads((qa/'eevee-iteration06-reopen-check.json').read_text(encoding='utf-8')),
 'limitations':'Nine fixed views only. No current-scene motion, FPS, film or whole-scene photorealistic PASS. Shadow linking is engine-independent and restored by the tested Cycles wrapper; only original Cycles glass shader preservation is hash-verified.',
 'interruption':'Seven GI bakes and first two views completed; run interrupted to add parent-supplied POOL pose. Resumed from last all-seven GI checkpoint with --skip-bake for remaining seven views. No completed bake/image repeated.'}
(qa/'eevee-iteration06-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps({'views':len(views),'bake_seconds':summary['bake_seconds'],'render_seconds':summary['render_seconds'],'source_sha':summary['source_sha256'],'preview_sha':summary['preview_sha256']},indent=2))
