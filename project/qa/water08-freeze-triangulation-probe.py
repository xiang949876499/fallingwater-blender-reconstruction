import bpy,numpy as np,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import importlib.util
sp=importlib.util.spec_from_file_location('freezer',Path(__file__).parent/'water08-freeze-helper.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
bpy.ops.wm.open_mainfile(filepath=str(m.OUTPUT));o=bpy.context.scene.objects[m.NAME];f=m.faces_of(o.data);base=m.coords(o.data.shape_keys.key_blocks[0].data)
act=(m.attribute_values(o.data,'H07_fall')>0)|(m.attribute_values(o.data,'H07_pond')>0)
bpy.context.scene.frame_set(3);ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();af=m.faces_of(me)
diff=np.where(np.any(f!=af,axis=1))[0]
n0=m.normals(base,af);n=m.normals(m.coords(me.vertices),af)
bad=np.flatnonzero((np.linalg.norm(n0,axis=1)>1e-9)&(np.einsum('ij,ij->i',n0,n)<0))
print('TRIANGULATION_PROBE',json.dumps({'different':len(diff),'active_different':int(np.any(act[af[diff]],axis=1).sum()),'basis_normal_bad_on_actual_triangles':bad.tolist(),'examples':[{'triangle':int(i),'basis':f[i].tolist(),'evaluated':af[i].tolist(),'coordinates':base[af[i]].tolist(),'active':act[af[i]].tolist()} for i in diff[:8]]}),flush=True)
