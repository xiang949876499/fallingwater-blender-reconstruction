# Guest circulation10 — selected C design, numerical stage

**Select a south service arrival at−1.18m, keep the north foyer/Chauffeur/Boiler level0 and upper hall+2.352675m, and use four half flights plus the two drawn front-walkway stair groups.** This is a concrete C construction design, not an installed model or a new navigation PASS. No production guest/data/tour/main/furnishings file was changed or Blender scene built.

The complete station coordinates, finished-plane identities, count enumeration, analytical headroom witnesses, retained negative cases, connector proposal and production input hashes are in `guest-circulation10-design.json`. Reproduce using `guest-circulation10-probe.py`; it writes only this task's JSON. The new full-sheet source review is `guest-level-context09-review.md/json`. Native guest01 south paving/service crops and guest03 stair elevation crop were actually opened for this design.

## Selected flights and heights

All heights below are relative to guest MAIN LEVEL, with the current absolute guest datum+8.4m retained. MAIN0 and SECOND+2.352675 are printed; B1−2.36 remains the existing C datum. South−1.18 is a C finished-face interpretation inside the observed grade-line interval−1.20..−1.11, not an A platform label.

N risers correspond to N−1 going intervals. The design retains the stated screens: risers0.13–0.19m, goings0.25–0.40m, headroom≥1.95m and body radius0.18m. These are explicit project design criteria, not a claim of statutory compliance.

| Flight | Source plan direction and stations | Risers | Riser / going m | Finished Z m |
|---|---|---:|---|---|
| Lower left F1 | Full first-floor left projectionY368→404.5, south | 8 | .147500 / .274897 | −2.36→−1.18 |
| Lower right F2 | First-floor rightY400.8→350, north | 8 | .147500 / .382597 | −1.18→0 |
| Upper left F3 | Second-floor leftY369→405.5, south | 8 | .180975 / .274897 | 0→1.447800 |
| Upper right F4 | Second-floor rightY405.5→382, north | 5 | .180975 / .309730 | 1.447800→2.352675 |
| Front west W1 | X324→336, east; source DOWN west | 3 | .168571 / .315360 | −1.18→−.674286 |
| Front east W2 | X428→448, east; source DOWN west | 4 | .168571 / .350400 | −.674286→0 |

At the selected south level, **8+8 is the unique lower pair with a common riser** within both full projected run lengths and the fixed screens. South−1.18 is25.5mm below the source grade-line center, within its reading interval; choosing the midpoint between B1 and L1 also eliminates a change in riser between these two flights.

The front walk has two feasible pairs:3+4 and3+5. Select **3+4** because its two/three goings match the two/three visible bands and it adds no inferred extra edge. Its middle terrace is−.674286; the east terrace and eastern room approach stay0. The original useful walkway laneY450..472 is retained, with path centerY461. Lounge's interior floor is not lowered to the front-walkway level.

This explicitly abandons the previous four-visible-edge lower solution with a−1.633846 south return. It also rejects forcing8 risers into the basement inset's visible-only span: that would give only.130294m goings, or.210880m if the whole inset enclosure were consumed. The selected longer lower flight instead uses the first-floor UP/DOWN/break projection, so its overlap/hidden-edge interpretation remains C.

## Finished faces and circulation

The new faces must replace the old membranes, not be installed beneath them:

| Existing face | Candidate treatment |
|---|---|
| `GUEST_L1_HALL_SOUTH`, presently0 | Low south plane−1.18 overY405.5..472, plus exact lower flight stubs; no0m slab across the well/return |
| `GUEST_L2_STAIR_TOP_LANDING`, presently+2.352675 | Remove the fullY404..422 upper plate; retain only the drawn returnY405.5..419.6 at+1.4478 |
| `GUEST_L2_STAIR_PASSAGE` | Keep north paved approach throughY369; open the left shaft south of369 |
| `GUEST_L2_CORRIDOR_FLOOR` | Right approach reaches the actual upper-flight endY382; the left opening starts369; split shared faces without duplicate finish |
| North L1 floor/vestibule | Preserve all real northern doors; right flight meetsY350 and a separate left paved approach reaches369 |
| Flat front terrace | Split into W1, lower middle plane, W2 and retained eastern0 plane |
| Existing B1 landing/door | Door station(285,365.835) and−2.36 datum retained; landing remains connected to the first lower riser at368 |

The walking skeleton is continuous in this numerical design:

1. Main connector reaches low service arrival(305,423,−1.18). Northward, the low return atY412.3 connects down the left flight to B1 and up the right flight to the unchanged northern L1 foyer.
2. In that foyer, pass north around the central divider at approximatelyY342.5, then along the left paved approach to the upper left flight. Cross the upper south return atY412.3 and ascend the right flight to the upper hall atY382. At L2, cross north of its divider/opening aroundY364 to the bedrooms. Neither crossover is a straight segment through the central masonry.
3. From the low service arrival, continue south to the front walk, ascend W1, traverse the middle front plane, ascend W2, and reach the eastern0 terrace. Existing eastern Guest Room→Gallery→Lounge connections provide the current source-supported room access skeleton.

The main connector must actually meet the new low arrival: its guest endpoint becomes worldZ**7.22**, with the main endpoint fixed at5.26415. The JSON gives all ten existing XY controls with a monotonic rescaling of their current C walking heights. This preserves the plan and upward direction and avoids a1.18m endpoint drop. It does **not** move the guest datum, north rooms, or printed storey height. No automatic canopy-roof relocation is proposed: its existing envelope sits above the lowered walking profile. Supports, ground interface and exact steps need real candidate checks.

## Headroom, wall joins and negative controls

The numerical probe evaluates exact overlaps between constant-height tread/landing rectangles and overhead surfaces with a0.18m disk along the path centerline. Treads are assumed.13m and landing slabs.21m. These are C construction envelopes, not mesh rays. The current guest circulation slabs have no extra cork finish layered over their datum; bathrooms are separate.

| Critical region | Minimum available headroom m |
|---|---:|
| Lower left first tread beneath L1 north approach | **2.002500** |
| Lower right/south route beneath upper works | **2.290175** |
| Upper left first tread beneath L2 north cap/plate | **1.961700** |
| Low return directly beneath upper middle platform | **2.417800** |

The upper north-cap case retains only**11.7mm** reserve. Combined slab/downward finish must be≤.2217m there. SourceY369..372.6 is a drawn frame/cap band, not an established empty strip at the proposed lower elevation. Its identity must be checked in a separate candidate; the nominal visible-only upper run still misses the.25m going screen. No tolerance was silently relaxed.

The actual existing basement retaining wall also matters. Its measured inner plane worldX2.1627 corresponds to sourceX301.4593, inside the nominal upper-left raster width at lower heights. Keep its XY and the printed2′5″ finished-gap control. Use the source-aligned path centerX296.75: the .18m body envelope stays **67.52mm** west of that wall. The available upper-left width below its existing C top is approximately**.65486m**, exceeding.36m; tread construction must trim/merge into the wall face, not claim the full.81468m raster width is clear. The lower tread proposal is.70m wide inside the previously measured minimum finished gap.720369m. Actual model joins/finished protrusions remain a required mesh check.

The old faces are explicit failing controls:

- Low return−1.18 under the old L1 south slab: only**.96m** headroom.
- Upper return1.4478 under the old L2 south slab: only**.694875m**.
- Keeping the old L1 south walkway under the new upper return: only**1.2378m**.
- Keeping the old west L2 strip above the second upper-left tread: **1.800725m**.

The design depends on removing those incorrectly assigned full planes, not on weakening headroom checks.

## Specific gates before a separate model candidate is accepted

**West Lounge opening:** the current model labels the leafless west gap a door at0. The native plan in that position resembles continuous corner glazing; this review does not establish a walk-through door. Do not use it as a candidate walking edge and do not add an unmarked1.18m stair or lower the entire Lounge to make it connect. Use the existing eastern room connections for now. Before any production opening/adjacency update, establish its facade identity. If it is a real door, this candidate has not yet supplied its source-supported approach; an unguarded door over the new drop cannot be accepted.

**Measured line residuals:** south-elevation visible riser intervals are approximately.154–.159m, **6.7–11.3mm above** the selected.1475. Their first edge is above MAIN0, so those visible lines are not assumed to span exactly−1.18→0. This is a retained C/U projection discrepancy, not a direct fit. The underground lowest line is approximately−1.89 with unresolved finish/footing identity; the preserved B1−2.36 is **.46962m lower**, and remains explicitly provisional. Neither discrepancy is erased from the JSON.

**Bounded next validation:** build only a separate candidate after root authorizes it; check the six flights, all three northern entrances and both midlandings with real finished meshes, .18m bodies and1.95m headroom; verify the north cap and retaining-wall joins; prove no old flat faces remain through the well; verify actual east-door/Gallery/Lounge access; then check the lowered connector against support/terrain/canopy. Full adjacency and integer-frame tour tests follow that geometry, not this numerical screen. Current09 production and earlier failed evidence remain untouched.

This study selects a workable C skeleton and exact face/route actions instead of merely listing unknowns. It does not elevate approximate planes/counts to A or claim final physical/visual acceptance. Documentation reconciliation is limited to this task's JSON, probe/log and report; shared production, STATUS and AGENTS were not edited.
