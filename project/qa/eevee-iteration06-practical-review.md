# Iteration 06 practical MAIN_L3 coverage candidate

**Partial removal of excessive World contribution; overall visual FAIL.** The practical XYZ coverage/lattice/density configuration removes most of the large overbright surrounding wall regions and brings overall brightness much closer to the matched physical reference. Internal dark patches, an overly dark middle wall and uneven ceiling shading remain clearly visible. The candidate is saved independently, not adopted as a production or film-ready configuration.

## Why an enclosing box alone is insufficient

Blender 5.2.1's atlas-load shader gives outer padding voxels distant-probe lighting, and treats padding as valid during cell interpolation. Thus a surface can lie inside the probe object and still interpolate unoccluded World lighting from its padded outer layer. This explains why merely extending Z until a surface is just inside the box is insufficient. The local intensity multiplier does not eliminate that padding contribution. [Blender 5.2.1 atlas loading](https://raw.githubusercontent.com/blender/blender/v5.2.1/source/blender/draw/engines/eevee/shaders/eevee_lightprobe_volume_load.bsl.hh).

For one axis with object bounds L,H and N nominal samples, spacing `d=(H-L)/(N+1)` and runtime coordinate `q=(P-L)/d+0.5`. Original samples occupy q=1.5 through N+0.5; outer samples are padding. Keeping the full interpolation cell away from padding requires at least one spacing of interior margin. Normal/view sampling biases can move the query by up to their absolute sum in grid units. Therefore the sufficient bound used here is `margin > (1+abs(normal_bias)+abs(view_bias))*d`. It also exceeds the shader's maximum 0.75-cell stochastic border-transition region. This is a geometric sufficiency rule for avoiding direct padding interpolation, not a guarantee that the baked values are physically correct. [Blender 5.2.1 volume sampling](https://raw.githubusercontent.com/blender/blender/v5.2.1/source/blender/draw/engines/eevee/shaders/eevee_lightprobe_volume.bsl.hh).

Here normal bias is 0.3 and view bias is zero. The profile uses maximum spacings (0.8,0.8,0.32) m, each finer than the original lattice; margin is `1.35*maximum_spacing+0.05 m`, and resolution is `ceil(expanded_length/maximum_spacing)-1`. Consequently actual spacing is no larger than requested and actual margin exceeds 1.3 cells on every axis. The saved Study camera and all three previously inspected wall points pass this check; their smallest bound distance is 2.5967 cells.

## Actual geometry and configuration

821 renderable meshes were included by MAIN_L3 name or L3 room tags. The set includes actual wall, slab, ceiling, roof and associated details, plus the original probe XY domain and saved Study camera. Geometry crossing below the evaluated Study slab bottom is clipped to that bottom when defining this L3 region, rather than extending the candidate over the entire lower stair flight. The selection and each evaluated bound are recorded in `profile.json`; the room metadata ceiling is not used as the vertical limit.

| Item | Practical candidate |
|---|---|
| Actual domain minimum XYZ | −4.506400,8.274800,5.044150 m |
| Actual domain maximum XYZ | 10.699800,24.592747,7.640000 m |
| Added margin XYZ | 1.130,1.130,0.482 m |
| Final probe minimum XYZ | **−5.636400,7.144800,4.562150 m** |
| Final probe maximum XYZ | **11.829800,25.722747,8.122000 m** |
| Grid resolution | **21×23×11 = 5,313 samples** |
| Actual nominal spacing XYZ | **0.793918,0.774081,0.296654 m** |
| Required bias-safe margin XYZ | 1.032094,1.006305,0.385650 m |
| RNA surfel density | 32 |
| Physical surfel interval/radius | **0.290280 / 0.145140 m** |

This is explicitly a **combined practical configuration**, not a single-variable causal experiment. Physical surface density differs from the earlier density32-only trial (interval 0.205734 m), because the expanded probe's maximum scale increases. It is still substantially finer than the original density8 interval of 0.822934 m. Fixed scalar surface/escape biases now convert to 0.008091 / 0.016181 m; nominal point positions, cell spans and normal-bias distances also change with the lattice. No claim is made that only coverage changed.

All actual lights retain their transforms, powers, colors, other scalar settings, shadow flags and shadow-link collections. Ray tracing stays on and Fast GI off. Only the original Bath own-filament exclusion remains. No fill light, emissive adjustment, new reflection probe or shadow disabling was introduced. Original Cycles glass and physical glazing geometry hashes are retained. All other object transforms and render visibility are unchanged; the only differing object transform is MAIN_L3's volume. Other probe data/matrices are unchanged.

Only MAIN_L3 was selected for one `subset='ACTIVE'` cache bake. The other six caches were not requested for rebaking; their internal cache arrays were not byte-hashed. The expanded L3 volume overlaps lower-floor probe regions, so unchanged settings do not imply identical shading at every other level's blending boundary. Only Study B is visually reviewed here.

## Budget and execution

The read-only budget used actual transformed triangle areas with capture-box rejection. It examined 10,515 meshes, 7,333,831 evaluated vertices and 7,742,037 triangles; 5,295,622 triangle bounding boxes overlap capture bounds. Three-axis projected area is 29,528.45 m². With 3.444945 surfels per meter, the planning estimate is about 350,434 surfels and **454 MiB** of auxiliary capture/grid work, below an 8 GiB guard. This is a planning allowance, not a measured GPU allocation or rigorous upper bound.

Single ACTIVE bake: **31.789 seconds**, FINISHED. Single render: **22.164 seconds**. Process exit 0. Camera `CAM_MAIN_L3_STUDY_B`, saved pose, 28 mm, frame 1, EV+2.4, 960×540, 32 samples, four CPU preparation threads. The candidate was actually opened at native size and compared with the already inspected matching EEVEE baseline and physical Cycles reference. No second view, bracket or second candidate was rendered. The usual shutdown `Unable to delete file` message remains in the log; both saved artifacts decoded/hashed and no evidence was deleted.

## Actual visual result

| Display pixel | Original EEVEE RGB | Practical RGB | Cycles RGB |
|---|---|---|---|
| (720,275), middle wall | 35,31,20 | **5,4,3** | 27,26,19 |
| (720,125), upper wall | 141,143,129 | **34,36,31** | 19,17,10 |
| (710,454), lower solid wall | 135,135,119 | **25,25,20** | 30,27,20 |
| (600,60), ceiling | 128,135,134 | **7,8,8** | 26,23,17 |
| (350,230), left wall | 91,87,71 | **1,1,0** | 7,5,2 |

Full-image mean absolute display-RGB difference to Cycles decreases from **64.495/255 to 10.305/255**. This describes the large brightness correction, not a perceptual quality score or proof of acceptance. The middle wall and ceiling are now too dark, with visible internal blotches. A narrow bright bottom strip also persists in the parent's physical Cycles images at both sky strengths; its geometric cause remains undiagnosed by this task.

The selected camera and prior wall hits are now well beyond the padding/border region, so remaining interior patches cannot all be explained as those points directly falling outside this probe. A subsequent one-image test zeroed only the active stone Bump strength without rebaking; the large pattern remained effectively unchanged (mean display RGB difference0.121159/255). See `eevee-iteration06-stone-normal-review.md`; do not adopt bump disabling. Baked SH, per-cell validity and virtual offsets remain unavailable through the inspected RNA interface, and that material test does not test capture normals. This candidate supplies a reproducible margin rule and a substantial World-light correction, but **does not yet supply an accepted complete EEVEE lighting solution**.

## Persistent artifacts and boundaries

| Artifact | SHA-256 |
|---|---|
| Original preview, unchanged | `e317241899808995f049e8d3343eac96c591cbecfddaa980949d6babb51ccce6` |
| Physical Cycles06 source, unchanged | `172b76340d1224a2b98f415b21042d19ad7fba4d849543d7156beb17e5fcf055` |
| `eevee-iteration06-practical/CAM_MAIN_L3_STUDY_B_EV2p4.png` | `92718e1e6a1c6c3763b49e30dccc81c11b5b6a2eba8ab5aac49446697dc23d9d` |
| `eevee-iteration06-practical/Fallingwater_main_l3_coverage_candidate.blend` | `cee741ac1c25c84f487c4967158a4c29bb3552871102338442f9b9fc85488ebf` |

`profile.json` preserves the explicit bounds, resolution, density, derivation, geometry selection and point checks. The candidate also stores compact `fw_eevee_coverage_profile_json` plus an explicit unaccepted-candidate scope. `report.json` records every original/final probe state, invariant check, timing and image result; `preflight.json` records budget evidence. The source-to-candidate driver is `eevee-iteration06-practical.py` and the completed log is `eevee-iteration06-practical.log`.

Neither EEVEE helper was changed by this experiment; the previously verified metadata-only spacing correction remains. No production default, physical scene, global preference, lower-level cache or final film was overwritten. The forthcoming sky/source change requires new bakes; this frozen06 profile must not be represented as already tested on that later scene. This bounded task is complete, the GPU is released, and no further diagnostic has been started.
