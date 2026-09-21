# Sandstone close-view relief — bounded pilot

2026-09-20. Status: **main and guest fireplace finishes frozen for integration; full scene/photo acceptance remains pending.** Version 2 decorates the corrected guest05 fireplace and retires the old west-wall candidate.

## Evidence and scope

Actually viewed `data/photo_refs/main_living_48.jpg` (HABS PA-5346-48), `data/photo_refs/guest_living_11.jpg` (HABS PA-5346-A-11), and iteration04 HERO/Living B renders. The photographs show long horizontal split-stone courses, occasional thick blocks, staggered short joints and projecting edges. They support the construction's appearance, not our precise stone sizes or bond. All generated dimensions, course sequence, chipped edges and protrusions are **C reconstruction choices**. The photographed Poly Haven stone material remains a generic CC0 surface, not a Fallingwater scan.

The visible iteration04 fireplace had existing relief on its back wall, but smooth large front jamb/lintel boxes. The active module adds shallow finish only to:

- `MAIN_L1_hearth_jamb_n`: front +X and external +Y return.
- `MAIN_L1_hearth_jamb_s`: front +X and external −Y return.
- `MAIN_L1_hearth_lintel`: front +X.

The back-wall courses, hearth, firebox opening, hanging kettle, wall mass, ceiling and furniture are retained. Every surface is clipped 6 mm inside its source U/Z rectangle. The lintel's new front begins above its original opening. There is no underside projection into the firebox.

## Implementation and cost

`scripts/masonry_detail.py` exposes `build(ctx, rooms)`. It can run after structural walls and furnishings. It creates/replaces only objects prefixed `FW_MASONRY_` and writes its own embedded report. It does not change existing meshes, materials or cameras. `data/masonry-detail.json` contains reference, seed and reconstruction choices.

The default call builds both finishes. The corrected guest05 structure must exist first; `guest_house.build()` already calls `guest_architectural_detail`. For independent QA only, `include_main=False` or `include_guest=False` selects one finish. Separate deterministic seeds ensure guest-only geometry matches the integrated build. A changed guest firebox datum or nonrectangular substrate raises a review error rather than applying an old exclusion blindly.

The active main finish is one mesh `FW_MASONRY_MAIN_HEARTH`: **183 stones, 4,941 vertices, 3,843 polygons, zero modifiers**, unit object scale. Uneven front planes and small irregular edge chips are real geometry. There are no per-stone Blender objects and no common rounded bevel. Object-space coordinates remain in metres for the existing material's 2 m photographed texture mapping.

The intended local protrusion range is 5–25 mm; actual generated front vertices range **5.000–23.342 mm** beyond the substrate. The back surface enters the substrate by 0.8 mm to make deliberate solid contact. This small contact overlap is intentional; new stones do not overlap one another.

## Actual validation

The immutable source was `scene/Fallingwater_iteration04.blend`, SHA-256 `247d20f7863e4f7e9c18587d4c032bd663857a420bcfb828d271195665841ac2`. The working blend was not modified.

- 433 relevant pre-existing meshes retained matching transform, visibility, vertices, faces and material-name signatures after the addition.
- The new main mesh has 0 non-manifold edges and positive signed volume 0.117750576 m³.
- 99 finite ray segments across the main firebox found no new obstruction. Another 198 segments across the two guest doors found no obstruction; guest additions were disabled for the accepted pilot.
- All 16,653 pairs of conservative stone bounding boxes are disjoint, including the front/return corners.
- The actual Cycles output `qa/masonry-detail-main.png` was opened and visually inspected. It preserves the firebox and kettle, adds legible horizontal relief to the formerly flat front, and avoids a uniformly rounded brick appearance. The look is still more regular than the reference's large natural splits; this limited 960 px view does not establish final photographic realism.

The main image uses the unchanged `CAM_MAIN_L1_LIVING_B`, exposure +2.4, 960×540, 32 adaptive samples, denoising, CPU with 4 threads; measured render time **73.972 seconds**. Lighting and material colour were not retuned. The independent `qa/masonry-detail-pilot.blend` saves the reviewable scene.

Machine-readable evidence: `masonry-detail-pilot.json`, `masonry-detail-overlap.json`, `masonry-detail-render.json`. Build/render entry point: `masonry-detail-pilot.py`. The source-object diagnostic is `masonry-detail-objects.json`.

## Guest05 finish and actual regression

`guest.enabled` is **true** for the corrected fireplace. The selected faces are `GUEST_FIREPLACE_north_mass` south (−Y), and `GUEST_FIREPLACE_corner_hood` south (−Y) / east (+X). The old `GUEST_L1_WEST_LOUNGE_pier_0` selection code was removed. Its initial, unrendered candidate report remains historical evidence in `masonry-detail-initial-geometry.json`.

The strict firebox exclusion is world X3.631264–4.4512, Y39.567296–40.268472, Z8.60–9.48. Its 2D projection on each finish is expanded by 6 mm. The covered area behind the hearth is also excluded. The north mass finish omits the hood's whole footprint plus its maximum 25 mm finish projection and a 6 mm seam; this prevents the two finishes intersecting at the concave corner. Nothing is added beneath the hood or on the chamber's brick lining.

The guest result is **119 stones in one mesh, 3,213 vertices, 2,499 polygons, zero modifiers**. Actual protrusions are 5.000–22.686 mm. Both finishes total 2 meshes, 302 stones, 8,154 vertices and 6,342 polygons. Main finish vertex/face/transform SHA remained exactly `612849a930d12ab5f359c057755e665021699b841de43cb9818b4fba4754d5d5` after adding the guest implementation; it was not re-rendered.

The guest pilot was built fresh from the frozen guest05 scripts/data, with input hashes in `masonry-detail-guest-pilot.json`; it was not pasted onto the obsolete iteration04 west wall. Actual regression after adding the finish:

| Check | Result |
|---|---|
| Pre-existing guest mesh signatures | 867 unchanged |
| New finish topology | 0 non-manifold edges; positive volume 0.077160446 m³ |
| All 7,021 stone bounds pairs | 0 overlap pairs |
| Strict firebox volume | 0 stone bounds intersections; 242 internal free-volume rays clear |
| Independent structural dimensions, unchanged GEO-02 tolerance | 17 PASS / 0 FAIL / 5 NOT_RUN |
| Existing seven door probes | 7 PASS |
| Basement stair / pool dry stair samples | 42 / 12 PASS |
| Original real firebox checks | 4 PASS: east/south opening rays reach back lining, vertical rays reach hearth/hood |

Two early geometric attempts detected finish intersections at the concave hood/wall join. The final 31 mm local seam reserve removed them. `masonry-detail-guest-rejected-overlap.json` and its log retain the failure evidence.

An additional diagnostic started 40 mm outside the east aperture, only 4 mm from the north back plane. Ten rays hit the adjacent north-wall finish at X4.457–4.487, entirely **outside** the firebox maximum X4.4512. Those exterior approach-edge hits are retained in `masonry-detail-guest-rejected-rays.json`; they are not relabeled PASS or confused with cavity intrusion. The 242 internal probes use endpoints 2 mm inside the specified cavity volume. The author's original four scene-wide cavity tests independently remain PASS.

Exactly one guest image was rendered and actually opened: `qa/masonry-detail-guest.png`, **960×540, Cycles 32 adaptive samples, CPU 4, exposure +2.8, 31.236 seconds**. It is a guest-only daylight close-up with the unchanged generic CC0 stone material. The horizontal relief and open corner are legible; the bottom frame crops the hearth. This image does not prove whole-room furnishing clearance or photographic material matching. Broad stone colour variation and regular course outlines remain more synthetic than the source photo.

Guest deliverables are `masonry-detail-guest-pilot.blend`, `masonry-detail-guest-geometry.blend`, and reports `masonry-detail-guest-pilot.json`, `masonry-detail-guest-dimensions.json`, `masonry-detail-guest-regression.json`, `masonry-detail-guest-render.json`. Reproduce with `masonry-detail-guest-pilot.py` in a fresh Blender background process. No shared guest files, furniture files, source checkpoints, working blend, global settings or GPU settings were modified.

## Integration limits

Run scene/camera/navigation checks again after integration and guest structural changes. This pilot is not GEO07 photo alignment, a complete masonry survey, a final 4K render, or a whole-scene acceptance result. The module is deliberately restricted to near-view representatives; it does not globally cover the building with extra geometry.

The neat-freak handoff review reconciled this report and the versioned data with the active code, while preserving prior failures as evidence. Root README/STATUS/AGENTS integration pointers remain the integrating agent's responsibility under the assigned ownership boundaries.
