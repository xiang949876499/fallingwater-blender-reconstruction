# Bathroom fixture identification and bounded-curve correction

**Confirmed geometry bug:** the apparent large metal guard around the basement basin is the separate **towel rail**, enlarged by Bezier AUTO overshoot. It is not the shower pipe or a reflected duplicate of the faucet.

Images actually opened: `renders/previews/iteration06-focus/CAM_MAIN_B_BATH_A.png` and `qa/animation-renderer06-smoke/frame_000002.png`. The latter's render log identifies camera `CAM_MAIN_B_BATH_B` in `scene/Fallingwater_preview_iteration06.blend`. The preview's 27 relevant curve signatures match the unchanged iteration06 geometry exactly.

## Identification from actual geometry

The responsible object is `FW_FURN_MAIN_B_BATH_towel_rail_02_rail`. Its evaluated mesh projects to pixels X735.9–899.9 / Y101.6–274.8 in the 960×540 A image, and X41.2–154.6 / Y34.2–87.9 in the 384×216 B image. In each camera, 63 sampled centerline rays hit this object directly before any mirror. The small arch at the taps is the distinct `FW_FURN_MAIN_B_BATH_washbasin_00_basin_spout`; both cameras also directly identify it. The toilet inlet is hidden in A and outside the useful B frame. Ceiling-lamp guards project above both frames and are unrelated to the basin ring.

The basement room contains no bath-tub/shower assembly. The shower-riser check below concerns the other modeled bathrooms and the same long-span/short-return AUTO-handle failure.

## Quantified before and after

| Component | Before correction | After correction |
|---|---|---|
| Towel rail | Authored depth 90 mm; centerline depth 181.101 mm, a 91.101 mm overrun. Evaluated mesh depth 193.101 mm including 12 mm tube radius. | Centerline depth 90.000 mm; mesh depth 102.000 mm. Width returns from 486.084 mm to 464.000 mm including tube radius. |
| Basin spout | Centerline top rises 20.734 mm above the highest authored point. | Excess below 0.001 mm numerical tolerance; original endpoint heights and 13 mm radius retained. |
| Shower riser | Unequal connected spans produce 101.988 mm of unintended lateral bow. | All handles remain inside the authored envelope; unchanged tube endpoints and radius. |
| Toilet inlet | AUTO produces 17.177 mm lateral and 9.815 mm downward overrun. | Excess below 0.001 mm numerical tolerance; original plumbing endpoints retained. |

`bath-fixtures-iteration06-probe.json` records every cubic segment's two endpoints and two control handles, their convex-hull vertices/bounds, 201 sampled centerline positions summarized as bounds, and the actual evaluated tube-mesh bounds. Centerline excess is measured separately from physical bevel radius. There is no claim that an ordinary tube's radius should fit inside its centerline bounding box.

## Scoped implementation and verification

`Asset.tube()` now applies tangent-continuous circular fillets only to bathroom basin spouts, toilet inlets, towel rails and tub spouts/risers. Corners are trimmed locally; the longer spans remain straight. Other curves, including kettle and practical-light guards/filaments, retain their construction.

Actual candidate verification changes 27 fitting curves. Every endpoint, radius and world transform stays unchanged. All new cubic control handles remain within the original authored coordinate bounds, and the minimum normalized tangent dot at joins is 0.99999988. All non-target object identities, data-block identities and transforms remain identical. The basement bath's existing inspection path and both camera body clearances pass before and after. The sink, toilet, towel, mirror, lights, architecture and hearth geometry are not modified.

Candidate: `scene/Fallingwater_bath_fixtures_candidate07.blend`, SHA256 `d76f2ea35ed25feb30a11c65ada9cf122b6cfe99425c25021401bba765643149`. This is an isolated iteration06-derived fitting candidate, not the fully integrated iteration07 scene. Reproducible scripts are `bath-fixtures-iteration06-probe.py` and `bath-fixtures-iteration07-fix-check.py`; after-state evidence is `bath-fixtures-iteration07-probe-after.json` and `bath-fixtures-iteration07-fix-check.json`.

## Retained appearance uncertainty

The basic sanitaryware remains a C-level modeled approximation. Local `research/interiors.md` documents bathroom/cork context but does not establish exact basement fixture profiles or towel-rail placement. In the current arrangement, the towel-rail centerline is 80 mm above the nominal basin rim; this unverified placement can still read as a guard bar after removing the overrun. No historical claim is made for that position, and it has not been silently moved or replaced by a modern fixture.

**Visual acceptance is NOT_RUN** for the corrected candidate. No image was rendered in this task. The integrator should compare the same cameras before treating the curve repair as an appearance pass. Coarse porcelain profiles and C-level fixture placement remain separate appearance issues.
