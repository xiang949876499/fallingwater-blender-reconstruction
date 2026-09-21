from pathlib import Path
import json,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];Q=R/'qa';read=lambda n:json.loads((Q/n).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
b=read('guest-bays12-build-check.json');r=read('guest-bays12-reopen.json');old=read('guest-bays11-finish-source-probe.json')
assert r['all_finished_samples_pass_20mm'] and r['all_joints_occupied'] and r['source_reproduction_every_object_fingerprint_equal']
assert sha(b['candidate'])==b['candidate_sha256'] and sha(R/'scripts/guest_bays12.py')==b['helper_sha256']
before=[x for x in old['samples'] if x['station_m']==0 and 'visible_span_m' in x];after=[x for x in b['actual_complete_surface_samples'] if x['station_m']==0]
fig,ax=plt.subplots(figsize=(8,6),layout='constrained')
ax.axvspan(2.466025,2.506025,color='#e6efec',label='Printed completed-face span +/-20mm')
ax.axvline(2.486025,color='#2d4857',ls='--',lw=1.4,label='Printed 2.486025 m')
ax.plot([x['visible_span_m'] for x in before],[x['z']-8.4 for x in before],lw=1.2,color='#ac6550',label='11b actual exposed surface (retained FAIL)')
ax.plot([x['completed_face_span_m'] for x in after],[x['z']-8.4 for x in after],lw=1.4,color='#267d74',label='12a actual exposed backing + rough stone')
ax.set(xlabel='Measured completed-face north bay width (m)',ylabel='Height above floor (m)',title='North bay12a: rough layering retained within the finished-face bound')
ax.grid(alpha=.15);ax.legend(loc='lower left',fontsize=8);fig.savefig(Q/'guest-bays12-finished-profile.png',dpi=160);fig.savefig(Q/'guest-bays12-finished-profile.svg');plt.close(fig)
limit=max(abs(b['completed_surface_min_m']-2.486025),abs(b['completed_surface_max_m']-2.486025))
freeze={'status':'FROZEN_PASS_LOCAL_NORTH_FINISHED_FACE_GEOMETRY_PENDING_INDEPENDENT_VISUAL_REVIEW','source11b_sha256':b['source11b_sha256'],'candidate':b['candidate'],'candidate_sha256':b['candidate_sha256'],'candidate_bytes':b['candidate_bytes'],'helper_sha256':b['helper_sha256'],'integration_call':'guest_bays12.apply(scene) once AFTER guest_bays11.apply(scene, resolve_seats=True); on11b only call12','changed_objects':b['changed_objects'],'all_other_object_fingerprints_identical':True,'all_object_matrices_centers_camera_values_identical':True,'course_blocks_changed':b['course_blocks_changed'],'unselected_course_vertices_unchanged':b['unselected_course_vertices_unchanged'],'nominal_finished_span_m':2.486025,'finished_span_min_m':b['completed_surface_min_m'],'finished_span_max_m':b['completed_surface_max_m'],'max_absolute_finished_error_m':limit,'tolerance_m':.02,'actual_finished_samples_initial':b['complete_surface_sample_count'],'actual_finished_samples_independent_saved_reopen':r['actual_finished_surface_count'],'finished_sample_failures':0,'backing_included_in_completed_surface_probes':True,'actual_joint_union_occupied_samples':r['joint_occupied_union_count'],'actual_joint_union_failures':0,'source_reproduction_all_saved_objects_equal':True,'floor_support_pass_count':len(b['floor_support']),'new_north_door_pass_count':len(b['north_door_checks']),'normal_camera_proposals_pass_count':len(b['camera_proposals']),'numeric_route_and_entry_sample_pass_count':len(b['accepted10_numeric_route_samples']),'numeric_body_sweep_failure_count':0,'mesh_closed_positive_volume':True,'scene_settings_unchanged':True,'protected_source_files_unchanged':b['protected_files_unchanged'],'rendered':False,'limits':['C relief amplitude +/-8mm and8mm backing allocation; not archival individual stones.','Independent source-dimension/visual acceptance is separate; no claim all20 GEO02 anchors pass.','Middle nonparallel AB dimension remains NOT_PASS and unchanged.','No saved7584 animation claim: accepted10 numeric local routes only, original camera matrices unchanged.'],'evidence':['guest-bays12-source-plan.md','guest-bays12-build-check.json','guest-bays12-reopen.json','guest-bays12-finished-profile.png']}
(Q/'guest-bays12-freeze.json').write_text(json.dumps(freeze,indent=2),encoding='utf-8')
doc=f'''# Guest north bay12a handoff

Saved independent candidate: `scene/Fallingwater_guest_bays_candidate12a.blend`
SHA256 **{b['candidate_sha256']}**; **{b['candidate_bytes']:,} bytes**.
Helper: `scripts/guest_bays12.py`, SHA256 **{b['helper_sha256']}**.
Call `guest_bays12.apply(scene)` once after11b-equivalent geometry; on a fresh
base call `guest_bays11.apply(scene, resolve_seats=True)` then12. All other
helpers/production data and original11b are unchanged. Source reproduction from
11b matched every saved12a object fingerprint.

The actual completed masonry span is **{b['completed_surface_min_m']:.6f}–
{b['completed_surface_max_m']:.6f} m** against printed **2.486025 m**. All **2,556**
samples pass20 mm; maximum absolute error **{limit*1000:.3f} mm**. An independent
fresh process reopened the saved scene before applying anything and repeated
all2,556 actual completed-surface values with zero failures and less than1µm
difference from the initial measurement. Probes include exposed recessed backing
at mortar gaps **and** rough stone faces; there is no hidden-core substitution or
mean-only acceptance. The old558 locations fall within the expanded grid.

## Exact physical change

Six existing objects only: north `DIAGONAL_BACK_pier_0`, pier2 north backing,
the batched courses, and three existing north joint pieces (window base/header/
end return). Both complete masonry panels keep their architectural datum,
centers, far faces and ends. Backing faces recess8 mm. Twenty-six north-wall and
66 pier2 course blocks retain every layer elevation, length, stagger and depth
ordering; their unverified former7–37 mm all-positive decoration becomes
−8…+8 mm around the finished datum. Relief is16 mm, not flat. Their thicknesses
are6.4–22.4 mm and overlap the backing by6.4 mm. This is C mesh allocation inside
a solid masonry wall, not a historical thin-veneer claim.

The window-base/header/end-return tails extend16 mm into the backing at their
real structural junctions. No door/window frame moves. The overlap is8 mm,
greater than the existing7 mm bevel. These tails close construction joints;
they are not measuring patches. Independent occupied-union tests at1 mm axial
spacing and seven heights verify **574 actual junction points** are inside or
in contact with the relevant closed components, without relying on an unrelated
distant ray hit.

All object matrices, all cameras, every other mesh/furniture/material, original
room and route data, other openings, stairs/connector and the11b chairs'0.90 m
translation remain identical. **75,504 non-target stone vertices** are unchanged.
All six modified meshes remain closed and positive-volume. No objects were
added or removed, and no scene/render setting changed.

## Support and movement

The actual slab still supports42 wall-side positions. The21 north-door standing
checks pass4 mm support,0.18 m radius and1.95 m head/body height. Both new normal
photographic locations and their approaches pass on12a without moving a camera.
The accepted10 Theater film path plus ADJ_040 entry retain154 passing numeric
samples and all body sweeps. This local numeric route check is not a7,584 saved
animation audit or full graph acceptance. The original A/B values and their
previous failures were not relabeled.

For root previews, the unchanged proposed24 mm /36 mm sensor /16:9 views are:

| View | Eye XYZ | Target XYZ |
|---|---|---|
| North bay | (0.6,51.8,10.0) | (−2.866858,51.681335,9.48) |
| Middle bay | (0.4,49.9,10.0) | (−2.412213,48.720924,9.48) |

## Qualification and retained evidence

The printed finished-face boundary is the dimensional control. Individual
stone shape/amplitude and backing depth remain **C construction choices**, and
visual naturalness must be judged in root's actual preview. No render occurred
here. North's completed-surface numerical check is now eligible for independent
GEO02 review; this report does not declare all20 anchors or photo realism passed.
The middle nonparallel AB span remains NOT_PASS and unchanged.

Preserved originals:11b scene, its554/558-style prior finished-face reports and
negative ranges, earlier core-only/finite-AB qualifications, and all old camera
failures. Read `guest-bays12-build-check.json`, `guest-bays12-reopen.json` and
`guest-bays12-freeze.json` for exact values and whitelist. The comparison chart
`guest-bays12-finished-profile.png` keeps11b's actual surface failure visible.
The scoped source plan and this handoff reconcile current behavior; root-owned
STATUS/AGENTS, central dimension CSV and other agents' documentation were not edited.
'''
doc=doc.replace('554/558-style prior','558-sample prior')
doc+='\nThe first containment-check log is retained as `guest-bays12-reopen-attempt01.log`. It incorrectly used an overlapping core+course BVH as one Boolean solid; an internal stone-entry face was mistaken for outside volume. The final check tests closed components independently, preserving union membership. No geometry or tolerance was changed to resolve that test-method error.\n'
(Q/'guest-bays12-handoff.md').write_text(doc,encoding='utf-8')
print(json.dumps({k:freeze[k] for k in ['status','candidate_sha256','helper_sha256','finished_span_min_m','finished_span_max_m','max_absolute_finished_error_m']}))
