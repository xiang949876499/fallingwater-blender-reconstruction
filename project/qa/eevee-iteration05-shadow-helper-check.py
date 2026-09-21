"""Fresh-process helper round-trip and installed bulb shader check; no render/save."""
import hashlib, json, sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import eevee_preview, eevee_glass
source=ROOT/'scene/Fallingwater_preview_iteration05.blend'
expected='b855de89492af8ae31ae4d53bb2674f518ea13cf2e8f1585b2b9a31b35511939'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene
name='FW_FURN_MAIN_B_BATH_practical_ceiling_lamp_C_03_bulb_photometric_proxy'
light=s.objects[name]
before=(list(light.matrix_world.translation),light.data.energy,light.data.shadow_soft_size,light.data.use_shadow)
cycles_before=eevee_glass.cycles_signature()
geometry_before=eevee_glass.geometry_signature(s)
first=eevee_preview.apply_emitter_shadow_exclusions(s,[name])
second=eevee_preview.apply_emitter_shadow_exclusions(s,[name])
assert first[0]['created'] and not second[0]['created']
assert len(light.light_linking.blocker_collection.objects)==1
restore=eevee_preview.restore_emitter_shadow_exclusions(s)
assert restore==[name] and light.light_linking.blocker_collection is None
assert eevee_preview.restore_emitter_shadow_exclusions(s)==[]
assert before==(list(light.matrix_world.translation),light.data.energy,light.data.shadow_soft_size,light.data.use_shadow)
assert cycles_before==eevee_glass.cycles_signature()
assert geometry_before==eevee_glass.geometry_signature(s)
s.render.engine='CYCLES'
try:
    eevee_preview.apply_emitter_shadow_exclusions(s,[name])
except ValueError:
    guard_pass=True
else:
    raise AssertionError('EEVEE engine guard missing')
mat=bpy.data.materials['FW_service_clear_bulb_C']
bulb={'material':mat.name,'use_transparent_shadow':mat.use_transparent_shadow,
    'surface_render_method':mat.surface_render_method,
    'output_links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in mat.node_tree.links],
    'transparent_colors':[(n.name,list(n.inputs['Color'].default_value)) for n in mat.node_tree.nodes if n.type=='BSDF_TRANSPARENT']}
report={'status':'PASS','source_sha256':expected,'rendered':False,'saved':False,
    'first_apply':first,'second_apply':second,'restore':restore,'cycles_engine_guard':guard_pass,
    'light_energy_radius_pose_and_shadow_flags_unchanged':True,'cycles_surface_hash':cycles_before,
    'glazing_geometry_hash':geometry_before,'bulb_shadow_api':bulb}
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
(ROOT/'qa/eevee-iteration05-shadow-helper-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report),flush=True)
