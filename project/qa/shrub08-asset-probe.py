"""Small CPU-only geometry preflight. No render and no scene saved."""
import bpy, sys, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import understory_detail08
mat=bpy.data.materials.new('Temporary test material')
reports=[]
for index in (2,3):
    branches,leaves,report=understory_detail08.make_asset(index,mat,[mat,mat,mat])
    reports.append(report)
(ROOT/'qa/shrub08-asset-preflight.json').write_text(json.dumps(reports,indent=2),encoding='utf8')
print('SHRUB08_ASSET_PREFLIGHT',json.dumps([{k:v for k,v in r.items() if k not in ('skeleton','terminals','leaves')} for r in reports]),flush=True)
