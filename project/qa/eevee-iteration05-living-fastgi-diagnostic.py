"""Single Fast GI switch, retaining screen ray tracing and all real shadows/GI."""
import hashlib,json,time
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'scene/Fallingwater_preview_iteration05.blend'
EXPECTED='b855de89492af8ae31ae4d53bb2674f518ea13cf2e8f1585b2b9a31b35511939'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s=bpy.context.scene
s.frame_set(1)
s.camera=s.objects['CAM_MAIN_L1_LIVING_B']
s.view_settings.exposure=.8
s.render.engine='BLENDER_EEVEE'
s.eevee.taa_render_samples=32
s.render.threads_mode='FIXED'
s.render.threads=4
s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage=960,540,100
s.render.image_settings.file_format='PNG'
s.render.image_settings.color_mode='RGBA'
s.render.image_settings.color_depth='8'
before={k:getattr(s.eevee,k) for k in ['use_fast_gi','use_raytracing','ray_tracing_method','fast_gi_method']}
before['trace_max_roughness']=s.eevee.ray_tracing_options.trace_max_roughness
assert s.eevee.use_fast_gi and s.eevee.use_raytracing
s.eevee.use_fast_gi=False
output=ROOT/'qa/eevee-iteration05-living-fastgi_off'
assert not output.with_suffix('.png').exists(), 'Existing output preserved'
s.render.filepath=str(output.with_suffix('.png'))
record={'status':'RUNNING','source_sha256':EXPECTED,'variant':'use_fast_gi_false',
    'before':before,'change':{'property':'scene.eevee.use_fast_gi','before':True,'after':False},
    'camera':s.camera.name,'exposure':.8,'resolution':[960,540],'samples':32,
    'screen_raytracing_retained':s.eevee.use_raytracing,
    'all_light_shadows_retained':all(o.data.use_shadow for o in s.objects if o.type=='LIGHT' and not o.hide_render),
    'volume_intensities':{o.name:o.data.intensity for o in s.objects if o.type=='LIGHT_PROBE' and o.data.type=='VOLUME'},
    'materials_geometry_lights_unchanged':True,'production_saved':False,'gi_rebaked':False,
    'scope':'Disables rough-surface Fast GI horizon scan; 5.2.1 internally sets tracing max roughness to 1, keeping full ray tracing.'}
record_path=output.with_suffix('.json')
record_path.write_text(json.dumps(record,indent=2),encoding='utf-8')
start=time.perf_counter()
bpy.ops.render.render(write_still=True)
record.update(status='RENDERED',seconds=time.perf_counter()-start,path=s.render.filepath,
    sha256=hashlib.sha256(Path(s.render.filepath).read_bytes()).hexdigest(),visual_acceptance='NOT_REVIEWED')
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
record_path.write_text(json.dumps(record,indent=2),encoding='utf-8')
print('LIVING_FASTGI_DIAGNOSTIC '+json.dumps(record),flush=True)
