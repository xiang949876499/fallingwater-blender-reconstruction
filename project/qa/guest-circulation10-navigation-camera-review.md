# Candidate circulation10 camera scope

The four render diagnostics in `guest-circulation10-render-cameras.json` were
tested against frozen 10f, SHA256
`7286427d1f47ae9219204ed5dd54a970387683c8b384d1b4259244a7b991d852`.
They reuse exact existing camera names but were not assigned to or saved in the
scene. Lens and exposure are proposed; rays are not visual acceptance.

Root subsequently inspected the four renders: the first southeast-entry view
was too close and omitted the complete door head. That diagnostic pose is
superseded by `guest-circulation10-navigation-entry-camera-retreat.json` at
source (466,465), with normal 1.6 m eye height and 17 mm lens. Actual body/ground
tests pass, and the entire jamb/head mesh projects within normalized frame
X0.362–0.653, Y0.051–0.938. Root then rendered and inspected the retreated
view: the full header and jambs are visible, so it is accepted locally as an
entrance inspection image. The room remains dark and the view does not show
the full Lounge. This is not room-image or overall visual acceptance; see
`guest-circulation10-root-visual.md` for root's actual image review.

All four diagnostics pass the evaluated-mesh eye radius and local 1.95 m
headroom / 0.18 m body / 4 mm ground screen. The upper diagnostic looks toward
the actual rounded end of the new solid divider; its first sightline hit is that
divider, not an unnoticed intervening wall. The other three target lines are
clear. The camera check JSON retains actual hit coordinates and body results.

## Existing census cameras affected by the changed surfaces

| Saved camera | Actual 10f observation | Candidate action |
|---|---|---|
| GUEST_L1_STAIR_HALL A | Saved eye is world Z12.352870, above the right upper flight now at Z10.028776; it does not represent the northern L1 platform. | Relocate to the physical northern L1 platform. |
| GUEST_L1_STAIR_HALL B | Former south flat-floor eye is over terrain at Z6.962803, beyond the low platform's actual south end. | Relocate north onto the low arrival at Z7.22. |
| GUEST_L1_TERRACE B | The western paving beneath the saved eye is now the actual intermediate plane Z7.725715. | Use that plane, away from its southern edge. |
| GUEST_B1_STAIR A | Saved support/eye belongs to L1, beside the new upper-left first step. This is an existing census-level mismatch, not newly missing basement ground. | Place the B1 inspection at the actual B1 north platform. |
| GUEST_L2_HALL A | Existing eye is clear. New source divider/return needs a separate useful view. | Proposed grounded upper-return replacement; existing north Hall B remains available. |

The additional proposed replacements and their actual geometric test are
recorded separately in `guest-circulation10-navigation-camera-overrides.json`
and `guest-circulation10-navigation-camera-overrides-check.json`. These are
candidate overlays, not modifications to the reviewed production 120-camera
settings. A failed proposed pose must not appear in the usable overlay.

All 15 affected saved-camera eyes examined have no 0.13 m eye-ray collision.
Some old CarCourt/L2 Hall body-radius findings concern unchanged stone faces;
they are not reclassified as regressions caused by circulation10. The existing
CAM_CONNECTOR is an exterior free camera: absence of ground under it is not a
camera collision failure. Its new grounded diagnostic is an alternative view.

This bounded inspection is not a new all-120-camera acceptance, and a diagnostic
view does not replace the full room camera render review.
