# Master / Master Bath navigation10 handoff

Current result: **three complete walking connections and the north wardrobe's
inspection connection pass their explicit local tests; 360 local integer frames
pass both initial validation and a saved-file reopen**. This is not the full
60-edge / 7,584-frame combined acceptance, photographic acceptance or final film.
The immutable machine-readable entry point is
[master-navigation10-final-freeze.json](D:/zx/test/project/qa/master-navigation10-final-freeze.json).

## Frozen inputs and output

- Physical combined input: `scene/Fallingwater_integration_candidate10a.blend`,
  SHA256 `dc7594d60b68effaf10b85dd1804827fc9cb16dd786656daa4da16c761b33518`.
- Local camera/key candidate: `scene/Fallingwater_master_navigation_candidate10a.blend`,
  **46,393,381 bytes**, SHA256
  `86b9605cdb73c76c4dd6d0e899798235c26053d6f7ccbb7edc502a511fd34ad9`.
- Adapter: `scripts/master_navigation10.py`, SHA256
  `dafbd4ded6c14112e8d07292ada5bb880eb65433b81e507a87afeb4661eb6e9a`.
- Earlier single-object physical10g: SHA256
  `34dbbb2b6639718a11d876f9ef44d2de251513a701c4c04ba4611a763bda7631`;
  `master_detail10.py` SHA256
  `243a642da59bbf28030b65a916b5e031467785eea3664818e88b33982c1ef837`.
  The combined input already contains it. **Do not apply physical helpers again.**

The candidate changes only the four review cameras below and adds
`QA_MASTER10_TOUR` / `QA_MASTER10_SUPPLEMENTAL` for bounded verification. Every
other existing object fingerprint is unchanged, including geometry, materials,
lights and existing tour cameras. Scene frame/range/active camera/render settings
remain unchanged. Reopen fingerprints match; protected source files and original
scene bytes match. No rendering occurred in this task.

## Composition

```python
tour, candidate_rooms, guest_spec = guest_circulation10_routes.prepare(
    isolated_workspace, scene, embedded_rooms)
master_spec = master_navigation10.apply(
    tour, scene, candidate_rooms, isolated_workspace)
master_navigation10.apply_cameras(scene)  # Explicit four-camera operation.
tour.install(scene, candidate_rooms)      # Root runs complete graph/frame QA.
```

`apply()` mutates the supplied candidate room list and returns the specification.
It does not reload tour, replace Guest's Probe or overwrite Guest's dispatch.
Guest Probe/stair/anchor/connector function identities were retained; prior Guest
hinted_connection and room_candidates are captured for unrelated IDs. Local QA
used Guest `prepare(..., read_only=True)` on isolated copied data. Adapter writes
only inside the supplied workspace. It never saves a scene or writes production
camera settings. Runtime output is `workspace/data/master_navigation10.json`.

Master and Bath candidate navigation datum is the actual stone finish **Z2.8668**,
with eye **Z4.4668**, not the old structural datum Z2.8448. The room's previous
datum remains recorded. Closet M stays a semantic storage inspection, observed
from Master toward the actual new north wardrobe; it is not a walk-in room.

## Local route evidence

| Connection | Result and scope |
|---|---|
| Hall → Master | Complete true north door, crosses corrected ceiling break, reaches common Master anchor; PASS |
| Master → Bath M | Same common anchor, true southeast entry, reaches Bath interior anchor; PASS |
| Master → Terrace S | East approach around actual open leaf, explicit two-foot step over track, reaches terrace; PASS |
| Master → Closet M | Five visible rays onto the broad front of actual north wardrobe door plus clear short camera sweep; PASS_INSPECTION_ONLY_STORAGE |

The common Master foot anchor is **(1.6768, 8.4429, 2.8668)**, source (359,381).
Master's film path crosses the previous ceiling obstruction to source (359,338).
Additional tested paths attach the storage observer and both rooms' A/B positions
to the common room anchors. Independent disconnected points were not used to
claim room connectivity.

Flat routes use dependency-graph evaluated triangles, 4 mm floor agreement at
nine support points, body radius 0.18 m, clear height 1.95 m, ≤1 cm samples,
body columns, radial rays and continuous segment rays. These are sampled geometry
tests, not a formal solid collision solver. Global legacy thresholds are unchanged.

### Raised terrace track

Flat walking remains **FAIL**: the real modeled sill spans Y6.81990..6.87990,
top Z2.91900, **52.2 mm above adjacent finish**. Its 60 mm depth cannot support an
entire 240 mm foot. The first diagonal approach also hit the open leaf; both
negative results remain in `master-navigation10-diagnostic.json` and the combined
probe's per-piece results. The successful approach goes around the leaf's east
side at X2.62; the clear opening is X2.2198..3.002733 (0.782933 m).

The explicit alternative alternates two actual support feet on opposite side
floors. It checks **122 poses / 1,890 support samples**, 4 mm agreement, swing-foot
volume and continuous sweeps, leg rays and a 0.18 m / 1.95 m upper body envelope.
The narrow track is stepped over, never treated as a foot-sized platform. C gait
assumptions: foot 0.10×0.24×0.055 m, centers 0.18 m apart, stride 0.52 m, peak swing
lift 0.12 m and 52.2 mm body-datum rise/fall. Minimum swing sole clearance above the
sill is **25.0718 mm**. See
[full support/pose evidence](D:/zx/test/project/qa/master-navigation10-sill-step-final.json).
This is a bounded navigation construction, not biomechanical certification or a
rendered human animation. The adapter keeps flat FAIL separate from step PASS.

Actually opened Columbia Master face2 and main05 plan crop: full-height operable
south terrace doors and a threshold are visible. The exact single active modeled
panel and inward 78° leaf pose remain C; the source photograph shows an outward
open leaf. The geometry was not changed to make this route pass.

## Cameras and local saved frames

| Camera | Eye XYZ | Target XYZ | Lens |
|---|---|---|---|
| CAM_MAIN_L2_MASTER_A | 1.6768, 8.4429, 4.4668 | 3.4584, 10.9917, 3.8868 | 24 mm |
| CAM_MAIN_L2_MASTER_B | 2.7772, 8.2305, 4.4668 | -0.1048, 10.4076, 3.8868 | 24 mm |
| CAM_MAIN_L2_BATH_M_A | 6.45, 7.75, 4.4668 | 6.10, 9.50, 3.8168 | 24 mm |
| CAM_MAIN_L2_BATH_M_B | 5.60, 9.00, 4.4668 | 6.50, 7.15, 3.6668 | 24 mm |

All four saved poses pass strict clearance after reopening; no pose was reapplied
before checking. Old actual camera failures are preserved in the freeze, both at
their original height and at the corrected finish height. Local animation is
168 frames Master + 96 Bath + 96 wardrobe inspection. All **360 initial and 360
reopened frames** pass FCurve values, actual evaluated world pose and previous-frame
sweeps. Saved keyframes were not rebuilt for reopen. The two QA cameras are not
the complete tour. Root must run new combined 60-edge / 7,584-frame checks.

Root's integration10a Master A/B EV2.4 renders were actually opened here. Furniture
and fireplace remain legible but dark; the stone front is too regular, bed-cover
color differs from the source and the narrow independent beam form is not proven.
The two Master proposals record Root's EV2.4 preference only as metadata; the
adapter does not change scene exposure. The Bath views still require Root's actual
render review. No source identity or material/photographic status is upgraded by
navigation PASS.

## Preserved history and cleanup

The older 10f ceiling has 18 real **1.9232 m FAIL** rays. Root authorized only the
C bottom correction to 4.8468 while preserving top 5.005 and XY. Its 18 reopened
1.98 m results and single-object/source-reproduction checks are in
`master-navigation10-physical10g-freeze.json`. Earlier 119-point Master route PASS
used a lower body screen and does not override the later 1.95 m finding.

This handoff is the current bounded integration guide. Prior physical10f documents
remain historical checkpoints, not instructions to revert the helper. The
neat-freak reconciliation is limited to this owned QA/module interface: global
AGENTS/STATUS, production data, unrelated reports and other workers' modules were
not edited. Source photo files remain REFERENCE_ONLY_EXCLUDE_PUBLIC_PACKAGE.
