"""Download one CC0 candidate using the already inspected official file manifest."""
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit
import requests

root = Path(__file__).resolve().parents[1]
qa = root / 'qa'
aid = 'fern_02'
source = json.loads((qa / f'near-tree-asset07-{aid}-files.json').read_text())['blend']['2k']['blend']
items = {f'{aid}_2k.blend': {k: v for k, v in source.items() if k != 'include'}, **source['include']}
assert sum(v['size'] for v in items.values()) <= 200_000_000
dest = root / 'assets' / 'candidates' / 'fern_02_2k'
dest.mkdir(parents=True, exist_ok=True)
s = requests.Session()
s.headers['User-Agent'] = 'Fallingwater-research/1.0'
rows = []
for rel, info in items.items():
    assert urlsplit(info['url']).hostname == 'dl.polyhaven.org'
    p = (dest / rel).resolve()
    assert p.is_relative_to(dest.resolve())
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        response = s.get(info['url'], timeout=60)
        response.raise_for_status()
        assert len(response.content) == info['size']
        assert hashlib.md5(response.content).hexdigest() == info['md5']
        p.write_bytes(response.content)
    b = p.read_bytes()
    assert len(b) == info['size'] and hashlib.md5(b).hexdigest() == info['md5']
    rows.append(dict(path=str(p.relative_to(root)), size=len(b), md5=info['md5'],
                     sha256=hashlib.sha256(b).hexdigest(), url=info['url']))
report = {'asset': aid, 'license': 'CC0', 'license_url': 'https://polyhaven.com/license',
          'asset_url': 'https://polyhaven.com/a/fern_02', 'source': 'Poly Haven official API',
          'files': rows, 'total_bytes': sum(r['size'] for r in rows),
          'status': 'ISOLATED_CANDIDATE_NOT_IN_PRODUCTION', 'preview': 'NOT_VIEWED_TOOL_UNAVAILABLE'}
(qa / 'near-tree-asset07-download.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
