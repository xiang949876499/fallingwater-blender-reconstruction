# Main-house geometry evidence — iteration05 source

The current main-house module builds in Blender 5.2.1 LTS: 40 inspection spaces, 3,599 objects and 22,160 raw mesh faces. All 40 space polygons are valid and contain their representative centers. These are execution and geometry checks, not photographic or complete navigation acceptance.

## Registration and interfaces

The authoritative main04 frame is 1024 × 789: X=(px−327)×0.0524 m, Y=(540−py)×0.0531 m. +Y is drawing-up, not surveyed geographic north. Main terrace datum is 0; L1 interior floor +0.10 m is inferred, L2 terrace +2.8448 m, L3 terrace +5.26415 m. The four section slab/roof labels and the identified north-spine dimension have independent mesh comparisons; other traced construction remains C evidence.

Current files: `../scripts/main_house.py`, `../data/main_house.json`, `main-geometry-smoke.blend/json`, `main-geometry-polygons.json`. The data contains 40 inspection spaces, 40 adjacency records and 24 threshold records. Counts include foundation, pool and stair inspection spaces; they are not counts of living rooms.

The main-to-guest handoff is **(5.4496, 23.4702, 5.26415)**, source (431,98). `MAIN_L3_LINK` now describes the real north upper walk and spiral landing, not the southward canopy roof projection. Guest-module ownership begins at this handoff; the next accepted guest path point is (2.62,23.58,5.83). Cross-building height remains C.

## Current repaired geometry

- Pool deck uses perimeter strips and independent basin sides. Its opening first hits water at −2.70 m. The east-terrace pool stair has an actual slab opening and top landing. The water-hatch leaf lies open along its northern hinge edge.
- Internal stair openings and floor thresholds are explicit. The L2→L3 stair moved south by 0.568 m to clear the north bath, a C registration adjustment. Sleeping-alcove north masonry remains closed; no direct Gallery→Link door is claimed.
- Living-room floor is continuous beneath the dining table, which was previously misread as a floor notch. Ceiling keeps the actual stair opening, and window heads meet concrete head bands. The original pixel-ray failures and repaired four rays are preserved in `main-geometry-living-ray.json` and `main-geometry-living-fixes.json`.
- Kitchen door follows original main04 x324/y270–287; the former y294–315 opening is closed. The south window bay reaches the floor and follows the traced three-segment outline. Servant-room north rock-edge bay and the separate descending service stair are restored. Material treatment uses 9-inch Cherokee-red kitchen rubber and bathroom cork. See `main-dimension-resolution.md` for original-image evidence and limits.
- Original main04 extension lines establish the 11 ft north-spine span. The east return and corresponding Living inner corners moved 53.2 mm; measured outer-face separation is now 3.3527998999 m. The L1 east exterior band is −0.49…+1.08 m, read from main09 relative to two floor datums; its 55 mm graphical uncertainty does not create a new GEO-02 dimension anchor.

## Iteration05 topology corrections

Wine access is through its **internal north stair leg**. The west edge is retaining rock, so the false west opening is closed rather than given an invented outdoor floor. The north floor connection and `stair_wine` hint cross source (264,239)→(264,250). Guest Bath G opens east into **Hall**, not directly into the Guest Bedroom; only the adjacency and attribution changed there.

The actually viewed `renders/previews/camera04-review/CAM_MAIN_B_BATH_B.png` exposed two black floor strips at Wine↔Bath. Six matching camera-ray samples hit sound floor, while the strips coincide with overlapping coplanar room/threshold finishes. The threshold finish now joins the true source floor edges x285 and291 without overlap; the same shared partition footprint y244..283 receives continuous substrate. The actual door remains y255..275 and walls are unchanged. A separate 8,829-point downward grid around the opening/jambs found 135 thin gaps before this repair and zero afterward (`main-geometry-bath-seams-before.json`, `-after.json`). Removal of black rendering artifacts still requires the integrator's same-camera image; ray support alone does not establish that visual result.

The external curve now climbs **south to north**, matching the visible UP/DOWN relationships in main05/06. The old northern low-step approach was unsupported. Sixteen approximate treads lead from L2 terrace to the north upper walk; the stepped canopy above is separately tagged non-walkable. The full old southward L3 floor has been removed. Actual step centers and the corrected handoff are in `main-geometry-iteration05-check.json`.

Source review used saved main03/05/06 JPEGs, enlarged with a coordinate grid in `main-geometry-iteration05-source-03.png`, `-05.png`, `-06.png`; all were actually opened. These are not original-resolution TIFFs. Main04 and main10 original TIFFs were inspected separately. Stair count, source trace and canopy clearances remain C.

## Verification and remaining gates

`main-geometry-iteration05-check.json` records 352 bounded architecture-only samples: 39 Wine north-passage, 39 Hall↔Bath G, 48 tread samples, 225 lower/upper/handoff approach samples and one closed-west-wall check. All pass at sampled width 0.36 m and head height 1.95 m. The report includes source/module/scene hashes. This is sampled support and vertical clearance, not continuous swept-body acceptance with site and furniture.

`main-dimensions-measured.json` measures actual evaluated mesh vertices using **GEO-02=max(20 mm,0.5% of reference)**: 5 numeric PASS, 16 NOT_RUN. Source-reading uncertainty is a separate field and cannot relax this standard. Six un-arrowed nominal room annotations remain diagnostic bounding spans; ten chain/overall labels lack established physical endpoint correspondences. All-dimensions acceptance remains incomplete.

Historical tests retain the scene scope on which they ran. In particular, the old arc landing assertions in `main-geometry-living-fixes.json` are superseded by iteration05's corrected stair direction and north walk; they must not be used to restore the removed false canopy floor. The integrated iteration04 checkpoint is preserved unchanged. Full iteration05 furniture/site/guest traversal and updated lit imagery remain the integrator's responsibility; no final visual or navigation acceptance is claimed here.
