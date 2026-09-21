# Guest north/middle bay photography proposals — actual11b read-only

These are two new normal standing viewpoints, not inherited PASS labels from
the old Theater A/B. No camera object was created, no settings were applied,
no rendering occurred and no scene was saved. Both use 24 mm focal length,
36 mm sensor width, 16:9 aspect, 1.60 m eye height above the actual8.4 m floor,
zero intentional roll, and a modest downward aim. Exposure remains for the
integrator's actual preview; this report does not claim lighting acceptance.

| Suggested temporary name | Eye XYZ (m) | Aim XYZ (m) |
|---|---|---|
| CAM_QA_GUEST_BAY11_NORTH | (0.600000, 51.800000, 10.000000) | (−2.866858, 51.681335, 9.480000) |
| CAM_QA_GUEST_BAY11_MIDDLE | (0.400000, 49.900000, 10.000000) | (−2.412213, 48.720924, 9.480000) |

Both pass actual evaluated-mesh 4 mm floor support, 0.18 m body radius, 1.95 m
head height and 0.13 m near-camera clearance. Their local approaches pass dense
20 mm samples and body sweeps without moving any furniture or source geometry.
All four full-bay corners, from floor8.4 through top10.56, fit with frame margin.
The first middle candidate (0,49,10) passed standing checks but clipped the full
head; it is retained in attempt01 and is not the final recommendation.

North approach: accepted Theater route endpoint (−0.29519,50.2696,10) →
(0.055,50.2,10) → (0.055,51.65,10) → proposed eye. Its 20 target stations all
lie within the frame. Sixteen rays first reach the new bay geometry; four rays
at bay fraction0.70 pass through the **real open door**, not an occluder or lost
wall. This shows the full window/door relationship from within the room.

Middle approach: central room aisle (−0.54,49.0,10) → (0.055,49.0,10) →
(0.055,49.95,10) → proposed eye. Eighteen of
20 target stations directly reach the new middle glazing in frame. Two low
stations at Z8.75 m are naturally occluded by the unchanged seat04 seat and
seat05 upholstered back. Upper window/return relationships remain visible; these
chairs were not hidden or moved to increase the score. This is a room photograph
proposal, not an orthographic evidence view or exact archival photo match.

Detailed tests and the four north/five middle bounded candidates are preserved
in `guest-bays11-camera-proposal.json`. Suggested names are labels only; they do
not exist in the saved scene. The old A/B geometric failures remain recorded.
