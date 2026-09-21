"""Separate EEVEE diffuse ambient from visible/reflected sky; isolated test."""
import bpy,json,hashlib,time
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=root/'qa/eevee-iteration07-small-ao/Fallingwater_preview_small_ao_candidate07.blend'
output=root/'qa/eevee-iteration07-diffuse-world';output.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
original=s.world;s.world=original.copy();s.world.name='FW_PREVIEW_DIFFUSE_WORLD_TEST'
n=s.world.node_tree.nodes;l=s.world.node_tree.links
out=next(x for x in n if x.type=='OUTPUT_WORLD' and x.is_active_output)
physical=out.inputs['Surface'].links[0].from_socket
background=physical.node
assert background.type=='BACKGROUND'
weak=n.new('ShaderNodeBackground');weak.name='EEVEE weak diffuse ambient'
weak.inputs['Strength'].default_value=.006
if background.inputs['Color'].is_linked:
 l.new(background.inputs['Color'].links[0].from_socket,weak.inputs['Color'])
else:weak.inputs['Color'].default_value=background.inputs['Color'].default_value
path=n.new('ShaderNodeLightPath');mix=n.new('ShaderNodeMixShader')
l.new(path.outputs['Is Diffuse Ray'],mix.inputs[0]);l.new(physical,mix.inputs[1]);l.new(weak.outputs[0],mix.inputs[2])
out.target='CYCLES';ee=n.new('ShaderNodeOutputWorld');ee.target='EEVEE';l.new(mix.outputs[0],ee.inputs['Surface'])
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=32
s.camera=s.objects['CAM_MAIN_L3_STUDY_B'];s.frame_set(48);s.view_settings.exposure=2.4
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.filepath=str(output/'CAM_MAIN_L3_STUDY_B_EV2p4.png')
started=time.perf_counter();bpy.ops.render.render(write_still=True)
report=dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),seconds=time.perf_counter()-started,
 diffuse_world_strength=.006,visible_glossy_world_strength=background.inputs['Strength'].default_value,
 world_light_path_support_source='https://developer.blender.org/docs/release_notes/5.1/eevee/',
 added_lights=0,bakes=0,status='RENDERED_VISUAL_NOT_RUN',scope='EEVEE-only art-directed diffuse ambient; copied world. Cycles output retains original background shader and physical lights unchanged.')
bpy.ops.wm.save_as_mainfile(filepath=str(output/'Fallingwater_preview_diffuse_world_candidate07.blend'))
(output/'report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
