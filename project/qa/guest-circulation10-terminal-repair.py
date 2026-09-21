import bpy, sys, json, hashlib
from pathlib import Path
ROOT=Path('D:/zx/test/project');sys.path.insert(0,str(ROOT/'scripts'))
import guest_circulation10 as mod
old_sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
assert old_sha=='ff6ad7f2c3401a874c54dc5e3c7aab714b87c638883ebd9177b4b069c56e0a0b'
manifest=json.loads(bpy.data.texts['FW_GUEST_CIRCULATION10_CANDIDATE.json'].as_string())
outline=mod.rebuild_terminal_landing(manifest)
manifest['implementation_sha256']=hashlib.sha256((ROOT/'scripts/guest_circulation10.py').read_bytes()).hexdigest()
manifest['exact_repair_from_candidate_sha256']=old_sha
manifest['repair_scope']='Only P_SOUTH_LOW mesh rebuilt from identical target footprint union, closed prism7.01..7.22; remaining objects unchanged'
text=bpy.data.texts['FW_GUEST_CIRCULATION10_CANDIDATE.json'];text.clear();text.write(json.dumps(manifest,indent=2))
dest=ROOT/'scene/Fallingwater_guest_circulation_candidate10e.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest),check_existing=False)
freeze={'candidate':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'source_sha256':mod.SOURCE_SHA,
        'parent_candidate_sha256':old_sha,'status':'AWAITING_INDEPENDENT_REOPEN','repair_scope':manifest['repair_scope']}
(ROOT/'qa/guest-circulation10-freeze.json').write_text(json.dumps(freeze,indent=2),encoding='utf-8')
print('C10 REPAIR',len(outline),freeze,flush=True)
