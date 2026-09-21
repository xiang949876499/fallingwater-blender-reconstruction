# Iteration07 first complete integer-frame pass: retained negative evidence

Source scene SHA256: `bf50530009e4a93315915815473188c91d891272ef2d8e9e0169b704bd2e2f16`. The complete 60-edge adjacency audit passed (52 walking connections and eight typed inspection relationships). The first full 7,584-frame scan nevertheless found **47 frames with body contact across six local camera segments**. No checked07 scene was saved from this attempt.

| Segment | Failed frames | First frame | First actual object hit |
|---|---:|---:|---|
| GUEST_LOUNGE | 9 | 2358 | `FW_FURN_GUEST_L1_LOUNGE_low_lounge_table_02_thick_horizontal_top` |
| MAIN_L2_DRESSING | 7 | 4456 | `FW_FURN_MAIN_L2_DRESSING_sling_study_chair_01_sling_diagonal.001` |
| MAIN_L2_BATH_G | 14 | 4681 | `FW_FURN_MAIN_L2_BATH_G_towel_rail_02_folded_towel` |
| MAIN_L2_GUEST | 2 | 4960 | `FW_FURN_MAIN_L2_GUEST_desk_chair_03_seat` |
| MAIN_L2_STAIR | 4 | 5385 | `MAIN_stair2_00` |
| GUEST_B1_LAUNDRY | 11 | 6806 | `FW_FURN_GUEST_B1_LAUNDRY_folding_worktable_03_thick_horizontal_top` |

Every failure has an evaluated integer-frame camera position, the body column's hit point/normal/distance and a preceding-frame sweep result in `tour-path-camera-coverage-iteration07-attempt01.json`. The route and graph are separately preserved in `tour-path-route-iteration07-attempt01.json` and `tour-path-all-adjacency-iteration07-attempt01.json`. Exit code 1 is intentional: the runner refuses to save a checked scene after a failing camera scan.

These contacts were missed between the earlier 0.25m body-column samples used to choose local room shots. Location FCurves still matched their polylines; the failure was the selected path's fine geometry clearance, not interpolation overshoot. This first report uses the legacy `FAIL_ANIMATION_VALUES` status label, but its `geometry_failure_frame_count` and actual hits identify the reason. Subsequent reports distinguish animation values from integer-frame mesh failure explicitly.

The next selection uses 0.01m body samples for cinematic room moves and retains the independent actual-frame check after keying. Candidate searches stay bounded to the same room's existing positions. No wall, furniture, fixture, opening or floor is moved to accommodate a camera, and no threshold or body-radius tolerance is relaxed. The L2 stair contact occurs where a flat landing shot approached the first tread; it does not invalidate the separately checked stair ascent.

The source-retracted historical Loggia–East Terrace dry ring route remains separate from this issue. It is not one of the current 60 valid edges and is not silently reintroduced through the pool observation node. Frozen iteration06 evidence remains unchanged.
