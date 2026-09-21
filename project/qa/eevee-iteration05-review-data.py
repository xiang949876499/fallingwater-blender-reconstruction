"""Read completed EEVEE renders; verify hashes and create an unretouched review sheet."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1]
sets = [('eevee-iteration05','eevee-iteration05-setup.json'),
        ('eevee-iteration05-additional','eevee-iteration05-extra-setup.json')]
notes = {
 'CAM_MAIN_L1_LIVING_B': ('FAIL_LIGHTING','Glazing is readable; broad horizontal black shading on fireplace and dining wall. Raising exposure is not an accepted fix.'),
 'CAM_MAIN_L1_KITCHEN_B': ('FAIL_LIGHTING','Broad horizontal black shading obscures cabinet faces, stone wall and appliances; room details are not reliably readable.'),
 'CAM_MAIN_L2_MASTER_B': ('PARTIAL_GLASS_ONLY','Windows and open casement are transparent without former blue-black blocks. Column and desk retain excessive dark bands; no overall lighting acceptance.'),
 'CAM_GUEST_L1_LOUNGE_B': ('FAIL_CAMERA','Almost full-frame near wall/fireplace; parent reports old camera intersects newly built hearth. Negative evidence retained; no exposure repair.'),
 'CAM_MAIN_OVERVIEW': ('FAIL_CAMERA','Foreground foliage heavily obscures building/glazing, so this viewpoint does not establish exterior window acceptance.'),
 'CAM_MAIN_B_BATH_B': ('FAIL_LIGHTING','Visible practical lamp and cork walls, but large inverted triangular black region with broad edges; fixtures largely outside this framing.'),
 'CAM_MAIN_L3_STUDY_B': ('FAIL_LIGHTING','Shelf/desk/chair visible, but large black wall rectangle and thick dark halos; narrow bright floor-wall edge also needs investigation.'),
 'CAM_GUEST_B1_LAUNDRY_B': ('FAIL_LIGHTING','Appliances and room visible; a large V-shaped dark patch appears on the left door and ceiling remains uneven.'),
 'CAM_GUEST_L2_BEDROOM_NORTH_B': ('PARTIAL_GLASS_ONLY','Glazing is readable; cabinet/wall furniture have broad black patches/halos. General lighting is not accepted.')}
summary = {'status':'RENDERABLE_NOT_VISUALLY_ACCEPTED', 'views':[],
    'visual_review':'All nine first PNG images actually opened at native 960x540. Living +1.6 bracket and prior Cycles fireplace view also opened.',
    'exposure_calibration':'No new camera exposure certified. All base frames use +0.8; brackets are saved candidates, not calibrated values.'}
for rel in ['scene/Fallingwater_iteration05.blend','scene/Fallingwater_preview_iteration05.blend',
            'qa/eevee-iteration05-additional/Fallingwater_preview_extra_views.blend']:
    path = root/rel
    summary[rel] = {'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}
sheet = Image.new('RGB',(1440,3*294),(25,28,30)); draw=ImageDraw.Draw(sheet)
index=0
for directory, filename in sets:
    report_path=root/'qa'/directory/filename
    report=json.loads(report_path.read_text())
    if not summary.get('bakes'):
        summary['bakes']=report['probe_bakes']
        summary['bake_seconds_total']=sum(r['seconds'] for r in report['probe_bakes'])
        summary['glass_invariants']=report['glass_invariants']
        summary['reflection_capture']=report['glass_preview']['reflection_probe']
        summary['source_sha256']=report['source_sha256']
    for view in report['first_views']:
        path=Path(view['path']); picture=Image.open(path).convert('RGB')
        assert picture.size==(960,540)
        assert hashlib.sha256(path.read_bytes()).hexdigest()==view['sha256']
        result,note=notes[view['camera']]
        view['visual_acceptance']=result; view['visual_review_notes']=note
        record={**view,'hash_verified':True,'actually_opened':True}
        summary['views'].append(record)
        x,y=(index%3)*480,(index//3)*294
        sheet.paste(picture.resize((480,270),Image.Resampling.LANCZOS),(x,y+24))
        draw.text((x+5,y+4),view['camera'].removeprefix('CAM_')+' | '+result,fill='white')
        index+=1
    report['visual_acceptance']='FAIL: see per-view results and eevee-iteration05-review.md'
    report['status']='RENDERED_HASH_VERIFIED_VISUAL_REVIEW_COMPLETE'
    report_path.write_text(json.dumps(report,indent=2),encoding='utf-8')
sheet.save(root/'qa/eevee-iteration05-nine-views-contact.png')
summary['bake_operator_pass_count']=sum(b['operator_result']==['FINISHED'] for b in summary['bakes'])
summary['bake_intended_room_records']=sum(len(b['rooms']) for b in summary['bakes'])
summary['render_seconds_total']=sum(v['seconds'] for v in summary['views'])
summary['gpu_released']=True
(root/'qa/eevee-iteration05-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k.startswith('scene/') or k in ('status','bake_seconds_total','render_seconds_total','bake_operator_pass_count','bake_intended_room_records')},indent=2))
