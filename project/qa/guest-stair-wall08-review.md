# Guest laundry exterior stair wall — 2026-09-20

**Candidate08b passes the bounded geometry/clearance checks below. Visual acceptance and the full iteration08 integration remain pending.** The missing opposing solid wall now exists, with the plan's rounded south end and thick north return. The original07 scene and tour, and the failed candidate08, are preserved. This report does not change their historical results or declare GEO-02 complete.

## Source and endpoint identity

Actually viewed source: [native guest01 plan crop](guest-stair-wall08-source-plan.png), [guest03 south elevation crop](guest-stair-wall08-source-south.png), [guest04 section crop](guest-stair-wall08-source-section.png), and the surrounding guest01 basement plan. [Crop provenance](guest-stair-wall08-source-crops.json) includes original image dimensions, raw pixel crop and SHA256. The plan comes from the 17673×13632 original TIFF; raw crop is `[4660,10526,5609,12510]`, without generative alteration.

The printed **2′5″ = 0.7366 m** has extension lines to the laundry east wall's outside face and the opposite solid wall's inside face. Neither the 0.83 m tread extent nor the inferred metal rail is the right endpoint. The distinct 7′6⅛″ longitudinal dimension is not used as a substitute for this width. The original07 lacks that solid opposite wall: retain its NULL/NOT_RUN status.

The plan proves the wall identity and rounded free end. Its basement inset is mapped to existing wall/door/stair controls, not misread as the guest plan's world-coordinate pixel array. The mapped south tip follows the existing descent start (source Y402); the northern inside return follows the existing door opening's north edge (source Y357.9). These mapping details, 0.20 m wall thickness and small corner radii remain **C**. The south elevation contains rounded wall-end clues, but no uniquely identified height dimension was found. The guest04 U-shaped section is not confidently this wall and was not borrowed as its height.

**Height/finish remain C:** top L1+0.80 = 9.20 m; buried base B1−0.24 = 5.80 m; ochre concrete material. No claim is made that these are archival measured heights or an identified original finish.

## Finished-face measurement, including the failed candidate

| Measurement | Candidate08 | Candidate08b |
|---|---:|---:|
| Core east face to new inner face | 736.600 mm | 755.100 mm |
| Actual sampled first visible opposing surfaces | 703.544–736.600 mm (103 pairs) | **720.369–755.100 mm (2,621 pairs)** |
| Maximum absolute difference from 736.6 mm | 33.056 mm | **18.500 mm** |
| Original max(20 mm, 0.5% L) tolerance | FAIL | PASS for sampled finished faces |

The early candidate08 core-only report is superseded for dimension acceptance by its independent `guest-stair-wall08-reopen.json` **REQUIRES_REVIEW / FAIL_FINISH_RANGE**. The failed blend and raw report remain intact. Its initial core-only geometry PASS must not be reused as finished-face evidence.

Candidate08b moves only the new wall's straight inner face 18.5 mm east, to X≈2.162699938 m. The existing rough stone is unchanged. The 18.5 mm offset represents the midpoint of its implemented 0–37 mm projection envelope; this nominal finish plane is explicitly **C**, not a new archival measurement. The hidden core is not relabeled as the finish face. Actual stone protrusions and exposed mortar/core patches are included in the range above.

The independent reopen check uses Blender's actual `scene.ray_cast`, in 20 mm Y and height increments over the stair-supported portion below the existing east wall top. Of 3,731 retained records, 2,621 identify both actual opposing finished surfaces. Other first-hit identities, unsupported stations and exclusions are recorded rather than silently counted as PASS. The range is a dense sample result, not a mathematical claim about every possible continuous surface point.

Reproducible extrema from [08b reopen data](guest-stair-wall08b-reopen.json):

| Case | Ray origin X,Y,Z / m | Left actual hit X / m | Right actual hit X / m | Width / m |
|---|---|---:|---:|---:|
| Minimum sampled | 1.775900006, 39.669998169, 8.177143097 | 1.442331314 (`GUEST_LAYERED_SANDSTONE_COURSES`, face 41469) | 2.162699938 (new wall, face 11) | 0.720368624 |
| Maximum sampled | 1.775900006, 38.330001831, 8.182856560 | 1.407600045 (`GUEST_B1_BASE_EAST_pier_end`, exposed face 52) | 2.162699938 | 0.755099893 |
| Fixed comparison station | 1.775900006, 38.787040710, 8.050000191 | 1.415150404 (stone face 42417) | 2.162699938 | 0.747549534 |

All pairs use directions −X/+X and opposing face normals. The minimum station is 1.80 m above actual tread11 at Z6.377142906. No nominal JSON dimensions, object names alone or global stone-mesh bounding box replace the actual intersections.

For the central audit, the recommended new category is **connection / stair-well clear width**, with the first visible exterior laundry face and this straight inner face as selectors. Keep target 0.7366 m and tolerance 0.020 m; attach this actual range and the C finish-plane interpretation. Do not use the new wall's custom-property value as a measurement. Central eligibility remains the integrator's decision; this subtask does not modify `dimension_audit.py`, dimension rows or old07 NOT_RUN.

## Bounded change and actual regression

Production changes are confined to `guest_house.py`: a reusable local wall helper, its build call, and omission of the four previous inferred east-side rail/baluster parts occupying the new wall. The other inner rail, all 14 original descent treads, the laundry door, service stair, architecture, furnishings and cameras are unchanged. Before/after data-block and world-matrix signatures confirm no unrelated objects changed. The module diff against the saved before file was reviewed.

- Fresh full guest-module build: **PASS**, 20 room records / 859 objects; the wall matches saved-candidate bounds; 14 treads and four inner-rail parts remain, four outer parts are absent.
- Independent reopened wall mesh: closed manifold, no edges with incorrect face incidence.
- Fourteen real tread positions × three body columns: **42 PASS**, 0.48 m width and 1.95 m head clearance, including actual support checks.
- Original `L1_STAIR_HALL ↔ B1_STAIR` and `B1_STAIR ↔ B1_LAUNDRY` paths: **both PASS**, before and after.
- Original laundry doorway: **18 PASS** across 0.48 m width and six actual cross-wall heights through 1.94 m; door opening retained.
- All **7,584** saved07 integer camera positions were considered for the changed-volume envelope. **96 potentially affected frames** were actually set/evaluated against before/after body, ground, camera and incoming sweep geometry; **0 new failures**. The other 7,488 frame envelopes cannot meet this local volume and retain their frozen07 full-scene evidence. This is not a claim that full iteration08 navigation was already rerun.

Raw evidence: [08b geometry/route checks](guest-stair-wall08b-check.json), [independent reopen/visible-face checks](guest-stair-wall08b-reopen.json), [fresh module smoke](guest-stair-wall08b-module-smoke.json). Each has its reproducible Python probe and captured log beside it. All Blender jobs used 5.2.1 LTS, CPU `-t 4` and `--python-exit-code 1`; none rendered, baked or changed an open user scene.

## Two additional diagnostic camera overrides

The frozen `CAM_GUEST_B1_STAIR_A/B` really view the laundry descent: their center rays hit `GUEST_LAUNDRY_DESCENT_tread_06` and `tread_05`. They are not views of `GUEST_SERVICE_ASCENT`. Both fail to frame the new rounded tip adequately, so the following JSON is expressly **additional diagnostic coverage**, not a replacement for room120 or a visual PASS:

`qa/guest-stair-wall08b-diagnostic-camera-settings.json`, for use with `render_views.py --camera-settings` on candidate08b and exact cameras `CAM_GUEST_B1_STAIR_A,CAM_GUEST_B1_STAIR_B`.

| Temporary camera slot | Location / m | Target / m | Lens | Purpose | Proposed exposure |
|---|---|---|---:|---|---:|
| A | 1.86,37.40,10.25 | 1.84,39.35,7.65 | 24 mm | South upper view of rounded tip, straight wall and north return | 1.6 |
| B | 1.92,40.23,7.64 | 1.40,39.75,7.50 | 18 mm | Lower treads and unobstructed real laundry doorway | 3.0 |

Actual camera clearance tests pass. Thirty framed witness points were independently confirmed with scene rays: A has 26 including 16 rounded-tip top facets; B has the real doorway sightline and three treads. [Final witness report](guest-stair-wall08b-camera-final.json) preserves coordinates/projections/hits. Exposure is proposed and unreviewed. No temporary camera or override was saved into candidate08b or the original room cameras. Root owns rendering and visual judgement.

## Frozen artifacts and handoff

| File | SHA256 |
|---|---|
| `scene/Fallingwater_iteration07.blend` (unchanged) | `bf50530009e4a93315915815473188c91d891272ef2d8e9e0169b704bd2e2f16` |
| `scene/Fallingwater_tour_checked_iteration07.blend` (unchanged source) | `792882445860ae6a7bb37e3e03838d74a07647e89dbf5475a056125d6bac067e` |
| `scene/guest_stair_wall_candidate08.blend` (failed finished clearance; preserved) | `9c7625596c08ac2a4a6cb71817aafb2981d9e5b6ab65e9e8c62b9c0ace5c32c1` |
| `scene/guest_stair_wall_candidate08b.blend` (current candidate) | `7213acc3f1c44d7de0829fb6ecc17ef6cfab47b2b2edecf8f4b30f8fa0c20a20` |
| `scripts/guest_house.py` at smoke test | `17f42fda4280050f72d10ed7fc1b5c2b9a6891e156e54e86b2ccc103e053a54f` |

Scoped neat-freak reconciliation: this report consolidates current acceptance and superseded evidence; before/failed files are retained for the project QA requirement. `STATUS.md`, `START_HERE.md`, central dimension files and `AGENTS.md` remain owned by the integrator and were not edited. Parent receives the exact new status, limitations and links for integration. No global settings or unrelated modules changed.
