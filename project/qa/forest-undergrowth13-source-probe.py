"""Read frozen combined11 roots, accepted meshes and current cameras; no save."""
import bpy,json,hashlib,sys,re
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];Q=R/'qa';sys.path[:0]=[str(R/'scripts'),str(Q)]
import understory_detail as approved
import shrub08_auditlib as audit
P=R/'scene/Fallingwater_navigation_candidate11a.blend'
SHA='d66ded0f23b7d19c20b81d2f59f94aa5aa77747be4568e85e1d105395fc219ff'
assert hashlib.sha256(P.read_bytes()).hexdigest()==SHA
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;s.frame_set(48);dep=bpy.context.evaluated_depsgraph_get()
cameras=['CAM_HERO','CAM_MAIN_OVERVIEW','CAM_MAIN_L1_LOGGIA_B']
# The root's actually viewed overview used this recorded external35mm camera,
# not the saved overview pose. Apply only in this unsaved source probe.
overview={'location':[27.862123489379883,-21.79529571533203,27.94647979736328],
          'target':[3.700000047683716,7.0,3.200000047683716],'lens':35,'exposure':.8,'shift_x':0,'shift_y':0}
cam=s.objects['CAM_MAIN_OVERVIEW'];cam.location=overview['location'];cam.rotation_euler=(Vector(overview['target'])-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens=35;cam.data.shift_x=cam.data.shift_y=0;bpy.context.view_layer.update()
assets=[]
for index in (2,3):
 for key in ('old_branch_mesh','old_leaf_mesh','new_branch_mesh','new_leaf_mesh'):
  name=approved.APPROVED['assets'][str(index)][key];m=bpy.data.meshes[name];m.calc_loop_triangles()
  assets.append({'name':name,'signature':approved.mesh_signature(m),'vertices':len(m.vertices),'triangles':len(m.loop_triangles),
                 'bounds':[[min(v.co[i] for v in m.vertices),max(v.co[i] for v in m.vertices)] for i in range(3)],
                 'materials':[mat.name if mat else None for mat in m.materials]})
accepted={r['name'] for r in approved.APPROVED['objects']};rows=[]
for ob in s.objects:
 if not re.fullmatch(r'TREE_Understory_\d{4}_Leaves',ob.name):continue
 root=ob.matrix_world.translation
 projected={}
 for name in cameras:
  p=world_to_camera_view(s,s.objects[name],root)
  projected[name]=[(p.x*1280),((1-p.y)*720),p.z]
 rows.append({'name':ob.name,'branch':ob.name.replace('_Leaves','_Branches'),'mesh':ob.data.name,
              'root':list(root),'scale':list(ob.scale),'matrix':[list(r) for r in ob.matrix_world],
              'accepted16':ob.name in accepted,'projected_root_1280x720':projected})
pixels={'CAM_HERO':[(100,560),(220,625),(315,538),(1120,532),(1220,427)],
        'CAM_MAIN_OVERVIEW':[(240,195),(305,283),(1116,310),(1170,445),(866,48)],
        'CAM_MAIN_L1_LOGGIA_B':[(430,250),(350,150),(400,330)]}
rayrows=[]
terrain_bvh,_=audit.world_bvh([s.objects['SITE_Continuous_BearRun_Terrain']],True)
for name,points in pixels.items():
 cam=s.objects[name];corners=cam.data.view_frame(scene=s);eye=cam.matrix_world.translation
 for x,y in points:
  # Camera.view_frame returns TR,BR,BL,TL; interpolate in the local camera plane.
  top_left=corners[3];top_right=corners[0];bottom_left=corners[2]
  local=top_left+(top_right-top_left)*(x/1280)+(bottom_left-top_left)*(y/720)
  direction=(cam.matrix_world.to_3x3()@local).normalized()
  hit,point,normal,idx,obj,mat=s.ray_cast(dep,eye,direction,distance=150)
  ground=terrain_bvh.ray_cast(eye,direction,150)[0]
  rayrows.append({'camera':name,'pixel':[x,y],'first_object':obj.name if obj else None,'point':list(point) if hit else None,
                  'terrain_direct_ray_point':list(ground) if ground is not None else None})
texts={t.name:t.as_string() for t in bpy.data.texts if t.name in ('FW_CONFIG.json','FW_BUILD_INPUTS.json')}
out={'source':str(P),'source_sha256':SHA,'frame':48,'assets':assets,'roots':rows,'camera_count':sum(o.type=='CAMERA' for o in s.objects),
     'camera_names':cameras,'pixel_first_hits':rayrows,'source_config_texts':texts,'saved':False,'rendered':False,
     'terrain_materials':[m.name for m in s.objects['SITE_Continuous_BearRun_Terrain'].data.materials],
     'overview_image_external_override':overview,'source_file_changed':False}
(Q/'forest-undergrowth13-source-probe.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:out[k] for k in ('assets','camera_count','pixel_first_hits','terrain_materials')},indent=2))
