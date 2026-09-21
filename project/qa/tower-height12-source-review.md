# Tower 12 — HABS height endpoint review

2026-09-21 · `/root/site_visual` · **READ_ONLY_COMPLETE; model unchanged; one anchor proposed, not adopted**.

The `MAIN TOWER 32′9½″` witness line is level with the **upper outline of the continuous masonry/coping course**. Independently raised flue outlets and cowls are visibly above it. The nominal value must therefore not be measured to the highest flue. The same section names the lower reference **MAIN LEVEL TERRACE 0′0″**. In the frozen model, the closest continuous-top counterpart is `MAIN_chimney_cap`, at world Z 9.56000042 m. Its nominal discrepancy is approximately **−0.435 to −0.457 m**, depending on the explicitly chosen model terrace datum; both options fail the existing nominal tolerance convention.

## Source and what was actually read

- Primary drawing: HABS PA-5346, main-house sheet 10, **Section Looking West**. [LOC record](https://www.loc.gov/pictures/item/pa1690.sheet.00010a/), [original TIFF](https://tile.loc.gov/storage-services/master/pnp/habshaer/pa/pa1600/pa1690/sheet/00010a.tif). Live record access returned HTTP 403 during this review; the previously downloaded and registered original was read locally.
- Local original: `research/references/architecture/main-10-original.tif`; 30,171,041 bytes; SHA256 `db6591996c049961a50ba593c002dc394d5708f1c15c5935e1c3671aed1e2ac7`.
- The stored image is 13632 × 17702, 1-bit, EXIF orientation 8. In this decoder the flag disappears on load without rotating dimensions. A 90° clockwise rotation produces the correctly oriented 17702 × 13632 image, independently checked against the official small JPEG. EXIF-only counterclockwise rotation was rejected after actual viewing. The original TIFF was not changed.
- All nine final crops were actually opened. Native crops preserve original pixels; only the named context overview is resized. Crop coordinates, hashes and viewed records: [crop manifest](D:/zx/test/project/qa/tower-height12-source-crops.json). No generated imagery or image editing was used to fill source evidence.

**A: printed nominal labels.** Tower 32′9½″ = 9.9949 m; main-level terrace 0′0″. The image does not label a separate named cap slab, prescribe its construction material, or call the raised flue the tower datum.

**C: graphic endpoint interpretation.** Continuous top course and witness line align within original line thickness; outlets rise above them. Calling the visible row masonry/coping and mapping it to the current model's `MAIN_chimney_cap` are source-to-model interpretations, not model names printed on the source.

Reproducible original-image locators, after the verified clockwise rotation:

| Feature | Native X window | Native peak ink Y | Interpretation |
|---|---:|---:|---|
| Continuous coping upper edge | 8231–10431 | 7637–7638 | Upper outline of continuous stone course |
| Tower witness line away from stonework | 11122–14322 | 7636 | Same elevation within line thickness |
| Main terrace zero witness | 14485–15785 | 10839–10840 | Explicit lower datum label |

These are reproducible visual locators, **not pixel-derived metre measurements**. The metric target comes from the printed dimension. The high-resolution top crop shows the independent raised outlets plainly. See [top crop](D:/zx/test/project/qa/tower-height12-source-tower-top-native.png), [label crop](D:/zx/test/project/qa/tower-height12-source-tower-line-label-native.png), [witness-line crop](D:/zx/test/project/qa/tower-height12-source-tower-line-middle-native.png), and [context](D:/zx/test/project/qa/tower-height12-source-west-section-context-overview.png).

## Date is separate from dimension evidence

The museum's current primary research page says the as-built drawing collection was completed **circa 2010**. This independently confirms the existing collection-level dating, not an exact date for this sheet. [Official architectural drawing guidance](https://fallingwater.org/learn/preservation-and-collections/research-resources/architectural-drawings/)

- Collection date: **circa 2010**, museum/catalogue context (B), independently reopened 2026-09-21.
- Exact sheet-10 survey/drawing date: **UNKNOWN**. No legible exact date was found in the inspected title crops.
- Local retrieval date: 2026-09-20; this is not a survey date.
- Main sheet 1's visible `1934–1939` belongs to building/design history. It is not promoted to the HABS survey date.
- Absolute as-built surveying accuracy: **UNKNOWN**. A nominal drawing match is not proof of actual-site millimetre accuracy.

## Actual saved surfaces and the 22 mm datum issue

Read-only, fresh Blender 5.2.1 CPU4 process; frame 48; source `Fallingwater_iteration10.blend`, SHA256 `1e7b17d9c2396513f005724e50788bf834097eedb401b91a7f1030825e2c4ed9`. The process did not save or render, and source SHA was unchanged. Measurements select actual evaluated upward horizontal faces, rather than object origins or guessed dimensions. [Complete mesh probe](D:/zx/test/project/qa/tower-height12-source-mesh-probe.json)

| Actual surface | World top Z (m) | Role |
|---|---:|---|
| `MAIN_chimney_cap` | 9.560000420 | Proposed continuous upper silhouette counterpart |
| `MAIN_stone_tower_west`, `_north` | 9.460000038 | Underlying structure; not the upper continuous course |
| `MAIN_chimney_flue`, `.001` | 9.600000381 | Raised outlets; excluded from tower nominal endpoint |
| `MAIN_L1_TERRACE_W_finish`, `_E_finish` | 0.0219999999 | Actual visible terrace finish |
| `MAIN_L1_TERRACE_W_slab`, `_E_slab` | 0.000000000 | Actual structural slab top |
| `MAIN_L2_TERRACE_S_finish` / `_slab` | 2.866800070 / 2.844799995 | Demonstrates the finish offset |
| `MAIN_L3_TERRACE_finish` / `_slab` | 5.286149979 / 5.264150143 | Demonstrates the same finish offset |

The existing dimension table mixes conventions: `MAIN_LEVEL_2` uses actual finish-to-finish faces; `MAIN_LEVEL_3` and `MAIN_ROOF_WEST` currently use slab-to-slab faces. The generated model calls world zero the main terrace datum and adds a 22 mm finish. Therefore the earlier progress inference that every existing height uses the finished datum was too broad. This review explicitly corrects that inference.

The drawing confirms the main terrace datum, but does not independently justify the model's extra 22 mm finish layer or the split in table conventions. The visible terrace surface is the preferred semantic correspondence for a new finished-top anchor (C). Keep the structural convention visible as an alternative until the integrator resolves the model-wide datum policy; do not silently switch endpoints to improve a score.

| Lower model face | Cap-to-datum actual (m) | Printed nominal (m) | Error (m) |
|---|---:|---:|---:|
| Actual visible finish, Z 0.022 | 9.538000420 | 9.994900000 | −0.456899580 |
| Existing structural datum, Z 0 | 9.560000420 | 9.994900000 | −0.434899580 |

Both discrepancies exceed `max(0.020 m, 0.005 × nominal)` = **0.0499745 m**. The 22 mm datum issue is material to consistent bookkeeping but cannot explain away the much larger tower shortfall. Measuring to the flue would change the wrong endpoint; it would not repair the dimensional evidence.

The local tower12 surface candidate preserves the five tower structural objects. Its prior exact readback and 79 protected physical checks therefore preserve these same tops. Candidate SHA remains `b267636a9cbbe297513968f08f3b85930c0302cae1ebb75ed775043250e11a48`; this task did not reopen it for mutation, alter its geometry, or replace the root's visual review.

## One independent anchor proposal

Proposed ID: `MAIN_TOWER_CONTINUOUS_COPING_RELATIVE_MAIN_TERRACE`. It is not currently present in `dimensions.csv`. This is one new vertical extent, not a count of several cap corners or repeated terrace stations. [Machine-readable proposal](D:/zx/test/project/qa/tower-height12-source-anchor-proposal.json)

- Upper: `MAIN_chimney_cap`, evaluated polygon 1, upward normal `(0,0,1)`, vertices `[4,5,6,7]`. Centroid `(-0.340599984, 9.982799530, 9.560000420)` m. Upper outline/continuous coping correspondence: C.
- Preferred lower: `MAIN_L1_TERRACE_W_finish`, evaluated polygon 1, vertices `[4,5,6,7]`. Centroid `(-2.384199858, 2.283299923, 0.0219999999)` m. Same source terrace-zero correspondence: C.
- Structural alternative: the same upward face of `MAIN_L1_TERRACE_W_slab`, Z 0; its mixed-convention rationale and separate result are preserved in the proposal.
- Method: subtract the measured horizontal face elevations. These faces need not be vertically superposed in XY; this is a relative elevation check. Confirm east terrace gives the same datum; do not count it as a second anchor.
- Status: **nominal FAIL for either stated datum; absolute survey accuracy UNKNOWN**. The central table remains unchanged. Do not automatically stretch only a cap slab or promote the flue as a replacement endpoint.

The next height correction, if authorized separately, needs a coordinated tower/coping/outlet design with a declared terrace datum. It must retain the distinction between a printed nominal target and the C reconstruction of masonry/course/cap construction.

## Scope reconciliation

The `neat-freak` closeout is confined to this task's QA ownership: crop viewed flags reconciled, original source and endpoint evidence linked, earlier datum inference corrected in this report, and one explicit anchor proposal written. No changes were made to `AGENTS.md`, global memory/settings, `dimensions.csv`, production modules, shared materials, candidate scenes, working scene, cameras or renders. Earlier tower12 geometry/visual evidence remains intact.
