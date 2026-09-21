"""One bounded real-time profile test; no GI bake or production mutation."""
import hashlib,json,time
from pathlib import Path
import bpy
root=Path(__file__).resolve().parents[1]
source=root/'qa/eevee-iteration07-novolume/Fallingwater_preview_iteration07_no_volume.blend'
output=root/'qa/eevee-iteration07-small-ao';output.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene
assert not any(o.type=='LIGHT_PROBE' and o.data.type=='VOLUME' for o in s.objects)
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=32
s.eevee.use_fast_gi=True
s.eevee.fast_gi_method='AMBIENT_OCCLUSION_ONLY'
s.eevee.fast_gi_distance=.6
s.eevee.fast_gi_thickness_near=.08
s.eevee.fast_gi_quality=.5
s.eevee.fast_gi_step_count=16
s.eevee.fast_gi_ray_count=4
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
s.camera=s.objects['CAM_MAIN_L3_STUDY_B'];s.frame_set(48);s.view_settings.exposure=.8
s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8'
s.render.filepath=str(output/'CAM_MAIN_L3_STUDY_B_EV0p8.png')
report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'scope':'Preview approximation candidate only; small-distance AO profile plus display exposure. Not a single-parameter causal claim. No VOLUME GI, added lights or production changes.',
 'profile':{p.identifier:str(getattr(s.eevee,p.identifier)) for p in s.eevee.bl_rna.properties if 'fast_gi' in p.identifier},
 'frame':48,'resolution':[960,540],'samples':32,'status':'NOT_RUN'}
started=time.perf_counter();bpy.ops.render.render(write_still=True)
report['seconds']=time.perf_counter()-started
for ev in [0.,1.6,2.4]:
 s.view_settings.exposure=ev
 bpy.data.images['Render Result'].save_render(str(output/('CAM_MAIN_L3_STUDY_B_EV'+str(ev).replace('.','p')+'.png')),scene=s)
report['status']='RENDERED_NOT_VISUALLY_REVIEWED'
s.view_settings.exposure=.8
bpy.ops.wm.save_as_mainfile(filepath=str(output/'Fallingwater_preview_small_ao_candidate07.blend'))
(output/'report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report))
