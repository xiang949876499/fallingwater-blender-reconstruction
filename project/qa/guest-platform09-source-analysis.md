# Guest service stair09 — implementation hold for source levels

2026-09-21. This is a source-interpretation note, not geometry acceptance or a final stair reconstruction. No guest or tour production edits have been made after frozen08.

Actually viewed by the implementation agent: guest01 original native crop `guest-platform09-source.png`, its wider `guest-01-service.png`; guest02 `guest-02-rooms.png` and the independent reviewer's native `guest-stair-source09-guest02-service.png`; guest04 section, labelled datum crops and overview. The independent reviewer is separately checking both complete TIFF contexts and elevations.

Confirmed observations:

- Both floor plans show the right-side UP direction toward drawing north. The current right-side `GUEST_SERVICE_ASCENT` rises toward drawing south. That directional conflict must not be disguised by a platform patch or old navigation PASS.
- The actual saved08 north platform edge Y40.843120575 and old first tread edge Y40.690959930 leave a 152.160645 mm unsupported strip. A continuous paved-to-stair interface is drawn; no narrow hole is drawn. The correct repair height depends on the correct stair and platform identities.
- Guest02 has a continuous arrow line down the left run, across the southern landing and up the right run. This establishes directional continuity in the drawing but does not, by itself, establish that both runs span the same L1→L2 storey.
- Guest01's left projection has both UP-south and DOWN-north annotations and a break symbol. The basement laundry stair shares that XY projection. Its existing B1 datum −2.36 m is C and cannot prove which visible line belongs to which level.
- The right run's visible north end differs between guest01 (about source Y350) and guest02 (about source Y382). A direct copy of the second-floor visible footprint onto the first-floor run is therefore unjustified without explaining the projection/level difference.
- Guest04 clearly labels MAIN LEVEL 0′0″ and SECOND LEVEL 7′8⅝″. The particular longitudinal stair section and the southern landing's datum have not yet been identified in the inspected transverse section/elevation material.

Rejected premature actions: shifting a route directly onto the first tread to skip the support gap; adding a 152mm slab before determining its correct level; placing an assumed short L1-to-midlanding flight over the existing B1 high treads without independently checking both headroom and source layer identity; reversing or constructing a folded staircase purely to restore the old graph PASS.

Current production hashes remain `guest_house.py` = `17f42fda4280050f72d10ed7fc1b5c2b9a6891e156e54e86b2ccc103e053a54f`, `tour.py` = `105c10dfb180448384ea6c9970b9d5d167295776f7475b280b43f341cbd26901`. Root has directed the two independent source readings to agree on layer/platform identification before a09 candidate is built. The exact08 negative support/body evidence is in `tour-path-iteration08-stair-gap-probe.json` and the complete negative acceptance record is `tour-path-iteration08-review.md`.

Subsequent authorized numerical study: `guest-stair-hypothesis09.md/json` evaluates an explicit four-half-flight C hypothesis without building or installing geometry. Its conditional intrinsic envelope is feasible, but the unchanged08 south platforms/west return floor conflict, and north-cap construction plus source layer/registration remain U. This does not lift the implementation hold or reinterpret the above negative findings as PASS.
