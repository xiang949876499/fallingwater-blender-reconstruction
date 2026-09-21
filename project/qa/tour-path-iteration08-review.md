# Iteration08 navigation — negative frozen result

Executed 2026-09-20–21 on `scene/Fallingwater_iteration08.blend`, SHA256 `c5cd501e4c8ae0205ecb2437cd2d06d0c92bcc9a87e7d93d3986aeef976070d7`. The source hash remained unchanged. Blender 5.2.1 LTS, CPU4, `--python-exit-code 1`; no render, GPU, GUI or bake.

**Full adjacency is incomplete: 58 PASS / 2 FAIL / 0 NOT_RUN.** Fifty normal walking connections and eight typed inspections pass. All 60 declared spaces remain; the separate exterior inspection endpoint gives 61 graph nodes. No failed edge was dropped or converted to an inspection to improve the count.

**All 7,584 actual integer camera frames pass geometry checks**, including 6,144 body/ground/camera frames and 1,440 explicitly free-camera frames. All frames use `scene.frame_set()` and evaluated world matrices, and adjacent frames within a segment receive body/camera sweeps. All 60 spaces are covered by 10 main and 49 supplemental segments, with no excluded requested segment. This camera result does not satisfy the two failed graph edges and is not rendered visual acceptance.

The strict save gate correctly refused to write `Fallingwater_tour_checked_iteration08.blend`. The process exited 1 at its explicit failure assertion after all checks and reports had completed; this is a failed acceptance result, not an unexecuted or crashed audit. No independently reopened checked08 exists. Frozen07 and its checked tour remain untouched.

## Failed connections and actual local probes

1. **ADJ_041 — GUEST_L1_CAR_COURT → GUEST_L1_STAIR_HALL.** Old candidate approaches intersect the new exterior laundry retaining wall, for example body point `(1.14553,41.06560,10.00000)` with a side-column hit at `(1.32553,41.06560,9.19900)`. The search exhausts 388 nodes without validating a route. A separately verified northern opening path `(2.85,41.24,10.0) → (2.85,40.98,10.0)` passes at 1cm spacing and rests on `GUEST_L1_HALL_NORTH`; this is a possible source-consistent route-anchor correction, not yet installed.
2. **ADJ_054 — GUEST_L1_STAIR_HALL → GUEST_L2_HALL.** The original 14-tread body centerline and upper attachment pass, but the lower approach hits the new wall or loses floor support. The exact geometry leaves **0.152160645 m** between the north platform edge Y40.843120575 and the first tread's north edge Y40.690959930. At `(2.88848,40.78541,eye10.08402)` there is no floor near expected Z8.48402. Eight cross-width stations × eleven Y samples return 56 terrain hits through the gap, 16 actual tread hits and 16 platform hits. The old07 approach also fails a new 1cm replay on08 at `(3.00852,40.80591,eye10.09024)`. Its old coarse positive result must not substitute for this negative evidence.

Adding the first tread as a room candidate can make the generic stair attachment appear to pass through a zero-length approach. The local probe records that experiment, but **it was not installed or accepted**: it would omit the real approach and leave the support gap unresolved. No wall, stair, floor, furniture or route was changed during this audit.

## Architectural source review now gates correction

Actual newly viewed native TIFF crop: [guest-platform09-source.png](guest-platform09-source.png), with [provenance](guest-platform09-source.json). It shows continuous drawn paving at the northern stair interface and no narrow construction gap. However, it also exposes a stair-direction issue that must be resolved before choosing a patch elevation: the right long run's UP arrow points north in guest01 and guest02, while the existing right run rises south.

The hypothesis that a return flight is missing is still under independent review. Guest01's left run has both UP-south and DOWN-north annotations plus a break line, potentially referring to the basement flight; guest02's left-UP interpretation and platform elevation need corroboration. Root has directed an independent two-sheet TIFF review. No speculative folded staircase or isolated 152mm patch has been built. The next geometry correction belongs to iteration09, followed by a new full-scene route audit.

## Evidence files

- `tour-path-all-adjacency-iteration08-attempt01.json`: all 60 fresh actual edge checks, including complete failures and retained source retraction.
- `tour-path-camera-coverage-iteration08-attempt01.json`: all 7,584 actual integer-frame camera/body checks.
- `tour-path-check-iteration08-attempt01.json`, `tour-path-route-iteration08-attempt01.json`: installed-in-memory route, coverage and open issues; no saved checked blend.
- `tour-path-iteration08-attempt01-result.json` and `.log`: strict acceptance failure after complete execution.
- `tour-path-iteration08-local-probe.json`: exploratory anchors, before/after candidate semantics and negative approach results; no accepted geometry repair.
- `tour-path-iteration08-stair-gap-probe.json`: exact object bounds, 88 independent scene rays, dense path replay and valid northern opening segment.
- `tour-path-iteration08-semantics-review.md/json`: independent code/data review, explicitly not a geometry execution claim.

The source-retracted Loggia–East Terrace dry route remains outside valid edges and is not a repaired PASS. All eight typed inspections retain their observer/target evidence and do not merge walking components. The validator SHA during this run was `105c10dfb180448384ea6c9970b9d5d167295776f7475b280b43f341cbd26901`.

Scoped documentation reconciliation preserves earlier failures and checked07, distinguishes geometric camera success from failed navigation, and defers central STATUS/dimension updates to the integrator. No final delivery or full iteration08 navigation success is claimed.
