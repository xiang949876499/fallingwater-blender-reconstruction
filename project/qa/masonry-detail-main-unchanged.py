"""Confirm guest addition did not alter accepted main finish; no rendering."""
import bpy,sys,json,hashlib
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from fwlib import collection
import masonry_detail
def digest(obj):
    h=hashlib.sha256()
    h.update(str([tuple(v.co) for v in obj.data.vertices]).encode())
    h.update(str([tuple(p.vertices) for p in obj.data.polygons]).encode())
    h.update(str([list(r) for r in obj.matrix_world]).encode())
    return h.hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene/Fallingwater_iteration04.blend'))
masonry_detail.build(SimpleNamespace(root=ROOT,mats={'stone':bpy.data.materials['FW_stone']},collection=collection),[],include_guest=False)
actual=digest(bpy.data.objects['FW_MASONRY_MAIN_HEARTH'])
with bpy.data.libraries.load(str(ROOT/'qa/masonry-detail-pilot.blend'),link=False) as (before,after):
    after.objects=['FW_MASONRY_MAIN_HEARTH']
reference=digest(after.objects[0])
result={'status':'PASS' if actual==reference else 'FAIL','current_geometry_sha256':actual,'accepted_pilot_geometry_sha256':reference,'rendered':False}
(ROOT/'qa/masonry-detail-main-unchanged.json').write_text(json.dumps(result,indent=2))
assert actual==reference
print('MAIN_MASONRY_UNCHANGED',json.dumps(result),flush=True)
