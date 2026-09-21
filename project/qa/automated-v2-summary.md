# Structural validator v2 — old integrated scene

Executed in Blender 5.2.1 LTS, without rendering or GPU work, against `scene/Fallingwater_working.blend` saved at 2026-09-20 13:11:48. The room manifest was read from that blend's embedded `FW_ROOMS.json`, so current source edits did not silently redefine the older scene.

## Result

Overall **FAIL**: 60 room records comprise **41 PASS for applicable sampled checks, 17 INCOMPLETE, 2 FAIL**. The previous validator reported 30 failed records. These numbers are not whole-project acceptance: independent enclosure, door/stair routes, visual fidelity, GUI navigation, performance and package relocation remain unrun by this validator.

| Retained failure | Actual mesh evidence | Action |
|---|---|---|
| `GUEST_L1_BOILER` | All five interior probes hit the floor at Z8.4 but no overhead structural surface near the recorded 2.16m clear height. Example XY `(4.87168,41.59752)`. | Verify the boiler roof footprint north of the low guest arm; add the source-supported roof/ceiling if absent. |
| `GUEST_L1_TERRACE` | One of four interior probes, XY `(24.69994,35.67970)`, has no flat floor at Z8.4. This is source pixel approximately `(730.25,443.25)`. | Reconcile terrace room polygon with pool/coping/stair boundaries. The record may include water/raised coping; filling a new slab there could incorrectly cover the pool. |

Both were sent to the guest module author. Main-house ordinary flat-room surface probes passed this limited check. Main/guest stairs, pools and foundations remain INCOMPLETE, including previously identified real clearance defects; changing the checker did not close those defects.

## Corrected checker behavior

- Guest wall-builder piers/sills/lintels are recognized from their architectural role and emitted segment names. A missing literal `wall` substring no longer produces a false missing-wall result.
- Furniture component metadata takes precedence over words embedded in room/object names, preventing furniture from becoming structural wall/floor/window evidence.
- Shared floors, landings, terraces and walls can support multiple room records through evaluated mesh ray hits. The absence of a dedicated room ownership tag is not a failure. Conversely, metadata or a bounding-box overlap does not constitute a pass.
- Surface hits must have an approximately horizontal actual normal; wall association requires an actual approximately vertical surface hit within the room boundary envelope at occupied height.
- Uniform-Z probe diagnostics are retained for stairs, pools, foundations and halls containing stairs, but their pass/fail assertion is `NOT_RUN`. Those room results are explicitly `INCOMPLETE` until dedicated tests resolve the appropriate treads, landings, coping/water/basin or exposed structure.
- Loggia cover extent remains a reference-dependent limitation, rather than assuming either a fully enclosed ceiling or complete open sky.
- Car courts are recognized as exterior; special emitted floor names such as upper terrace and stair landing are treated as horizontal structure.

## Actual regression validation

`automated-v2-regression.py` builds a tiny real Blender mesh scene without rendering. All five checks passed:

1. Guest architectural pier naming identifies a wall.
2. First room with no owned meshes receives actual evidence from a shared slab/ceiling/wall.
3. Adjacent second room independently receives actual evidence from the same shared geometry.
4. A room with genuinely absent structural floor still fails.
5. A stepped route remains INCOMPLETE with uniform floor test NOT_RUN rather than passing silently.

Outputs: `automated-v2-old.json`, `automated-v2-old.log`, `automated-v2-regression.json`, `automated-v2-regression.log`.

## Remaining scope

The code-level P1 findings in `integration-review.md` are separate evidence and are not superseded by this checker. Rebuild the architecture fixes, rerun this validator against the new embedded manifest, and run the dedicated route/head-clearance checks before closing those findings. PASS labels in this report refer only to applicable sampled structural assertions, not complete enclosure or navigation acceptance.
