"""Write a compact handoff only after build, reopen and framing evidence exists."""
from pathlib import Path
import hashlib,json
Q=Path(__file__).resolve().parent;R=Q.parent
build=json.loads((Q/'masonry12b-build-check.json').read_text())
read=json.loads((Q/'masonry12b-readback.json').read_text())
camera=json.loads((Q/'masonry12b-camera-probe.json').read_text())
assert build['status']=='PASS_PHYSICAL_CANDIDATE_NOT_VISUALLY_ACCEPTED'
assert read['status']=='PASS_FRESH_PROCESS_EXACT_REOPEN'
assert read['candidate_sha256']==build['candidate_sha256']==camera['candidate_sha256']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(Path(build['candidate']))==build['candidate_sha256']
assert sha(Path(build['source']))==build['source_sha256']
app=build['application'];contacts=[x['signed_gap_m'] for c in build['component_checks'] for x in c['actual_back_contacts']]
summary={
 'status':'PASS_BOUNDED_HEIGHT_GEOMETRY; NOT_VISUALLY_REVIEWED; LEGACY_CAP_AND_OUTLETS_UNRESOLVED',
 'candidate':build['candidate'],'candidate_sha256':build['candidate_sha256'],
 'helper':'scripts/masonry_tower12b.py','helper_sha256':build['helper_sha256'],
 'source_12a_sha256':build['source_sha256'],'non_target_objects_unchanged':build['non_target_objects_unchanged'],
 'protected_physics_count':len(build['protected_physics']),
 'new_closed_stones':app['component_count'],'new_triangles':app['triangles'],
 'retained_12a_closed_stones':501,'retained_12a_triangles':20622,
 'combined_stones':501+app['component_count'],'combined_triangles':20622+app['triangles'],
 'core_cap_outlet_five_closed_checks':read['five_modified_evaluated_meshes_closed'],
 'actual_height':build['actual_nominal_anchor'],
 'root_camera_count':len(build['all_131_cameras']),
 'minimum_saved_camera_clearance_m':min(c['nearest_new_finish_m'] for c in build['all_131_cameras']),
 'movie_position_count':sum(m['samples'] for m in build['movie_positions']),
 'minimum_movie_position_clearance_m':min(m['minimum_clearance_m'] for m in build['movie_positions']),
 'route_rays':build['current_route_regression']['ray_count'],'new_route_obstacles':len(build['current_route_regression']['new_obstacles']),
 'back_contact_signed_gap_range_m':[min(contacts),max(contacts)],
 'minimum_new_stone_triangle_area_m2':min(c['min_area_m2'] for c in build['component_checks']),
 'new_nonadjacent_self_or_cross_component_intersections':read['nonadjacent_self_or_cross_component_intersections'],
 'new_high_volume_neighbor_intersections':build['extended_volume_intersections'],
 'neighbor_intersections':build['neighbor_intersections'],
 'source_and_candidate_guards_unchanged_after_read':True,
 'external_camera_settings_sha256':sha(Q/'masonry12b-camera-settings.json'),
 'framing':camera,'rendered':False,'production_integrated':False,
 'known_limits':[app['cap_status'],app['outlet_status'],'Whole environment still fails photoreal acceptance; height nominal agreement does not certify actual survey precision.'],
}
(Q/'masonry12b-final-audit.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
cfg=camera['settings']
text=f'''# Tower12b height completion handoff

2026-09-21 · /root/site_visual · **Local height/mesh checks PASS; NOT_RENDERED; legacy cap/outlet form NOT_ACCEPTED.**

Candidate: `scene/Fallingwater_masonry_tower_candidate12b.blend`  
SHA256: `{summary['candidate_sha256']}`  
Helper: `scripts/masonry_tower12b.py`  
SHA256: `{summary['helper_sha256']}`

The source12a is unchanged at `{build['source_sha256']}`. Source iteration10 remains1e7b17d9…. Production scripts, original12a helper, central dimensions table, shared materials, working model and saved camera settings were not modified.

## Height evidence and explicit datum

`tower-height12-source-review.md` resolves the HABS32′9½″ witness to the continuous masonry/coping upper outline, excluding raised outlets. Nominal9.9949m is A; source-to-model component correspondence is C. The drawing names MAIN LEVEL TERRACE0′0″. This candidate explicitly maps it to the **actual visible terrace finish** (worldZ{build['actual_nominal_anchor']['lower']:.12f}), consistent with the existingMAIN_LEVEL_2 finish comparison. ExistingMAIN_LEVEL_3/ROOF rows use structural zero; that22mm mixed convention remains disclosed and was not silently rewritten.

New continuous cap top worldZ{build['actual_nominal_anchor']['upper']:.12f}; actual relative height **{build['actual_nominal_anchor']['relative']:.12f}m**; numerical nominal error{build['actual_nominal_anchor']['error_m']:.9g}m. This is a floating-point fit to a printed target, **not actual-site survey precision**. Exact sheet survey date and survey accuracy remainUNKNOWN; museum collection context is circa2010.

## Bounded change

- Exactly five old object data blocks change: `MAIN_stone_tower_west`, `MAIN_stone_tower_north`, `MAIN_chimney_cap`, `MAIN_chimney_flue`, `MAIN_chimney_flue.001`.
- Each structural body changes only its four native old-top vertices, raising them by{app['correction_m']:.12f}m. All other native vertices, XY coordinates, object matrices, material slots and existing Crafted edges Bevel settings remain unchanged. No whole-object Z scaling, lower floor shift or window-interface movement.
- Cap and two old outlet meshes translate by the same delta. Plan extents/thicknesses and relative offsets remain their previous C geometry.
- Three new `MASONRY12b_TopCompletion_*` meshes add6courses, **{app['component_count']}closed stones / {app['triangles']}triangles** within the existing35.5mm finish projection allowance. New top/bottom chips are0–4mm C, with small bounded mid-face facets. No rounded displacement or new shared material.
- The501closed stones /20622triangles of12a remain exact. Combined finish is{summary['combined_stones']}stones /{summary['combined_triangles']}triangles. New geometry uses the already-private12a stone material unchanged.

## Verification

- {summary['non_target_objects_unchanged']} non-target objects exactly unchanged;{summary['protected_physics_count']} physical hashes preserved, including core/water/bridge/paths/terrain and all three lower12a finish batches. All original globals/material nodes/image settings/lights/actions and all other mesh users unchanged.
- All70 new stone components and all five modified evaluated core/cap/outlet meshes are closed, oriented, positive-volume and nondegenerate. New nonadjacent self/cross-component intersections:0. Actual neighboring building intersections:0. Extended high-volume intersections with all candidate-neighbor meshes (including broad vegetation/terrain meshes):0.
- Minimum new triangle area{summary['minimum_new_stone_triangle_area_m2']:.9g}m². Back contacts against actual substrate have signed gaps{min(contacts):.9g}to{max(contacts):.9g}m (intentional hidden .8mm embed).
- All131saved camera positions: minimum local tower clearance{summary['minimum_saved_camera_clearance_m']:.6f}m. All7584current movie positions: minimum{summary['minimum_movie_position_clearance_m']:.6f}m. Current12264route rays:0newobstacles. This does not replace the parent’s complete navigation or GUI review.
- Fresh process reopened exact candidate fingerprint and checked repeated application is a verified no-op. No image rendering or GPU use.

`masonry12b-build-check.json`, `masonry12b-readback.json`, and `masonry12b-final-audit.json` carry detailed results. The failed unsavedattempt01 (too-narrow modifier prerequisite) andattempt02 (derived dimensions.z not yet explicitly whitelisted) are retained. Independent probes identified the exact savedBevel and dimension-only change; final checks permit only that known modifier and exact delta, not arbitrary object changes. No failed scene was saved.

## Explicit remaining cap/outlet failure

**The tower is not a finished photoreal or historically complete chimney.** Original cap plan is a broad single slab; source continuous coping row appears closer to the wall line. The two old objects namedflue are only30mm-thick dark boxes, have a10mm gap above the cap, and do not establish the source outlet count/shape. The second oldflue lies outside the west-core footprint and is carried only by the existing overhanging cap. These problems are preserved, documented, and not accepted by this height correction.

No new guessed vent bank, platform, support columns or unknown roof penetrations were added. A reliable complete outlet correction needs a roof plan or identifiable overhead view that locates individual outlets; the west silhouette alone does not locate their XY positions. Do not count the highest outlet as the nominal tower top.

## Parent render and entry

Use savedCAM_HERO atframe48. For a detail comparison, `masonry12b-camera-settings.json` keeps the same eye/target/exposure and uses lens{cfg['lens']:.1f}mm. The original36mm framing {'clips the corrected tower top' if camera['external_lens_changed_to_keep_corrected_top_in_frame'] else 'still contains the corrected tower top'}; both original and proposed measured screen bounds are in `masonry12b-camera-probe.json`. Apply the identical external setting to12a and12b; do not compare mismatched lenses. No saved camera was changed.

`masonry_tower12b.build(ctx)` expects the exact completed12a geometry and its private material. For a later fresh integration the order is12a first, then12b; do not call12a’s original guard check again after12b has intentionally changed its five protected tops. The12b entry verifies its own stored geometry on repeat and rejects partial/changed states. This remains a candidate entry, not a production enablement request.

neat-freak closeout is confined to ownedQA: dimensional evidence, controlled failure history, candidate/hash/interface facts and NOT_RUN/known-failure states are consolidated here. RootAGENTS, STATUS and central manifests remain unchanged.
'''
(Q/'masonry12b-handoff.md').write_text(text,encoding='utf-8')
print(json.dumps({k:summary[k] for k in ('status','candidate_sha256','helper_sha256','non_target_objects_unchanged','protected_physics_count','actual_height','minimum_saved_camera_clearance_m','minimum_movie_position_clearance_m','framing')},indent=2))
