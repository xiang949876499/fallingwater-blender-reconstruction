import bpy,sys,json,hashlib
from pathlib import Path
R=Path('D:/zx/test/project');sys.path.insert(0,str(R/'scripts'))
import guest_circulation10 as module
source=Path(bpy.data.filepath);source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
assert source_sha=='e3f134081bddd77d8a4344a3046ef224c1db1bea0ff35644e7e7bf750a06c01d'
text=bpy.data.texts['FW_GUEST_CIRCULATION10_CANDIDATE.json'];manifest=json.loads(text.as_string())
obj,evidence=module.add_upper_divider();manifest['created_objects'].append(obj.name)
manifest['upper_source_divider']=evidence
manifest['implementation_sha256']=hashlib.sha256((R/'scripts/guest_circulation10.py').read_bytes()).hexdigest()
manifest['source_wall_completion_parent_sha256']=source_sha
manifest['source_wall_completion_scope']='Add real guest02 upper central solid divider; unknownCtop L2+1.0m, below existing roof. Lower return route restored tosourcey412.3.'
text.clear();text.write(json.dumps(manifest,indent=2))
dest=R/'scene/Fallingwater_guest_circulation_candidate10f.blend'
assert not dest.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(dest),check_existing=False)
freeze={'candidate':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'source_sha256':module.SOURCE_SHA,
        'parent_candidate_sha256':source_sha,'status':'AWAITING_FULL_LOCAL_REOPEN_WITH_SOURCE_DIVIDER'}
(R/'qa/guest-circulation10-freeze.json').write_text(json.dumps(freeze,indent=2),encoding='utf-8')
print('DIVIDER10F',freeze,evidence,flush=True)
