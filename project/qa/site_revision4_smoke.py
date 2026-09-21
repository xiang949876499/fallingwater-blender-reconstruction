import bpy, json, sys, importlib.util, time, hashlib, math
from pathlib import Path
from types import SimpleNamespace
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(r'D:\zx\test\project')
sys.path.insert(0,str(root/'scripts'))
import fwlib, materials
spec=importlib.util.spec_from_file_location('fw_site',root/'scripts'/'site.py')
site=importlib.util.module_from_spec(spec);spec.loader.exec_module(site)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
t=time.time()
ctx=SimpleNamespace(root=root,mats=materials.build_materials(),collection=fwlib.collection,config={})
result=site.build(ctx)
report={k:v for k,v in result.items() if k not in ('tree_positions','distant_forest_positions')}
cfg=json.loads((root/'data'/'site.json').read_text(encoding='utf8'))
site._resolve_guest(ctx,cfg);site._resolve_main(ctx,cfg)
cfg['_terrain_river_path']=list(reversed(cfg['river_upstream_extension'][1:]))+cfg['river_path']
terrain=bpy.data.objects['SITE_Continuous_BearRun_Terrain']
deps=bpy.context.evaluated_depsgraph_get();bvh=BVHTree.FromObject(terrain,deps)
counter=Counter(edge for polygon in terrain.data.polygons for edge in polygon.edge_keys)
boundary=[edge for edge,n in counter.items() if n==1]
bounds=cfg['terrain_bounds']
def outer(v):
    return min(abs(v.x-bounds[0]),abs(v.x-bounds[1]),abs(v.y-bounds[2]),abs(v.y-bounds[3]))<.001
report['terrain_boundary_edges']=len(boundary)
report['terrain_interior_boundary_edges']=sum(not all(outer(terrain.data.vertices[i].co) for i in edge) for edge in boundary)
report['terrain_overlapping_edges']=sum(n>2 for n in counter.values())
report['finite_coordinates']=all(math.isfinite(c) for mesh in bpy.data.meshes for v in mesh.vertices for c in v.co)
preserved=[]
for entry in cfg['preserved_vegetation']:
    obj=bpy.data.objects[entry['name']+'_Branches']
    error=max(abs(a-b) for a,b in zip(obj.location[:2],entry['location'][:2]))
    error=max(error,abs(obj.rotation_euler.z-entry['angle']))
    error=max(error,max(abs(a-b) for a,b in zip(obj.scale,entry['scale'])))
    ground=site._height(obj.location.x,obj.location.y,cfg)
    hit,_,_,_=bvh.ray_cast(Vector((obj.location.x,obj.location.y,100)),Vector((0,0,-1)),250)
    preserved.append({'name':entry['name'],'xy_rotation_scale_error':error,'z_ground_correction_m':obj.location.z-entry['location'][2],'ground_root_delta_m':obj.location.z-ground,
                      'actual_mesh_root_delta_m':obj.location.z-hit.z if hit else None})
report['preserved_tree_max_xy_rotation_scale_error']=max(r['xy_rotation_scale_error'] for r in preserved)
report['preserved_tree_roots']=preserved
report['preserved_tree_root_max_abs_delta_m']=max(abs(r['ground_root_delta_m']) for r in preserved)
report['preserved_tree_root_mesh_max_above_ground_m']=max(r['actual_mesh_root_delta_m'] or 0 for r in preserved)
main=json.loads((root/'data'/'main_house.json').read_text(encoding='utf8'))
caps=[]
for zone in cfg['building_exclusions']:
    if not zone['name'].startswith(('main_final_','guest_')):continue
    x0,x1,y0,y1=zone['bbox'];x=(x0+x1)/2;y=(y0+y1)/2
    loc,normal,face,distance=bvh.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),400)
    caps.append({'name':zone['name'],'sample_xy':[x,y],'terrain_z':loc.z if loc else None,
                 'allowed_ground_cap':zone['ground_cap'],'excess_m':max(0,loc.z-zone['ground_cap']) if loc else None})
report['building_ground_cap_samples']=caps
report['max_ground_cap_excess_m']=max(r['excess_m'] or 0 for r in caps)
source=(root/'scripts'/'site.py').read_text(encoding='utf8')
chunk=source[source.index('def _shader_water'):source.index('def _tube')]
baseline=json.loads((root/'qa'/'site_revision4_baseline.json').read_text(encoding='utf8'))
report['existing_water_function_sha256']=hashlib.sha256(chunk.encode()).hexdigest()
report['existing_water_function_unchanged']=report['existing_water_function_sha256']==baseline['water_function_sha256']
report['original_river_first16_unchanged']=cfg['river_path'][:16]==baseline['first16']
water=bpy.data.objects['WATER_BearRun_Continuous_Upstream_Downstream']
report['existing_main_river_normal_z_range']=[min(p.normal.z for p in water.data.polygons),max(p.normal.z for p in water.data.polygons)]
report['existing_main_river_normal_note']='Original water geometry deliberately unchanged; independent water_integration.py owns normal correction and local fluid trim.'
remote=bpy.data.objects['SITE_Remote_Upstream_Creek_Continuation']
report['new_remote_upstream_normal_z_min']=min(p.normal.z for p in remote.data.polygons)
report['scene_objects']=len(bpy.data.objects)
report['unique_mesh_vertices']=sum(len(mesh.vertices) for mesh in bpy.data.meshes)
report['unique_mesh_faces']=sum(len(mesh.polygons) for mesh in bpy.data.meshes)
report['terrain_distance_from_main_center_to_boundary_m']=min(abs(b) for b in bounds)
report['terrain_distance_from_guest_center_to_boundary_m']=min(bounds[1]-20,20-bounds[0],bounds[3]-45,45-bounds[2])
report['build_and_geometry_qa_seconds']=time.time()-t
report['gpu_render']='NOT_RUN: integrator owns unified iteration04 render'
report['visual_status']='PENDING image review; geometry checks do not demonstrate photorealism or invisibility of all boundaries.'
(root/'qa'/'site_revision4_geometry.json').write_text(json.dumps(report,indent=2),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'qa'/'site_revision4_smoke.blend'))
print('SITE_REVISION4 '+json.dumps({k:v for k,v in report.items() if k not in ('preserved_tree_roots','building_ground_cap_samples','limitations','suggested_views')},ensure_ascii=False))
