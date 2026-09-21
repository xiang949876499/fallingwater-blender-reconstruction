# Daylight and exposure calibration

The original hero image was underexposed, and living-room camera A was almost black. Replacing the old sky model with a **multiple-scattering atmospheric sky** and retaining a single matching direct Sun improved window illumination. Camera-specific photographic exposure then made interior surfaces readable without adding unmotivated fill lights.

All comparisons use the actual combined building/site geometry saved in `scene/Fallingwater_working.blend` (23,176,743 bytes, saved before subsequent geometry fixes). The inspected A camera's center/edge rays first hit surfaces 3–13 m away, so immediate camera intersection was not the cause of its black frame. No geometry was moved or removed during lighting work.

## Selected daylight setup

`scripts/lighting.py` provides `build(scene, rooms=None)`, `apply(scene, preset='DAYLIGHT')`, and `apply_camera_exposure(scene, camera)`.

- Sky: Blender 5.2 `MULTIPLE_SCATTERING`, strength **0.12**, air density 1.0, aerosol density 1.5, ozone density 1.0, ground albedo 0.22 and altitude parameter 350 m. These are rendering choices, not surveyed atmospheric conditions.
- Solar elevation **47°**, rotation **235°** in the model coordinate frame; one Sun at energy **2.5**, angular diameter setting **2°**, color `(1.0, 0.96, 0.89)`. The sky's own solar disc is disabled, so a second direct Sun is not added. Model direction is not asserted to be an exact geographical date/time reconstruction.
- AgX, scene baseline exposure **+0.8 EV**. Preserve the same scene illumination for all daylight viewpoints.
- Only existing visible bedroom lamp diffusers receive warm emission, strength 1.5 for daylight. Their object names are recorded in the lighting result JSON. There are no additional giant invisible area lights, emissive room fills or floating sources. In particular, the living room is illuminated by real openings and reflected sky/Sun light.
- Minimum light-path settings in the module: 12 total, 6 diffuse and 8 transmission bounces. These support multi-bounce window illumination; the change does not claim that extra bounces alone fixed the exposure.

| View | Selected exposure | Reviewed image |
|---|---:|---|
| Exterior hero | +0.8 EV | `lighting01/CAM_HERO.png` |
| Living A, toward interior walls | +3.2 EV | `lighting02/CAM_MAIN_L1_LIVING_A_EV3p2.png` |
| Living B, toward glazing | +2.4 EV | `lighting03/CAM_MAIN_L1_LIVING_B_EV2p4.png` |

These three camera objects receive `fw_exposure` defaults only when they do not already have an explicit value. The renderer must call `apply_camera_exposure` before each image and record the actual exposure. Other cameras retain the scene baseline until inspected; this is intentionally not a claim that every room has been calibrated. For a continuous tour, exposure changes should be gradual and separately checked, rather than snapping between static-view values.

Living-A +2.4 EV remains dark, whereas +3.8 EV lifts surfaces further but flattens floor/ceiling separation. Living-B +3.2 EV is unnecessarily bright near the glazing; +2.4 retains visible outside tree and ground contours. Applying +3.2 to the exterior visibly washes out the building, demonstrating why the interior correction is not a global lighting increase.

## Actual tests

The initial preview process had fully quit before these tests began. Three small test groups were rendered sequentially on HIP at **640×360, 16 samples**, with AgX and denoising:

| Group | View / runtime | Record |
|---|---|---|
| 1 | Hero 54.999 s; Living A 52.874 s | `lighting01/lighting-results.json`, `lighting01.log` |
| 2 | Living A 54.094 s; same linear result exported at +2.4, +3.2, +3.8 | `lighting02/lighting-results.json`, `lighting02.log`, linear EXR |
| 3 | Hero 48.608 s; Living B 45.476 s; same results exported at +0.8, +2.4, +3.2 | `lighting03/lighting-results.json`, `lighting03.log`, linear EXRs |

Exposure brackets were exported through Blender from the same scene-linear Render Result, not repainted or relit independently. The last group enabled Persistent Data, but the camera workloads differ; this does **not** establish a causal speedup or a final-animation throughput claim. A controlled repeated-frame benchmark remains necessary before planning thousands of frames around assumed caching gains.

The worker actually opened the original hero/A images, the physical-sky hero/A images, all three A exposure brackets, B's +2.4/+3.2 images, and the deliberately over-bright +3.2 hero comparison. `lighting-metrics.json` additionally records display-referred statistics: living-A pixels below display luma 0.03 decreased from approximately **86.65% to 0.11%**, and selected living-B pixels above 0.98 are approximately **0.41%**. These diagnostics support the exposure finding, not objective photographic realism or measured illuminance.

`lighting-verification.json` records a no-render repeated-apply check: mesh names/vertex/polygon counts remain unchanged, the second application does not duplicate objects, and only the new physical Sun is active as a light object. Original lamp mesh emission remains a separately listed source. `lighting-final-preview.blend` is a diagnostic copy with hero as its opening camera; the production scene was not overwritten.

## Remaining limits

This is a successful correction of the demonstrated dark-lighting problem at preview size. The scene still visibly needs architecture, furniture, forest, water and material refinement. **Photographic visual acceptance is not passed.** Sixteen-sample preview denoising does not establish final detail/noise quality. Retest these exposures after any window, wall, vegetation or material change; the present evidence predates later geometry fixes.

An `EVENING` preset is supplied as a documented starting setup but was not rendered during this bounded task and remains **NOT_RUN**. It uses `fw_exposure_evening` only when a separately calibrated camera value exists, rather than silently reusing daylight interior exposure. Other rooms, detail cameras, 4K crops, final multi-view reference matching and the continuous tour remain to be verified by the main task.
