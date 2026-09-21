"""Read-only fresh-process preview settings and actual Cycles wrapper restoration."""
import hashlib,json,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import eevee_preview,eevee_glass,render_views
source=ROOT/'scene/Fallingwater_preview_iteration06.blend'
expected='e317241899808995f049e8d3343eac96c591cbecfddaa980949d6babb51ccce6'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene
name='FW_FURN_MAIN_B_BATH_practical_ceiling_lamp_C_03_bulb_photometric_proxy'
light=s.objects[name]
geometry_before=eevee_glass.geometry_signature(s)
cycles_before=eevee_glass.cycles_signature()
assert s.eevee.use_fast_gi is False and s['fw_eevee_use_fast_gi'] is False
assert json.loads(s['fw_eevee_self_emitter_light_names'])==[name]
assert light.light_linking.blocker_collection is not None
settings=eevee_preview.configure(s,32)
assert settings['fast_gi'] is False and settings['fast_gi_selection_source']=='saved_scene_property'
glass=eevee_glass.apply(s)
assert not bpy.data.materials['FW_glass'].use_raytrace_refraction
assert eevee_glass.geometry_signature(s)==geometry_before and eevee_glass.cycles_signature()==cycles_before
assert len(json.loads(s['eevee_probe_bake_json']))==7
assert all(o.data.use_shadow for o in s.objects if o.type=='LIGHT' and not o.hide_render)
pool=s.objects['CAM_GUEST_POOL']
assert (pool.location.x,pool.location.y,pool.location.z)==(41,37,11) and pool.data.lens==35
physical=render_views.configure_engine(s,'CYCLES',32,'CPU')
assert light.light_linking.blocker_collection is None
assert physical['preview_shadow_exclusions_restored']==[name]
assert 'fw_eevee_self_emitter_light_names' not in s
assert eevee_glass.cycles_signature()==cycles_before
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
report={'status':'PASS','source_sha256':expected,'rendered':False,'saved':False,
    'default_configure_retains_saved_fast_gi':settings,'glass_reapplied_after_configure':True,
    'glazing_geometry_hash':geometry_before,'original_cycles_glass_surface_hash':cycles_before,
    'seven_bake_records':True,'all_light_shadows_enabled':True,'corrected_guest_pool_pose_retained':True,
    'root_cycles_wrapper_restored_one_preview_shadow_link':physical,
    'scope':'No frame rendered. Original Cycles glass shader retained; shadow-link restoration separately tested through root wrapper.'}
(ROOT/'qa/eevee-iteration06-reopen-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report),flush=True)
