import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];out=[]
for scene in ['Fallingwater_iteration09.blend','Fallingwater_main_interface_candidate10b.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(R/'scene'/scene));s=bpy.context.scene;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4;dg=bpy.context.evaluated_depsgraph_get();c=s.objects['CAM_MAIN_L1_LOGGIA_A'];fr=c.data.view_frame(scene=s);lo=[min(v[k] for v in fr) for k in (0,1)];hi=[max(v[k] for v in fr) for k in (0,1)]
 for x,y in [(100,200),(150,300),(270,200),(200,350),(260,390)]:
  d=(c.matrix_world.to_quaternion()@Vector((lo[0]+(x+.5)/960*(hi[0]-lo[0]),hi[1]-(y+.5)/540*(hi[1]-lo[1]),fr[0].z))).normalized();h,p,n,f,o,_=s.ray_cast(dg,c.matrix_world.translation,d,distance=100);out.append(dict(scene=scene,pixel=[x,y],object=o.name if h else None,point=list(p) if h else None))
(R/'qa/main-interface10-surface-check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
