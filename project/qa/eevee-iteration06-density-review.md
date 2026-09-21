# Iteration 06 MAIN_L3 density-only candidate

**FAIL: surfel density 8→32 modestly changes captured illumination, but the broad Study wall rectangle and overbright surrounding regions remain.** Higher density alone is insufficient to resolve this defect. The independent candidate is retained; no production density or coverage default was changed.

## Controlled scope and result

The frozen source is `scene/Fallingwater_preview_iteration06.blend`, SHA-256 `e317241899808995f049e8d3343eac96c591cbecfddaa980949d6babb51ccce6`. This experiment reopened the original source, not the preceding expanded-Z candidate. Only `FW_PROBE_MAIN_L3.data.surfel_density` changed, from 8 to 32. The active probe alone was baked once. One `CAM_MAIN_L3_STUDY_B` image was rendered at its saved pose, 28 mm, frame 1, EV+2.4, 960×540, 32 samples and four CPU preparation threads. No exposure bracket or other camera was rendered.

MAIN_L3 retains bounds X[−4.027600,8.907660], Y[11.425800,24.592747], Z[5.384150,7.184150] m and resolution 10×10×4. Nominal spacing remains 1.175933 / 1.196995 / 0.360000 m. The physical surfel interval decreases **0.822934→0.205734 m**; radius decreases **0.411467→0.102867 m**. Effective surface bias remains 0.011250 m and escape bias 0.022500 m. Intensity, capture distance, all biases, validity/dilation, bake samples and capture options are unchanged.

Every object's transform/render visibility and all light settings/shadow-link collections were compared and retained. Other probe properties, including every setting of the other six volumes and the Living SPHERE, were unchanged. Fast GI stayed off, ray tracing on, every real light shadow flag on, with only the saved Bath filament exclusion active. Original Cycles glass shader and glazing geometry hashes match. The cache operator used only MAIN_L3 selected, `subset='ACTIVE'`; six other caches were retained, not requested for rebaking. Their internal cache arrays are not exposed for an independent byte-level comparison.

The single bake returned FINISHED in **34.229 seconds**. The single render completed in **22.415 seconds**; process exit 0. The new image was opened at native resolution and compared with the already opened matching baseline and parent's physical Cycles image. The rectangle remains in the same place; its middle becomes slightly brighter and local furniture shadows change. The upper, lower and left surrounding bright regions remain almost unchanged.

| Pixel, top-left origin | Baseline RGB | Density32 RGB | Cycles RGB |
|---|---|---|---|
| (720,275), middle wall | 35,31,20 | 40,36,26 | 27,26,19 |
| (720,125), upper wall | 141,143,129 | 141,143,129 | 19,17,10 |
| (710,454), lower solid wall | 135,135,119 | 134,135,119 | 30,27,20 |
| (600,60), ceiling | 128,135,134 | 128,135,135 | 26,23,17 |
| (350,230), left wall area | 91,87,71 | 91,87,70 | 7,5,2 |

Mean absolute full-image difference is **2.823/255 display RGB code values**. This is not a linear irradiance measurement. The result demonstrates some local sensitivity to capture density, but does not support coarse surface capture as a sufficient explanation or standalone cure for the large rectangular contrast. It also does not establish corrupted cached normals. The separate narrow bottom strip persists in the parent's physical Cycles images at two sky strengths; its geometric cause remains outside this diagnosis.

## Resource preflight and actual execution

The first preflight stopped before baking. It conservatively multiplied entire overlapping mesh areas by the largest object scale squared and added a per-triangle boundary allowance. On this scene, nonuniform transforms and the large terrain made that estimate impractically loose: approximately 127 GiB against an 8 GiB planning guard. This was an estimation failure, not an observed Blender allocation failure. The original script, STOPPED report and log remain as evidence.

A separate read-only refinement used actual world-space triangles and rejected triangles whose bounding boxes miss the capture box. It examined 10,014 evaluated meshes with 6,654,572 vertices and 7,067,759 triangles; 4,210,107 triangles overlap the capture box. Their retained full areas sum to 22,716.22 m², and their three-axis projected areas to 25,954.76 m². Crossing triangles were not clipped, so their complete area is conservatively included. The four empty meshes included by the first estimate add no triangles.

At 4.860656 surface samples per meter, projected area predicts about **613,207 surfels**. Blender's packed structure fields total 224 bytes per surfel, giving approximately **131 MiB** for the principal buffer. A sixfold planning allowance—twice the count for uncertainty and three times the buffer work—was **786 MiB**, below the 8 GiB guard and the 35.90 GiB physical memory available when execution began. This is a planning estimate, not a rigorous bound or measured GPU peak. [Blender 5.2.1 Surfel structure](https://raw.githubusercontent.com/blender/blender/v5.2.1/source/blender/draw/engines/eevee/eevee_lightprobe_shared.hh).

The formal bake/render completed without a resource failure. An OS process observation after baking, during rendering, reported working set 4,839,276,544 bytes and peak-to-that-observation 6,042,456,064 bytes (about 5.63 GiB). These are process working-set figures, not total GPU allocation or a guaranteed final peak. The shutdown log contains the same `Unable to delete file` message as prior successful jobs; output and source hashes were checked, and no evidence was deleted.

## Preserved artifacts

| Artifact | SHA-256 |
|---|---|
| `eevee-iteration06-density/CAM_MAIN_L3_STUDY_B_EV2p4.png` | `05ae3c534e337079341d1c382c5b3e276e09f3649a6bb9fb27c3a9d4cba4455b` |
| `eevee-iteration06-density/Fallingwater_study_density32_candidate.blend` | `ee743bddd6febb3fa7a91a2d25c2c6768e504d8860ad91c080fc876fb33c94e1` |
| Original preview, unchanged | `e317241899808995f049e8d3343eac96c591cbecfddaa980949d6babb51ccce6` |
| Physical Cycles06 source, unchanged | `172b76340d1224a2b98f415b21042d19ad7fba4d849543d7156beb17e5fcf055` |

Detailed invariants, pixel comparison and settings: `eevee-iteration06-density/report.json`. First rejected estimate: `report-initial-preflight.json` and `eevee-iteration06-density.log`. Refined estimate: `preflight-refined.json` and `eevee-iteration06-density-preflight-refine.log`. Completed execution: `eevee-iteration06-density-run.log`. The candidate keeps separate `fw_eevee_study_density_candidate_json` and scope properties for its replacement MAIN_L3 cache.

No helper was changed by this density test; the separately verified spacing-metadata correction remains in `eevee_preview.py`. The two independent tests reject their individual fixes: vertical coverage affects the edge positions substantially, while density32 mostly changes local shading. Both remain failed candidates. The later separately authorized practical XYZ margin/resolution/density candidate is documented in `eevee-iteration06-practical-review.md`; it reduced overbrightness but also failed overall. No production change or whole-scene acceptance is claimed by this density test.
