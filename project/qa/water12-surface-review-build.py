"""Reconcile the completed static iteration from actual saved QA; no Blender launch."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def read(name):return json.loads((ROOT/'qa'/name).read_text(encoding='utf8'))
r=read('water12-surface07.json');a=read('water12-surface07-final-audit.json');d=read('water12-surface07-display.json')
summary={'status':'STATIC_GEOMETRY_PROGRESS_VISUAL_FAIL_CONTACT_PARTIAL','candidate':r['output'],'candidate_sha256':r['output_sha256'],
         'display_candidate':d['output'],'display_sha256':d['output_sha256'],'geometry':r['geometry_audit'],
         'contact_by_actual_role':a['contact'],'shared_interfaces':a['actual_shared_interfaces'],
         'nine_branches_one_component':a['all_nine_branches_share_single_component'],'connected_components':a['connected_components'],
         'largest_component_bounds':a['largest_component_bounds'],'source_sha256':r['source_sha256'],
         'visual_review':{'root_rendered':True,'root_and_water_agent_opened_both':True,'files':['renders/previews/water12-surface07/CAM_HERO.png','renders/previews/water12-surface07/CAM_WATER_DETAIL.png'],
             'actual_root_settings':{'width':1280,'height':720,'samples':48,'frame':48},
             'findings':['Transparent blue-grey bands are smooth, parallel and near-uniform in width.','Landing transitions share a conspicuous horizontal line.','Natural fanning, broken highlights, aeration and impact foam are absent.','Static geometry closure does not satisfy visual realism or motion.']},
         'physics_claims':False,'new_FLIP_or_cache_changes':False,'production_install':False,'animation_status':'NOT_IMPLEMENTED_STATIC_ONLY',
         'bounded_CSG_failure':'water12-surface06a.json: 180-second supervised hard stop, no output, observed working set 41.214GB',
         'next_parent_authorized_task':'One visual hybrid candidate from the closed body, frame48, CPU4 geometry; preserve07. Root schedules rendering. No long bake.'}
(ROOT/'qa/water12-surface-review.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
text=f'''# Water12 continuous surface reconstruction — actual static handoff

This iteration produces a complete independent full-scene candidate. **Static visual status remains FAIL.** Root rendered and opened both 1280×720, 48-sample, frame48 HERO/WATER_DETAIL views; the water agent also actually opened both images. They show smooth transparent blue-grey ribbons, very regular lateral edges and aligned pool joins. Natural fanning, breakup, aeration and impact foam are missing.

## Frozen deliverables

- Main candidate: `{r['output']}`; SHA256 `{r['output_sha256']}`.
- Display-only copy: `{d['output']}`; SHA256 `{d['output_sha256']}`. Adds `CAM_WATER12_FOOT` only. The world-space water mesh hash is `{d['water_mesh_world_sha256']}` and geometry is unchanged.
- Existing `CAM_HERO`, `CAM_WATER_DETAIL` retained. Frame48 is a static authored body. Root schedules all renders.
- Source is frozen iteration09, SHA `{r['source_sha256']}`. Visible frozen core/terrain/banks are unchanged. No production file, FLIP modifier or cache is modified.
- Builder: `scripts/water_surface12.py`; exact executed07 snapshot: `qa/water12-surface07-builder-snapshot.py`. Construction reads `data/site.json`; its recorded hash is `{r['site_config_sha256']}`.

## Geometry evidence and scope

The original folded river skin is not reused as a solid. Upper and pool surfaces use a single strictly ordered stream coordinate map. Nine rectangular section rings share the actual layer vertex indices; no overlap plane hides a gap. Corresponding surfaces are closed at actual shared edges. Floating-point shore pinches are split into separate shell fans without moving the triangles.

The final body has **700,646 vertices, 1,400,980 triangles, zero boundary edges, zero nonmanifold edges, zero degenerate triangles, and zero nonshared BVH overlap pairs**. All nine branches belong to the same connected component. Each upper and pool join has460 shared edges in total, each paired with exactly two real faces. Other isolated wet regions exist: the full body contains {a['connected_components']} connected components; this does not establish one hydraulically connected river to the remote scene extent. The remote upstream extension interface is not certified.

Geometry is C authored. Original upper water heights were retained where sampled. The crest section descends8mm from each original source section; the thin underside was adjusted locally. The original3 shape keys remain on the hidden old water, **not** on the rebuilt body. The rebuilt body is currently static. Its computed signed volume is only a closed-mesh quantity, never a discharge measurement or physical water-budget result.

The near layer omits partially wet triangles conservatively. A further133 upper and16 pool triangles were rejected when their center or edge midpoint probed the frozen land/rock interior. This produces a finite sampling gap at some shorelines, up to a local cell; it is an explicit C approximation requiring visual review, not a claim of exact shore contact. The step is roughly0.035–0.15m in the closest upper reach,0.06m in the near pool, with ordered lateral spacing at most0.09m; farther sampling is coarser.

## Contact by actual use

The reporting cutoff remains0.5mm. These are actual vertex/centroid/edge samples, not an exhaustive analytic triangle-solid certificate.

| Role | Samples | Actual result |
|---|---:|---|
| Falling body vertices |44,620|No terrain or rock interior over0.5mm|
| Falling-body triangle centers |88,320|**5 real rock-lip counterexamples remain, max1.025mm**; all have odd parity in3 independent rays|
| Near free-water triangle centers |229,597|No terrain or rock interior over0.5mm|
| Actual upper shoreline edge midpoints |2,783|No terrain or rock interior over0.5mm|
| Side closure triangle centers |5,380|3 terrain /70 rock interior samples; max terrain17.02mm, rock40.00mm. These are separated from the top seam; normal-view visibility/transmission still needs inspection|
| Deep C bottom-closure centers, every third |76,680|5,052 terrain /850 rock interior samples; max112.04mm/107.66mm. These are **optical closure approximations**, not CFD bed interfaces|

The five remaining falling-body points near `(2.88,-3.88,-3.056)` are retained as a real local contact FAIL. They are not relabeled as deep bottom caps and are not made acceptable by changing a threshold. The original mixed-role11.2cm/8.1cm failure records remain intact; their scope was mixed and must not be attributed wholesale to the visible water surface.

## Preserved attempts and actual cost

- Surface01:54 open/nonmanifold join edges and264 confirmed crossings.
- Surface02:closed, zero confirmed crossings, but wrong handling of open terrain and tiny shore triangles.
- Surface03/04:improved true terrain/solid classification; retained numerical shore counterexamples.
- Surface05/05b:conservative shoreline;05b separates19 touching edges, with every triangle coordinate and winding bitwise unchanged.
- Surface06a:one exact core difference on the **new valid**05b body, hard stopped at180seconds; no output. Observed working set41,214,496,768bytes. No further Boolean chain ran.
- Surface07:actual build+geometry audit {r['elapsed_s']:.3f}seconds, CPU4. It preserves old failures and is independently saved. No rendering was performed by this agent.

## Next bounded direction selected by root

Keep this closed base and make **one** visual hybrid candidate, at frame48: varying shallow sheets/fans plus small water droplets, broken whitewater and impact treatment, guided by actual source photos. Do not infer a larger water supply from those effects. Root will render it. Long simulation, production installation and a final5–10second motion PASS remain unauthorized/unachieved at this point.
'''
(ROOT/'qa/water12-surface-review.md').write_text(text,encoding='utf8')
print('STATIC_HANDOFF_WRITTEN',r['output_sha256'])
print('LARGEST_COMPONENTS',a['largest_component_bounds'][:6])
print('SOURCE_PHOTO_CANDIDATES')
for base in (ROOT,ROOT.parent/'research'):
    for p in base.rglob('*'):
        if p.suffix.lower() in ('.jpg','.jpeg','.png') and not any(x in p.parts for x in ('renders','caches','node_modules')):
            if any(x in str(p).lower() for x in ('reference','source','photo','fallingwater','habs')):print(p)
