"""Fresh, reviewable rebuild without replacing the user's working checkpoint."""
from pathlib import Path
import sys,json,hashlib,time
import bpy

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import build_scene,iteration10_details
OUTPUT=ROOT/'scene/Fallingwater_rebuild_candidate10a.blend'
WORK=ROOT/'qa/rebuild10-workspace'
assert not OUTPUT.exists() and not WORK.exists(),'Preserve prior build evidence'
assert bpy.app.background and not bpy.data.filepath
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'scene/Fallingwater_working.blend',ROOT/'scene/Fallingwater_iteration09.blend')}
started=time.monotonic()
report=build_scene.main(output_name=OUTPUT.name,manifest_root=WORK,
    after_details=iteration10_details.apply,config_override={'status':'revision10_rebuild_candidate_not_final'},run_dimensions=False)
after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'scene/Fallingwater_working.blend',ROOT/'scene/Fallingwater_iteration09.blend')}
assert before==after,'Production checkpoints must remain unchanged'
record={'status':'FRESH_REBUILD_SAVED_REOPEN_COMPARISON_PENDING','candidate':str(OUTPUT),
    'candidate_sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),'candidate_bytes':OUTPUT.stat().st_size,
    'working_checkpoints_unchanged':before==after,'seconds':time.monotonic()-started,'build':report,
    'limits':['Old saved QA cameras still require revision10 overlays','No integrated film/navigation/photographic acceptance',
              'New dimensions/forest/water11 candidates not included']}
(ROOT/'qa/rebuild10-fresh.json').write_text(json.dumps(record,indent=2),encoding='utf8')
print(json.dumps(record),flush=True)
