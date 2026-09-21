from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];Q=R/'qa'
def read(n):return json.loads((Q/n).read_text(encoding='utf-8'))
a=read('guest-bays11-build-check.json');b=read('guest-bays11-reopen-and-seat-check.json');r=read('guest-bays11-route-reopen.json');j=read('guest-bays11-joint-interpret.json');f=read('guest-bays11-finished-face-probe.json')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert r['helper_sha256']==sha(R/'scripts/guest_bays11.py')
assert b['scene11b_sha256']==sha(b['scene11b']) and a['candidate_sha256']==sha(a['candidate_scene'])
assert r['source_reproduction_all_object_fingerprints_identical'] and not r['new_point_failures'] and not r['new_sweep_intersections']
freeze={'status':'FROZEN_LOCAL_GEOMETRY11B_NOT_PHOTOREAL_OR_FULL_SCENE_ACCEPTANCE','source10a_sha256':a['source_scene_sha256'],'candidate11a_sha256':a['candidate_sha256'],'candidate11a_bytes':a['candidate_bytes'],'candidate11b_sha256':b['scene11b_sha256'],'candidate11b_bytes':b['scene11b_bytes'],'helper_sha256':r['helper_sha256'],'integration_call':'guest_bays11.apply(scene) defaults resolve_seats=True for accepted 11b; resolve_seats=False reconstructs archived 11a geometry','changed_existing_objects':a['changed']+b['target_object_changes'],'removed_existing_objects':a['removed'],'added_objects':a['created'],'preserved_unselected_course_vertices':a['protection']['unselected_course_vertices'],'changed_course_blocks':sum(map(len,a['course_block_ids'].values())),'all_non_target_fingerprints_unchanged':True,'all_saved11b_objects_reproduced_from10a_and_current_helper':True,'floor_polygon_changed':False,'window_door_heights_materials_evidence':'C/U; dimensions do not establish vertical identity','north_nominal_core_actual_m':a['measurements'][0]['actual_evaluated_mesh_m'],'north_rough_visible_clearance_m':[x['span_m'] for x in f['visible_surface_samples']],'north_dimension_final_qualification':'INDEPENDENT_REVIEW_PENDING; core vs projecting C rough surface distinguished','middle_dimension_final_qualification':'NOT_PASS_C_DIAGNOSTIC_NONPARALLEL_AB_AND_PIER_FACES; old missing finite endpoint preserved','middle_face_angle_deg':b['middle_finite_face_station_diagnostics'][0]['normal_parallelism_angle_degrees'],'seat_translation_m':b['seat_translation_m'],'seat_foot_contacts_pass':8,'new_north_door_strict_samples_pass':21,'floor_actual_slab_support_pass':42,'wall_joint_total':len(b['wall_joint_rays']),'wall_joint_direct_hits':sum(x['closed'] for x in b['wall_joint_rays']),'wall_joint_finite_misses_proven_inside_pier':j['original_finite_ray_misses_preserved'],'film_numeric_integer_samples':r['film_integer_samples'],'adjacency040_numeric_samples':r['adjacency_samples'],'local_before_and_after_point_failures':0,'local_before_and_after_sweep_intersections':0,'saved_120_camera_pose_values_unchanged':True,'old_camera_geometry_failures_preserved':['CAM_GUEST_L1_THEATER_A: east body radius intersects pre-existing stone course','CAM_GUEST_L1_THEATER_B: west lateral foot support outside old floor'],'animated_cameras_in_input':0,'scope_limits':['No saved 7584 animation assertion: source10a has no animation actions; accepted10 numeric route checked independently.','No third lower bay rewrite, no source stair/connector/true southeast entry changes.','No production guest_house/data/furnishings/navigation/cameras/scene originals changed.','No render or new historical photo proof; exact seat layout is generic C.'],'evidence':[n for n in ['guest-bays11-source-review.md','guest-bays11-source-endpoints-final.png','guest-bays11-build-check.json','guest-bays11-reopen-and-seat-check.json','guest-bays11-route-reopen.json','guest-bays11-joint-interpret.json','guest-bays11-finished-face-probe.json']]}
(Q/'guest-bays11-freeze.json').write_text(json.dumps(freeze,indent=2),encoding='utf-8')
endpoint=read('guest-bays11-source-endpoints-final.json');endpoint.update(view_status='ACTUALLY_OPENED_FINAL_CORRECTED_ANNOTATION',middle_prediction_qualification='2.158240m is extended-plane-only prediction; finite prior locator misses AB; green finite-face station is C diagnostic because faces differ 7.3805 degrees')
(Q/'guest-bays11-source-endpoints-final.json').write_text(json.dumps(endpoint,indent=2),encoding='utf-8')
md=f'''# Guest bays11b handoff — 2026-09-21

Frozen independent local candidate: `scene/Fallingwater_guest_bays_candidate11b.blend`.
SHA256 **{b['scene11b_sha256']}**, {b['scene11b_bytes']:,} bytes.
Helper `scripts/guest_bays11.py` SHA256 **{r['helper_sha256']}**.
Call `guest_bays11.apply(scene)` once on full10a-equivalent physical geometry;
the default includes the two C-seat translations. `resolve_seats=False` creates
11a without that furniture correction. Do not reapply to an already modified
scene. Fresh source application reproduced every saved11b object fingerprint.

## Source and physical scope

The actual original Guest01 2010 HABS drawing and final endpoint annotation
were opened. This is the enclosed THEATER configuration, not the earlier open
carport. North inner stone face and printed 8′1⅞″ locate the full diagonal
architectural bay. The entire north wall moves 131.6 mm to that source face;
the NE first pier alone extends back to keep its existing window endpoint.
The two retained piers, associated stone blocks, and upper two wrong straight
WEST enclosure groups are corrected to the source staggered axes. A real
window/door and short return replace them. The lower third bay stays outside
this bounded accuracy claim. No local measuring-only patch was introduced.

The explicit whitelist is in `guest-bays11-freeze.json`: 26 architectural
objects changed, 22 obsolete enclosure objects removed, 32 new closed objects.
514 disjoint stone blocks move with their own walls; 72,128 other course vertices
are byte-identical. All 57 new/changed core meshes have closed manifold topology
and positive signed volume. The physical floor polygon is unchanged: the actual
existing slab supports all 42 sampled wall-side positions.

In 11a, source corrections exposed actual intersections with generic seat08/09.
`room_theater()` explicitly marks exact current seats/projector unverified C and
uses an algorithmic row arrangement. Root authorized only these two whole roots
to move inward. 11b translates both by (+0.777115, +0.453973, 0) m, preserving
number, yaw, mesh, materials and height. At 0.85 m along that axis one real
triangle intersection remained; at 0.90 m all disappear. Eight leg bottoms touch
the real slab within 4 mm. The 11a collision scene and logs are retained.

## Dimensions: do not turn diagnostic agreement into PASS

North nominal evaluated core faces: **2.486024857 m**, matching the printed
2.486025 m constraint. This is a core-face geometric result, not a claim that
projecting C rough stone courses have identical visible clearance. Actual
visible/core-combined surface measurements at five heights are separately
recorded in `guest-bays11-finished-face-probe.json`. Final dimension qualification
remains with the independent dimension reviewer.

Middle lower endpoint is the finite short unhatched AB jamb/return, not pier1's
long stone face. Source identity is B/C; material and full-height continuation
are C/U. The old C locator misses the finite AB edge by about 12 mm. The earlier
2.158240 m is an **extended-plane prediction only**, retained as such. Parallel
stations at 15%, 50%, 85% along actual AB hit spans **2.163070 / 2.171228 /
2.179389 m**. Opposing normals differ **7.3805°**, so the middle printed dimension
**does not PASS**; shifting station changes the span. AB was not moved to force
the printed number. The old NOT_RUN and missing endpoint remain available.

## Reopen, joints and circulation

All 72 wall-joint rays are accounted for: 66 directly hit enclosure. Six short
rays began and ended inside the solid retained pier and therefore hit no surface;
independent vertical and longer transverse actual mesh rays prove occupied,
closed pier volume at those stations. They are not holes.

The new north door has 21 strict standing samples with 0.18 m radius, 1.95 m
head height and 4 mm support tolerance; all pass before/after seat translation.
The accepted10 numeric Theater film route (96 integer samples) and true ENTRY
ADJ_040 (58 samples plus body sweeps) both have **zero failures before and after**.
Route source hash and coordinate values are archived in `guest-bays11-route-reopen.json`.
No route keys or production data were applied or saved.

The physical10a input contains **no animated camera actions**. Consequently this
is not a 7,584 saved-frame audit or full graph acceptance. All original camera
values are unchanged. The old Theater A east body/course collision and Theater B
west lateral foot-support failure also remain unchanged; they require the
integrator's existing camera adaptation, not geometry edits to hide them.

## Evidence and integration limits

Primary records: `guest-bays11-source-review.md`, `guest-bays11-source-endpoints-final.png`,
`guest-bays11-build-check.json`, `guest-bays11-reopen-and-seat-check.json`,
`guest-bays11-route-reopen.json`, `guest-bays11-joint-interpret.json`,
`guest-bays11-finished-face-probe.json`, and `guest-bays11-freeze.json`.
The intermediate endpoint image with plane-only prediction is archived and the
final annotation explicitly corrects its interpretation. Attempt01 foot-check
log is preserved: its ray started below the coincident contact plane; corrected
slab-only probes from above verify actual contact without moving geometry.

No rendering occurred. Source-photo shape/material acceptance and final combined
navigation remain separate integration work. Production source/data, all stairs,
connector, true southeast entrance, lighting, camera poses and every other
furniture group are protected. The original10a and both11a/11b scenes remain.

Documentation cleanup followed the neat-freak workflow within assigned ownership:
source identity text was revised rather than appended with contradictory status,
the helper's default11b behavior is documented here, and old negative evidence is
explicitly linked. Root-owned STATUS/AGENTS and central dimension CSV were not changed.
'''
(Q/'guest-bays11-handoff.md').write_text(md,encoding='utf-8')
print(json.dumps({'helper_sha256':freeze['helper_sha256'],'candidate11b_sha256':freeze['candidate11b_sha256'],'status':freeze['status']}))
