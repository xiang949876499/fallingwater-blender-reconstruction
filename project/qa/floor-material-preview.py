import bpy, sys, time, json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'scripts'))
import asset_materials
bpy.ops.wm.open_mainfile(filepath=str(root/'scene/Fallingwater_working.blend'))
s=bpy.context.scene
asset_materials.apply_material(bpy.data.materials['FW_stone_floor'],'slate_floor_02',root)
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=32
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.03
s.cycles.use_denoising=True;s.render.resolution_x=1280;s.render.resolution_y=720
s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.camera=bpy.data.objects['CAM_MAIN_L1_LIVING_A'];s.view_settings.exposure=3.2
s.render.filepath=str(root/'qa/floor-material-preview.png')
t=time.perf_counter();bpy.ops.render.render(write_still=True)
(root/'qa/floor-material-preview.json').write_text(json.dumps({'seconds':time.perf_counter()-t,'source':bpy.data.filepath,'camera':s.camera.name,'asset':'slate_floor_02','status':'RENDERED; visual review pending'},indent=2))
