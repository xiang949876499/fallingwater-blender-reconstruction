import json,hashlib
from pathlib import Path
R=Path('D:/zx/test/project');Q=R/'qa'
a=json.loads((Q/'guest-circulation10-final-audit.json').read_text(encoding='utf-8'))
r=json.loads((Q/'guest-circulation10-reopen-check.json').read_text(encoding='utf-8'))
f=json.loads((Q/'guest-circulation10-freeze.json').read_text(encoding='utf-8'))
assert a['candidate_sha256']==f['sha256'] and a['independent_reopen_counts']['FAIL']==0
assert not a['finish_failures'] and not a['solid_mesh_failures']
assert hashlib.sha256((R/'scripts/guest_circulation10.py').read_bytes()).hexdigest()==r['implementation_sha256'], 'Frozen physical report: do not relabel a migrated implementation; use the navigation runtime-migration handoff'
assert a['implementation_matches_loaded_candidate']
f['status']='LOCAL_PHYSICAL_CHECKS_PASS_C_HYPOTHESIS_NOT_INSTALLED'
f['local_counts']=a['independent_reopen_counts'];f['local_samples']=a['actual_local_sample_count']
f['source_limitations']=['Four-flight levels/counts remain C','Source divider is a real solid; its traced outline, finish and L2+1.0m top remain C','No full60edge/7584frame rerun or visual acceptance']
(Q/'guest-circulation10-freeze.json').write_text(json.dumps(f,indent=2),encoding='utf-8')
overlay_path=Q/'guest-circulation10-candidate-adjacency.json'
overlay=json.loads(overlay_path.read_text(encoding='utf-8'))
local_edge_checks={
    frozenset(('GUEST_L1_STAIR_HALL','GUEST_L1_CHAUFFEUR_LOUNGE')):['CHAUFFEUR_NORTH_DOOR'],
    frozenset(('GUEST_L1_STAIR_HALL','GUEST_L1_TERRACE')):['F2_LOWER_RIGHT_NORTH','F2_LOWER_RIGHT_NORTH_JOINTS','LOWER_RETURN','FRONT_LOW_TO_W1','W1_FRONT_WEST','W1_FRONT_WEST_JOINTS','FRONT_MIDDLE','W2_FRONT_EAST','W2_FRONT_EAST_JOINTS','FRONT_EAST'],
    frozenset(('GUEST_L1_TERRACE','GUEST_L1_LOUNGE')):['REAL_SOUTHEAST_LOUNGE_ENTRY'],
    frozenset(('GUEST_L1_LOUNGE','GUEST_L1_GALLERY')):['GALLERY_TO_LOUNGE'],
    frozenset(('GUEST_L1_GALLERY','GUEST_L1_GUEST_ROOM')):['GUEST_TO_GALLERY'],
    frozenset(('GUEST_L1_GUEST_ROOM','GUEST_L1_TERRACE')):['GUEST_EAST_DOOR'],
    frozenset(('GUEST_L1_STAIR_HALL','GUEST_B1_STAIR')):['F1_B1_LEFT_SOUTH','F1_B1_LEFT_SOUTH_JOINTS','LOWER_RETURN','F2_LOWER_RIGHT_NORTH','F2_LOWER_RIGHT_NORTH_JOINTS','NORTH_L1_CROSSOVER'],
    frozenset(('GUEST_B1_STAIR','GUEST_B1_LAUNDRY')):['B1_DOOR_APPROACH'],
    frozenset(('GUEST_L1_STAIR_HALL','GUEST_L2_HALL')):['F3_UPPER_LEFT_SOUTH','F3_UPPER_LEFT_SOUTH_JOINTS','UPPER_RETURN','F4_UPPER_RIGHT_NORTH','F4_UPPER_RIGHT_NORTH_JOINTS','NORTH_L2_APPROACH'],
}
by_id={c['id']:c for c in r['checks']}
for edge in overlay['adjacency']:
    ids=local_edge_checks.get(frozenset((edge['from'],edge['to'])),[])
    assert all(by_id[c]['status']=='PASS' for c in ids)
    edge['candidate_validation']='PASS_LOCAL_PHYSICAL_GROUPS' if ids else 'NOT_RUN_OUTSIDE_LOCAL_SCOPE'
    edge['actual_check_ids']=ids
overlay['validated_candidate_sha256']=f['sha256']
overlay['scope']='Guest edge overlay only: local group evidence is named; no full 60-edge or camera-frame claim.'
overlay_path.write_text(json.dumps(overlay,indent=2),encoding='utf-8')
table=[]
names=['F1_B1_LEFT_SOUTH','F2_LOWER_RIGHT_NORTH','F3_UPPER_LEFT_SOUTH','F4_UPPER_RIGHT_NORTH','W1_FRONT_WEST','W2_FRONT_EAST']
for name in names:
    c=next(c for c in r['checks'] if c['id']==name)
    table.append('| '+name+' | '+str(c['samples'])+' | '+format(c['lowest_overhead']['clearance'],'.6f')+'m | PASS |')
text=f'''# Guest circulation10 independent candidate handoff

Current artifact: `scene/{Path(f['candidate']).name}`.

- Candidate SHA256: `{f['sha256']}`.
- Immutable full09 source SHA256: `{f['source_sha256']}`.
- Adapter: `scripts/guest_circulation10.py`; SHA256 `{hashlib.sha256((R/'scripts/guest_circulation10.py').read_bytes()).hexdigest()}`.
- Independent reopen: **{a['independent_reopen_counts']['PASS']} local groups / {a['actual_local_sample_count']} samples PASS; 0 FAIL; 0 NOT_RUN within this local scope**. This is not full navigation, source-authenticity or visual acceptance. The candidate is not installed in production.

## Result and scope

The candidate implements lower8+8 and upper8+5half flights, the two front3+4stair groups, south−1.18m, upper intermediate+1.4478m and the unchanged northern room/storey levels. Four-flight elevations/counts remainC. The actual main connector begins at its existing22mm finish5.28615m, rises through14uniform138.132mm risers, and joins the south arrival at7.22m. Its six same-height terminal pieces and the south platform form one15-point closed prism; no overlapping terminal top sheets remain.

The west Lounge false entrance is now glazing. Newly viewed MCAH2001 panorama faces and the native guest01 doorway/swing identify the true southeast entrance near sourcex457..476,y430, beside the fixed sidelights. The candidate preserves Terrace↔Lounge through that door and retracts only the old western route identity. Door details/open pose and window heights/grid remainC. See `guest-circulation10-panorama-review.md` and the separate candidate adjacency overlay.

The north return of the existing basement retaining wall is trimmed only beneath the northernL1paving, preserving its physical lower wall, long curved end, XY footprint and2ft5anchors. The last three canopy panels are closed at the service building's south facade footprint; their absolute heights are retained. The C soil trench is restricted to the actual low paving/connector footprint with0.10m construction margin and0.30m blended edge. Maximum lowering is0.928210m over4673changed vertices; changedXY bounds are[-4.41875,9.15]×[29.30,36.69375]m. Before/after terrain rays and every changed vertex are in the embedded candidate manifest. No sampled vegetation root needed reseating; no river, bank, core bedrock, furniture or production module was changed.

## Independent physical evidence

Ground rays start205mm above expected feet, so a higher overlapping slab cannot be missed; permitted ground error is4mm. Body radius is180mm and head clearance1.95m. Stair approach ankle allowance is200mm for legitimate risers; head/body limits are unchanged. Full-scene evaluated regional meshes include stone protrusions, rails, furniture, terrain, canopy and posts.

| Flight | Dense tread samples | Lowest measured overhead | Result |
|---|---:|---:|---|
{chr(10).join(table)}

Each flight's physical first/last contacts and every intervening riser have separate passing joint probes. Additional groups cover basement and chauffeur doors, lower/upper turns, north platforms, both front transitions, the real southeast entry, Gallery/Lounge access, the complete connector and its main/guest seams.

Independent 2ft5 audit: {a['finish_measurement_count']} stations on the actual common finished-wall height, measured {a['finish_width_min_max'][0]:.6f}–{a['finish_width_min_max'][1]:.6f} m versus 0.7366 m nominal; all within 20 mm. This is the sampled range, not a claim about unseen surfaces. All {len(a['solid_mesh_audit'])} distinct new/locally modified solids have zero boundary/nonmanifold edges. {r['unchanged_nonwhitelist_count']} nonwhitelisted source objects retain their geometry/matrix/material signatures. The adapter hash matches the loaded candidate; production guest/data/tour hashes remain unchanged.

## Source limits that remain explicit

The guest02 upper central divider is now a visible, closed solid at approximately source x304.5–308.4, y372.6–407.5. Its identity is plan-supported; the traced outline, finish and height remain C. The constant top is world 11.752675 m: 1.0 m above the highest adjacent L2 finish, 1.904875 m above the upper return, and nominally 1.12 m below the existing roof underside. It was not reduced to make a path pass. Both return routes now use source y412.3 and have been replayed against the actual divider, floors, ceiling, rails and furnishings. The wall-less 10e result remains historical and is not used as evidence for this wall.

South−1.18m is still an inferred finished plane within the sourcegrade interval; B1−2.36m remains the previousCdatum. The new interior panoramas do not show the western service flights and do not settle these exterior levels. The numeric source residuals and rejected nominal going lengths in `guest-circulation10-design.json` remain applicable. Full60declared-edge/7584integer-frame, all-room camera and visual checks were deliberately not claimed.

## Reproduction and preserved failures

On a newly loaded frozen09 scene, import the adapter and call `apply()`. It asserts the expected source target names, changes only an explicit whitelist, adds an embedded candidate manifest and does not save, render or write production data. `guest-circulation10-check.py` performs a fresh candidate build with4CPUthreads and a non-overwriting output guard. `guest-circulation10-final-audit.py` reopens the frozen candidate, repeats all29groups, measures the finished wall gap and checks closed solids. UseBlender5.2.1with `--python-exit-code1`. NoGPU/render/GUI operation was performed.

Preserved artifacts: first10scene/`firstFAIL-*` record real wall/canopy/terrain failures;10b/`second-*` are historical weaker-ground results;10c/`third-strict-ground-negative.*` demonstrate the24mm riser support overhang caught by the stronger ground method;10d/`10d-nonmanifold-negative.*` preserve the rejected Boolean landing and out-of-height dimension probes.10e changes that landing to one closed outline and uses only valid common wall heights; its `10e-without-upper-divider.*` and `10e-review.md` preserve the remaining source-wall omission.10f adds the source divider and restores the full southern turning band. These historical checks are not retroactively relabeled PASS.

Scoped neat-freak reconciliation: this handoff is the current local entry point; older numeric/negative artifacts remain identified as history under the explicit preservation requirement. AGENTS.md remains14lines and still correctly states the production boundaries; STATUS/START_HERE are root-owned and were not edited. No global settings or memory were changed.
'''
(Q/'guest-circulation10-review.md').write_text(text,encoding='utf-8')
print('HANDOFF_WRITTEN',f['status'])
