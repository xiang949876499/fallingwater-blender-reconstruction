"""Promote the checked intermediate as byte-identical files; keep09 intact."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
old=ROOT/'scene/Fallingwater_iteration09.blend'
working=ROOT/'scene/Fallingwater_working.blend'
source=ROOT/'scene/Fallingwater_navigation_candidate10a.blend'
target=ROOT/'scene/Fallingwater_iteration10.blend'
old_sha='489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331'
new_sha='1e7b17d9c2396513f005724e50788bf834097eedb401b91a7f1030825e2c4ed9'
assert sha(old)==sha(working)==old_sha and sha(source)==new_sha and not target.exists()
reopen=json.loads((ROOT/'qa/integration10-navigation-reopen.json').read_text(encoding='utf8'))
assert reopen['status']=='PASS_FRESH_REOPEN_ALL_SAVED_FRAMES' and reopen['source_sha256']==new_sha
captured=ROOT/'qa/checkpoint10-capture'
data=json.loads((captured/'camera-settings-actual.json').read_text(encoding='utf8'))
summary=json.loads((captured/'capture.json').read_text(encoding='utf8'))
subset={k:data[k] for k in summary['changed_pose_or_lens_vs09']}
(ROOT/'data/camera-settings-iteration10-overrides.json').write_text(json.dumps(subset,indent=2),encoding='utf8')
shutil.copy2(source,target);shutil.copy2(source,working)
assert sha(target)==sha(working)==new_sha and sha(old)==old_sha
report={'status':'INTERMEDIATE_CHECKPOINT_ONLY_NOT_FINAL','time_utc':datetime.now(timezone.utc).isoformat(),
        'working_scene':str(working),'checkpoint':str(target),'sha256':new_sha,'bytes':target.stat().st_size,
        'previous_checkpoint_unchanged':str(old),'previous_sha256':old_sha,
        'rooms':60,'objects':23437,'saved_qa_cameras':120,'total_cameras_including_tour':131,
        'graph_pass':60,'saved_integer_frames_pass':7584,'reopen_keys_unchanged':True,
        'build_entry':'scripts/build_iteration10.py',
        'limits':['Water10/11 native experiments not installed','11 canopy, floor and terrace candidates not installed',
                  'Complete photo quality and120 updated room views pending','Actual GUI/performance and final portability pending'],
        'legacy_metadata':'Root rooms.json and data/tour-route.json still historical09; current10 actual metadata and route are embedded or isolated in qa/integration10-navigation-workspace.'}
(ROOT/'qa/integration10-freeze.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report))
