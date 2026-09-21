# Masonry12: upper main tower, source diagnosis only

2026-09-21, site_visual. **DESIGN_ONLY / NOT_BUILT / NOT_RENDERED / NOT_VISUALLY_ACCEPTED.** No production code, material, geometry, camera, source asset or scene was changed. The single CPU4 Blender probe opened the frozen main-terrace11a scene, evaluated frame 48, wrote QA and exited without saving. Source SHA remained `e856456005d3a4493e70122644d52192dd49c2d2ffc046248b1247484beb4750`.

## Actually viewed evidence

| Evidence | Actual observation | Limit |
|---|---|---|
| Official [Classic Spring](https://fallingwater.org/wp-content/uploads/2021/03/FW_ZOOM_Classic-View_SPRING.jpg), local `forest-canopy11-source-official-classic.jpg`, 1920×1080 | Upper central tower, approximate source rectangle x470–679/y51–342: irregular long thin beds, occasional thicker blocks, shallow fractured ledges, short staggered vertical joints, continuous corner bond. Broad face roughly x493–622, narrow return x625–676. Pale gray/buff in daylight, ochre near lamps. | B observed morphology. Exact per-stone bond and RGB are not measured. Perspective, illumination and foliage prevent scale recovery from pixels alone. |
| Official [East Spring](https://fallingwater.org/wp-content/uploads/2021/03/FW_ZOOM_East-Elevation_SPRING.jpg), local `forest-canopy11-source-official-east.jpg`, 1920×1080 | Long thin slabs in x942–1104/y226–419; thicker blocks interleaved with thin packing in x1112–1279/y190–790. Broken edges and shadow gaps have real depth; neither face is uniform granite paneling. | B corroboration from another orientation; this east pier is **not asserted to be the same physical west-tower face**. Date unknown beyond filename Spring. |
| HABS PA-5346 [sheet10 sections](https://www.loc.gov/pictures/item/pa1690.sheet.00010a/), `main-10-sheet.jpg`, plus existing TIFF-derived `main-10-inspection-levels.png` | Sections confirm vertically continuous masonry masses, openings, different terrace datums and a layered exterior representation. West section upper tower hatch region approximately JPEG x467–631/y444–522. | A datums/structure; drawn stone hatch is not a stone-by-stone measured bond or measured joint depth. Full original TIFF direct-display attempt failed with invalid base64; only the JPEG and existing native datum crop were actually viewed this task. |
| HABS [sheet07 south elevation](https://www.loc.gov/pictures/item/pa1690.sheet.00007a/), `main-07-sheet.jpg` | Main-tower position and narrow south return, JPEG approximately x293–317/y171–339, support the group identity and continuity through levels. | Used for identity, not new plan tracing or exact stone dimensions. |
| main-terrace11a / `CAM_MAIN_L2_TERRACE_W_A.png` and `CAM_MAIN_L2_TERRACE_S_A.png`, 960×540 | W: broad smooth mottled slab wall around doors plus narrow regular coursing at right edge. S: upper-left brick-like side courses and bare smooth tower end; glass/terrace parts outside this task. | Images actually opened; these close views are the source of the ray-identification rows below. |
| `worn_rock_natural_01_diff_2k.jpg` | Warm mottled worn rock with roughly isotropic flaked areas; not a scan of Fallingwater masonry, laid thin beds or mortar. | CC0 PBR is usable microdetail, not evidence for masonry bond or physical joints. |

Official photographs remain **reference-only, excluded from public release**, never textures. Existing rights/source metadata is preserved. File hashes, pixel rectangles and viewed flags are in `masonry12-source-viewed.json`; this report does not change the central manifests.

## One target group, with actual identities

**Upper main west tower only**; nominal structural z=5.25–9.46 m. Use exactly the 300 existing `MAIN_tower_course_courseRR_JJ_SIDE` finish objects listed individually in `masonry12-source-targets.json`, not a broad runtime wildcard. RR=00…29, SIDE=-1 or 1. First/last lexical identities are `MAIN_tower_course_course00_00_-1` and `MAIN_tower_course_course29_04_1`.

The two structural objects and three cap/flue objects are guards, not replacement targets:

| Guard object | Current world bounds, metres |
|---|---|
| `MAIN_stone_tower_west` | X -0.941400…-0.211400; Y 8.389800…11.363400; Z 5.25…9.46 |
| `MAIN_stone_tower_north` | X -0.628800…0.157200; Y 10.993401…11.733400; Z 5.25…9.46 |
| `MAIN_chimney_cap` | X -1.100400…0.419200; Y 8.283600…11.682000; Z 9.44…9.56 |
| `MAIN_chimney_flue`, `MAIN_chimney_flue.001` | Z 9.57…9.60; full bounds/hash in probe |

The 300 finish blocks occupy X -0.976900…-0.175900, Y 8.395800…11.357400, Z 5.256500…9.453500. Both long wall faces receive a matching sequence. North return, lower L2 core, hearth, all other walls and bridge remain outside the candidate scope.

Actual render-pixel rays, top-left image origin, frame48:

| Image and pixel | First hit | World point (m) | Implication |
|---|---|---|---|
| W (940,55) | `MAIN_tower_course_course05_02_-1` | (-0.968569,9.725069,6.020320) | Selected upper tower is visibly brick-like. |
| S (69,25) | `MAIN_tower_course_course07_03_1` | (-0.188400,8.949616,6.285588) | Opposite long face has the same problem. |
| S (31,36) | `MAIN_stone_tower_west` | (-0.375914,8.389800,6.065713) | Bare south end is exposed; two-face decoration alone leaves a smooth end. |
| W (405,185) | `MAIN_L2_dressing_shell_north_0` | (-4.474401,16.021788,4.426068) | Broad door wall is **not this tower**. |
| W (352,47) | `MAIN_L3_study_core_0` | (-4.401999,16.483191,5.624643) | Upper smooth slab belongs to another group. |
| W (943,185) | `MAIN_L2_core_course11_04_-1` | (-0.913566,9.570344,4.407692) | Lower coursing remains a separate later scope. |

Thus improving this one group cannot be reported as repairing all masonry visible in the two terrace views.

## Cause, supported by saved scene and code

1. **A five-height repeating bond, not absent texture.** `main_house.py:396` builds 30 rows. The five usual actual mesh heights are 82 / 98.25 / 114.5 / 130.75 / 147 mm, plus the final clipped 51.75 mm. Median 114.5 mm. Lengths use a four-position arithmetic schedule with alternate-row stagger. Both faces mirror this schedule, with five pieces per row per face. There are no genuine occasional very thin packing slabs.
2. **The visible joints are wider than the apparent input gap.** `z += height + .016` while mesh height is `height - .013` yields **29 mm** horizontal gaps. Along a row, `.015` advance plus `.012` mesh shortening yields **27 mm** vertical gaps. The substrate is present behind them; the repeated wide grid reads as brickwork.
3. **Every stone is an eight-vertex rectangular box with the same style of bevel.** Evaluated stone count is 300×108 = **32,400 triangles**. Bevel widths 6 / 7.667 / 9 mm, two segments; all evaluated polygons flat shaded. There is no smoothing-normal mistake or missing bevel application: the rounded edge profile itself is uniform. Protrusion beyond substrate varies only 23…35.5 mm. Faces remain planar beneath shader bump. Two regular walls do not wrap around the bare south end.
4. **Saved PBR is active and in metre-scale object coordinates.** All target object scales are (1,1,1), dimensioned local vertices carry real metres. Object→SCALE .5→BOX image is a 2 m texture period, blend .22. Diffuse(sRGB)→multiply(.68,.73,.72)→Base Color; roughness(Non-Color)→.63… .90; displacement image(Non-Color)→Bump strength .5/distance .022 m→Normal. The older procedural bump/color nodes are disconnected from the shader. Bump is normal perturbation, not silhouette or mortar geometry.
5. **Per-box local phase repeats.** Each box samples the same central neighborhood of the 2 m image from its own centered local coordinates; rotations are shared. This adds repeated mottling. It is not an incorrect scale factor. The large substrate samples a broader portion of the same mottled scan and reads as a granite slab when no actual joints cover it.
6. **Lighting is not ruled out.** AgX, exposure +.8 and scene lighting influence the rendered cool gray appearance. Source photographs vary between shadow, daylight and warm lamps. No source justifies replacing global color with a sampled photographic RGB. Geometry and repeated phase explain the grid even without a color correction.

## Minimal independently reviewable candidate proposal

**C reconstruction, not a measured bond.** Replace only those 300 finish objects and introduce at most **three joined mesh batches**: west long face, east long face and the narrow south end of `MAIN_stone_tower_west`. Do not rebuild the tower core, alter its height, add thickness to the structural mesh, decorate all building walls or touch the north-return structural object. South-return finish is needed for the actually visible bare end, not a new structural wall.

Suggested first and only prototype parameters:

- Preserve source-inspired long horizontal bedding and corner continuity. Use a finite non-repeating course layout, about **40–46 course bands across the 4.18 m finish height**, not the same cross-section on every band. Interleave thin 35–70 mm stones, common 75–125 mm stones and occasional 130–195 mm blocks. These numeric ranges are C with roughly ±30% morphological uncertainty, not dimensions read from HABS. Allow short thin packing stones beside thicker neighbors so every seam does not cross the full face.
- Long stones mainly .35–1.05 m, a few short closers .12–.30 m. Avoid equal five-piece rows. Use staggered short vertical joints; only a few larger bedding lines remain laterally continuous. Correlate profiles where the bond turns the south corner, without identical mirrored faces.
- Target actual clear horizontal joint widths **6–12 mm**, vertical **6–14 mm**, backed by the existing intact substrate, with front-to-substrate recess **12–35.5 mm**. Return front may project south by at most35.5 mm; new Y minimum 8.354300 m is a C local allowance requiring clearance tests. No negative-thickness planes or coplanar mortar overlay. Back of each stone can enter its substrate by .8 mm for contact; exposed front cannot be coplanar with substrate.
- Use closed angular stones with a few localized 2–6 mm chips and interrupted ledge edges across .15–.4 m segments. At most a few facets per face; no uniform round bevel, high-frequency noise displacement, inflated blobs, or random protruding boulders. Avoid self-crossing corner shells by clipping the three batches to disjoint corner ownership and bonding the visible edges.
- Constrain long-face outward extents to the existing X envelope [-.976900,-.175900]. Finish z within [5.2565,9.4390] to stop below the preserved cap; the old top stone intersects the cap's z9.44 start. Preserve actual opening, floor, roof and cap shapes. South-return and corner samples must respect the same union of allowed envelopes.
- Budget **≤560 closed stone components, ≤40,000 triangles total, ≤3 added mesh objects**, no runtime Boolean or per-stone modifier stack. This provides extra edge information at comparable evaluated size to the old32,400 triangles.
- Use a **local copy** of FW_stone for new finish only, retaining the existing image sources, 2 m width and initial tint/roughness. Give the joined batches a consistent world-metre origin or explicit metre UVs, avoiding per-stone centered-image repetition. As the single material adjustment, reduce bump distance from22 to **6 mm (C, range4–8 mm)** so isotropic worn-rock relief remains secondary to actual split-stone geometry. Do not globally tint FW_stone, add another paid/scanned asset, change exposure or vary every stone to a different saturated color. If this limited material still reads mottled in the controlled render, mark that result honestly rather than call it sandstone photorealism.

## Interface and physical safeguards before any later build

- Existing `masonry_detail.build` is **not the exterior tower builder**. It only creates `FW_MASONRY_MAIN_HEARTH` and `FW_MASONRY_GUEST_LOUNGE` from `masonry-detail.json`. Its build deletes all `FW_MASONRY_*` before validating required objects. Reusing that entry for the tower risks deleting accepted interior finishes. A later local helper needs its own exact namespace, dry validation before mutation, and an idempotence/partial-application guard.
- `main_house.stone_courses` is a nested function used for other piers/core/hearth. Changing it globally affects unrelated surfaces. A candidate must apply to the exact saved300 whitelist after source fingerprint validation, and preserve the generator until explicitly integrated.
- Saved **FW_stone has2,908 mesh-object users**, including both accepted interior masonry batches, original bridge abutments and four accepted bridge10 return walls. Never mutate that shared material or clear its slots. New material names must be private to the finish batch. Any later substrate material editing would be an additional scope request; this proposal needs none.
- The existing masonry_detail UV/comment claim “world metre mesh coordinates” does not automatically apply to centered box objects. A new batch origin/UV convention must be explicit. Check texture width after any transform; never normalize a metre mesh to0…1 without compensation.
- Old bridge coplanar finish panels produced visible black end strips. Avoid this known failure: closed stones, substrate penetration only on hidden backs, no duplicate faces, no coincident exposed ends, no shadow-only dark plane. Check normals and degenerate triangles in a fresh process.
- Freeze every non-target object fingerprint, all original material node graphs, lights, cameras, image settings, tower guards and primary core/water/terrain/bridge/path hashes. Do not use a whole-scene rebuild reading concurrently edited configs; later parent chooses a new frozen source and records hashes.
- Quantitative checks: exact300 old object identities; target structure hash unchanged; all component surfaces closed/manifold and nondegenerate; front/back signed depth and allowed-envelope checks; no intersecting adjacent exposed corners; actual nearest camera distances for **every current camera and tour position**, and swept route collision tests, especially third-floor study/terrace near z5.25. No nominal AABB-only pass. Candidate needs saved/reopened equivalence, and repeat application must be a verified no-op or a clear pre-mutation rejection.

### Separate dimensional issue, not silently repaired here

Actually viewed existing high-resolution sheet10 datum crop shows MAIN TOWER **32′9½″ =9.9949 m**, while saved upper cap ends9.56 m and flues9.60 m. The current group's label/extents do not establish which physical highest feature HABS dimension addresses. This is a discrepancy for the parent's dimension audit; **it is not a warrant to stretch a wall during surface work**. Freeze current geometry for this candidate and do not call its tower height A-verified. It was communicated to root separately.

## Same-view decision gate for parent

After a later authorized candidate exists, use the parent's actual frozen integrated source and matched frame48, camera matrices/lenses, world, lights, AgX, exposure and sample settings. The already-viewed reference pair gives exact local identification:

1. `CAM_MAIN_L2_TERRACE_W_A`: old right-hand tower should lose the repeating brick grid; dressing/study slab walls must remain visibly unchanged.
2. `CAM_MAIN_L2_TERRACE_S_A`: inspect both thin-course side and newly bonded narrow south end; no black strips, outline bulge, cap penetration or door obstruction.
3. Parent-selected existing classic exterior/HERO camera: stone tower must read as horizontal split sandstone at overview distance, not a noisy tiled surface. Do not create a flattering camera in place of the existing view. If the saved HERO framing does not show the target, report that limitation and use the existing appropriate exterior view identically on both source/candidate.

No model candidate or render is delivered in this task. This is a finite first proposal, not acceptance of the material, tower dimensions or entire environment.

## Documentation reconciliation

neat-freak applied within assigned QA-only ownership. Current source/interface facts and explicit NOT_RUN states consolidated here and in the machine-readable probe/view/target files. Root `AGENTS.md` already requires actual image review and preserves failed evidence; it needs no duplicate history. `STATUS.md`, manifests, runtime modules and central memory remain parent-owned and untouched. No commit, public upload or asset relicense occurred.
