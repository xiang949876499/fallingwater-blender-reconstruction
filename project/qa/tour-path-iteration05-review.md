# Iteration05 tour and full adjacency audit

Frozen scene: `scene/Fallingwater_iteration05.blend`, SHA256 `6bcfee7841c22e8e2b636352cfca79ae94968afb4235fc20cdc57e250ae046ff`.

Saved tour: `scene/Fallingwater_tour_checked_iteration05.blend`, SHA256 `21b15a19e7a2887ad03819b65d0e7f0a7f930ec7e6ea69f1956fae8c043b6a9d`. Iteration03 and iteration04 tour files are retained. Source scenes were not overwritten.

## Actual results

- All 61 declared adjacency edges were executed: **58 PASS / 3 FAIL / 0 NOT_RUN**. Of the passing edges, 52 are walking paths with body/ground checks and 6 are explicitly limited inspection relationships. These categories are not interchangeable.
- All 60 space records retained. Two storage cabinets are observed from their parent bedrooms; three foundation bays use clear free-camera observation and target-face rays; the living hatch has a dry observation point and checked stair geometry. Plunge and guest pool observations also pass, but their stair defects keep the corresponding overall edges FAIL.
- Ten main segments total 120 seconds, including 36 seconds outside. Forty-nine separate supplemental segments cover the remaining space records. No requested main segment or space is omitted.
- Seven selected film door connections, the 45-tread covered connector, and access via gallery → inner stairs → second-floor hall → north terrace → corrected exterior curved stairs → north upper walk all pass. There is no invented gallery/alcove north-wall door.
- The saved tour was reopened. Every one of 7,584 delivered integer-frame camera positions matches the checked polyline within 0.00000438 m; orientations are finite and all interpolation is linear.
- Geometry audit used 86,155 mesh rays. Moving-camera exposure, final rendered composition, GUI navigation, and collision-controller behavior remain separate work.

## Remaining failures

| Edge | Actual defect | Diagnostic |
|---|---|---|
| ADJ_016 Loggia → Plunge | `SITE_Path_bridge_north_approach` crosses the real modeled `MAIN_loggia_pool_stair_` body path. Water remains visible from a checked dry observer. | Body hit `(17.41427,9.45180,-0.023)`; intended stair eye `(17.41427,9.45180,-0.12000)`. |
| ADJ_017 Loggia → East terrace | Same bridge obstruction, followed by additional terrain and lower-pool approach collisions when each path piece is checked independently. | First hit `(15.98733,9.45180,-0.023)`; lower route also hits terrain, `MAIN_B_pool_wall_0`, and the second stair approach. |
| ADJ_051 Guest terrace → Pool | Pool coping still occupies the new dry stair entrance. The old water-plane collision is gone. | `GUEST_POOL_coping_16` bounds X `22.979303–23.213709`, Y `36.396042–36.547009`, Z `9.034850–9.104850`; first-step eye `(23.090290,36.414639,10.176213)`. |

The bridge approach mesh spans X `15.75005–28.18950`, Y `5.22443–11.62829`, at Z `-0.022`. A focused 0.10 m body-column diagnostic records 115 bridge intrusions and 5 coping intrusions. The diagnostic is not permission to remove historically supported geometry: source registration and actual stair/perimeter routes must be resolved first.

## Evidence and reuse

`tour-path-all-adjacency-iteration05-final.json` retains all edges, typed observation points, five-ray target patches, short motion checks, actual stair centers, failures, and normal-walk graph components. `tour-path-check-iteration05-final.json` records film paths and main-to-guest access. `tour-path-camera-coverage-iteration05-final.json` records saved-file hash, per-frame validation, and room/frame mapping. `tour-path-route-iteration05-final.json` fixes the tested camera route. `tour-path-iteration05-interference.json` contains exact mesh bounds, interference samples, and every lower Loggia-route waypoint ground ray and independent segment result.

The next scene version must rerun all adjacency edges and camera paths. Inspection PASS does not establish body access into water, cabinetry, or foundation voids. Editorial cuts never establish connectivity. This is geometric evidence, not final visual acceptance.
