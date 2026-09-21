# Four printed dimensions: evaluated-surface supplement12

**FINAL: read-only frozen-case checks PASS.** Helper SHA256: `433ac64d9a4ccb4a0ec14b9d95c9c68184d146940ae5c8a51526d07727fbf9ac`. The full snapshots, repeated measurements, source file hashes and protected central-file hashes were unchanged. No geometry or rendered scene is delivered by this task.

Scope: a read-only, self-contained `scripts/dimension_supplement12.py`. Call `measure(bpy.context.scene)` after composing the desired physical helpers. It returns a JSON-serializable dictionary with exactly four `anchors`, their `counts`, per-station triangle hits and source qualifications. It does not import construction helpers, read a dimension CSV, save a scene, change a mesh/material/camera or start a render. The caller must bind the current composed scene to its own saved-file hash; `bpy.data.filepath` alone is not proof of an unsaved scene's provenance.

## Endpoint meanings and independence

| Stable anchor ID | Printed source | Selected physical endpoints |
|---|---|---|
| `MAIN10_L2_WEST_TERRACE_X` | HABS05,28 ft11¼ in | Unified `MAIN_L2_west_parapet_0` exterior WEST face → `MAIN_L2_dressing_shell_middle` WEST stone face. This is a horizontal projection, not a cantilever or clear room width. |
| `MAIN10_L2_WEST_TERRACE_Y` | HABS05,17 ft6⅜ in | NORTH OUTER face → SOUTH OUTER face of the same unified west `parapet_0` mesh. Neither is an inside face or its object's maximum dimension field. |
| `MAIN10_L2_SOUTH_TERRACE_X` | HABS05,25 ft5¼ in | WEST OUTER face → EAST OUTER face of unified `MAIN_L2_south_parapet_0`. |
| `SOURCE08_MAIN_BRIDGE_SOUTH_STONE_GAP` | HABS04,13 ft3 in | Opposing inward vertical END FACES of `SITE_Bridge10_Stone_Return_SW` and `_SE`. Concrete parapets, deck edges and north stone ends are excluded from this assertion. |

These IDs intentionally match earlier source assertions. Deduplicate by ID when updating a central report; nine repeated stations per anchor are not nine independent dimensions, and remeasuring an already listed source value is not a new source assertion.

The west projection has two west-facing boundary planes. Both rays correctly approach from the west and report normals pointing west. Forcing one ray to return the inner parapet face would silently change the source meaning. The other three anchors use opposite ray directions and opposite expected face normals. All endpoints are actual evaluated triangle hits, with evaluated triangle/polygon indices, normals and world points. The axis separation is computed from those hits, never from an object bounding box, `Object.dimensions`, constructor constants or source nominal metadata attached to a model.

## Viewed source and precision

Actually opened in this task: `dimensions10-main05-westchain.png`, `dimensions10-main05-southwidth-detail.png`, their two separately marked witness overlays, `bridge10-native-south_dimension.png`, `bridge10-native-south_west.png`, and `bridge10-native-south_east.png`. These are already stored faithful excerpts; no new image extraction, source modification or download was performed. The full original TIFFs were not directly displayed by this task. Exact source hashes and archive identifiers are embedded in each anchor.

Main05 witness points are retained in the original excerpt's coordinate system, with its actual pixel dimensions; the desktop's display resize is not a new source coordinate system. Main05 has no documented numerical pixel tracing uncertainty for these witness picks, so it remains U rather than inventing one. Bridge witnesses are upright-native approximately(14028,11254) and(15359,11254), projected to the stone ends near native y10230. Its existing±5 native-pixel trace bound and±50 mm world-registration bound are explicitlyC.

The four printed labels are A values. Their displayed fraction quantum is recorded separately:6.35 mm for¼ in,3.175 mm for⅛ in,25.4 mm for whole-inch notation. This is transcription resolution, **not survey accuracy**. Survey absolute accuracy remains U for every anchor. Existing C placement, terrace fixed-interface choices, bridge center placement and sample locators remain C. Passing nominal lengths does not upgrade their absolute registration or construction details to A.

The existing nominal acceptance threshold stays `max(20 mm,0.5% of printed length)`. Each of nine stations must produce both designated surfaces, correct flat-face normals and a span within that threshold. Missing mesh or the old, unmerged terrace segment semantics returns `NOT_RUN` with a concrete reason. A present designated surface that misses the probe or fails the correct face/length condition returns `FAIL`. There is no bbox fallback, tolerance widening or substitution of a rounded lip.

## Frozen independent cases

The exact outputs and final counts are in `dimension-supplement12-check.json`, the two per-scene JSON files, and the check log. No PASS is copied across scenes. Terrace11a returned **4 PASS / 0 FAIL / 0 NOT_RUN**. Bridge10 endfix returned **1 PASS / 0 FAIL / 3 NOT_RUN**, for the concrete prerequisite reasons described below.

| Nominal source value | Actual median from nine stations in terrace11a | Maximum absolute numerical residual |
|---|---:|---:|
| 28 ft 11¼ in = 8.820150 m | 8.820149899 m | 0.000578 mm |
| 17 ft 6⅜ in = 5.343525 m | 5.343525887 m | 0.000887 mm |
| 25 ft 5¼ in = 7.753350 m | 7.753350735 m | 0.001688 mm |
| 13 ft 3 in = 4.038600 m | 4.038599014 m | 0.000986 mm |

Those tiny residuals reflect floating-point evaluation of geometry deliberately built to the printed nominal. They are not source surveying accuracy or evidence of photogrammetric fidelity. The bridge endfix scene independently produced the same actual bridge median; it did not reuse the terrace11a result.

- Terrace11a candidate: `scene/Fallingwater_main_terrace_candidate11a.blend`, SHA256 `e856456005d3a4493e70122644d52192dd49c2d2ffc046248b1247484beb4750`. Contains the unified terrace surfaces and the bridge end faces, so all four anchors are exercised.
- Bridge10 endfix candidate: `scene/Fallingwater_bridge10_endfix.blend`, SHA256 `2a7630b8024c37bd768e563236807f8049469172c7e44b03379a450f91637063`. Its actual bridge is exercised; old terrace objects do not carry the new unified face identity, so the three terrace anchors are explicitly NOT_RUN here.

Each case is freshly opened in a CPU4 Blender5.2.1 process with Python exit-code enforcement. The same helper is called twice for deterministic equality. Full source-scene fingerprints before/after the calls protect object/mesh/material/image/world/light/camera/action/settings state. Both source hashes and the central `dimension_audit.py`/`dimensions.csv` hashes are checked unchanged. No candidate scene is created or saved by this task.

The proof is limited to these four nominal dimensions. It is not full GEO02 completion, overall source accuracy, geometry repair, navigation acceptance or a visual judgment. During this task the parent reported new dark horizontal bands at the integration11a south/west slab/parapet interface and began a separate geometry diagnosis. This helper retains the same true parapet_0 dimension faces and does not promote11a or infer the cause of those bands. Parent's `forest-litter12-root-visual.md` rejects the independent litter layer; this dimension helper neither applies nor reclassifies it.

Neat-freak reconciliation is limited to the owned helper and this QA family. Source reports, old negative results, shared central files, project status and production helpers remain unchanged. Root AGENTS/README correctly retain the broader project's incomplete status.
