"""Bind final camera QA evidence and outside-viewpoint limitations to exact files."""
import json, hashlib, collections, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(rel):return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def sha(rel):return hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
cfg_path='qa/camera05-settings-frozen-v2.json'
cfg=read(cfg_path);old=read('qa/camera04-settings-frozen.json')
verification=read('qa/camera05-frozen-v2-verification.json')
rooms=read('rooms.json');rm={r['id']:r for r in rooms}
expected={'CAM_'+r['id']+'_'+s for r in rooms for s in ('A','B')}
assert set(cfg)==expected and len(cfg)==120
assert verification['status']=='GEOMETRY_ONLY_PASS' and len(verification['cameras'])==120
assert all(not r['issue'] and r['stored_outside_flag_matches'] for r in verification['cameras'])
assert verification['settings_sha256']==sha(cfg_path)==sha('data/camera-settings-reviewed.json')
assert verification['scene_sha256']=='6bcfee7841c22e8e2b636352cfca79ae94968afb4235fc20cdc57e250ae046ff'
notes={
'CAM_MAIN_B_BATH_A':'On adjacent wine-cellar finish looking through the real bath doorway; changed lower lens shift needs a new image.',
'CAM_MAIN_B_BOILER_B':'Mechanical-room inspection from its actual connecting floor; internal-room occupation is not claimed.',
'CAM_MAIN_B_PLUNGE_A':'Pool inspection from the north bridge approach; a dry external viewpoint, not a point in water.',
'CAM_MAIN_L1_COAT_A':'Closet inspection from adjacent entry finish, through the opening.',
'CAM_MAIN_L1_TERRACE_W_B':'At the living-west threshold finish, inspecting the exterior terrace.',
'CAM_MAIN_L2_BATH_N_A':'Bath inspection from adjacent upper hall finish.',
'CAM_MAIN_L2_BATH_G_A':'Bath inspection from the actual guest-bath doorway threshold.',
'CAM_MAIN_L2_BATH_M_A':'Bath inspection from adjacent master-bedroom finish.',
'CAM_MAIN_L2_STAIR_A':'On an actual upper tread of the named stair flight; upper endpoint outside the nominal lower-level polygon.',
'CAM_MAIN_L3_BATH_A':'Bath inspection from adjacent gallery finish.',
'CAM_GUEST_L1_GUEST_ROOM_A':'Eye is 16.406mm west of the revised guest-room polygon; it remains on real main floor. Adjacent-viewpoint flag corrected; room occupancy not accepted.',
'CAM_GUEST_L1_POOL_A':'On real dry main floor beside the pool, 0.15m west of the old failed point; no claim of standing on water.',
'CAM_GUEST_L1_POOL_B':'Retained actual dry main floor viewpoint outside the water polygon.',
'CAM_GUEST_B1_STAIR_B':'On the real basement landing adjacent to the stair polygon; lower reverse view of the laundry descent.',
'CAM_GUEST_L1_BOILER_A':'Utility-room inspection from the adjacent north hall.',
}
outside=[]
for r in verification['cameras']:
    if not r['outside_current_room_polygon']:continue
    n=r['camera'];c=cfg[n]
    outside.append({'camera':n,'room_id':c['room_id'],'location':c['location'],'target':c['target'],
                    'actual_support':r['actual_center_support'],'interpretation':notes[n],
                    'point_geometry':'GEOMETRY_ONLY_PASS','semantic_and_image_acceptance':'PENDING_ACTUAL_IMAGE_REVIEW',
                    'navigation_acceptance':'NOT_ESTABLISHED_BY_POINT_TEST'})
changes=[]
for n,c in cfg.items():
    delta={k:{'before':old[n].get(k,0),'after':c.get(k,0)} for k in ('location','target','lens','shift_x','shift_y') if old[n].get(k,0)!=c.get(k,0)}
    if delta:changes.append({'camera':n,'room_id':c['room_id'],'changes':delta})
manifest={'date':'2026-09-20','scene':'scene/Fallingwater_iteration05.blend','scene_sha256':verification['scene_sha256'],
          'settings':cfg_path,'settings_sha256':sha(cfg_path),'active_build_settings':'data/camera-settings-reviewed.json',
          'status':'GEOMETRY_ONLY_PASS_VISUAL_PENDING','camera_count':len(cfg),'room_record_count':len(rooms),
          'pose_changed_camera_count':len(changes),'pose_changed_space_count':len({r['room_id'] for r in changes}),
          'previous_frozen_config':{'path':'qa/camera05-settings-frozen.json','sha256':sha('qa/camera05-settings-frozen.json'),
                                    'difference':'v2 changes only Main B Bath A shift_y from -0.44966 to -0.55 and its evidence note; pose safety is unchanged, actual shifted render pending.'},
          'geometry':verification['geometry'],'rays_cast':verification['rays_cast'],'vegetation_in_room_geometry_index':False,
          'verification':'qa/camera05-frozen-v2-verification.json','outside_viewpoints':outside,'pose_changes':changes,
          'exposure_evidence':'qa/iteration05-focus-review.md; selected by root from actual images. Reuse after pose changes remains provisional.',
          'scope_limits':['Point body/foot/head rays do not verify a continuous route or full room occupancy.',
                          'Outside viewpoints are not automatically accepted by their successful geometric probes.',
                          '41 revised views remain candidates until actual render review; full VIS05 not passed.',
                          'The 120 actually viewed iteration04 pictures are historical evidence, not current visual acceptance.'],
          'notes':['Main Coat B support name changed to actual closet finish at unchanged elevation.',
                   'Pool A actual center is 2.93mm below selected stored support near the floor bevel; within the explicit 40mm storage check.'],
          'evidence_files':[]}
for rel in ('qa/camera05-original-verification.json','qa/camera05-composition-supplement-geometry.json','qa/camera05-residual-geometry.json',
            'qa/camera05-frozen-v2-verification.json','qa/camera04-visual-ledger.json','qa/camera04-preview-followup.json'):
    manifest['evidence_files'].append({'path':rel,'sha256':sha(rel)})
(ROOT/'qa/camera05-freeze-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:manifest[k] for k in ('settings','settings_sha256','status','camera_count','room_record_count','pose_changed_camera_count','pose_changed_space_count')}))
print('outside_viewpoints',len(outside))
