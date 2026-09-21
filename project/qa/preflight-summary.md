# G0 rendering and tool preflight — 2026-09-20

Actual environment: Blender 5.2.1 LTS, Windows 11 build 26200, AMD Ryzen AI Max+ 395 CPU and AMD Radeon 8060S HIP device. All outputs are local, with no installation or preference changes. This tests a deliberately small glass/wood/layered-stone proxy, not Fallingwater visual fidelity.

| Test | Actual result | Evidence |
|---|---|---|
| Cycles HIP, 512×512, 32 samples | PASS, 3.119 seconds | `preflight/cycles_hip.png`, `preflight/preflight.json`, `preflight/blender-preflight.log` |
| Cycles CPU, same proxy/settings | PASS, 1.107 seconds | `preflight/cycles_cpu.png`, same JSON/log |
| Fresh-process open and HIP render | PASS, 2.616 seconds | `preflight/reopen_render.png`, `preflight/reopen.json`, `preflight/blender-reopen.log` |
| Legacy EEVEE identifier | FAIL; `BLENDER_EEVEE_NEXT` is unavailable in this installation | Preserved in first preflight JSON/log |
| Correct EEVEE identifier | Render PASS, 14.925 seconds; default glass appearance FAIL, visibly opaque | `preflight/eevee.png`, reopen JSON/log. EEVEE's original sample default was not explicitly recorded; do not interpret the report's Cycles 32-sample field as an EEVEE measurement. |
| EEVEE transmission fix | Render PASS, 23.280 seconds, 512×512, explicit 32 samples; pane transmits, but roughness .06 visibly blurs masonry | `preflight/eevee_glass.png`, `preflight/eevee-glass-retest.json` |
| EEVEE smooth-window follow-up | Render PASS, 18.114 seconds, 512×512, explicit 32 samples; rear stone joints visible with roughness .025 | `preflight/eevee_glass_smooth.png`, `preflight/eevee-glass-smooth.json`, fixed `.blend` |
| Actual render script, HIP, 512×512/32 | PASS, both PNG and scene-linear EXR written from same Render Result | `preflight/render-script-test/render-benchmark.json` and camera output files |
| Navigation support | In-file text install and panel registration/unregistration PASS; GUI interaction NOT_RUN | `preflight/support-tools-test.json` |
| Geometry validator controls | PASS: detects existing floor, fails when actual floor hidden; absent ceiling and missing second camera correctly fail | `preflight/support-tools-test.json`, `preflight/support-tools-test.log` |

The Cycles debug log explicitly says `Path tracing on: AMD Radeon(TM) 8060S Graphics (HIP)`. CPU was disabled in the HIP device selection. This is actual renderer device evidence; no GPU utilization or memory telemetry was collected. EEVEE runs on its graphics backend, and the Cycles CPU setting has no meaning for its execution. Tiny-scene CPU/HIP timings do not predict which backend wins for the final forest/interior scene.

The image reviewer opened Cycles, original EEVEE, fixed EEVEE and smoother fixed EEVEE PNGs. Opaque-pane failure is resolved in this proxy. Some glass softness and noisy contact shading remain at 32 samples; the proxy is a capability test, not a finished material approval. Full-scene indoor/outdoor/grazing-angle checks remain NOT_RUN.

## Verified Blender 5.2 controls

- EEVEE engine identifier: `BLENDER_EEVEE`.
- Sky types: `SINGLE_SCATTERING`, `MULTIPLE_SCATTERING`, `PREETHAM`, `HOSEK_WILKIE`.
- Principled socket selectors include `Transmission Weight`, `Thin Wall`, `Roughness`, `IOR`.
- EEVEE refraction needed `scene.eevee.use_raytracing = True` and `material.use_raytrace_refraction = True`.
- Tested glass uses `material.thickness_mode = 'SLAB'`, Material Output socket `Thickness = 0.018`, roughness .025, ray tracing resolution scale `'1'`, screen trace quality 1.0. The .018 value is the proxy's actual mesh thickness, not a measured Fallingwater window thickness.
- Node and property lists are preserved in the preflight JSON files. EEVEE settings should be saved in the scene rather than changing the user's global preferences.

`preflight/preflight_glass_fixed.blend` is the saved successful EEVEE small scene. No full-building render or performance claim has been made by this worker.
