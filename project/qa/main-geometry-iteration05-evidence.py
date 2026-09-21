"""Snapshot the owned module's handoff evidence without changing architecture."""
import hashlib,json
from pathlib import Path
P=Path('D:/zx/test/project');Q=P/'qa'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def source(name,explanation):
 p=Q/name
 return {'artifact':str(p),'sha256':sha(p),'viewed':True,'derivation':explanation,'geometry_evidence':'C'}
d=json.loads((P/'data/main_house.json').read_text(encoding='utf-8'))
test=json.loads((Q/'main-geometry-iteration05-check.json').read_text(encoding='utf-8'))
before=json.loads((Q/'main-geometry-bath-seams-before.json').read_text(encoding='utf-8'))
after=json.loads((Q/'main-geometry-bath-seams-after.json').read_text(encoding='utf-8'))
dims=json.loads((Q/'main-dimensions-measured.json').read_text(encoding='utf-8'))
out={
 'iteration':'05 main-house source freeze',
 'artifacts':{str(p.relative_to(P)):sha(p) for p in [P/'scripts/main_house.py',P/'data/main_house.json',Q/'main-geometry-smoke.blend']},
 'preserved_checkpoint':{'path':'scene/Fallingwater_iteration04.blend','sha256':'247d20f7863e4f7e9c18587d4c032bd663857a420bcfb828d271195665841ac2','modified':False},
 'source_review':[
  source('main-geometry-iteration05-source-03.png','Saved main03 JPEG crop enlarged with coordinate grid, not original-resolution TIFF. North internal wine access and west rock boundary.'),
  source('main-geometry-iteration05-source-05.png','Saved main05 JPEG crop enlarged with coordinate grid. Lower curved-stair approach and UP direction.'),
  source('main-geometry-iteration05-source-06.png','Saved main06 JPEG crop enlarged with coordinate grid. DOWN direction, north upper walk, and explicitly labeled stepped canopy.'),
  source('main-dimension-resolution-spine-source.png','Original main04 TIFF-derived extension-line evidence.'),
  source('main-dimension-resolution-spine-grid.png','Original main04 TIFF-derived coordinate overlay; analytical lines are C.'),
  source('main-dimension-resolution-east-parapet-grid.png','Main09 JPEG elevation contour crop, not a surveyed dimension label.'),
  source('main-dimension-resolution-east-parapet-datums.png','Main09 JPEG two-datum comparison; 55mm graphical uncertainty.')],
 'topology':{'wine':'Basement Stair -> internal north passage -> Wine. No west outside doorway.','bath_guest':'Main L2 Hall -> Guest Bath; guest bedroom is not the direct neighbor of that door.','exterior_stair':'L2 North Terrace -> south-low curved stair -> north-high upper walk -> guest connector.','canopy':'Roof over stair is tagged non-walkable; removed old southward L3 false walking floor.'},
 'handoff':d['exterior_connector_handoff'],
 'bounded_main_only_clearance':{'checks':test['check_count'],'summary':test['summary'],'scene_sha256':test['provenance']['scene_sha256'],'body_width_m':.36,'head_height_m':1.95,'continuous_swept_body':False,'integrated_site_furniture_guest':False},
 'bath_wine_floor_seam':{'viewed_image':'renders/previews/camera04-review/CAM_MAIN_B_BATH_B.png','black_pixel_rays':len(before['pixels']),'black_pixel_findings':'All six ray samples first hit sound floor. Visible black strips coincide with old coplanar overlap; cause requires same-camera render confirmation.','grid_before':before['summary'],'grid_after':after['summary'],'new_threshold_source_rect':[285,244,291,283],'actual_door_source_y':[255,275],'walls_unchanged':True,'visible_finish_overlap_removed':True,'same_camera_rerender_status':'NOT_RUN by this subagent'},
 'dimensions':{'standard':dims['tolerance_standard'],'counts':dims['counts'],'north_spine':next(m for m in dims['measurements'] if m['id']=='MAIN_CHAIN_03'),'all_dimensions_accepted':False},
 'superseded_checks':['Old arc landing assertions in main-geometry-living-fixes.json belong to the old reversed stair. Use iteration05-check for current geometry.','Old main-dimension-resolution-initial-measured.json used source reading uncertainty as tolerance; it is preserved but not a GEO-02 PASS.'],
 'remaining':['Full integrated 05 guest/site/furniture traversal and updated same-camera imagery.','Stair count/canopy clearance/cross-building Z remain explicitly C.','16 nominal or unregistered dimension correspondences remain NOT_RUN.'],
 'documentation_cleanup':'Owned current notes and dimension-resolution document reconciled; root README/AGENTS/STATUS remain integrator-owned.'}
(Q/'main-geometry-iteration05-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'artifacts':out['artifacts'],'checks':test['check_count'],'bath_grid_after':after['summary'],'dimensions':dims['counts']},indent=2))
