"""Run bounded CPU4 readback without relying on PowerShell startup."""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
log_path = root / 'project/qa/forest-undergrowth13-readback.log'
with log_path.open('w', encoding='utf-8') as log:
    result = subprocess.run([
        r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe',
        '-b', '-t', '4', '--python',
        str(root / 'project/qa/forest-undergrowth13-readback.py'),
    ], cwd=root, stdout=log, stderr=subprocess.STDOUT)
print('READBACK_PROCESS_EXIT', result.returncode, flush=True)
sys.exit(result.returncode)
