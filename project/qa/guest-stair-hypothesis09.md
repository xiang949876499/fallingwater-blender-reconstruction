# Guest stair09 — four half-flight numerical hypothesis

2026-09-21. **C numerical feasibility only; no model built or installed.** The four half flights can fit a conditional envelope, but cannot coexist with the unchanged08 south platforms and west return floor. Source storey assignment, north-cap construction and inter-sheet registration remain unresolved. This is neither navigation acceptance nor a historical reconstruction approval.

Complete machine-readable inputs, every enumerated option, analytical rectangle-pair witnesses and immutable input hashes are in [guest-stair-hypothesis09.json](guest-stair-hypothesis09.json). Reproduce using the adjacent `guest-stair-hypothesis09-probe.py`; it imports no Blender modules and only writes its QA JSON. Independent `nav08_semantics` arithmetic agrees and that agent has finished.

## What is established, and what is assumed

Actually viewed source: guest01/02 original TIFF crops and guest04 datum/section crops, recorded in `guest-stair-source09-review.json`. The native guest02 service crop was reopened for the northern cap check. The printed L1 datum0 and L2 datum2.352675m are A. The right UP arrows point north on both plans, and guest02's arrow turns south along the left run and north along the right run. These directions do not establish platform levels.

B1=-2.36m, absolute guest datum+8.4m, each half-flight's storey assignment, stair slab thickness and alignment between the separately printed basement inset and the two plans are C/U. The enumerator uses explicit C design-screen intervals: riser0.13–0.19m, going0.25–0.40m. These are not a claim of statutory compliance or measured original dimensions. The existing project headroom1.95m and body radius0.18m are unchanged.

For N risers there are N−1 goings between the first and last riser lines. Current production uses a different L/N slab convention; these counts cannot simply be passed to that builder. Visible raster edges are recorded separately, never promoted to validated riser counts.

## Numerical candidate

All heights below are relative to guest L1=0. Source coordinates are normalized width1024 on the explicitly named sheet; the B1 inset is not already world registered.

| Flight | Source centerline pixels | Visible edges | Tested risers / going / riser | Start → end Z m |
|---|---|---:|---|---|
| F1, B1 left, south | guest01 B1 inset (296.25,655.8)→(296.25,673.1) | 4 | 4 / .304019 / .181538 | −2.360000→−1.633846 |
| F2, lower right, north | guest01 (316.35,400.8)→(316.35,350.0) | 10 incl boundaries | 9 / .334772 / .181538 | −1.633846→0 |
| F3, upper left, south | guest02 (296.75,369.0)→(296.75,405.5) | 7; visible starts372.6 | 8 / .274897 / .180975 | 0→1.447800 |
| F4, upper right, north | guest02 (316.35,405.5)→(316.35,382.0) | 5 incl boundaries | 5 / .309730 / .180975 | 1.447800→2.352675 |

The lower pair has three integer solutions:4+9,4+10,4+11. At the fixed provisional B1 datum, their lower middle landings range **−1.730667 to−1.633846m**. The table selects4+9 as one example. Treating the entire B1 enclosure as tread length gives eight additional arithmetic options, but consumes the drawn door/landing zone; those optimistic options are recorded and not selected.

The **nominal visible-only upper left run372.6→405.5 is a retained negative case**: it can hold only6–7 risers under the stated going interval; the upper right holds5, while the2.352675m rise requires at least13 total. It therefore has zero nominal integer solutions. However, the additional length needed to fit eight left risers at minimum going is only **15.512mm ≈0.2942px**. Approximate tracing and unresolved registration are larger than this difference, so the nominal failure is not a robust proof against the hypothesis. No tolerance is silently added to turn it into a pass.

Extending the left start to369 gives the single8+5 solution. **This extension is not yet approved source geometry.** The native crop visibly outlines a cap/frame band from approximately369 to372.6, rather than unequivocally showing a vacant walking strip. The tested interpretation is C: that band is a higher projected edge and the lower first tread can pass beneath it. Its height and solid construction still need evidence.

## Headroom and unchanged08 conflicts

The probe computes exact interval intersections of constant-height tread/landing rectangles with an overhead rectangle and a0.18m disk along the tread centerline. It includes tread discontinuities and finite body radius. This is a numeric envelope, **not actual mesh collision, doorway validation or a full route test**. Treads are assumed0.13m thick; new platforms0.21m. Same-flight end landings are handled as stair transitions, not misclassified as low ceilings.

| Conditional envelope location | Minimum headroom m |
|---|---:|
| B1 door / upper L1 approach | 2.150000 |
| Lower right and return / upper works | 2.227746 |
| First upper-left tread / L2 northern slab edge | **1.961700** |

The limiting upper-left first tread has only **11.7mm** reserve. The combined slab and any downward finish may be no thicker than **0.2217m** at that overlap. Unverified beam/cap geometry could invalidate the candidate. The two hypothetical middle platforms themselves differ by3.081646m, avoiding the earlier idea of squeezing a new landing directly above existing high B1 treads.

The unchanged production slabs produce actual numerical contradictions at overlapping plan locations:

| Lower walking surface / upper structure | Headroom m | Consequence |
|---|---:|---|
| Lower middle / `GUEST_L1_HALL_SOUTH`, thickness.22 | **1.413846** | Fails even if the old slab had zero thickness |
| Upper middle / `GUEST_L2_STAIR_TOP_LANDING`, thickness.21 | **.694875** | Fails even at zero thickness |
| Upper-left flight / `GUEST_L2_STAIR_PASSAGE`, thickness.19 | **.895850** minimum | Already fails at its second tread:1.800725m |
| Existing L1 south walkway / hypothetical upper return, thickness.21 | **1.237800** | Existing south route cannot remain under the new middle platform |

No old slab has been removed or altered to suppress these contradictions. Treating the new platforms as the levels of the formerly flat south areas would change the current circulation interpretation, including the main connector arrival. That requires its own source and full-context checks.

## Registration and next gate

For this test only, B1 inset station648 aligns with the unchanged modeled door midpoint365.835: inset Y translation−282.165px. F1 then occupies plan Y373.635→390.935. Its lower return needs a **.520083m** longitudinal offset to the right-flight start400.8. The probe uses an explicit C return stub and a C south turning band; their drawn layer and true extent are not established.

Alternatively aligning the last B1 visible edge directly with the right-flight start moves the existing door registration by **.520083m**. This discrepancy is preserved, not hidden by moving the door. Sheet01 and sheet02 control correspondence also remains U. Printed B1 finished width.7366m and upper return depth.743352m satisfy the nominal .36m body-width necessity; that does not validate walls, railings, openings or real turns.

**Decision:** retain this as a possible C construction hypothesis with explicit failed controls. Do not install it or label the four runs A. Root must decide whether further source evidence justifies a separate candidate, particularly the north cap, south platform layer/extent, B1 registration, and connection to the existing north and south circulation. Current08 negative acceptance remains58PASS/2FAIL with7584 camera frames passed; no checked08 scene exists.

Scoped documentation reconciliation: this report and the JSON agree with the completed numerical run; production `guest_house.py`, `tour.py`, `guest_house.json` hashes are unchanged. Frozen08 and all earlier failed scenes/reports were neither loaded nor modified in this task. Shared STATUS/AGENTS remain owned by the root integrator.
