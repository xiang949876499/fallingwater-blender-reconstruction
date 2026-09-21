# Iteration 06 EEVEE preview review

**Renderable, but overall visual acceptance FAIL.** Seven actual GI bakes and nine 960×540 images completed. Every base PNG was opened at native resolution; all 27 exposure variants were reviewed in three comparison sheets. The verified Bath self-emitter and Living Fast GI corrections survive integration. Kitchen, Study, Laundry and guest-bedroom defects remain. No current-scene moving-camera quality, interactive FPS or final-film acceptance is claimed.

## Frozen source and independent preview

| Artifact | SHA-256 |
|---|---|
| `scene/Fallingwater_iteration06.blend` | `172b76340d1224a2b98f415b21042d19ad7fba4d849543d7156beb17e5fcf055` |
| Last seven-level GI checkpoint, `qa/eevee-iteration06/checkpoints/Fallingwater_GI_FW_PROBE_GUEST_L2.blend` | `88552c89a9f3bb83af981b12cc71a2c67a484d7e1b471e92aac07b4f9be48d3d` |
| `scene/Fallingwater_preview_iteration06.blend` | `e317241899808995f049e8d3343eac96c591cbecfddaa980949d6babb51ccce6` |

The source was not changed. The initial run completed all seven bakes and the first two images. The parent then supplied the separately stored corrected exterior POOL pose; the run was interrupted and the remaining seven images resumed from the final GI checkpoint using `--skip-bake`. No completed GI bake or image was repeated. The interrupted first-run status, log, checkpoints and completed images remain as evidence. The final preview incorporates POOL location (41,37,11), target (22,37,9.6), lens 35 mm from `eevee-iteration06-camera-overrides.json`. This is separate from the scene's embedded 120 room-camera configuration.

Guest Lounge A/B were deliberately omitted because their composition was under correction by the camera worker. Guest L2 Bath B substituted for that view. Later corrected Lounge images are not included in this nine-view review.

## Actual settings and cache scope

Blender 5.2.1 LTS, EEVEE, 32 render samples, four CPU preparation threads, 960×540, frame 1, AgX. Base exposure is +0.8 for every view. +0.8/+1.6/+2.4 exports reuse the same linear Render Result; these are nine renders, not 27 renders.

- `use_fast_gi=False`, `use_raytracing=True`, SCREEN tracing retained, full tracing resolution and precision.
- Every actual light retains `use_shadow=True`; energy, radius, placement and visible fixture meshes are unchanged.
- Only `FW_FURN_MAIN_B_BATH_practical_ceiling_lamp_C_03_bulb_photometric_proxy` excludes its own emissive filament. Its bulb, guard, walls and all other casters remain eligible. Other thirteen fixtures have no such exclusion.
- `eevee_glass.apply(scene)` runs **after** `configure()`, preserving the selected thin-window EEVEE output and physical 8/12 mm pane geometry. The existing checked Living SPHERE is retained; no blind per-room sphere additions.
- All seven VOLUMEs capture world, indirect light and emission with intensity 1, 64 bake samples, surfel density 8 and capture distance 20 m. Their intended room coverage is not independent per-room lighting acceptance.

| Probe group | Grid | Intended room records | Actual bake seconds |
|---|---|---:|---:|
| MAIN_B | 8×6×4 | 4 | 33.350 |
| MAIN_L1 | 20×14×4 | 9 | 4.797 |
| MAIN_L2 | 12×8×4 | 10 | 4.328 |
| MAIN_L3 | 10×10×4 | 6 | 3.321 |
| GUEST_L1 | 17×15×4 | 8 | 3.640 |
| GUEST_B1 | 5×4×4 | 3 | 3.853 |
| GUEST_L2 | 6×9×4 | 5 | 4.390 |

Total **57.679 seconds**. Every bake operator returned FINISHED and each result was saved as a checkpoint. Later groups reuse prepared scene resources; these timings are not isolated GPU benchmarks.

## Nine actual image findings

| Camera | Result | Actual finding | Render seconds |
|---|---|---|---:|
| MAIN_B_BATH_B | Partial local correction | Washbasin and door are readable; no giant triangle in the new pose. Close composition shows only part of the bathroom. | 29.947 |
| MAIN_L1_LIVING_B | Partial local correction | Former horizontal band is gone. Stone joints are weak and surfaces appear soft/flat; material quality remains below Cycles reference. | 24.170 |
| MAIN_L1_KITCHEN_B | FAIL lighting | Broad black zone above back counter and across lower parts of upper cupboards remains. Exposure does not remove it. | 57.047 |
| MAIN_L3_STUDY_B | FAIL lighting | Large blurred dark wall rectangle remains. The lower bright gap and shading discontinuity need separate diagnosis. | 11.078 |
| GUEST_B1_LAUNDRY_B | FAIL lighting | A large V-shaped shadow remains on the left door. This fixture was intentionally not changed by the Bath-only override. | 12.083 |
| GUEST_L2_BEDROOM_NORTH_B | FAIL lighting | Bed, cupboard and window are readable; large dark rectangle/halo persists on left wall and cupboard. | 21.942 |
| GUEST_L2_BATH_B | Partial composition | Toilet and walls are readable. A dark patch enters from upper left, preventing lighting acceptance. | 12.993 |
| HERO | Partial exterior | Main house and glazing are visible. Forest, water and surface detail are still visibly synthetic; not photorealistic acceptance. | 17.329 |
| GUEST_POOL | FAIL window region | Corrected exterior pose shows pool and guest house, but blurred dark shading remains in the central window/interior region. Pool reflection is very soft. | 29.564 |

Nine completed renders total **216.153 seconds**. First render in each process includes initial setup. The repeated preliminary first-camera preparation interrupted during handoff is not included in completed-image timing. These are offline render times, not FPS.

Exposure sheets `eevee-iteration06-exposure-contact-1.png` through `-3.png` were actually opened. +1.6 improves Bath fixture readability; +2.4 improves Living visibility while leaving material softness evident. +2.4 still leaves the Kitchen/Study/guest-bedroom dark regions. HERO and POOL are most usable at the base +0.8; higher brackets wash out the exterior. These comparisons are inspection preferences, not final calibrated exposures. The saved preview still records +0.8 for the rendered cameras. Native +2.4 Bath and Living images were also opened; Study +2.4 was additionally opened for the subsequent volume diagnosis. Other brackets were examined on the comparison sheets.

## Persisted helper behavior and Cycles boundary

`configure(scene, samples=32, fast_gi=None)` keeps prior behavior when no choice was saved. An explicit Boolean choice is persisted as `scene['fw_eevee_use_fast_gi']`; a subsequent default call honors it. The CLI offers `--fast-gi preserve|on|off`, `--self-emitter-exclusions`, and `--camera-settings`. Metadata is written to the scene and setup report. Default configuration does not automatically exclude every lamp.

The factory-scene check verified default compatibility, explicit Fast GI disabling, and a later default call honoring the saved choice. A new Blender process then reopened the final **e317…** preview and verified the persisted setting, seven bake records, single Bath exclusion and corrected POOL pose. It ran default `configure()` followed by `eevee_glass.apply()` and confirmed unchanged original Cycles glass output hash `b5003cc9588bed13d22b02be8fad2b357e17ffb549ea9680dda9454819c91d1d` and glazing geometry hash `655896c42f23f6b59c3105ca8e865815051a4340016b6a95f20e8972dbbe597d`.

**Shadow linking is engine-independent.** Original Cycles glass shader preservation does not mean the active exclusion has no Cycles lighting effect. The fresh-process check therefore called the parent's actual `render_views.configure_engine(scene,'CYCLES',32,'CPU')`; it restored exactly the helper-owned Bath link and left the original glass hash unchanged. It did not render or save. Results: `eevee-iteration06-config-check.json`, `eevee-iteration06-reopen-check.json`. The source and final preview hashes remained unchanged after this read-only verification.

## Remaining causes and bounded next work

The matched iteration05 experiments establish two causes: Bath's own-filament proxy shadowing, and Living's rough-surface Fast GI discontinuity. Their evidence and current API/source limitations are in `eevee-iteration05-shadow-review.md`. The subsequent Laundry-specific experiment in `eevee-iteration06-followup-review.md` confirms that excluding only its own filament removes its giant V-shaped door shadow. That candidate was not saved to this nine-view checkpoint.

The Kitchen/Study/guest-bedroom rectangles remain with Fast GI already off. The Study comparison with the entire ray module disabled failed; the later seven-volume intensity-zero comparison also leaves the rectangle in place. Matched Cycles images show continuous dark walls without the exaggerated rectangle edges. Actual Study rays put the bright upper/lower wall outside its inset volume and the dark center inside; scale-aware inspection also finds very coarse surfel capture. A separate MAIN_L3 Z-extension and one-volume rebake reduced upper/lower overbrightness but failed overall. A further original-bounds density8→32 test changed local shading but left the broad rectangle and surrounding brightness; it also failed. These are separate candidates, not proof of corrupted cached normals. Details are in `eevee-iteration06-volume-review.md`, `eevee-iteration06-coverage-review.md` and `eevee-iteration06-density-review.md`. The helper's nominal-spacing report formula has been corrected and independently checked; production probe defaults are unchanged. Guest POOL's dark region should also be separated into glass reflection and interior illumination before adding probes.

The practical MAIN_L3 XYZ-margin/resolution/density candidate is now documented in `eevee-iteration06-practical-review.md`. The official padding math yielded a reproducible sufficient interior margin, and the rendered candidate removed much of the excessive World brightness. Internal dark patches remained, so it is still a failed, separately saved candidate. Its `profile.json` records a PASS for the defined geometric margin check separately from visual FAIL; it has not been applied to the production preview or the later sky/source revision. A subsequent no-rebake stone Bump-strength-zero discriminant left the large pattern effectively unchanged; `eevee-iteration06-stone-normal-review.md` records that negative result. Do not disable stone relief as a fix or confuse this shading-normal test with capture-normal verification.

The Laundry-only experiment reused the checked opt-in helper while preserving every other caster. Broader exclusions, new reflection probes, changed light strengths, global GI-default adoption or final-film rendering are not justified by the present images. The parent owns the two-frame animation workflow/reuse check; it is separate from visual acceptance here. Only the separately verified spacing-report metadata has changed in the helper; the visual candidates did not change global defaults.

Machine-readable source chain, image hashes, findings, bake timings and settings are in `eevee-iteration06-summary.json`. The original and resumed setup reports remain under `qa/eevee-iteration06/`; both logs remain at `qa/eevee-iteration06-build.log` and `qa/eevee-iteration06-resume.log`.
