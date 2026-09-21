"""Identify structural backing behind the visible Closet M masonry holes."""
import hashlib,json
from pathlib import Path
import bpy
from mathutils import Vector
root=Path(__file__).resolve().parents[1];source=root/'scene/Fallingwater_iteration07.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100
cam=s.objects['CAM_MAIN_L2_CLOSET_M_B'];cs=cam.data.view_frame(scene=s)
xlo,xhi=min(q.x for q in cs),max(q.x for q in cs);ylo,yhi=min(q.y for q in cs),max(q.y for q in cs)
deps=bpy.context.evaluated_depsgraph_get();rows=[]
for x,y in [(538,169),(552,166),(550,201),(590,93),(543,111),(570,190),(510,190)]:
 d=cam.matrix_world.to_quaternion()@Vector((xlo+(x+.5)/640*(xhi-xlo),yhi-(y+.5)/360*(yhi-ylo),cs[0].z))
 h,p,n,f,o,_=s.ray_cast(deps,cam.matrix_world.translation,d.normalized(),distance=100)
 rows.append(dict(pixel=[x,y],hit=h,object=o.name if h else None,point=list(p) if h else None))
bounds=[]
for ob in s.objects:
 if ob.type=='MESH' and (ob.name.startswith('MAIN_L2_core') or ob.name=='MAIN_L2_master_hearth'):
  pts=[ob.matrix_world@Vector(v) for v in ob.bound_box]
  bounds.append(dict(object=ob.name,bounds=[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]))
report=dict(scene_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),camera=list(cam.location),rays=rows,objects=bounds)
(root/'qa/closet07-masonry-probe.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
