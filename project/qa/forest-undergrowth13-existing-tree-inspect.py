import json
from pathlib import Path
qa=Path(__file__).resolve().parent
p=json.loads((qa/'forest-undergrowth13-existing-tree-probe.json').read_text())
for k in ('source_sha256','camera_location','camera_lens','explicit_pixels','tree_hit_counts','objects','seconds'):
    print(k, json.dumps(p[k],ensure_ascii=False,indent=2))
