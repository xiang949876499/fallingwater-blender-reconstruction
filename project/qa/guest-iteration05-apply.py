"""One-time source-supported repair; preserved pre-edit module/data alongside this file."""
import json
import hashlib
from pathlib import Path
p=Path('D:/zx/test/project/data/guest_house.json')
backup=Path('D:/zx/test/project/qa/guest-iteration05-before-guest_house.json')
if hashlib.sha256(p.read_bytes()).hexdigest()!=hashlib.sha256(backup.read_bytes()).hexdigest():
    raise RuntimeError('Historical one-time migration: current data is not the preserved pre-edit input. Do not repeat.')
d=json.loads(p.read_text(encoding='utf-8'))
w={v['id']:v for v in d['walls']}
r={v['id']:v for v in d['rooms']}
w['GUEST_L1_CHAUFFEUR_EAST']['openings'][0].update(span=[.5/70,17/70],reference='Guest sheet1 original: open north end of east wall, y351.5..368; C tracing ~1px',swing=-1)
r['GUEST_L1_CHAUFFEUR_LOUNGE']['entry']=[283,359.75]
d['slabs'].append({'id':'GUEST_L1_CHAUFFEUR_DOOR_LANDING','polygon':[[284,351],[306,351],[306,369],[284,369]],'level':'L1','thickness':.18,'reference':'HABS guest1: unhatched flagstone vestibule north of basement descent; ends before descending run','evidence':'A plan topology / C pixel trace'})
w['GUEST_L2_UPPER_ROOM_EAST']['openings'][0].update(span=[(266.9-202)/219,(280.3-202)/219],reference='Guest sheet2 actual original: short hall-facing gap between bath south wall and north/middle partition; source y266.9..280.3',swing=-1)
r['GUEST_L2_BEDROOM_NORTH']['entry']=[283,273.6]
for a in d['adjacency']:
 if a['from']=='GUEST_L2_HALL' and a['to']=='GUEST_L2_BEDROOM_NORTH':
  a.update(evidence='A guest02 direct Hall door below Bath south wall, y266.9..280.3; old model opening inside Bath was misplaced',verified_source='qa/guest-iteration05-grid-guest-02-270.png',requires_retest='iteration05 actual integrated meshes')
w['GUEST_STONE_CHIMNEY'].update(a=[327.4,349],b=[327.4,361.9],thickness=.305,reference='HABS guest1 plan and guest4 section looking north: chimney at service EAST/living WEST wall, not chauffeur east wall; exact back/flue footprint C',evidence='A section height retained; B/C plan identity and trace')
w['GUEST_L1_WEST_LOUNGE']['openings'].insert(0,{'span':[0,(375.2-363)/(440-363)],'type':'firebox','sill':.20,'head':1.08,'reference':'Guest1 NW lounge corner cutout + guest4 section + HABS A11; real void with west/north back walls built separately','evidence':'B form / C opening height'})
d['fireplace_detail']={'enabled':True,'source_bounds_px':[329.4,361.9,345.0,375.2],'back_x_px':[324.5,329.4],'north_back_y_px':[358.0,361.9],'hearth_top_m':.20,'opening_head_m':1.08,'hood_top_m':2.12725,'reference':['HABS guest01 original NW lounge cutout','HABS guest04 section looking north visible brick-lined opening','HABS PA-5346-A-11 photo circa1985 visible unsupported corner fireplace'],'evidence':'A source existence and plan registration; B corner-opening identity; C heights, chamber lining and unseen back thickness','do_not_copy':'1985 vessels, books, lamp or furniture arrangement not treated as contemporary surveyed objects'}
# Room inspection boundary excludes the source stone mass and projecting firebox.
r['GUEST_L1_LOUNGE']['polygon']=[[346,365],[440,365],[440,397],[475,397],[475,430],[440,430],[440,441],[336,441],[336,376],[346,376]]
d['pool']['dry_west_notch']={'x_max_px':733,'y_max_px':477,'stair_from':[696.5,435],'stair_to':[721.5,435],'stair_width_m':1.0544,'count':4,'landing_px':[[721.5,425],[733,425],[733,449],[721.5,449]],'reference':'HABS guest01 pool: dry raised stair/planter projection at NW corner; unchanged maximum inner/outer shell dimensions','evidence':'A plan topology; C trace and riser division'}
d['iteration05_revision']={'status':'MODULE_EDITED_NOT_INTEGRATED','basis_scene':'scene/Fallingwater_iteration04.blend','basis_sha256':'247d20f7863e4f7e9c18587d4c032bd663857a420bcfb828d271195665841ac2','changes':['Source chauffeur threshold, vestibule and chimney registration','North bedroom direct Hall door relocated from false Bath opening','Actual corner fireplace cavity','Dry pool stair/planter water exclusion'],'qa':'All 17 previously passing dimensions and stair clearances must be actually rerun; iteration04 geometry PASS cannot be reused.'}
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
