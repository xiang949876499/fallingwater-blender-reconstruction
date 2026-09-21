# Iteration06 tour and full adjacency audit

Source: `scene/Fallingwater_iteration06.blend`, SHA256 `172b76340d1224a2b98f415b21042d19ad7fba4d849543d7156beb17e5fcf055`.

Independent saved tour: `scene/Fallingwater_tour_checked_iteration06.blend`, SHA256 `0c9b9a48251cdca265fb7f0d108bbbeef43bb04f6ff7c299820dd259dfc57be6`. Earlier checked scenes and negative evidence are retained. Neither the working scene nor immutable iteration06 was overwritten.

## Executed results

- **61 edges: 60 PASS / 1 FAIL / 0 NOT_RUN.** Passing edges comprise 52 normal walking connections and 8 explicitly limited inspection relationships. The latter include cabinetry, foundation bays and dry observations of water/stair spaces; they are not body entry into those spaces.
- All 60 space records are retained. Ten main segments provide 120 seconds, including 36 seconds outside; 49 separate supplemental segments cover the remaining spaces. No requested main segment or room inspection is excluded.
- Seven selected doorway connections, the covered connector and the true main-building approach via interior stairs, second-floor hall, north terrace, curved stairs and north upper walk pass actual mesh checks.
- The former bridge-road/terrain interference with the Loggia stairs is gone. ADJ_016's entire physical stair run and dry water observation pass. The guest pool coping cut also works: ADJ_051's physical dry steps and water observation pass.
- Geometry evaluation used 88,574 rays. The independent saved tour was reopened: all **7,584 integer frames** pass location/orientation/interpolation validation. Maximum position discrepancy is `0.0000043703 m`.

## Remaining ADJ_017 failure

The direct modeled lower-level connection from Loggia to East terrace is still **FAIL**. The north deck cannot serve as a level shortcut through the upper portion of the East terrace stair. That attempted alternative remains in the evidence with three failed pieces.

The corrected bounded route goes down the actual Loggia tread centers, around the east and south dry decks, and then up from the measured lowest East terrace tread. Its main lower waypoints are:

`(19.0736,9.1332,-0.9)` → `(19.126,8.344984,-0.9)` → `(19.126,6.149989,-0.9)` → `(11.1612,6.149989,-0.9)` → lowest tread eye `(11.1612,6.288810,-0.733333)`.

These are eye positions; lower deck ground is Z `-2.50 m`. All path pieces are independently tested. **Only its entry through the north pool recess fails:** body eye `(19.08670,8.93615,-0.9)` has a lateral body-column hit on `MAIN_B_pool_wall_0` at `(19.08670,8.75615,-1.971)`. The rest of the southern route and the full ascending stair pass. No walls or other structural objects were modified by this audit.

The architectural owner separately confirms that main04 supports continuous narrow east/south stone paving and a north wall stopping near drawing X628 rather than the modeled X700. This supports the southern route concept; the modeled paving width remains C. The wall diagnosis is a pending correction, not a positive result for this frozen scene. The affected connection must be rechecked after integration.

## Evidence and limits

`tour-path-all-adjacency-iteration06-final.json` records all nodes/edges, walking components, actual observer/target patches, stair runs and both bounded lower-deck attempts. `tour-path-check-iteration06-final.json` records the film paths and main-to-guest access. `tour-path-camera-coverage-iteration06-final.json` records the actual reopened-file hash and per-frame/per-room mapping. `tour-path-route-iteration06-final.json` preserves the tested route.

The probe uses a 0.18 m body radius, a 1.60 m eye height, multiple vertical body columns, lateral swept rays, and ground-height/normal checks. It is sampled mesh evidence, not a general-purpose capsule controller. Camera cuts never establish room connectivity. Final imagery, moving exposure, video delivery and GUI navigation remain separate acceptance work. No rendering was launched by this audit.
