# Guest lounge screen placement and chair clearance

The complete slat screen and low cabinet now occupy the source-supported southeast entrance position. The earlier placement beside the northwest fireplace was inconsistent with both HABS guest01 and the A11 interior photograph. Source images were actually inspected; see the independent `guest-lounge-visual-review06.md` and its source grid.

The manually read slat line is approximately source X440, Y394–430, centered on (440,412). Current registration maps that center to **(9.4444,37.6272,8.4)m**. The complete assembly was translated from (4.927919,39.143429,8.4), retaining its rotation, 13 mesh members and existing dimensions. It is not automatically fitted back toward the fireplace. Source tracing is C with about ±2px reading uncertainty (roughly 0.105m); the retained 1.522554m cabinet depth is not asserted as a surveyed dimension or the full source slat-line length.

The original inferred armchair overlaps the corrected cabinet. Its final position is **(8.4644,38.5372,8.4)m**, a translation of approximately (-1.169894,+0.500145,0)m. Its 270° orientation, eight mesh members, form and materials are unchanged. This is explicitly C furniture placement. The low table, bookcase, fireplace, architecture, lights and cameras were not moved.

## Actual geometry checks

On the independent iteration06-derived 07e candidate, the evaluated scene mesh checks pass for the unchanged GUEST_LOUNGE film path, both static camera body positions, Lounge–Gallery door connection, Lounge–Terrace door connection, and a 1.30m body-clear segment between the chair and screen. Cabinet-to-other-furniture and chair-to-other-furniture world AABB overlaps are both empty. These conservative bounds establish nonintersection for the furniture parts, while the body and ground checks use the actual evaluated mesh.

The chair–screen gap test uses X8.9844, Y37.887201–39.187201 at eye Z10.0. The film path is retained exactly: (6.16991,39.14343,10) to (8.36166,37.90134,10). Door checks preserve their original topology and test a real body-clear line through each opening; they do not claim all possible approaches are clear. All object transforms and data blocks outside the two translated assemblies remain unchanged.

The saved 07e candidate was independently reopened. A fresh `furnishings.room_living()` build using its embedded room record reproduces both assemblies exactly: 104 screen vertices and 64 chair vertices, maximum world-coordinate and matrix error **0.0**. This verifies the source script reproduces the tested location; the candidate itself is not the full integrated iteration07 building.

## Candidate and retained negative evidence

- **Use 07e:** `scene/Fallingwater_furniture_candidate07e.blend`, SHA256 `d6084c1ebca7e1328f1a008b673d86e55c738da4b5ee8a52c5b7e5ce86b8eadd`. It includes the separately verified 27 bathroom curve repairs. Results: `guest-screen-placement07e-check.json`, `guest-screen-placement07-source-check.json`.
- **Retain 07b:** corrected screen intersects the old chair seat and two legs. The seat overlap is 0.375105m × 0.600000m × 0.055000m. Evidence: `guest-screen-placement07-check.json`.
- **Retain 07c:** west-only chair move clears cabinet but intersects the old film path at eye (7.96316,38.12717,10). Evidence: `guest-screen-placement07c-check.json`.
- **Retain 07d:** chair Y38.687202 clears the film path, but the added chair–screen gap test ends too close to the unchanged bookshelf. Body ray at (8.9844,39.3372,10) hits its shelf at Y39.5172. Evidence: `guest-screen-placement07d-check.json`.

Reproduction uses `guest-screen-placement07-check.py -- --chair-clearance --variant 07e` with `Fallingwater_bath_fixtures_candidate07.blend`, followed by `guest-screen-placement07-source-check.py` on saved 07e. Blender 5.2.1, four CPU threads and `--python-exit-code 1` were used. All older candidates and QA files remain available.

**Visual acceptance remains NOT_RUN.** No render was started. The integrator should inspect the same lounge and basement-bath cameras before granting appearance acceptance, and rerun the full route/topology checks on the eventual integrated scene. Frozen iteration06 route results are unchanged.
