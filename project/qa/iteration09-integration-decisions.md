# Iteration09 integration

2026-09-21. **Build complete; project delivery remains incomplete.**

`scene/Fallingwater_working.blend` and frozen `scene/Fallingwater_iteration09.blend` have SHA256 `489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331`,44,414,422 bytes. The fresh background build completed in130.433 seconds with exit0:60 space records,23,385 objects,9,566 meshes and1,394,192 unique mesh vertices. These include service, terrace and inspection spaces, not60 bedrooms.

Accepted changes are structure09/09b source-bound floor, ceiling and stone-corner repairs, plus10 sewn soft pillow meshes on8 beds. The main09 four-view,09b two-view and pillow two-view images were actually opened. [Structure09b visual limits](structure09b-root-visual.md) and [pillow visual limits](softgoods09-root-visual.md) remain explicit. This build does not install the guest stair hypothesis, new shrubs, new ground material, native water or the preview-light experiment.

## Reproducibility and independent checks

- [Frozen inputs and build](integration09-freeze.json) identify23 unchanged inputs and the prior generated main-house data snapshot. `main_house.build()` regenerates `data/main_house.json`; a fresh source-only export independently matched its exact new UTF-8/Windows-CRLF bytes. The first overly broad immutability assertion and initial LF-only comparison failed, and their logs remain. No source or geometry was changed to bypass those checks.
- [Build log](build-iteration09.log) and [counts](integration-build09.json) are preserved independently of later builds. Frozen08 remains unchanged.
- [Independent saved camera check](camera09-validation-summary.json):120/120 actual saved settings match and120/120 geometry checks pass, using3,840 rays. Camera configuration remains `f011c9462431e12137a49d3829a85586da0804a5a934086e03d7143c7d5dc1d0`. This does not validate all room images or continuous navigation.
- Full09 independent checks finished:58/60 connections PASS,2 FAIL (ADJ041/054), and7,584/7,584 integer frames PASS. No checked09 scene was saved. All production files remain unchanged. See `tour-path-iteration09-review.md`. Five integrated focus images have since been rendered and actually opened; see `iteration09-focus-review.md`.

## Guest circulation evidence changes the next reconstruction

The [full-sheet review](guest-level-context09-review.md) finds a southern service-stair visible ground line around−1.15m relative to the guest MAIN0 datum, two west-descending stair groups along the south passage, and further steps toward the pool and connector. That contradicts the existing flat south circulation assumption. The exact floor-surface and storey correspondence remains partly uncertain; the basement lowest outline at about−1.89m is not a confirmed finished-floor datum.

The earlier four-half-flight numerical hypothesis at south−1.633846m must not be called source-confirmed. A new explicitlyC reconstruction is being screened against complete circulation, real openings, unchanged north doors and the existing headroom/tread requirements. No speculative staircase is installed in09.

## Water and landscape remain diagnostic work

The stable09 true-bed static control passes, and one36-frame impact cache conserves water approximately within its stated diagnostic tolerance. Its effective flow exceeds the authored target by70.44%, and its artificial pool cannot join the natural scene. [Root actually viewed three raw frames](water09-root-visual.md); no water candidate is installed.

The scanned-leaf ground material failed three views. A16-plant branch/leaf shape candidate preserves root positions, counts and original materials. Root and worker actually opened three candidate and three baseline images and accept local morphology only; the full environment still fails. See `shrub08-root-visual.md`. It does not alter this09 build.

Final requirements still include corrected guest circulation, source/photo matching, complete room quality, accepted water and landscape, verified realtime interaction/performance,12 final4K images, full films, portable delivery and the user-authorized publicGitHub repository. Nothing in this integration record closes those gates.
