# Two local west stone faces, candidate12a

2026-09-21. Scope is exactly the west exterior faces of `MAIN_L2_dressing_shell_north_0` and `MAIN_L3_study_core_0`. The latter also receives its source-supported, existing-frame-aligned genuine window aperture. No tower treatment, other Dressing wall pieces, north/east faces or global material changes are included. Visual acceptance remains **NOT_RUN** until the integrator opens the controlled renders.

## Actually inspected sources

| Local evidence | Observation and evidence boundary |
|---|---|
| `renders/previews/checkpoint10-exterior/CAM_HERO.png` | The upper left and middle left walls read as large smooth mottled slabs. Their stone identity is lost despite a working stone texture. |
| `renders/previews/main-terrace11a/CAM_MAIN_L2_TERRACE_W_A.png` | Close view of the same west side shows unbroken panel texture around openings. Existing independent ray identification in `masonry12-source-review.md` locates pixels (405,185) on Dressing north0 and (352,47) on Study core0. That report's ray evidence is attributed, not a new pixel measurement by this agent. |
| HABS `main-05-sheet.jpg` | Second-floor Dressing west perimeter has separated solid wall pieces and window/terrace openings. The selected north0 piece spans source x246/y227–253. This task does not generalize the finish to all Dressing pieces. |
| HABS `main-06-sheet.jpg` | Third-floor Study west perimeter has a real window at approximately source x246/y259–276. Existing production code placed its frame there but left an uncut continuous stone core. |
| HABS `main-08-sheet.jpg` | West elevation explicitly depicts irregular horizontally coursed masonry around these upper west openings. The drawing supports stone identity and opening arrangement; individual joints are not measured construction records. |
| HABS `main-07-sheet.jpg`, `main-09-sheet.jpg`, `main-10-sheet.jpg` | South/east elevations and sections provide cross-checks of the masonry masses, contrasting solid concrete terrace bands, and roof/terrace levels. No new room datum or building dimension is inferred. |
| Official [East Spring](https://fallingwater.org/wp-content/uploads/2021/03/FW_ZOOM_East-Elevation_SPRING.jpg), local `forest-canopy11-source-official-east.jpg` | Actual thin horizontal ledges, occasional thicker blocks, broken edges and short staggered joints. The east pier is not misidentified as this west wall. Used as B morphology corroboration. |
| Official [Classic Spring](https://fallingwater.org/wp-content/uploads/2021/03/FW_ZOOM_Classic-View_SPRING.jpg), local `forest-canopy11-source-official-classic.jpg` | Stone differs visibly from smooth terrace concrete; long nonuniform bedding and shallow relief are visible. B morphology only, not measured RGB, individual bond or finish depth. |

The two official photographs remain copyrighted reference-only material. They are not used as textures and are not copied into a distributable asset package. Existing source files and rights records are preserved.

## Actual scene diagnosis and bounded change

Frozen source: `scene/Fallingwater_navigation_candidate10a.blend`, SHA256 `1e7b17d9c2396513f005724e50788bf834097eedb401b91a7f1030825e2c4ed9`.

`masonry-wall12-probe.json` independently identifies both actual core meshes and their world coordinates. Dressing north0 is an eight-vertex solid spanning X−4.4744…−4.0144, Y15.2397…16.6203, Z2.8448…5.06 m. Study core0 spans X−4.402…−3.982, Y11.5227…16.6203, Z5.26415…7.60 m. Both use shared `FW_stone` and a 7 mm two-segment edge bevel.

The source Study window is blocked: the three source-only rays at Y14.4963/Z5.9,6.5,7.2 hit the wall at X−4.402. This negative evidence is preserved. The parent explicitly authorized correcting that real opening within this independent helper, rather than hiding it with masonry.

The rough aperture follows the unchanged jamb and sill/head **center lines**: Y14.0184…14.9211, Z5.70…7.46 m. It passes through the complete 420 mm wall thickness. The 38 mm perimeter steel sections therefore retain nominal 19 mm seating on each edge; actual seated probe points are checked inside the evaluated stone. Window framing, glass, existing opening leaf, wall object transform, bevel, outer perimeter, slabs and roofs remain unchanged. The opening is a window and is not declared a walking door. Its plan identity is supported by HABS; existing sill/head heights remain C.

Each exterior finish is a set of individually closed shallow stone solids joined in one mesh batch, with identity object transform and world-metre vertices. Longitudinal sizes are mostly0.38–1.01 m, with shorter closures. Randomly ordered finite course heights mix roughly40–155 mm stones, followed by6.5–10.5 mm bedding gaps; vertical joints are6–13 mm. Actual realization and extrema belong to the machine-readable manifest, not these target ranges. Per-stone front offset is approximately16.5–33 mm, hard bound35.5 mm; backing embeds0.8 mm into the actual original flat face. Edges have independent inward chips up to1.8 mm, not a repeated global bevel. Each front has5×3 stations and triangulated slight depth variation. There is no displacement, emission plane or large undivided noise panel.

The saved global stone material remains untouched. One private copy retains the source diffuse/roughness/BOX mapping at a2 m period, and reduces only its own bump distance from22 to6 mm because geometric relief now carries the joints. Existing Poly Haven `worn_rock_natural_01` CC0 maps remain microdetail, not a masonry scan or evidence of site color. No asset download or material recoloring occurs.

Actual evaluated neighboring triangles are clipped into each thin face envelope before projecting conservative exclusions. A giant terrain/tree batch bounding box alone cannot erase an entire wall. The real Study aperture receives an additional explicit mask. Split mask remnants have6 mm internal kerfs so no two new pieces share coincident closed end faces. No decoration is installed on another wall face or across an opening.

## QA meaning and preserved failed attempt

The first unsaved attempt projected aggregate terrain/tree bounding boxes and consequently rejected all stone pieces. Its later camera check failed on an empty mesh. `masonry-wall12-attempt01-check.json/log` preserve this implementation failure; no empty candidate was saved. The mask method was corrected to use actual triangle clipping and a minimum nonempty-surface guard, without weakening physical thresholds.

Attempt02 generated241 stones but actual mesh checking found top courses penetrating the unchanged Study roof. Its negative report/log remain. Exact native axis-aligned solids now contribute their occupied volume to the masks; other large batched meshes still use actual clipped triangles. No roof is moved and no collision exception is granted.

Attempt03 reached224 stones with local mesh/window/camera/route checks passing but failed the strict original-object preservation gate. The generic Boolean changed the core's derivedZ dimension from2.3358500004 to2.3361473083 m and introduced an unused material slot. The candidate was not saved. `masonry-wall12-core-property-probe.log` records the diagnosis. The final aperture implementation instead reuses the exact native eight outer corner coordinates and adds eight aperture-ring vertices in the wall's local coordinates, with16 connected quads. This leaves the existing object transform, outer dimensions, material slots and bevel exactly unchanged. `masonry-wall12-core-property-probe-native.log` confirms that only the expected mesh data pointer changes. It is not a threshold relaxation or an accepted exterior deformation.

The candidate checks closed, oriented positive-volume individual stones and core, actual backing contact, inter-stone intersections, non-target mesh collisions, outward-envelope limits, both-direction aperture rays and four-sided steel seating. Full original object/material/image/camera/light/world fingerprints protect every other part. All131 existing camera positions and all7584 integer tour positions are checked against the new finish; changed geometry is also tested along the complete frozen route with body/sweep rays. The independent readback additionally applies1.95 m body columns with0.18 m radial offsets and inter-frame sweeps at every relevant saved integer frame. This is regression of the local changed objects, not a new all-adjacency source or GUI navigation certificate.

Only independent saved-file reopening can conclude physical readiness. Root-controlled renders must still assess the visual result; no source-faithful bond precision or whole-building masonry completion is claimed.
