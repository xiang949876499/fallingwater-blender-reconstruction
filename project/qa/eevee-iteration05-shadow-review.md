# Iteration 05 local shadow diagnosis

**Bath: the enormous inverted triangle is caused by the point proxy shadowing its own visible emissive filament.** Excluding that filament from that one light removes the triangle while every light keeps shadows enabled. The visible bulb, metal guard and walls remain shadow casters. **Living: disabling only Fast GI removes the broad horizontal band**, while screen ray tracing, all real shadows and all seven baked volume intensities remain enabled. These are local symptom corrections, not whole-scene, photorealistic or animation acceptance.

All images below were actually rendered and opened at native 960×540. Blender 5.2.1 LTS EEVEE, 32 samples, exposure +0.8, frame 1, original saved camera pose, four CPU preparation threads. Each variant reopens `scene/Fallingwater_preview_iteration05.blend`, SHA-256 `b855de89492af8ae31ae4d53bb2674f518ea13cf2e8f1585b2b9a31b35511939`. No diagnostic scene was saved and no GI cache was rebaked. `eevee-iteration05-shadow-summary.json` verifies output hashes and dimensions.

## Actual single-factor images

| View / sole change | Seconds | Actual finding |
|---|---:|---|
| Bath baseline | 59.724 | Huge inverted dark triangle covers both cork walls. |
| Bath raytracing off | 63.788 | Triangle remains. |
| Bath seven VOLUME intensities zero | 28.624 | Triangle remains and deepens. |
| Bath fourteen visible practical lights' shadows off | 14.157 | Triangle disappears; diagnostic only, never adopted. |
| Bath one light excludes only its own filament | 94.209 | Broad triangle disappears. A narrow corner shadow remains; this candidate does not remove real guard/wall shadows. |
| Living baseline | 37.704 | Broad black band crosses hearth and right wall. |
| Living Sun shadows off | 71.395 | Furniture brightens but the broad wall band remains. |
| Living seven VOLUME intensities zero | 18.854 | Hearth middle darkens; bright upper strip and lower edge remain. |
| Living Fast GI off, screen ray tracing retained | 79.721 | Broad horizontal band and abnormal upper light strip disappear. Stone-joint detail weakens, and the image remains dim/noisy. Local symptom removal only. |

The failed initial jitter experiment never wrote a PNG. Its retained JSON is explicitly `CANCELLED_BEFORE_PNG`; the one-line log is interruption evidence, not a completed test. No second Bath candidate was needed after the isolated filament exclusion succeeded. Contact sheets are `eevee-iteration05-shadow-bath-contact.png` and `eevee-iteration05-shadow-living-contact.png`; they resize existing renders for comparison and do not retouch the images.

## Bath geometry and causal evidence

The actual point is `FW_FURN_MAIN_B_BATH_practical_ceiling_lamp_C_03_bulb_photometric_proxy`, at world **(-1.152799964, 14.655599594, -0.240000010) m**, radius **0.027 m**, power **18 W**. The visible filament is a 2.2 mm-radius tube surrounding the point. Camera rays were cast through the black center and the two bright sides; each resulting wall target was then joined to the real point by an actual scene ray segment. Full evaluated object/material/face/normal records are in `eevee-iteration05-shadow-rays.json`.

| Camera pixel / wall target | First filament hit | Bulb shell hit | Wall distance |
|---|---:|---:|---:|
| (505,325), `MAIN_B_bath_1`, (-0.399400264,14.752950668,-0.920219243) | 0.3468 mm, back face | 51.0785 mm | 1.0197 m |
| (170,300), `MAIN_B_bath_0`, (-0.883016944,15.526399612,-0.802107573) | 0.2450 mm, back face | 52.8402 mm | 1.0710 m |
| (850,300), `MAIN_B_bath_1`, (-0.399400294,13.817974091,-0.815032721) | 0.3209 mm, back face | 54.2979 mm | 1.2649 m |

The dark-center wall normal is approximately (-1,0,0), evaluated face 50; the left wall normal is (0,-1,0), face 50; the right wall is again (-1,0,0), face 50. None of these three centerline segments hits a metal guard. Geometric intersection alone does not prove a shadow-map contribution; the actual single-light exclusion render establishes the filament's causal contribution.

The stored `shadow_buffer_clip_start` is 0.05 m, but **this is not evidence of the current EEVEE shadow near plane**. Blender 5.2.1's point-shadow setup computes a near plane from the influence radius divided by 4000, and the shadow fragment first performs light-shape clipping. The earlier possible “50 mm clip versus 51 mm bulb” explanation is therefore not accepted. [Point shadow setup](https://raw.githubusercontent.com/blender/blender/v5.2.1/source/blender/draw/engines/eevee/eevee_light.cc), [shadow fragment implementation](https://raw.githubusercontent.com/blender/blender/v5.2.1/source/blender/draw/engines/eevee/shaders/eevee_surf_shadow.bsl.hh)

The installed bulb material already has `use_transparent_shadow=True`, `surface_render_method='DITHERED'`, and `Light Path.Is Shadow Ray` mixing its physical Principled output with white Transparent BSDF. Therefore the successful candidate leaves the bulb shader and mesh alone. EEVEE's shadow pipeline supports this transparent branch, subject to the transparent-shadow flag; it averages transmittance and does not simulate refractive or colored caustics. [Shader conditions](https://raw.githubusercontent.com/blender/blender/v5.2.1/source/blender/draw/engines/eevee/eevee_shader.cc), [shadow implementation](https://raw.githubusercontent.com/blender/blender/v5.2.1/source/blender/draw/engines/eevee/shaders/eevee_surf_shadow.bsl.hh), [material pipelines](https://raw.githubusercontent.com/blender/blender/v5.2.1/source/blender/draw/engines/eevee/eevee_material.cc)

## Scoped reusable correction

The local API test confirmed `light.light_linking.blocker_collection` and collection member `light_linking.link_state='EXCLUDE'`. A collection containing only excluded objects leaves every other object eligible to cast shadows from the light. EEVEE supports light and shadow linking. [Official light-linking semantics](https://docs.blender.org/manual/en/latest/render/lights/light_linking.html), [EEVEE introduction](https://developer.blender.org/docs/release_notes/4.3/eevee/)

`scripts/eevee_preview.py` exposes an **explicit opt-in** helper; it is not called by `configure`, the CLI, or the root animation renderer:

```python
eevee_preview.apply_emitter_shadow_exclusions(scene, [
    'FW_FURN_MAIN_B_BATH_practical_ceiling_lamp_C_03_bulb_photometric_proxy'
])
# Before using this preview scene in Cycles:
eevee_preview.restore_emitter_shadow_exclusions(scene)
```

It requires EEVEE and explicitly named point proxies, checks matching bulb and filament, refuses to overwrite other shadow-link collections, and excludes only the named light's own filament. The function is idempotent. The restore helper removes only its own marked collection links and restores the original null blocker link. A fresh Blender process verified apply twice, restore twice, Cycles guard, unchanged point position/energy/radius/shadow flag, unchanged original Cycles surface hash and unchanged glazing geometry hash. See `eevee-iteration05-shadow-helper-check.json`.

**Shadow linking itself is engine-independent.** The helper is a documented EEVEE preview approximation for a duplicated visible-emitter/point-proxy representation. Persisting its link and then switching to Cycles without restoring would change Cycles lighting. The source `.blend` files were not modified. The unchanged Cycles material hash proves shader preservation, not that an active shadow-link override would be ignored by Cycles.

No automatic exclusion was applied to the other thirteen fixtures. They share a construction pattern, but other rooms and moving viewpoints still need actual review. The successful Bath image hash is `0cc3c7ce81c53284308260670c2e4b38524d409d42e575723c9cf88257f35ae3`. The original Cycles surface hash is `b5003cc9588bed13d22b02be8fad2b357e17ffb549ea9680dda9454819c91d1d`; glazing geometry hash is `655896c42f23f6b59c3105ca8e865815051a4340016b6a95f20e8972dbbe597d`.

## Independent Living diagnosis

The Living room has no POINT or AREA light: its 28 emissive screen/cove meshes provide baked indirect illumination, with the scene Sun providing direct light. The source is therefore different from Bath. Rays from the actual downward-facing emitter surface to three selected wall samples tested the four nearest emitters per sample. Eleven of twelve segments reached their wall without an intermediate hit. Only one segment toward the **already bright upper wall** hit a screen crossbar. This does not support a broad self-occlusion explanation for the dark middle band. Sun rays toward all three selected samples are blocked by actual roofs/core/hearth geometry, including the upper bright sample.

Neither disabling Sun shadows nor zeroing volume intensity resolves the band. This does not prove that either Sun or volume GI is perfect; it shows that disabling either alone does not remove the abnormal spatial boundary. The three Bath tests cannot be generalized to this room.

The subsequent installed RNA inspection is recorded in `eevee-iteration05-screen-api.json`. `use_fast_gi` selects a faster approximation for high-roughness surfaces. `use_raytracing` enables the entire ray module, including Fast GI. Their scopes overlap: turning ray tracing off cannot be described as a pure screen-ray change. In the 5.2.1 implementation, turning only Fast GI off internally raises the tracing roughness threshold to 1, assigning those surfaces to the full tracing path. [Official ray-trace implementation](https://raw.githubusercontent.com/blender/blender/v5.2.1/source/blender/draw/engines/eevee/eevee_raytrace.cc)

Only `scene.eevee.use_fast_gi=False` was then changed in the frozen source. The actual 79.721-second image retains `use_raytracing=True`, `ray_tracing_method='SCREEN'`, every light's shadow flag and all seven VOLUME intensities at 1.0. The broad black band and bright top strip disappear. This isolates Fast GI's approximate rough-surface path as the source of that spatial discontinuity. However, stone joints are much less visible and the image is dim/noisy; it is not a final lighting or material PASS. No second ray-module-off image was needed to repeat a broader disable. Output `eevee-iteration05-living-fastgi_off.png`, SHA-256 `9526f0456a1b1d154c0daacbf69c1e42a0a891b784d7f219a397637509bd8b1f`.

The parent's iteration06 Cycles `renders/previews/iteration06-focus/CAM_MAIN_L1_LIVING_B.png` was also actually opened. It shows continuous wall illumination and clearer stone joints. It uses a revised hearth, CPU 32 samples and exposure +2.4, so it is a qualitative comparison, not a matched numeric reference. No iteration06 GI or film has been started by this subtask. `configure()` defaults have not been changed by this diagnostic; a separately configured preview can explicitly set `scene.eevee.use_fast_gi=False` before new image review. Moving-camera stability and broader-room quality remain untested.
