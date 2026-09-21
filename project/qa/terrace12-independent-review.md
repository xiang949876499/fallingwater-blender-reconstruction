# Independent review of terrace interface candidate 12a

**FAIL for the promised zero intersection and unchanged exterior union.** The large duplicate facade faces are removed and structural walking support is retained. The remaining failures are small, measured differences caused by subtracting raw wall boxes instead of the evaluated 55 mm bevelled wall. This report is frozen for 12a and must not be overwritten by a later candidate's result.

Read-only source: `scene/Fallingwater_navigation_candidate11a.blend`, SHA256 `d66ded0f23b7d19c20b81d2f59f94aa5aa77747be4568e85e1d105395fc219ff`.

Read-only candidate: `scene/Fallingwater_terrace_interface_candidate12a.blend`, SHA256 `0499c4594e4143ebc8ae28735417ae17765e1ffdafe20285903f654768958fa1`.

| Independent check | West | South |
|---|---:|---:|
| Closed mesh, every edge degree 2, no degenerate triangles, positive volume | PASS | PASS |
| New slab actual volume, m³ | 9.36973736923004 | 13.920962961513023 |
| Actual residual solid intersection with bevelled parapet, m³ | **0.0003083630199207814** | **0.00030835611168881187** |
| Lost slab + parapet exterior union, m³ | **0.0011086166642633177** | **0.0014556261449911734** |
| Finish support locations, including 0.1 mm inset boundaries | 2,651 | 3,358 |
| Introduced unsupported locations at four structure elevations | 0 | 0 |

The intersection is about 0.308 litres per terrace, located at the two concave inside corners of each L/U-shaped parapet. For example, `(-13.064549675,12.757800827,2.83)` and `(-0.341600170,-2.047099819,2.83)` are inside both their new slab and their unchanged parapet. Three non-axis-aligned ray directions independently confirm each point; the closest exit distance from the intersecting solids is approximately 8.640 mm.

Exterior concrete was also removed at the bottom arris and convex corners. The west witness `(-7.651399685,17.870326447,2.625)` and south witness `(7.160749840,6.477199959,2.625)` are inside the old slab but outside both new solids, approximately 22.876 mm from the actual wall surface. This is a **sampled local shortest distance**, not a bound on every possible deviation. A normal facade ray at `(-14.29455,13.329329,2.625)` towards +X moves inward 1.989 mm; at Z 2.630 it moves 0.995 mm. Some near-tangent rays miss an entire bevelled strip and next hit geometry metres away; those long chord differences are retained in the raw evidence and are not represented as local concrete recession.

The direct exterior-face survey has 210 stations: 140 old slab/parapet hit pairs were coincident within 10 microns; 0 new pairs are coincident. This is sampled confirmation that the large black-band-producing duplicate faces were removed, not proof that the remaining intersecting corner solids are acceptable. The source image `renders/previews/integration11a/CAM_HERO.png` was actually opened. No image was rendered during this review; parent owns visual acceptance.

All four printed dimension identities were remeasured using actual evaluated opposing faces in both scenes: **4 PASS / 0 FAIL / 0 NOT_RUN** each. These are four anchors, not 72 independent dimensions. The existing nominal/source precision and C registration limitations in `dimension_supplement12.py` remain unchanged.

The complete scene fingerprint comparison found exactly the two intended slab mesh replacements, their matching custom properties and derived extents, plus the intended scene marker. The other **23,432 objects**, materials, image references, lights, world/render settings, cameras, and action keyframes are identical. Object count remains 23,434. Both slabs have empty modifier stacks; the unchanged parapets retain their 55 mm bevel modifiers. Source/candidate file hashes remain unchanged. Neither scene was saved or mutated by the review.

## Methods and evidence

- `terrace12-independent-extract.py` / `-extract.json`: actual evaluated geometry, all-scene state comparison, 210 paired exterior stations, and frozen four-anchor measurement. The repair helper and its construction boxes were not imported.
- `terrace12-independent-volume.py` / `-volume.json`: partitions each axis-aligned slab at its actual evaluated vertex coordinates. Cell sums reproduce signed mesh volume. Each unchanged evaluated wall is integrated as signed tetrahedra clipped to those independently derived cells. Four analytic tetrahedron clipping tests and full-wall clipped-vs-mesh-volume checks pass. Arithmetic uses double precision and 1e-8 m³ numerical tolerance; measured failures are orders of magnitude larger. This does not substitute a broad nominal dimension tolerance for zero intersection.
- `terrace12-independent-witness.py` / `-witness.json`: actual BVH point and ray witnesses, corner profiles and 24,036 structure-level samples below 6,009 walkable finish positions. Five finish samples occupied by the parapet above were explicitly excluded from walking support, not silently counted as passed.
- `terrace12-independent-witness-attempt01.log`: preserved QA implementation failure. Advancing a float32 BVH ray by 1 micron at world Y≈18 m rounded onto the same face. The corrected advance is 0.1 mm, below each witness clearance; all final three-direction classifications agree. No scene geometry was changed to fix the checker.

The scope remains the two local slab/parapet interfaces. No whole-building navigation rerun or final environment/film acceptance is claimed. Scoped documentation cleanup retained all negative evidence and changed only these review files; shared project guidance and production modules remain untouched.
