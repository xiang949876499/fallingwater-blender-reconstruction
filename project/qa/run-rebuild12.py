from pathlib import Path
import subprocess

root=Path(__file__).resolve().parents[1]
with (root/'qa/build-iteration12-entry01.log').open('w',encoding='utf-8') as log:
    run=subprocess.run([r'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe','-b','--factory-startup','-t','4','--python-exit-code','1','-P',str(root/'scripts/build_iteration12.py')],stdout=log,stderr=subprocess.STDOUT,cwd=root.parent)
raise SystemExit(run.returncode)
