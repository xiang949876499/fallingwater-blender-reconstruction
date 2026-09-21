# Iteration04 navigation preparation

Status: **PREPARED, NOT RUN against the latest integrated scene**. The iteration03 tour results remain historical evidence for their recorded source file. Corrected kitchen/guest geometry and new fixtures require a fresh integration check.

The authoritative main and guest data declare 60 edges, plus the integrator's covered cross-building connector: 61 deduplicated edges. The graph retains all 60 space records and the undeclared `EXTERIOR_UNDERCROFT` endpoint. Reverse/synonymous declarations are merged by endpoint pair while their source and type information are preserved. `tour-path-adjacency-preparation.json` contains the complete list with source hashes; no previous PASS status is copied.

The next `tour.install` performs every declared-edge check alongside the film-camera checks. Surveyed main thresholds and guest wall-opening spans are tested first. Both room approaches must connect to a physically clear threshold. Remaining same-level routes may use a room-union turning search, capped at 1,800 nodes per edge. Stair edges use the actual named tread meshes and checked end approaches, with at most 1,200 search nodes per attachment. A failed bounded search remains a failure requiring review, not proof that a historical passage never existed.

The corrected kitchen door is source x324, y270–287: world x−0.1572, y13.4343–14.3370. Its body-probe center is y13.88565; old door hints are not retained. AGA, worktable and chair placements were coordinated with this door and passed an independent architectural/furnishing module test; this does not replace iteration04 validation.

The following declared cases need explicit semantics and cannot automatically receive a walking PASS:

- Three foundation bays refer to `EXTERIOR_UNDERCROFT`, which has no room polygon/ground definition.
- Two bedroom closet connections are cabinet access, not passages for a standing body.
- Pool and water-stair endpoints require separation of dry approach/coping from actual entry into water. Actual tread runs can be tested independently, but that does not establish standing-body traversal of the water space.
- Loggia to east terrace names a multi-flight exterior route. Its lower landing sequence must be defined before it can be tested as one continuous route.

Results will be written to `tour-path-all-adjacency.json`, preserving every edge, exact failure details, test limits and connected components formed only by passed edges. Any FAIL or NOT_RUN keeps full navigation acceptance incomplete. Camera coverage, rendered views and GUI traversal remain separate evidence.
