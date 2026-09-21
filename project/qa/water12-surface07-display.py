"""Add a foot diagnostic camera to the independent complete static scene."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import hybrid_water as h
src=ROOT/'scene/Fallingwater_water12_surface07.blend';out=ROOT/'scene/Fallingwater_water12_surface07_display.blend';assert not out.exists()
expected='46bbc92557fe24259accae4e2d808c49f74331d4cf024bc00c7201519548fef7';assert hashlib.sha256(src.read_bytes()).hexdigest()==expected
bpy.ops.wm.open_mainfile(filepath=str(src));assert not any(m.type=='FLUID' for ob in bpy.data.objects for m in ob.modifiers)
o=bpy.data.objects['WATER12_Continuous_Upper_9Branches_Pool_OuterRiver'];shape=h.shape_hash(o)
camdata=bpy.data.cameras.new('CAM_WATER12_FOOT');cam=bpy.data.objects.new('CAM_WATER12_FOOT',camdata);bpy.context.scene.collection.objects.link(cam)
cam.location=h.point(7,6,-2.9);target=h.point(1.3,0,-4.7);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
camdata.lens=32;camdata.sensor_width=36;camdata.clip_start=.05;camdata.clip_end=5000
bpy.context.view_layer.update();direction=(target-cam.location).normalized()
hit=bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),cam.location,direction,distance=(target-cam.location).length)
report={'source_scene':str(src),'source_sha256':expected,'output':str(out),'camera_added':'CAM_WATER12_FOOT',
   'camera_location':list(cam.location),'target':list(target),'lens_mm':32,'center_ray_first_object':hit[4].name if hit[0] else None,
   'existing_cameras_preserved':True,'water_mesh_world_sha256':shape,'frame':48,'water_geometry_unchanged':h.shape_hash(o)==shape,
   'recommended_root_views':['CAM_HERO','CAM_WATER_DETAIL','CAM_WATER12_FOOT'],'suggested_preview':{'width':1280,'height':720,'samples':64,'engine':'CYCLES','device':'CPU','threads':8,'frame':48},
   'display_only_changes':['Added one diagnostic camera; no material, light, water head or geometry changes'],
   'no_render_started':True,'no_cache_access':True,'production_install':False,'visual_status':'NOT_RENDERED_OR_VIEWED_BY_THIS_AGENT'}
bpy.ops.wm.save_as_mainfile(filepath=str(out));report['output_sha256']=hashlib.sha256(out.read_bytes()).hexdigest()
(ROOT/'qa/water12-surface07-display.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('WATER12_DISPLAY_READY',report,flush=True)
