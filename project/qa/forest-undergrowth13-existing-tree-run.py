from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[2]
with (root/'project/qa/forest-undergrowth13-existing-tree-probe.log').open('w',encoding='utf-8') as log:
    result=subprocess.run([r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe','-b','-t','4','--python',str(root/'project/qa/forest-undergrowth13-existing-tree-probe.py')],cwd=root,stdout=log,stderr=subprocess.STDOUT)
print('EXISTING_TREE12_PROCESS_EXIT',result.returncode,flush=True)
sys.exit(result.returncode)
