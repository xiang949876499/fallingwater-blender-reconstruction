# Bridge 10 handoff — isolated structural candidate

**Current decision (2026-09-21): use the accepted endfix described in the final section. Everything before that section is the historical meshclean record, retained as requested. Its visual NOT_RUN state and helper SHA are superseded. Watertrim remains FAILED and must not be integrated.**

## Historical meshclean record — superseded by endfix

Geometry/readback PASS; visual acceptance NOT_RUN; complete water QA NOT_PASSED. No production hook or original scene changed. No rendering was performed.

Candidate: `scene/Fallingwater_bridge_candidate10_meshclean.blend`

SHA256 `15260dcfd92783a4695ce7fc0de83072531e5c09564bcdb26dbf2f2ac6717588`. Source full09 `489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331`. Saved frame73; render comparisons must explicitly use frame48.

The 77 exact original stone-parapet objects were removed only in this candidate. Seven new objects provide two continuous .20m concrete parapets with rounded ends, four terrain-seated layered stone L returns, and a .123m west edge closure. The existing deck, flags, four deep abutments, both approaches and all other objects remain unchanged. The photos establish construction identity; positions/heights/thicknesses and foundation continuation remain C with uncertainties in `bridge10-source-design.md`. The central rectangle/four squares remain U, with no new obstacle.

Verification: 23308 retained object fingerprints identical; original material/light/camera/render/config globals identical; 63 core/shoulder/water evaluated physical hashes unchanged. All seven new evaluated meshes are closed and finite, with zero zero-area polygons or triangles. Fresh-process reopen reproduced the full scene fingerprint and new physical hashes.

Nine evaluated face-to-face horizontal rays through the SOUTH stone return ends measured **4.038599014m** against nominal **4.0386m (13 ft3 in)**. Both actual inward faces and their normals were validated, not inferred from object bounds. This is the nominal south return gap, not deck width. The retained walking route had11,554 checks and0new obstacles. All129 existing cameras retain their transforms; minimum distance to any new bridge mesh is4.8165m. Each of220 foundation perimeter samples sits20mm below the same frozen terrain.

## Remaining water boundary

Water-bank contact is expected. The specific unresolved issue is that the old continuous river still contains triangles inside the new CLOSED masonry volume. The spatial probe clips each water triangle against the actual sloping lower triangles of the L core and its top plane. It therefore excludes water below the foundation, rather than treating every XY overlap as a collision. Shallow stone face projections are included in the exact crossing-point BVH test but excluded from the core interior area.

| Return | Actual intersection X | Y | Z | Upward water surface inside core |
|---|---:|---:|---:|---:|
| SITE_Bridge10_Stone_Return_SW | 23.238636…25.430441 | -4.166305…-2.456291 | -2.908846…-2.784373 | 1.942248m² |
| SITE_Bridge10_Stone_Return_SE | 29.469040…31.425056 | -4.168301…-2.458253 | -2.873380…-2.751796 | 1.727537m² |

Both intersections are below the original deck bottom−.555m and paving+.012m, never through the road-height stone faces. The north returns have no intersection. These measurements do not prove how much is visible through water/refraction in a rendered view; root must inspect the images. Opaque masonry may hide internal water, but the triangles have not been physically trimmed at the new shore.

`bridge10-water-spatial-mask.json` is the detailed trim evidence: actual intersection points, intersecting evaluated water-triangle IDs, clipped polygons, L-core rectangles and actual bottom-plane method. `bridge10-water-spatial-summary.json` is the short version. For the later water pass, retain the real L masonry and trim only the water portion INSIDE its evaluated volume, preserving the central stream and every elevation. Do not cut the entire AABB box or lower terrain/core. Both upper and lower river faces are present, so the combined projected area is not a unique surface area; use the upward-facing area column above. The old full river has409,192triangles and a very broad inheritedAABB; it is not a suitable global mask.

## Root render pair

Use the same temporary QA cameras for frozen09 and the mesh-clean candidate, frame48, unchanged exposure/material/light settings. These suggestions were ray-probed without creating cameras; no obstruction lies within .20m of either camera, and wall-target rays first hit the intended bridge components. They are authored QA views, not surveyed source cameras.

| QA view | Camera XYZ | Target XYZ | Lens | Purpose |
|---|---|---|---|---|
| SOUTH_APPROACH | (27.45,−10.5,1.8) | (27.45,2.0,.25) |28mm| Both rounded parapets and south stone endpoints/13′3″ gap |
| HOUSE_SIDE | (18.0,1.0,3.8) | (27.45,1.5,−.25) |28mm| Continuous pale concrete elevation and tall stone bank faces, comparable to Hyde composition |

Parent schedules CPU renders; this agent ran none. A front/side visual comparison remains necessary before structural appearance acceptance.

## Helper and archives

`scripts/bridge_detail10.py` exposes `apply(old_names)` for an independently opened frozen09. Pass exactly `bridge10-source-probe.json["exact_replace_names"]` after verifying source SHA; caller owns full before/after audit. It rejects missing names, non-parapet names, wrong list count and a second application while Bridge10 objects exist. It does not load source photographs or create new materials. This is an isolated candidate helper, not a production integration entry. Do not call it silently on another scene revision.

Helper SHA256 `b575a9d01641c38af48f3be99effacfdf712084f465ac6a807cc8a44ce3e0b5d`.

Preserved negative evidence: original `Fallingwater_bridge_candidate10.blend` SHAaaf7c1abda92b54bd5dfd4790f40de593f3b5b8ba7c236c084aa0fc28bac49c1 and attempt02 check/readback files retain the44collinear cap triangles. The mesh-clean version changes only cap triangulation/one internal support point per new L. Attempt01 records the Blender5.2 triangulation return-type mismatch, fixed before any candidate save. The first unfiltered water-volume probe was interrupted and archived; spatial filtering reduced it to a local calculation without changing the answer.

Independent source viewing and manifest proposal: `bridge10-reference-viewed.json`, `bridge10-reference-manifest-append.csv`, `bridge10-source-identity.json`. All three photos are reference-only, excluded from public packages and never textures. Central manifest untouched.

Neat-freak reconciliation was limited to the owned bridge10 QA handoff/source notes; globalAGENTS/STATUS/production documentation remain parent-owned. No git commit was made (workspace root is not currently a Git repository).

## Current endfix handoff — 2026-09-21

Accepted scope: the continuous concrete parapets, solid L-shaped bridge returns, and removal of the black end-face stripes. Root and this agent actually opened both `renders/previews/bridge10-endfix/CAM_HERO.png` and `CAM_WATER_DETAIL.png`. Broad black coplanar bands seen in the preceding `bridge10` renders are absent. This is local bridge acceptance; the forest, banks and overall photorealism remain FAIL.

Use `scene/Fallingwater_bridge10_endfix.blend`, SHA256 **2a7630b8024c37bd768e563236807f8049469172c7e44b03379a450f91637063**. Do not use historical meshclean15260 or the failed watertrim40f scene for integration. The endfix skips zero-projection broad stone panels on the four exact end planes, leaving the complete original stone core faces as the finished surface. Other stone projections keep their deterministic sequence. The south inward finished X planes remain25.43044/29.46904; all nine evaluated rays still measure4.038599014m.

Final helper: `scripts/bridge_detail10.py`, SHA256 **5176abb7b749e424918ae713baa2866ccbdef1703f9505a551f2dc1a8d736aac**. This equals the dependency recorded by the process that generated the accepted endfix. Runtime data is now `data/bridge_detail10.json`: exact77 removal names,139 retained bridge names, seven expected new names, source/candidate/helper hashes and acceptance limits. It has no runtime dependency on `qa/`.

The caller reads that JSON, verifies the helper SHA, and calls `bridge_detail10.apply(config["exact_replace_names"])` after the original terrain/bridge and accepted terrain-contact corrections exist. The four bridge foundation neighborhoods must match frozen09. Apply before final navigation/physics verification; its exact77-name and existing-new-object checks reject partial or duplicate application. To repeat, start a fresh full build or reopen the unmodified source. The caller remains responsible for comparing non-target fingerprints on a newer integration checkpoint. No production build hook was edited here. The helper's returned candidate-status string is historical; the scoped visual acceptance is recorded by the new data file and this handoff.

Endfix evidence: `bridge10-watertrim-endfix-check.json`, `bridge10-watertrim-endfix-fingerprint.json`, `bridge10-watertrim-endfix-diagnosis.json`. The comparison from historical meshclean changes only the four L-stone objects;23,311 other objects and globals are identical. Against frozen09,23,308 retained objects remain identical. Original route checks remain11,554 with zero new obstacles, all129 camera transforms remain unchanged, and the seven bridge meshes retain finite closed surfaces with no degenerate triangles. Their disconnected overlapping face-stone prisms are deliberately not claimed to be a Boolean-ready single manifold union.

The earlier endfix report's generic `BRIDGE_END_DUPLICATE_FACE` flag included narrow caps at the ends of perpendicular face stones. Fresh readback classifies these separately from the removed broad zero-projection panels; none of those broad panels remains. This corrects the diagnostic classification and does not change the accepted bridge scene or its hash.

Water remains unresolved. `bridge10-watertrim-handoff.md` records the actual implemented attempts and six-frame failure. The saved diagnostic scene `scene/Fallingwater_bridge10_watertrim.blend` (40f08d0f…) already contains the accepted endfix but also contains failed water modifiers; do not adopt it. Keep the real L masonry and unchanged old water in the next bridge checkpoint, explicitly retaining incomplete water QA. No whole-animation cache or new render was produced by this agent.
