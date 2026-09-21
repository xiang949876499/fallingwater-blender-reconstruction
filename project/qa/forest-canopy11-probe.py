import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'))
import shrub08_auditlib as audit
SOURCE=ROOT/'scene/Fallingwater_bridge10_endfix.blend'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='2a7630b8024c37bd768e563236807f8049469172c7e44b03379a450f91637063'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;scene.frame_set(48)
assets={};rows=[]
terrain,_=audit.world_bvh([scene.objects['SITE_Continuous_BearRun_Terrain']],True)
for obj in scene.objects:
 if obj.type!='MESH' or not obj.name.startswith('TREE_') or not obj.name.endswith('_Leaves') or 'Understory' in obj.name or 'Distant' in obj.name:continue
 if not obj.data.name.startswith('TREE_Asset_'):continue
 mesh=obj.data
 if mesh.name not in assets:
  mesh.calc_loop_triangles();coords=np.empty(len(mesh.vertices)*3,np.float32);mesh.vertices.foreach_get('co',coords);coords=coords.reshape(-1,3)
  area=sum(t.area for t in mesh.loop_triangles)
  assets[mesh.name]={'vertices':len(mesh.vertices),'polygons':len(mesh.polygons),'triangles':len(mesh.loop_triangles),'individual_leaf_count':mesh.get('individual_leaf_count'),'bounds':[coords.min(axis=0).tolist(),coords.max(axis=0).tolist()],'area_m2':area,'mesh_fingerprint':audit.mesh_fingerprint(mesh),'materials':[m.name for m in mesh.materials]}
 p=obj.matrix_world.translation;hit=terrain.ray_cast(Vector((p.x,p.y,80)),Vector((0,0,-1)),180)[0]
 projected={}
 for name in ('CAM_HERO','CAM_WATER_DETAIL','CAM_MAIN_L1_LOGGIA_B','CAM_MAIN_L1_LIVING_A'):
  cam=scene.objects.get(name)
  if cam:
   points=[world_to_camera_view(scene,cam,obj.matrix_world@Vector(v)) for v in obj.bound_box]
   projected[name]={'range_xy':[[min(q[i] for q in points),max(q[i] for q in points)] for i in range(2)],'depth':[min(q.z for q in points),max(q.z for q in points)]}
 rows.append({'name':obj.name,'branch':obj.name[:-7]+'_Branches','asset':mesh.name,'matrix':[list(r) for r in obj.matrix_world],'root':list(p),'root_gap_m':p.z-hit.z if hit else None,'bounds':audit.bounds(obj),'projected':projected})
out={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'frame':48,'assets':assets,'instances':rows,'materials':{m.name:audit.node_tree_state(m.node_tree) for m in bpy.data.materials if m.name.startswith('FW_Site_Textured_leaf')},'camera_count':sum(o.type=='CAMERA' for o in scene.objects),'rendered':False,'saved':False}
(ROOT/'qa/forest-canopy11-probe.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('FOREST_PROBE',json.dumps({'assets':{k:{f:v[f] for f in ('triangles','individual_leaf_count','area_m2','bounds')} for k,v in assets.items()},'instances':len(rows)}),flush=True)
