"""One guarded exact core cut on new self-valid surface05b, not inherited water."""
import sys,json,hashlib,time
from pathlib import Path
import bpy,bmesh,numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import water_surface12 as g
import hybrid_water as h
source=ROOT/'scene/Fallingwater_water12_surface05b.blend';output=ROOT/'scene/Fallingwater_water12_surface06a.blend'
assert not output.exists();assert hashlib.sha256(source.read_bytes()).hexdigest()=='6366d4f992faab07a0407462ac7332014c1e7c0b4b196ecb7e49bf470817203a'
bpy.ops.wm.open_mainfile(filepath=str(source));assert not any(m.type=='FLUID' for ob in bpy.data.objects for m in ob.modifiers)
o=bpy.data.objects['WATER12_Continuous_Upper_9Branches_Pool_OuterRiver'];before=h.topology(o);assert before['nonmanifold_edges']==0
core=bpy.data.objects['SITE_Core_Continuous_Fractured_Sandstone'];corehash=h.shape_hash(core)
v,f=g.geometry(core);me=bpy.data.meshes.new('W12_READONLY_CORE_TRIANGLES_OPERAND');me.from_pydata(v,[],f);me.update()
operand=bpy.data.objects.new('W12_06_TEMP_CORE_OPERAND',me);bpy.context.scene.collection.objects.link(operand)
names=json.loads(o['water12_tag_names']);names.append('closure_core_cut');o['water12_tag_names']=json.dumps(names)
attr=me.attributes.new('water12_part','INT','FACE');attr.data.foreach_set('value',[len(names)-1]*len(me.polygons))
start=time.perf_counter();print('W12_NEW_VALID_CORE_CUT_START',before,flush=True)
mod=o.modifiers.new('ExactFrozenCoreCut_NewValidWaterOnly','BOOLEAN');mod.solver='EXACT';mod.operation='DIFFERENCE';mod.object=operand;mod.use_self=True
for ob in bpy.context.selected_objects:ob.select_set(False)
o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.object.modifier_apply(modifier=mod.name)
elapsed=time.perf_counter()-start
bpy.data.objects.remove(operand,do_unlink=True)
bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
after=h.topology(o);report={'input_scene':str(source),'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
  'frozen_core_geometry_sha256':corehash,'old_self_intersecting_water_not_used':True,'before':before,'after':after,'elapsed_s':elapsed,
  'status':'PASS_TOPOLOGY_VOLUME_GUARD' if after['nonmanifold_edges']==0 and 0<after['signed_volume_m3']<=before['signed_volume_m3']+.00001 else 'FAIL_CORE_CUT_GUARD',
  'geometry_volume_not_physical_water_quantity':True,'no_simulation_or_render':True,'deep_caps_not_targeted_as_physics':True}
print('W12_NEW_VALID_CORE_CUT_END',report,flush=True)
if report['status']=='PASS_TOPOLOGY_VOLUME_GUARD':
    tags=[names[q.value] for q in o.data.attributes['water12_part'].data];report['audit']=g.audit_mesh(o,tags)
    bpy.ops.wm.save_as_mainfile(filepath=str(output));report['output']=str(output);report['output_sha256']=hashlib.sha256(output.read_bytes()).hexdigest()
else:
    failed=ROOT/'scene/Fallingwater_water12_surface06a_failed.blend';bpy.ops.wm.save_as_mainfile(filepath=str(failed));report['failed_output']=str(failed)
assert h.shape_hash(core)==corehash
(ROOT/'qa/water12-surface06a.json').write_text(json.dumps(report,indent=2),encoding='utf8')
