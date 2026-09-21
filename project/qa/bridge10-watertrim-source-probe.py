import bpy,json,sys,hashlib,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'))
import shrub08_auditlib as a
SOURCE=ROOT/'scene/Fallingwater_bridge_candidate10_meshclean.blend'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='15260dcfd92783a4695ce7fc0de83072531e5c09564bcdb26dbf2f2ac6717588'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));o=bpy.data.objects['WATER_BearRun_Continuous_Upstream_Downstream']
r={'object':a.props(o),'data':a.props(o.data),'materials':[m.name for m in o.data.materials], 'base_vertices':len(o.data.vertices),'base_polygons':len(o.data.polygons),'modifiers':[(m.name,m.type,a.props(m)) for m in o.modifiers],'animation':a.props(o.animation_data) if o.animation_data else None,'shape_keys':o.data.shape_keys.name if o.data.shape_keys else None,'scene_frame_range':[bpy.context.scene.frame_start,bpy.context.scene.frame_end],'frames':[]}
for frame in [1,24,48,120,240]:
 t=time.monotonic();bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles()
 r['frames'].append({'frame':frame,'evaluated_vertices':len(m.vertices),'evaluated_polygons':len(m.polygons),'triangles':len(m.loop_triangles),'eval_s':time.monotonic()-t,'first_vertex':list(m.vertices[0].co),'last_vertex':list(m.vertices[-1].co)})
 ev.to_mesh_clear()
 r['frames'][-1]['physical']=a.physical_hash(o)
(ROOT/'qa/bridge10-watertrim-source-probe.json').write_text(json.dumps(r,indent=2),encoding='utf8')
print(json.dumps(r),flush=True)
