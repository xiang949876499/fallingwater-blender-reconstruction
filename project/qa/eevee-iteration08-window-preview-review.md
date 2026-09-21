# Window08 EEVEE preview candidate

**Result: PARTIAL, not a general accepted preview.** The wooden desk and shelving look brown again rather than metallic blue-grey. The room is readable and directionally lit, without the earlier VOLUME black lobes. However, the new AREA produces a conspicuous diagonal lighting boundary on the ceiling and visible grain on the ceiling/shelf at 32 samples. The illumination is stronger and less diffuse than the physical Cycles reference. No further light tuning, bake or render was performed.

Native images actually opened:

- [Window08 EV 2.4](eevee-iteration08-window-preview/CAM_MAIN_L3_STUDY_B_EV2p4.png)
- Same linear render: [EV 1.6](eevee-iteration08-window-preview/CAM_MAIN_L3_STUDY_B_EV1p6.png), [EV 3.2](eevee-iteration08-window-preview/CAM_MAIN_L3_STUDY_B_EV3p2.png)
- [Previous diffuse-only weak World](eevee-iteration07-diffuse-world/CAM_MAIN_L3_STUDY_B_EV2p4.png)
- [Frozen physical Cycles 07 reference](../renders/previews/iteration07-focus/CAM_MAIN_L3_STUDY_B_EV2p4.png)

EV 1.6 makes the shelving darker; EV 3.2 brightens the lit wall. Neither export removes the strong lighting boundary or grain. These are display exports from one render, not additional sampled images.

## Exactly what changed

Source: `qa/eevee-iteration07-diffuse-world/Fallingwater_preview_diffuse_world_candidate07.blend`, SHA `4c26a2667e8697282357688cfb7f580a49e01a7b9f9c88c2dee4a60febb02059`.

The source's diffuse-only split was replaced in a new copied EEVEE World by **Is Camera Ray**: camera-visible World strength 0.36, noncamera World strength 0.006. The physical Cycles World branch was unchanged. One **PREVIEW_APPROXIMATION** AREA was added in its own marked collection.

| AREA setting | Actual value |
|---|---|
| Object | `FW_PREVIEW_WINDOW08_AREA` |
| Collection | `PREVIEW_APPROXIMATION_WINDOW08` |
| Position, metres | −3.930000, 14.469750, 6.580000 |
| Emission direction | +X |
| Rectangle size | 0.75 m across Y × 1.60 m vertically |
| Power | 20 W, normalized |
| Color | Linear white RGB 1,1,1 |
| Shadows | Enabled |

This light is an interior-side approximation of window illumination, not a new architectural fixture. Actual placement rays found the shelving back board 0.460207 m in front, the west wall 0.052000 m behind, an open glass leaf 0.062738 m along −Y, the roof 0.833650 m above and the finish floor 1.293850 m below. Those real nearby occluders remain. The new ceiling boundary is not labeled an engine artifact without a separate diagnosis; it occurs with a real nearby area source and preserved geometry/shadows.

The source's limited AO profile was preserved exactly: Fast GI enabled, `AMBIENT_OCCLUSION_ONLY`, distance 0.6 m, near thickness 0.08 m, quality 0.5, 16 steps, 4 rays, bias 0.05, resolution scale 2. Ray tracing remains enabled. There are zero VOLUME objects and no GI bake. The inherited Living SPHERE capture is retained. No production `configure()` or material helper default was changed.

The model/API accepts and links the `Is Camera Ray` output in a World shader with an EEVEE-targeted output; the graph compiles and renders. This combined candidate changes both World routing and direct window illumination, so it does not isolate the contribution of either change. No separate screen-reflection mask test, large visible-sky view, or moving sequence was performed. The result must not be read as proof that every screen-reflection path behaves like physical path tracing.

## Render evidence

- **One render, 48.390 seconds**, process exit 0; **zero bakes**.
- Frame 48, saved `CAM_MAIN_L3_STUDY_B`, 28 mm, 960×540, 32 samples, EV 2.4, AgX/None, gamma 1; preparation threads 4.
- Camera position and lens unchanged. Same source frame/camera as physical Cycles 07 reference.
- Every original light pose, parameter and shadow link, object transform/visibility, Cycles glass branch and physical pane geometry checked unchanged.
- Source and physical 07 SHA rechecked unchanged. Both production EEVEE helper hashes unchanged.
- The shutdown `Unable to delete file` warning is retained; successful image/save and exit were verified independently.

Selected display RGB comparisons, supporting native inspection rather than serving as photometric acceptance:

| Pixel | Previous diffuse-only split | Window08 | Physical Cycles |
|---|---|---|---|
| Desk (600,388) | 46,51,58 | 51,44,36 | 27,22,17 |
| Shelf panel (257,274) | 30,28,28 | 49,40,34 | 25,18,12 |
| Lit wall (600,270) | 35,39,35 | 105,95,75 | 43,46,38 |
| Ceiling (450,65) | 35,38,37 | 123,116,102 | 41,40,34 |
| Chair fabric (389,456) | 51,69,83 | 51,69,83 | 73,98,113 |

The desk's blue-dominant values become brown-dominant, consistent with the actual visual improvement. The lit wall and ceiling exceed the physical reference. Whole-image display-code MAE against Cycles is 26.254/255, which is not a visual pass criterion.

## Actual Cycles restoration

The candidate loads only the original `FW_Lighting_Daylight` World datablock from frozen physical 07, preserving it as `FW_WINDOW08_PHYSICAL_WORLD_RESTORE`. The original physical scene SHA is `bf50530009e4a93315915815473188c91d891272ef2d8e9e0169b704bd2e2f16`.

The candidate-local `restore_preview_for_cycles(scene)` in [the scoped script](eevee-iteration08-window-preview.py) removes only the marked added AREA and its empty collection, reassigns that exact original World, and switches through the existing Cycles CPU configuration. It does not alter original lights or disable their shadows.

A **fresh reopen of the saved candidate** followed by this function actually passed:

- Added light count becomes zero; the owned AREA datablock and collection are removed.
- Original light names, physical parameters, poses and shadow links match exactly, excluding only cross-session `ID.session_uid` metadata.
- The complete original World shader graph is restored; graph SHA `6881571162a3b886ce0e3dbcfe354076e067a0aaacfcdc18d401a5643377745f`.
- Original Cycles glass branch and pane geometry remain unchanged.
- Source and candidate files unchanged; restore check performed no render, bake or save.

See [cycles-restore-check.json](eevee-iteration08-window-preview/cycles-restore-check.json). **This local restore is not integrated into the production engine-switch path. Merely choosing Cycles without explicitly calling this function would leave the added AREA active.** The saved scene carries this limitation and its restore metadata. It cannot yet be used as a general preview checkpoint.

## Saved evidence and disposition

Candidate: `qa/eevee-iteration08-window-preview/Fallingwater_preview_window_candidate08.blend`, SHA `718c1884de910225a6f13aeb44925017915e81ff9ffbe427dc9d9b9138929731`.

Main PNG SHA: `dbe703016544d9ab571b98cbbaee2cb4e78a70617fa2b2670e066aa52719de77`.

The [machine report](eevee-iteration08-window-preview/report.json) contains all actual AO/light settings, source and helper hashes, shadow/geometry invariants, and the two same-linear export hashes. Its reviewed status is PARTIAL_NOT_ACCEPTED; saved scene was created before visual inspection and was not resaved only for this status.

No production helper integration, additional lights, other-room QA, motion QA or further rendering was performed. The GPU job is finished and released. This bounded test establishes a more useful local preview approximation while retaining the remaining lighting/noise and switching limitations.
