# Full-scene rendering schedule

The original PRD remains the target: at least 12 different 3840×2160 Cycles showcase stills, at least two complementary QA views per room, a 1080p 24/30 fps tour lasting 2–4 minutes, and 5–10 seconds of continuous water inspection. Proxy render times cannot justify reducing these requirements.

1. Root coordinates one full-scene GPU process at a time. Select an exterior with forest/water, an interior through glass, and a water close-up. Render each at 512×512/32 for scene stability and gross visual defects; preserve exact scene, frame, camera, device and timing.
2. After fixing those defects, render the same cameras at 1920×1080/128, and one representative camera at 3840×2160/512. The full-size test checks whether stone joints, window frames, leaves, wood texture and dark corners survive denoising. Compare raw and denoised crops where needed. Cycles 512–2048 is the permitted final sampling range; select actual settings by image evidence.
3. Use actual per-camera sample cost to schedule all 12 final stills. A rough initial estimate can separate synchronization/loading from path tracing and scale the latter by pixels and samples, but adaptive sampling, glass path length, memory pressure and denoising break simple proportionality. Clearly label estimates; replace them with actual recorded completion times.
4. Capture every registered room's two complementary QA cameras. A small image proves only visibility; inspect room finish and reference-specific furniture at adequate size. All-room QA and 12 showcase images are separate deliverables.
5. For film, first verify the camera route passes through real openings at each turn, staircase and doorway. Then render 120–240 consecutive frames covering water and one demanding interior move, at final 1080p and chosen frame rate. Check temporal denoising/aliasing, transparent surfaces, leaf flicker, foam contact and water continuity before committing to the sequence.
6. A 2-minute/24 fps tour requires 2,880 frames; 4 minutes requires 5,760. At 30 fps the respective counts are 3,600 and 7,200. Render fixed frame ranges to numbered images for resumability, verify all frames, then encode a playable movie at the declared rate. Preserve route/frame mapping and per-room supplementary segments. A shorter video does not fulfill the PRD.
7. Example arithmetic only: 2,880 frames averaging 5/10/30 seconds would require about 4/8/24 hours of rendering, excluding QA/encoding. These are not observed scene benchmarks or completion promises. Estimate only after step 5, continue the authorized work, and retain incomplete tests as NOT_RUN/FAIL until evidence exists.

Viewport FPS remains a separate GUI test: 1920×1080, four representative 60-second routes after warm-up, median ≥30 fps and P95 frame time ≤50 ms. Offline render throughput cannot establish this result.

Useful still invocation (run via the installed Blender executable):

```text
--background --debug-cycles --python-exit-code 1 --python project/scripts/render_views.py -- --scene project/scene/fallingwater.blend --output project/renders/stills --cameras CAM_name_1,CAM_name_2 --engine CYCLES --device HIP --samples 512 --resolution 3840x2160
```

Names and file paths above are invocation placeholders; use the actual saved scene and camera inventory. The script writes PNG and EXR from the same render, updates `render-benchmark.json` after every image, and exits nonzero if any render fails. Existing-output skipping records NOT_RUN for files it did not verify.
