# run05 water integration into frozen iteration03

Later assessment: this remains a failed frame48 diagnostic, not an animated river solution. Run06's fixed full-width contour and entry01's thin-inlet calibration also failed; see [dynamic assessment](water-dynamic-review.md) and [entry01](fluid-entry01-review.md). The independent orientation repair is still usable. No cached water has been approved for the current working scene.

Current diagnostic scene: [Fallingwater_fluid_integrated_run05.blend](../scene/Fallingwater_fluid_integrated_run05.blend), **frame 48**. New implementation: [water_integration.py](../scripts/water_integration.py). The frozen source and `working.blend` were not overwritten; source03 SHA-256 remains `2f4f904a0364cf2792036ad59b7a112280cd64a15405945a13e975615a561bf4`.

## Verified changes

- Appended run05's actual cached liquid and simulated foam/spray particles. No cache rebake, geometry warp, stone deletion or hidden filler surfaces were used.
- Disabled rendering/view display of 59 previous local waterfall, impact foam, advecting foam and droplet objects. The rest of the river remains present.
- **Normal fault confirmed and repaired:** 14,414 of the original 14,430 river faces pointed downward. After face-only clipping, all 14,182 retained faces point upward. Area-weighted normal Z changes from −0.99882 to +0.99915.
- The 75 mm Solidify modifier keeps `offset = −1`. At upstream probe (60, 1), its former downward normals placed the visible shell 75 mm **above** the original water surface. After repair, the upper surface is at the original water level and thickness extends below it.
- The original **15,500 vertex coordinates, all three shape-key coordinates, relative-key relationships and driver expressions retain identical SHA-256/signature records** before and after the edit.
- The first mask removed 579 face centers inside the solver's rectangular bounds. It exposed 62 centers with no cached water, so that version was preserved as `Fallingwater_fluid_integrated_run05_domain_mask.blend`, with separate `fluid-integrated-run05-domain-mask` images and JSON/log evidence.
- The current mask removes **248** faces only where actual frame48 cached water is near the original surface. It retains 62 unsupported faces and 269 faces whose liquid level is outside the −0.30…+0.60 m diagnostic matching band. Every removed face center now has a cached-water ray hit. This prevents the former rectangle-only empty coverage; it is not proof that the entire seam is closed.

## Actual full-scene renders

Cycles CPU, maximum 8 threads, 960×540, 24 samples, frame48, AgX, exposure +0.8 EV. Each saved image was opened and inspected.

| Camera | Time | Image / observation |
|---|---:|---|
| HERO | 38.98 s | [Image](../renders/previews/fluid-integrated-run05/CAM_HERO.png). The waterfall sits below the cantilever and remains legible in the full scene. Its water curtain is still overly uniform in parts. |
| WATER_DETAIL | 43.93 s | [Image](../renders/previews/fluid-integrated-run05/CAM_WATER_DETAIL.png). Contact with the actual ledge and side rocks is visible; the top water layer and granular foam still need photographic refinement. |
| WATER_OUTLET_QA | 63.37 s | [Image](../renders/previews/fluid-integrated-run05/CAM_WATER_OUTLET_QA.png). Added only because both original cameras crop out most of the impact pool. It shows thick/faceted swells, patchy foam and the transition from the clearer cached liquid to the darker original river. |

The two requested cameras were not repositioned. The third camera is a separately named diagnostic viewpoint, not a replacement for either.

## Remaining issues — not final water acceptance

1. **Seams are not accepted.** Coverage-based clipping avoids empty deleted face centers, but three sampled cut-edge neighborhoods still lack a cached-water hit within the tested 40 cm inset. The mask is irregular and frame-specific. The original and cached liquid levels/materials remain distinct. Full edge ranges include rays reaching the lower pool or splash crests across the cliff, so their extreme deltas must not all be described as literal seam steps.
2. **Volume/detail require refinement.** The curtain top and impact-pool swell shapes remain thick and overly smooth/faceted in places; foam still looks granular close up. No rendered comparison has established photographic acceptance.
3. **Duration remains only 48 frames.** This integration mask is derived at frame48. No ten-second continuity, changing-frame mask stability or final film proof is claimed. A frame outside 1–48 exceeds this real cache.
4. **Portability remains pending.** A new Blender process reopened this saved integration, preserved frame48, matched all original vertex/key/driver signatures, recovered the 420,682-vertex / 842,172-polygon liquid mesh, and confirmed all old local water remained hidden. This is an original-path reopen, not a relocated delivery package.

Detailed machine evidence: [integration JSON](water-integration-run05.json), [fresh-process reopen](water-integration-reopen.json), [pilot cache/physics report](fluid-review.md).

## Integrator API

`water_integration.install(scene, cache_blend=None, frame=48, mask_mode='cached_surface')` appends the cache, corrects original river normals and performs the reviewed face-only mask. It does not save, mutate `site.py` or move terrain. It refuses a scene that already contains an installed fluid pilot. The standalone command always writes a separate output checkpoint.

`water_integration.repair_surface_normals(scene)` exposes the verified normal/thickness correction independently. It does not install the short cache or cut any river faces, so the integration owner can adopt that correction while the remaining fluid/seam issues are developed.
