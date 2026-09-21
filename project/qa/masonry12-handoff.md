# Upper tower12a candidate handoff

2026-09-21 — **PHYSICAL PASS / FRESH REOPEN PASS / VISUAL NOT_RUN.** This implements the finite proposal in `masonry12-source-review.md`; that file remains the earlier read-only research record. No render was made by site_visual. Parent must compare source and candidate images before any production adoption.

| Deliverable | Frozen identity |
|---|---|
| Source | `scene/Fallingwater_iteration10.blend`, SHA256 `1e7b17d9c2396513f005724e50788bf834097eedb401b91a7f1030825e2c4ed9` |
| Independent candidate | `scene/Fallingwater_masonry_tower_candidate12a.blend`, SHA256 `b267636a9cbbe297513968f08f3b85930c0302cae1ebb75ed775043250e11a48` |
| Helper | `scripts/masonry_tower12.py`, SHA256 `e71403d89289db9e1ad5efb005a4b86072d7c8ac7d11335426dbec5e082cc391` |
| Call, only on explicitly selected source copy | `masonry_tower12.build(ctx)`; ctx can be a namespace with the project root. No imports of main_house/site/masonry_detail or mutable configs. |
| Namespace | Collection `MASONRY12_Upper_Tower`; objects `_W`, `_E`, `_South_Return`; private material `_Stone`. It does not delete any broad `MASONRY12_*` prefix. |

The helper validates the exact300 source finish objects plus5 structural guards against the frozen evaluated geometry digest before replacing anything. Every original finish must still use FW_stone at unit scale. Repeat application validates all three generated geometry hashes and all five structural guards, then performs a no-op. Partial application or edited geometry is rejected. This is a candidate entry, not automatic production wiring; any later change to tower heights or underlying geometry requires a new reviewed source signature, not disabling the guard.

## Actual local change

- Removed exactly `MAIN_tower_course_course00_00_-1` through the recorded300 object whitelist, never the structural tower.
- Added **501 independently closed angular stones**, batched as204 west +165 east +132 south/corner components into **three meshes,20,622 triangles**. Old evaluated finish was32,400 triangles. No modifier stack, Boolean, new image or whole-scene rebuild.
- **44 non-repeating beds**, actual nominal body heights35.865–162.335mm; inter-bed gaps6.637–10.353mm before inward edge chips of at most1.8mm per edge. Selected thicker stones are split into a thin packing piece and thicker partner. Long face stones use .38–1.02m lengths before cuts; clipped neighbors can be shorter.
- South batch contains88 **closed L-footprint stones** wrapping the existing southern tower corners, plus44 central-end pieces. These have an actual solid return, not floating front/back planes. The structural footprint, both source long-side outer envelopes and tower height are retained; the source-authorized south surface allowance is shallow, ≤35.5mm beyond the existing substrate, not an enlarged replacement wall.
- Backing penetrates the existing tower by0.8mm. All501 components have actual evaluated-substrate nearest-point signed contacts between **-0.800133 and-0.799954mm**. Front relief is angular and within the allowed shallow envelope; no added underlying backing sheet hides the core.
- Finish starts at z5.277m and ends below z9.439m, with roof/window clips. Top cap and flues remain untouched. The source-review HABS tower-height discrepancy remains open; this is not a new height certification.
- Copied FW_stone once to `MASONRY12_Upper_Tower_Stone`; source photographs,2m Object BOX mapping, tint and roughness remain unchanged. Only private Bump.001 distance changes22→6mm. Joined world-metre vertices with identity object transforms prevent every stone sampling the same centered image patch. Original shared material nodes and every remaining user are unchanged.

## Physical and protection evidence

`masonry12-build-check.json/log` records the successful process; `masonry12-readback.json/log` records a separate fresh process.

| Check | Measured result |
|---|---|
| Non-target scene objects | **23,137 exactly unchanged**; exact300 removed, exact3 added |
| Source globals | Every original material, image, world, light/camera setting, action and text unchanged; only private material/collection added |
| Protected evaluated physical geometry | **79 hashes unchanged**: existing core/shoulders/water/bridge/paths/terrain plus5 tower guards |
| Closed stones |501/501; every edge incident twice, consistently oriented on fresh reopen; all positive volumes; minimum triangle area1.442699e-6m² |
| Stone-to-stone and internal nonadjacent surfaces | Zero intersections, including fresh-process self/cross-component checks |
| Actual neighboring architecture | Zero candidate intersections with the ten recorded evaluated meshes below |
| All131 saved cameras at frame48 | Minimum new-finish clearance **0.728763m**, at CAM_MAIN_L3_STUDY_B |
| Current frozen full route | **12,264 rays**, zero baseline target hits and zero new finish hits |
| All7,584 delivered film eye positions | Main2,880 positions min1.690414m; supplemental4,704 min2.155594m; independent direct evaluated matrix samples exactly agree with linear fcurve positions |
| Save/reopen | Full saved object/global/mesh fingerprint exactly reproduced; repeat entry causes zero mutation |
| Original source file | SHA still matches1e7… after all checks |

The shared `shrub08_auditlib.route_regression` routine emits a legacy text label “frozen08”; the actual input here is the frozen iteration10 route copied into `masonry12-frozen-route.json`, with its SHA in the build report. The source file,131 cameras and7,584 film positions are the current1e7 iteration10, not an older08 scene. This is a changed-volume regression plus frozen non-target proof, not a claim to have newly certified unrelated source collision defects.

The ten actual neighboring source meshes were: `MAIN_L3_STUDY_finish`, `MAIN_L3_study_east_south`, `MAIN_L3_study_roof`, `MAIN_L3_roof_fascia_0`, `MAIN_stone_tower_north`, and `MAIN_L3_study_south_sill`, `_head`, `_mullion_3`, `_transom_2`, `_glass_2`. Their source world bounds and geometry hashes are stored. Construction uses conservative masks from their actual bounds with2mm clearance; acceptance additionally checks their evaluated triangles. Cut-generated internal split lines have a real6mm kerf, not two coincident closed ends. Existing openings, windows, floors and roofs are not modified.

## Parent render comparison

Source and candidate must use the same frame48, engine, lighting, AgX, exposure, resolution, samples and denoising. Do not use another concurrently rebuilt scene as the baseline.

- **CAM_HERO:** preserve its saved camera and exposure. It is deliberately absent from the override JSON.
- **CAM_WATER_DETAIL:** optional external diagnostic override in `masonry12-camera-settings.json`: eye(-7,2.5,8.7), target(-.58,9.68,7.35),36mm, no shifts, exposure+.8. Apply it identically to both files. This does not modify any saved camera; `masonry12-camera-probe.json` separately records full-tower framing, local camera clearance and actual first-hit rays. A40mm draft clipped the full protected tower bound by1.5px and was widened before handoff; the rejected framing log is retained.
- The source-review terrace W/S views remain useful extra checks if desired, but are not a request for another full render sweep. W dressing/study slab walls belong to the separate wall12 agent; this tower candidate cannot claim to fix those large bare walls.

Visual questions: do thin/thick beds and south return read as split sandstone rather than the old brick grid; do narrow cracks retain real depth without black coplanar bands; are corner widths and top cap visibly unchanged; does the generic worn-rock PBR remain too mottled despite reduced bump. No claim of photoreal acceptance follows from these physical passes.

The final36mm diagnostic probe passed: tower plus all five guard bounds project to x323.324…657.791/y31.813…514.356 at960×540. Nearest actual scene surface to the camera is TREE_Landmark_00_Leaves at3.840754m; center ray hits the new west tower. All15 distributed aim rays first hit the intended finish (10 west,5 south return). Camera-settings SHA256: `918ed404ec8c705fef31915b0d378cf036d8938aae0a0e2f10da42962ce4240f`.

## Failure evidence and coordination

- Attempts01/02 ended before any scene save because the local Blender5.2.1 tessellate_polygon API returns point indices, not the older Vector return. Actual local docstring/example was inspected and preserved in `masonry12-tessellate-api.log`; the helper now uses the verified indices directly. No geometric tolerance was loosened.
- Attempt03 was unsaved and rejected because rectangular remnants around an L-shaped roof cut had coincident internal end faces. These were caught by the inter-component BVH test. The final helper introduces true6mm separation; it does not suppress those intersections in QA. Attempt03 helper/report/log are preserved.
- Root owns build_scene/config/production integration and rendering. The parallel wall12 worker owns the distinct dressing/study external walls; namespace and layer/material choices were communicated. No other worker's files were reverted.
- neat-freak reconciliation is scoped to this handoff and the owned QA records. Earlier source research and negative attempts remain historical evidence. No central STATUS, AGENTS, manifest, source photographs, existing assets or working blend was rewritten; no publication or commit happened here.
