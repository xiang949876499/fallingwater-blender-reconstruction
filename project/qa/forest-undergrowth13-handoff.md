# Forest undergrowth13a — bounded candidate, visual review pending

2026-09-21. Physical candidate and fresh-process readback PASS. No rendering or production integration was performed. Whole-environment visual acceptance remains open.

## Frozen inputs and deliverables

- Source: `scene/Fallingwater_navigation_candidate11a.blend`, SHA256 `d66ded0f23b7d19c20b81d2f59f94aa5aa77747be4568e85e1d105395fc219ff`.
- Candidate: `scene/Fallingwater_forest_undergrowth_candidate13a.blend`, SHA256 `95590f217243ebff86072449fcf8bbb069960963119916ef90b702d3105261f5`.
- Entry: `scripts/forest_undergrowth13.py`, SHA256 `e599cbfbe04a4e6e5d9a84e99fa9789946af255f2e32fabe1735547dff0a2f2c`.
- Exact 189-root/378-object whitelist, matrices and old-data signatures: `qa/forest-undergrowth13-plan.json`, SHA256 `e34d4e4a4aef1ba667bbedfbfbe3752bb58759c9ece3754ae3093d4863dbd6ce`.
- Main evidence: `forest-undergrowth13-final-audit.json`, `-build.json`, `-readback.json`, `-plan.json`; complete snapshots and negative preflight records remain alongside them.

## What the candidate changes

189 existing skinny asset2/3 understory roots retain their exact objects, roots, matrices and labels. Only their two `object.data` pointers change to four already-present, previously accepted native branch/leaf meshes. No mesh, material, object, asset library or vegetation count is added. The original 16 accepted shrubs and 18 accepted canopy trees are unchanged.

| Region interpreted from actual source photographs and rendered terrain hits | Accepted roots |
| --- | ---: |
| HERO west bank | 55 |
| HERO south bank | 69 |
| Overview near slope | 24 |
| Loggia east bank | 41 |

The finite ellipse unions have probabilistic soft edges; 9 edge roots keep their old form. Of 217 physically tested roots, 28 fail one or more checks and keep their old form. No roots move to resolve a failure. The 189 selected roots comprise 98 asset2 and 91 asset3 instances: 797,048 final instance triangles, net +654,542 versus their old shape; 49,154 connected leaves versus 17,199. Shared asset2 is 3,832 triangles/236 leaves and asset3 is 4,632 triangles/286 leaves. This is below both the requested net +1.2M limit and the stricter 1.2M total target-instance budget enforced by the entry.

The official Classic/East green-season references support grouped broadleaf understory and retained rock gaps; `research/interiors.md` S12 supports rhododendron as site context. Exact roots, zone boundaries, chosen native morphology and local density are C interpretations; exact species/cultivar is U. Reference photographs are reference-only, not scene textures or redistributable assets.

## Actual checks and limits

- 23,056 non-target objects remain exact; all existing shared mesh/material datablocks and scene globals remain exact. Terrain stays `FW_ForestFloor11a_C_OrganicZones`; no water, soil, sky, architecture or old tree trunk change.
- 242 protected physical hashes, including core/shoulder/water/bridge/path/terrain and accepted16 objects, remain exact at frame48.
- Roots retain their existing approximate 12mm insertion: measured range −12.031 to −11.962mm. New leaf/terrain gap is at least 47.497mm, above-basal branch/terrain gap 13.628mm; zero leaf or above-basal branch triangle intersections with actual terrain. Basal contact is allowed and separately recorded (lowest basal point −56.644mm).
- The existing accepted native petiole/branch contact bound, transformed per root, is at most 0.000449mm. Native shared geometry is used exactly; this round does not regenerate or trim leaves.
- Actual path boundary distance minus crown radius is at least 0.434943m. Path footprints and explicit plunge exclusion remain clear. Actual building, rock and water triangle overlap tests reject conflicting candidates.
- All 131 saved cameras are clear of changed geometry; nearest is `CAM_MAIN_L3_LINK_B`, 3.286213m. All 7,584 actual current movie positions are clear; minimum 4.065431m. Evaluated camera matrices agree exactly with FCurve positions at sampled segment endpoints/midpoints.
- 12,264 current route rays have zero candidate hits/new obstacles. The shared audit helper retains a legacy text label “frozen08” in its scope field; the executed route input is the frozen11 route and actual d66 actions, not the old08 scene. This audit concerns changed objects; it does not certify that every existing old object is collision-free.
- 717 coarse 32px-grid rays in the three comparison views protect currently visible architecture/rock. This is a sampled safeguard, not pixel-exact occlusion proof. `TREE_Understory_1906` was rejected for hiding `MAIN_L1_kitchen_west_0` at HERO pixel(240,400); 3 other roots were rejected for intersecting real `SITE_Bank_*` stones.
- Fresh CPU4 readback takes 143.006s, verifies full saved fingerprint, all four native signatures and 242 physical hashes; repeated entry call is a verified no-op. Build was 172.596s. No image was rendered.

## Same-view visual comparison for root

Use source and candidate at frame48, identical 1280×720 settings, with `qa/forest-undergrowth13-camera-settings.json`: `CAM_HERO`, `CAM_MAIN_OVERVIEW`, `CAM_MAIN_L1_LOGGIA_B`. Exposure is 0.8 on both. HERO/Loggia preserve their saved poses. Overview uses the actual logged 35mm comparison pose: location(27.86212349,−21.79529572,27.94647980), target(3.70000005,7,3.20000005), shift0. The d66 saved Overview pose is not the pose used by the earlier rendered integration11a Overview image.

The first saved-Overview pixel probe was therefore archived as `forest-undergrowth13-source-probe-saved-overview-not-render-camera.json`; the final probe/selection uses the actual external comparison pose. Both source renders and official green-season references were actually opened. No claim about candidate density/colour/silhouette is made before root opens all three images.

## Calling the entry and later integration

`forest_undergrowth13.build(ctx, plan, enabled=True)` accepts the decoded checked plan. The default is disabled. It verifies all target original-data signatures and matrices, population2400, original accepted16 signatures, and the exact native shared asset signatures before any mutation. A partial prior application or missing/mismatched asset raises rather than rebuilding or silently accepting a different shape. Complete prior application returns `SKIPPED_ALREADY_APPLIED` without mutation.

This is an independent candidate entry, not wired to production. It imports `understory_detail` for the accepted native signatures. For a future adopted checkpoint, root should freeze the accepted whitelist outside QA and apply only after accepted16/native meshes exist. If terrain, paths, cameras, movie actions or architecture change, rerun contact/route/occlusion checks on that new base; a matching root/data precondition alone is not a new physical acceptance. No whole-forest expansion is implied.

## Scoped closeout

The neat-freak closeout is limited to this task's owned helper and QA files. The source/candidate distinction, old incorrect Overview probe, rejected roots and NOT_RENDERED status are reconciled here. Root owns `STATUS.md`, `AGENTS.md`, production wiring and final scene publication; no competing edits to them were made. The newly requested integration12 existing-tree diagnostic is a separate read-only artifact under `forest-undergrowth13-existing-tree-*`, not part of the 189-root replacement or its no-new-obstacle claim.
