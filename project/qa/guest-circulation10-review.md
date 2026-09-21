# Guest circulation10 independent candidate handoff

Current artifact: `scene/Fallingwater_guest_circulation_candidate10f.blend`.

This is the frozen physical 10f report. Subsequent candidate navigation and
runtime packaging are documented in `guest-circulation10-navigation-handoff.md`.
The current physical helper only changes the design input path to
`data/guest_circulation10_design.json`; its SHA256 is
`97b5b69a6e6214efd491d7629e13c916cd12b4de90349a3950c4dbfc5250f345`.
The original code hash below belongs to the preserved
`guest-circulation10-navigation-runtime-before-guest_circulation10.py` source.
The migration report proves byte-identical design data and a single path-literal
change, with no physical value change. Historical test results remain unchanged.

- Candidate SHA256: `7286427d1f47ae9219204ed5dd54a970387683c8b384d1b4259244a7b991d852`.
- Immutable full09 source SHA256: `489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331`.
- Adapter: `scripts/guest_circulation10.py`; SHA256 `c2220aee3f283dd4c50178478b488e126a7f48043799cad545879abac6fcd28a`.
- Independent reopen: **29 local groups / 3503 samples PASS; 0 FAIL; 0 NOT_RUN within this local scope**. This is not full navigation, source-authenticity or visual acceptance. The candidate is not installed in production.

## Result and scope

The candidate implements lower8+8 and upper8+5half flights, the two front3+4stair groups, south−1.18m, upper intermediate+1.4478m and the unchanged northern room/storey levels. Four-flight elevations/counts remainC. The actual main connector begins at its existing22mm finish5.28615m, rises through14uniform138.132mm risers, and joins the south arrival at7.22m. Its six same-height terminal pieces and the south platform form one15-point closed prism; no overlapping terminal top sheets remain.

The west Lounge false entrance is now glazing. Newly viewed MCAH2001 panorama faces and the native guest01 doorway/swing identify the true southeast entrance near sourcex457..476,y430, beside the fixed sidelights. The candidate preserves Terrace↔Lounge through that door and retracts only the old western route identity. Door details/open pose and window heights/grid remainC. See `guest-circulation10-panorama-review.md` and the separate candidate adjacency overlay.

The north return of the existing basement retaining wall is trimmed only beneath the northernL1paving, preserving its physical lower wall, long curved end, XY footprint and2ft5anchors. The last three canopy panels are closed at the service building's south facade footprint; their absolute heights are retained. The C soil trench is restricted to the actual low paving/connector footprint with0.10m construction margin and0.30m blended edge. Maximum lowering is0.928210m over4673changed vertices; changedXY bounds are[-4.41875,9.15]×[29.30,36.69375]m. Before/after terrain rays and every changed vertex are in the embedded candidate manifest. No sampled vegetation root needed reseating; no river, bank, core bedrock, furniture or production module was changed.

## Independent physical evidence

Ground rays start205mm above expected feet, so a higher overlapping slab cannot be missed; permitted ground error is4mm. Body radius is180mm and head clearance1.95m. Stair approach ankle allowance is200mm for legitimate risers; head/body limits are unchanged. Full-scene evaluated regional meshes include stone protrusions, rails, furniture, terrain, canopy and posts.

| Flight | Dense tread samples | Lowest measured overhead | Result |
|---|---:|---:|---|
| F1_B1_LEFT_SOUTH | 84 | 2.002499m | PASS |
| F2_LOWER_RIGHT_NORTH | 119 | 2.290175m | PASS |
| F3_UPPER_LEFT_SOUTH | 84 | 1.961700m | PASS |
| F4_UPPER_RIGHT_NORTH | 56 | 2.300974m | PASS |
| W1_FRONT_WEST | 28 | 3.002856m | PASS |
| W2_FRONT_EAST | 45 | 2.328571m | PASS |

Each flight's physical first/last contacts and every intervening riser have separate passing joint probes. Additional groups cover basement and chauffeur doors, lower/upper turns, north platforms, both front transitions, the real southeast entry, Gallery/Lounge access, the complete connector and its main/guest seams.

Independent 2ft5 audit: 72 stations on the actual common finished-wall height, measured 0.722276–0.755098 m versus 0.7366 m nominal; all within 20 mm. This is the sampled range, not a claim about unseen surfaces. All 248 distinct new/locally modified solids have zero boundary/nonmanifold edges. 23234 nonwhitelisted source objects retain their geometry/matrix/material signatures. The adapter hash matches the loaded candidate; production guest/data/tour hashes remain unchanged.

## Source limits that remain explicit

The guest02 upper central divider is now a visible, closed solid at approximately source x304.5–308.4, y372.6–407.5. Its identity is plan-supported; the traced outline, finish and height remain C. The constant top is world 11.752675 m: 1.0 m above the highest adjacent L2 finish, 1.904875 m above the upper return, and nominally 1.12 m below the existing roof underside. It was not reduced to make a path pass. Both return routes now use source y412.3 and have been replayed against the actual divider, floors, ceiling, rails and furnishings. The wall-less 10e result remains historical and is not used as evidence for this wall.

South−1.18m is still an inferred finished plane within the sourcegrade interval; B1−2.36m remains the previousCdatum. The new interior panoramas do not show the western service flights and do not settle these exterior levels. The numeric source residuals and rejected nominal going lengths in `guest-circulation10-design.json` remain applicable. Full60declared-edge/7584integer-frame, all-room camera and visual checks were deliberately not claimed.

## Reproduction and preserved failures

On a newly loaded frozen09 scene, import the adapter and call `apply()`. It asserts the expected source target names, changes only an explicit whitelist, adds an embedded candidate manifest and does not save, render or write production data. `guest-circulation10-check.py` performs a fresh candidate build with4CPUthreads and a non-overwriting output guard. `guest-circulation10-final-audit.py` reopens the frozen candidate, repeats all29groups, measures the finished wall gap and checks closed solids. UseBlender5.2.1with `--python-exit-code1`. NoGPU/render/GUI operation was performed.

Preserved artifacts: first10scene/`firstFAIL-*` record real wall/canopy/terrain failures;10b/`second-*` are historical weaker-ground results;10c/`third-strict-ground-negative.*` demonstrate the24mm riser support overhang caught by the stronger ground method;10d/`10d-nonmanifold-negative.*` preserve the rejected Boolean landing and out-of-height dimension probes.10e changes that landing to one closed outline and uses only valid common wall heights; its `10e-without-upper-divider.*` and `10e-review.md` preserve the remaining source-wall omission.10f adds the source divider and restores the full southern turning band. These historical checks are not retroactively relabeled PASS.

Scoped neat-freak reconciliation: this handoff is the current local entry point; older numeric/negative artifacts remain identified as history under the explicit preservation requirement. AGENTS.md remains14lines and still correctly states the production boundaries; STATUS/START_HERE are root-owned and were not edited. No global settings or memory were changed.
