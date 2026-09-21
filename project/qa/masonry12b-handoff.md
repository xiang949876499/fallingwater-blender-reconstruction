# Tower12b height completion handoff

2026-09-21 · /root/site_visual · **Local height/mesh checks PASS; NOT_RENDERED; legacy cap/outlet form NOT_ACCEPTED.**

Candidate: `scene/Fallingwater_masonry_tower_candidate12b.blend`  
SHA256: `35d743a55af14290daa4a12e647a6d1d7717b3adeddc073a83739001f78f17c4`  
Helper: `scripts/masonry_tower12b.py`  
SHA256: `8f801ada246e6c492785d3174b11532e1d5ed495578498864258d2687eca05c4`

The source12a is unchanged at `b267636a9cbbe297513968f08f3b85930c0302cae1ebb75ed775043250e11a48`. Source iteration10 remains1e7b17d9…. Production scripts, original12a helper, central dimensions table, shared materials, working model and saved camera settings were not modified.

## Height evidence and explicit datum

`tower-height12-source-review.md` resolves the HABS32′9½″ witness to the continuous masonry/coping upper outline, excluding raised outlets. Nominal9.9949m is A; source-to-model component correspondence is C. The drawing names MAIN LEVEL TERRACE0′0″. This candidate explicitly maps it to the **actual visible terrace finish** (worldZ0.021999999881), consistent with the existingMAIN_LEVEL_2 finish comparison. ExistingMAIN_LEVEL_3/ROOF rows use structural zero; that22mm mixed convention remains disclosed and was not silently rewritten.

New continuous cap top worldZ10.016900062561; actual relative height **9.994900062680m**; numerical nominal error6.2680245e-08m. This is a floating-point fit to a printed target, **not actual-site survey precision**. Exact sheet survey date and survey accuracy remainUNKNOWN; museum collection context is circa2010.

## Bounded change

- Exactly five old object data blocks change: `MAIN_stone_tower_west`, `MAIN_stone_tower_north`, `MAIN_chimney_cap`, `MAIN_chimney_flue`, `MAIN_chimney_flue.001`.
- Each structural body changes only its four native old-top vertices, raising them by0.456899580264m. All other native vertices, XY coordinates, object matrices, material slots and existing Crafted edges Bevel settings remain unchanged. No whole-object Z scaling, lower floor shift or window-interface movement.
- Cap and two old outlet meshes translate by the same delta. Plan extents/thicknesses and relative offsets remain their previous C geometry.
- Three new `MASONRY12b_TopCompletion_*` meshes add6courses, **70closed stones / 2876triangles** within the existing35.5mm finish projection allowance. New top/bottom chips are0–4mm C, with small bounded mid-face facets. No rounded displacement or new shared material.
- The501closed stones /20622triangles of12a remain exact. Combined finish is571stones /23498triangles. New geometry uses the already-private12a stone material unchanged.

## Verification

- 23135 non-target objects exactly unchanged;77 physical hashes preserved, including core/water/bridge/paths/terrain and all three lower12a finish batches. All original globals/material nodes/image settings/lights/actions and all other mesh users unchanged.
- All70 new stone components and all five modified evaluated core/cap/outlet meshes are closed, oriented, positive-volume and nondegenerate. New nonadjacent self/cross-component intersections:0. Actual neighboring building intersections:0. Extended high-volume intersections with all candidate-neighbor meshes (including broad vegetation/terrain meshes):0.
- Minimum new triangle area8.83486517e-05m². Back contacts against actual substrate have signed gaps-0.000800132751to-0.000799953938m (intentional hidden .8mm embed).
- All131saved camera positions: minimum local tower clearance0.240649m. All7584current movie positions: minimum1.248500m. Current12264route rays:0newobstacles. This does not replace the parent’s complete navigation or GUI review.
- Fresh process reopened exact candidate fingerprint and checked repeated application is a verified no-op. No image rendering or GPU use.

`masonry12b-build-check.json`, `masonry12b-readback.json`, and `masonry12b-final-audit.json` carry detailed results. The failed unsavedattempt01 (too-narrow modifier prerequisite) andattempt02 (derived dimensions.z not yet explicitly whitelisted) are retained. Independent probes identified the exact savedBevel and dimension-only change; final checks permit only that known modifier and exact delta, not arbitrary object changes. No failed scene was saved.

## Explicit remaining cap/outlet failure

**The tower is not a finished photoreal or historically complete chimney.** Original cap plan is a broad single slab; source continuous coping row appears closer to the wall line. The two old objects namedflue are only30mm-thick dark boxes, have a10mm gap above the cap, and do not establish the source outlet count/shape. The second oldflue lies outside the west-core footprint and is carried only by the existing overhanging cap. These problems are preserved, documented, and not accepted by this height correction.

No new guessed vent bank, platform, support columns or unknown roof penetrations were added. A reliable complete outlet correction needs a roof plan or identifiable overhead view that locates individual outlets; the west silhouette alone does not locate their XY positions. Do not count the highest outlet as the nominal tower top.

## Parent render and entry

Use savedCAM_HERO atframe48. For a detail comparison, `masonry12b-camera-settings.json` keeps the same eye/target/exposure and uses lens32.0mm. The original36mm framing clips the corrected tower top; both original and proposed measured screen bounds are in `masonry12b-camera-probe.json`. Apply the identical external setting to12a and12b; do not compare mismatched lenses. No saved camera was changed.

`masonry_tower12b.build(ctx)` expects the exact completed12a geometry and its private material. For a later fresh integration the order is12a first, then12b; do not call12a’s original guard check again after12b has intentionally changed its five protected tops. The12b entry verifies its own stored geometry on repeat and rejects partial/changed states. This remains a candidate entry, not a production enablement request.

neat-freak closeout is confined to ownedQA: dimensional evidence, controlled failure history, candidate/hash/interface facts and NOT_RUN/known-failure states are consolidated here. RootAGENTS, STATUS and central manifests remain unchanged.
