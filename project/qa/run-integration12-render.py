import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cmd = [r'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe', '-b', '-t', '8', '--python-exit-code', '1', '-P', str(root/'scripts/render_views.py'), '--', '--scene', str(root/'scene/Fallingwater_integration_candidate12a.blend'), '--output', str(root/'renders/previews/integration12a'), '--cameras', 'CAM_HERO,CAM_MAIN_OVERVIEW,CAM_MAIN_L2_MASTER_A,CAM_GUEST_L1_THEATER_A', '--samples', '48', '--device', 'CPU', '--threads', '8', '--resolution', '1280x720', '--frame', '48', '--no-exr']
with (root/'qa/integration12-root-render02.log').open('w', encoding='utf-8') as log:
    result = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, cwd=root.parent)
raise SystemExit(result.returncode)
