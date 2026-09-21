# Guest/service geometry review

State: independent module built and rendered in Blender 5.2.1 LTS; integration still required.

- Sources actually inspected: all four guest HABS JPEG sheets and all four original TIFFs; original-resolution crops of first-floor dimensions/room labels, basement, second-floor service rooms, west elevation and north-looking section datum labels. Original files and SHA-256 are listed in `data/guest_house.json`.
- 20 spatial records retain Laundry Room and Bath, 2010 Theater, Car Court, Chauffeur Lounge, Boiler Room, service stairs, Lounge, connecting gallery, Guest Room/Bath, pool terrace/pool, three upper service bedrooms, upper bath/hall/terrace. Names marked gallery/hall are circulation interpretations rather than invented surveyed labels.
- 22 independent dimension/elevation transcriptions are retained. Nominal room dimensions are not substituted for rectangular room polygons; unmeasured model values remain null. Scan X/Y scales are independently cross-checked against the pool outside horizontal dimension and service-wing vertical chain; trace uncertainty remains approximately one normalized pixel (roughly 5 cm), plus wall-edge interpretation.
- Explicit openings divide wall geometry into piers, sills, and heads. Windows have narrow steel frames and finite glass. Open door leaves keep inspectable frames. Stair floors omit their principal voids; an upper landing return strip was added after reviewing the stair route.
- Stone coursing is actual batched geometry with horizontal joints and shallow varying projections. Bath floors are cork; main surfaces use the shared architectural material palette.
- Pool shell is a rounded hollow basin with surveyed 30′1″ × 13′0″ plan dimensions; top of pool wall follows +2′3¾″ relative guest level. Water and basin depth remain C.
- First Workbench review exposed triangular canopy gaps. These were fixed using shared-edge curved-strip mesh sections. The revised overview image was actually opened and inspected; it shows continuous canopy segments and the distinct pointed service-wing end, low guest arm, and pool.

## Evidence

- `guest-geometry-test.py`: actual Blender build/diagnostic render command.
- `guest-geometry-check.blend`: module-only saved checkpoint, complete architecture (not an interior/site delivery).
- `guest-geometry-overview.png`: latest full geometry view.
- `guest-geometry-cutaway.png`: diagnostic view; the single batched sandstone mesh is retained and therefore can show upper-level veneer in the cutaway. Use the full model for completeness checks.
- `guest-geometry-build-report.json`: actual execution statistics and Blender version.
- `guest-geometry-world-rooms.json`: transformed world room records from last smoke check.

## Limits requiring integrated QA

1. Final main/guest registration and absolute guest datum are being reconciled by the integrator; XY has been frozen from site2 at (3.4, 37.1); absolute guest datum remains 8.4 m, C, with provisional range 7.4–9.4 m. Guest relative elevations are now based on independently viewed labels, not provisional generic floor heights.
2. The full circulation graph, stair return, furniture collisions and each room entry require combined architectural/furniture navigation inspection. This module test does not claim route QA passed.
3. Original fine joinery, boiler/laundry fittings, theater fittings, subtle roof transitions and terrain contacts are C/U as appropriate. The architecture builder does not claim historical furniture fidelity.
4. Workbench output proves geometry visibility and buildability; it is not photoreal acceptance, performance evidence, or 4K delivery.
5. All source-image files remain references rather than texture assets; no source artwork is silently embedded in materials.

## Site registration follow-up

The site2 original was actually inspected via `site-02-review.jpg`; an annotated centerline crop is retained as `data/guest_refs/site-connector-grid.png`. The connector is now registered to its visible arc, including west centerline near site pixel(483,246), lower centerline(549,297), and guest landing near(523.3,193.2). Its 2.48 m canopy width is kept separate from its 1.72 m walking width. Source/main matching, the unchanged measured main endpoint, and the deliberately approximate Z interpolation are retained in the JSON.

No shared numerical absolute benchmark was found in guest4 or the inspected main8–11 material. Guest4 datum0′0 is independent, and main11 is a detail sheet. The unsupported absolute precision was not invented.

## Integrated P1 correction: service stair and bathroom finishes

The upper service corridor slab was incorrectly present over the start of the ascent. Its southern edge now stops at drawingY351, the west return strip runs X287–306/Y351–404, and the original top landing remains at Y404–422. The stair geometry and surveyed level rise were preserved.

`guest-geometry-clearance-check.py` rebuilt the module without rendering and cast rays against evaluated meshes at47 positions (14 tread centers×3 body-width offsets, lower approach, upper landing and west return). Minimum measured vertical clearance was2.120m, exceeding1.95m. Reintroducing the old solid slab in memory caused12 failures, confirming that the regression test detects the reported defect. Full samples and hit-object identities are saved in `guest-geometry-clearance-report.json`.

Bathroom walls now carry8mm one-sided cork linings, clipped to the bathroom portion of shared wall runs and to real door openings. The other wall face keeps its architectural substrate. Actual built lining counts are8 in guest first-floor bath,6 in basement bath, and6 in upper service bath, all usingFW_cork and tagged to their room. Floor cork remains. This update did not re-render while the integrator was using the GPU; existing overview images predate this fix.

## Structural validator v2 retained failures — corrected

Added the boiler projection roof north of the low arm, following guest sheet2 roof footprint and joining the existing roof at normalizedY346. All five originally failing boiler probes now strike the floor atZ8.4 and the actual roof underside atZ10.56, with opposing horizontal normals.

The flat terrace census now stops atX697 south ofY417; its previous overlap with pool/coping/stairs was removed without adding any floor geometry. The original failed probe(24.69994,35.67970) is outside the terrace polygon, inside the pool census, and still intersects the actual pool water atZ8.96485. All three previous valid terrace probes retain actual flat floor hits.

Executed `guest-geometry-v2fix-check.py` in Blender5.2.1 without rendering; `guest-geometry-v2fix-report.json` records all original probe positions and actual mesh hits. These are focused module fixes awaiting the rebuilt integrated validator run, not final project acceptance.
