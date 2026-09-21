# Iteration 06 Study and Laundry single-factor follow-up

**Laundry: the giant V-shaped door shadow is removed by excluding only that light's own emissive filament. Study: disabling the entire ray-tracing module does not remove the wall rectangle and makes it darker/sharper.** The Laundry result is a local correction candidate; the Study variant must not be adopted as a fix. Neither change was saved to the preview.

Exactly two images were rendered from separately reopened copies of `scene/Fallingwater_preview_iteration06.blend`, SHA-256 `e317241899808995f049e8d3343eac96c591cbecfddaa980949d6babb51ccce6`. Both use 960×540, 32 samples, four CPU preparation threads, saved source camera pose, frame 1 and exposure +0.8. Each render produced +1.6/+2.4 exports from the same linear result. **All six resulting PNGs were actually opened at native resolution.** No GI rebake, source save, extra camera or additional candidate was performed.

| Variant | Actual result | Seconds | Base PNG SHA-256 |
|---|---|---:|---|
| Study B: `use_raytracing=False` only | FAIL. Black wall rectangle persists and deepens; shelf/ceiling become brighter and fine speckling increases. Higher exposure does not remove the defect. | 45.117 | `e29162679d6f6a9d0c561b62924a51bf1099e64df97a307e263d44aac9e6536a` |
| Laundry B: own-filament exclusion only | Local symptom PASS. Giant V disappears at all three exposures; door-handle and other real shadowing remain. | 26.325 | `0b31251523c8a1b0c8d9e9a2bb30ece6ef5453594158c247f1008078c06c9356` |

The Study source already had Fast GI disabled. Turning the entire ray module off retains all seven volume intensities and all actual light shadows. Therefore this result rejects the proposed simple ray-module-disable fix. It does not independently distinguish direct shadows from cached GI or other remaining shading terms. No claim is made that screen tracing is perfect; it was contributing light inside the region rather than being sufficient to explain the remaining black rectangle.

The Laundry target is `FW_FURN_GUEST_B1_LAUNDRY_practical_ceiling_lamp_C_05_bulb_photometric_proxy`. Its collection excludes only its own `..._visible_emissive_filament`. The visible bulb shell, protective guard, door, handle, walls and every other caster remain eligible. The already saved Bath exclusion remains unchanged. No new light was added; no power, color, radius, transform or shadow flag changed. The before/after state of every actual light is recorded and asserted in the per-variant JSON.

Both variants retain the seven volume intensities and unchanged physical glazing geometry / original Cycles glass shader hashes. Laundry also retains ray tracing with Fast GI off. Shadow linking remains engine-independent: this correction is only an unsaved EEVEE diagnostic candidate and would require the existing restoration path before Cycles if later persisted. The successful result does not authorize automatic expansion to the other fixtures or imply whole-scene visual acceptance.

Outputs:

- `eevee-iteration06-followup-study_raymodule_off.png`, its +1.6/+2.4 variants and JSON.
- `eevee-iteration06-followup-laundry_own_filament_excluded.png`, its +1.6/+2.4 variants and JSON.
- `eevee-iteration06-followup-contact.png`: unretouched native-pixel baseline/candidate comparison at +0.8.
- `eevee-iteration06-followup-summary.json`: verified hashes, view status, invariants and conclusions.
- `eevee-iteration06-followup.log`: both completed renders and normal process exit.

The original preview still contains only the previously saved Bath exclusion and keeps ray tracing enabled. The helper sources were not modified by this follow-up. GPU work ended after these two renders; no further diagnostic was started.
