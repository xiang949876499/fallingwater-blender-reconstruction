# Iteration04 route audit

The immutable iteration04 scene was loaded with four CPU threads. The source SHA-256 is `247d20f7863e4f7e9c18587d4c032bd663857a420bcfb828d271195665841ac2`. Neither the working scene nor the iteration04 source was saved over. The third-round tour scene and evidence were retained before creating the new tour checkpoint.

The 120-second main film has 10 mesh-tested segments, including a 36-second exterior flight. Forty-nine supplemental inspection segments preserve coverage of all 60 space records. All 7,584 delivered integer-frame camera positions were checked after reopening the saved scene; maximum route-position error was 0.000004371 m, with valid nonzero quaternion values, linear interpolation and no collapsed waypoint frames. This is camera/geometry evidence, not rendered appearance or GUI navigation acceptance.

Full adjacency result: **47 PASS / 5 FAIL / 9 requiring further traversal or inspection-type validation** across 61 deduplicated declared edges. Stair-space anchors use actual endpoint tread centers within their declared polygons, avoiding a false assumption that an entire stair room has one flat floor. The initial 43/9/9 result is retained in `tour-path-all-adjacency-iteration04-initial.json`.

| Failed declared edge | Actual finding | Corrective owner / boundary |
|---|---|---|
| Basement stair → wine | The current west gap begins at unsupported ground. Source-plan review identifies the true internal north passage instead. | Main architecture: reconstruct the documented internal passage, without inventing an outdoor west platform. |
| Main guest bedroom → guest bath | Actual east bath door endpoints belong to BathG and Hall. A C toilet also occupied its inner body clearance. | Main architecture: source-confirmed Hall↔BathG relation. Furnishings: toilet reoriented against northeast wall; in-memory rebuild gives a door-core PASS, pending05. |
| North terrace → exterior upper connector | Actual north-low curved stair endpoint does not meet the terrace; failed point has terrain about0.295m below even a flat terrace datum. | Main architecture: source review found stair rise direction reversed; rebuild correct source geometry and recheck both landings. |
| Guest stair hall → chauffeur lounge | Door core intersects the stone chimney; its hall-side endpoint also lacks floor. | Guest architecture: correct chimney/entry landing from the source plan. |
| Guest upper hall → north bedroom | Current04 opening is positioned opposite Bath, with a C wardrobe inside its approach. | Guest source review confirms the real door farther south directly to Hall; relocate door and seal the erroneous one. Furnishings moves wardrobe west and desk/chair slightly north. |

Two additional physical defects are retained beneath water-edge tests: the main loggia/pool stair body intersects `SITE_Path_bridge_north_approach`, and the guest coping-ascent step starts within the pool water volume. A dry observation viewpoint cannot erase these defects.

The nine unresolved semantic/traversal cases have explicit plans in `tour-path-inspection-semantics.json`: two cabinet-front inspections, three free-flight foundation-support inspections, three dry water-edge inspections, and one normal multi-flight terrace connection. The candidate observer coordinates come from fourth-round checked cameras, but targets and clearances must be reverified against iteration05. Space counting remains unchanged.

Source furniture corrections are recorded in `data/furnishing-evidence.json`; `interiors-door-clearance-iteration05-precheck.json` preserves the limited in-memory rebuilding test. Main BathG's real door core passed after furniture movement. The erroneous fourth-round guest opening still meets the bath wall after its wardrobe is removed, so that complete doorway test remains FAIL until architecture is rebuilt. No updated-source PASS is substituted into the immutable fourth-round results.
