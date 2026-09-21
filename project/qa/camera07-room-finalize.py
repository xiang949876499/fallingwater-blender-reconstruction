"""Freeze the manual120-image review with provenance and04 comparisons."""
import collections,csv,hashlib,json,math
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'qa'
source=ROOT/'renders/room-contact-sheets/iteration07/views'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
benchmark=load(source/'render-benchmark.json')
config=load(QA/'camera07e-settings-frozen.json')
assert benchmark['status']=='PASS' and len(benchmark['runs'])==120
assert benchmark['scene_sha256']=='bf50530009e4a93315915815473188c91d891272ef2d8e9e0169b704bd2e2f16'
assert sha(ROOT/'data/camera-settings-reviewed.json')==sha(QA/'camera07e-settings-frozen.json')=='4def78dcbae91f3292562f41796adec71c4680b64e04301f051fdc1833ce8666'
notes=list(csv.DictReader((QA/'camera07-room-observations.psv').open(encoding='utf-8'),delimiter='|'))
assert len(notes)==len({r['camera'] for r in notes})==120
assert {r['camera'] for r in notes}==set(config)=={r['camera'] for r in benchmark['runs']}
old_ledger=load(QA/'camera04-visual-ledger.json')
old={r['camera']:r for r in old_ledger['cameras']}
contacts=load(QA/'camera07-room-contact-manifest.json')
assert contacts['page_count']==20 and contacts['available_source_count']==120
assert contacts['render_benchmark_status_at_build']=='PASS'
contact_map={r['camera']:(page,r) for page in contacts['pages'] for r in page['cameras']}
runs={r['camera']:r for r in benchmark['runs']}
reopened=set('''CAM_MAIN_L2_BATH_N_A CAM_MAIN_L2_BATH_N_B CAM_MAIN_L2_BATH_G_B
CAM_GUEST_L1_BOILER_B CAM_MAIN_L1_SERVANT_A CAM_MAIN_L1_SERVANT_B CAM_MAIN_L2_CLOSET_M_B CAM_MAIN_L2_DRESSING_B CAM_MAIN_L3_GALLERY_B
CAM_MAIN_L2_BATH_M_B CAM_MAIN_L2_BATH_G_A CAM_MAIN_L2_TERRACE_N_B CAM_MAIN_L1_LOGGIA_A CAM_GUEST_L1_STAIR_HALL_B
CAM_MAIN_B_PLUNGE_B CAM_MAIN_L1_COAT_B CAM_MAIN_L2_CLOSET_G_A CAM_MAIN_L2_CLOSET_G_B CAM_MAIN_L3_ALCOVE_B CAM_MAIN_L3_BATH_A
CAM_MAIN_L2_DRESSING_A CAM_MAIN_L2_GUEST_A CAM_MAIN_L2_MASTER_A CAM_MAIN_L3_BATH_B CAM_MAIN_L3_ALCOVE_A CAM_MAIN_L3_STAIR_B CAM_MAIN_L3_GALLERY_A'''.split())
structural_tags={'VISIBLE_WALL_BASE_GAP','VISIBLE_MASONRY_GAPS','VISIBLE_LANDING_GAP','VISIBLE_FLOOR_BLACK_REGION','VISUAL_SEAM_SUSPECT','CEILING_SEAM_SUSPECT'}
context_tags={'STRUCTURE_CONTEXT_REVIEW','EXPOSED_INTERIOR_EDGES'}
records=[]
for n in notes:
    name=n['camera'];page,c=contact_map[name];path=source/(name+'.png')
    assert sha(path)==c['sha256'] and runs[name]['status']=='PASS'
    with Image.open(path) as im:assert im.size==(640,360)
    tags=n['issue_tags'].split(',')
    if n['status']=='FRAMING_FAIL':assert name in reopened,name
    records.append({'camera':name,'room_id':config[name]['room_id'],'actually_viewed':True,
        'review_method':'Original640x360 image on lossless1280x1170 contact page, each page2 columns x3 rows actually opened at original size; selected anomalies also individually reopened.',
        'contact_sheet':page['page'],'contact_sheet_sha256':page['sha256'],'individual_image_reopened':name in reopened,
        'image':c['source'],'sha256':c['sha256'],'dimensions':[640,360],'exposure':runs[name]['exposure'],
        'diagnostic_status':n['status'],'issue_tags':tags,'notes':n['observation'],
        'structure_assessment':'CONFIRMED_FLOOR_WALL_GAP_BY_ROOT_PROBE' if name in ('CAM_MAIN_L2_BATH_N_A','CAM_MAIN_L2_BATH_N_B') else 'VISIBLE_ANOMALY_CAUSE_UNVERIFIED' if structural_tags.intersection(tags) else 'OPENING_CONTEXT_REVIEW_NO_FAILURE_INFERRED' if context_tags.intersection(tags) else 'NO_SPECIFIC_VISIBLE_ANOMALY_FLAGGED_NOT_A_STRUCTURAL_PASS',
        'previous04':{'diagnostic_status':old[name]['diagnostic_status'],'notes':old[name]['notes'],'image_sha256':old[name]['sha256']},
        'final_visual_acceptance':'NOT_ACCEPTED'})
counts=collections.Counter(r['diagnostic_status'] for r in records)
for s in ('READABLE_DIAGNOSTIC','LIMITED_COMPOSITION','FRAMING_FAIL','ILLUMINATION_FAIL'):counts.setdefault(s,0)
room_groups=collections.defaultdict(list)
for r in records:room_groups[r['room_id']].append(r)
assert len(room_groups)==60 and all(len(x)==2 for x in room_groups.values())
transition=collections.Counter((r['previous04']['diagnostic_status'],r['diagnostic_status']) for r in records)
room_records=[]
for rid,rows in room_groups.items():
    rows=sorted(rows,key=lambda r:r['camera'])
    room_records.append({'room_id':rid,'camera_a':rows[0]['camera'],'camera_b':rows[1]['camera'],
        'previous04_a':rows[0]['previous04']['diagnostic_status'],'previous04_b':rows[1]['previous04']['diagnostic_status'],
        'current07_a':rows[0]['diagnostic_status'],'current07_b':rows[1]['diagnostic_status'],
        'readable_diagnostic_views':sum(x['diagnostic_status']=='READABLE_DIAGNOSTIC' for x in rows),
        'structure_findings':[x['camera'] for x in rows if structural_tags.intersection(x['issue_tags'])],
        'final_room_acceptance':'NOT_ACCEPTED'})
root_probe=QA/'bathroom07-floor-probe.json'
probe=load(root_probe)
assert probe['scene_sha256']==benchmark['scene_sha256']
ledger={'scene':benchmark['scene'],'scene_sha256':benchmark['scene_sha256'],
    'settings_sha256':sha(QA/'camera07e-settings-frozen.json'),'render_benchmark_sha256':sha(source/'render-benchmark.json'),
    'render_status':benchmark['status'],'successful_runs':len(runs),'unique_images':120,'actual_images_reviewed':120,'contact_pages_actually_opened':20,
    'individual_images_reopened_count':len(reopened),'individual_images_reopened':sorted(reopened),
    'resolution':[640,360],'samples':16,'engine':benchmark['engine'],'device':benchmark['device']['device'],'counts':dict(counts),
    'diagnostic_definition':'READABLE_DIAGNOSTIC means the named inspection space or its principal feature and relationships are recognizable, even if other flagged defects exist. It is not photography, final lighting, materials, structural integrity, source fidelity, route or final quality PASS. LIMITED means useful partial view only. FRAMING_FAIL means blocking/semantic mismatch prevents useful space view. ILLUMINATION_FAIL means lighting prevents recognizing content. Dark but readable and bright but readable remain explicitly flagged.',
    'scope':'All120 renders from60 inspection-space records, not60 bedrooms. All20 contact pages actually viewed, all10 framing failures and17 additional ambiguous views individually reopened. Reports only; no camera, geometry, production JSON or render mutation.',
    'geometry_evidence':{'root_bathN_probe':'qa/bathroom07-floor-probe.json','root_probe_sha256':sha(root_probe),'confirmed':'Three BathN_A wall-base pixels hit SITE_Continuous_BearRun_Terrain; wall/floor control points hit correct surfaces. BathN_B shows the same continuous strip. Other black regions are not proven holes by color alone.'},
    'comparison04':{'ledger':'qa/camera04-visual-ledger.json','ledger_sha256':sha(QA/'camera04-visual-ledger.json'),'counts':old_ledger['counts'],'transitions':[{'from':a,'to':b,'count':c} for (a,b),c in sorted(transition.items())],
        'scope':'Comparison to prior recorded04 human labels, not a new re-review of all04 images. Camera poses, geometry, lighting and review display size changed together (04 used426x240 thumbnails,07 uses640x360); label changes are not a controlled quality score or causal effect.'},
    'rooms_with_two_readable_views':sum(r['readable_diagnostic_views']==2 for r in room_records),'rooms_with_one_readable_view':sum(r['readable_diagnostic_views']==1 for r in room_records),'rooms_with_no_readable_view':sum(r['readable_diagnostic_views']==0 for r in room_records),
    'structure_anomaly_camera_count':sum(bool(structural_tags.intersection(r['issue_tags'])) for r in records),
    'issue_counts':dict(collections.Counter(t for r in records for t in r['issue_tags'])),
    'room_pairs':room_records,'cameras':records,'final_visual_acceptance':'NOT_ACCEPTED'}
save(QA/'camera07-room-visual-ledger.json',ledger)
with (QA/'camera07-room-pairs.csv').open('w',encoding='utf-8-sig',newline='') as f:
    fields=['room_id','previous04_a','previous04_b','current07_a','current07_b','readable_diagnostic_views','structure_findings','final_room_acceptance']
    w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(room_records)
short={'READABLE_DIAGNOSTIC':'R','LIMITED_COMPOSITION':'L','FRAMING_FAIL':'F','ILLUMINATION_FAIL':'I'}
matrix=['# 第07轮60检查空间双视图对照','',
    'R=诊断可辨；L=有限视图；F=构图失败；I=照明导致无法辨认。R仍可能有结构缺口等独立问题；没有一项表示最终摄影或结构通过。04列读取旧台账，07全部图实际查看。','',
    '| 检查空间 | 04 A/B | 07 A | 07 B | 结构/接缝可见异常 |','|---|---|---|---|---|']
for rr in room_records:
    a,b=(next(x for x in records if x['camera']==rr[k]) for k in ('camera_a','camera_b'))
    matrix.append(f"| {rr['room_id']} | {short[rr['previous04_a']]}/{short[rr['previous04_b']]} | [{short[a['diagnostic_status']]}](../{a['image']}) | [{short[b['diagnostic_status']]}](../{b['image']}) | {', '.join(n.rsplit('_',1)[-1] for n in rr['structure_findings']) or '未特指，不等于通过'} |")
matrix+=['','完整逐图说明、源PNG及接触页SHA256见 [120图台账](camera07-room-visual-ledger.json)。','']
(QA/'camera07-room-pair-comparison.md').write_text('\n'.join(matrix),encoding='utf-8')
print(json.dumps({'counts':dict(counts),'room_pairs':len(room_records),'two_one_zero_readable':[ledger['rooms_with_two_readable_views'],ledger['rooms_with_one_readable_view'],ledger['rooms_with_no_readable_view']],'individual_reopened':len(reopened),'structure_anomaly_cameras':ledger['structure_anomaly_camera_count']},indent=2))
