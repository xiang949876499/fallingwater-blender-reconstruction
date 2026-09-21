# Forest litter12: bounded ground morphology

This candidate is separate from both the floor11a shader and canopy11 changes.
Root accepted the soil-color direction of11a, but its three real images still
failed environment realism (`forest-floor11-root-visual.md`). Existing source
geometry is frozen; no slope correction is part of this task.

## Reference, interpretation and bounds

The official Spring east/classic images and all three actual1280×720
forest-floor11a images were opened and inspected. Spring references show
interlocking understory, woody stems and darker ground/organic fragments
between plants. They do not establish the species, individual fern positions,
exact leaf count or moisture of the candidate. The far bank vegetation and
terrain outline remain outside this local layer experiment.

Actual terrain-only camera rays are preserved in `forest-litter12-probe.json`.
Loggia's dominant left slope samples world X23.387–26.611,Y9.873–15.302;
the bridge-facing bank samples X27.450–39.071,Y9.306–12.406. Several actual
normals have Z.44–.56, meaning steep ground. The layer is constrained to
**X23–40,Y9–19 metres**, and no source terrain vertex is changed.

Sixteen non-grid windrow/plant neighborhoods follow local contour direction,
with unequal extents/masses and Gaussian falloffs. Roots and leaf blades still
have independent actual contact/exclusion tests. This is a C ecological
composition, not evidence that these exact windrows existed in the photo.
Leaf accumulation thins on steep ground; candidates below normalZ.40 are
rejected. Low fern roots require normalZ≥.55. A large hillside cannot be made
source-faithful by covering its wrong shape, so the geometry limitation remains.

Maximums for this single candidate are24,000 fallen leaves,40 low fern clumps
and65 small twigs. Actual admitted counts are in the build manifest; maxima are
not passed-off as achieved counts. A future merged scene must perform its own
navigation/image review rather than inherit this independent candidate's gate.

## Assets, authors and rights

| Asset | Authorship / license / actual use |
|---|---|
| Curled fallen-leaf mesh and five surfaces | Original project-authored procedural geometry and shading in forest_litter12.py. Unequal12-point outlines plus folded center, .065–.145m blades; not a site scan or botanical species claim. |
| Small fallen-twig mesh and surface | Original project-authored six-sided bent closed tubes, .20–.62m long and2.2–5.0mm radius. No borrowed photograph is used as a texture. |
| [Poly Haven Fern02](https://polyhaven.com/a/fern_02) | Rob Tuytel scanning; Rico Cilliers modeling; CC0 according to the already-recorded official asset/license metadata. Four physical variants, shared native geometry/material/texture assets. Species U, local placement C. |
| Official Fallingwater Spring photographs | Reference only. Copyright Fallingwater; provenance and original URLs in forest-canopy11-sources.json. Not a texture and not for public model redistribution. |

Existing fern package: `assets/candidates/fern_02_2k/fern_02_2k.blend`, SHA256
`cf721e00ed5bb72f0b9c3fb59b8febc7b2b9b2082f162d5a80ba3a11e4e7028d`.
Its official download/author/license evidence remains in
`near-tree-asset07-download.json`, `near-tree-asset07-fern_02-info.json` and
`near-tree-asset07-review.md`. No new package was downloaded. The diffuse atlas
was actually opened this turn: serrated pinnate green fronds and small brown
patches are visible. That atlas inspection is not a new rendered-plant approval;
the previous unavailable vendor-preview status is not relabeled.

New material/image IDs are prefixedLITTER12. Appended texture paths are repaired
only on those new IDs. The original package files and all existing scene image
settings/materials are preserved. The six existing floor11a CC0 textures remain
unchanged and the litter helper does not require or reapply that shader.

## Physical placement and validation

Every leaf outline/center is projected onto the actual saved terrain BVH,
then given millimetric curl. Triangle centers are also checked. A leaf crossing
a crease is rejected if it cannot meet the small contact range; no horizontal
sheet bridges the bank. Five chromatic leaf surfaces and irregular shapes
produce local color variation without an opaque monochrome ground patch.

Twigs follow six actual terrain-supported points; their closed tubes include
both end caps. Fern source roots retain their slight below-origin stem region,
with at most45mm soil embedding allowed only in the explicitly identified root
zone. Every remaining fern vertex and face center must clear the actual ground;
unknown floating-frond results are not automatically called rooted.

Exact saved path-strip polygons receive an extra .24m exclusion around all new
geometry. Actual nearby main/guest/furniture/stone/water and woody-tree meshes
form a separate protected-surface BVH; construction surfaces and water above
terrain cannot be used as soil. Room footprints provide an additional
conservative exclusion. The admitted leaf, twig and fern extents—not just
their origin points—are tested. Nothing is moved to accommodate placement.

The independent readback tests actual saved new vertices and polygon centers,
terrain clearance, exact path/room-footprint exclusions and complete original
scene fingerprints. It is local change evidence, not a replacement for all
adjacency/camera-frame checks on the final combined scene. Root performs all
rendering and visual acceptance with the same three11a camera overlays.
