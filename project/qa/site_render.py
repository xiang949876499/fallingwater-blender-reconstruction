exec(compile(open(r'D:\zx\test\project\qa\site_smoke.py',encoding='utf8').read(), 'site_smoke.py', 'exec'))
from mathutils import Vector
for obj in list(bpy.data.objects):
    if obj.name in ('Cube','Light','Camera'):bpy.data.objects.remove(obj,do_unlink=True)
world=bpy.context.scene.world;world.use_nodes=True
nodes=world.node_tree.nodes;links=world.node_tree.links
sky=nodes.new('ShaderNodeTexSky');sky.sky_type='MULTIPLE_SCATTERING';sky.sun_elevation=.72;sky.sun_rotation=2.05
links.new(sky.outputs['Color'],nodes.get('Background').inputs['Color']);nodes.get('Background').inputs['Strength'].default_value=.40
light=bpy.data.lights.new('SITE_TEST_Sun','SUN');light.energy=2.5;light.angle=.09
o=bpy.data.objects.new('SITE_TEST_Sun',light);bpy.context.scene.collection.objects.link(o);o.rotation_euler=(.64,-.38,-.65)
camd=bpy.data.cameras.new('SITE_TEST_Camera');cam=bpy.data.objects.new('SITE_TEST_Camera',camd);bpy.context.scene.collection.objects.link(cam)
cam.location=(-27,-34,12);target=Vector((10,9,1));cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler();camd.lens=37
scene=bpy.context.scene;scene.camera=cam;scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=960;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(root/'qa'/'site_overview.png');scene.view_settings.view_transform='AgX';scene.render.film_transparent=False
scene.frame_set(61);bpy.ops.render.render(write_still=True)
cam.location=(-7,-13,-2.7);cam.rotation_euler=(Vector((4.2,1,-2.8))-Vector(cam.location)).to_track_quat('-Z','Y').to_euler();camd.lens=36
scene.render.filepath=str(root/'qa'/'site_water_close.png');bpy.ops.render.render(write_still=True)
