"""Trace actual image defects to frozen07 surfaces; no mutation."""
import hashlib,json
from pathlib import Path
import bpy
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
source=root/'scene/Fallingwater_iteration07.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene;s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100
deps=bpy.context.evaluated_depsgraph_get()
groups={'CAM_MAIN_L2_BATH_N_A':[(115,323),(200,277),(266,244),(182,261),(188,300)],
        'CAM_MAIN_L2_BATH_G_B':[(200,280),(300,290),(380,300)],
        'CAM_MAIN_L2_BATH_M_B':[(200,280),(300,290),(380,300)]}
results=[]
for name,pixels in groups.items():
 cam=s.objects[name];corners=cam.data.view_frame(scene=s)
 xlo,xhi=min(q.x for q in corners),max(q.x for q in corners)
 ylo,yhi=min(q.y for q in corners),max(q.y for q in corners)
 for x,y in pixels:
  d=cam.matrix_world.to_quaternion()@Vector((xlo+(x+.5)/640*(xhi-xlo),yhi-(y+.5)/360*(yhi-ylo),corners[0].z))
  hit,p,n,face,ob,_=s.ray_cast(deps,cam.matrix_world.translation,d.normalized(),distance=100)
  results.append(dict(camera=name,pixel=[x,y],hit=hit,object=ob.name if hit else None,point=list(p) if hit else None,face=face))
report=dict(scene_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),results=results)
(root/'qa/bathroom07-floor-probe.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report))
