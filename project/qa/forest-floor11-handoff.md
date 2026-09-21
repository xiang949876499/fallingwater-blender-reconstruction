# Forest floor11a handoff

**One independent material candidate; visual review NOT_RUN / not installed.**
The source and candidate are both preserved. No new recolor variant is planned.

Candidate: `scene/Fallingwater_forest_floor_candidate11a.blend`, SHA256
`5bc4e480237bfa202b205370aea647e4501797ec46e8e335b5106f4ca9fc1d27`.
Source: `scene/Fallingwater_bridge10_endfix.blend`, SHA256
`2a7630b8024c37bd768e563236807f8049469172c7e44b03379a450f91637063`.

## Change and integration interface

`scripts/forest_floor11.py: apply(scene=None) -> manifest` makes a private copy
of the terrain's only material, builds the new shader, and replaces slot0. It
refuses a second application if the candidate material already exists. It
reads path strip vertices and actual bank-stack bounds from the supplied scene;
it has no runtime dependency on QA design data or current mutable site.json.
The only external dependencies are six existing CC0 texture files. No production
script/data/texture or existing mesh has been edited by this helper.

The new material is `FW_ForestFloor11a_C_OrganicZones`: 744 nodes, 17 actual path
segments, 111 grouped bank-stone soft masks. Its JSON custom property contains
the actual world-coordinate masks, all source object names, texture scales,
shading amplitudes and explicit C status. Material details and viewed-reference
interpretations are in `forest-floor11-design.md`; this is not measured site
color, soil moisture or a collision mask.

The original scan is grass/moss/twig/soil, retained at the pre-existing C 2 m
mapping. Partial leaves use the existing 1.26 m scan. Macro variation is 11.76 m,
leaf-patch scale 2.38 m and moisture scale 5.88 m; all use world metre coordinates.
Shading-only bump is 12 mm/.32 and 6 mm/.16. There is no output displacement,
emission, shadow card, new geometry or new terrain attribute.

## Verification scope

`forest-floor11-check.json` records 23,315 compared scene objects. The single
allowed object difference is terrain material slot0. All23,314 other objects,
their meshes, old shared materials/images, lights, camera transforms/exposure,
actions and scene globals are unchanged. The terrain's vertices/edges/face
indices/material indices/smooth flags remain unchanged. The shader output graph
is connected and all six images load with the expected size and color space.

The independent reopen result is in `forest-floor11-reopen.json`. The first
unqualified snapshot assertion failed; exact diagnoses and failed logs are
preserved. Two explicit Blender save operations explain those differences:

1. Six new relative image paths are stored with Windows backslashes. The
   resolved files, image color settings and content hashes are the same.
2. `FW_Continuous_Forest_Floor`, whose only source reference was terrain slot0,
   has zero users after replacement and is not saved. It is not shared with
   another object; its untouched full node graph remains in frozen source.

The corrected reopen compares every remaining property after those two
specified serialization rules. No geometry or shader change was made to
produce that normalization. The original failed assertion is not called a
visual failure or silently removed. `forest-floor11-reopen-real-differences.json`
is the canonical raw JSON comparison; the earlier debug dump also recorded
Python tuple/list representation differences and is not a physical-change list.

## Root's three-view comparison

Use `qa/forest-floor11-camera-settings.json` on **both** 2a source and candidate,
with explicit frame48 and identical resolution/samples. This JSON is byte-for-
byte identical to the forest_canopy11 comparison settings, allowing separate
floor-only and canopy-only judgments. It is an unsaved camera overlay.

| Existing name reused | Comparison pose | Lens / exposure |
|---|---|---|
| CAM_HERO | Bridge south approach, eye (27.45,-10.5,1.8), target (27.45,2,.25) | 28 mm / 0 EV |
| CAM_WATER_DETAIL | Native water overview, eye (-26.61335084,-37.15869118,16.28835084), target (-4,-5.5,-6.325) | 40 mm / +.8 EV |
| CAM_MAIN_L1_LOGGIA_B | Preserve saved source camera and lens | +.8 EV |

Suggested equal conditions: 960×540,32 samples,Cycles CPU,frame48. This agent
has not rendered these images or changed saved camera settings. Root should
check whether the pale green carpet breaks into plausible soil/moss/litter,
whether the damp bank edge forms an artificial halo, whether warm ground is
too dark, and whether patch boundaries are visible. Large slope geometry,
tree/shrub silhouettes and overall photorealism remain separate limitations.

Scoped neat-freak reconciliation: root README/AGENTS and the relevant07b/08
negative reports were checked; their incomplete/FAIL scopes remain correct.
This handoff is the new bounded entry point. No root status, agent memory,
global setting or another agent's documentation was modified.
