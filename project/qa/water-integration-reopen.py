"""Fresh-process check of saved integrated water and unchanged shape-key data."""
import bpy,hashlib,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'scripts'))
import water_integration
source=root/'scene/Fallingwater_iteration03.blend'
saved=root/'scene/Fallingwater_fluid_integrated_run05.blend'
reference=json.loads((root/'qa/water-integration-run05.json').read_text(encoding='utf-8'))
assert hashlib.sha256(source.read_bytes()).hexdigest()==water_integration.FROZEN03_SHA
bpy.ops.wm.open_mainfile(filepath=str(saved))
scene=bpy.context.scene
assert scene.frame_current==48
surface=scene.objects[water_integration.SURFACE]
actual=water_integration._geometry_signature(surface)
assert actual==reference['surface_edit']['before']
assert water_integration._normal_stats(surface)['downward']==0
domain=scene.objects['WATER_Mantaflow_Local_Cascade']
ev=domain.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
vertices=len(mesh.vertices);polygons=len(mesh.polygons);ev.to_mesh_clear()
assert vertices==420682 and polygons==842172
assert all(scene.objects[name].hide_render for name in reference['hidden_old_local_water_objects'])
out={'status':'PASS_SAVED_INTEGRATED_CHECKPOINT_REOPEN','frame':scene.frame_current,
     'source03_sha256_unchanged':True,'all_vertex_shape_key_and_driver_signatures_preserved':True,
     'original_vertex_count':len(surface.data.vertices),'remaining_original_faces':len(surface.data.polygons),
     'fluid_vertices':vertices,'fluid_polygons':polygons,'all_old_local_water_hidden':True,
     'scope':'Original-path local reopen; not relocated final package, seam or temporal acceptance'}
(root/'qa/water-integration-reopen.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out),flush=True)
