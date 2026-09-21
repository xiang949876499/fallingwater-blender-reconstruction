# Bridge10 watertrim — failed bounded candidate, 2026-09-21

**DO NOT INTEGRATE.** The saved animated candidate was freshly reopened and reproduces its recorded scene and physical hashes, but fails closed-surface, degeneracy and shoreline-preservation checks. Root accepted stopping this bounded task. There are no further watertrim variants underway.

The independently accepted bridge-only endfix remains `scene/Fallingwater_bridge10_endfix.blend`, SHA256 `2a7630b8024c37bd768e563236807f8049469172c7e44b03379a450f91637063`. Root and this agent actually viewed its HERO/WATER_DETAIL images and accepted the local black-band repair; overall environment/photo acceptance is still FAIL.

## Concrete failed implementation

`scene/Fallingwater_bridge10_watertrim.blend`, SHA256 `40f08d0f847e60b06f0656e0e1b08f0fb9bd6778f15db705d1ac81645529512c`, derives from that endfix. It adds two hidden masks built from the actual SW/SE closed L cores and face-stone prisms, then two EXACT Difference modifiers after the original water Solidify. It does not delete an AABB region, move the water head, lower the bed, alter the bridge deck or bake one static frame.

Only original object `WATER_BearRun_Continuous_Upstream_Downstream` changes, by appending the modifiers. All23,314 other original objects, base meshes, water shape keys/drivers, materials and scene globals match.62 protected core/shoulder/other-water physical hashes remain identical. The two new masks are `WATERTRIM10_SW_Actual_Masonry_Union` and `WATERTRIM10_SE_Actual_Masonry_Union`. This scene is saved at frame73; diagnostic checks explicitly use the six frames below.

The byte-exact helper used for that failed scene is archived at `qa/bridge10-watertrim-helper-exact-attempt01.py`, SHA256 `c6a0a4f3e8300e9be307d45faad53327311281d18cd2e9ce8aba59694ba41e55`. Current `scripts/bridge_watertrim10.py`, SHA256 `a02328a1653996c4c9b9e6e290753f5977f9ab2e9a595546e4f6304e45c40c59`, preserves the same failed recipe but requires explicit `apply(diagnostic=True)` and labels the result known-failed. Default `apply()` refuses. It is a failure-reproduction helper, not a production integration entry. Historical check scripts used the archived API; do not rerun them over the existing saved scene.

## Fresh verification

Authoritative corrected evidence: `bridge10-watertrim-readback.json` and `.log`; process exit0, status `FRESH_REOPEN_PASS_CANDIDATE_PHYSICAL_FAIL`. The source and candidate were reopened in a new Blender5.2.1 background CPU4 process. No render or scene re-save occurred.

| Frame | Candidate open edges | Zero-area triangles | Water remains strictly inside core | Exterior wet samples changed | Channel samples changed |
|---|---:|---:|---:|---:|---:|
|1|3|6|27|59|1|
|24|0|4|27|53|1|
|48|4|5|26|53|3|
|120|0|5|27|54|1|
|240|0|4|25|66|1|
|241|3|6|27|59|1|

Each frame uses964 samples:398 strictly inside the actual core,359 on its wet exterior,207 in the retained channel. Exterior samples clear the core by at least26mm, exceeding face-stone projection (19mm maximum). Wet-surface tolerance is0.15mm; failures include millimetre changes after Boolean retessellation. Frame1 maximum retained wet-height error is6.103mm. These are geometric comparison results, not claims of rendered visibility. Normal shoreline contact is not classified as an error.

Original water has409,192 evaluated triangles and zero open edges or degenerate triangles on all six frames. It also has1,054 isolated vertices referenced by no face. Fresh comparison excludes these unused points from exterior-surface preservation: **zero missing or new used far vertices** in all candidate frames. The first report's1,054 missing-far-vertex flags were bookkeeping false positives, not remote surface removal.

The current ray audit uses Blender's actual evaluated loop triangles. The earlier generic BVH polygon tessellation could choose a different diagonal for a deformed nonplanar quad; earlier shoreline counts are superseded by this table. Despite the corrections, genuine holes, degenerate triangles and residual internal water remain. Both baseline/candidate water still vary with time; frame1 physical hash equals frame241 exactly. Frame240 is not the loop duplicate. Drivers remain `cos((frame-1)*2π/240)` and `-sin((frame-1)*2π/240)` on the original two relative shape keys.

## Bounded methods tried and retained

| Method | Measured outcome | Evidence |
|---|---|---|
|Direct complete L meshes, EXACT with self-intersection handling|Frame1 took102.20s; second frame interrupted before bridge-end fix. No saved scene.|`bridge10-watertrim-timing-exact-self-interrupted.json/log`|
|Static exact union masks, then two EXACT water differences|Mask preparation about11.90+9.76s; pure evaluations3.94s/1.95s at1/24. Saved40f diagnostic; failures above.|`bridge10-watertrim-timing-exact-union.json/log`, `bridge10-watertrim-check.json`|
|Triangulate and clean only static masks|Masks become closed with no degenerate triangles. MANIFOLD still rejects river input. EXACT retry with fixed triangulation:1/24 take8.50s/6.34s, both4 open edges,32/34 zero-area triangles.|`bridge10-watertrim-solver-probe-attempt01.json/log`, `bridge10-watertrim-solver-probe.json/log`|
|Separate actual core/near-water prism collection|EXACT takes51.90s/46.44s, with11/15 open edges and9,707/9,290 nonmanifold edges. No saved scene.|`bridge10-watertrim-components-probe.json/log`|
|Remove only evaluated orphan points, clean masks, MANIFOLD (with/without explicit triangulation)|Solver still rejects. Apparent fast results leave physical river triangles unchanged, so they are not successful trimming or performance evidence.|`bridge10-watertrim-timing.json/log`, `bridge10-watertrim-manifold-native-tris.json/log`|

The original static union masks were edge-closed but contained353/249 zero-area triangles (SW/SE). Cleanup resolved those mask defects but did not make the dynamic operation pass. The baseline's used surfaces have no BMesh bad edges; all1,054 bad vertices are isolated. Removing only those isolated points does not resolve MANIFOLD's input rejection. The remaining exact solver/input-conversion cause is unresolved, rather than attributed conclusively to a single mesh defect. The final experimental helper is preserved as `bridge10-watertrim-helper-manifold-failed.py`.

## Integration and limits

Adopt only bridge endfix via `data/bridge_detail10.json` and `scripts/bridge_detail10.py`; leave old water untouched and label complete water QA not passed. Existing intersection evidence lies aroundZ−2.91…−2.75, below deck bottom−.555m and paving+.012m. It is not a road-height flooding defect. Do not remove the source-supported L walls just to hide this unresolved old-water penetration.

Dynamic2–4s evaluations do not meet24fps playback. Static orbit performance after dependency-graph caching was not measured. No240-frame cache was baked, and no realtime or animation-quality acceptance is claimed. A later offline mesh-cache strategy would still require valid per-frame trimmed surfaces first; these failed surfaces must not be baked as if repaired.

All attempts and negative evidence remain archived. No original water script, site/build/config, core geometry, production scene or user-opened scene was modified. Documentation reconciliation follows the neat-freak skill only within owned bridge10/data/QA files; root remains responsible for global STATUS and release manifests.
