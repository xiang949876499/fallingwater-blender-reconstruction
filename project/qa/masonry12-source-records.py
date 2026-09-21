"""Create metadata for the completed read-only masonry inspection."""
import json,hashlib
from pathlib import Path
from PIL import Image
W=Path(__file__).resolve().parents[2];R=W/'project';Q=R/'qa'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
specs=[
('project/qa/forest-canopy11-source-official-classic.jpg','https://fallingwater.org/wp-content/uploads/2021/03/FW_ZOOM_Classic-View_SPRING.jpg','B',[[470,51,679,342]],'Official reference only; exclude public package; not a texture.'),
('project/qa/forest-canopy11-source-official-east.jpg','https://fallingwater.org/wp-content/uploads/2021/03/FW_ZOOM_East-Elevation_SPRING.jpg','B',[[942,226,1104,419],[1112,190,1279,790]],'Official reference only; exclude public package; not a texture.'),
('research/references/architecture/main-10-sheet.jpg','https://www.loc.gov/pictures/item/pa1690.sheet.00010a/','A',[[467,444,631,522]],'HABS advisory retained in existing reference manifest; private reference, not texture.'),
('research/references/architecture/main-10-inspection-levels.png','https://tile.loc.gov/storage-services/master/pnp/habshaer/pa/pa1600/pa1690/sheet/00010a.tif','A',[],'Existing TIFF-derived datum crop only; not full TIFF visual verification.'),
('research/references/architecture/main-07-sheet.jpg','https://www.loc.gov/pictures/item/pa1690.sheet.00007a/','A',[[293,171,317,339]],'HABS advisory retained; private reference, not texture.'),
('project/renders/previews/main-terrace11a/CAM_MAIN_L2_TERRACE_W_A.png',None,'C',[[920,0,960,109]],'Authored current scene; not historic source.'),
('project/renders/previews/main-terrace11a/CAM_MAIN_L2_TERRACE_S_A.png',None,'C',[[0,0,130,86]],'Authored current scene; not historic source.'),
('project/assets/textures/worn_rock_natural_01_diff_2k.jpg','https://polyhaven.com/a/worn_rock_natural_01','C',[],'Existing CC0 texture; not Fallingwater stone scan.')]
viewed=[]
for path,url,evidence,rects,rights in specs:
    p=W/path
    with Image.open(p) as im:size=list(im.size)
    viewed.append({'path':path,'sha256':sha(p),'source_url':url,'size':size,'actually_viewed':True,'viewer':'site_visual','date':'2026-09-21','evidence':evidence,'rectangles_xyxy':rects,'rectangles_status':'Approximate visual ROI, not camera-registered measurement','rights_and_scope':rights})
full=W/'research/references/architecture/main-10-original.tif'
viewed.append({'path':str(full.relative_to(W)),'sha256':sha(full),'actually_viewed':False,'attempted':True,'error':'view_image: fs/readFile invalid base64 dataBase64, Invalid symbol61 offset20952285','fallback':'main-10-sheet.jpg and existing main-10-inspection-levels.png actually viewed'})
(Q/'masonry12-source-viewed.json').write_text(json.dumps(viewed,indent=2),encoding='utf-8')
probe=json.loads((Q/'masonry12-source-probe.json').read_text(encoding='utf-8'))
rows=probe['target_objects'];courses=[o for o in rows if o['name'].startswith('MAIN_tower_course')]
assert len(courses)==300
targets={'status':'DESIGN_ONLY_NOT_AUTHORIZED_FOR_BUILD','source_scene':probe['source'],'source_sha256':probe['sha256'],'frame':48,
 'replace_finish_exact_names':[o['name'] for o in courses],'finish_source_records':courses,
 'structural_cap_flue_guards':[o for o in rows if o not in courses],
 'proposed_new_geometry':'At most3 batches: long west/east faces plus existing west-tower south end finish; no structural rewrite',
 'proposal_is_C':True,'scene_saved':False,'rendered':False}
(Q/'masonry12-source-targets.json').write_text(json.dumps(targets,indent=2),encoding='utf-8')
audit={'scope':'QA-only read-only task; no production change',
 'source_still_same':sha(Path(probe['source']))==probe['sha256'],
 'dependency_hashes_still_same':{p:sha(R/p)==expected for p,expected in probe['dependencies'].items()},
 'owned_files':[str(p.relative_to(R)) for p in sorted(Q.glob('masonry12-source-*'))],
 'report_lines':len((Q/'masonry12-source-review.md').read_text(encoding='utf-8').splitlines()),
 'root_AGENTS_lines':len((W/'AGENTS.md').read_text(encoding='utf-8').splitlines()),
 'root_project_markdown_inventory':[str(p.relative_to(W)) for p in sorted(R.glob('*.md'))],
 'neat_freak_resolution':'Consolidated own source/probe/target/report records; central STATUS/manifests/build/AGENTS and unrelated accepted helpers are root-owned, unchanged by this task.',
 'no_commit':True,'no_publication':True}
assert audit['source_still_same'] and all(audit['dependency_hashes_still_same'].values())
(Q/'masonry12-source-doc-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
print(json.dumps({'viewed_images':8,'failed_full_TIFF_display':1,'exact_finish_names':len(courses),'guards':len(targets['structural_cap_flue_guards']),'source_still_same':audit['source_still_same'],'dependencies_still_same':all(audit['dependency_hashes_still_same'].values()),'report_lines':audit['report_lines']}))
