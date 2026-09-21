# Native hearth rock revision

The former three similar stacked polygons have been replaced by two asymmetric rock lobes traced from the stippled native-rock regions of HABS main04. The revised component is in `scripts/furnishings.py`; the isolated candidate is `scene/Fallingwater_hearth_candidate06.blend`.

References actually inspected: `data/photo_refs/main_living_48.jpg`, `research/references/architecture/main-04-original.tif`, `research/references/architecture/main-04-sheet.jpg`, and `research/references/architecture/main-11-sheet.jpg`. The TIFF's orientation was checked before tracing. Enlarged source crops are `interior-hearth-plan-wide-reference.png` and `interior-hearth-elevation-reference.png`.

Main04 supports separate north and south projections with an irregular intervening fissure. Photo PA-5346-48 supports broad uneven upper faces and broken edges; main11 supports their low relationship to the finished floor. Exact manually traced boundaries, unmeasured height, unseen joining root, surface fracturing and shader grain remain **C**. This is not a scan. The new surface uses restrained 1.6 mm grain relief; the large form is actual mesh geometry.

The finished floor remains at Z 0.10 m. Rock bases embed 24 mm below that plane. Visible north and south lobes have different slopes and edge heights, rather than concentric courses. Walls, the fireplace aperture, kettle, logs, lights and existing camera paths retain their positions.

## Geometry verification

`interior-hearth-iteration06-check.json` records a local actual-mesh comparison against immutable iteration05:

- All six component meshes are manifold.
- 496 lobe-base points contact existing support: 493 at finished floor and 3 along the existing hearth masonry edge. Masonry contacts are explicitly distinguished from floor contacts.
- Fifteen rays through the unchanged fireplace aperture find no new rock obstruction.
- Seven existing living-room tour/door/inspection paths have no new failures. The unchanged Living_B camera has clear body space.
- Every other object retains its name, transform and mesh vertex count; the practical-fixture configuration still contains 14 entries.

The check saves a separate candidate and never overwrites iteration05 or its tour. No image was rendered. **Visual acceptance remains NOT_RUN** until the integrator compares the unchanged Living_B image with the source.

## Retained negative evidence

The old component geometry is in `interior-hearth-iteration05-geometry.json`; its original function is in `interior-hearth-iteration05-old-function.txt`; the negative image is `interior-hearth-iteration05-negative.png`. The full old component also remains in immutable `scene/Fallingwater_iteration05.blend`. Tour05 evidence stays frozen until the next integrated scene is checked.
