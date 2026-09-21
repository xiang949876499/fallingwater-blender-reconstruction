# Main04 dimensions and corrected geometry

The four room annotations are legible, not OCR errors. None has arrows or extension lines fixing its endpoints or axis assignment. They remain **NOT_RUN for nominal-label conformity**: bounding boxes and numerically similar furniture-to-wall spans are not proof of intended endpoints. The original TIFF was actually inspected again at the rock edge, stair strips, kitchen jambs and south-window line.

Source: `research/references/architecture/main-04-original.tif`, rotated clockwise to17683×13632 and addressed in the existing1024×789 frame. `main-dimension-resolution-evidence.json` records original crop bounds, source/artifact hashes, analytical points and conclusions. Colored lines in the images are **analyst overlays(C), not original dimension arrows**. All four annotated crops were actually opened.

| Annotation | Current mesh and conclusion | Source crop |
|---|---|---|
| Living33′8″ /10.2616m | Complete stepped floor X span11.2136m. Visible seat-front-to-stone-face diagnostic≈9.7726m measures a different quantity. No arrows connect either to the label. No scaling or wall shift applied. | [Living width](main-dimension-resolution-living-width-annotated.png) |
| Kitchen15′9″ /4.8006m | Original core floor stopped at y318; the traced south step is at y320–321. Core diagnostic y230–321 gives4.8321m. The traced projecting window bay reaches y331, making the full bounding span5.3631m. Label endpoints remain unspecified. | [Kitchen length](main-dimension-resolution-kitchen-length-annotated.png) |
| Servant11′5″ /3.4798m | Restored the missing northern bay. Corrected X span3.1964m; assigning the label to X was unproven. The separate10′11″ dimension below the room has extension lines for an outside span and was not substituted for this label. | [Servant length](main-dimension-resolution-servant-length-annotated.png) |
| Servant9′4″ /2.8448m | Corrected Y span2.88333m versus old2.0709m. The room visibly extends to the stair partition near y214.7. Difference+38.53mm would exceed GEO-02 if this axis correspondence were proven; it is not reported as passing. | [Servant width](main-dimension-resolution-servant-width-annotated.png) |

## Implemented geometry

Kitchen door moved from incorrect source x324/y294–315 to traced x324/y270–287. The old opening is continuous masonry, with no alternate doorway. World endpoints are(−0.1572,14.3370,0.10) and(−0.1572,13.4343,0.10), gap0.9027m, approximate stone thickness0.3668m. Door height2.05m remains C. Entry, threshold and exported metadata match. New probe is(−0.5240,13.88565)→(0.3668,13.88565).

Servant floor/ceiling now include the north bay against the rock/stair boundary. The descending stair strip is y200–213; its former modeled center y213 incorrectly occupied the bay. Center moved to y206.5, width0.68m, retaining the separate stair opening. Exact vertical stair details remain C.

Kitchen south glazing follows the original three-segment line(260,319.4)→(272.5,319.4)→(272.5,331)→(307,331), with matching floor projection. See [original south-window detail](main-dimension-resolution-kitchen-south-detail.png). HABS photograph PA-5346-56 (`project/data/photo_refs/main_kitchen_56.jpg`) was actually viewed and shows floor-height glass with multiple horizontal steel bars. New glazing runs Z0.12–2.40m, with different bar patterns for front/return. Heights and detailed divisions are photograph-based C, not surveyed. Stone bounds and the corrected door are retained.

## Actual checks and precision

Current CPU main-house build:40 inspection spaces,3599 objects,22160 raw faces. `main-dimension-resolution-check.json` contains79 evaluated-mesh checks first run on the source-corrected iteration04 module:25 new-door body rays,3 old-opening closure probes,5 north-bay floor/head checks,39 service-stair support/1.95m head probes,7 south-window/bay probes. All pass. The23-threshold support/body audit passed after the door change. Integrated navigation and imagery remain separate acceptance gates.

`main-dimensions-measured.json` uses **GEO-02=max(0.020m,0.005×reference length)**: **5 numeric PASS,16 NOT_RUN**. Reading uncertainty is separate. The superseded report using uncertainty as tolerance is preserved in `main-dimension-resolution-initial-measured.json`.

The original TIFF supplies true extension lines for the north-spine **11ft /3.3528m** label. Native column centers5670.5 and6776.5 correspond to source x328.3714301872 and392.4184810270, a traced3.3560654640m. The former integer trace328..393 gave3.406m and was53.2mm too wide. See the actually viewed `main-dimension-resolution-spine-source.png` and `-spine-grid.png`, with extracted line groups in `main-dimension-resolution-spine-profile.json`.

The minimum source-supported correction keeps the west return fixed and shifts the east return53.2mm west; the adjacent horizontal wall endpoints and Living floor/ceiling inner corners follow it. No other walls or nominal room dimensions were adjusted. Independent evaluated mesh faces now measure **3.3527998999m**, difference−0.0000001001m from the label, passing GEO-02. The four actual slab/roof elevations also pass; the remaining16 comparisons retain NOT_RUN. Numeric arithmetic does not upgrade C reconstruction to surveyed precision.

Main09 east-band review uses the L2 datum at image row407 and L1 datum at461:54pixels represent2.8448m. Traced outer contour rows440.52 and470.24 imply approximately+1.079/−0.487m relative to L1 terrace. Only the two L1 east parapet segments changed to **−0.49…+1.08m**, with floor planes and XY fixed. The exterior contour includes the downward structural band; it is not merely the rail above the floor. See `main-dimension-resolution-east-parapet-grid.png` and `-east-parapet-datums.png`; both were actually viewed. This JPEG graphical reading is C±0.055m and is not an additional GEO-02 anchor.

The missing geometry and wrong doorway are corrected. The four un-arrowed labels and all-dimensions acceptance are not claimed resolved.
