"""Three one-factor EEVEE dark-patch diagnostics; no scene is saved."""
import hashlib
import json
import sys
import time
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'scene/Fallingwater_preview_iteration05.blend'
EXPECTED='b855de89492af8ae31ae4d53bb2674f518ea13cf2e8f1585b2b9a31b35511939'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
for variant in ['raytracing_off','volume_intensity_zero','practical_shadows_off']:
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED, 'Frozen source changed'
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    s=bpy.context.scene;s.frame_set(1)
    s.camera=s.objects['CAM_MAIN_B_BATH_B'];s.view_settings.exposure=.8
    s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=32
    s.render.threads_mode='FIXED';s.render.threads=4
    s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
    record={'variant':variant,'source':str(SOURCE),'source_sha256':EXPECTED,'camera':s.camera.name,
        'camera_location':list(s.camera.location),'camera_rotation':list(s.camera.rotation_euler),
        'exposure':s.view_settings.exposure,'engine':s.render.engine,'samples':32,'resolution':[960,540],
        'status':'RUNNING','production_scene_saved':False,'gi_rebaked':False,'changes':[]}
    record['eevee_before']={p.identifier:str(getattr(s.eevee,p.identifier)) for p in s.eevee.bl_rna.properties
        if p.identifier.startswith('fast_gi') or p.identifier in ['use_fast_gi','use_raytracing']}
    if variant=='raytracing_off':
        record['changes'].append({'property':'scene.eevee.use_raytracing','before':s.eevee.use_raytracing,'after':False})
        s.eevee.use_raytracing=False
    elif variant=='volume_intensity_zero':
        for o in s.objects:
            if o.type=='LIGHT_PROBE' and o.data.type=='VOLUME':
                record['changes'].append({'object':o.name,'property':'intensity','before':o.data.intensity,'after':0})
                o.data.intensity=0
        assert len(record['changes'])==7
    else:
        for o in s.objects:
            if o.type=='LIGHT' and not o.hide_render and o.get('visible_source') and o.get('visible_source') in bpy.data.objects:
                record['changes'].append({'object':o.name,'visible_source':o['visible_source'],
                    'property':'use_shadow','before':o.data.use_shadow,'after':False,
                    'energy_unchanged':o.data.energy,'location_unchanged':list(o.matrix_world.translation)})
                o.data.use_shadow=False
        assert record['changes'], 'No visible practical proxies found'
    out=ROOT/'qa'/('eevee-iteration05-dark-'+variant)
    record_path=out.with_suffix('.json')
    if out.with_suffix('.png').exists():raise RuntimeError('Preserve existing variant output')
    record_path.write_text(json.dumps(record,indent=2),encoding='utf-8')
    s.render.filepath=str(out.with_suffix('.png'))
    start=time.perf_counter();bpy.ops.render.render(write_still=True)
    record.update(status='RENDERED',seconds=time.perf_counter()-start,path=s.render.filepath,
        sha256=hashlib.sha256(Path(s.render.filepath).read_bytes()).hexdigest(),visual_acceptance='NOT_REVIEWED')
    record_path.write_text(json.dumps(record,indent=2),encoding='utf-8')
    print('DARK_PATCH_DIAGNOSTIC '+json.dumps(record),flush=True)
