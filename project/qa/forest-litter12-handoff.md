# Forest litter12a handoff

**Independent candidate; visual status NOT_RUN, not production installation.**
Root owns same-camera rendering and the later decision to integrate. Soil11a
has local directional acceptance only (`forest-floor11-root-visual.md`), and
this layer does not change that image judgment by itself.

**Local physical gates complete:**656,269 saved vertex/face-center samples,
0 contact/exclusion failures under the recorded tolerances; three site paths,
2,829 standing positions and113,160 rays,0 new obstruction. The final machine
entry point is `forest-litter12-final.json`. Independent Blender processes
exited0; there has been no render or production application.

Source `scene/Fallingwater_forest_floor_candidate11a.blend`, SHA256
`5bc4e480237bfa202b205370aea647e4501797ec46e8e335b5106f4ca9fc1d27`.
Candidate `scene/Fallingwater_forest_litter_candidate12a.blend`, SHA256
`5fed8ce2d7513565ce978af32f494c74ae40e09c101e18ce8578e56b0b1bcdb9`.

## Actual additions and independent application

`scripts/forest_litter12.py: apply(scene=None, max_leaves=24000,
max_ferns=40, max_twigs=65) -> manifest` adds a single named collection with
**31 new objects**: one24,000-leaf aggregate, one65-twig aggregate and29 rooted
fern clumps. It refuses duplicate installation. All additions use LITTER12
names, so their geometry and material layer can be isolated from terrain11a.
The helper does not require, modify or reapply a terrain shader; on a future
combined source it reads that scene's actual terrain, paths and nearby solids.

The leaf aggregate has312,000 vertices/288,000 triangles. Blades are
65–145mm long, with twelve uneven outline points and a folded/curled center.
The total leaf surface area is118.002m² **before overlap**, not an asserted
pixel/ground coverage fraction. Leaves form unequal contour-related windrows
and are thinned on steep ground. There is no horizontal soil-cover sheet.

The actual fern count is29 because further attempted roots/extents failed the
strict bank/contact filters; the40-clump cap was not achieved by relaxing them.
The four existing CC0 fern geometries/materials are shared. Source root
embedding is limited to45mm inside the explicit root region; other frond
points retain the normal1mm penetration threshold. Source package authors,
license, species limits, native dimensions and references are in
`forest-litter12-design.md` and the preserved near-tree-asset07 evidence.

All generation is confined to world X23–40/Y9–19m, based on actual terrain hits
from Loggia/bridge images. The24000-leaf,65-twig and29-fern counts remain C
composition choices, not a site inventory. The old slope shape, existing trees,
water, path edges and buildings are retained. This experiment does not repair
the full valley or claim final environmental realism.

## Evidence and preservation

`forest-litter12-check.json` records every original23,315 object and original
mesh matching the11a source, along with unchanged old material/image settings,
lights, world, actions and cameras. Its manifest records actual root positions,
contour neighborhoods, placement rejections and148 protected nearby objects.
No room footprint intersected this particular bounded rectangle; actual nearby
architecture/stone/water and woody-tree meshes still participate in exclusion.

`forest-litter12-reopen.json` and `forest-litter12-reopen-contacts.json` are the
authoritative saved-geometry checks. Raw first-reopen failure and diagnosis are
retained. They identify only new fern matrix recomposition (maximum element
difference2.459e−7, translations exact), four new-image slash normalizations,
derived new-fern dimension differences at most1.193e−7m from the same matrix
recomposition,
and three pre-existing **zero-user** legacy grass image IDs omitted on save.
Active FLOOR11 copies still use the exact same intact texture files. Those
three IDs are checked as zero-user in the source before permitting cleanup.
No original object transform or physical threshold is normalized away.

The readback samples new saved vertices and polygon centers against the actual
terrain, path polygons with230mm margin, room footprints and protected mesh
contact. A separate `forest-litter12-pathcheck.json` records incremental body
rays over the three real site-path strips. This is local change regression,
not the full adjacency7584-frame audit on a future merged scene.

## Same-view comparison

Use `qa/forest-litter12-camera-settings.json` on both11a and12a, explicit
frame48,1280×720,48 samples,Cycles CPU—the conditions of the actual11a renders.
It duplicates the frozen11a/canopy camera overlay byte-for-byte and is not
installed in any saved source camera.

| Existing camera name reused | Purpose / exposure |
|---|---|
| CAM_HERO | Bridge approach; floor-layer continuity on the north-facing bank;0EV |
| CAM_MAIN_L1_LOGGIA_B | Close left slope; curled leaves, low fronds, clear road edge;+.8EV |
| CAM_WATER_DETAIL | Overview control; additions are restricted to the bridge/Loggia rectangle, not a full-valley treatment;+.8EV |

Check for irregular readable patches, plausible leaf scale/curl, fern roots
seated in soil, no obvious repetitive plant pairs, no dark continuous blanket
or carpet of evenly spaced dots, and no path intrusion. Sparse tall understory
and large smooth slope silhouettes remain separate constraints. This agent has
not rendered or installed the layer and has not changed scene lighting/exposure.

Scoped neat-freak: the new design and this handoff reconcile the prior11a visual
status and preserve07b/08 negative studies. Root README/AGENTS remain accurate
about incomplete delivery. Central STATUS/START_HERE, production asset manifest
and global agent memory/settings remain with their owners; no parallel agent
edits have been reverted.
