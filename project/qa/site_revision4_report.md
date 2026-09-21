# Site revision 4 — bounded distant-environment repair

2026-09-20. Source frozen for the integrator's iteration04 render. Geometry checks passed; visual acceptance is **PENDING**, and this stage produced no GPU or CPU render.

## Evidence inspected

Actual iteration03 images inspected: `renders/previews/iteration03/CAM_HERO.png`, `renders/rooms/iteration03/CAM_MAIN_L1_TERRACE_W_B.png`, `CAM_MAIN_L1_LIVING_A.png`, `CAM_GUEST_L1_POOL_A.png`, and `CAM_GUEST_L1_POOL_B.png`. They showed a short straight downstream channel, terrain termination/empty distant background, and bright sparsely wooded slopes outside windows.

## Changes

- Terrain now spans X/Y −1040 to +1040 m, with 108,900 vertices. Near-resolution triangles transition to lower density distant terrain. The old continuously rising plane becomes a gently folded remote valley.
- Original river nodes 0–15 remain identical. Downstream continuation after node 15 meanders through the larger terrain; distant banks broaden and vary laterally. The upstream continuation starts at the original X=90 m endpoint and is a separate object. Neither change moves the near waterfall or bridge.
- Added 3,845 distant broadleaf trees in four density/size bands (718 / 1,015 / 1,438 / 674), using shared reduced leaf/branch meshes beyond 85 m. Added 180 lower woodland trees. Existing fern/shrub instances, moss tufts, leaf litter and original near tree mesh shapes remain available.
- All 6,749 tree/shrub instances now seat their stems 12 mm into the **actual triangulated terrain**. This corrects discrepancies between the smooth terrain formula and the sampled mesh, particularly beside slope roads. Original near Z coordinates were not retained where they caused floating roots.
- Of 159 recorded near/landmark/sapling trees, 158 retain their XY positions, rotations, scales and source mesh shapes. `TREE_Near_037` originally stood inside the finalized `MAIN_L2_TERRACE_W` polygon; it moved 5.216319 m west to X=−17.2 m. Its original coordinates and the reason are recorded in `data/site.json`. Its shape, rotation and scale remain unchanged.
- Site reads current main room world polygons and the guest registration/polygons on each build. Soil is capped below each actual floor; roads passing above a lower plunge terrace no longer raise soil into its structural clearance.

## Verified results

`site_revision4_geometry.json` and `site_revision4_build.log` record a 25.58 s background build and geometry audit. This scene contains only the site module, not the complete project: 14,164 objects, 1,146,120 unique mesh vertices, and 1,030,601 unique faces.

- Finite coordinates: PASS. Internal terrain boundary edges: 0. Edges with more than two incident faces: 0. The 1,316 open perimeter edges are all on the distant external boundary.
- Minimum terrain-boundary distance: 1,040 m from the main origin; at least 995 m from the guest reference center. This is a distance check, not proof that every view hides the horizon boundary.
- Preserved near XY/rotation/scale numerical error after the documented relocation: below 0.000001. Highest near root above the actual mesh: −0.011962 m (all sampled roots seated).
- `site_revision4_floor_clearance.json`: a 7×7 grid clipped to each of all 60 actual room polygons, raycast against the built terrain. Soil-above-floor samples: 0; minimum soil clearance below floor: 0.315009 m. Main plunge terrace minimum: 0.319560 m. This checks soil intrusion, not room construction completeness.
- Existing `_shader_water` through `_water` source block SHA-256 remains `67dba23965dd1adffb1cabf05a7aa902622639479fada8eb18a2be8a750108eb`. Original first 16 river nodes compare equal. Existing river mesh normal correction and local simulation-face removal belong to the independent `water_integration.py` contribution.
- New remote upstream surface minimum normal Z: 0.999832. It uses the original animated river material and does not replace or trim the local fluid sample.

## Rebuild dependency and handoff

`data/site.json` and the module default reference **`assets/models/site_near_trees.blend`**, a 17,561,826-byte local authored mesh library extracted from the original working scene. Include this file when moving or packaging the project; its SHA-256 is `633f9215cbf590556e190f5ff41045464b111beaa1d6c968ed12e567828eb1e2`. The QA original `qa/site_revision4_near_trees.blend` is retained, and both files have matching SHA-256. The extraction source and 159 placements are in `site_revision4_preserved.json`. The original tree meshes remain editable Blender geometry, with individual geometric leaves rather than image crowns. Final path relocation happened after the successful geometry build and changes no mesh contents; the build log retains the prior QA-library path as historical evidence.

`site_revision4_smoke.blend` is the final site-only inspection checkpoint. `site_revision4_smoke.blend1` retains the preceding contact-error checkpoint; neither is the user-facing integrated scene. Root should use the normal full build and then inspect the same terrace, living-room and guest-pool views. Existing camera clipping was 800 m; a 2,500 m far clip is recommended for complete use of the new environment and is owned by the integrator.

All remote terrain shape, river meanders, tree distribution, species-scale variation and canopy geometry are **C: authored approximations**, not measured terrain or surveyed individual trees. Near HABS-derived architecture/bridge placement and the original near river registration are preserved. No new download, external upload, long fluid bake, or render was performed for this revision.

The neat-freak documentation pass enumerated project Markdown and reviewed the implementation ownership/state documents. This scoped report and the site data now describe the actual revision. Integrator-owned `STATUS.md`, `START_HERE.md`, global asset manifests and final render acceptance remain with root; earlier site revision reports retain their historical failed/pending status.
