# Forest canopy11a handoff — 2026-09-21

**Superseded acceptance status:** root subsequently accepted the18-root local shape after the paired images (`forest-canopy11-root-visual.md`). Production native loading and full-nav10a regression are documented in `forest-canopy11-integration-handoff.md`. The original standalone candidate record below remains historical.

**Physical and fresh-reopen PASS; visual NOT_RUN.** One candidate is ready for the parent’s three paired CPU renders. No production integration or rendering was performed by this agent. Local canopy improvement, global forest density and photorealism remain unaccepted until actual image review.

Candidate: `scene/Fallingwater_forest_canopy_candidate11a.blend`.

SHA256 `b8b46f839afa980229222be4ec92f58ad3d6c76ba88313d579a009a1a8a0c16b`.

Source: `scene/Fallingwater_bridge10_endfix.blend`, SHA256 `2a7630b8024c37bd768e563236807f8049469172c7e44b03379a450f91637063`. Old water, original ground material and all other bridge/full09 content are preserved. Saved frame73; render comparisons must explicitly set frame48.

## Final bounded content

Three copied assets serve18 unchanged roots and replace only36 branch/leaf object data pointers. All23,279 non-target objects and all original mesh blocks/global state match the source. Old vertices, faces, UVs, materials and transforms are retained; the added branch/leaf surfaces remain within the original leaf-crown convex envelope and preserve world crown XYZ bounds/tree height. No asset library, site/build/config, material, terrain or source scene was changed.

| Asset | Selected roots | Original → final leaves per asset | Final one-sided leaf area m² | Final branch+leaf triangles per asset | Added connected shoots |
|---|---:|---:|---:|---:|---:|
|0|6|15,552 → 25,256|235.139|183,216|1213|
|7|7|2,880 → 4,784|41.031|36,358|238|
|8|5|4,320 → 7,488|63.828|56,628|396|

The six shared copied meshes add110,820 unique triangles, representing655,440 added triangles across the18 selected instances. Their87,392 added world-instance leaves are separate folded blades on short real branches. Counts include every original leaf and woody face. These are implementation budgets, not ecological field measurements. No billboard, sphere, canopy-volume object, mesh scatter or new tree root is used.

The original15,552/2,880/4,320 blades had modeled areas148.565/26.954/40.276m²; final235.139/41.031/63.828m² is a roughly52–58% area increase inside the retained crown. Material tones were deliberately preserved for this geometry-only comparison. Smooth original trunks, unchanged far canopy and sparse global planting remain limitations. Source species at each exact root remain unidentified; shoot placement and density are C.

## Verified constraints

- All1,847 new shoots have actual triangle contact with original woody geometry (1,213/238/396 per asset); no detached shoot remains. New leaf bases are within1.981µm local-space distance of the final branch mesh.
- All18 root matrices remain exact. Actual terrain gaps stay approximately−12mm (−12.031 to−11.981mm); roots were not reseated. New crown geometry is at least.6134m above actual terrain and produces no triangle crossings with frozen hard geometry.
- The full frozen09 route supplies11,554 rays per selected instance,207,972 ray checks total, with zero new obstruction. All129 stored camera transforms remain unchanged; minimum clearance to added geometry is.4065m against the.40m criterion.
-616 conservative main-house sightlines across the three specified QA views have zero added hits after shared-asset pruning. This64×36 per-view sampling is not an exhaustive all-pixel occlusion guarantee; parent must inspect images.
-73 evaluated core/shoulder/old-water/path/bridge physical hashes remain identical. All old materials, worlds, cameras, lights, render settings, embedded config and object count are fingerprint-identical.
- Fresh process reopened the saved file and reproduced the complete saved scene fingerprint plus all73 physical hashes. `forest-canopy11-readback.json` reports `FRESH_REOPEN_PASS_VISUAL_NOT_RUN`. No scene re-save occurred during readback.

The first unsaved attempt found that removing only a camera’s nearest leaf group left a second layer within.40m. `forest-canopy11-check-attempt01.json`/`forest-canopy11-build-attempt01.log` preserve the failed evidence. Final filtering removes every group intersecting the actual camera radius, and deterministic visibility-layer pruning removes remaining protected-ray blockers. The design, random seed, root positions and original geometry did not change. Per-asset final group exclusions are2/11/0, in addition to81/39/36 groups rejected outside the original envelope.

## Exact selection and reproduction

Exact18 roots,36 modified object names, matrices and data identities are in `forest-canopy11-check.json` and `forest-canopy11-approved-groups.json`. Callable generator/application helper is `scripts/forest_canopy11.py`, SHA256 `f6fbc3626fcc299e46f4bf852dd2698ef0c4672f7e62910ef3928ddebfcc5b74`. It is an isolated candidate helper; no production wrapper was enabled. `forest-canopy11-build.py` demonstrates guard checks, exact source opening, deterministic group generation, conservative pruning, application and whole-scene comparison. It refuses to overwrite an existing candidate. Reproducing a future scene requires a separate destination and a new full-context regression, not mutating this accepted-for-review checkpoint.

Parent rendering: (1) native overview target(−4,−5.5,−6.325), eye=target+normalize(−1,−1.4,1)×45,40mm; (2) bridge approach eye(27.45,−10.5,1.8), target(27.45,2,.25),28mm; (3) saved `CAM_MAIN_L1_LOGGIA_B`. Apply identical camera/light/exposure/frame settings to source2a and candidate11a. The first two are external QA camera specifications and were not inserted into the candidate.

Ready `render_views.py --camera-settings` mapping: `qa/forest-canopy11-camera-settings.json`. It uses existing `CAM_HERO` for the bridge approach (EV0, matching root's bridge10-endfix pair), existing `CAM_WATER_DETAIL` for the native overview (EV+.8, matching the earlier native overview), and preserves the saved LoggiaB transform/lens with EV+.8 (matching iteration08-focus). Apply the same file to both scenes at frame48. No novel camera object or source-scene save is needed.

Source findings and limitations: `forest-canopy11-design.md`; numerical source asset inventory: `forest-canopy11-probe.json`. The two official Spring JPEGs are actual-viewed reference-only evidence, never textures or public-package assets. `forest-canopy11-reference-manifest-append.csv` proposes their two central-manifest rows for root to merge; central manifest is unchanged.

Neat-freak reconciliation was limited to these owned QA handoff/design/source records. Global AGENTS/STATUS/build integration and release manifests remain parent-owned. No commit was made.
