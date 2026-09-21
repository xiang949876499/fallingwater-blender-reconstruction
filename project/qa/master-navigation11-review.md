# Master navigation11 — bounded saved-key and doorway adapter

Local geometric acceptance on physical ceiling11b. Source ceiling height remains **OPEN** and GEO-07 is **NOT_RUN**. No image was rendered in this task; these checks do not establish photographic correctness or complete-film acceptance.

## Artifacts and integration

- Helper: `project/scripts/master_navigation11.py`, SHA256 `5bf1a511c5057b61617ed0fbcd717fccd828cb064e31729c125cf0bc7a9c9100`.
- Physical input: `project/scene/Fallingwater_master_ceiling_candidate11b.blend`, SHA256 `c0d71ca14782c8af5a5b6593336cd4f652c4808da7f824405538a159280ddcde`.
- Reopenable navigation candidate: `project/qa/master-navigation11-workspace/scene/Fallingwater_navigation11a.blend`, SHA256 `f54a77177f8994b904e21cbb3a308e96a8e977f4b867077f6ca6ce5a9c2f4d3c`.
- Corrected route: `project/qa/master-navigation11-workspace/data/tour-route.json`.
- Frozen reference route: `project/qa/integration10-navigation-workspace/data/tour-route.json`.
- Build evidence: `master-navigation11-build-check.json`; independent new-process readback: `master-navigation11-reopen.json`. Corresponding scripts and logs are retained.

Nothing runs on import. Explicit integration order is physical geometry first, then the existing guest adapter, then frozen Master10, then this adapter. Use the caller's isolated workspace, with its guest route specification already present when using read-only preparation:

```python
tour, rooms, guest_spec = guest_circulation10_routes.prepare(
    workspace, scene, rooms, read_only=True)
master_navigation10.apply(tour, scene, rooms, workspace)
spec = master_navigation11.apply(
    tour, scene, rooms, workspace, reference_route=frozen10_route)
```

The adapter reads actual evaluated `MAIN_L2_MASTER_finish`, `MAIN_L2_TERRACE_S_finish`, and `MAIN_L2_master_south_sill` faces. It fails before installing dispatch or writing room changes if actual geometry is incompatible. Root's combined terrace11a/tree/soil geometry must be rechecked; this candidate contains only ceiling11b physics.

For a scoped update of the **existing saved cameras**, then call:

```python
master_navigation11.patch_saved_terrace_keys(scene, route, spec)
master_navigation11.embed_metadata(scene, rooms, spec)
# Caller writes its route and saves its candidate explicitly.
```

`patch_saved_terrace_keys` first validates the unique segment, camera, frame interval, route endpoints and target, all 96 actual saved XYZ evaluations, and non-overlap with other segments. A mismatched route rejects before mutation; this was tested. It changes only two location.Z keys, at frames 5089 and 5184. The corrected route target rises equally, while saved camera rotations remain unchanged. Repeated patching rejects instead of accumulating another rise.

For a full navigation rebuild, install the adapter before the caller's `tour.install`. The explicit terrace `room_shot` preserves frozen10 XY endpoints; it avoids default resampling after changing the floor datum. Do not also patch an already rebuilt camera. This task did not run a full rebuild, revalidate all 60 graph edges, or all 7,584 film frames. The two-foot doorway graph proof remains separate from the original 96-frame terrace film segment; it is not compressed into that film segment.

## Actual geometry and saved-key results

| Check | Result |
|---|---|
| Real finish datum, Master and terrace | Z 2.8668000698 m |
| Preserved source/structural record datum | Z 2.8448 m |
| Real sill rise above actual finish | 52.200079 mm |
| Old flat walking attempt | FAIL, raised sill encountered |
| Old Master10 raised-torso step | FAIL, new continuous low ceiling encountered |
| New outward and inward two-foot steps | PASS, each 122 poses and 1,890 support points |
| Maximum support error, each direction | 0.0000302 mm, within unchanged 4 mm threshold |
| Minimum swing sole clearance above track | 25.0719 mm |
| Torso lift during new step | 0 m; full 1.95 m head height and 0.18 m body radius retained |
| Approach, departure, both joining edges, room endpoints | PASS in both directions |
| Original terrace saved frames 5089–5184 | 96/96 FAIL before correction; 96/96 PASS after correction |
| Original Master saved frames 1441–1608 | 168/168 PASS; all keys unchanged |
| Fresh readback of corrected 96 frames | PASS including adjacent-frame sweeps; maximum actual finish error 0.000143 mm |
| Independent reverse body columns on 96 saved positions | 1,632 downward columns, zero obstacle hits |
| Boundary matrices 5088/5185 | Unchanged |
| Boundary matrices 5089/5184 | Only world Z changes by 22.00007 mm |

The gait uses two distinct supported footprints on the real side floors. One foot stays supported while the other rises and crosses. Its sole, foot volume, legs, upper body, and sampled continuous sweeps are checked. No whole 240 mm foot is claimed to stand on the 60 mm track. The reverse step actually recomputes the two feet and sweeps in reverse travel, rather than reversing only the eye path. The numerical footprint, lift, timing, and fixed-torso construction are **C** navigation choices; these checks are not biomechanical certification or a human animation.

Negative evidence is retained in the candidate workspace's `qa/`: `master-navigation11-flat-ground-fail.json` and `master-navigation11-old-raised-torso-fail.json`. The older ceiling11 gait and foot-datum failures remain untouched. Neither thresholds nor true floor/window/track geometry were changed to make a pass.

## Data meaning and protection

Only Master and south terrace room records gain explicit `source_level_datum_z`, `navigation_finish_z`, `navigation_finish_evidence`, and navigation revision fields. Their `z` now supplies the measured finish to navigation consumers; their original Z 2.8448 source/structural record remains separately recorded. This does **not** upgrade that original record to a surveyed historical elevation. Reopening and rerunning guest + Master10 + navigation11 preserved the original datum, rather than overwriting it with the already corrected finish or adding another 22 mm.

All 23,436 object fingerprints, all 58 materials, scene/render settings, and object counts were unchanged. Of 1,281 saved camera keys, precisely two terrace location.Z keys and their own handles changed; the other 1,279 were unchanged, including all rotations and review cameras. All other route data, embedded room records, and existing embedded texts were unchanged. Existing guest/default Probe, stair, connector, and storage dispatch identities were retained. An actual unaffected Master–bath connection returned the identical result before and after installing this adapter. Frozen10 helpers, original tour, source scene, production data, and source geometry hashes stayed unchanged.

Source relation: the outward leaf identity is supported by the earlier source review (**B**); current physical dimensions and finish positions are measured model geometry. The ceiling low/high elevations and divider remain **C**, and the model's 0.1532 m drop still differs from the earlier graphical **C** estimate 0.417 ± 0.04 m. Full height precision, high-window appearance, GEO-07 and photographic acceptance remain unresolved.

Scoped neat-freak handoff: this report is the current API/result record. No root STATUS, AGENTS, shared model, source file, or another worker's documentation was rewritten. Earlier failed evidence is retained explicitly instead of being relabelled PASS.
