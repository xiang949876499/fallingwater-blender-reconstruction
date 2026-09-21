# Forest floor11a — one material experiment

This isolated candidate changes only slot0 on
`SITE_Continuous_BearRun_Terrain`, starting from bridge10_endfix SHA256
`2a7630b8024c37bd768e563236807f8049469172c7e44b03379a450f91637063`.
The forest_canopy11 candidate uses the same source but owns different data.
No existing production script, input texture, terrain vertex, root, bank stone,
path, water surface, camera or light is edited by forest_floor11.

## Sources actually viewed this turn

| Local image | Observation and limits |
|---|---|
| assets/textures/forrest_ground_01_diff_2k.jpg | Grass/moss, twigs, earth and small fragments; not a broadleaf-litter scan. It remains the main fine-detail input. |
| assets/textures/leaves_forest_ground_diff_2k.jpg | Overlapping curled broadleaf fragments, pale leaves, orange leaves and dark soil. Only partial patches are used, never a full-field leaf replacement. |
| qa/forest-canopy11-source-official-east.jpg | Dense shrubs/root shade, brown/green vegetation and a separate paved approach; little unobstructed ground available for measurement. |
| qa/forest-canopy11-source-official-classic.jpg | Dense spring vegetation, darker ground between shrubs, wet rock below; vegetation and rock geometry account for much of the appearance. |
| data/photo_refs/main_sw_87.jpg | Persistent exposed bedrock and broadleaf understory, wet dark rock. Historical winter exposure is not a current albedo reference. |
| data/photo_refs/main_east_88.jpg | Layered trunks/understory and dark ground; view and illumination differ from the renderer. |
| renders/previews/water10-native-frame01/CAM_WATER10_NATIVE_OVERVIEW.png | Nearly continuous pale green terrain, sharp tree shadows and evenly dispersed small plants. This is the current failure trigger, not an accepted image. |
| renders/previews/terrain-material08/CAM_MAIN_L1_LOGGIA_B.png | Full-field leaf scan became bright uniform gravel-like speckles. |
| renders/previews/iteration07b-near-terrain/CAM_HERO.png | Gray-treated slope and sparse repeated leaf speckles failed to establish natural ground structure. |

Existing 07b/08 diagnostics, asset review, root visual and negative candidate
reports were read. Their VISUAL_FAIL / NOT_ADOPTED states remain unchanged.
Photographs are reference-only, not shader textures or redistributed assets.
Fallingwater official spring-image rights/provenance remain in
`forest-canopy11-sources.json`; viewing status above is this agent's own record.

The two texture sets are existing Poly Haven CC0 assets. The original grass
scan keeps the existing **C 2.0 m** author mapping. Leaves use the recorded
**1.26 m** manufacturer planar footprint from the prior official API/license
review (`terrain-material08-asset-review.md`). These are not Fallingwater
site scans. No assets were downloaded or original images edited this turn.

## Explicit material choices

The entire material is **C artistic appearance**. No RGB sample from a photo is
called a measured surface color. In particular, no ambient-occlusion node,
emission, baked fake shadow, shadow plane or displacement is added.

- `Geometry.Position` supplies world metres. Macro soil/moss scale is .085/m
  (11.76 m nominal noise scale); partial leaf patches .42/m (2.38 m); moisture
  .17/m (5.88 m). A .23/m vector-noise warp has 2.2 m full amplitude, avoiding
  repeated circles/stripes or normalized whole-object coordinates.
- Warm humus RGB remains chromatic, with retained original scan color/detail;
  moss uses a different chromatic multiply of that scan. The leaf scan is
  damp-brown multiplied and contributes at most .46, suppressed near paths
  and bank stone. This limits the previous full-field pale-leaf speckle failure.
- Path edge weight is a smooth .04–.90 m falloff from 3D centerline capsules
  derived from actual saved strip vertices and half-widths. It increases
  exposed-earth contribution and suppresses moss/litter. It does not alter
  paving or assert an exact pedestrian wear survey.
- Bank proximity uses soft ellipsoids fitted to actual adjacent stone-stack
  bounds, with .85 m added radii. These are explicitly approximate material
  masks, not precise rock-surface distances or collision evidence. The mask
  modulates dampness and thins litter. Actual rock shaders are unchanged.
- Dampness reduces the material's albedo factor toward .55 and roughness by
  at most .16; its spatial amount is C, not a hydrology simulation.
- Original and leaf roughness/height maps retain Non-Color settings. The
  color maps remain sRGB. Each is independently loaded into a new image ID,
  so no shared image setting changes.
- Scan Bump is .012 m Distance / .32 Strength; secondary soil grain is .006 m
  / .16. Both are C shading amplitudes, not measured scan heights. The active
  Material Output has no Displacement link; no silhouette or collision change
  can result from these normal-only nodes.

This single bounded candidate cannot supply missing shrub/rock/root silhouettes
or repair terrain shape. Material graph/dependency and preserved-geometry PASS
must remain separate from root's pending same-camera visual comparison. There
will be no unreviewed sequence of recolor variants or autonomous render here.
