"""Standalone07 main-house candidate; preserve integrated06 as negative evidence."""
import bpy,json,sys,hashlib,math
from pathlib import Path
from mathutils import Vector
P=Path('D:/zx/test/project');Q=P/'qa';sys.path.insert(0,str(P/'scripts'))
import fwlib,materials,main_house
S=P/'scene/Fallingwater_iteration06.blend'
SHA='172b76340d1224a2b98f415b21042d19ad7fba4d849543d7156beb17e5fcf055'
def probe(gate_only=False):
 s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();a=Vector((19.126,8.90,-2.5) if gate_only else (19.0736,9.1332,-2.5));b=Vector((19.126,8.3449836,-2.5));n=Vector((-(b-a).y,(b-a).x,0)).normalized();rows=[]
 for i in range(21):
  p=a.lerp(b,i/20)
  for side in [-.18,-.09,0,.09,.18]:
   q=p+n*side
   ok,g,_,_,ob,_=s.ray_cast(dg,q+Vector((0,0,.10)),Vector((0,0,-1)),distance=.30)
   floor={'object':ob.name,'z':g.z} if ok else None
   ok,h,_,_,ob,_=s.ray_cast(dg,q+Vector((0,0,.025)),Vector((0,0,1)),distance=1.925)
   head={'object':ob.name,'z':h.z} if ok else None
   rows.append({'t':i/20,'offset_m':side,'floor':floor,'body':head,'status':'PASS' if floor and abs(floor['z']+2.5)<.05 and not head else 'FAIL'})
 return {'samples':rows,'failures':sum(r['status']=='FAIL' for r in rows),'gate_only':gate_only,'start':list(a),'end':list(b),'limits':'Width0.36m support/vertical body samples. Broad approach includes low step00; a flat-foot probe there reports its legitimate riser, not proof of a failed stair traversal. Gate-only begins south of that tread. Neither test validates a dry ring route or coping use.'}
assert hashlib.sha256(S.read_bytes()).hexdigest()==SHA
bpy.ops.wm.open_mainfile(filepath=str(S));before=probe();gate_before=probe(True)
bpy.ops.wm.read_factory_settings(use_empty=True)
class Context:
 root=P;config={};collection=staticmethod(fwlib.collection);mats=materials.build_materials()
rooms=main_house.build(Context());bpy.context.view_layer.update();after=probe();gate_after=probe(True)
candidate=Q/'main-pool-iteration06-candidate07.blend';bpy.ops.wm.save_as_mainfile(filepath=str(candidate),compress=True)
out={'negative_scene':str(S),'negative_scene_sha256':SHA,'candidate_scene':str(candidate),'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'module_sha256':hashlib.sha256((P/'scripts/main_house.py').read_bytes()).hexdigest(),'before':before,'after':after,'gate_before':gate_before,'gate_after':gate_after,'scene06_unchanged':hashlib.sha256(S.read_bytes()).hexdigest()==SHA,'geometry_scope':'Only north wall shortened; candidate main module generated in a new empty background scene. Room polygon/level/access notes and false dry-edge retraction are metadata.','rendered':False}
(Q/'main-pool-iteration06-candidate-check.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'before_failures':before['failures'],'after_failures':after['failures'],'gate_before_failures':gate_before['failures'],'gate_after_failures':gate_after['failures'],'samples_each':len(after['samples']),'candidate_sha256':out['candidate_sha256'],'scene06_unchanged':out['scene06_unchanged']},indent=2))
