"""Frozen iteration06 preview runner with a no-render configuration regression check."""
import hashlib,json,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import eevee_preview
source=ROOT/'scene/Fallingwater_iteration06.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='172b76340d1224a2b98f415b21042d19ad7fba4d849543d7156beb17e5fcf055'
s=bpy.context.scene
s.eevee.use_fast_gi=True
compat=eevee_preview.configure(s,32)
assert compat['fast_gi'] is True and compat['fast_gi_selection_source']=='preserved_existing_setting'
explicit=eevee_preview.configure(s,32,fast_gi=False)
assert not s.eevee.use_fast_gi and not s['fw_eevee_use_fast_gi']
s.eevee.use_fast_gi=True
retained=eevee_preview.configure(s,32)
assert not s.eevee.use_fast_gi and retained['fast_gi_selection_source']=='saved_scene_property'
assert s.eevee.use_raytracing
check={'status':'PASS','default_backward_compatible':compat,'explicit_off':explicit,
    'saved_property_honored_after_flag_change':retained,'rendered':False,'source_saved':False}
(ROOT/'qa/eevee-iteration06-config-check.json').write_text(json.dumps(check,indent=2),encoding='utf-8')
print('CONFIG_CHECK '+json.dumps(check),flush=True)
eevee_preview.main()
