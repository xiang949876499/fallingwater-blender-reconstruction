# Guest circulation10 navigation and runtime handoff

Current gate: **60 / 0 / 0 adjacency and all 7,584 integer frames PASS**, followed
by an independent reopen of the saved camera keys and **all 7,584 frames PASS
again**. No keys were rebuilt for the reopen. All source/candidate hashes and
protected data stayed unchanged in their respective frozen checks. No production
install, rendered-film acceptance or all-room visual acceptance is claimed.
The machine-readable current entry point is `guest-circulation10-navigation-final.json`.

The graph result is 60 PASS / 0 FAIL / 0 NOT_RUN, consisting of 52 normal-walk
edges and 8 explicitly typed inspection-only edges. Camera cuts do not satisfy
any graph edge. The source is frozen physical 10f, SHA256
`7286427d1f47ae9219204ed5dd54a970387683c8b384d1b4259244a7b991d852`.
Saved candidate animation:
`scene/Fallingwater_guest_circulation10_navigation_attempt04.blend`, SHA256
`7c3e2dc6819268185a7b956bdd49445f509088107128fa1a3d63d0ddeb56c094`.

## Composition interface

`guest_circulation10_routes.prepare(workspace, scene, rooms, read_only=False)`
returns `(tour_module, candidate_rooms, guest_spec)`. The workspace must be an
isolated metadata/output directory. It reads the actual embedded physical
manifest, writes candidate overlays, loads a fresh instance of the production
tour implementation and redirects that instance to the workspace. No production
tour or guest-house data file is modified.

Apply any master-room adapter to that returned module and room list, preserving
prior function wrappers for unrelated IDs, then call
`tour_module.install(scene, candidate_rooms)`. Guest wraps evaluated Probe,
hinted_connection, stair_connection, room_candidates, stair_space_anchors and
connector_shot. It does not modify any main-house room node and does not wrap
connection, room_shot or camera_evidence. For saved-animation reopen,
`prepare(..., read_only=True)` reads the frozen workspace specification without
writing metadata or rebuilding camera keys.

`data/guest_circulation10.json` contains actual foot-coordinate paths, flight
treads, platforms, connector pieces, source-divider data, room overrides and the
candidate guest adjacency overlay. Source-pixel and world-coordinate fields
remain explicitly named. The changes replace the old guest stair/flat paving
identities and the false west Lounge door; the real southeast door is retained.
The room count remains 60.

## Runtime design data

Canonical physical input: `data/guest_circulation10_design.json`, SHA256
`f30e65fc967a61b0465f326f91b58a21b9ce4ede00340b63243ec9bcc665b6c6`.
It is byte-identical to the archived numerical design input. The original QA
copy remains historical evidence and is no longer the runtime read location.

Current physical helper SHA256:
`97b5b69a6e6214efd491d7629e13c916cd12b4de90349a3950c4dbfc5250f345`.
Current route adapter SHA256:
`a9298ba4f340eb91c461988f6ff19698e49153742e6b08b376af9b8e3f173412`.
Both migrations changed exactly one path literal. Numerical inputs and geometry
values did not change. The saved tour was validated with the archived adapter
SHA256 `b416bfe8618204b1886198d52a73fe35f16b9c06f6817ef5f40f5b558c55bc0f`;
the independent reopen uses that exact archived source. See
`guest-circulation10-navigation-runtime-migration.json` for before/after hashes.

## Measurement boundaries

The full navigation method retains the production tour thresholds: 0.18 m body
radius, body columns to 1.71 m, 0.19 m walking ground tolerance and a 0.13 m camera
clearance test. It now indexes dependency-graph evaluated mesh geometry. This
must not be described as a full-building 1.95 m headroom audit.

The separate physical candidate audit tests 1.95 m headroom, 0.18 m body radius
and 4 mm ground agreement: 29 groups / 3,503 samples passed against the new solid
divider, four service flights, both front stair groups and full connector. Its
minimum measured clearance is 1.961699 m. This stricter local standing/body
screen and the full-tour animation method are distinct evidence. C levels,
counts and divider height remain C after either geometric test.

## Cameras and preserved failures

Use `guest-circulation10-render-cameras.json` for the four initial diagnostics,
with the southeast view superseded by
`guest-circulation10-navigation-entry-camera-retreat.json`. Five proposed census
camera replacements are in `guest-circulation10-navigation-camera-overrides.json`;
all passed actual body/ground/eye tests and remain unapplied to production.
See `guest-circulation10-navigation-camera-review.md` for affected plane/level
identities and the distinction between camera clearance and image quality.

Root has rendered and inspected the retreated southeast view and accepts its
visible complete door header/jambs as local entrance inspection evidence. The
Lounge interior is still dark and is not fully pictured. Root's four-view and
retreated-entry review in `guest-circulation10-root-visual.md` accepts the local
solid circulation corrections but retains overall environment/photorealism
FAIL; it does not replace future merged-scene navigation or 120-image review.

Attempts01 and02 retain the first-step proximity and outdated B1 census-envelope
failures. The envelope correction unions the actual north landing footprint;
it does not create a floor or alter space counts. Attempt03 retains 59 PASS /
1 FAIL and 7,584 passing frames: a collinear Chauffeur-door node at a shared
floor edge returned a vertical normal with the validator's 1 mm BVH epsilon.
Attempt04 removes only that collinear node, keeping the physical straight path,
endpoints, geometry and thresholds unchanged. No earlier failure was relabeled.

Scoped neat-freak reconciliation: this is the current candidate navigation
entry point. The physical 10f report points here; design, panorama and negative
candidate documents remain labeled by scope/version. Root README/AGENTS were
reviewed and remain accurate about incomplete production delivery; AGENTS stays
14 lines. Root owns global STATUS/START_HERE and no global settings were edited.
