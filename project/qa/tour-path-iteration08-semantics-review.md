# Iteration08 navigation semantics review

**PASS_SEMANTIC_REVIEW_NOT_GEOMETRY_ACCEPTANCE — 2026-09-20.** This independent review inspected current declarations, the navigation dispatcher and the dedicated iteration08 save gate. It did not launch Blender, load a scene, cast geometry rays or render images. The running iteration08 geometry result was not yet available when this review finished.

The coordinator-reported target is `scene/Fallingwater_iteration08.blend`, SHA256 `c5cd501e4c8ae0205ecb2437cd2d06d0c92bcc9a87e7d93d3986aeef976070d7`. The reviewer did not independently hash the scene. Code and data hashes are recorded in the companion JSON.

## Declared graph

- 39 main-house declarations + 20 guest-house declarations + one explicit cross-building connection produce **60 unique current edges**. No CSV-only edge is pending reconciliation.
- All **60 source space records** remain present: 40 main-house and 20 guest-house spaces. The graph has **61 nodes** because `EXTERIOR_UNDERCROFT` is a separate point-defined endpoint, not another room.
- Dispatch classifies **52 normal walking edges and 8 inspection relationships**: three dry-edge observations (Living–Hatch, Loggia–Plunge, Guest Terrace–Pool), two cabinet observations, and three foundation/free-fly observations.
- The historical Loggia–East Terrace pair is absent from the active adjacency list and retained under `retracted_edges` as `SOURCE_UNSUPPORTED_AS_DRY_WALKEDGE`. It is not a repaired PASS. The manifest also skips this pair if encountered in stale CSV data.

`all_adjacency_checks()` routes pool/water endpoints to `water_inspection()` before considering the general exterior-step branch. Thus Loggia–Plunge cannot silently become the withdrawn dry cross-pool route. Storage tests observe cabinet surfaces from outside; pool tests assert no body entry into water; foundation tests define a free camera endpoint. Water acceptance additionally requires its named stair run to pass.

Only the exact status `PASS_MESH_AND_GROUND` enters the walking graph. `PASS_INSPECTION_*` observations contribute to typed acceptance counts but never join walking components. An isolated control-flow test executed the current dispatcher with synthetic geometry-helper results: it produced the expected 52/8 split and placed every inspection edge's endpoints in different walking components. These synthetic results are **not actual geometry evidence**.

## Save gate

The dedicated runner checks the source path and expected scene hash before installing cameras. Its save expression requires 60 PASS / 0 FAIL / 0 NOT_RUN, the exact 52/8 split, the full successful route status, 7,584 frames with zero geometry failures, actual camera coverage PASS for all 60 spaces, actual world-matrix and within-segment sweep flags, 10 main + 49 supplemental segments, and no exclusions or uncovered spaces. An existing checked08 file prevents overwrite.

The camera evidence implementation evaluates each actual dependency-graph camera matrix after setting the integer frame, tests its position and previous-frame sweep, and includes geometry failures in both segment and aggregate camera status. The runner therefore does not infer safety from the frame total alone. Synthetic gate tests rejected a geometry failure, failed camera status at the full frame count, absent matrix flag, false sweep flag, incomplete frames, an incorrect walking/inspection split, and uncovered space.

One non-blocking hardening opportunity remains: `source_hash_unchanged` is computed before saving but asserted only afterward. Including it in the pre-save `passed` condition would fail closed if a future run allowed concurrent source replacement. The source is explicitly frozen for this run. The generic `tour.py --save-checked` option also saves without this strict gate; it is not used by iteration08.

## Scope and handoff

Actual iteration08 geometry acceptance and independent reopening of the saved scene remain with the coordinator. The global status correctly still identifies iteration07 as the last completed route acceptance; it must not be promoted from this semantic review. Visual quality, GUI navigation and film delivery are outside this report. Neat-freak reconciliation was limited to these owned review artifacts and checking the existing status/iteration notes; no shared code, data, project guidance or memory was changed.
