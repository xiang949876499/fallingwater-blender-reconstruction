import sys,json,traceback
from pathlib import Path
import bpy
sys.path.insert(0,'D:/zx/test/project/scripts')
import fwlib,materials,main_house
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
class Context:
 root=Path('D:/zx/test/project')
 config={}
 collection=staticmethod(fwlib.collection)
 mats=materials.build_materials()
rooms=main_house.build(Context())
report={'rooms':len(rooms),'objects':len(bpy.data.objects),'meshes':len(bpy.data.meshes),'faces':sum(len(m.polygons) for m in bpy.data.meshes),'rooms_with_surfaces':len({o.get('room_id') for o in bpy.data.objects if o.get('room_id')}),'runtime_status':'PASS','geometry_precision':'traced reconstruction; not measured-detail acceptance'}
Path('D:/zx/test/project/qa').mkdir(exist_ok=True)
Path('D:/zx/test/project/qa/main-geometry-smoke.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
bpy.ops.wm.save_as_mainfile(filepath='D:/zx/test/project/qa/main-geometry-smoke.blend')
