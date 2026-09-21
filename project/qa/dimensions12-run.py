"""Launch one fresh background CPU4 Blender, with structured Windows arguments."""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[1]
args=[r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe','-b','-t','4','--python-exit-code','2',
      '--python',str(root/'scripts/dimension_supplement12_integration.py'),'--',
      '--scene',str(root/'scene/Fallingwater_integration_candidate12a.blend'),
      '--expected-sha256','50e0a8fc0bab10fdec0e0b9d26c4ef4a4c71fa56aea6401e75197787c8c0e75a',
      '--prefix','dimensions12-integration12a']
with (root/'qa/dimensions12-integration12a-attempt02.log').open('w',encoding='utf8') as log:
    result=subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
print('BLENDER_EXIT',result.returncode,flush=True)
raise SystemExit(result.returncode)
