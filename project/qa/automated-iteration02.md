# Iteration02 independent structural verification

Scene: `scene/Fallingwater_working.blend`, saved2026-09-20 13:39:18, 14,976 objects. Read its own embedded `FW_ROOMS.json`. No render or GPU workload was used.

## Whole-scene sampled validator

**43 PASS, 17 INCOMPLETE, 0 FAIL** across60 records. Overall status remains INCOMPLETE because stepped routes, foundations, pools and unresolved loggia cover extents need dedicated verification. A PASS here is a sampled structural assertion, not final room acceptance.

The old guest boiler ceiling failure is resolved. The old terrace failure was correctly resolved by excluding the pool area from the flat-terrace census, rather than covering the water.

## Independent recheck of corrected P1 geometry

| Route | Actual tread/lateral samples | Minimum measured headroom | Result |
|---|---:|---:|---|
| Main L2→L3 stair | 42 | 2.0584m | PASS |
| Main pool→east terrace stair | 45 | 2.6648m | PASS |
| Main living-room water stair | 51 | 2.4975m | PASS |
| Guest service ascent | 42 | 2.1200m | PASS |

These180 positions use tread centers and±0.22m lateral offsets. Ground must be present within0.03m of the actual tread top; vertical clearance must be at least1.95m. At every tread center, five body heights and eight horizontal directions were checked to radius0.22m. No obstacle was found. The complete integrated mesh, including furniture and terrain, participated in the rays.

- Nine actual opened terrace-door bays: crossing rays at four heights through1.94m above sill found no blocking transverse frame or glass. The nominal minimum bay width is0.6523m; this is an observed architectural width, not an accessibility certification.
- Main water-hatch top exit: the former blocked plane is clear at four heights.
- Twenty-three main-house thresholds: all focused ground and centerline penetration checks pass. This supplements the author report, whose23 checks also passed; neither is a complete swept-body proof.
- Main plunge pool: first downward hit is its water surface at Z-2.7000.
- Guest pool preservation: the former erroneous terrace sample still hits actual water at Z8.96485.
- Kitchen material is the saved red rubber grid with0.2286m tile scale; actual cork finishes/guest linings are present. Photographic material comparison remains pending.

## Closure

The six specific original geometry P1 findings in `integration-review.md` may be closed for this exact integrated scene. The material implementation mismatch is corrected, but visual acceptance remains open. Full room enclosure, source overlays, all navigation connections, rendered fidelity, real-time performance and relocated-package reopening are not established by these tests.

Evidence: `automated-iteration02.json`, `.log`, `.geometry.json`, `.geometry.py`, `.geometry.log`. These remain finite diagnostic samples, not final project acceptance.
