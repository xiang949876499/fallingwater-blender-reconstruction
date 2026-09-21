"""Bounded read-only source audit. Run from repository root with ordinary Python.

Original TIFF is never changed. Windows/ink bands are declared from visual source
identification, not selected to match model coordinates. No Blender or rendering.
"""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
QA = ROOT / 'project/qa'
PREFIX = 'master-ceiling12-source-'
SOURCE = ROOT / 'research/references/architecture/main-10-original.tif'
EXPECTED_SHA = 'db6591996c049961a50ba593c002dc394d5708f1c15c5935e1c3671aed1e2ac7'
Image.MAX_IMAGE_PIXELS = 300_000_000

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

assert sha(SOURCE) == EXPECTED_SHA
im = Image.open(SOURCE).rotate(-90, expand=True)
assert im.size == (17702, 13632)

# Original oriented pixel coordinates; no anisotropic resizing.
CROPS = {
    'west-levels-upper': (14383,7261,16077,9249),
    'west-levels-lower': (14227,9491,16077,11081),
    'master-native': (7105,8851,9767,10130),
    'west-datum-lines': (9508,8160,14487,11012),
    'east-levels': (14175,1988,16077,5808),
    'west-scale': (13657,11686,15783,12810),
    'west-third-connect': (7300,8970,12000,9360),
    'west-second-connect': (4600,9730,12000,10030),
    'west-main-connect': (9400,10700,14100,10930),
    'west-roof-connect': (9800,8240,12500,8460),
    'west-tower-connect': (8000,7500,12500,7740),
    'west-third-labelled': (10800,8900,16077,9250),
    'west-second-labelled': (11200,9730,16077,10030),
    'west-main-labelled': (13000,10660,16077,11000),
    'west-roof-labelled': (10600,8175,16077,8480),
    'west-tower-labelled': (10550,7480,16077,7790),
}

def bands(box, fraction=.7):
    pixels = np.array(im.crop(box), dtype=bool)
    rows = np.where((~pixels).mean(axis=1) >= fraction)[0] + box[1]
    groups = []
    for y in rows.tolist():
        if groups and y == groups[-1][-1] + 1:
            groups[-1].append(y)
        else:
            groups.append([y])
    return [[g[0], g[-1]] for g in groups]

PROBES = {
    'tower_datum_tail': (15820,7600,15900,7670),
    'roof_datum_tail': (15820,8310,15900,8380),
    'third_datum_tail': (15820,9040,15900,9110),
    'second_datum_tail': (15820,9870,15900,9950),
    'main_datum_tail': (15820,10810,15900,10880),
    'tower_datum_near_building': (11100,7580,11400,7690),
    'tower_coping': (8500,7580,8900,7690),
    'roof_datum_near_building': (11600,8300,11900,8390),
    'roof_plane': (9900,8300,10200,8390),
    'third_datum_near_building': (11300,9020,11600,9130),
    'third_datum_middle': (12300,9020,12500,9130),
    'third_common_top': (8700,9020,9250,9130),
    'third_right_interior_REJECTED_AS_TERRACE_DATUM': (10430,9020,10630,9230),
    'second_datum_near_building': (11480,9870,11900,9960),
    'second_datum_middle': (12700,9870,12900,9960),
    'second_left_terrace_top': (4900,9870,5400,9960),
    'second_terrace_near_window_top': (6500,9870,7000,9960),
    'master_floor_top': (7900,9870,9200,9960),
    'master_floor_top_east_probe': (9600,9870,9700,9960),
    'master_low_soffit': (7700,9240,8150,9300),
    'master_high_soffit': (8700,9110,9250,9190),
    'main_datum_middle': (13900,10790,14100,10890),
    'main_ground_right': (11700,10790,12200,10890),
    'main_floor_left': (7300,10790,7550,10890),
    'east_labels_SEPARATE_VIEW_NOT_CALIBRATION': (15700,2000,15800,5800),
}
probes = {key: {'native_box': box, 'black_fraction_threshold': .7,
                'ink_bands_y_inclusive': bands(box)} for key, box in PROBES.items()}

levels = [
    ('main', 'MAIN LEVEL TERRACE', "0'-0\"", 0., 10839.5),
    ('second', 'SECOND LEVEL TERRACE', "9'-4\"", 2.8448, 9907.5),
    ('third', 'THIRD LEVEL TERRACE', "17'-3 1/4\"", 5.26415, 9075.5),
    ('roof', 'ROOF', "24'-11 3/4\"", 7.61365, 8346.5),
    ('tower', 'MAIN TOWER', "32'-9 1/2\"", 9.9949, 7635.5),
]
scales = []
for lower, upper in zip(levels, levels[1:]):
    dz, dy = upper[3] - lower[3], lower[4] - upper[4]
    scales.append({'pair': [lower[0], upper[0]], 'delta_printed_m': dz,
                   'delta_datum_native_px': dy, 'conditional_m_per_px': dz/dy,
                   'qualification': 'Adjacent labelled datums, not proof of uniform graphic scale or finish identity.'})

local_scale = scales[1]['conditional_m_per_px']
picks = {'top': 9078.5, 'high': 9145., 'low': 9282.5, 'floor': 9923.5}
# Whole ink-band envelopes include the independent east floor probe and thick
# source pen strokes. These are reading bounds, not statistical confidence.
envelopes = {'top': [9073,9085], 'high': [9139,9151],
             'low': [9277,9288], 'floor': [9917,9929]}

def difference(name, bottom, top):
    px = picks[bottom] - picks[top]
    lo = envelopes[bottom][0] - envelopes[top][1]
    hi = envelopes[bottom][1] - envelopes[top][0]
    # Tail line bands each span one pixel; allow an extra pixel for their
    # 1-3px drift nearer the building, without silently moving either plane.
    slo, shi = 2.41935/836, 2.41935/828
    return {'id': name, 'pair': [bottom, top], 'nominal_native_px': px,
            'ink_band_distance_px': [lo,hi], 'conditional_nominal_m': px*local_scale,
            'conditional_ink_and_datum_range_m': [lo*slo,hi*shi]}

metrics = [difference('step', 'low','high'), difference('low_clear','floor','low'),
           difference('high_clear','floor','high'), difference('north_plate_graphic_thickness','high','top'),
           difference('south_plate_graphic_thickness','low','top')]

actual_planes_scale = 2.41935/(picks['floor']-picks['top'])
old = json.loads((QA/'master-ceiling11-source-review.json').read_text(encoding='utf-8'))['bounded_graphical_section_measurement']
old_native_scale = old['calibration_scale_m_per_normalized_pixel']*1024/17702
step = metrics[0]['conditional_nominal_m']
north_thickness = metrics[3]['conditional_nominal_m']
physical = {'master_finish_z':2.8668,'l2_source_datum_z':2.8448,
            'l3_source_top_z':5.26415,'low_underside_z':4.8468,
            'high_underside_z':5.0,'ceiling_panel_thickness':.018,
            'overhead_elongated_roof_bottom_z':5.03415,
            'overhead_l3_terrace_slab_bottom_z':5.04415}

report = {
    'schema_version':1,'date_local':'2026-09-21',
    'status':'SOURCE_HEIGHT_OPEN_NO_JUSTIFIED_CEILING_ONLY_CORRECTION',
    'scope':'Read-only local raster source review; new ceiling12 QA files only; no Blender, model edits, rendering, download or navigation rerun.',
    'source':{'path':str(SOURCE.relative_to(ROOT)),'sha256':EXPECTED_SHA,
              'native_raw_size':[13632,17702],'orientation':'clockwise 90 degrees, no resampling',
              'oriented_size':list(im.size),'tiff_dpi_metadata':[400,400],
              'dpi_limit':'Metadata does not establish the scale or isotropy of the drawn artwork.',
              'url':'https://www.loc.gov/pictures/item/pa1690.sheet.00010a/'},
    'printed_levels_A':[{'id':a,'text':b,'printed_value':c,'metres':d,'west_tail_line_y':e} for a,b,c,d,e in levels],
    'level_identity_findings':{
        'tower':'WEST coping top, not the tops of chimney caps. Ink7637..7640 vs near datum7636..7637.',
        'roof':'WEST sectioned upper roof plate TOP, not underside; ink8343..8354 contains near datum8347..8349.',
        'third':'WEST continuous plate TOP directly above Master, ink9073..9084 contains near datum9077..9078. Right interior floor9178..9184 is a different local surface and excluded.',
        'second':'Label identifies second TERRACE datum. The continuous left terrace-to-Master upper hatched boundary is at9921..9933,9919..9931,9918..9929: about16px BELOW the label datum. Finish equivalence is UNRESOLVED, not assumed. No stair tread selected.',
        'main':'WEST exterior ground/terrace line10833..10849 and L1 sectioned slab upper edge10838..10849 overlap datum10839..10840; upper nearby furniture line10799..10803 excluded.',
        'east_exclusion':'EAST is a separate section. ROOF there is24ft7 3/8in, not WEST24ft11 3/4in. East L2/L3 label pixel intervals confirm a similar pattern only; never mixed into Master calibration.'},
    'ink_probes':probes,
    'adjacent_vertical_scales':scales,
    'scale_causality':'Not established. Adjacent span differences persist after identifying sections/datums, but do not demonstrate nonuniform scan, wrong storey heights, or wrong printed labels. No single vertical scale is certified.',
    'graphical_picks_C':{'nominal_y':picks,'ink_envelopes_y':envelopes,
        'master_floor_identity':'Upper boundary of sectioned floor slab, visibly continuous through terrace and room. Separate finished-floor build-up is not drawn legibly: exact finish identity U.',
        'ceiling_identity':'Lowest broad south underside and highest broad north underside of same sectioned plate; thin window head and fireplace lines excluded.'},
    'local_conditional_metrics_C':metrics,
    'local_calibration_qualification':'Uses the two printed WEST terrace datums as a local vertical mapping, with their non-coincidence to Master floor explicitly unresolved; not an A dimension assertion or navigation authority.',
    'alternative_physical_plane_assumption_C':{'hypothesis':'Only if actual Master floor/top slab ink centres are treated as exactly the printed L2/L3 terrace elevations. Not established by source.',
        'm_per_px':actual_planes_scale,
        'step_m':137.5*actual_planes_scale,'low_clear_m':641*actual_planes_scale,
        'high_clear_m':778.5*actual_planes_scale},
    'sensitivity_not_a_confidence_interval':[
        {'mapping':s['pair'],'m_per_px':s['conditional_m_per_px'],
         'step_m':137.5*s['conditional_m_per_px'],'low_clear_m':641*s['conditional_m_per_px'],
         'high_clear_m':778.5*s['conditional_m_per_px']} for s in scales],
    'old_ceiling11_estimate_preserved':old,
    'old_estimate_status':'Preserved negative/superseded evidence. Absolute clearances are not accepted as source height; horizontal-to-vertical isotropy was unverified. Earlier suggestion to consider raising high face is superseded by this boundary audit.',
    'current_model_values_from_existing_11_QA_NOT_FRESH_MEASUREMENT':physical,
    'compatibility_arithmetic_NOT_PROPOSED_GEOMETRY':{
        'current_datum_storey_height_m':5.26415-2.8448,
        'current_finish_to_upper_top_m':5.26415-2.8668,
        'current_low_clear_m':4.8468-2.8668,
        'current_high_clear_m':5.0-2.8668,
        'current_step_m':.1532,
        'retain_low_plus_conditional_step_high_z':4.8468+step,
        'remaining_to_l3_top_if_raise_high_m':5.26415-(4.8468+step),
        'source_graphical_north_plate_thickness_m':north_thickness,
        'raise_existing_18mm_ceiling_before_upper_roof_intersection_m':5.03415-(5.0+.018),
        'retain_low_plus_source_graphic_step_and_north_thickness_required_top_z':4.8468+step+north_thickness,
        'retain_l3_top_plus_source_graphic_thickness_and_step_low_z':5.26415-north_thickness-step},
    'correction_boundary':[
        'Continuous low-field topology remains supported; exact plan break and all local underside elevations remain C/U.',
        'Printed L2/L3 values match existing model source datums; this audit does not establish a wrong global storey height.',
        'Source graphic step remains materially larger than model0.1532m; using old or revised C values cannot justify raising high ceiling through existing upper structure.',
        'No sufficient A/B evidence to thin upper slab, move L3, move the room floor, or raise/lower the low soffit. A ceiling-only metric correction is not authorized by this evidence.',
        'Keep source-height OPEN. Navigation1.95m/0.18m tests neither determine real architectural heights nor validate source scale.',
        'Exact constructed thickness, finish build-ups and the terrace-datum/floor offset require independent surveyed vertical detail; no more unrelated research in this bounded task.'],
    'GEO07_status':'NOT_RUN; no camera registration or photo-scale height recovery',
    'artifact_manifest':PREFIX+'crops.json',
}
(QA/(PREFIX+'review.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

manifest=[]
for key, box in CROPS.items():
    out=QA/(PREFIX+key+'.png')
    im.crop(box).convert('RGB').save(out)
    manifest.append({'id':key,'source':str(SOURCE.relative_to(ROOT)),'source_sha256':EXPECTED_SHA,
                     'orientation':'clockwise90 native pixels','native_box':box,
                     'output':str(out.relative_to(ROOT)),'size':list(Image.open(out).size),
                     'view_status':'ACTUALLY_VIEWED','viewed_on':'2026-09-21',
                     'output_sha256':sha(out)})

box=CROPS['master-native']
annot=im.crop(box).convert('RGB')
d=ImageDraw.Draw(annot)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25)
for name, x0,x1,y0,y1,color in [
    ('L3 common top: 9073..9085',8700,9250,9073,9085,'#0080c8'),
    ('High underside: 9139..9151',8700,9250,9139,9151,'#237a21'),
    ('Low underside: 9277..9288',7700,8150,9277,9288,'#c22433'),
    ('Floor slab top: 9917..9929 (finish U)',7900,9200,9917,9929,'#993dba')]:
    local=(x0-box[0],y0-box[1],x1-box[0],y1-box[1])
    d.rectangle(local,outline=color,width=3)
    pos=(local[0],local[1]-32)
    text_box=d.textbbox(pos,name,font=font)
    d.rectangle(text_box,fill='white')
    d.text(pos,name,font=font,fill=color)
out=QA/(PREFIX+'master-picks-annotated.png')
annot.save(out)
manifest.append({'id':'master-picks-annotated','source':str(SOURCE.relative_to(ROOT)),
                 'source_sha256':EXPECTED_SHA,'native_box':box,'output':str(out.relative_to(ROOT)),
                 'size':list(annot.size),'annotation':'Coloured measured ink bands only; original native crop retained.',
                 'view_status':'ACTUALLY_VIEWED','viewed_on':'2026-09-21',
                 'output_sha256':sha(out)})
for number, box in [(7,(830,156,951,323)),(8,(839,68,950,331))]:
    src=ROOT/f'research/references/architecture/main-{number:02}-sheet.jpg'
    out=QA/(PREFIX+f'main{number:02}-labels.png')
    manifest.append({'id':f'main{number:02}-labels','source':str(src.relative_to(ROOT)),
        'source_sha256':sha(src),'native_box':box,'output':str(out.relative_to(ROOT)),
        'size':list(Image.open(out).size),'resampling':'5x NEAREST display; no additional source information',
        'view_status':'ACTUALLY_VIEWED','qualification':'Existing1024px sheet only. Corroborates level words/9ft4; tiny third fraction not treated as independent strong reread.'})
overview=QA/(PREFIX+'main10-overview.png')
manifest.append({'id':'main10-overview','source':str(SOURCE.relative_to(ROOT)),
                 'source_sha256':EXPECTED_SHA,'orientation':'clockwise90',
                 'output':str(overview.relative_to(ROOT)),'size':list(Image.open(overview).size),
                 'view_status':'ACTUALLY_VIEWED','qualification':'Sheet/view identity only; no numeric picks on thumbnail.'})
(QA/(PREFIX+'crops.json')).write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'local_C_metrics':metrics,
                  'physical_plane_alternative':report['alternative_physical_plane_assumption_C'],
                  'compatibility':report['compatibility_arithmetic_NOT_PROPOSED_GEOMETRY'],
                  'reviewed_images':len(manifest),
                  'view_attestation':'Manual image inspection2026-09-21, not inferred from script success.'},indent=2))
