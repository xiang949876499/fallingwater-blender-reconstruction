# Iteration 05 EEVEE integration and seven-level GI review

**Usable for rendering/debugging; overall visual acceptance FAIL.** All seven requested volume bakes completed and nine actual images were rendered, hash-verified and opened. Glazing is clearer than the original screen-refraction branch, but several rooms show severe broad dark bands or patches. Two views are unusable because of camera obstruction. No final film or current-scene moving-camera acceptance was performed.

## Frozen files

| File | SHA-256 | Bytes |
|---|---|---:|
| `scene/Fallingwater_iteration05.blend` | `6bcfee7841c22e8e2b636352cfca79ae94968afb4235fc20cdc57e250ae046ff` | 43,415,677 |
| `scene/Fallingwater_preview_iteration05.blend` | `b855de89492af8ae31ae4d53bb2674f518ea13cf2e8f1585b2b9a31b35511939` | 65,108,076 |

The preview was reopened in a new Blender process with this exact hash to produce the four additional-level views. It contains the seven baked volume probes and one checked living-room SPHERE reflection capture. Only this independently saved preview was changed; the frozen iteration05/working model was not edited by this subtask.

`eevee_preview.configure()` ran before `eevee_glass.apply(scene)`, then all seven GI groups were baked from the scene's embedded FW_ROOMS.json. Glass geometry and original Cycles-surface hashes were unchanged during initial application and the fresh-process reapplication. The Cycles hash is `b5003cc9588bed13d22b02be8fad2b357e17ffb549ea9680dda9454819c91d1d`; glazing geometry hash is `655896c42f23f6b59c3105ca8e865815051a4340016b6a95f20e8972dbbe597d`. No additional lamp or intensity multiplier was introduced. See `eevee-glass-review.md` for the explicitly approximate thin-window model and its boundaries.

## Actual GI bakes

All use 64 bake samples, surfel density 8, world/indirect/emission capture enabled, capture distance 20 m and intensity 1.0. Each operator returned FINISHED. Each level was saved separately under `qa/eevee-iteration05/checkpoints/` before proceeding.

| Group | Grid | Intended room records | Seconds |
|---|---|---:|---:|
| MAIN_B | 8×6×4 | 4 | 61.263 |
| MAIN_L1 | 20×14×4 | 9 | 5.418 |
| MAIN_L2 | 12×8×4 | 10 | 5.501 |
| MAIN_L3 | 10×10×4 | 6 | 5.176 |
| GUEST_L1 | 17×15×4 | 8 | 5.108 |
| GUEST_B1 | 5×4×4 | 3 | 5.317 |
| GUEST_L2 | 6×9×4 | 5 | 5.610 |

Total: **93.393 seconds**, including initial setup in the first group. The other groups reuse prepared scene resources, so per-layer times are not isolated hardware comparisons. The 45 room records indicate intended volume coverage, not 45 independently verified lighting solutions. Exact bounds and achieved grid spacing are saved in `eevee-iteration05/eevee-iteration05-setup.json` and `eevee-iteration05-summary.json`.

## Five required plus four additional actual views

All nine base images use Blender 5.2.1 LTS EEVEE, 960×540, 32 samples, AgX, exposure +0.8 and four CPU preparation threads. EEVEE uses the graphics backend. Each base PNG was individually opened at native resolution; the nine-image contact sheet was also opened. The extra exposure exports are candidates from the same linear image, not additional renders or certified exposure settings.

| Saved iteration05 camera | Result | Finding | Render seconds |
|---|---|---|---:|
| MAIN_L1_LIVING_B | FAIL lighting | Clear window transmission, but severe horizontal dark region across fireplace/dining wall. +1.6 was also opened and did not resolve it. | 37.704 |
| MAIN_L1_KITCHEN_B | FAIL lighting | Broad dark band obscures cabinets, wall and appliances. | 20.022 |
| MAIN_L2_MASTER_B | Partial glazing only | Clear windows/open casement; dark bands remain on column and desk. | 21.233 |
| GUEST_L1_LOUNGE_B | FAIL camera | Almost full-frame nearby wall/fireplace. Parent confirms old camera position intersects the new hearth; retained as negative evidence. | 14.079 |
| MAIN_OVERVIEW | FAIL camera | Foreground foliage obstructs building and glazing, preventing exterior-window acceptance. | 27.203 |
| MAIN_B_BATH_B | FAIL lighting | Visible fixture/cork walls, but enormous inverted triangular dark patch with broad edges. | 59.724 |
| MAIN_L3_STUDY_B | FAIL lighting | Large black rectangle and thick shading halos around wall/desk; bright lower wall edge also needs checking. | 15.998 |
| GUEST_B1_LAUNDRY_B | FAIL lighting | Appliances are visible, but the left door has a large V-shaped dark patch; uneven ceiling shading. | 18.763 |
| GUEST_L2_BEDROOM_NORTH_B | Partial glazing only | Clear window view; black patches/halos remain around cabinet/wall furniture. | 29.382 |

Nine renders total **244.108 seconds**. These are offline render timings, not interactive FPS. Partial glazing results are not whole-image PASS. The source cameras were preserved as requested; later corrected room cameras require new evidence.

The prior Cycles fireplace view `renders/previews/iteration04/CAM_MAIN_L1_LIVING_B.png` was opened as a qualitative comparison. Its illumination is more continuous across the fireplace and dining wall. It has a different scene revision/independent exposure, so it is not a matched numeric reference. The new EEVEE dark-band source is not yet established; screen ray approximation, volume interpolation/visibility and practical fixture shadows need isolated diagnostics. No shadow disabling, intensity zeroing or hidden fill light has been adopted as a production fix.

## Outputs and handoff

- `qa/eevee-iteration05-nine-views-contact.png`: unretouched nine-view review sheet.
- `qa/eevee-iteration05-summary.json`: scene/output hashes, exact bake settings, all per-view findings and timings.
- `qa/eevee-iteration05/`: first five renders plus exposure candidates and incremental bake report.
- `qa/eevee-iteration05-additional/`: four additional level renders, exposure candidates and new-process report.
- `scene/Fallingwater_preview_iteration05.blend`: renderable seven-level cache checkpoint; **not visually accepted**.

The helper now supports embedded room records, configurable resolution/thread count, applying the reviewed glazing after engine configuration, optional per-level checkpoints, source/render hashes and an explicit output scene path. It keeps the previous interface defaults available. No changes were made to the root-owned animation renderer.

The subsequent bounded diagnosis is documented in `eevee-iteration05-shadow-review.md`. Bath's enormous triangle is caused by the point proxy shadowing its own emissive filament; one-light self-emitter exclusion removes it without disabling other casters. Living's horizontal band disappears when only Fast GI is disabled, retaining full screen ray tracing, actual shadows and baked volume light. Both are local symptom results, not final image acceptance; Living's stone detail and noise still need work. These preview overrides were not saved to this checkpoint. Corrected GuestLounge_B and exterior camera views, broader current-scene window angles, stable moving-camera QA and final film quality remain pending.
