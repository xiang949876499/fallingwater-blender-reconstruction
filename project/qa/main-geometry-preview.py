exec(open('D:/zx/test/project/qa/main-geometry-smoke.py',encoding='utf-8-sig').read())
from mathutils import Vector
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=1024;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH';scene.display.shading.show_object_outline=False
scene.display.shading.background_type='WORLD';scene.world.color=(.18,.18,.18)
camdata=bpy.data.cameras.new('MAIN_QA_CAMERA');cam=bpy.data.objects.new('MAIN_QA_CAMERA',camdata);scene.collection.objects.link(cam);scene.camera=cam
cam.location=(-24,-29,25);cam.rotation_euler=(Vector((3,9,3.3))-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=35
scene.render.filepath='D:/zx/test/project/qa/main-geometry-axon.png';bpy.ops.render.render(write_still=True)
cam.location=(3,10,55);cam.rotation_euler=(0,0,0);cam.rotation_euler=(Vector((3,10,0))-cam.location).to_track_quat('-Z','Y').to_euler();camdata.ortho_scale=38
scene.render.filepath='D:/zx/test/project/qa/main-geometry-top.png';bpy.ops.render.render(write_still=True)
