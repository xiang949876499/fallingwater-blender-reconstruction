"""Two independent Living light-source diagnostics; frozen source, never saved."""
import hashlib, json, time
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'scene/Fallingwater_preview_iteration05.blend'
EXPECTED='b855de89492af8ae31ae4d53bb2674f518ea13cf2e8f1585b2b9a31b35511939'
for variant in ['sun_shadows_off', 'volume_intensity_zero']:
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
    report={'variant':variant,'source':str(SOURCE),'source_sha256':EXPECTED,'camera':s.camera.name,
        'location':list(s.camera.location),'rotation':list(s.camera.rotation_euler),'exposure':.8,
        'resolution':[960,540],'samples':32,'status':'RUNNING','production_saved':False,
        'gi_rebaked':False,'geometry_and_materials_unchanged':True,'changes':[]}
    if variant=='sun_shadows_off':
        for obj in s.objects:
            if obj.type=='LIGHT' and obj.data.type=='SUN' and not obj.hide_render:
                report['changes'].append({'object':obj.name,'property':'use_shadow','before':obj.data.use_shadow,'after':False})
                obj.data.use_shadow=False
        assert len(report['changes'])==1
    else:
        for obj in s.objects:
            if obj.type=='LIGHT_PROBE' and obj.data.type=='VOLUME':
                report['changes'].append({'object':obj.name,'property':'intensity','before':obj.data.intensity,'after':0})
                obj.data.intensity=0
        assert len(report['changes'])==7
    output=ROOT/'qa'/('eevee-iteration05-living-'+variant)
    assert not output.with_suffix('.png').exists(), 'Existing output preserved'
    report_path=output.with_suffix('.json')
    report_path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    s.render.filepath=str(output.with_suffix('.png'))
    start=time.perf_counter()
    bpy.ops.render.render(write_still=True)
    report.update(status='RENDERED',seconds=time.perf_counter()-start,path=s.render.filepath,
        sha256=hashlib.sha256(Path(s.render.filepath).read_bytes()).hexdigest(),visual_acceptance='NOT_REVIEWED')
    report_path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('LIVING_LIGHT_DIAGNOSTIC '+json.dumps(report),flush=True)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
