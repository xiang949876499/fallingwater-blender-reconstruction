import sys,json,math
from pathlib import Path
from types import SimpleNamespace
import bpy
from mathutils import Vector
root=Path('D:/zx/test/project');sys.path.insert(0,str(root/'scripts'))
from fwlib import collection
from materials import build_materials
import guest_house
bpy.ops.wm.read_factory_settings(use_empty=True)
ctx=SimpleNamespace(root=root,mats=build_materials(),collection=collection,config=json.loads((root/'config.json').read_text()))
rooms=guest_house.build(ctx)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD';scene.world=bpy.data.worlds.new('Guest QA World');scene.world.color=(.13,.15,.17)
scene.render.resolution_x=1100;scene.render.resolution_y=740;scene.render.resolution_percentage=100
camera=bpy.data.objects.new('Guest geometry QA camera',bpy.data.cameras.new('Guest geometry QA camera'));scene.collection.objects.link(camera);scene.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=48;camera.location=(55,12,46);camera.rotation_euler=(Vector((12,38,10))-camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(root/'qa/guest-geometry-overview.png');bpy.ops.render.render(write_still=True)
verts=sum(len(o.data.vertices) for o in scene.objects if o.type=='MESH');faces=sum(len(o.data.polygons) for o in scene.objects if o.type=='MESH')
report={'status':'module_build_pass','rooms':len(rooms),'objects':len(scene.objects),'vertices':verts,'faces':faces,'blender_version':bpy.app.version_string,'world_registration':ctx.config['guest_actual_registration'],'limitations':['XY frozen from site2; guest absolute Z remains C8.4m with range7.4–9.4m','WorkBench is geometry inspection, not photoreal visual acceptance','Per-room navigation and architecture/furniture integration not tested by this module check']}
(root/'qa/guest-geometry-build-report.json').write_text(json.dumps(report,indent=2))
(root/'qa/guest-geometry-world-rooms.json').write_text(json.dumps(rooms,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'qa/guest-geometry-check.blend'))
# Cutaway is a diagnostic only, upper-storey geometry is retained in saved full model.
for o in scene.objects:
 if o.type=='MESH' and ('ROOF' in o.name or 'UPPER' in o.name or o.name.startswith('GUEST_L2_') or 'CHIMNEY' in o.name):o.hide_render=True
camera.location=(26,16,56);camera.rotation_euler=(Vector((11,38,9))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=48
scene.render.filepath=str(root/'qa/guest-geometry-cutaway.png');bpy.ops.render.render(write_still=True)
print(json.dumps(report))
