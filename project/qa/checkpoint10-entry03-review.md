# Iteration10 entry reproduction — independent02 failure and scoped03 repair

The original corrected rebuild02 reproduces the frozen scene's static geometry and four repaired Quaternion review cameras, but **does not exactly reproduce its saved animation**. The scoped03 repair restores the one drifting service-stair film move from a production data input. It passes the unchanged camera-evidence function on that segment and exactly restores every source camera key, including handles.

Fresh saved all-object/camera readback: **PASS_EXACT_GEOMETRY_CAMERAS_AND_ANIMATION**. All1,281 keys and98 actual affected/boundary matrices match exactly. This report does not establish photographic, GUI, source-height, or final-movie acceptance.

## Inputs and unchanged failures

| Artifact | SHA256 |
|---|---|
| `scene/Fallingwater_iteration10.blend` | `1e7b17d9c2396513f005724e50788bf834097eedb401b91a7f1030825e2c4ed9` |
| `scene/Fallingwater_iteration10_rebuilt02.blend` | `c2a7ebb018c2a1d3773298b736b6519cdd5b8a996e7f1966321ded8798959629` |
| `scripts/build_iteration10.py`, scoped repair entry | `7c6976c83ae16b48970a45b7cd1351ee3389b847128ac07420df87a5910923e3` |
| `data/iteration10-room-shots-frozen.json` | `78488808499b39edf6046928c4967ec09c8d139c78ffec8510000e93346808ad` |
| `qa/checkpoint10-entry03-scoped-workspace/scene/Fallingwater_iteration10_rebuilt02_frozen_shot.blend` | `4fad11d6a5f2ba66a16ef44338ab656547cbd0fec7dc5c59c32afe2847f7b2b0` |

The root build02 log records 60 graph edges and 7,584 integer frames passing. Its actual report is `qa/iteration10-rebuild-20260920-201526/rebuild-result.json`. This audit did not repeat that complete navigation run. A navigation pass does not prove animation equality with a previous scene.

The earlier first rebuild failure, the new02 animation failure, and the first scoped-repair guard failure are retained. New evidence does not overwrite `checkpoint10-entry-comparison.json` or `terrain10-rebuild-semantic-check.json`.

## What02 reproduced exactly

Independent new-process evidence: `qa/checkpoint10-entry02-independent.py/.json/.log`, with complete saved state snapshots `checkpoint10-entry02-independent-state-0.json` and `-state-1.json`.

- Both scenes contain 23,437 objects: 22,996 meshes, 153 curves, 142 empties, 131 cameras and 15 lights.
- 23,436 indexed object hashes are identical. The only indexed difference is `SITE_Continuous_BearRun_Terrain`.
- The terrain's **128,601 vertices, 383,980 edges and 255,380 oriented faces** are exactly the same multisets in world float32 coordinates. This was checked by direct equality of sorted binary sequences, preserving duplicate multiplicities, not only by matching hashes. Face orientation is preserved: cyclic start rotations are allowed, reversal is not. Its matrix, material, smooth flags and zero UV layers also match. No numeric tolerance or coordinate rounding is used. Proof: `terrain10-rebuild02-independent.json`.
- All four `CAM_MAIN_L2_MASTER_A/B` and `CAM_MAIN_L2_BATH_M_A/B` have identical saved and evaluated world matrices, local matrices, Quaternion modes and active values, location/scale, camera properties, exposure custom values, constraints and animation state. The corrected entry sets the rotation mode before restoring the active rotation channel.
- Static states of all131 cameras match. All material states, object modifiers, constraints, parents, collections, visibility and custom properties included in the audit match.
- All60 room geometry/navigation records match. Differences are only `model_status` text on60 records and a new `surface_identity_note` on five guest circulation records. Those annotation differences remain explicit; this is not a claim that every metadata byte or the `.blend` byte stream matches.

## The real02 animation failure

`CAM_TOUR_SUPPLEMENTAL`, `MAIN_L1_SERVICE_STAIR`, frames3745–3840:

- At3745, X changes from **−3.2184000015 m** to **−3.4584000111 m**, a real **−240.0000095 mm** displacement. The target is unchanged, so all four Quaternion key values also change.
- Five key coordinates therefore differ: location.X plus four Quaternion channels at3745. A sixth key record, Quaternion channel1 at3840, differs only in automatic handles.
- The handles follow neighbouring key values. Some differences are tiny float results, including a Quaternion channel3 right handle at3745, but they were not ignored. All key interpolation is LINEAR, so handle-only changes do not themselves alter the delivered motion. Re-keying with the original points/target restores the same automatic handle results exactly.
- Actual dependency-graph matrices differ on **95 frames,3745–3839**. The preceding cut frame3744, final endpoint3840 and next cut3841 match. Evidence: `checkpoint10-entry02-independent-animation-diff.json` and `checkpoint10-entry02-independent-animation-probe.json`. Thus this is not a Quaternion-sign-only difference or an inactive-property difference.

## Cause investigation and bounded correction

The default `room_candidates` loops through the room centre, entry offsets, reference hints and a fixed grid. `room_shot` sorts pairs by distance/focus penalty and takes the first mesh-clear pair. Searching again is not itself a saved-camera specification.

On both reopened scenes, a local evaluated BVH reproduces the original source path. Reversing scene-object insertion into that BVH still produces the same candidates and original path. The original frozen path passes actual mesh testing in all four trials. These results do **not** establish that room iteration or mesh insertion order caused the fresh-build02 drift; the build-time search context remains unconfirmed. We did not introduce an unproven generic ordering change that would affect other rooms.

Instead, the already verified source10 polyline, target and full segment metadata are frozen in `data/iteration10-room-shots-frozen.json`. The runtime entry no longer reads a QA-run directory for this input. `build_iteration10.install_frozen_room_shots(tour)` runs after guest preparation and Master10 adaptation, wrapping only `MAIN_L1_SERVICE_STAIR`. It checks real endpoint membership and re-tests the polyline against the caller's actual mesh at the original1cm sampling. A failing frozen path returns a failure; it is never exempted from geometry checks.

Endpoint membership uses Blender's actual float32 `Vector`, as original candidate evaluation does. The first guard attempt used the rounded JSON double directly:16.461 is a few double ulps below semantic16.461000000000002, while the saved Blender coordinate is16.4610004425 inside that boundary. The correction uses the actual representation, with no tolerance and no coordinate change. The first attempt script/log remain `checkpoint10-entry03-scoped-reinstall.py/.log`; its assertion stopped before any camera change or save.

The main entry then calls the original `tour.install`, including its normal `camera_evidence`, and checks that the installed service-stair segment metadata equals the frozen input. All other rooms retain their original dispatcher. No frozen10 helper, original `tour.py`, source scene or working scene was edited.

## Scoped03 execution and independent verification

Per the bounded request, physical geometry was not rebuilt a second time. A new CPU4 process opened the already generated02 checkpoint, installed the explicit room-shot adapter, used unchanged `tour.set_keys` for this one segment, and called unchanged `tour.camera_evidence` directly for the same96 frames. This is the function used within `tour.install`; the scoped evidence has a legacy hardcoded `main_frames=2880` field, which does **not** mean2,880 frames were tested in this call.

`checkpoint10-entry03-scoped-reinstall02.json` records:

- 96 actual saved poses and previous-frame mesh sweeps pass; zero geometry failures.
- All1,281 camera keys exactly equal source10, including coordinates, interpolation and both handles; no numeric tolerance.
- All23,437 static object fingerprints, material states, scene settings and embedded texts remain unchanged from02. Source files and original tour hashes are unchanged.
- The only changed data are the six previously differing camera key records. The output is a separate saved QA candidate, never the working model.

`checkpoint10-entry03-saved-compare.py` independently reopens that saved candidate, compares all objects and131 full camera states to source10, and compares98 actual affected/boundary matrices. For terrain, it additionally verifies exact indexed equality to02, which was already independently proven to be the exact source multiset; this transitive proof introduces no tolerance.

This work confirms the bounded integration path. A second complete from-scratch build using the new entry has not been run. Root can use the explicit frozen input in its next rebuild; the original install continues to perform all of its normal navigation checks.

Scoped neat-freak handoff: these new reports and the production input are the current record. Prior failed evidence is retained; root STATUS/AGENTS, iteration11 helpers, source geometry and other workers' documentation remain untouched.
