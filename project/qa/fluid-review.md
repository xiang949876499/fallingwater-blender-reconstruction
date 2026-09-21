# Local Bear Run liquid simulation pilot

This is a bounded Mantaflow experiment, not final water acceptance. The prior procedural water had failed two visual reviews, so this pilot follows `prompt.md` section 6.2. Hydraulic velocities, initialization and bathymetry are authored C-level parameters, not measured site hydraulics.

Current status: **no cached pilot is accepted for full-river installation**. Run05 remains a frame48 diagnostic; its full-scene seams failed review. Run06 completed72 frames but the fixed full-width contour failed. The one36-frame entry01 calibration also failed downstream depth and continuous coverage. See [dynamic assessment](water-dynamic-review.md) and [entry01 measurements and viewed image](fluid-entry01-review.md). Historical run01–05 details below are retained as evidence, not current integration approval.

## Run 01 — cache works, image fails

- Blender 5.2.1 LTS, CPU 8 threads, 24 fps, frames 1–48, domain resolution 64, mesh scale 2.
- Actual domain: 13.6647 × 14.6118 × 4.6 m. Main lip inherited from `site.json`: (2.4, −2.83, −3.05), downstream direction (−0.88235, −0.47059).
- 30 local rock collision meshes and a 1,927-vertex closed riverbed patch from the site height function; no forest or full-site domain.
- `bpy.ops.fluid.bake_all()` returned FINISHED. Outer wall-clock 31.13 s; Blender's internal bake report 30.94 s.
- Actual cache: 144 files, 152,167,274 bytes; 48 liquid surface mesh files. Evaluated mesh vertices at frames 1/24/48: 16,234 / 30,720 / 35,738.
- Frames 24 and 48 were genuinely rendered in Cycles and opened for visual inspection. At 1280×720 and 48 samples, render time was 68.44 / 69.45 s under concurrent CPU workload.
- **Visual result: FAIL.** Water splits around the ledges and changes at the impact pool, but it is too thick and dark blue, has a visibly coarse surface, and lacks entrained foam. This is not an accepted photographic waterfall.

Files: `fluid-run01.json`, `fluid-run01.log`, `fluid-run01-frame024.png`, `fluid-run01-frame048.png`; scene `../scene/Fallingwater_fluid_run01.blend`; cache `../caches/fluid_pilot/run01`.

## Run 02 — clearer water, foam scale and sustained flow fail

This bounded experiment used resolution 96, frames 1–48 and 8 CPU threads. It reduced inlet depth and mesh particle radius, created a dedicated clearer liquid material, and used Mantaflow's simulated secondary foam and spray particles.

- Actual bake: 227.66 s; cache 192 files / 471,288,235 bytes (449.46 MiB), including 48 liquid mesh files.
- Mesh vertices at frames 1/24/48: 31,142 / 55,056 / 41,804.
- At frame 24, actual simulated secondary particle counts were 119,551 foam and 39,523 spray; at frame 48, 173,772 foam and 33,735 spray.
- Cycles 960×540, 32 samples: frame 24 rendered in 36.45 s, frame 48 in 35.23 s. Both images were opened and inspected.
- **Visual result: FAIL.** Transparency improves substantially over run 01. However, the 24 mm foam particle radius looks like white pebbles, and the broad falling flow visible at frame 24 becomes too weak by frame 48. The inlet's exposed depth above the rock was reduced below a reliable one-to-two-voxel layer; this is a likely cause requiring a new hydraulic check, not a proven measured flow diagnosis.
- A separate fresh Blender process appended only the cached liquid collection via `fluid_water.install`. Frames 1/24/48 had exactly the original vertex counts. **PASS_CACHED_COLLECTION_APPEND** establishes that the API loads the cache; it does not establish relocated delivery-package portability or final-river joins.

Files: `fluid-run02.json`, `fluid-run02.log`, `fluid-run02-frame024.png`, `fluid-run02-frame048.png`, `fluid-install-check.json`; scene `../scene/Fallingwater_fluid_run02.blend`; cache `../caches/fluid_pilot/run02`.

## Run 03 — particle scale improves, main flow still fades

Used the 96-resolution local domain for 60 frames. Inlet top was restored to −2.79 m; foam render radius became 8 mm and spray radius 2.5 mm, with reduced secondary-particle sampling.

- Actual bake: 111.07 s; 240 files / 660,747,715 bytes (630.14 MiB), including 60 liquid mesh files.
- Actual mesh vertices at frames 1/30/60: 32,002 / 55,492 / 54,096. Frame 60 has 62,705 foam and 12,532 spray particles; a subsequent state query confirmed all reported particles were ALIVE.
- Cycles 960×540, 32 samples: frames 30/60 rendered in 23.62 / 17.75 s. Both were opened and inspected.
- **Visual result: PARTIAL_IMPROVEMENT, NOT_ACCEPTED.** Foam scale and clear water improve, but the middle falling flow reduces substantially by frame 60 and the mesh still has thick under-resolved patches.
- Actual geometry diagnostic: across 17 cross-stream ray positions at Z = −4.2 m, frame 30 hits water 4 times, frame 60 hits 0 times. This is not merely clear water becoming hard to see. These are silhouette-coverage checks, not a volumetric discharge measurement.
- The sandstone collider is closed: zero non-manifold edges, positive signed volume 307.97 m³. The rightmost source cross-point is blocked by a shoulder rock (top Z −2.47 m), and the source's lower volume overlaps the upper bed. No bedrock was removed to redirect water.
- A new process again appended the cached fluid collection and matched all mesh and foam/spray particle counts at frames 1/30/60: `fluid-install-run03.json`.

Files: `fluid-run03.json`, `fluid-run03.log`, `fluid-run03-frame030.png`, `fluid-run03-frame060.png`, `fluid-diagnostics-run03.json`; scene `../scene/Fallingwater_fluid_run03.blend`; cache `../caches/fluid_pilot/run03`.

## Run 04 — sustained flow established at coarse resolution

Used 96 resolution / 60 frames / 8 CPU threads. Moved the inlet near the lip (along −1.0…−0.42 m), narrowed it to cross ±3.55 m so it avoids the shoulder, and placed its bottom/top at −2.99/−2.67 m. Delete In Obstacle was enabled. Inlet speed 1.8 m/s and all source placement are C-level hydraulic construction parameters. Actual rock geometry is unchanged.

- Actual bake: 58.75 s; 240 files / 446,208,097 bytes (425.54 MiB), including 60 mesh files.
- Mesh vertices at frames 1/30/60: 30,728 / 65,810 / 71,552.
- Cycles 960×540, 32 samples: frames 30/60 rendered in 34.97 / 37.89 s. Both were opened and inspected.
- **Stable supply improves.** The broad waterfall remains present through frame 60. At Z = −4.2 m the 17 cross-stream rays hit water 14 times at frame 30 and 13 times at frame 60; other tested heights also retain comparable coverage.
- A 3×17 sampling grid across the actual inlet finds no rock surface above the source bottom. This is a sampled geometry check, not a claim of exact volumetric intersection analysis.
- **Visual result: NOT_FINAL.** Continuous large-scale flow is established, but 0.152 m cells still create excessively thick water sheets. Stability between two sampled frames is not a ten-second video acceptance.

Files: `fluid-run04.json`, `fluid-run04-frame030.png`, `fluid-run04-frame060.png`, `fluid-diagnostics-run04.json`; scene `../scene/Fallingwater_fluid_run04.blend`; cache `../caches/fluid_pilot/run04`.

## Run 05 — finer short cache, ready for integration comparison

Used the successful source configuration with along limits −1.4…3.4 m and cross limits ±4.6 m, 160 resolution, 48 frames, 8 CPU threads. The full waterfall width and immediate impact pool remain covered, and all overlapping rock colliders remain present.

- Actual domain: 8.5647 × 10.3765 × 4.6 m; nominal solver cell 0.06485 m.
- Outer bake wall-clock: 501.01 s (Blender internal report 500.18 s). Actual cache: 192 files / 1,631,355,145 bytes (1.519 GiB), including 48 mesh frames.
- Actual mesh vertices at frames 1/24/48: 138,080 / 332,730 / 420,682; polygons: 276,152 / 666,180 / 842,172.
- Actual foam/spray particles at frame 24: 118,556 / 40,200; frame 48: 242,298 / 93,796.
- Cycles 960×540, 32 samples: frame 24 rendered in 36.03 s; frame 48 in 43.73 s. Both were opened and inspected. Edge breakup and impact detail improve over run 04, and the broad waterfall persists. The top layer and falling sheet still look overly uniform in parts, foam remains somewhat granular, and the isolated domain exposes its cropped boundaries. **INTEGRATION_CANDIDATE, NOT_FINAL_VISUAL_PASS.**
- At Z = −4.2 m, 15/17 cross-stream rays hit liquid at both frames 24 and 48; the other three tested heights also retain comparable coverage. All 51 inlet rock-clearance samples remain clear.
- SHA-256 was recorded for every cache file; all files are nonempty and every `.gz` stream passed decompression/CRC verification: `fluid-cache-run05.json`.
- A separate Blender process appended the cache and matched original mesh and particle counts at frames 1/24/48: `fluid-install-run05.json`. This verifies loading from the original cache path, not relocated final-package portability.

Timing does not justify skipping integration. A linear extension of this measured run is about 42 minutes / 7.6 GiB for 240 frames, or 52 minutes / 9.5 GiB for 300 frames; steady-state dynamics, threading and other workload may change both. These are estimates, not a completed long bake. After full-scene HERO/near-water comparison and seam fixes, a candidate next experiment is frames 1–300 with 1–60 for warm-up and 61–300 for ten seconds of continuous QA.

## Integration and reproducibility

`project/scripts/fluid_water.py` provides `build(ctx, settings=None)` to create a bounded simulator and `install(scene, cache_blend)` to append the cached liquid/particle-template collection. `build` does not bake automatically. The standalone CLI refuses a nonempty cache directory and requires a fresh factory-startup process; it never opens or overwrites `Fallingwater_working.blend`.

```python
import fluid_water
fluid_water.install(bpy.context.scene, project_root / 'scene/Fallingwater_fluid_run05.blend')
bpy.context.scene.frame_set(48)
```

The appended collection records its valid cache start/end and recommended preview frame. The source file and entire `caches/fluid_pilot/run05` directory must stay together in a later delivery layout, with paths rewritten and independently reopened. Texture resources are the parent project's existing materials/assets; this experiment introduces authored simulation data, not a newly downloaded third-party model.

The installer deliberately does not remove the existing river. Integration must replace the procedural falling ribbons and local foam, cut overlap faces from the upstream/downstream water surface while preserving shape-key vertices, and blend water level/flow at the cache boundaries. Test actual photographs' HERO and near-water angles after that change. The current main-scene default frame 73 exceeds this short cache; do not mistake an out-of-range frame for missing simulation.

## Resolution boundary

The current 14.6118 m longest domain edge yields a 0.1522 m solver cell at resolution 96. Mesh scale 2 does not make the physical solver resolve centimeter water sheets. A tighter, still complete lip/impact domain along −1.4…3.4 m and cross ±4.6 m has an axis-aligned longest edge about 10.38 m; resolution 128 / 160 gives cells about 8.1 / 6.5 cm. Resolving a 3–5 cm sheet with two solver cells would require roughly 415–692 cells across that domain. A shorter high-resolution timing experiment must precede any claim of acceptable fine breakup or a full-length cache.

## Remaining acceptance

Ten continuous seconds, full-river seam integration, final-shot photographic comparison, cache portability and animation performance remain NOT_RUN. A changing mesh count and successful bake only establish functioning simulation, not these visual or delivery requirements.

The official API and cache documentation informed the workflow; property names and secondary particle systems were also queried in the actual installed Blender build: [FluidDomainSettings](https://docs.blender.org/api/main/bpy.types.FluidDomainSettings.html), [Fluid cache](https://docs.blender.org/manual/en/latest/physics/fluid/type/domain/cache.html).
