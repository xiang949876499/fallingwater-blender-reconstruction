from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[1]
with (root/'qa/integration12-ceiling-strip-probe.log').open('w',encoding='utf-8') as log:
    p=subprocess.run([r'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe','-b','-t','4','--python-exit-code','1','-P',str(root/'qa/integration12-ceiling-strip-probe.py')],stdout=log,stderr=subprocess.STDOUT,cwd=root.parent)
raise SystemExit(p.returncode)
