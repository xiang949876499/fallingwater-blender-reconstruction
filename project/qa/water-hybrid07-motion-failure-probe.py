import bpy,numpy as np,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import hybrid_motion as hm
import hybrid_water as h
bpy.ops.wm.open_mainfile(filepath=str(hm.OUTPUT));bpy.context.scene.frame_set(24)
o=bpy.data.objects['WATER_Hybrid07a_Continuous_River_Branch_Pool'];o.data.calc_loop_triangles()
f=np.array([tuple(t.vertices) for t in o.data.loop_triangles]);base=np.array([tuple(v.co) for v in o.data.shape_keys.key_blocks[0].data],np.float64)
ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();v=np.array([tuple(x.co) for x in me.vertices],np.float64)
def normals(x):
 tri=x[f];return np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
a=normals(base);b=normals(v);bad=np.where((np.sum(a*b,axis=1)<0)&(np.linalg.norm(a,axis=1)>1e-9))[0]
def volume(x):
 tri=(x-np.array([0,0,-5]))[f];return float(np.sum(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])))/6)
report={'base_render_triangle_volume_m3':volume(base),'frame24_render_triangle_volume_m3':volume(v),
 'flipped':[{'triangle':int(i),'base_points':base[f[i]].tolist(),'actual_points':v[f[i]].tolist(),'area_m2':float(np.linalg.norm(a[i])*.5)} for i in bad]}
h.write(ROOT/'qa/water-hybrid07-motion-failure-probe.json',report);print(json.dumps(report,indent=2),flush=True)
