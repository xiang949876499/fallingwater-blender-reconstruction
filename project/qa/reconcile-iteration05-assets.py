"""Append explicitly scoped locally authored assets without changing source rights."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT/'assets_manifest.csv'
with path.open(encoding='utf-8-sig', newline='') as f:
    reader = csv.DictReader(f)
    fields, rows = reader.fieldnames, list(reader)
known = {r['asset_id'] for r in rows}
specs = [
    ('HEARTH_MASONRY_RELIEF', 'project/scripts/masonry_detail.py;project/data/masonry-detail.json',
     'Meters; 302 stones in two meshes; 5–23.342 mm measured modeled protrusion',
     'MAIN_L1_LIVING;GUEST_L1_LOUNGE', 'HABS PA-5346-48;HABS PA-5346-A-11',
     'Both actual pilot images viewed; cavity and original-geometry regressions pass; integrated whole-room visual review pending',
     'C bond/protrusion; no measured individual stone layout. Generic CC0 rock texture; not a scan of the actual wall.'),
    ('GUEST_CORNER_FIREPLACE', 'project/scripts/guest_architectural_detail.py',
     'Meters; firebox world X3.631264–4.4512 Y39.567296–40.268472 Z8.60–9.48',
     'GUEST_L1_LOUNGE', 'HABS PA-5346-A sheets 01/04;HABS PA-5346-A-11',
     'Four actual cavity rays pass; local image viewed; full-room photo alignment pending',
     'C unmeasured hood/firebox proportions inferred from drawings/photo, not surveyed dimensions.'),
    ('VISIBLE_SERVICE_LIGHT_FIXTURES', 'project/scripts/furnishings.py',
     'Meters; 14 locally modeled visible fixtures with assigned 9–32 W lights',
     'Eight bath/service spaces from iteration04 plus six additional bath/boiler spaces in iteration05',
     'Per-room HABS floor plans; C production lighting choice',
     'Actual iteration05 Main_B_Bath exposure brackets viewed; remaining new fixture views pending',
     'C fixture forms, power and color temperature; not historically measured luminaires or photometry.'),
    ('BEAR_RUN_MANTAFLOW_PILOTS', 'project/scripts/fluid_water.py;project/scripts/water_integration.py;project/data/fluid.json',
     'Meters; local liquid/foam/spray caches in project/caches/fluid_pilot',
     'Separate fluid pilot scenes; not yet accepted or installed in working iteration05',
     'MAIN_HABS_02_HIRES;MAIN_HABS_07_JPEG;authored site/rock geometry',
     'Real local solver caches run01–05; run06 ongoing at this ledger update; final seams and duration unaccepted',
     'C flow setup and water stages. Prior short caches have uncovered downstream/seam failures. Do not play beyond each cache range.')]
added = []
for asset_id, files, scale, used_by, refs, status, limits in specs:
    for name in files.split(';'):
        if not (ROOT.parent/name).is_file():
            raise FileNotFoundError(name)
    if asset_id in known:
        continue
    rows.append(dict(asset_id=asset_id, provider='Project-authored', author='Codex-assisted project implementation',
        local_files=files, physical_scale=scale, color_space='Scene-linear materials; downloaded surface channels listed separately',
        channels='Authored mesh/light/shader or locally computed simulation, as applicable',
        modifications='Editable local implementation; reference photographs not embedded as surface textures',
        used_by=used_by, verification_status=status, asset_origin='authored_procedural_not_scan',
        source_reference=refs, evidence_level='C reconstruction choices; reference evidence recorded separately',
        license_note='No external asset license asserted. Referenced design/photo rights remain distinct.', limitations=limits))
    added.append(asset_id)
for row in rows:
    if row['asset_id'] == 'SURFACE_GLASS':
        row['local_files'] = 'project/scripts/materials.py;project/scripts/eevee_glass.py'
        row['modifications'] = 'Original physical Cycles shader preserved; separately targeted EEVEE thin BLENDED/Fresnel approximation'
        row['verification_status'] = 'Actual old-Living six-static and 12-frame EEVEE test viewed; Cycles shader and 159 pane geometry hashes unchanged; iteration05 wider review pending'
        row['limitations'] = 'Preview thin-window branch is not exact refraction. Overlap/reflection behavior and full-building realtime performance require separate QA.'
with path.open('w',encoding='utf-8-sig',newline='') as f:
    writer = csv.DictWriter(f,fieldnames=fields)
    writer.writeheader();writer.writerows(rows)
result = {'asset_records':len(rows),'new_asset_ids':added,'manifest_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
          'scope':'Provenance reconciliation only; not final acceptance of listed assets.'}
(ROOT/'qa/asset-additions-iteration05.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(result)
