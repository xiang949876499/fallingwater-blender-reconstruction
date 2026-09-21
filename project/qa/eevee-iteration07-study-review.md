# Iteration 07 Study EEVEE readiness check

**Visual result: FAIL.** One MAIN_L3 cache baked and one 960×540 image rendered successfully, but this is not an accepted full-building preview. The actual image still has a broad dark wall band, dark lobes behind the chair, a dark ceiling field and excessive brightness near the upper wall. These are absent from the matched Cycles reference. The old narrow floor-perimeter bright strip is absent in both current images.

Both images below were opened at native resolution for review:

- Candidate: [Study EEVEE, EV 2.4](eevee-iteration07-study/CAM_MAIN_L3_STUDY_B_EV2p4.png)
- Physical reference: [Study Cycles, EV 2.4](../renders/previews/iteration07-focus/CAM_MAIN_L3_STUDY_B_EV2p4.png)

The new floor geometry and sky strength, fresh cache, and reduction from the old seven volumes to one volume make this an integration check. It does not establish a single-variable cause. The remaining dark pattern is not explained merely by the old physical floor gap, and the earlier normal-strength-zero negative result is retained in [the 06 report](eevee-iteration06-stone-normal-review.md). Further causes in GI capture or reconstruction remain unresolved.

## Actual execution and scope

Frozen source: `scene/Fallingwater_iteration07.blend`, SHA-256 `bf50530009e4a93315915815473188c91d891272ef2d8e9e0169b704bd2e2f16`, verified before and after. Source unchanged.

Independent saved candidate: `qa/eevee-iteration07-study/Fallingwater_preview_iteration07_study.blend`, SHA-256 `3843e7262c6c2a5b2c5f77f61128942f062aeed8d69cf045913fdb3b178ce261`.

Candidate PNG SHA-256: `2f4fa6743f0d45495b919e1902ec5b547838a0cb471d68f35a0578fc6cb4d80f`.

Physical reference PNG SHA-256: `d4fb43a837ac479e99731e900ec55f1ffd37a5b956ecbb3b8cf509e428b4ea5b`. Its benchmark records the same frozen source, frame 48, 960×540, 32 samples, AgX/None, CPU. The reference used here is the explicitly exported EV 2.4 bracket, not its base file (which has camera exposure 3.0).

- Blender 5.2.1 LTS, EEVEE preparation threads 4.
- Exactly one ACTIVE bake, MAIN_L3: **53.529 seconds**, operator FINISHED.
- Exactly one StudyB render: **34.707 seconds**, process exit 0, PNG opened.
- Frame **48**, EV **2.4**, **960×540**, **32 samples**, AgX/None, gamma 1.
- Saved source camera: location `(-0.552220, 11.974050, 6.886350)`, Euler `(1.466077, 0.000000050, 0.498627)`, lens 28 mm; no pose or lens override.
- MAIN_B, MAIN_L1, MAIN_L2, GUEST_L1, GUEST_B1, GUEST_L2: **NOT_BAKED**. Only StudyB was visually checked. No motion rendered.
- The helper adds its established Living SPHERE reflection capture, validated by six actual placement rays. This is separate from the sole diffuse VOLUME cache; it does not make Living or the other levels baked.
- Log retains the usual shutdown `Unable to delete file` warning. The render, saved file, exit status and immutable source hash were verified independently.

Saved scene properties explicitly state the one-level scope and the six NOT_BAKED levels. Its visual status remains NOT_REVIEWED because the scene was saved before opening the PNG; the reviewed JSON and this report record **FAIL**. No second save was done merely to rewrite this status, so the reported candidate SHA remains stable.

## Recalculated geometry, spacing and cost

The profile was recomputed from 821 current renderable MAIN_L3-prefixed or L3-room-tagged evaluated meshes, the embedded interior-room XY domain and saved StudyB camera. Cross-level geometry below the actual Study slab bottom at Z 5.044150 was clipped for this L3 domain. No metadata room-height assumption determined the actual wall/ceiling height. The bounding extents happen to equal the earlier practical candidate; the mesh contents, capture and sky are new.

| Quantity | Actual value |
|---|---|
| Actual domain minimum | −4.506400, 8.274800, 5.044150 m |
| Actual domain maximum | 10.699800, 24.592747, 7.640000 m |
| Probe minimum | −5.636400, 7.144800, 4.562150 m |
| Probe maximum | 11.829800, 25.722747, 8.122000 m |
| XYZ margin | 1.130, 1.130, 0.482 m |
| Nominal resolution | 21×23×11 = 5313 points |
| Actual nominal spacing | 0.793918, 0.774081, 0.296654 m |
| RNA surfel density | 32 |
| Converted surfel spacing | 0.290280 m |
| Effective surface / escape offset | 0.008091 / 0.016181 m |

Blender's [sampling source](https://raw.githubusercontent.com/blender/blender/v5.2.1/source/blender/draw/engines/eevee/shaders/eevee_lightprobe_volume.bsl.hh) places nominal samples with the `resolution + 1` denominator. Its [load source](https://raw.githubusercontent.com/blender/blender/v5.2.1/source/blender/draw/engines/eevee/shaders/eevee_lightprobe_volume_load.bsl.hh) gives padding samples distant/world illumination. The margin exceeds `(1 + abs(normal_bias) + abs(view_bias)) × actual spacing` on every axis. Current frame-48 wall hits and camera were recast; their minimum margin is 2.5967 cells, above the required 1.3. This verifies geometric coverage, not lighting validity.

Density is not an absolute per-metre constant: Blender divides RNA density by the largest object scale. Here density 32 becomes 3.444945 per metre. The grid and capture offsets are explicitly recorded rather than claiming that changing coverage preserves every physical sampling scale.

The read-only cost estimate used world-space triangle projected areas and capture-AABB culling: 10,509 meshes, 7,786,543 triangles, 5,340,126 overlapping triangles, projected area 29,401.004 m². Estimated 348,921 surfels, 224 bytes each; the planning allowance with a sixfold buffer multiplier and 1024 bytes per grid point was **452.414 MiB**, below the 8 GiB guard. This is a planning estimate, not an observed GPU peak.

## Preserved settings and visual evidence

`configure(..., fast_gi=False)` ran before thin-glass `apply()`. Ray tracing stayed enabled; Fast GI stayed disabled. World Background strength remained 0.36. All original light positions, energies, radii, shadow settings and shadow links, and all original object transforms and visibility were checked unchanged. No self-emitter shadow exclusion was added. Capture settings remain 64 samples, intensity 1, world/indirect/emission enabled, distance 20, normal/view/facing bias 0.3/0/0.5, validity 0.4, dilation 0.5/radius 1, surface/escape bias 0.05/0.1.

The thin-window EEVEE approximation keeps Fresnel IOR 1.5 and existing pane geometry. Original Cycles glass-surface hash remains `b5003cc9588bed13d22b02be8fad2b357e17ffb549ea9680dda9454819c91d1d`; glazing geometry hash remains `655896c42f23f6b59c3105ca8e865815051a4340016b6a95f20e8972dbbe597d`. These hashes describe glass, not the entire scene's shading graph. Shadow linking would affect both engines, but this candidate makes no shadow-link change.

Selected displayed RGB values reinforce the native visual review; they are not a photometric acceptance metric:

| Pixel | EEVEE RGB | Cycles RGB | Observation |
|---|---|---|---|
| Wall middle (720,275) | 9,8,5 | 50,51,42 | Excessive dark band |
| Wall upper (720,125) | 83,87,76 | 35,35,26 | Excessive upper-wall brightness |
| Wall lower (710,454) | 36,36,30 | 41,45,40 | Closer locally |
| Ceiling (480,50) | 16,18,17 | 46,44,38 | Excessively dark field |
| Wall near shelf (320,280) | 3,2,1 | 17,16,12 | Excessive shadow lobe |

Whole-image mean absolute difference is 19.050 of 255 display code values. It is supporting evidence only; the visible structured artifacts determine FAIL.

No global helper configuration was adopted. `eevee_preview.py` remains SHA `f68abbfde2ff6164618486a0df078bb144311e78482bfd794d15568d3b6803cd`; `eevee_glass.py` remains SHA `5ccc9326bc33bac735e76cf6a85051f7da31f86a7243e1979052c6710654a476`. The saved local profile is reproducible evidence and can be inspected, but does not justify a whole-building bake or final animation as an accepted configuration. GPU job is finished and released.

## Possible separate realtime route — not executed

**Subsequent result:** the later authorized zero-VOLUME baseline has now been rendered and reviewed in [eevee-iteration07-novolume-review.md](eevee-iteration07-novolume-review.md). It removes the black lobes but is severely washed out. The conditional fill stage was not entered. The following paragraph records the evidence available before that follow-up.

The parent requested an assessment of removing VOLUME GI and using explicitly disclosed preview-only indirect AREA lighting. No prior actual interior image tested complete removal of VOLUME objects and caches. The 06 Study diagnostic set all seven volume intensities to zero and retained the dark pattern; this suppresses the local captured contribution, but padding and distant/world sampling remain, so it is not evidence that a volume-free scene fails. The 05 Living intensity-zero diagnostic also failed; turning Fast GI off addressed that earlier band instead.

A separate volume-free preview with restrained window-oriented and ceiling-bounce AREA sources is a plausible approximation route. It would avoid the current local cache interpolation while allowing readable interiors, but there is no visual acceptance evidence yet, and ray/shadow problems may remain. Any such candidate should retain the physical Sun, sky, directional shadows and glass reflection; record every added light and its approximation scope; and isolate these lights in a preview-only collection that the Cycles restoration path hides or removes. The untouched physical Cycles scene remains the lighting reference. No such lights, collection, helper change or additional render were created in this task.
