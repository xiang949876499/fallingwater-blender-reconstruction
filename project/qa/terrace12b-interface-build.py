from pathlib import Path
import bpy,json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
SOURCE=ROOT/'scene/Fallingwater_navigation_candidate11a.blend'
SHA='d66ded0f23b7d19c20b81d2f59f94aa5aa77747be4568e85e1d105395fc219ff'
OUT=ROOT/'scene/Fallingwater_terrace_interface_candidate12b.blend'
assert not OUT.exists() and hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene
import main_terrace12b
result=main_terrace12b.apply();result['source_sha256']=SHA
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
result.update(output=str(OUT),sha256=hashlib.sha256(OUT.read_bytes()).hexdigest(),bytes=OUT.stat().st_size)
(ROOT/'qa/terrace12b-interface-build.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result),flush=True)
