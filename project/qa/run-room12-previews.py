"""Low-resolution framing survey; these are not final room QA photographs."""
from pathlib import Path
import argparse, hashlib, json, subprocess

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--batch',type=int,choices=(0,1),required=True)
a=parser.parse_args()
scene=root/'scene/Fallingwater_integration_candidate12a.blend'
expected='50e0a8fc0bab10fdec0e0b9d26c4ef4a4c71fa56aea6401e75197787c8c0e75a'
assert hashlib.sha256(scene.read_bytes()).hexdigest()==expected
evidence=json.loads((root/'qa/camera12-actual-check.json').read_text(encoding='utf-8'))
assert evidence['scene_sha256']==expected
cameras=sorted(r['camera'] for r in evidence['rows'])
assert len(cameras)==len(set(cameras))==120
selected=cameras[a.batch*60:(a.batch+1)*60]
output=root/f'renders/room-survey12/batch{a.batch}'
output.mkdir(parents=True,exist_ok=True)
assert not (output/'render-benchmark.json').exists(), 'Preserve any previous run'
(output/'scope.json').write_text(json.dumps({'source_sha256':expected,'cameras':selected,
    'purpose':'640x360 interim composition survey, NOT final room photography acceptance'},indent=2),encoding='utf-8')
command=[r'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe','-b','-t','8','--python-exit-code','1',
    '-P',str(root/'scripts/render_views.py'),'--','--scene',str(scene),'--output',str(output),
    '--cameras',','.join(selected),'--samples','32','--device','CPU','--threads','8',
    '--resolution','640x360','--frame','48','--no-exr']
with (root/f'qa/room-survey12-batch{a.batch}.log').open('w',encoding='utf-8') as log:
    p=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,cwd=root.parent)
raise SystemExit(p.returncode)
