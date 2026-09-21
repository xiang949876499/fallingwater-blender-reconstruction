# Iteration 06 volume coverage and capture diagnosis

**The single Study B intensity-zero variant fails to remove the dark wall rectangle. Coverage/blending and coarse surface capture are concrete suspects; corrupted cached normals are not established.** One additional 960×540 image was rendered, not a new seven-level bake. The independent preview and physical Cycles source remain unchanged. All three parent-provided Cycles references, the matched Study EEVEE baseline and this candidate were actually opened at native size.

## Controlled result

Source: `scene/Fallingwater_preview_iteration06.blend`, SHA-256 `e317241899808995f049e8d3343eac96c591cbecfddaa980949d6babb51ccce6`. Camera `CAM_MAIN_L3_STUDY_B`, frame 1, lens 28 mm, location `(-0.55221999,11.97404957,6.88635015)`, Euler radians `(1.46607685,0.00000005,0.49862689)`. This is the saved iteration06 camera used by the parent's physical reference, not a replacement pose.

Exactly seven existing VOLUME intensities changed from 1 to 0. Ray tracing stayed on; Fast GI stayed off. All real light transforms, colors, energy and shadow flags, the single Bath exclusion, probe matrices and every other scalar probe property were compared before/after and asserted unchanged. Original Cycles glass shader and glazing geometry signatures were also retained. No configure/apply call, rebake, source save, exposure bracket, new lamp or second candidate was used.

The render used **960×540, 32 samples, four CPU preparation threads, AgX, EV+2.4** to match the supplied Cycles reference. It completed in **34.906 seconds**, process exit 0. PNG SHA-256: `c47451cf5efcbe091d2f79eca9733807cabf24d116120b28dcf760677b769b79`. The log retains Blender's shutdown message `Unable to delete file`; the render completed, output decoded correctly and the source hash was unchanged. No cleanup deletion was attempted.

The rectangle remains in the same position with nearly the same outline. It becomes slightly darker, while the bright upper and lower wall regions remain. Full-image mean absolute RGB difference from the existing EEVEE EV+2.4 baseline is **1.606 code values out of 255**; maximum channel change is 41. This is display-image comparison, not a linear-light energy measurement. Intensity zero scales captured radiance; it does not remove probe selection, validity, visibility or bounds. Thus this experiment rejects the intensity-zero fix but does **not** exclude probe coverage or visibility as the cause.

## Same-camera geometry and coverage evidence

All three inspected pixels first hit `MAIN_L3_study_core_1`, face 50, front-facing normal `(0,-1,0)`, wall Y=16.410301. The MAIN_L3 probe bounds are Z=5.384150 to 7.184150. Its room floor/ceiling metadata are Z=5.264150 and 7.304150: the helper intentionally omitted 0.12 m at each end.

| Pixel, top-left origin | Wall Z, m | Probe coverage | Baseline RGB | Zero-intensity RGB | Cycles RGB |
|---|---:|---|---|---|---|
| (720,275), rectangle | 6.405839 | Inside | 35,31,20 | 33,27,15 | 27,26,19 |
| (720,125), upper wall | 7.262506 | Above | 141,143,129 | 141,143,129 | 19,17,10 |
| (710,454), lower wall | 5.332478 | Below | 135,135,119 | 134,134,119 | 30,27,20 |

The captured middle wall is close to the dark physical reference at these sample points; the surrounding EEVEE wall is much brighter. This supports investigating excessive boundary/world contribution instead of adding fill lights to brighten the rectangle. The lower sample hits solid wall, despite the inspection label `lower_bright_gap`; a separate narrow bright strip below it persists in the parent's physical Cycles images at two sky strengths. That strip's geometric cause is not diagnosed here and must not be classified solely as an EEVEE artifact.

The exact Blender 5.2.1 volume shader selects a containing volume, blends near its border, and eventually falls back to the world grid. Its nominal sample position is `local = -1 + 2*(index+1)/(resolution+1)`. With the runtime transform, object bounds are the coverage bounds; normal bias shifts sampling in grid units after volume selection. These source facts support the coverage hypothesis but do not replace a controlled corrected-coverage bake. [Blender 5.2.1 volume sampling source](https://raw.githubusercontent.com/blender/blender/v5.2.1/source/blender/draw/engines/eevee/shaders/eevee_lightprobe_volume.bsl.hh).

## Actual lattice and capture scale

Bounds, transforms, complete local RNA descriptions, nominal centers and geometry rays are stored in `eevee-iteration06-volume-inspect.json`. Positions here are **unshifted nominal samples**, not extracted baked virtual offsets.

| Group | Grid | Correct nominal XYZ spacing, m | Surfel spacing, m |
|---|---|---|---:|
| MAIN_B | 8×6×4 | 1.0755,0.9759,0.3820 | 0.6050 |
| MAIN_L1 | 20×14×4 | 1.3156,1.2059,0.4320 | 1.7267 |
| MAIN_L2 | 12×8×4 | 1.1598,1.0599,0.3860 | 0.9423 |
| MAIN_L3 | 10×10×4 | 1.1759,1.1970,0.3600 | 0.8229 |
| GUEST_L1 | 17×15×4 | 1.3038,1.3071,0.3840 | 1.4668 |
| GUEST_B1 | 5×4×4 | 0.9907,0.7642,0.3880 | 0.3715 |
| GUEST_L2 | 6×9×4 | 0.9889,1.1477,0.3760 | 0.7173 |

**Metadata correction:** old `eevee_preview.py` field `actual_grid_spacing_m` divides bounds length by `resolution-1`. Blender's actual nominal interval uses `resolution+1`. The earlier reported intervals were too large; object placement, resolution and completed caches were unaffected by that reporting error. This diagnostic records the correction without modifying helper defaults.

Blender converts the RNA surfel density to `density/max(object scale)` and uses surfel radius `0.5/converted_density`. With density 8, the Study radius is about 0.4115 m; Guest L2 radius is 0.3586 m. The propagation implementation also enlarges coverage to prevent leaks, with an acknowledged shadow/emission inflation tradeoff. Therefore density 8 across an entire floor is materially coarser than 8 samples per meter. This is a second plausible source of overly broad occlusion, separate from volume bounds. Runtime validity/dilation and intensity are separate inputs. [Blender 5.2.1 capture/atlas source](https://raw.githubusercontent.com/blender/blender/v5.2.1/source/blender/draw/engines/eevee/eevee_lightprobe_volume.cc).

The Study room contains 32 nominal lattice centers; two lowest centers first hit backfaces of bench cushions in five of six tested axis directions. Guest North Bedroom contains 48 centers; three lowest centers intersect mattress or bedside drawer geometry. These are geometric suspects, not measured cached validity. Study's eight nearest nominal samples to the black wall have seven clear segments and one blocked by the real 0.42 m core wall. The observed wall face itself is not reversed. Local RNA exposes no baked SH, validity or virtual-offset array, so the inspection cannot certify what correction/dilation was actually baked.

## Parameters and limits

All seven probes use intensity 1 in the saved source, normal bias 0.3, view bias 0, facing bias 0.5, validity threshold 0.4, dilation threshold 0.5/radius 1, surface bias 0.05, escape bias 0.1, density 8, 64 bake directions, capture distance 20 m, and world/indirect/emission capture enabled. The active API describes validity as front-facing hit ratio and dilation as copying neighboring valid samples. `capture_world` explicitly warns about losing correct blending to surrounding volumes.

`visibility_buffer_bias`, `visibility_bleed_bias`, `visibility_blur`, `visibility_collection` and `invert_visibility_collection` are all marked **Deprecated** in this Blender's RNA. They are not suitable modern controls for a speculative fix. `clip_start` describes reflection clipping and should not be treated as volume validity evidence.

The parent Cycles references show no exaggerated Guest North Bedroom rectangle, no Kitchen middle black band, and no Study large rectangle edge. Study's separate bottom opening remains physically present. Those three references were inspected but only Study received an additional EEVEE diagnostic. Prior intensity-zero tests involved Bath and Living; this did not repeat an earlier same-camera Study test.

The subsequent **separate MAIN_L3 Z-coverage candidate** retained physical surfel density and all light controls, rebaked only that volume and rendered one matched Study image. It reduced upper/lower overbrightness but failed overall; changing Z bounds also changes the nominal lattice and effective surface/escape offsets. A further original-bounds density8→32 test slightly changed local illumination but left the large rectangle and surrounding bright regions. Both failed independently. A later practical XYZ margin/resolution/density configuration removed most surrounding overbrightness but retained internal dark patches and also failed overall. See `eevee-iteration06-coverage-review.md`, `eevee-iteration06-density-review.md` and `eevee-iteration06-practical-review.md`. No whole-preview correction, final animation or visual PASS is claimed.

Evidence: `eevee-iteration06-volume-zero-study.png/json`, `eevee-iteration06-volume-zero.log`, `eevee-iteration06-volume-inspect.py/json/log`, and `eevee-iteration06-volume-summary.json`. Source and helper hashes remain unchanged. This bounded diagnostic is complete and the GPU has been released.
