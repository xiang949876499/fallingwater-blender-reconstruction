# Iteration07 navigation and saved tour audit

Source: `scene/Fallingwater_iteration07.blend`, SHA256 `bf50530009e4a93315915815473188c91d891272ef2d8e9e0169b704bd2e2f16`. Independent saved tour: `scene/Fallingwater_tour_checked_iteration07.blend`, SHA256 `792882445860ae6a7bb37e3e03838d74a07647e89dbf5475a056125d6bac067e`. Source and saved hashes were both rechecked after the independent reopening; neither source nor working scene was overwritten.

## Executed results

- **60 current valid edges: 60 PASS / 0 FAIL / 0 NOT_RUN.** These comprise 52 normal walking connections and 8 explicitly typed inspection relationships.
- All 60 space records remain covered by 10 main and 49 supplemental segments. The main tour is 120 seconds at 24 fps, including 36 seconds outside. No requested main segment or space was excluded.
- All seven selected doors and the actual main-to-guest approach through the inner stair, L2 hall, north terrace, curved stairs, upper north walk and covered connector pass sampled mesh/ground checks.
- The independent saved file was reopened and **7,584 actual integer-frame camera positions** were checked again. 6,144 frames receive body, ground and camera checks; the other 1,440 are explicitly free camera inspections or exterior flight. Adjacent frames within each segment receive a mesh sweep. No sweep or connectivity claim crosses a cut.
- Maximum piecewise-linear path discrepancy is `0.0000043703m`; actual dependency-graph world matrices are evaluated after `scene.frame_set()` at every frame. Integer-frame geometry failures: **0**. Reopen status: `PASS_REOPENED_TOUR_GEOMETRY_NOT_VISUAL_ACCEPTANCE`.

## Source-retracted pool route

The historical iteration06 result remains **61 edges: 60 PASS / 1 FAIL / 0 NOT_RUN** in its frozen JSON and scene. Its ADJ_017 Loggia–East Terrace dry route is now separately recorded as `SOURCE_UNSUPPORTED_AS_DRY_WALKEDGE`; it is not a repaired navigation PASS and was not removed merely to improve a count. HABS main03/04 support pool-edge stonework but do not establish a continuous dry walking surface at a shared stair-foot elevation. The stronger source-support wording in the old iteration06 prose was superseded by the architectural source review in `main-pool-iteration06-report.md`.

Loggia–Plunge is a dry observation/stair inspection relationship. It never joins two walking components through the pool. The pool's declared polygon is an inspection envelope with `walkable_polygon=False`; its supplemental camera is explicitly free inspection. Living–East Terrace remains the valid glazed-door access. The corrected north pool-wall corner does not establish an unsupported ring walk.

Current edge IDs are ordered within this iteration; compare the from/to room pair and retraction record across iterations rather than assuming old numeric IDs are stable.

## Retained first-attempt failures and local route changes

The first complete 7,584-frame pass found 47 body-contact frames in six local shots; no checked scene was saved from it. `tour-path-iteration07-attempt01-review.md` identifies the low tables, chairs, towel and first tread hit by the original paths. Room-move selection was tightened from 0.25m to 0.01m body sampling without relaxing any clearance rule or moving scene geometry. The subsequent actual-frame check remains independent of that selection sampling.

The final route changes 8 local shots from the negative attempt: GUEST_LOUNGE, MAIN_L1_SERVICE_STAIR, MAIN_L2_DRESSING, MAIN_L2_BATH_G, MAIN_L2_GUEST, MAIN_L2_STAIR, MAIN_L3_TERRACE, GUEST_B1_LAUNDRY. Exact before/after waypoints and modes are retained in `tour-path-iteration07-reopen-result.json`. The source script SHA256 is `105c10dfb180448384ea6c9970b9d5d167295776f7475b280b43f341cbd26901`.

An additional isolated 1cm replay is recorded in `tour-path-iteration07-local-repairs.json`. It reproduces contacts on the six originally failing stored paths and passes all eight revised paths. The original Service Stair and L3 Terrace stored paths also pass that replay; their reselected paths are valid alternatives, not two additional diagnosed failures. No failure is inferred merely because a candidate route changed.

## Evidence and limits

Frozen files: `tour-path-all-adjacency-iteration07-final.json`, `tour-path-check-iteration07-final.json`, `tour-path-camera-coverage-iteration07-final.json`, `tour-path-route-iteration07-final.json` and `tour-path-iteration07-reopen-result.json`. The eight actual observer/target patches and inspected stair runs are also collected in `tour-path-inspection-semantics-iteration07.json`. Attempt reports and logs remain available; previous iteration04–06 checkpoints are preserved.

The static world BVH comes from actual mesh polygons and evaluated curves. Body radius is 0.18m and eye height 1.60m; walking samples check ground height/normal, five body columns, several ray heights and lateral offsets. Stair seam recovery accepts an upward physical tread within 3cm. This remains sampled mesh evidence, not a general-purpose capsule controller or proof of every possible path through a doorway. Pool, storage and foundation observations are never reported as body entry into those spaces.

No image, GPU job, simulation bake or film render was started. Camera exposure is still proposed for the moving tour. Final visual quality, film output and GUI navigation performance remain separate acceptance work. This report reconciles current navigation evidence while preserving historical failures.
