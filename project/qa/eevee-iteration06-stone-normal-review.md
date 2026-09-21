# Iteration 06 stone shading-normal discriminant

**FAIL as a fix: disabling the active stone Bump strength does not remove the large wall lobes or ceiling bands.** The displayed image barely changes. Retain the original stone relief; do not adopt this zero-strength diagnostic.

One 960×540, 32-sample image was rendered from the separately reopened practical candidate, `eevee-iteration06-practical/Fallingwater_main_l3_coverage_candidate.blend`, SHA-256 `cee741ac1c25c84f487c4967158a4c29bb3552871102338442f9b9fc85488ebf`. It uses the same saved `CAM_MAIN_L3_STUDY_B` pose, 28 mm, frame 1, EV+2.4 and four CPU preparation threads. Ray tracing remains on and Fast GI off. Render time **63.041 seconds**, process exit 0. The candidate PNG was actually opened at native size and compared with the already inspected practical baseline.

The only change is `FW_stone → Bump.001 → Strength: 0.5→0.0`. The node is on the active surface path: `PH_Displacement.Color → Bump.001.Height → Principled BSDF.Normal`. Its Distance remains 0.02199999988 m, and all image, color, roughness and link inputs are retained. The original stone graph was compared against the result after normalizing exactly this one input; no other graph difference was allowed. All other material graph hashes, light settings and shadow links, probe data and matrices, and object transforms/render visibility were unchanged. Original Cycles glass shader and glazing geometry hashes were also retained.

**No GI rebake and no scene save occurred.** This is a shading-normal test against the existing cache, not a test of normals used when that cache was captured. The unsaved stone surface edit is engine-independent in memory; no original Cycles material file was changed. This result rejects zeroing the current Bump strength as the standalone fix, but does not prove that the baked SH, capture normals, validity or propagation are correct.

| Pixel, top-left origin | Practical baseline RGB | Bump-zero RGB |
|---|---|---|
| (720,275), middle wall | 5,4,3 | 5,4,3 |
| (720,125), upper wall | 34,36,31 | 33,35,31 |
| (710,454), lower solid wall | 25,25,20 | 25,25,20 |
| (600,60), ceiling | 7,8,8 | 7,8,8 |
| (350,230), left wall | 1,1,0 | 1,1,0 |

Whole-image mean absolute difference is **0.121159/255 display RGB code values**. The large dark pattern remains in its original position and shape. This metric is a display comparison, not a linear-light or perceptual acceptance score. The separate narrow bottom bright strip is still visible; the parent's physical Cycles images also retain it, and its architectural cause is outside this material test.

PNG: `eevee-iteration06-stone-normal-zero.png`, SHA-256 `9fe1073e75e9157cd13b7e1bd85bd6aa1f8aaddf8acef4b48d5809234374272d`. Settings, full before-stone graph and all material graph hashes are in its `.json`; execution is recorded in `eevee-iteration06-stone-normal.log`. The log retains Blender's shutdown `Unable to delete file` message; the PNG decoded and hashed correctly, and the source file remained unchanged.

The frozen practical source, original06 preview, physical06 scene and helper sources were not altered. Only one image was rendered, without additional exposure variants or follow-on candidates. GPU work is complete and released. Further architectural changes require new cache preparation and must not be conflated with this frozen-source result.
