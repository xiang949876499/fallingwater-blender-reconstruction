"""Compose accepted local11 changes, preserving the frozen10 and saved actions."""
from pathlib import Path
from types import SimpleNamespace
import bpy, hashlib, json, sys, time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
SOURCE=ROOT/'scene/Fallingwater_iteration10.blend'
OUT=ROOT/'scene/Fallingwater_integration_candidate11a.blend'
REPORT=ROOT/'qa/integration11-compose.json'
SHA='1e7b17d9c2396513f005724e50788bf834097eedb401b91a7f1030825e2c4ed9'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert bpy.app.background and sha(SOURCE)==SHA and not OUT.exists() and not REPORT.exists()
started=time.monotonic()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene
scene.render.threads_mode='FIXED';scene.render.threads=4
scene.frame_set(48)
import iteration11_details
result=iteration11_details.apply(SimpleNamespace(root=ROOT))
bpy.context.view_layer.update()
result.update(source_sha256=SHA,source_unchanged=sha(SOURCE)==SHA,
              objects=len(scene.objects),cameras=sum(o.type=='CAMERA' for o in scene.objects))
assert result['source_unchanged'] and result['cameras']==131
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
result.update(output=str(OUT),sha256=sha(OUT),bytes=OUT.stat().st_size,seconds=time.monotonic()-started)
REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:result[k] for k in ('status','objects','cameras','output','sha256','seconds')}),flush=True)
