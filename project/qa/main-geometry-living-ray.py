import bpy,json
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='D:/zx/test/project/scene/Fallingwater_working.blend')
s=bpy.context.scene;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
cam=bpy.data.objects['CAM_MAIN_L1_LIVING_A'];dg=bpy.context.evaluated_depsgraph_get();v=cam.data.view_frame(scene=s)
mnx=min(p.x for p in v);mxx=max(p.x for p in v);mny=min(p.y for p in v);mxy=max(p.y for p in v);zz=v[0].z
report={'camera':list(cam.matrix_world.translation),'pixels':[]}
for px,py in [(225,490),(300,493),(350,498),(210,480),(160,261),(900,273),(1230,263),(728,482)]:
 origin=cam.matrix_world.translation.copy();dire=(cam.matrix_world.to_3x3()@Vector((mnx+(px+.5)/1280*(mxx-mnx),mxy-(py+.5)/720*(mxy-mny),zz))).normalized();hits=[]
 for i in range(4):
  ok,loc,n,idx,ob,m=s.ray_cast(dg,origin,dire,distance=150)
  if not ok:break
  hits.append({'object':ob.name,'location':list(loc),'normal':list(n)});origin=loc+dire*.005
 report['pixels'].append({'pixel':[px,py],'hits':hits})
Path('D:/zx/test/project/qa/main-geometry-living-ray.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
