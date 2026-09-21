# Dynamic water boundary assessment — run06

2026-09-20. **FAIL for the proposed full-width fixed-contour seam; run06 is not installed.** Cache generation and cached collection append pass. These are separate results. The small, authorized inlet calibration is tracked in [fluid-entry01-review.md](fluid-entry01-review.md).

Frozen context: scene/Fallingwater_iteration04.blend, SHA256 247d20f7863e4f7e9c18587d4c032bd663857a420bcfb828d271195665841ac2. Source04, working, the site module and real rock structures were not edited. No global upstream water raise was applied.

## Actual bounded cache

Run06 completed72 frames at24fps, resolution192, CPU8. Domain10.9706 ×12.1647 ×4.6m gives a nominal6.336cm physical cell. It cannot resolve a5–9cm film with three cells; mesh subdivision does not improve solver resolution.

Actual bake time: **1,688.46s (28m08s)**. Cache: **288files, 5,815,442,910bytes, 72liquid mesh frames**. At frames1/36/72 the evaluated mesh has172,294 /470,968 /446,154vertices. [Cache integrity](fluid-cache-run06.json) verified nonzero files, SHA256 and gzip CRC. [Fresh-process append](fluid-install-run06.json) loaded matching mesh and particle counts at1/36/72. This is reopening against the original cache location, not relocated-package portability.

The authored downstream source spans along3.5–5.5m, top-5.965m, down velocity0.28m/s. Its424 closed cells clear sampled rocks by at least4cm;76 shallow/bank cells are omitted. Persistent source/rock surface intersections are zero. This is **C hydraulic boundary calibration**, not measured Bear Run flow. Existing rocks and closed site-height bed are retained.

## Source head is not the free outlet

[Head profile](fluid-head-profile-run06.json) measures every integer frame24–48. Centerline examples (metres, mean over25frames):

| Along position | Actual liquid top | Original program water | Interpretation |
|---|---:|---:|---|
| -0.70 | -2.63403 | -2.98527 | Inside source; about35.1cm too high |
| -0.20 | -2.74118 | -3.02620 | After source, falling head |
| 0.00 | -2.92345 | -3.04945 | Cliff edge; range-2.94386…-2.90429 |
| 4.30 | -5.92812 | -5.91289 | Outlet center; total temporal range3.23mm |

The source-height transition would create an uphill reach. Raising the complete upstream river to fit it is unacceptable. MAIN_B_lower_platform top is-2.84670m; its program river level is-2.89745m, leaving only5.08cm. A hypothetical water level-2.634m would stand21.27cm above the platform. This is an actual object-bounds/river-plan screening, not a full flood model. The raise was not applied. [Building, bank and rock context](fluid-run06-boundary-audit.json).

The older head-profile field axis_bed.collision_rock_top combines rock and local-bed hits. Use the boundary-audit's separate rock_top_m, local_closed_bed_m and source_scene_terrain_m fields when distinguishing them.

## Fixed free-discharge contour does not close

[Exact horizontal mesh sections](fluid-section-profile-run06.json) tested61 cross positions over all25 frames. Cross positions with no common liquid interval through time:25/61 at Z=-3.06,16/61 at-3.10 and15/61 at-3.14. The wider [ray-range check](fluid-section-range-check.json) verifies this is not simply the initial bounded along-ray window missing the sheet: at frame24 and several central cross positions there is no cached mesh hit at-3.10…-3.60 across along-4…+6m.

This rejects the simple full-width fixed contour. It does not establish that every possible split-stream/rock-contact interface is impossible, nor that no FLIP particles exist there. Real exposed rock and underresolved thin mesh sheets must be distinguished in further work. No animated face mask or water-plane filler is claimed as a solution.

Downstream along4.3m, all25×61 top rays hit water, but the whole width is **not flat/stable**: the maximum local temporal top range is42.70cm at cross+3.22m, with other crests around20cm. The quiet center alone is insufficient. [Outlet summary](fluid-run06-outlet-summary.json).

## Frozen interfaces and acceptance limits

- water_integration.repair_surface_normals(scene) is the verified orientation-only repair. It preserves base vertices, shape-key coordinates and drivers, and makes the75mm Solidify shell extend downward. Root05 may use this independently.
- fluid_water.build(ctx, settings) builds a separate bounded pilot; fluid_water.install(scene, cache_blend) appends a cached collection. Neither certifies or automatically joins a full river.
- Legacy water_integration.install(...) remains a **frame48 diagnostic**. Its mask cannot claim25-frame coverage.
- install_dynamic(...) is guarded by default and raises because the source-head transition is rejected. Its unexecuted opt-in diagnostic body is not a production interface. No dynamic integrated run06 scene was saved.

Run05 full-scene HERO/WATER_DETAIL/OUTLET images were actually viewed and failed material/volume/seam review; see [integration report](water-integration-review.md). Run06 has numerical boundary assessment but **no new full-scene render acceptance**. No final ten-second bake, subframe review, portable relocation or photographic acceptance is claimed. No new960px render was consumed by run06.
