# Independent terrace12b review — local interface accepted with measured residual

**Engineering conclusion: PASS for this bounded structural/interface correction, with the small residual below recorded explicitly. This is not mathematical exact-zero.** Candidate12a retains its independent FAIL report. No further geometry iteration is required for the residual in12b; the integrator made that decision after receiving its measured size. The reviewer also actually opened the integrator's `renders/previews/terrace-interface12b/CAM_HERO.png` and the earlier `renders/previews/integration11a/CAM_HERO.png`: the conspicuous black horizontal band is gone in the same camera view. This is local visual acceptance, not acceptance of the entire exterior environment. All rendering was performed by the integrator.

Baseline: `scene/Fallingwater_navigation_candidate11a.blend`, SHA256 `d66ded0f23b7d19c20b81d2f59f94aa5aa77747be4568e85e1d105395fc219ff`.

Reviewed candidate: `scene/Fallingwater_terrace_interface_candidate12b.blend`, SHA256 `285ea6d0c29b0ff483fb6f582c644f5286b23e83f1d894bedf32546fbca3a14c`.

| Actual evaluated-mesh result | West slab | South slab |
|---|---:|---:|
| Vertices / triangles | 187 / 370 | 175 / 350 |
| Actual volume, m³ | 9.37053756141235 | 13.922110137801118 |
| Closed, consistently oriented edges / positive connected volume | PASS | PASS |
| Degenerate triangles / retained modifiers | 0 / none | 0 / none |
| New empty material slots | 0 | 0 |
| Original same-direction coplanar face area, m² | 4.096565806041216 | 5.300229936367413 |
| New same-direction coplanar face area, m² | **0 detected** | **0 detected** |
| Residual slab/parapet intersection, m³ | 1.2082300532528266e-7 | 6.457162773217363e-8 |
| Intersection with swapped clipping order and shifted origin, m³ | 1.2072295729162536e-7 | 6.297194804710592e-8 |
| Lost slab + parapet union, m³ | 1.8228503506634297e-7 | 1.583168369734267e-7 |
| Maximum sampled mating-surface distance, mm | **0.0508679173** | **0.0508609946** |
| Maximum sampled signed penetration, mm | 0.000736678 | 0.000284774 |
| Old12a negative witnesses now corrected | 10 / 10 | 10 / 10 |
| Actual finish positions / structure-level occupancy samples | 2,651 / 10,604 | 3,358 / 13,432 |
| Introduced unsupported finish locations | **0** | **0** |

The two true12a corner intersections of approximately0.308 litres each and their8.64mm interior witnesses are gone. The remaining integrated intersection is about0.121/0.065 millilitres. Changing the integration order and subtracting a local coordinate origin changes that result by only about1.00e-10/1.60e-9m³. Therefore the small positive values are retained as a finite-mesh residual, not asserted to equal zero. The strict1e-8m³ literal-zero checks remain FAIL in `terrace12-independent-12b-volume.json`; they have not been relabelled or hidden by a dimension tolerance. Engineering acceptance here is a separate, explicitly limited conclusion.

The maximum sampled positive separation is approximately50.87 microns at a three-dimensional lower bevel corner. West example: slab triangle230 at `(-13.265245676,17.862368107,2.627350032)`, closest actual wall triangle164 at `(-13.265217463,17.862326747,2.627359029)`. South: slab triangle228 at `(6.951053977,6.469241023,2.627350032)`, closest wall triangle332. These discrepancies are larger than the maximum coordinate ULP (west1.907 microns; south0.477 microns), so the gap is **not described as pure float32 coordinate rounding**. Its location and the use of nonplanar bevel polygons in the Boolean cutter are consistent with a difference in surface triangulation; that explanation is an inference, not a separately proven Blender implementation claim.

The boundary survey measures2,250 west and2,475 south actual samples, using15 barycentric positions per identified matching triangle. Its maximum is a **sampled point-to-triangle distance**, not an exact continuous Hausdorff bound. No normal, height, body-clearance, or printed-dimension standard was changed to obtain this result. The approximately0.051mm local triangulation seam is retained in this acceptance record and does not constitute a whole-house quality or navigation claim.

## Exposed surfaces and support

The area check clips actual evaluated loop triangles against one another. It reports same-direction coplanar intersections above1e-12m², with1e-8m plane-matching tolerance. The old duplicate exterior area was approximately9.3968m² in total; no new pair meets those conditions. Opposite-facing surfaces that mate internally are distinguished from duplicate outward surfaces. Twenty-eight equal-distance profile ray pairs in the initial210-station survey are exactly atZ2.635, where the bottom bevel meets its neighbouring surface. They are shared seam-line hits; the actual triangle area test finds no exposed area duplication there. A zero-width edge hit is not the previous black band.

All20 preserved12a defect points were checked against all evaluated triangles in double precision, with three independent ray directions. Every old overlap point is now outside the slab and inside the unchanged wall; every old lost-union point is now inside the new slab and outside the wall. Below6,009 actual walkable finish positions,24,036 structure-level samples have no newly missing occupancy. Five points occupied by the parapet above the finish were explicitly excluded from walking-floor support. The slab top/bottom elevations, finish surfaces, door thresholds and parapets remain unchanged.

## Scene and dimension protection

Full saved-scene fingerprints compare23,434 objects. The other23,432 objects, all material slots and material node trees, images, cameras, lights, world/render settings and action keyframes are identical. Only the two intended existing slab mesh datablocks and their new custom markers, plus the scene marker, differ. The extraction's initial generic12a whitelist lists the three `terrace12b_slab_interface` markers as unmatched; they were individually reviewed as the three expected12b markers, not an undisclosed object/material mutation. The raw extraction is retained rather than rewritten to conceal this review step.

Both source files remain byte-identical to the stated hashes. This reviewer did not invoke either repair helper, save a scene, edit production code, render an image, or change the working file.

`dimension_supplement12.measure(scene)` was run separately in both frozen scenes: **4 PASS / 0 FAIL / 0 NOT_RUN** for each. These remain four independent printed source identities, not72 dimensions. All printed-unit/source-reading/C-registration limitations are unchanged. Do not duplicate an existing central bridge anchor when aggregating the four results.

## Reproducible evidence and checker limits

- `terrace12-independent-12b-extract.json`, its before/after extraction and geometry files: hashes, whole-scene differences, actual geometry and all four dimensions.
- `terrace12-independent-12b-volume.py` / `.json`: signed tetrahedron clipping for the non-orthogonal actual meshes, analytic clipping tests, numerical volumes and deliberately retained strict literal-zero failures.
- `terrace12-independent-12b-precision.py` / `.json`: same-direction face area and swapped/local-origin intersection calculation.
- `terrace12-independent-12b-boundary.py` / `.json`: authoritative double-precision all-triangle point classification, old defect regression, actual boundary residuals and all24,036 support samples.
- `terrace12-independent-12b-witness*.json`: provisional BVH exploration, retained for traceability. Its nearest-face normal-sign candidate counts are **not confirmed solid-intersection counts**: the closest point may lie at the edge of a very thin matching wedge. Its iterative ray advance can also skip thin wedges. Final classifications come from the double-precision all-triangle boundary report, which does not advance a ray origin and does not use an arbitrary nearest-face normal to classify inside/outside. The first n-gon exploration is preserved as `-witness-ngon-attempt01.json`, not accepted as scene-failure evidence.
- `terrace12-independent-review.md`: frozen12a FAIL; it is not superseded into a pass by this candidate.

Scoped neat-freak reconciliation retained the rejected candidate and checker attempts, separated literal numerical checks from engineering acceptance, and left shared project guidance and other agents' documentation untouched. No further model or render job was started during finalization.
