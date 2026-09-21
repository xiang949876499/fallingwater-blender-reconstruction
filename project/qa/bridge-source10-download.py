"""Local-only reference photographs from their publishing institutions/authors."""
from pathlib import Path
import hashlib
import json
import urllib.request
from PIL import Image

root = Path(__file__).resolve().parent
sources = [
    ('columbia-0', 'https://projects.mcah.columbia.edu/ha/panos/Fallingwater/Bridge-Over-Stream/images/1213_fallingwater2001_vr_040_o_800_0.jpg',
     'https://projects.mcah.columbia.edu/ha/panos/Fallingwater/Bridge-Over-Stream/', 'Columbia MCAH panorama; date in filename 2001, not independently verified'),
    ('columbia-3', 'https://projects.mcah.columbia.edu/ha/panos/Fallingwater/Bridge-Over-Stream/images/1213_fallingwater2001_vr_040_o_800_3.jpg',
     'https://projects.mcah.columbia.edu/ha/panos/Fallingwater/Bridge-Over-Stream/', 'Columbia MCAH panorama; date in filename 2001, not independently verified'),
    ('hyde-bridge', 'https://www.eg.bucknell.edu/~hyde/FrankLloydWright/Images/IMG_4577Copying.jpg',
     'https://www.eg.bucknell.edu/~hyde/FrankLloydWright/Fallingwater.html', 'Author Dan Hyde: trip 2005-04-22; page updated2005-04-25; copyright Daniel C Hyde'),
]
records = []
for name, url, page, provenance in sources:
    rec = dict(id=name, url=url, source_page=page, provenance=provenance,
               distribution='REFERENCE_ONLY_EXCLUDE_PUBLIC_PACKAGE', actual_view='NOT_VIEWED')
    out = root / ('bridge-source10-' + name + '.jpg')
    try:
        if out.exists():
            raise FileExistsError(str(out))
        with urllib.request.urlopen(url, timeout=25) as response:
            payload = response.read(25000000)
        out.write_bytes(payload)
        with Image.open(out) as im:
            rec['size'] = im.size
            im.verify()
        rec.update(status='DOWNLOADED_IMAGE_VERIFIED', path=out.name,
                   bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())
    except Exception as exc:
        rec.update(status='FAILED', error=str(exc))
    records.append(rec)
out = root / 'bridge-source10-download.json'
assert not out.exists(), 'Preserve earlier attempts'
out.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(records, ensure_ascii=False, indent=2))
