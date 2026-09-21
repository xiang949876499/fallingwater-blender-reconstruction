# Forest canopy11 native production entry

**Native library application, full-nav10a regression and independent fresh-reopen PASS.** This accepts production reproducibility of the18-root local shape; it does not accept global environment/photo quality. No render or production build hook was changed here.

The parent accepted the18-root local shape after opening all six source/candidate images (`forest-canopy11-root-visual.md`). Overall environment/photo quality remains FAIL. The approved source is candidate11a SHA b8b46f839afa980229222be4ec92f58ad3d6c76ba88313d579a009a1a8a0c16b. Original generator and accepted candidate are preserved unchanged.

The three runtime dependencies are `scripts/forest_canopy_detail11.py`, `data/forest_canopy11.json` and `assets/models/site_canopy18.blend`. Call `forest_canopy_detail11.build(ctx, {"enabled": True})` after the final site/root seating and before route/camera validation. Default disabled returns `NOT_RUN_DISABLED`. It does not use QA data, generator fitting, source photos or the complete candidate scene at runtime. It does not expand the18-tree selection.

The JSON holds the exact36 object whitelist,18 root matrices, six original/accepted mesh mappings, strict content signatures, material-slot names, library/source hashes and acceptance limits. Runtime independently fixes the exact whitelist and accepted source identity. Wrong root, mesh, partial application, unexpected modifier/shape key or conflicting new mesh names fails before object replacement. A complete correctly applied scene returns `SKIPPED_ALREADY_APPLIED`. The material slots of loaded meshes are replaced individually with original scene material references; no material-slot clearing or per-face index regeneration occurs.

The library is exported directly with Blender native datablock serialization from the six approved meshes. No vertices, faces, UVs, leaf color indices, random seed or pruning list is regenerated. Export fake-user flags are normalized back to the original approved mesh flags on import. The strict signature retains raw edge order AND loop-edge indices, not a canonical/sorted edge equivalence. It also checks ordered positions/polygons/loop vertices, all UVs, material and smooth indices, supported named attributes (including normals/colors), and material-slot names. This wrapper did not need the weaker canonical-edge comparison used to diagnose unrelated full rebuilds.

On any append/validation failure, original object data pointers are restored, the newly appended unused mesh/material/image/group dependencies are removed, and the exception is surfaced. Only36 `object.data` values are assigned after all source and native content checks pass. No labels, locations, scales, original shared meshes or global materials are modified.

Source for current integration regression: `scene/Fallingwater_navigation_candidate10a.blend`, SHA1e7b17d9c2396513f005724e50788bf834097eedb401b91a7f1030825e2c4ed9. This includes the combined60-edge/7584-frame navigation, updated main/guest cameras and both film cameras. Physical comparison uses frame48; the stored source frame is restored before saving. The native18-canopy and accepted16-understory names/data are disjoint.

Historical negative test: attempt01 passed mesh/material/clearance checks but its test harness restored a deliberately perturbed location through `matrix_world`, causing floating-point Euler/scale decomposition differences on the first tested branch. No scene was saved. Final test restores only the same original location field; neither library nor runtime helper/signature tolerance was changed. `forest-canopy11-integration-check-attempt01.json/log` retain that failure.


## Final verification and hashes

Ready independent integration scene: `scene/Fallingwater_forest_canopy_integration11.blend`, SHA256 `dcbddb63a90f5a3ad743f23b9bfdf3c28833b69b72da37985d98c05cfa6156f4`. Source remains the frozen full navigation10a1e7b17d9…; comparison and physical tests use frame48 and saved frame73 is preserved.

- Runtime helper SHA256: `19e7b58bfd00e262eef3d508470d7323fb2f32d2d926d411567a4067d38b8c3e`.
- Data manifest SHA256: `bc5c8a738061c4f62b933ac813ca11e20384509df852bad2a7a7bece88e22780`.
- Native library SHA256: `e8b71be6374f278283148c4975835850dd80dfd4c08e1097b85091130ff82829` (8,089,899 bytes).

All36 permitted data replacements match the exact accepted six native content signatures, including raw edge and UV order. There was no canonical-edge relaxation.23,401 non-target objects, every original shared mesh and all global materials/world/light/camera/render/animation/text state remain exact. All4,800 understory objects, including the16 accepted shrub pairs, are unchanged. Material index histograms match the accepted library individually for all six meshes.

At frame48,74 protected evaluated physical hashes are identical:63 core/shoulder/old-water objects plus seven bridge objects, three path objects and the terrain. The current complete navigation route produced12,264 additional-canopy ray checks with no new hit. All131 actual saved cameras were checked at frame48; minimum new-canopy clearance is.406510m against.40m. This includes the two newly installed movie cameras and revised main/guest viewpoints.

For films, all2,880 main plus4,704 supplemental integer locations were read from the saved LINEAR fcurves and checked against the new canopy. Minimum distances were5.652802m (`CAM_TOUR`, frame1776) and3.351970m (`CAM_TOUR_SUPPLEMENTAL`, frame3553). Threshold is.13m camera-body clearance, and no location fails. The camera objects are unparented, unconstrained and have no drivers;177 segment start/middle/end dependency-graph world-matrix checks exactly matched the curve positions. This is an independent added-canopy collision regression, not a claim to have rerun every original room/navigation proof or rendered a film.

All new canopy triangles remain free of intersections with current buildings, hard path/bridge geometry and actual terrain. Root matrices are exact and actual root-to-terrain gaps remain the accepted approximately−12mm. The native module does not reseat or refit roots.

`forest-canopy11-integration-readback.json` reports `FRESH_REOPEN_NATIVE_WRAPPER_PASS`: fresh saved snapshot exact, all74 physical hashes and all six native signatures exact, repeated `build` returns `SKIPPED_ALREADY_APPLIED` with a second complete unchanged snapshot. The process did not re-save the scene. Native library inventory is six meshes/four procedural materials, with no objects, scenes, images, texts or node groups; it embeds no reference photographs or full model scene.

Evidence: `forest-canopy11-integration-check.json`, `forest-canopy11-integration-fingerprint.json`, `forest-canopy11-integration-readback.json`, `forest-canopy11-library-export.json`. Exact materials/roots/whitelist are runtime-owned in `data/forest_canopy11.json`. Runtime imports have no QA or generator dependency.

Root owns the next build hook: place the enabled call after the final site/terrain-contact pass and the16-shrub entry, before full navigation and packaging checks. The shrub/canopy order is physically independent because their whitelists and meshes are disjoint. Future altered roots/material slot names/mesh contents intentionally fail the manifest guard; do not broaden the whitelist or regenerate a replacement to bypass it. This task does not authorize wider forest changes.

Central asset/license documentation is untouched; proposed row is `qa/forest-canopy11-assets-manifest-append.csv`. Add the authored six-mesh native library to the project release inventory without distributing the separate reference-only Spring JPEGs. Original tree library, understory library, accepted11a, source10a and original canopy generator paths/names remain unchanged.

Neat-freak reconciliation is limited to owned canopy handoff/manifest/QA documentation; root retains global STATUS/AGENTS/build ownership. Negative attempt01 remains archived. No commit or CodeGraph update was made.
