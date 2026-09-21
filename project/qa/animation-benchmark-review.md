# EEVEE continuous-frame benchmark — 2026-09-20

Both requested static cameras produced ten consecutive 1920×1080 PNG frames using Blender 5.2.1 LTS EEVEE, 32 samples, AgX, and full-resolution screen ray tracing. Rendering and output verification passed. This establishes an offline preview path; it does not establish photographic acceptance, a completed tour, or interactive viewport FPS.

| Camera | First frame | Median of frames 2–10 | Total, ten frames | Exposure |
|---|---:|---:|---:|---:|
| CAM_HERO | 31.6207 s | 5.4976 s | 83.6075 s | +0.8 |
| CAM_MAIN_L1_LIVING_B | 58.7964 s | 8.7447 s | 137.5731 s | +0.8, independently selected for EEVEE |

The parent task could render concurrently on the CPU. Startup includes scene and shader preparation; these figures are measurements of these runs, not isolated hardware maxima. At these warm medians, 2,880 frames would arithmetically take about 4.40–7.00 hours, plus startup, scene-dependent costs, encoding, and review. This is an estimate from two static views, not a promise for moving cameras or the remaining rooms. The original full-length delivery requirements remain unchanged. No 2,880-frame render was started.

## Files and verification

- Source checkpoint: `qa/animation-benchmark-eevee-exposure/Fallingwater_eevee_baked.blend`, SHA-256 `1f2a55b63aa331db2e26fb9bd9382239d4bcea1b273c433414cc5c7f64832835`.
- Numbered frames and per-frame elapsed time, SHA-256, camera, exposure, and coverage records: `qa/animation-benchmark-hero/animation-progress.json` and `qa/animation-benchmark-living/animation-progress.json`.
- Both `qa/animation-benchmark-*-10frames.mp4` files were checked with ffprobe: 1920×1080, 24 fps, exactly 10 frames, duration 0.416667 seconds. They are **ten-frame previews, not ten-second sequences**.
- The exterior sequence was reopened in a new Blender process and resumed: 10 existing frames verified by source/settings signature, SHA-256, PNG dimensions and exposure; 0 frames re-rendered. Original frame timings remain in `runs`; the latest invocation correctly reports zero rendering time.
- Both modules passed syntax compilation. Focused helper checks passed for inclusive sparse ranges, rejected invalid ranges/steps, route boundary selection and EEVEE-specific exposure interpolation.
- The baked scene was packed and reopened in independent exposure and sequence processes. All selected outputs exist and every recorded sequence frame passed. This is not a full portability test on another computer.

## Illumination and visual findings

One actual `VOLUME` LightProbe, `FW_PROBE_MAIN_L1`, was baked using `bpy.ops.object.lightprobe_cache_bake(subset='ACTIVE')`, which returned `FINISHED` after 31.173 seconds. Its grid is 20×14×4, bake samples 64, surfel density 8, capture distance 20 m, world/indirect/emission capture enabled, intensity 1.0. Nine MAIN_L1 room IDs fall within its declared volume. The floor/ceiling margins are 0.12 m and the XY margin 0.15 m. Exact bounds and local API inspection are saved in the setup report and `qa/animation-benchmark-probe-api.json`.

Only MAIN_L1 was baked. A room ID inside a volume establishes intended coverage, not proof that every probe is unobstructed or that every corner is correctly lit. The remaining six indoor level groups are not baked in this checkpoint. No additional invisible light emitter or intensity multiplier was introduced. Lighting comes from the scene's sky, sun, and modeled lamp emissions.

The inherited Cycles living-room exposure of +2.4 was too bright for this EEVEE result. The same linear render was exported at exposures 0, +0.8 and +1.6; 0 and +0.8 were visually inspected, and +0.8 selected for the benchmark. Final frame 10 from both sequences was also visually inspected. The living-room floor, ceiling, seating and piano are readable; exterior geometry is visible through the windows. However, the glass still shows broad dark bands and blurred screen-tracing detail. These artifacts must be resolved or the final route should use a validated alternative renderer. Raising samples alone is not established as a fix. The exterior also retains simplified site geometry and vegetation in this checkpoint; later scene changes require fresh evidence.

The sequence's automated `segment_exposure_verified` fields are not the authority for this visual review: the earlier exterior script inherited the generic camera evidence flag, while later interior code requires an EEVEE-specific flag and under-reports this manual review. Neither field establishes calibration of any untested tour segment.

## Whole-building GI and tour integration

After final geometry, vegetation, materials and lighting are stable, call `eevee_preview.bake(..., levels=['all'])` or the CLI `--levels all` in a separately saved scene. The current room list yields seven indoor groups: MAIN_B (4 rooms), MAIN_L1 (9), MAIN_L2 (10), MAIN_L3 (6), GUEST_B1 (3), GUEST_L1 (8), and GUEST_L2 (5): 45 indoor room records in total. The other 15 records are exterior or other non-interior spaces and do not require indoor volume coverage merely to satisfy a CSV count.

Start with the tested 1.5 m XY and 0.8 m Z target spacing. The helper caps each XY axis at 24 probes, so inspect the resulting actual spacing for large floors. Split or locally densify narrow corridors, stairwells and thin-wall adjacencies where a broad floor grid leaks or misses interior points. Inspect each floor in a section view and render dark corners, windows, doors and transitions. Keep intensity 1.0; correct spatial coverage, material transmission and real source lighting instead of adding hidden fill emitters. Bake caches must be regenerated when static geometry, materials or light sources change; animated water is not a rebaked diffuse light source on every frame.

The operator result alone is insufficient. Save and reopen the complete scene, confirm the actual volume objects and intended room coverage, inspect representative views from every group, then check a short moving section for leaks, exposure changes and glass artifacts. Final route metadata should include `exposure_by_engine` with a scalar or `exposure_start`/`exposure_end` per segment and an explicit visual verification flag. `render_animation.py --require-route-exposure` rejects requested frames lacking route exposure; it does not perform visual calibration itself. Unbaked room IDs are logged for each frame. Full tour clearance remains the tour agent's separate responsibility.

The local API and completed bake are the execution evidence. The official [EEVEE light-probe overview](https://docs.blender.org/manual/en/5.2/render/eevee/light_probes/index.html) describes the probe system, and the [Volume documentation](https://docs.blender.org/manual/en/5.0/render/eevee/light_probes/volume.html) describes cached volume data. Only search excerpts were retrievable for the latter page; full-page tool access returned HTTP 402. No third-party description was used as proof of the installed API.

## Runnable interface

`render_animation.py` runs inside Blender and supports `--scene`, `--camera`, `--frames` (inclusive ranges or comma-separated values), `--resolution`, `--samples`, `--engine`, `--device`, `--output`, `--route-metadata`, `--require-route-exposure` and explicit `--overwrite`. Use a new output directory after changing source scene or settings. Existing PNGs are reused only when verified against the matching job record; unverified files cause an error. It writes incremental JSON after every frame and does not encode or launch a complete film automatically.

`eevee_preview.py` supports `--levels`, `--bake-samples`, `--bake-density`, `--probe-spacing`, selected `--first-views`, `--skip-bake`, and exposure brackets. Blank `--first-views` permits baking and saving without extra static renders. Its default is MAIN_L1 only. Its output scene is separate from the production scene.

Full-building GI, route-wide EEVEE exposure, moving-camera temporal artifacts, a 10-second water review, final-film encoding, photographic QA and GUI FPS remain NOT_RUN in this benchmark. Global project documentation is reconciled by the parent task; this report is the authoritative handoff for these two modules.
