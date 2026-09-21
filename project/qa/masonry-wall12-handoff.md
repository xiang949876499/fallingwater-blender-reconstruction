# Masonry wall12a handoff

**READY FOR ROOT RENDER; independent physical readback PASS; visual NOT_RUN.**

- Source: `D:\zx\test\project\scene\Fallingwater_navigation_candidate10a.blend`; SHA256 `1e7b17d9c2396513f005724e50788bf834097eedb401b91a7f1030825e2c4ed9`.
- Candidate: `D:\zx\test\project\scene\Fallingwater_masonry_wall_candidate12a.blend`; SHA256 `7eec1f9cacb82e4494a06114f9f9ec30562c7eb8bb0416d91d477bebc8dce30f`.
- Helper: `D:\zx\test\project\scripts\masonry_wall12.py`; SHA256 `185d5209f029936a20c4dd5d7e7660e5933227c1b0fbf519174214c5ab8090f8`. Call `import masonry_wall12; manifest = masonry_wall12.apply(bpy.context.scene)` once on the guarded source. It rejects duplicate finish or changed wall geometry.
- Exactly one original object's mesh changes: `MAIN_L3_study_core_0`, to create the real frame-aligned west window aperture. Its transform, dimensions, bevel and material slots remain exact. The Dressing core is among the 23,436 unchanged original objects.
- Two new mesh batches contain 224 individual closed stones / 11,648 triangles. Actual front depth is 16.854–32.838 mm; stone face area is11.053 m². Only these west faces receive finish, with a private copied stone material. The tower, other Dressing pieces and other wall faces are outside scope.
- Fresh reopened geometry: 3,136 stone backing contacts, 126 window aperture rays, 28 frame-seat probes, no inter-stone or protected-surface collisions. Actual corrected core is closed and remains inside the original outer bounds.
- Route evidence: 12,264 changed-object route rays; all131 cameras; all7,584 saved integer camera positions; 153,627 readback rays with1.95 m walking body columns,0.18 m radial offsets and integer-frame sweeps against added finish. Zero new obstruction. This is local change regression, not a fresh all-adjacency or GUI-navigation certificate.
- Independent reopened snapshot exactly equals the pre-save snapshot, with no normalization exceptions. Source hash is still unchanged. Scene frame73 and saved camera settings remain preserved; root comparison should explicitly useframe48 in both files.

Use the unchanged `CAM_HERO` and `CAM_MAIN_L2_TERRACE_W_A` at matched baseline/candidate settings. No render was started here. The new aperture should be inspected visually as well as the two stone faces; preserved glass and the inset framing are expected, not a walk-through doorway.

See `masonry-wall12-design.md`, `masonry-wall12-final.json`, `masonry-wall12-check.json`, `masonry-wall12-reopen.json`, `masonry-wall12-reopen-physical.json`, `masonry-wall12-reopen-integer-frames.json`. All old failure reports/logs and the frozen source remain. Source photographs are reference-only and are not textures. CC0 rock maps are inherited unchanged; authored bond and relief are explicitC.
