"""Prepare new observations before fitting; no image or production scene changes."""
import json,hashlib,copy
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
old=json.loads((ROOT/'data/photo-match-points.json').read_text(encoding='utf-8'))
photos={p['id']:copy.deepcopy(p) for p in old['photos']}
p=photos['guest_exterior_10']
p['previous_points_path']='project/data/photo-match-points.json; unchanged'
p['points']=[]
# Manual post/head and post/sill junction centers picked from the 3x crop before
# optimization. The old picks sometimes used the outer trim or stone silhouette.
head=[(87,95),(174,181),(245,254),(298,309),(336,348),(365,378),(388,401),(407,420)]
sill=[(87,461),(174,485),(245,510),(298,530),(336,542),(365,551),(388,561),(407,567)]
for i in range(8):
 for kind,uv,edge in [('H',head[i],[4,5]),('S',sill[i],[0,1])]:
  p['points'].append(dict(id=f'W{i}{kind}',label=f'South facade post {i} west-to-east / {kind}',photo_px=list(uv),object=f'GUEST_L1_LOUNGE_FRONT_steel_window_0_mullion_{i}',edge_vertices=edge,role='fit' if i in (0,2,4,7) else 'holdout',pixel_pick_uncertainty=4,independently_verified=False,correspondence_confidence='B eight visible sequential posts; C model equal division, not independent bay survey',observation_basis='Viewed original A10 plus 3x unretouched crop before fit; center of physical frame junction, not top of rough stone'))
p['points'].append(dict(id='R01',label='Candidate outer soffit step; noncoplanar independent diagnostic holdout',photo_px=[657,467],object='GUEST_LOW_ARM_ROOF',vertex=1,role='holdout',pixel_pick_uncertainty=4,independently_verified=False,correspondence_confidence='U candidate local step association; not a confirmed roof corner',blocker='Exact longitudinal station of photographed soffit step not independently identified; exclude from acceptance'))
p['camera_eye_bounds']=[[0,31.5,7.0],[4.0,36.0,10.4]]
p['camera_seed']={'eye':[3.1,35.4,8.85],'target':[17,35.4,9.4],'focal_pixels':765}
p['gates']='NOT_RUN: planar repeated-window diagnostic only; roof correspondence U, no 8 independently verified dispersed non-coplanar structural points'
p['fit_plan']='Exactly one bounded 7-parameter fit; fixed principal point/scan; geometry, picks and train split frozen; 8 training window endpoints, 8 held window endpoints, 1 uncertain roof candidate held separately.'
guest=photos['guest_living_11']
guest['iteration05_findings']={
 'new_mesh_presence':['GUEST_FIREPLACE_north_mass','GUEST_FIREPLACE_corner_hood','GUEST_FIREPLACE_hearth','GUEST_L1_WEST_LOUNGE_lintel_0','GUEST_L1_WEST_LOUNGE_sill_0'],
 'left_firebox_candidates':{'P04':{'object':'GUEST_L1_WEST_LOUNGE_lintel_0','vertex':2},'P05':{'object':'GUEST_L1_WEST_LOUNGE_sill_0','vertex':6}},
 'not_fitted_reason':'Only two visible firebox left corners have plausible actual mesh candidates; right corners obscured by lamp; 1985 window return and ceiling return not securely paired; no 8 dispersed verified points.',
 'window_return_observation':'At approximately (365,287)-(365,382), photographed south window turns toward west wall; existing west bay is an empty door opening, so it must not be assigned a south mullion index by convenience.',
 'uncertain_ceiling_vertices':[[418,247],[704,230],[741,181]],
 'new_fireplace_does_not_clear_prior_blockers':True}
main=photos['main_living_48']
main['iteration05_additional_candidates']=[
 {'id':'COL_TOP_1','photo_px':[269,220],'candidate_object':'MAIN_L1_south_stone_pier_1','candidate_vertices':[6,7],'role':'unresolved','reason':'Pier identity plausible from northwest kitchen view; exact north/east/west face junction not independently confirmed'},
 {'id':'COL_TOP_2','photo_px':[294,219],'candidate_object':'MAIN_L1_south_stone_pier_1','candidate_vertices':[4,5,6,7],'role':'unresolved','reason':'Rough stone edge and ceiling cover obscure original rectangular substrate corner'},
 {'id':'COL_BASE','photo_px':[303,382],'candidate_object':'MAIN_L1_south_stone_pier_1','candidate_vertices':[0,1,2,3],'role':'unresolved','reason':'Stone relief, chair and desk hide actual floor-to-substrate corner; cannot promote visible random stone endpoint'}]
main['gates']='NOT_RUN: noncoplanar pier candidates require exact face confirmation; old light-screen diagnostic camera is not production camera'
audit={'test_id':'GEO-07','version':3,'scene_label':'iteration05','method':'One frozen-selection exterior diagnostic; other candidates explicitly unresolved; no geometry edits','photos':[p,guest,main]}
target=ROOT/'data/photo-match-points-iteration05.json'
target.write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding='utf-8')
for photo in [p,guest,main]:
 im=Image.open(ROOT.parent/photo['local_path']).convert('RGB');d=ImageDraw.Draw(im)
 d.rectangle((0,0,im.width,42),fill='#111111');d.text((10,8),'QA ONLY - observed/candidate landmarks BEFORE fitting',fill='white');d.text((10,24),'No photo warp. Orange = unresolved, cyan = window fit, yellow = holdout.',fill='white')
 rows=photo['points'] if photo is not main else photo['iteration05_additional_candidates']
 for q in rows:
  x,y=q['photo_px'];color='cyan' if q['role']=='fit' else 'yellow' if q['role']=='holdout' else 'orange'
  d.ellipse((x-4,y-4,x+4,y+4),outline=color,width=2);d.text((x+5,y+5),q['id'],fill=color)
 im.save(ROOT/'qa'/f'photo-match-{photo["id"]}-iteration05-observed.png')
print('Prepared',target,hashlib.sha256(target.read_bytes()).hexdigest())
