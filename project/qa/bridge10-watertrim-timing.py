import bpy,json,sys,time,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'qa'))
import bridge_watertrim10 as entry
import shrub08_auditlib as audit
SOURCE=ROOT/'scene/Fallingwater_bridge10_endfix.blend';assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==entry.SOURCE_SHA256
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));o=bpy.data.objects[entry.WATER_NAME]
r={'source_sha256':entry.SOURCE_SHA256,'shape_keys':{'name':o.data.shape_keys.name,'keys':[audit.props(k) for k in o.data.shape_keys.key_blocks], 'animation':audit.props(o.data.shape_keys.animation_data) if o.data.shape_keys.animation_data else None},'frames':[],'rendered':False}
r['application']=entry.apply()
for frame in [1,24]:
 print('BOOLEAN_TIMING_BEGIN',frame,flush=True);t=time.monotonic();bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles()
 r['frames'].append({'frame':frame,'seconds':time.monotonic()-t,'vertices':len(m.vertices),'faces':len(m.polygons),'triangles':len(m.loop_triangles)})
 ev.to_mesh_clear();print('BOOLEAN_TIMING_END',json.dumps(r['frames'][-1]),flush=True)
(ROOT/'qa/bridge10-watertrim-timing.json').write_text(json.dumps(r,indent=2),encoding='utf8')
print('BOOLEAN_TIMING_DONE',flush=True)
