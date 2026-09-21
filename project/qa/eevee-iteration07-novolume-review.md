# Iteration 07: no-VOLUME Study baseline

**Overall visual result: FAIL.** Removing the local volume path removes the earlier black wall lobes/band and dark ceiling field, but produces a strongly washed-out, flat interior. This is not a merely underlit room. The conditional AREA-fill stage was therefore **NOT_RUN**: no fill lights were added, no second image was rendered, and no GI was baked.

Actual native images opened and compared:

- [Zero-VOLUME EEVEE](eevee-iteration07-novolume/CAM_MAIN_L3_STUDY_B_NO_VOLUME_EV2p4.png)
- [Matched physical Cycles 07](../renders/previews/iteration07-focus/CAM_MAIN_L3_STUDY_B_EV2p4.png)
- Previous [one-volume practical candidate and review](eevee-iteration07-study-review.md)

The empty-volume candidate contains **zero VOLUME objects and zero VOLUME datablocks**, asserted both initially and on a fresh reopen. The frozen physical source already contained none; the candidate explicitly enumerated removal targets and verified that both counts remained zero. The standard Living SPHERE reflection capture is retained and is not a diffuse VOLUME cache.

This differs from the earlier diagnostic that set seven volumes' intensities to zero: that retained their interpolation and distant/world-padding paths. The current result supports involvement of the local volume path in the black pattern, while showing that unoccluded World/distant fallback alone is also unsuitable for this room. It does not prove which capture or interpolation subcomponent creates the black lobes.

## Actual execution

Frozen 07 source SHA: `bf50530009e4a93315915815473188c91d891272ef2d8e9e0169b704bd2e2f16`, unchanged.

Saved candidate: `qa/eevee-iteration07-novolume/Fallingwater_preview_iteration07_no_volume.blend`, SHA `a38639236bae8a08061bfc6f38218d24fe346ad476cdebdded1065f74266e3f3`.

PNG SHA: `e669ff344873de8c6b2676f9bc3f361e38c997eac3b48f9116695ece181bf7a8`.

- One render, **47.569 seconds**, exit 0; zero bakes, zero fill lights.
- Source StudyB pose and 28 mm lens, frame 48, 960×540, 32 samples, EV 2.4, AgX/None, gamma 1; preparation CPU threads 4.
- Original Sun, sky strength 0.36, ray tracing enabled, Fast GI disabled, original geometry, lights, shadow links and shadow settings retained.
- Standard thin-glass preview applied after configure; original Cycles glass branch and physical pane geometry verified unchanged.
- Every building level is NOT_BAKED. This candidate is not a complete accepted preview.
- The shutdown `Unable to delete file` warning is retained; the PNG, saved candidate, process status and source hash were checked separately.

## Comparison

The wall field is broadly bright rather than interrupted by the practical candidate's large black patches. Shelf, desk and ceiling shading lose the physical reference's enclosure and depth. Whole-image display RGB mean absolute error against Cycles is **135.774 of 255**, compared with 19.050 for the preceding one-volume candidate; neither passes visual review.

| Pixel | Zero-volume EEVEE RGB | Cycles RGB |
|---|---|---|
| Wall middle (720,275) | 184,181,167 | 50,51,42 |
| Wall upper (720,125) | 188,188,176 | 35,35,26 |
| Wall lower (710,454) | 169,165,146 | 41,45,40 |
| Ceiling (480,50) | 184,188,186 | 46,44,38 |
| Wall near shelf (320,280) | 153,149,129 | 17,16,12 |

These display-code comparisons support the actual visual inspection; they are not linear photometric measurements.

## Cycles restoration and task boundary

No preview AREA collection or additional light exists, so a fill-removal test is **NOT_APPLICABLE**, not an untested claim that a future fill helper works. A fresh-reopen check actually switches this baseline through the existing `render_views.configure_engine(..., 'CYCLES', 32, 'CPU')` path without rendering or saving. Original light names, physical parameters, poses and shadow links, Cycles glass branch and pane geometry remain unchanged. The result is in [cycles-switch-check.json](eevee-iteration07-novolume/cycles-switch-check.json).

Initial raw cross-process comparisons incorrectly included `ID.session_uid`; only those per-session identifiers differed. The failed check logs and exact differences are preserved. The corrected check excludes this single metadata key and compares every physical field, before and after switching engines. No production helper was changed for this verification.

The conditional second render was deliberately not executed because adding light would worsen the observed over-bright baseline. The parent has ended this bounded task. A separately authorized future investigation could check a small-radius Fast GI/AO approximation, after verifying the actual API options, without restoring the previous large-range behavior. That suggestion has not been implemented, tested or accepted here. All GPU work is complete and released.
