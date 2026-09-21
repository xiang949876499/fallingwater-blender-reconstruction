from pathlib import Path
import hashlib, json, shutil

root=Path(__file__).resolve().parents[1]
source=root/'qa/integration10-navigation-workspace/data/tour-route.json'
target=root/'data/iteration12-reference-route10.json'
if target.exists():
    assert target.read_bytes()==source.read_bytes()
else:
    shutil.copy2(source,target)
print(json.dumps({'path':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}))
