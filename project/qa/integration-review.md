# Integration geometry review

Review date: 2026-09-20. Scope: read-only review of `main_house.py`, `guest_house.py`, `furnishings.py`, `site.py`, `build_scene.py`, `fwlib.py`, room schedules, slab/wall/stair data, and material research. The findings below document the initial implementation snapshot. **Iteration02 follow-up closes the six identified geometry defects on sampled integrated mesh evidence; finish implementation was corrected, while material visual acceptance remains pending.** This is not final scene acceptance. See the dated follow-up at the end; historical source line numbers below precede the fixes.

## Findings requiring correction

### P1 — Continuous window transom crosses nominally open doors

`scripts/fwlib.py:108–112`, `window()`: `open_panel=True` skips a glass pane but still creates one transom across the whole opening at 72% of the window height. For typical main-house glazed doors, that bar is approximately 1.7 m above the walking surface. The corresponding doorway is not clear to a standing person despite the glass being removed. Split the transom by pane and omit it in the open doorway. Retain the actual non-door window divisions. Check the swung leaf and hinges separately.

### P1 — Main plunge-pool water is buried inside its deck slab

`scripts/main_house.py:198–200`: `MAIN_B_pool_deck` covers the full source rectangle `(534,375)–(700,432)` at Z `-2.78…-2.50`. `MAIN_B_plunge_water` is fully inside that footprint and at Z `-2.73…-2.70`. The slab covers the entire water surface. Make the deck an open ring around the basin, with independent bottom and side walls. A top/oblique actual render must show the open water.

### P1 — East-terrace stair ascends through the solid terrace slab

`scripts/main_house.py:177–182,243`: `MAIN_pool_eastterrace_stair` follows source `(540,423)→(540,380)` from Z `-2.50→0`. Its complete XY path is inside the main east terrace polygon, whose slab/finish has no stair cutout. A 0.22 m radius, 1.95 m tall path sample finds slab collision over approximately 14–92% of the ascent. Cut the required stairwell in both slab and finish, preserving the true upper landing and side guard. Do not resolve this by relying on Fly mode passing through the floor.

### P1 — Stair from main L2 to L3 intersects the north bathroom

`scripts/main_house.py:270,350–351`: `MAIN_stair2` follows source `(432,269)→(367,269)` from Z `2.8448→5.26415`. `MAIN_L2_bath_n_shell` has an east wall at source x394 and a south wall at y269, directly across/along the same path. The sampled standing envelope overlaps these walls over approximately 50–83% of the run; it also clips the bath ceiling and the L3 bath edge at the upper end. Recheck the HABS stair registration, bathroom boundary and landing together, then validate the whole route. Moving only the room-camera position will not fix this.

### P1 — Guest service stairwell starts too late for standing clearance

`data/guest_house.json`, `GUEST_SERVICE_ASCENT` and `GUEST_L2_CORRIDOR_FLOOR`; `scripts/guest_house.py:104–124`: the stair follows source `(316,354)→(316,404)` from Z `8.4→10.752675`. The upper corridor slab still covers source x287–326, y204–372. Its overlap with a 1.95 m standing envelope occurs around 9–44% of the ascent. The upper-level stair void must extend north of its present y372 edge, approximately to y351 for this authored run, while retaining a west circulation strip and the real upper landing. Exact final cutout should be checked against the plan and the evaluated mesh.

### P1 — Open water-hatch leaf blocks the top of its own stair

`scripts/main_house.py:245–253`: the water-stair top is source `(459,480)`, Z `.10`. `MAIN_hatch_open_leaf` is a full vertical glazed assembly on source x459, y462–498, Z `.10…2.22`, with `door=False`. This plane crosses the entire top exit of the modeled stair. Place/rotate the leaf at the photographed hinge edge so its open state clears the walking path, and retain the physical hatch frame. Inspect both from the living room and looking up the stair.

### P1 — Key kitchen and bathroom finishes contradict the accepted material evidence

`scripts/main_house.py:180–182` sets the kitchen finish to `dark`, with no 228.6 mm Cherokee Red rubber tile grid. Main bathroom floors fall back to `stone_floor`; their walls use `ceiling`. `scripts/guest_house.py:100–103` adds guest bath cork floors, but their walls remain the general wall material. `research/interiors.md:18–22,73,93` identifies the six cork bathroom interiors and distinguishes wall/floor reflectance, and selects the later 9 × 9 inch red rubber kitchen floor. Implement the documented room-specific finishes before claiming G3 acceptance. Other upper-floor cork assignments also require reference verification rather than extrapolation from the bathroom evidence.

## Method and limits

- Main straight stair footprints and walls/slabs were evaluated from the authored builder through read-only primitive capture; `export_data` was replaced in memory to avoid modifying module data. A standing cylinder was sampled at 101 positions, radius 0.22 m and height 1.95 m. This is a clearance diagnostic, not a collision engine.
- Guest stairs were checked directly against transformed slab polygons and wall segments with the authored opening intervals removed. The laundry descent did not produce the same definite ceiling/slab conflict.
- Main loggia-to-pool, water-stair structural slabs, first main internal ascent and service ascent did not produce definite slab/wall blocks under that limited diagnostic. Window panels were separately reviewed in source, hence the water-hatch issue remains valid despite the structural sample passing.
- Small stone-relief boxes in the capture do not apply their later object rotation; their apparent contacts were excluded from findings. The large slab and wall findings above use correct source polygons/segments.
- `furnishings.py` records zero footprint-placement warnings in the current build report, but its fitting routine tests room polygons and furniture footprints, not door paths or wall thickness. That count is not evidence that all furniture preserves navigation.
- No GPU/rendering or final GUI navigation was performed by this reviewer. The root integrator is testing the full scene. All P1 corrections need actual evaluated geometry, complementary rendered views and route verification after rebuild.

## Iteration02 independent closure review

The integrated `scene/Fallingwater_working.blend` saved **2026-09-20 13:39:18** was reopened and tested without rendering. Its embedded `FW_ROOMS.json` was used rather than a potentially newer external census. The complete structural validator returned **43 sampled PASS, 17 INCOMPLETE, no hard FAIL**. The 17 outstanding room types still need dedicated route, foundation, pool or cover review; they were not silently passed.

An additional independent test used the actual full evaluated scene, including furniture and site, to recheck the original specific defects. Evidence is in `automated-iteration02.geometry.json`; script and log share that stem.

| Original finding | Iteration02 evidence | Closure decision |
|---|---|---|
| Continuous transom across opened glazed doors | `fwlib.window` now splits transoms and omits the opened bay. Nine actual terrace-door gaps were crossed at four heights through 1.94m above sill; no frame/glass hits. | **CLOSED — identified geometry defect.** Other windows and whole-route usability still need visual/navigation review. |
| Main plunge-pool deck burying water | Actual downward ray at source `(615,402)` from Z-2.49 first hits `MAIN_B_plunge_water` at Z-2.7000. | **CLOSED — deck opening geometry.** |
| East-terrace stair through slab | All 45 tread/lateral ground and headroom samples pass; minimum measured headroom 2.6648m. Center radial body probes also found no obstruction. | **CLOSED — identified slab obstruction.** |
| Main L2→L3 stair through bathroom walls | Authored run shifted to source y279.7. All 42 tread/lateral samples pass; minimum headroom 2.0584m. Center radial probes found no bathroom/ceiling obstruction. | **CLOSED — identified bathroom conflict.** Historical registration remains explicitly approximate. |
| Guest service stair upper-floor obstruction | All 42 integrated tread/lateral samples pass, minimum headroom 2.1200m. The author report also verified approach/landing and reintroduced the old slab, producing 12 failures and minimum1.3024m clearance. | **CLOSED — identified corridor slab obstruction.** |
| Water-hatch leaf across top exit | The open leaf is now on the long side. All 51 tread/lateral samples pass, minimum headroom2.4975m; crossing the former top blocking plane at four heights produces no hit. | **CLOSED — identified leaf obstruction.** Exact hinge construction remains a visual/reference check. |
| Kitchen/bathroom finish mismatch | Actual saved material `MAIN_Kitchen_9inch_Cherokee_Rubber` is assigned to kitchen finish and carries0.2286m tile scale. Main bathroom finish surfaces use cork; guest actual cork floor/lining objects are present. Source changes implement the recorded finish families. | **Implementation corrected; visual acceptance OPEN.** Color, grain, wall/floor roughness, exposed edges and room-specific historical attribution require rendered comparison. |

The sampled stair test covered **180** tread-center/lateral positions, with standing-height requirement1.95m and lateral offsets±0.22m. At each tread center, five body heights and eight horizontal directions were probed to a0.22m radius against the complete scene. Nine terrace-door gaps and all **23** authored main-house thresholds passed their focused crossing/ground tests. These are finite mesh samples, not a continuous swept-body proof or a completed user navigation session. Minimum measured nominal terrace-door width remains0.6523m; this review records it, without claiming universal accessibility.

The two subsequent hard failures retained by validator v2 were also resolved in the integrated scene: the guest boiler room now has a source-supported roof, and the terrace census no longer claims a piece of the pool as flat floor. A separate integrated ray at the former terrace failure point still hits `GUEST_POOL_water` at Z8.96485, confirming no covering slab was inserted.

**Current status:** the six originally identified geometry P1 items are closed for this exact saved scene and the stated test scope. The finish assignment correction is implemented, but its visual validation and all broader PRD acceptance remain open.
