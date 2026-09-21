# Structure09b — Coat/Loggia corner and Alcove west floor

**Scoped geometry verified; visual acceptance awaits the integrator's two original-camera renders.** Five existing meshes changed, no objects added or removed. Guest stairs, tour, furnishings, camera/light state and other architecture were not edited. The candidate is derived from frozen structure09, so its furniture remains that input's state; the integrator will combine the independently tested softgoods revision separately.

Candidate: `scene/Fallingwater_structure_candidate09b.blend`

SHA256: `852b4f3c50ed7530bbba0f9957e2af4e4717496a4129a9169d17a234c86665a1`

Frozen `scripts/main_house.py` SHA256: `d80558f5780773f8f3b2e8324dea32da616500958c83a70d7637a9e3fc180caf`.

Unmodified input `scene/Fallingwater_structure_candidate09.blend` SHA256: `4fa1fc1f56795a2da88c97bacc9bd3b2a0730d3d085076173425b00addd744a0`. Frozen08, the first09 failed candidate and all their reports remain unchanged.

## Source classification and the bounded changes

Actual main04 native TIFF and the original main06 JPEG were opened. Their annotated boundaries are in `structure09b-main04-boundary.png` and `structure09b-main06-boundary.png`; the unmarked native main04 crop is also retained. Main06's official TIFF request returned HTTP403. No alternative image was fabricated; its approximate inner face is C with about one source-pixel uncertainty, not a high-resolution measurement. The independent source reader reached the same Alcove classification and then finished.

The Loggia_A image point(638,373) projects onto the L1 plane at source(534.767523,300.727694). Main04 places it within the continuous hatched eastern/southern Coat stone corner. The old model's east face ended atx531.3855, short of the drawn outer face nearx535. The area directly south of this corner is drawn stone paving, not a lower stair opening.

- `MAIN_L1_coat_1`: retain the old west inner face; extend the outside to the C source trace x535.05 and south endy301.56, with unchanged Z0.1..2.5. Its polygon excludes the part already supplied by `coat_2`, reducing a pre-existing coplanar cap overlap. The existing7mm edge bevel is explicitly preserved in production and candidate. Plan area0.292050→0.510170m².
- `MAIN_L1_LOGGIA_slab/finish`: add only the front junction to the existing threshold and actual northern wall inner face, with a5mm wall lap. The exact threshold diagonal/northern edge remains shared. Area10.542664→10.843698m², a **0.301034m²** addition at unchanged floor/finish Z0.1/0.122.
- `MAIN_L3_ALCOVE_slab/finish`: extend the west edge fromx435 to approximatelyx432 overy259..291. This **0.267116m²** strip lies east of the source stairwell and contains target(433,265). Keepx<432 open. Belowy291 the existing Gallery and threshold retain their shared boundaries, avoiding coplanar floor duplication. Z5.26415/5.28615 unchanged.

The source geometry identity is stronger than the numerical tracing accuracy: the stone corner is solid, the Loggia junction is paved, and the Alcove strip lies east of the stairwell. None of the selected decimal tracing coordinates is promoted to a surveyed A dimension.

## Actual checks and results

`structure09b-candidate-check.json` contains the input/after object fingerprints, all surface samples, original camera rays, opening controls, nearby stair tests, doorway support comparisons and sampled camera/route-body comparisons. A separate Blender process then reopened both frozen09 and the candidate and wrote `structure09b-reopen-validation.json`. Both processes used CPU4 and `--python-exit-code1`; no render was started by this agent.

| Check | Actual result |
|---|---|
| Five modified meshes rebuilt from current source, including evaluated7mm bevel | Same vertex/face counts and topology; maximum vertex error0m |
| All non-target scene object geometry/transforms/material slots/camera/light parameters | Fingerprints identical to4fa input |
| Candidate saved resolution, frame range/current frame, active camera and rendering settings | Identical to4fa input |
| Entire old/new floor extents and dense added-strip samples | **12,222 samples**, each has exactly one finish at its expected height |
| Existing camera and sampled route body points against changed meshes | **8,082 points**, no new0.18m proximity collision |
| Nearby main stair1/stair2 actual tread center and transverse controls | **90 samples**, supported with headroom≥1.95m |
| Existing24 threshold paths,31 support positions each | **744 samples**, no newly lost ground support |
| Stone caps, exact top/bottom planes across old and new Coat junction | **54,384 samples**, zero newly introduced coplanar locations; old repeated hits1,764→882 |
| Actual stair opening controls west ofx432 | Same original tread/underlying hits, no new upper floor cap |
| Walking/opening ceiling controls | Existing hit/object/height preserved |

These are scoped geometry regressions, not a new60-edge or7584-integer-frame global navigation acceptance. The remaining cap duplicates are the old northern junction; this task removes the southern overlap but does not silently expand its scope to rebuild all Coat walls.

The first checking process intentionally stopped at a failed blanket ceiling assertion. The source-classified solid point inside the extended masonry now looks upward to the wall's own top, whereas it previously saw the upstairs slab through the missing stone. Requiring its old free-ceiling hit was a category error. The failed script, report and log are preserved as `structure09b-initial-assertion-fail.*`. A separate actual reopen verified the occupied-stone classification and retained unchanged ceiling requirements at every walking/opening control. No geometry was changed to make that assertion pass; the candidate was not resaved.

## Original cameras and visible boundary evidence

Use the unchanged cameras **`CAM_MAIN_L1_LOGGIA_A`** and **`CAM_MAIN_L3_ALCOVE_B`**, at their existing framing and exposure.

| Target | Actual candidate ray / projection at960×540 |
|---|---|
| Loggia(638,373) | Previously terrainZ−3.25; now `MAIN_L1_coat_1` east sideZ0.130082 |
| Loggia new paving source(534,304) | Visible `MAIN_L1_LOGGIA_finish` atZ0.122, pixel≈(605.1,376.0) |
| Alcove source(433,265) | Visible `MAIN_L3_ALCOVE_finish` atZ5.28615, pixel≈(148.3,478.9) |

The old stone-control pixelLoggia(615,359) still hits stone, now the corrected southern face; it is not falsely counted as an earlier terrain hole. Other inherited original camera-ray controls stay unchanged.

`structure09b-CAM_MAIN_L1_LOGGIA_A-boundary.png` and `structure09b-CAM_MAIN_L3_ALCOVE_B-boundary.png` are **old09 rendered images with mathematically projected candidate target annotations**, clearly labelled as such. They are not09b renders and cannot prove final color/material appearance. These two crops and both source boundary overlays were actually opened. Their provenance and crop bounds are in `structure09b-boundary-manifest.json`.

Stage reconciliation is limited to this QA handoff, the explicit five meshes and their main-house source functions. Main source is frozen at the hash above; no further edits are pending. Root owns complete09 integration, global regression, actual visual acceptance and STATUS updates.
