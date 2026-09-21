# Guest circulation10 independent candidate handoff

Current artifact: `scene/Fallingwater_guest_circulation_candidate10e.blend`.

- Candidate SHA256: `e3f134081bddd77d8a4344a3046ef224c1db1bea0ff35644e7e7bf750a06c01d`.
- Immutable full09 source SHA256: `489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331`.
- Adapter: `scripts/guest_circulation10.py`; SHA256 `fd72d02b69baccaa45b754227f3aa0364bb123e6bcb581e00283f62b0ea65031`.
- Independent reopen: **29 local groups /3485 samples PASS;0 FAIL;0 NOT_RUN within this local scope**. This is not full navigation, source-authenticity or visual acceptance. The candidate is not installed in production.

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

Independent2ft5audit:72stations on the actual common finished-wall height, measured0.722276–0.755098m versus0.7366m nominal; all within20mm. This is the sampled range, not a claim about unseen surfaces. All247distinct new/locally modified solids have zero boundary/nonmanifold edges.23234nonwhitelisted source objects retain their geometry/matrix/material signatures. The adapter hash matches the loaded candidate; productionguest/data/tour hashes remain unchanged.

## Source limits that remain explicit

The guest02 upper central short solid divider, approximatelyx304.5..308.4,y372.6..407.5, is not fully represented by the old production assembly. The retained lower wall ends at itsCtop; the higher flight guards here areCrails. Thus the upper return passes against the actual candidate, **not against an unbuilt source solid divider**. Root was notified; a source-divider candidate/recheck is needed before treating the circulation as a complete source reconstruction. Its unknown top height must remainC. If that divider is added, the lower return should use the source-supported southern turning band rather than the current tightery408turn.

South−1.18m is still an inferred finished plane within the sourcegrade interval; B1−2.36m remains the previousCdatum. The new interior panoramas do not show the western service flights and do not settle these exterior levels. The numeric source residuals and rejected nominal going lengths in `guest-circulation10-design.json` remain applicable. Full60declared-edge/7584integer-frame, all-room camera and visual checks were deliberately not claimed.

## Reproduction and preserved failures

On a newly loaded frozen09 scene, import the adapter and call `apply()`. It asserts the expected source target names, changes only an explicit whitelist, adds an embedded candidate manifest and does not save, render or write production data. `guest-circulation10-check.py` performs a fresh candidate build with4CPUthreads and a non-overwriting output guard. `guest-circulation10-final-audit.py` reopens the frozen candidate, repeats all29groups, measures the finished wall gap and checks closed solids. UseBlender5.2.1with `--python-exit-code1`. NoGPU/render/GUI operation was performed.

Preserved artifacts: first10scene/`firstFAIL-*` record real wall/canopy/terrain failures;10b/`second-*` are historical weaker-ground results;10c/`third-strict-ground-negative.*` demonstrate the24mm riser support overhang caught by the stronger ground method;10d/`10d-nonmanifold-negative.*` preserve the rejected Boolean landing and out-of-height dimension probes.10e changes that landing to one closed outline and uses only valid common wall heights. These historical checks are not retroactively relabeledPASS.

Scoped neat-freak reconciliation: this handoff is the current local entry point; older numeric/negative artifacts remain identified as history under the explicit preservation requirement. AGENTS.md remains14lines and still correctly states the production boundaries; STATUS/START_HERE are root-owned and were not edited. No global settings or memory were changed.
