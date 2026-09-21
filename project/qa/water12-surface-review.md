# Water12 continuous surface reconstruction — actual static handoff

This iteration produces a complete independent full-scene candidate. **Static visual status remains FAIL.** Root rendered and opened both 1280×720, 48-sample, frame48 HERO/WATER_DETAIL views; the water agent also actually opened both images. They show smooth transparent blue-grey ribbons, very regular lateral edges and aligned pool joins. Natural fanning, breakup, aeration and impact foam are missing.

## Frozen deliverables

- Main candidate: `D:\zx\test\project\scene\Fallingwater_water12_surface07.blend`; SHA256 `46bbc92557fe24259accae4e2d808c49f74331d4cf024bc00c7201519548fef7`.
- Display-only copy: `D:\zx\test\project\scene\Fallingwater_water12_surface07_display.blend`; SHA256 `875daf50b19c652c7e25a772b2e325578cafd7d9e6e23806c578f3d22dab21f1`. Adds `CAM_WATER12_FOOT` only. The world-space water mesh hash is `eb42b001fcc31126b9c190e2423dfc7687d853464415d2786862e8b3da146cb7` and geometry is unchanged.
- Existing `CAM_HERO`, `CAM_WATER_DETAIL` retained. Frame48 is a static authored body. Root schedules all renders.
- Source is frozen iteration09, SHA `489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331`. Visible frozen core/terrain/banks are unchanged. No production file, FLIP modifier or cache is modified.
- Builder: `scripts/water_surface12.py`; exact executed07 snapshot: `qa/water12-surface07-builder-snapshot.py`. Construction reads `data/site.json`; its recorded hash is `2b4d5c712e7358dacc11458749d7dabc45bee98f43ec660fa9be4f36aa070c3d`.

## Geometry evidence and scope

The original folded river skin is not reused as a solid. Upper and pool surfaces use a single strictly ordered stream coordinate map. Nine rectangular section rings share the actual layer vertex indices; no overlap plane hides a gap. Corresponding surfaces are closed at actual shared edges. Floating-point shore pinches are split into separate shell fans without moving the triangles.

The final body has **700,646 vertices, 1,400,980 triangles, zero boundary edges, zero nonmanifold edges, zero degenerate triangles, and zero nonshared BVH overlap pairs**. All nine branches belong to the same connected component. Each upper and pool join has460 shared edges in total, each paired with exactly two real faces. Other isolated wet regions exist: the full body contains 91 connected components; this does not establish one hydraulically connected river to the remote scene extent. The remote upstream extension interface is not certified.

Geometry is C authored. Original upper water heights were retained where sampled. The crest section descends8mm from each original source section; the thin underside was adjusted locally. The original3 shape keys remain on the hidden old water, **not** on the rebuilt body. The rebuilt body is currently static. Its computed signed volume is only a closed-mesh quantity, never a discharge measurement or physical water-budget result.

The near layer omits partially wet triangles conservatively. A further133 upper and16 pool triangles were rejected when their center or edge midpoint probed the frozen land/rock interior. This produces a finite sampling gap at some shorelines, up to a local cell; it is an explicit C approximation requiring visual review, not a claim of exact shore contact. The step is roughly0.035–0.15m in the closest upper reach,0.06m in the near pool, with ordered lateral spacing at most0.09m; farther sampling is coarser.

## Contact by actual use

The reporting cutoff remains0.5mm. These are actual vertex/centroid/edge samples, not an exhaustive analytic triangle-solid certificate.

| Role | Samples | Actual result |
|---|---:|---|
| Falling body vertices |44,620|No terrain or rock interior over0.5mm|
| Falling-body triangle centers |88,320|**5 real rock-lip counterexamples remain, max1.025mm**; all have odd parity in3 independent rays|
| Near free-water triangle centers |229,597|No terrain or rock interior over0.5mm|
| Actual upper shoreline edge midpoints |2,783|No terrain or rock interior over0.5mm|
| Side closure triangle centers |5,380|3 terrain /70 rock interior samples; max terrain17.02mm, rock40.00mm. These are separated from the top seam; normal-view visibility/transmission still needs inspection|
| Deep C bottom-closure centers, every third |76,680|5,052 terrain /850 rock interior samples; max112.04mm/107.66mm. These are **optical closure approximations**, not CFD bed interfaces|

The five remaining falling-body points near `(2.88,-3.88,-3.056)` are retained as a real local contact FAIL. They are not relabeled as deep bottom caps and are not made acceptable by changing a threshold. The original mixed-role11.2cm/8.1cm failure records remain intact; their scope was mixed and must not be attributed wholesale to the visible water surface.

## Preserved attempts and actual cost

- Surface01:54 open/nonmanifold join edges and264 confirmed crossings.
- Surface02:closed, zero confirmed crossings, but wrong handling of open terrain and tiny shore triangles.
- Surface03/04:improved true terrain/solid classification; retained numerical shore counterexamples.
- Surface05/05b:conservative shoreline;05b separates19 touching edges, with every triangle coordinate and winding bitwise unchanged.
- Surface06a:one exact core difference on the **new valid**05b body, hard stopped at180seconds; no output. Observed working set41,214,496,768bytes. No further Boolean chain ran.
- Surface07:actual build+geometry audit 90.356seconds, CPU4. It preserves old failures and is independently saved. No rendering was performed by this agent.

## Next bounded direction selected by root

Keep this closed base and make **one** visual hybrid candidate, at frame48: varying shallow sheets/fans plus small water droplets, broken whitewater and impact treatment, guided by actual source photos. Do not infer a larger water supply from those effects. Root will render it. Long simulation, production installation and a final5–10second motion PASS remain unauthorized/unachieved at this point.
