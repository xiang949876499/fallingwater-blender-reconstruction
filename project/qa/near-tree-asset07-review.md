# Near-camera forest candidate audit — 2026-09-20

**Decision:** no suitable mature-tree replacement confirmed within the requested official Poly Haven search and 200 MB limit. One small forest-understory candidate, `fern_02` at 2K, is isolated for the site owner. It is not in production and cannot solve the mature canopy by itself.

## Actual current-scene evidence

Opened the actual HERO and WATER_DETAIL PNGs in both `renders/previews/iteration06-geology-baseline/` and `renders/previews/iteration07b-geology-candidate/`. Both show very open, smooth bank surfaces; repeated twig silhouettes and thin-looking crown edges dominate the background. These are observations of the actual project renders, not vendor example imagery.

Read the current `site.py` tree generator and preserved-placement loader, `data/site.json`, and the real authored library `assets/models/site_near_trees.blend` in a separate Blender 5.2.1 CPU4 process. The library is 17,561,826 bytes; its captured SHA256 is in `near-tree-asset07-offline-audit.json`. It contains 18 unique woody/leaf meshes, 600,702 triangles in total. The three detailed near-tree assets total 367,896 triangles and use 15,552 / 15,552 / 20,736 seven-vertex leaves.

**The leaves are not geometrically needles.** Measured stored blades on the three near assets are 0.11–0.19 m long and have shoulder width / blade length 0.585–0.792, averaging approximately 0.689. The displayed thinness should not be answered by blindly widening every leaf. The code repeatedly places paired leaves along similar straight twigs; all blades share one six-triangle outline and three procedural color variants. Three near-tree assets repeat throughout the preserved near placements. This supports a diagnosis of repetitive leaf fans, twig spacing and sparse crown coverage; density, shading and actual camera projection still need a controlled render comparison to apportion their effects.

Suggested future canopy work for the owner: preserve trunk positions, major branch shapes and building/path exclusions; test irregular groups of shorter/longer shoots, break paired leaf alignment, vary leaf orientation and local crown density, and preserve readable voids. This is a C-level form study, not a species or individual-tree survey claim. No tree geometry was changed during this audit.

## Official source check — two detailed candidates only

The official model inventory returned 521 assets. Its Broadleaf Trees category contained `jacaranda_tree` and `tree_small_02`; the latter is explicitly tagged Burkea africana / wild syringa / small. The existing project's documented vegetation list names tulip tree, red maple, chestnut oak, American beech, sugar maple and black cherry, with hemlock forest (`research/interiors.md:99`). Neither catalogue name provides a matching mature-tree identity. No botanical equivalence was invented.

| Detailed candidate | Official metadata | Exact Blend + included PBR bytes | Decision |
|---|---|---:|---|
| [Jacaranda Tree](https://polyhaven.com/a/jacaranda_tree) | 312,356 API polycount; LODs and geometry nodes flagged. API dimensions correspond to approximately 24.17 × 18.03 × 19.83 m. Actual evaluated/LOD mesh counts unknown, since not downloaded. | 1K: 213,178,295; 2K: 300,042,484 | Not downloaded. Smallest complete Blend package already exceeds 200,000,000 bytes; identity is not supported by the project's forest evidence. |
| [Fern 02](https://polyhaven.com/a/fern_02) | Four low plants; API polycount 6,232. No botanical species specified. | 2K: **5,283,047** (five files). 1K: 1,760,325; 4K: 17,074,594. | Isolated C-level understory form candidate; species remains U. |

[Poly Haven's asset licence](https://polyhaven.com/license) identifies downloadable models/textures as CC0. [Official API terms](https://github.com/Poly-Haven/Public-API/blob/master/ToS.md) permit data and asset access with an identifying user agent. Requests used `Fallingwater-research/1.0`; source manifests and endpoint documentation are saved in the adjacent `near-tree-asset07-*-info/files.json` and `near-tree-asset07-api-docs.json`. The API is public and no login, payment, account, configuration or external write was used.

## Preview status: NOT_VIEWED

The official asset page and its Preview/Clay links were opened with the web tool. The tool returned image URLs but no inspectable image pixels; the fern clay fetch also timed out. The in-app browser was unavailable, and the browser inventory was empty. Therefore vendor preview inspection remains **NOT_VIEWED_TOOL_UNAVAILABLE**. Example images were not downloaded as a workaround and are not treated as evidence that the downloaded mesh renders correctly. The offline mesh/material audit below is independent of those previews. The site owner has been told that an actual project render is still required.

## Download and offline checks

Candidate folder: `assets/candidates/fern_02_2k/`. Only the official 2K Blend file and its four declared dependencies were downloaded. All five exact byte counts and official MD5 checks pass; all five local SHA256 values are recorded in `near-tree-asset07-download.json`.

Blend SHA256: `cf721e00ed5bb72f0b9c3fb59b8febc7b2b9b2082f162d5a80ba3a11e4e7028d`.

| Append object | Mesh | Vertices | Triangles | Dimensions X × Y × Z, m | Local minimum Z, m |
|---|---|---:|---:|---|---:|
| `fern_02_a` | `Plane.006` | 525 | 784 | 0.552 × 0.613 × 0.287 | -0.028774 |
| `fern_02_b` | `Plane.024` | 1590 | 2384 | 0.990 × 0.894 × 0.428 | -0.030510 |
| `fern_02_c` | `Plane.044` | 1500 | 2248 | 0.874 × 0.765 × 0.349 | -0.028774 |
| `fern_02_d` | `Plane.059` | 545 | 816 | 0.573 × 0.593 × 0.213 | -0.013579 |

All four meshes have UVs, unit object scale, no modifiers, no native LOD collection, and no embedded text blocks. The four originals are laid out on an approximately 1 m presentation grid, so their source object XY must be replaced with actual placements. Their roots are not proven by the bounding box; preserve the slight below-origin stem allowance and perform root-region terrain ray tests before acceptance.

The one shared material `fern_02` has working relative paths to all four 2048² images: sRGB diffuse JPG, Non-Color normal/roughness EXRs and alpha PNG. The material connects the normal, roughness and alpha maps, and includes a translucent shader. Alpha-edge quality, backlighting and render noise are **NOT_RUN**, because this audit performs no rendering or baking.

## Concrete import and LOD/budget proposal

Append the four objects once into an isolated candidate collection, retain their shared mesh/material/image data, and create **12–24 linked clumps** in a few existing near-bank bare pockets. The site owner should test root contact, slope, creek/road/building exclusions and camera occlusion against the actual scene BVH. Use bounded 0.8–1.2 uniform scaling and differing orientation; avoid making a field of equally spaced ferns. Do not change the mature-tree count or turn this ground plant into a tree crown.

At this scale no mesh decimation is justified: all 24 instances of the heaviest variant would total only **57,216 submitted triangles**, while shared unique geometry remains 6,232 triangles / 4,160 vertices. Keep the full meshes within the tested near-bank patch. For a later larger distribution, use a/d (≤816 triangles each) for the middle distance and cull the tiny projected clumps beyond it; those are native shape variants, **not vendor LODs**. Any temporal LOD transition needs a fly-through check. Do not decimate alpha-cutout leaf edges before such a check.

Memory budget is not the 5.28 MB download size. The loaded Blender image flags show three RGBA float buffers and one RGBA byte buffer: a simple decoded-buffer model is `3 × 2048² × 16 + 2048² × 4 = 208 MiB`, or about **277.3 MiB including a full mip chain**. A positions/normals/UV plus triangle-index geometry proxy is about 0.20 MiB; it excludes Blender data, corner attributes and acceleration structures. Reserve **0.4 GiB incremental headroom as a planning limit for this one shared asset**, not a measured VRAM claim. Actual GPU formats, BVH allocation, peak CPU/GPU usage and frame rate remain unknown. Linked copies should share the images; making materials/textures single-user per clump would defeat this budget.

## Handoff and scope

`site_visual` received exact object names, hashes, dimensions, source presentation offsets and negative local Z values, and owns any independent placement candidate. The root agent owns visual validation and production integration. This audit changed no `site.py`, production manifest, `.blend` working scene, guest structure or global settings. No render/bake was run. Notes and manifest were reconciled as the scoped neat-freak handoff; project-level status and README remain with the root owner.
