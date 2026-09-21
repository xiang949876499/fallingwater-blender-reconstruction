from pathlib import Path
from types import SimpleNamespace
import bpy,json,hashlib,sys,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
SOURCE=ROOT/'scene/Fallingwater_terrace_interface_candidate12b.blend'
SHA='285ea6d0c29b0ff483fb6f582c644f5286b23e83f1d894bedf32546fbca3a14c'
OUT=ROOT/'scene/Fallingwater_integration_candidate12a.blend'
assert not OUT.exists() and hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
started=time.monotonic();bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene
s.render.threads_mode='FIXED';s.render.threads=4;s.frame_set(48)
import iteration12_details
report=iteration12_details.apply(SimpleNamespace(root=ROOT))
report.update(source_sha256=SHA,objects=len(s.objects),cameras=sum(o.type=='CAMERA' for o in s.objects))
assert report['cameras']==131
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
report.update(output=str(OUT),sha256=hashlib.sha256(OUT.read_bytes()).hexdigest(),bytes=OUT.stat().st_size,seconds=time.monotonic()-started)
(ROOT/'qa/integration12-compose.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:report[k] for k in ('status','objects','cameras','sha256','bytes','seconds')}),flush=True)
