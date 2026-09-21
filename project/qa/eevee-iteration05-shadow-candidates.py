"""Bounded Bath point-shadow precision candidates; no production saves."""
import hashlib,json,time
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'scene/Fallingwater_preview_iteration05.blend'
EXPECTED='b855de89492af8ae31ae4d53bb2674f518ea13cf2e8f1585b2b9a31b35511939'
for label,clip in [('jittered',None),('jittered_near5mm',.005)]:
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;s.frame_set(1)
    light=next(o for o in s.objects if o.type=='LIGHT' and 'MAIN_B_BATH' in o.name)
    before={k:getattr(light.data,k) for k in ['use_shadow','use_shadow_jitter','shadow_jitter_overblur','shadow_buffer_clip_start','shadow_soft_size','energy']}
    light.data.use_shadow_jitter=True;light.data.shadow_jitter_overblur=0
    if clip is not None:light.data.shadow_buffer_clip_start=clip
    after={k:getattr(light.data,k) for k in before}
    s.camera=s.objects['CAM_MAIN_B_BATH_B'];s.view_settings.exposure=.8
    s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=32
    s.render.threads_mode='FIXED';s.render.threads=4
    s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
    output=ROOT/'qa'/('eevee-iteration05-shadow-'+label)
    if output.with_suffix('.png').exists():raise RuntimeError('Existing output preserved')
    s.render.filepath=str(output.with_suffix('.png'))
    report={'source_sha256':EXPECTED,'variant':label,'light':light.name,'before':before,'after':after,
        'light_position_unchanged':list(light.matrix_world.translation),'light_energy_and_radius_unchanged':True,
        'geometry_unchanged':True,'all_shadows_still_enabled':all(o.data.use_shadow for o in s.objects if o.type=='LIGHT' and not o.hide_render),
        'exposure':.8,'camera':s.camera.name,'status':'RUNNING','production_saved':False,'gi_rebaked':False}
    output.with_suffix('.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    start=time.perf_counter();bpy.ops.render.render(write_still=True)
    report.update(status='RENDERED',seconds=time.perf_counter()-start,path=s.render.filepath,
        sha256=hashlib.sha256(Path(s.render.filepath).read_bytes()).hexdigest(),visual_acceptance='NOT_REVIEWED')
    output.with_suffix('.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('SHADOW_CANDIDATE '+json.dumps(report),flush=True)
