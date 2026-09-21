# Forest canopy11a — one bounded candidate

Source: `scene/Fallingwater_bridge10_endfix.blend`, SHA256 `2a7630b8024c37bd768e563236807f8049469172c7e44b03379a450f91637063`. This is the accepted bridge-only endfix with the original old animated water, not the rejected watertrim or native-fluid diagnostic display. Scene comparisons use frame48. Production site/config/assets library are not edited.

## Actual viewing and diagnosis

Actually opened: `renders/previews/water10-native-frame24/CAM_WATER10_NATIVE_OVERVIEW.png`, both `renders/previews/bridge10-endfix/CAM_HERO.png` and `CAM_WATER_DETAIL.png`, HABS `data/photo_refs/main_sw_87.jpg`/`main_east_88.jpg`, and Columbia `qa/bridge-source10-columbia-0.jpg`. The HABS and Columbia trees are mainly leaf-off deciduous plants with evergreen understory. They support branch structure and retained trunks, but cannot be used as summer leaf-area targets.

Two official photographs were also opened at their native1920×1080 resolution. [Classic Spring](https://fallingwater.org/wp-content/uploads/2021/03/FW_ZOOM_Classic-View_SPRING.jpg) shows uneven, overlapping groups of small leaves along forked lateral branches around a still-readable building. [East Spring](https://fallingwater.org/wp-content/uploads/2021/03/FW_ZOOM_East-Elevation_SPRING.jpg) includes much bare upper branching and fresh leaf-out. Both come from the [Fallingwater virtual-background page](https://fallingwater.org/virtual-backgrounds/); exact capture date is unverified. These are local reference-only QA evidence, excluded from public packages and never scene textures. Paths, source URLs, SHA256 and independent viewing records are in `forest-canopy11-sources.json`.

The [reserve manager](https://waterlandlife.org/land-conservation/explore-our-preserves/bear-run-nature-reserve/) identifies mature deciduous/hemlock forest and several dominant broadleaf species. That supports broadleaf growth-form candidates, not exact species, exact leaf count or individual root placement. Those remain C, with species U at the selected roots.

Saved assets really contain many separate leaves: mature asset0 has15,552 blades/93,312 leaf triangles/148.565m² one-sided modeled leaf area; small assets7/8 have2,880/4,320 blades and26.954/40.276m². Asset0 leaf bounds span about12.12×12.40×10.30m;7/8 span5.40×6.84×3.36m and6.45×5.92×4.69m. The simple ratio to the XY bounds is about.99/.73/1.06 respectively. These are mesh statistics, not surveyed LAI or ecological density.

The visible problem is spatial distribution: existing leaves lie in thin separated terminal fans, with large gaps between them; foliage clumps often read as horizontal tiers or sparse umbrellas. Merely scaling each blade would enlarge the already11–19cm leaves and alter the crown outline. The saved green material already has three leaf tones, vein bump and a translucent component; there is no evidence of missing material assignment requiring a color replacement. Smooth bare trunks and sparse global planting remain limitations, but this task explicitly freezes trunk geometry and root count.

## Single intervention

Only assets0/7/8 are copied. Eighteen existing tree roots (six mature and twelve saplings) keep all matrices, names and old geometry;36 branch/leaf object `data` pointers are the only permitted original-object mutations. Original assets remain unmodified and shared by every other instance. No spheres, foliage volumes, new tree objects, moved roots, enlarged tree height, texture changes or lighting changes are used.

At each original terminal twig, up to two short authored side shoots are attached to the actual old woody surface. Mature shoots are.40–.67m; sapling shoots.30–.52m. Each carries eight separate folded broadleaf blades, mature.115–.18m and sapling.105–.165m long. Blades start on the real tapered shoot face, with alternating placement and differing inclinations. New wood is12 triangles per shoot and foliage48, so the maximum added budget is60 triangles per eight-leaf group before constraint pruning. All original vertices and faces are preserved verbatim.

Every added group must lie inside the original leaf XYZ extrema and its full convex-hull envelope. The hull is only an invisible computation constraint; it is not created as a scene object. Local additions stay within one short shoot length of an existing terminal branch. The unchanged source geometry sets the overall tree height and crown outline. The proposal intentionally changes leaf coverage inside that envelope, not exact source leaf triangles/collision surfaces.

The same copied asset is shared by all selected instances of its index. If any selected instance violates hard-object, terrain, route, camera or protected-house sightline constraints, remove that whole new group from that asset for all selected instances; do not move a root or protected object. The deterministic pruning only removes proposed groups, never generates another random variant or alters the density target to chase a render.

## Physical acceptance scope

Fresh scene fingerprints protect every non-target object, original shared mesh, material, world, light, camera, render setting and embedded configuration. Original core/shoulder/water/path/bridge evaluated triangles are separately hashed. Check each retained leaf base to the actual final woody mesh; new above-ground vertices and triangle intersections against actual terrain; the frozen full09 route;0.40m clearance around all129 existing camera positions; and64×36 MAIN-hit rays from each of the three comparison views. The latter is a sampled conservative sightline regression, not proof that every pixel of the building is unchanged.

The root-contact check reports the existing root-to-terrain gap rather than reseating trees. Because all original wood and object matrices are byte-equivalent, any pre-existing root geometry issue is preserved and not falsely reported as newly fixed. No final visual or global forest-density acceptance follows from these physical checks.

## Parent comparison views

Use identical settings on source2a and candidate11a, frame48. First: native overview target(−4,−5.5,−6.325), eye=target+normalize(−1,−1.4,1)×45,40mm. Second: bridge south approach eye(27.45,−10.5,1.8), target(27.45,2,.25),28mm. Third: saved `CAM_MAIN_L1_LOGGIA_B`. These QA cameras are only specified in the report; this agent does not modify source cameras or render. Root determines local visual adoption after opening the three paired images.
