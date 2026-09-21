# Daylight sky fill comparison

The integrator actually opened the matching frame1 HERO, Living A and Study B Cycles renders from `renders/previews/iteration07-lighting-baseline/` and `iteration07-lighting-skyfill/`. Both batches completed with process exit0, 960×540, 32 samples, CPU8, AgX, identical source geometry and camera poses. Different exposure exports come from each image's same linear EXR; exposure does not add illumination to the scene.

The candidate changes only physical sky strength **0.12→0.36**. Sun energy remains2.5, and all practical light values/geometry stay unchanged. Source scene hash and light-value equality are recorded in `lighting07-skyfill-candidate.json`. This is an artistic daylight ratio, not a measured Bear Run weather reconstruction.

At HERO EV0.8, the candidate retains the sunny direction while opening the foundation, cantilever undersides and forest shadows. It is less contrasty and slightly cooler; vegetation, ground and waterfall geometry still visibly need improvement. The old image's harsh shadow is not mistaken for inherently more photographic lighting.

Living A with the candidate at EV2.4 is readable across the floor, window seat, table, glazed opening and overhead structure. The old sky at EV3.2 gives a similarly bright exterior with darker interior masses. The candidate produces a better interior/exterior balance at a lower exposure. Study B at candidate EV2.4 has clearer wall/bookcase/chair values while retaining a shaded interior; the bright narrow strip near the base of the back wall appears in both physical configurations and its architectural cause is not yet diagnosed.

**Decision: use sky strength0.36 for the next integrated daylight iteration; Living A exposure2.4, HERO0.8.** This is a staged lighting improvement, not a final realism score or blanket approval of every room's exposure. All other existing camera exposures remain subject to new integrated images. EEVEE's old cached indirect lighting cannot be reused as validated lighting after this change; rebake the final preview separately. The evening preset remains a separate unreviewed configuration.

No geometry/material changes or simulated water-cache acceptance are implied. The 06 frozen source and both comparison folders remain available.
