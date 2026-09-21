"""Exactly two independent Study/Laundry diagnostics from the frozen 06 preview."""
import hashlib,json,sys,time
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import eevee_preview,eevee_glass
SOURCE=ROOT/'scene/Fallingwater_preview_iteration06.blend'
EXPECTED='e317241899808995f049e8d3343eac96c591cbecfddaa980949d6babb51ccce6'
LAUNDRY='FW_FURN_GUEST_B1_LAUNDRY_practical_ceiling_lamp_C_05_bulb_photometric_proxy'

def lights(scene):
    return {o.name:{'matrix':[list(r) for r in o.matrix_world],'energy':o.data.energy,
        'color':list(o.data.color),'type':o.data.type,'shadow':o.data.use_shadow,
        'radius':getattr(o.data,'shadow_soft_size',None),
        'blocker_collection':o.light_linking.blocker_collection.name if o.light_linking.blocker_collection else None}
        for o in scene.objects if o.type=='LIGHT'}

for label,camera in [('study_raymodule_off','CAM_MAIN_L3_STUDY_B'),
                     ('laundry_own_filament_excluded','CAM_GUEST_B1_LAUNDRY_B')]:
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
    output=ROOT/'qa'/('eevee-iteration06-followup-'+label)
    assert not output.with_suffix('.png').exists(), 'Existing diagnostic preserved'
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    s=bpy.context.scene;s.frame_set(1)
    assert s.render.engine=='BLENDER_EEVEE' and s.eevee.use_raytracing and not s.eevee.use_fast_gi
    s.camera=s.objects[camera];s.view_settings.exposure=.8
    s.eevee.taa_render_samples=32
    s.render.threads_mode='FIXED';s.render.threads=4
    s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage=960,540,100
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
    before_lights=lights(s)
    before_volumes={o.name:o.data.intensity for o in s.objects if o.type=='LIGHT_PROBE' and o.data.type=='VOLUME'}
    before_cycles=eevee_glass.cycles_signature();before_geometry=eevee_glass.geometry_signature(s)
    report={'status':'RUNNING','variant':label,'source_sha256':EXPECTED,'camera':camera,
        'camera_location':list(s.camera.location),'camera_rotation':list(s.camera.rotation_euler),
        'lens':s.camera.data.lens,'exposure':.8,'resolution':[960,540],'samples':32,'cpu_preparation_threads':4,
        'before_lights':before_lights,'before_volume_intensities':before_volumes,
        'cycles_glass_surface_before':before_cycles,'glazing_geometry_before':before_geometry,
        'production_saved':False,'gi_rebaked':False}
    if label=='study_raymodule_off':
        s.eevee.use_raytracing=False
        report['change']={'property':'scene.eevee.use_raytracing','before':True,'after':False,
            'scope':'Entire ray module disabled; Fast GI was already off in the source. Baked volume GI and real shadow flags retained.'}
    else:
        assert before_lights[LAUNDRY]['blocker_collection'] is None
        report['change']=eevee_preview.apply_emitter_shadow_exclusions(s,[LAUNDRY])
    after_lights=lights(s)
    assert before_volumes=={o.name:o.data.intensity for o in s.objects if o.type=='LIGHT_PROBE' and o.data.type=='VOLUME'}
    for name,before in before_lights.items():
        after=dict(after_lights[name])
        if label=='laundry_own_filament_excluded' and name==LAUNDRY:
            assert after['blocker_collection'] is not None
            after['blocker_collection']=before['blocker_collection']
        assert before==after, 'Unexpected light setting change: '+name
    assert eevee_glass.cycles_signature()==before_cycles and eevee_glass.geometry_signature(s)==before_geometry
    report['after_lights']=after_lights
    report['actual_flags']={'raytracing':s.eevee.use_raytracing,'fast_gi':s.eevee.use_fast_gi,
        'all_visible_light_shadows':all(o.data.use_shadow for o in s.objects if o.type=='LIGHT' and not o.hide_render)}
    report['invariants_passed']=True
    s.render.filepath=str(output.with_suffix('.png'))
    record_path=output.with_suffix('.json')
    record_path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('FOLLOWUP_START '+label,flush=True)
    start=time.perf_counter();bpy.ops.render.render(write_still=True)
    report.update(status='RENDERED',seconds=time.perf_counter()-start,path=s.render.filepath,
        sha256=hashlib.sha256(Path(s.render.filepath).read_bytes()).hexdigest(),visual_acceptance='NOT_REVIEWED')
    report['exposure_bracket']=[]
    for ev in [1.6,2.4]:
        s.view_settings.exposure=ev
        p=output.with_name(output.name+'_EV'+str(ev).replace('.','p')).with_suffix('.png')
        assert not p.exists(), 'Existing exposure export preserved'
        bpy.data.images['Render Result'].save_render(str(p),scene=s)
        report['exposure_bracket'].append({'exposure':ev,'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'same_linear_render':True,'viewed':False})
    s.view_settings.exposure=.8
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
    report['source_unchanged']=True
    record_path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('FOLLOWUP_COMPLETE '+json.dumps({'variant':label,'seconds':report['seconds'],'sha256':report['sha256']}),flush=True)
