# Iteration 06 MAIN_L3 Z coverage candidate

**FAIL: extending only the vertical volume coverage changes the bright bands substantially, but does not produce continuous, physically plausible Study lighting.** The large middle region becomes too dark and the strong left-side bright/dark division remains. The candidate is preserved separately and must not replace production06.

The candidate, existing EEVEE baseline and parent's Cycles reference were all opened at native 960×540. All use `CAM_MAIN_L3_STUDY_B`, saved pose, 28 mm, frame 1, EV+2.4; the two EEVEE views use 32 samples. The candidate used four CPU preparation threads. No other view, exposure bracket, lamp change or second candidate was rendered.

## What actually changed

| Item | Before | Candidate |
|---|---|---|
| MAIN_L3 volume bounds X | −4.027600 to 8.907660 m | Same |
| Bounds Y | 11.425800 to 24.592747 m | Same |
| Bounds Z | 5.384150 to 7.184150 m | **4.514150 to 8.100000 m** |
| Grid resolution | 10×10×4 | Same |
| Nominal sample spacing X/Y | 1.175933 / 1.196995 m | Same |
| Nominal sample spacing Z | 0.360000 m | **0.717170 m** |
| RNA surfel density | 8 | Same |
| Maximum object scale | 6.583473 m, Y axis | Same |
| Physical surfel interval/radius | 0.822934 / 0.411467 m | Same |
| Surface-bias distance after internal scale conversion | 0.011250 m | **0.022412 m** |
| Escape-bias distance after internal scale conversion | 0.022500 m | **0.044823 m** |

The evaluated stone core wall extends from Z=5.264150 to 7.600000. The actual Study ceiling mesh spans Z=7.384150 to 7.402150, above the room metadata ceiling at 7.304150. The candidate adds 0.75 m below the wall/floor datum and 0.50 m above its top. This gives the sampled upper/lower wall and ceiling space inside the padded capture grid; a 0.12 m adjustment would leave them near its blending border.

Only the probe object's location Z and scale Z changed. Every object's transform/render visibility was compared; the only differing object was `FW_PROBE_MAIN_L3`. Every scalar probe property, all light properties and shadow-link collections, original Cycles glass surface and glazing geometry signatures were retained. Fast GI remained off, ray tracing on, every real light shadow flag on, and only the previously saved Bath filament exclusion remained active. The other six VOLUME transforms and settings did not change. The cache operator was called exactly once with only MAIN_L3 selected and `subset='ACTIVE'`; the other six were not requested for rebaking. Their hidden cache byte arrays were not independently hashed.

Preserving RNA settings does not preserve every derived scale. At four fixed Z samples, the nominal Z locations and spacing change; geometry/validity sampling therefore changes too. Blender converts surface and escape biases with `min(object scale / resolution)`, so the effective distances in the table increase. Normal bias remains 0.3 grid units: its physical Z offset for a horizontal surface increases from about 0.108 to 0.215 m; its Y offset on the inspected wall is unchanged. A one-cell dilation radius also spans a larger vertical interval. In contrast, **surfel density really is unchanged in world space**, because the largest XY scale remains fixed. These coupled effects mean this is a bounds-and-resulting-lattice test, not an isolated measurement of world blending. [Blender 5.2.1 scale conversions](https://raw.githubusercontent.com/blender/blender/v5.2.1/source/blender/draw/engines/eevee/eevee_lightprobe_volume.cc).

The expanded Z range overlaps MAIN_L2's existing bounds over approximately 0.381 m. Only Study was rendered, so effects on lower-floor transitions are not accepted or ruled out. No global coverage default was changed.

## Observed result

Single ACTIVE bake: **41.593 seconds**, operator FINISHED. Single render: **22.362 seconds**. Process exit 0. The PNG and separate candidate blend were saved. Blender's shutdown `Unable to delete file` message is retained in the log; no output was deleted or assumed missing.

| Display pixel, top-left origin | Baseline RGB | Candidate RGB | Cycles RGB |
|---|---|---|---|
| (720,275), middle wall | 35,31,20 | **8,7,4** | 27,26,19 |
| (720,125), upper wall | 141,143,129 | **36,38,33** | 19,17,10 |
| (710,454), lower solid wall | 135,135,119 | **22,21,16** | 30,27,20 |
| (600,60), ceiling | 128,135,134 | **21,22,21** | 26,23,17 |
| (350,230), left wall area | 91,87,71 | **86,82,68** | 7,5,2 |

Upper/lower wall and ceiling become much closer to the dark physical reference at these pixels; the middle wall becomes darker than the reference. The left wall remains greatly overbright. Whole-image mean absolute difference from the original EEVEE image is 44.725/255 display RGB code values. These are display comparisons, not irradiance calibration or perceptual acceptance scores.

The vertical change clearly moves/removes much of the former upper/lower overbrightness, supporting coverage/lattice involvement. It does not remove the broad horizontal discontinuity. The subsequent original-bounds density8→32 test also failed: local shading changed but the large rectangle remained; see `eevee-iteration06-density-review.md`. A separate narrow bright bottom strip persists in the parent's physical Cycles images at both tested sky strengths; its geometric cause was not diagnosed here and it must not be classified solely as an EEVEE artifact. Neither adding fill lights nor adopting this partial coverage candidate is justified.

## Metadata-only helper correction

`eevee_preview.py` now reports `(high-low)/(resolution+1)`, matching Blender 5.2.1's nominal padded-grid sample formula. This changes reporting only; probe placement/resolution/bake behavior are unchanged. The assignment was evaluated against adjacent nominal sample centers inspected through Blender's matrix API for all seven saved probes; all matched within 5 micrometers. The official sampling formula was also checked. [Blender 5.2.1 sample positions](https://raw.githubusercontent.com/blender/blender/v5.2.1/source/blender/draw/engines/eevee/shaders/eevee_lightprobe_volume.bsl.hh).

Removing exactly the two new comments and reverting this denominator from the current helper reconstructs its previous SHA-256 `eab1810e58b0708196d0028d283068deb174bdf2871c3ee22ba6da4be7ddc149`. This independently verifies that no other helper content changed. Current helper SHA: `f68abbfde2ff6164618486a0df078bb144311e78482bfd794d15568d3b6803cd`. `eevee_glass.py` is unchanged. Evidence: `eevee-iteration06-spacing-check.py/json`.

## Artifacts and completion boundary

| Artifact | SHA-256 |
|---|---|
| Original independent preview, unchanged | `e317241899808995f049e8d3343eac96c591cbecfddaa980949d6babb51ccce6` |
| Physical Cycles06 source, unchanged | `172b76340d1224a2b98f415b21042d19ad7fba4d849543d7156beb17e5fcf055` |
| `eevee-iteration06-coverage/CAM_MAIN_L3_STUDY_B_EV2p4.png` | `96f73cbd0cc123f39c1e4390a29561931c739c7e1deb6a4e9d34a205aa55ab99` |
| `eevee-iteration06-coverage/Fallingwater_study_coverage_candidate.blend` | `a2664c378383385bcf5ac9154b579c53793b31b5051cb39e1b6eeb49035f9e1c` |

Full before/after light, probe and object differences are in `eevee-iteration06-coverage/report.json`; execution evidence is `eevee-iteration06-coverage.log`. The candidate preserves original seven-bake provenance and writes separate `fw_eevee_study_coverage_candidate_json` / scope properties for the replaced MAIN_L3 bake, so it does not claim the old bounds remain current. No production source, renderer, model or global settings were overwritten. The bounded task is complete and the GPU is released; whole-scene and motion acceptance remain open.
