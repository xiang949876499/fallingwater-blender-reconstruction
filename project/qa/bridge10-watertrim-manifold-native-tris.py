import bpy,bmesh,sys,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'qa'));sys.path.insert(0,str(R/'scripts'))
import bridge_watertrim10 as entry
import bridge10_watertrim_auditlib as t
bpy.ops.wm.open_mainfile(filepath=str(R/'scene/Fallingwater_bridge10_watertrim.blend'));w=bpy.data.objects[entry.WATER_NAME]
for name in entry.MASK_NAMES:
 m=bpy.data.objects[name].data;bm=bmesh.new();bm.from_mesh(m);bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY');bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free()
entry._evaluation_filter(w);w.modifiers.remove(w.modifiers[entry.TRI_NAME]);w.modifiers.move(len(w.modifiers)-1,1)
for m in w.modifiers:
 if m.type=='BOOLEAN':m.solver='MANIFOLD'
r=[]
for f in [1,24]:
 st=time.monotonic();bpy.context.scene.frame_set(f);bpy.context.view_layer.update();d=t.evaluate(w);r.append({'frame':f,'seconds':time.monotonic()-st,'quality':d['quality']});print('NO_EXPLICIT_TRI_MANIFOLD',json.dumps(r[-1]),flush=True)
(R/'qa/bridge10-watertrim-manifold-native-tris.json').write_text(json.dumps(r,indent=2),encoding='utf8')
