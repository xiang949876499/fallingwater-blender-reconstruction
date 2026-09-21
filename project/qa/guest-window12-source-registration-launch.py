"""Direct subprocess launch avoids the host's PowerShell startup stall."""
import subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
with (root/'qa/guest-window12-source-registration-probe-run.log').open('w',encoding='utf-8') as log:
    p=subprocess.run(['C:/Program Files/Blender Foundation/Blender 5.2/blender.exe','--background','--threads','4','--python-exit-code','1','--python',str(root/'qa/guest-window12-source-registration-probe.py')],stdout=log,stderr=subprocess.STDOUT)
print('Blender exit',p.returncode)
raise SystemExit(p.returncode)
