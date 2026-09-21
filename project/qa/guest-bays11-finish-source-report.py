from pathlib import Path
import json,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];Q=R/'qa'
d=json.loads((Q/'guest-bays11-finish-source-probe.json').read_text(encoding='utf-8'))
c=json.loads((Q/'guest-bays11-camera-proposal.json').read_text(encoding='utf-8'))
rows=[r for r in d['samples'] if r.get('station_m')==0 and 'visible_span_m' in r];z=[r['z']-8.4 for r in rows]
fig,ax=plt.subplots(1,2,figsize=(11,5.7),sharey=True,layout='constrained')
ax[0].plot([r['visible_span_m'] for r in rows],z,color='#a34031',lw=1.3,label='Actual exposed surface clearance')
ax[0].axvline(2.486025,color='#203746',lw=1.5,ls='--',label='Printed 2.486025 m / current core')
ax[0].set(xlabel='North bay width (m)',ylabel='Height above floor (m)',title='Actual source-axis width varies with courses')
ax[0].legend(loc='lower left',fontsize=8);ax[0].grid(alpha=.18)
ax[1].plot([r['north_additive_projection_m']*1000 for r in rows],z,label='North wall projection',color='#4e7781',lw=1.1)
ax[1].plot([r['pier2_additive_projection_m']*1000 for r in rows],z,label='Pier 2 projection',color='#a97738',lw=1.1)
ax[1].plot([r['projection_sum_m']*1000 for r in rows],z,label='Sum = missing clearance',color='#a34031',lw=1.3)
ax[1].set(xlabel='Additive stone outside traced wall core (mm)',title='Two always-outward C layers explain the deficit');ax[1].legend(loc='lower left',fontsize=8);ax[1].grid(alpha=.18)
fig.suptitle('Guest north bay11b — geometric diagnosis, not a finished-dimension PASS',fontsize=13)
fig.savefig(Q/'guest-bays11-finish-source-profile.png',dpi=160);fig.savefig(Q/'guest-bays11-finish-source-profile.svg');plt.close(fig)
summary=d['summary'];average=summary['projection_sum_m']['mean']*1000
texts={
'guest-bays11-finish-source-review.md':f'''# North bay finished masonry datum — independent read-only review

Input: saved11b SHA256 `{d['scene_sha256']}`. No geometry, helper, material,
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
**20.924 mm from the north wall + 20.097 mm from pier2 = {average:.3f} mm**.
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
''',
'guest-bays11-camera-proposal.md':'''# Guest north/middle bay photography proposals — actual11b read-only

These are two new normal standing viewpoints, not inherited PASS labels from
the old Theater A/B. No camera object was created, no settings were applied,
no rendering occurred and no scene was saved. Both use 24 mm focal length,
36 mm sensor width, 16:9 aspect, 1.60 m eye height above the actual8.4 m floor,
zero intentional roll, and a modest downward aim. Exposure remains for the
integrator's actual preview; this report does not claim lighting acceptance.

| Suggested temporary name | Eye XYZ (m) | Aim XYZ (m) |
|---|---|---|
| CAM_QA_GUEST_BAY11_NORTH | (0.600000, 51.800000, 10.000000) | (−2.866858, 51.681335, 9.480000) |
| CAM_QA_GUEST_BAY11_MIDDLE | (0.400000, 49.900000, 10.000000) | (−2.412213, 48.720924, 9.480000) |

Both pass actual evaluated-mesh 4 mm floor support, 0.18 m body radius, 1.95 m
head height and 0.13 m near-camera clearance. Their local approaches pass dense
20 mm samples and body sweeps without moving any furniture or source geometry.
All four full-bay corners, from floor8.4 through top10.56, fit with frame margin.
The first middle candidate (0,49,10) passed standing checks but clipped the full
head; it is retained in attempt01 and is not the final recommendation.

North approach: accepted Theater route endpoint (−0.29519,50.2696,10) →
(0.055,50.2,10) → (0.055,51.65,10) → proposed eye. Its 20 target stations all
lie within the frame. Sixteen rays first reach the new bay geometry; four rays
at bay fraction0.70 pass through the **real open door**, not an occluder or lost
wall. This shows the full window/door relationship from within the room.

Middle approach: central room aisle (−0.54,49.0,10) → (0.055,49.0,10) →
(0.055,49.95,10) → proposed eye. Eighteen of
20 target stations directly reach the new middle glazing in frame. Two low
stations at Z8.75 m are naturally occluded by the unchanged seat04 seat and
seat05 upholstered back. Upper window/return relationships remain visible; these
chairs were not hidden or moved to increase the score. This is a room photograph
proposal, not an orthographic evidence view or exact archival photo match.

Detailed tests and the four north/five middle bounded candidates are preserved
in `guest-bays11-camera-proposal.json`. Suggested names are labels only; they do
not exist in the saved scene. The old A/B geometric failures remain recorded.
'''}
for name,text in texts.items():(Q/name).write_text(text,encoding='utf-8')
c['readout_interpretation']={'NORTH':'All20 target stations framed:16 hit new bay geometry;4 at fraction0.70 are actual clear open-door portal rays, not occlusion.','MIDDLE':'18/20 new bay geometry targets visible;2 low targets physically occluded by retained seat04 seat/seat05 back.'}
c['suggested_names']=['CAM_QA_GUEST_BAY11_NORTH','CAM_QA_GUEST_BAY11_MIDDLE']
(Q/'guest-bays11-camera-proposal.json').write_text(json.dumps(c,indent=2),encoding='utf-8')
print('READONLY_REPORTS_SAVED')
