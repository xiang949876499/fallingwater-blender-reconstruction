"""Fetch two public HABS bridge photographs for local source inspection only."""
import hashlib
import json
from pathlib import Path
import urllib.request
from PIL import Image

root = Path(__file__).resolve().parent
records = []
for num, label in [(134152, '13-west'), (134153, '14-southeast')]:
    url = f'https://tile.loc.gov/storage-services/service/pnp/habshaer/pa/pa1600/pa1690/photos/{num}pv.jpg'
    record = {'candidate_photo': label, 'url': url,
              'identification': 'LOC caption 13/14; numeric identifier cross-linked by reproduction host, original image identity pending actual view',
              'distribution': 'LOCAL_REFERENCE_ONLY', 'actual_view_status': 'NOT_VIEWED'}
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            payload = response.read()
        path = root / f'bridge-source09-{label}.jpg'
        path.write_bytes(payload)
        with Image.open(path) as im:
            im.verify()
        record.update(status='DOWNLOADED', path=path.name, bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())
    except Exception as exc:
        record.update(status='DOWNLOAD_FAILED', error=str(exc))
    records.append(record)
(root / 'bridge-source09-download.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
print(json.dumps(records, indent=2))
