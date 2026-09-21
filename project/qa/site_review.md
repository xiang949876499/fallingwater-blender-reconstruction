# Site module checkpoint

This report covers the site worker's local implementation. It is not full-scene acceptance.

- `site.py` builds continuous metre-scale terrain, stepped sandstone beds, Bear Run crossing bridge and paths, four principal water meshes, 55 advecting foam traces, 9 linked branching-tree assets, and 4 linked understory assets. Independent individual leaf surfaces have their own UVs, a raised midrib, procedural surface variation and transmitted light.
- Three successive 960×640 EEVEE diagnoses were opened and visually inspected. Fixes removed random green triangle assignments, blended harsh terrain exclusion boundaries, increased and reshaped foliage, placed rock behind the falling-water lip, and replaced coarse reflective twisting ribbons with 88 finer aerated streams. Diagnostic images are `site_overview.png` and `site_water_close.png`; the standalone scene deliberately lacks architecture.
- `site_smoke.py` directly builds the module through Blender 5.2.1. The successful build with 55 foam-advection traces took 5.84 seconds, used 624,964 unique vertices and had no extreme-coordinate vertices. Main water geometry changed through frames 1/61/121/181/241 and had zero sampled coordinate error at loop closure; the foam sample also closed with zero position error. Thirteen leaf mesh assets have explicit per-leaf UVs. Subsequent `site_smoke.json` gives the latest timing and checks. Foam height now follows a four-segment sampling of the actual water surface along its downstream path.
- `site.py` reads current guest registration from `data/guest_house.json`, respecting `config.guest_registration`, and derives ground caps and plant exclusions per room. Main exclusions keep terrain beneath the cellar and foundation bays. The bridge uses the first-floor drawing registration and has individually laid paving and stone parapets.

## Evidence and limitations

All river/terrain/individual-plant positions and hydraulics are evidence **C**. HABS sheet 2 explicitly limits surveyed reliability for the creek and paths. Local geometry is photograph-informed approximation; no lidar, complete terrain survey, species-level tree map or fluid simulation has been obtained.

The EEVEE diagnoses still show artificial regularity in the river and forest. Site photorealism is **not accepted**. After those images, the large water-wave artifact was traced to Generated coordinates stretching shader noise across the entire creek; the material now uses metre-scale Object coordinates and a thinner water lip. The integrated building scene needs Cycles comparison at both the classic downstream and close-water cameras, plus repeated matched-view refinements. Static-frame smoke checks do not prove ten-second visual continuity, absence of shader flicker, or real-time navigation performance. A 10-second animation diagnostic remains for the integrated near-water camera; the main integrator has been informed.

The site owns no lighting or final cameras. Suggested cameras and exact fixed seed are in `data/site.json`. No external textures or purchased assets are used by this module; all geometry and procedural surface definitions are locally authored.

## Integrated hero feedback — site revision 2

The first integrated Cycles hero (`renders/previews/iteration01/CAM_HERO.png`) was actually opened. It exposed three P1 issues: regular curtain-like waterfall, sparse pole/conifer-like tree structure, and a largely bare hillside. Foreground branches also crowded the camera. These were treated as structural defects, not exposure problems.

Revision 2 replaces the continuous curtain with nine unequal rock-controlled flow packets, with sideways displacement, irregular open air holes and retained dry gaps. A sampled uneven lip replaces the straight edge; 115 partial impact arcs and 55 downstream foam traces follow the impact pools. The direction of traveling surface detail was corrected to progress downstream. The soil volume covering the waterfall rock face is removed; eleven actual sandstone strata and broad fractured rock shoulders occupy that volume.

Mature trees now end their main bole at low forks and form three or four unequal broadleaf crowns on curved structural branches. Young trees have two or three lower crowns. All foliage remains individual leaf geometry attached to actual twig branches. Tree distribution is denser with separate lower vegetation, and the downstream photographic lookout has a camera clearance mask. The surface includes topography-following moss patches and clustered weathered leaf litter.

The non-render Blender smoke test passed: **9.98 seconds** module build, **655,359 unique vertices**, **324 linked tree instances**, **2,400 understory instances**, **835 moss patches**, and **8,455 individual fallen leaves**. Fourteen foliage/litter meshes have leaf UVs. Both surface and foam sampling closed the 240-frame loop with zero measured error. Full details are in `site_smoke.json` and `site_build.json`; the tree-asset replacement and its own bounded test record are in `site_tree_design.py`.

No GPU rendering was performed for this revision, as coordinated with the root integrator's lighting work. The prior diagnostic images describe earlier revisions and must not be used to accept this revision. **P1 visual acceptance remains pending a matched integrated Cycles rerender.**

## Integrated hero feedback — site revision 3

Both `iteration02/CAM_HERO.png` and `iteration02/CAM_WATER_DETAIL.png` were opened. Revision 2 still failed the photorealistic target: conspicuous regular stacked rock plates, opaque strip-like water, faceted/collared tree branches, open sky through narrow crowns and visible bare slope. The procedural waterfall has not been accepted; the root integrator is commissioning the required local fluid-simulation sample. This revision does not change the water implementation or run a fluid bake.

The cliff is now one continuous closed sandstone volume with nine uneven geological bed intervals, shallow varying dip, eroded fronts and vertical joint interruptions. Side shoulders use fewer, thicker, overlapping fractured volumes with unequal outlines; the former eleven regularly separated plates are removed. All rock objects directly use the shared `FW_rock` and `FW_wet_rock` materials, allowing the root's `asset_materials.py` to apply the newly obtained CC0 `worn_rock_natural_01` photograph texture. The terrain retains the explicitly mapped `FW_Continuous_Forest_Floor` material for CC0 `forrest_ground_01`. Thus the earlier statement that this module had no external surface assets describes earlier revisions, not the integrated revision-3 material pipeline.

Tree curves now use continuous shared vertex rings with stable transported cross sections and smooth bark normals. Primary attachments are staggered and buried in the parent surface instead of ending in raised collars. Asset tests show crown widths increased by approximately 36–42%, with lower leaf-bearing branches; mature heights vary from roughly 12 to 19 metres. Leaf backlighting transmission was adjusted, and visibly flat green moss patches were replaced with short filament geometry following the ground.

The revision-3 smoke build passed in **19.05 seconds**, with **929,130 unique vertices**, 324 tree instances and 2,400 understory instances. A separate reopen geometry test passed: the main cliff has **zero nonmanifold edges**, outward orientation with positive volume **307.97 m³**, and exactly the shared wet/dry rock material assignments. All bark faces in nine tree assets are smooth. A 13-frame sample confirms foam movement, and frame 241 closes its loop. Evidence: `site_revision3_geometry.json` and `site_smoke.json`.

No rendering or fluid work was performed. **Visual P1s remain pending the root's matched integrated Cycles test and fluid sample.**
