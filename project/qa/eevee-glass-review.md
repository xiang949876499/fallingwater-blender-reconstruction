# EEVEE glazing diagnosis and bounded preview candidate

The selected candidate removes the broad blue-black window obstruction in the tested living-room view and remained clear through twelve actual camera positions. It is an **EEVEE preview approximation**, not a claim that EEVEE now reproduces physically exact glazing or that the project passes photographic QA. The editable production scene was not modified.

## Evidence and comparison

The frozen source is `eevee-glass-source.blend`, copied from the MAIN_L1 volume-baked checkpoint. SHA-256: `1f2a55b63aa331db2e26fb9bd9382239d4bcea1b273c433414cc5c7f64832835`. All six static images use the same CAM_MAIN_L1_LIVING_B pose, 28 mm lens, exposure +0.8, AgX, 960×540, 32 samples and screen tracing at full resolution. Blender is the installed 5.2.1 LTS; CPU preparation was limited to four threads. EEVEE itself uses the graphics backend, not the Cycles CPU/HIP device switch. Other project CPU renders could run concurrently.

| Static variant | Observed result | Render seconds |
|---|---|---:|
| Original physical glass | Broad dark horizontal/window patches and blurred screen transmission; failed this diagnostic | 49.331 |
| Original plus connected 8 mm thickness | Visually unchanged; failed | 72.012 |
| Transparent + Fresnel, DITHERED | More readable exterior, but noisy glazing and dark reflections; failed | 76.561 |
| Transparent + Fresnel, BLENDED | No dither grain, but large blue-black panes; failed | 63.097 |
| Original physical glass + SPHERE | Captured reflection detail appears, but broad obstructions remain; failed | 44.949 |
| BLENDED thin window + SPHERE + two-sided Fresnel correction | Exterior and open casement remain readable; selected for bounded motion check | 58.604 |

Every static output was opened and visually inspected, individually and in `eevee-glass-six-variants-contact.png`. The connected-thickness image differs from the baseline by only 0.003891/255 mean absolute RGB value, P95=0 and maximum=1. This does not support the claim that connecting thickness alone fixes the problem.

The prior Cycles view, `renders/previews/iteration02/CAM_MAIN_L1_LIVING_B.png`, was also actually opened. It uses the same camera composition, 1280×720/48 samples and independently chosen exposure +2.4. Its casement and right window are clear without EEVEE's broad blue-black obstruction. This is a geometry/reflection-shape comparison, not a like-for-like exposure or pixel-error reference. The left dark vertical regions also include real stone columns; their darkness should not be removed by deleting reflection.

## What was wrong and what changed

The installed API inspection found 159 FW_glass mesh objects: 150 have 8 mm local minimum thickness and nine have 12 mm. All have unit object scale and outward convex-box normals. Material thickness was SLAB, raytrace transmission enabled, and the Material Output Thickness socket was unconnected. Blender's documented default already uses the object's minimum dimension when that socket is unconnected. The diagnostic 8 mm connection therefore was not a justified universal geometry correction, especially for the nine existing 12 mm panels. [Blender 5.2 Material Output documentation](https://docs.blender.org/manual/id/5.2/render/shader_nodes/output/material.html)

The original frozen checkpoint contains one VOLUME probe and no SPHERE or PLANE reflection captures. A SPHERE is useful as the screen-ray fallback; a VOLUME records diffuse lighting. The added living-room capture has BOX influence and parallax, resolution 512, location (4.9256, 7.5402, 1.3), object scale (5.6068, 7.3809, 1.2), influence distance 1.25, falloff .15, clip .05–150 m and parallax distance 1. Six actual axis ray checks first hit front-facing geometry at 1.178–7.324 m. No light was added. This SPHERE API has no intensity multiplier; existing volume intensity remains 1. The capture updates automatically per offline frame. [Blender 5.2 Sphere documentation](https://docs.blender.org/manual/uk/5.2/render/eevee/light_probes/sphere.html), [Volume documentation](https://docs.blender.org/manual/sr/5.2/render/eevee/light_probes/volume.html)

Adding the probe alone did not fix original screen transmission. EEVEE documents only one correctly modeled refraction event and restrictions on one raytrace-transmissive material appearing through another. The local 5.2 defaults also enable backface ray hits at radiance scale .25, with .1 m screen intersection thickness; these were recorded rather than silently changed. [EEVEE limitations](https://docs.blender.org/manual/de/5.2/render/eevee/limitations/limitations.html), [5.2 ray tracing changes](https://developer.blender.org/docs/release_notes/5.2/eevee/)

The first thin-window shader had an additional modeling error: it transmitted an unbent ray, then evaluated the rear face as though that direction were inside the refractive medium. Blender's Fresnel node inverts its input IOR on a backface and can then return total internal reflection. The 5.2 release source confirms this behavior. The selected EEVEE branch uses Geometry Backfacing to supply 1.5 on the front and 1/1.5 on the back, cancelling that internal inversion only for the explicitly approximate unbent transmission model. It keeps Fresnel-dependent reflection, roughness .025 and both actual pane surfaces. It does **not** zero the reflection, lower the physical Cycles IOR, remove glass geometry or use backface culling to hide a panel. [Blender's 5.2 Fresnel implementation](https://raw.githubusercontent.com/blender/blender/blender-v5.2-release/source/blender/gpu/shaders/material/gpu_shader_material_fresnel.glsl)

The selected shader routes Transparent + Glossy through Fresnel to an EEVEE-specific Material Output, uses BLENDED with overlapping layers and disables screen refraction for this material. The original Principled graph is still connected to its original output, targeted to CYCLES. Geometry and original Cycles-surface hashes were identical before and after application and after a fresh-process reopen/reapplication. There is exactly one EEVEE output and one living-room reflection probe after repeated application. Details are in `eevee-glass-integration-check.json`.

The sixth image changes both the reflection capture and the two-sided thin-shader correction relative to the fourth image. The static set therefore establishes that the **combination works in this view**, not a measured isolated contribution from each change. The physical-plus-probe control demonstrates that the probe by itself is insufficient.

## Moving-camera evidence

`eevee-glass-thin_blended-probe-two-sided-sequence/` contains twelve actual 960×540 PNG renders at fixed orientation with a total .24 m lateral camera move. All twelve image dimensions and SHA-256 values were checked, and all twelve hashes are distinct. The complete contact sheet, including native-pixel casement crops from every frame, was opened. The final frame was also opened at full size. No blue-black window band or dither grain reappeared within this short movement; glazing silhouettes stayed coherent. This limited review cannot rule out other-angle sorting errors, reflection swimming, temporal issues elsewhere or long-path exposure problems.

First frame took 61.608 s; warm-frame median was 14.931 s; twelve frames totaled 227.594 s. Sphere recapture occurs every frame, and concurrent CPU tasks can affect these times. This is not a viewport FPS test or an isolated performance comparison. Full-frame adjacent differences include intended camera parallax and are not a flicker metric.

`eevee-glass-selected-12frames.mp4` was encoded and independently probed: 960×540, 24 fps, exactly 12 frames, **0.500000 seconds**. It is not a twelve-second clip, a ten-second water test or the final tour. The MP4 was verified by ffprobe; visual review used the actual frame images/contact sheet rather than claiming playback inspection.

The earlier DITHERED sequence was deliberately cancelled before its first completed PNG when the scope expanded to a BLENDED static test. Its one-line log and explicit CANCELLED report are retained. It is not counted as a successful sequence.

## Integration and limits

`project/scripts/eevee_glass.py` provides `apply(scene)`. Defaults select the reviewed BLENDED, two-sided thin-window model with the living-room SPHERE. To handle reflection captures separately, use `apply(scene, reflection_probe=False)`. This helper does not render, change the current engine, bake GI, alter lights, save the production file or modify global settings. Diagnostic modes and the CLI remain available with explicit flags. The saved candidate is `qa/eevee-glass-thin_blended-probe-two-sided-candidate.blend`.

Call it after production materials are built and after any helper that resets transmissive material flags. In particular, `eevee_preview.configure()` currently loops over Principled transmission and sets `use_raytrace_refraction=True`; therefore apply the reviewed EEVEE branch **after configure and before the final bake/render**. The module's original Cycles shader remains available on engine switch.

Only this living-room capture placement and camera sweep were checked. Glass material application affects all objects using FW_glass, but other rooms need suitable reflection captures and their own reviews. Box parallax is an approximation to an irregular room; captures can misplace near reflected objects. BLENDED surfaces retain documented screen-ray, layering, depth-of-field and reflection limitations. Two transparent interfaces with independent Fresnel terms approximate parallel thin glazing; they do not reproduce ray bending, absorption through thick edges or multiple internal bounces. The real Cycles shader should continue to serve physical still-image rendering.

This source predates current architectural, lighting and site repairs. Its existing MAIN_L1 diffuse cache was deliberately held fixed to compare the material candidates. Geometry/material/light changes require fresh GI baking. Apply to the new integrated checkpoint, rebake the final interior volumes, inspect multiple window angles including exterior views and overlapping open casements, then measure native navigation and a longer moving segment. Full-building quality, current-scene integration, 1080p final-film acceptance and interactive performance remain NOT_RUN by this subtask.
