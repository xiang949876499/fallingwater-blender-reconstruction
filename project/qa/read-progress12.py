import json
from pathlib import Path

p = Path(__file__).resolve().parent
for name in ['camera12-actual-check.json', 'integration12-full-check.json']:
    a = json.loads((p / name).read_text(encoding='utf-8-sig'))
    print(name, json.dumps({k:v for k,v in a.items() if k != 'rows'}, ensure_ascii=False))
    for row in a.get('rows', []):
        if any(t in row['camera'] for t in ['MASTER', 'THEATER']):
            print('CAMERA_NAME', row['camera'])
print('WATER_LOG', (p / 'water12-surface07-root-render.log').read_text(encoding='utf-8-sig', errors='replace')[-2200:])
