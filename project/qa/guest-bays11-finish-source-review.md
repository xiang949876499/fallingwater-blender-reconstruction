# North bay finished masonry datum — independent read-only review

Input: saved11b SHA256 `c025c0e1d6adc55077d4bcaa0c3d028174eb5643aa002f466e9c162067c17f74`. No geometry, helper, material,
camera, route or scene save occurred. Actual source views: the original Guest01
north dimension crop, final endpoint annotation, Guest04 west elevation detail,
and HABS A10/A1 photographs. A10 is a different Guest wall; it supports rough
course character but cannot quantify this bay or the 2010 survey datum.

## What the source does and does not establish

The Guest01 8′1⅞″ arrows end on **opposing hatched masonry outlines**. No separate
hidden structural-core boundary, added stone veneer layer, mean-surface offset,
measurement height or high-point convention is identified on this detail. Thus
the printed length belongs to the architectural masonry faces represented by
the drawing; calling it an independently proven hidden-core dimension is not
supported. The 1′6″ pier thickness likewise spans the complete drawn masonry
outline. The source line is a simplified architectural boundary, not a scan of
every rough stone point. It does not prove that every recess and projection at
every height must have one identical clearance.

Guest04 and the actual A10 photo show varied stone courses and recessed joints.
They oppose flattening all relief into one plane. They do **not** supply the
surface datum or a numerical roughness allowance for the north Theater bay.
Both finish-datum interpretation and modeled relief depth remain C/U. There is
no source basis to waive the independent finished-face failure automatically.

## Cause of the discrepancy is directly measured

558 paired actual-mesh samples cover 186 heights at each of three parallel
stations (0, 100, 200 mm). Core span varies only 0.892 mm between stations due
to the small traced wall-angle difference: 2.485133–2.486025 m. Visible clearance
is 2.414063–2.486025 m, mean **2.444558 m**. The mean inward contribution is
**20.924 mm from the north wall + 20.097 mm from pier2 = 41.021 mm**.
At every sample the sum explains the entire missing width within 0.00015 mm
floating-point residual. This is not a new level, axis or wrong-pier diagnosis.

The cause is explicit in `guest_house.py`'s existing `quadstone`: each stone box
has depth 12–42 mm; its center is outside the wall by thickness/2 + depth/2 − 5 mm.
Every outer stone face therefore lies **7–37 mm beyond an already traced masonry
wall outline**. The11b transform preserved these C positive offsets; it did not
introduce the relief profile. Some height samples hit the exposed core in 9 mm
course joints, explaining near-zero projection at those stations. Both actual
surfaces remain visible; neither was hidden during measurement.

## Smallest defensible next candidate — proposal only

Keep the source-supported whole-wall/pier positions, bay axes and every stone's
shape. Correct the **backing/relief registration** on the two bay-facing surfaces,
rather than adding a second thickness outside the source masonry boundary.
Treat that boundary as a stated finished-masonry reference datum; recess the
backing and rebase the corresponding course blocks together into their own wall.
The far faces, retained pier ends, slab and neighboring bays should stay fixed.
Keep complete blocks, course heights and depth variation. Check real frame/jamb
connections after rebasing: any required recess packing must be a physical full
joint, not a thin measuring-only patch.

A bounded **C construction trial of 22 mm inward per bay-facing surface** follows
the midpoint of the existing generic 7–37 mm relief range, not a selected ray's
error or the printed bay width. It preserves the original 30 mm relief span and
places stone faces about ±15 mm around the stated datum, with recessed mortar.
That value is **not an archival measurement** and is not authorized/applied by
this report. A source or field datum should supersede it if available.

Even this honest rebasing cannot make every rough-height sample a strict ±20 mm
PASS: current sampled peak-to-recess width variation is about 72 mm. No constant
translation can reduce that variation to a 40 mm tolerance band. Do not select
the most favorable height, shrink relief until it fits, offset the entire walls,
or retroactively name a mean/peak convention as source-proven. Keep the full
visible range and independent dimension qualification separate from a nominal
reference-plane result. The north finished-face anchor remains **NOT PASS / datum
qualification unresolved** in the current11b.

Evidence: `guest-bays11-finish-source-probe.json` and
`guest-bays11-finish-source-profile.png`/`.svg`. Original source crops remain
`guest-bays11-source-north.png` and `guest-bays11-source-endpoints-final.png`;
no source pixel or production file was changed.
