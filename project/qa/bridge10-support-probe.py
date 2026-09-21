import json,sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'))
import shrub08_auditlib as a
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene/Fallingwater_iteration09.blend'))
bpy.context.scene.frame_set(48)
tb,_=a.world_bvh([bpy.data.objects['SITE_Continuous_BearRun_Terrain']],True)
pathobjs=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('SITE_Path_bridge_')]
pb,po=a.world_bvh(pathobjs,True)
positions=[]
for side,xs in [('W',[23.3,23.8,24.5,25.14,25.43]),('E',[29.47,29.70,30.4,30.9,31.4])]:
 for y in [-4.2,-3.1,-2.5,6.4,6.7,7.0,7.8]:
  for x in xs:
   t=tb.ray_cast(Vector((x,y,30)),Vector((0,0,-1)),80)[0]
   p,_,pi,_=pb.ray_cast(Vector((x,y,30)),Vector((0,0,-1)),80)
   positions.append({'side':side,'xy':[x,y],'terrain_z':t.z if t else None,'path':po[pi] if p else None,'path_z':p.z if p else None})
report={'stations':positions,'cameras':{o.name:list(o.matrix_world.translation) for o in bpy.context.scene.objects if o.type=='CAMERA'},'path_vertices':{o.name:[list(o.matrix_world@v.co) for v in o.data.vertices] for o in pathobjs}}
(ROOT/'qa/bridge10-support-probe.json').write_text(json.dumps(report,indent=2))
print('bridge stations',json.dumps(positions))
