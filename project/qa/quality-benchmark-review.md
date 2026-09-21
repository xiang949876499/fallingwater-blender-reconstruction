# Fixed 4K-pixel-density CPU comparison — 2026-09-20

This is a bounded quality/performance comparison on the same iteration 03 source scene, not final-image acceptance or a full-film performance guarantee. Source SHA-256: `2f4f904a0364cf2792036ad59b7a112280cd64a15405945a13e975615a561bf4`. An exact byte-for-byte checkpoint is retained as `qa/quality-benchmark-source.blend`.

Both variants use 3840×2160 camera projection with an actual 640×640 render border, frame 1, seed 19, Cycles CPU with 8 fixed threads, 512 maximum samples, automatic adaptive minimum, AgX, accurate/high OpenImageDenoise on CPU, 8 transmission and 12 transparent bounces, and 4 glossy bounces. Baseline uses threshold 0.01, 12 total and 6 diffuse bounces. Candidate uses threshold 0.025, 8 total and 4 diffuse bounces. Camera exposure is fixed between variants. The candidate runs second with persistent data, so the measured reduction includes any warm-cache benefit. Other coordinated CPU work could run concurrently; hardware isolation was not enforced. This is not an isolated test of threshold or bounce count alone.

## Exterior result

`CAM_HERO`, exposure +0.8, full-frame top-left pixel rectangle `(1440,300,640,640)` (x 1440–2079, y 300–939). This contains foliage, thin branches, tree bark, upper/lower window mullions and glass reflections. Both raw PNGs and both denoised PNGs were opened at their native 640×640 resolution.

| Measurement | Baseline | Candidate |
|---|---:|---:|
| Render plus output time | 216.5216 s | 121.8995 s |
| Mean normalized sample-debug value, inner 608×608 | 0.71325 | 0.28935 |
| Fraction of inner pixels with sample-debug value 1 | 37.12% | 4.94% |
| Linear RGB raw-minus-denoised RMS, inner region | 0.00527 | 0.00971 |

Observed elapsed-time reduction is 43.70%. The denoised candidate differs from the denoised baseline by mean 1.55/255 and P95 5/255 in absolute RGB channel difference over the inner region; mean linear luminance changes by −0.073%. These are comparison diagnostics, not a ground-truth noise score or an automatic acceptance threshold. The raw-minus-denoised residual includes both noise removal and denoiser bias. The sample-debug pass is reported in its actual normalized units; it is not presented as a separately verified absolute sample count.

Candidate raw glass and shaded bark visibly contain more grain. After denoising, the continuous mullion lines and major leaf/branch silhouettes remain close to the baseline. The candidate has slightly more smoothing in some reflected/shaded detail; both variants already smooth glass reflections. The result justifies testing the interior candidate. It does **not** qualify the whole scene, tiny distant foliage in motion, or unseen dark corners. Avoid judging the crop boundary, where denoiser context differs from a full-frame render; the quantitative region excludes 16 pixels on each side.

Per-region measurements for foliage, upper windows, dark windows and bark are in `qa/quality-benchmark-hero-analysis.json`. Original settings, times, hashes and output filenames are in `qa/quality-benchmark-hero/quality-benchmark.json`; image and linear EXR outputs are grouped under `baseline/` and `candidate/`.

## Interior result — candidate rejected

`CAM_MAIN_L1_LIVING_B`, exposure +2.4, uses the same frozen source at rectangle `(3120,1380,640,640)` (x 3120–3759, y 1380–2019). The actual output shows the room's right stone wall, deeply shaded floor joints, and small window-edge openings. It does not show the bench/table location anticipated from the older iteration 02 camera image. The full-room iteration 03 diagnostic was opened and confirms the current saved camera direction. This is a Cycles comparison, independent of the earlier EEVEE exposure choice.

| Measurement | Baseline | Candidate |
|---|---:|---:|
| Render plus output time | 241.3940 s | 92.4324 s |
| Mean normalized sample-debug value, inner 608×608 | 0.98412 | 0.30906 |
| Fraction of inner pixels with sample-debug value 1 | 90.58% | 0.98% |
| Linear RGB raw-minus-denoised RMS, inner region | 0.00183 | 0.00304 |

Elapsed time decreased by 61.71%, but image quality did not hold. All four native-resolution interior PNGs were opened. The candidate raw image is much grainier. Its denoised floor develops conspicuous nonuniform dark/light swirls and patches that differ from the smoother baseline, while stone-wall detail also changes. Tile joint positions remain recognizable; that alone is not sufficient acceptance.

The inner region's mean linear luminance decreases by 8.97%; the separately measured dark-floor region decreases by **14.28%**. This is a material lighting change despite a whole-crop mean absolute display-RGB difference of only 2.24/255 (P95 5/255). Low average display-space differences must not conceal a substantial relative change in dark-room illumination. The coupled test cannot isolate how much comes from reduced bounce depth, earlier adaptive termination, or denoiser behavior. It provides sufficient evidence to **reject this candidate as a general interior preset**. Per-region evidence is in `qa/quality-benchmark-living-analysis.json`.

Retain the interior 0.01 / 12 total / 6 diffuse baseline. If further optimization is needed after geometry correction, a separate threshold-only comparison that preserves bounce depth would isolate the tradeoff more clearly; it has not been run here. The exterior candidate remains only a provisional exterior option requiring a representative complete frame and temporal review before final adoption. No production preset was changed.

## Output validity and installed API

`scripts/render_quality_benchmark.py` produces the raw and denoised images from one path-tracing result for each variant. In Blender 5.2.1, the compositor Render Layers `Noisy Image` socket provides raw color, and `Image` provides Cycles' denoised color. Both also have 32-bit linear EXR exports; the sample-debug EXR is saved independently. No second render is used to manufacture the noisy comparison.

The installed API was inspected rather than assuming an older Blender interface: `scene.compositing_node_group`, `file_output_items.new('RGBA', 'image')`, and `ImageFormatSettings.media_type='IMAGE'` are used. An initial tiny self-test failed because the output node defaults to multi-layer EXR; that failure log remains in `qa/quality-benchmark-selftest.log`. The corrected 16×16 CPU self-test then generated all five expected outputs, verified exact dimensions, and exited cleanly (`qa/quality-benchmark-selftest-v2.log`). Both full comparison processes exited cleanly. All 20 produced files (8 PNGs and 12 EXRs) were rechecked against their recorded SHA-256 hashes; all PNGs are 640×640. All eight comparison PNGs were visually inspected. `qa/quality-benchmark-summary.json` records these checks. Full-page official 5.2 documentation was unavailable through the web tool; installed API inspection and actual successful output are the execution evidence.

No source scene, global preference, driver, production material, full-resolution deliverable or long animation was modified by this benchmark. The interior candidate was rejected; exterior adoption still requires representative final-frame/moving-image review after geometry corrections. No further render job is running from this benchmark.
