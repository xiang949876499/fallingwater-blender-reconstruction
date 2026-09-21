import bpy, json, sys, importlib.util, time
from types import SimpleNamespace
from pathlib import Path
root=Path(r'D:\zx\test\project')
sys.path.insert(0,str(root/'scripts'))
import fwlib, materials
spec=importlib.util.spec_from_file_location('fw_site',root/'scripts'/'site.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
t=time.time()
ctx=SimpleNamespace(root=root,mats=materials.build_materials(),collection=fwlib.collection,config={})
result=module.build(ctx)
result['build_seconds']=time.time()-t
result['object_count']=len(bpy.data.objects)
result['vertices_unique']=sum(len(m.vertices) for m in bpy.data.meshes)
result['bad_coordinates']=sum(1 for obj in bpy.data.objects if obj.type=='MESH' for v in obj.data.vertices if any(abs(c)>1e6 for c in v.co))
water=bpy.data.objects['WATER_BearRun_Continuous_Upstream_Downstream']
sample=[]
foam_sample=[]
for frame in (1,61,121,181,241):
    bpy.context.scene.frame_set(frame)
    deps=bpy.context.evaluated_depsgraph_get()
    evaluated=water.evaluated_get(deps)
    m=evaluated.to_mesh()
    sample.append({'frame':frame,'v100':list(m.vertices[100].co)})
    evaluated.to_mesh_clear()
    foam=bpy.data.objects['WATER_Downstream_Advecting_Foam_00'].evaluated_get(deps)
    foam_sample.append({'frame':frame,'position':list(foam.matrix_world.translation),'scale':list(foam.scale)})
result['animation_sample']=sample
result['loop_vertex_error']=max(abs(a-b) for a,b in zip(sample[0]['v100'],sample[-1]['v100']))
result['advecting_foam_sample']=foam_sample
result['foam_loop_position_error']=max(abs(a-b) for a,b in zip(foam_sample[0]['position'],foam_sample[-1]['position']))
result['leaf_uv_meshes']=sum(1 for m in bpy.data.meshes if 'Leaves' in m.name and len(m.uv_layers)>0)
(root/'qa'/'site_smoke.json').write_text(json.dumps(result,indent=2),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'qa'/'site_smoke.blend'))
print('SITE_SMOKE_OK '+json.dumps({k:v for k,v in result.items() if k!='tree_positions'}))
