# Tour path validation

Camera installation generated a 120-second, 24fps main timeline (frames 1–2880) and separately named supplemental inspection segments. Delivery resolution is 1920×1080. No video has been rendered by this module.

Actual scene mesh ray casts: 1,306,941. Candidate walking points test expected floor height, upward body columns and camera clearance. Continuous walking sweeps test several body heights and lateral offsets. Ground tolerance is ±0.19m to accommodate treads. Free inspection segments test the camera path only and are explicitly labeled.

7 of 7 selected doorway connections passed (straight or turning paths as individually recorded). The covered connector status is `PASS_MESH_AND_GROUND`. Main-building access by inner stair, north terrace, outer curved stair and upper landing is `PASS_SEGMENTS_NOT_GUI_ACCEPTANCE`. 0 requested main segments and 0 room inspection placements remain excluded or blocked. Exact object names and positions are in `tour-path-check.json`.

The installed camera values are `PASS_CAMERA_VALUES_AND_COVERAGE`: 10 main segments and 49 supplemental segments cover 60 of 60 space records. Every delivered integer-frame camera location is compared to the checked polyline, with finite nonzero orientation and linear interpolation checked. The per-room camera/frame mapping is in `tour-path-camera-coverage.json`. Space records include terraces, pool, stairs and service areas, not only habitable rooms.

Full declared adjacency status: `INCOMPLETE_FULL_ADJACENCY_ACCEPTANCE`. Of 60 deduplicated declared edges, 58 passed, 2 failed and 0 remain untested or require an explicit non-walking endpoint definition. All declared space nodes are retained. Exact edges, source hashes, failures and validated connected components are in `tour-path-all-adjacency.json`. The seven selected film doors do not represent full navigation acceptance.

Cuts occur between every main segment. They are deliberate editorial cuts and do not prove connected floors or accessible rooms. All keyframes use linear interpolation to prevent spline overshoot. This is geometric route evidence, not rendered visual acceptance, GUI collision support, or a performance test.
