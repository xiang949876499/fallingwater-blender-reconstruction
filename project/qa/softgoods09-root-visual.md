# Softgoods09 root visual review

2026-09-21. **LOCAL SHAPE IMPROVEMENT ACCEPTED; final material/room quality remains incomplete.**

The integrator actually opened both original-size 960×540 rendered PNGs. Both used the saved camera, Cycles CPU8, 64 samples, frame48 and the existing exposure/materials. Rendering completed with exit0; the image review below is separate from that technical result.

| Saved source | Actual image | Finding |
|---|---|---|
| Single-pillow candidate `e62b26f281bc03d62d2c0f9c47048cbebcc7a648c5e22333f8c6535e450acea6` | `../renders/previews/softgoods09/CAM_MAIN_L3_ALCOVE_B.png` | Rounded sewn outline and gently raised top replace the rigid block. The pillow stays in contact with the cover. Bed textiles remain bright and visually simple; this is not a photorealism pass. |
| All-pillow candidate `0eae45a4a8e6a23a5c80c9451c717384b268c4eaa5f91f6049832766ef692939` | `../renders/previews/softgoods09-all/CAM_GUEST_L2_BEDROOM_MIDDLE_A.png` | Guest pillow has the expected curved profile and readable perimeter seam. No old box shape or visible gap under its central body. The wide shot does not resolve every stitch; the flat cover and generic cabinet/desk still require further furnishing/material work. |

The [all-pillow verification](softgoods09-all-review.md) covers eight beds and ten pillows, including the explicit second guest bed. Actual cover-height agreement is within 0.87 micrometres. It independently records 5,610 contact points, 16,170 underside samples, closed meshes, normal consistency, no self intersections and unchanged non-target objects. These geometry results do not substitute for the two actual image reviews.

The production `furnishings.bed()` hook and helper are accepted for the next fresh build. The working iteration08 scene has not yet been rebuilt with them. Frozen08, both candidates and all original failure evidence remain available.
