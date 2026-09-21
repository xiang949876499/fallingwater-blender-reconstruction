"""Read-only world triangle-area resource estimate, no bake/render/save."""
import hashlib,json,math,time
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'scene/Fallingwater_preview_iteration06.blend'
EXPECTED='e317241899808995f049e8d3343eac96c591cbecfddaa980949d6babb51ccce6'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s=bpy.context.scene;s.frame_set(1);s.render.threads_mode='FIXED';s.render.threads=4
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
probe=s.objects['FW_PROBE_MAIN_L3'];density=32/max(probe.scale)
low=np.array(probe.location)-np.array(probe.scale)-probe.data.capture_distance
high=np.array(probe.location)+np.array(probe.scale)+probe.data.capture_distance
rows=[];start=time.perf_counter()
for original in s.objects:
    if original.type!='MESH' or original.hide_render:continue
    obj=original.evaluated_get(deps)
    bb=np.array([obj.matrix_world@Vector(p) for p in obj.bound_box])
    if np.any(bb.max(axis=0)<low) or np.any(bb.min(axis=0)>high):continue
    mesh=obj.data
    if not mesh.polygons:continue
    mesh.calc_loop_triangles()
    vertices=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',vertices)
    vertices=vertices.reshape(-1,3)
    matrix=np.asarray(obj.matrix_world,dtype=np.float64)
    vertices=vertices@matrix[:3,:3].T+matrix[:3,3]
    indices=np.empty(len(mesh.loop_triangles)*3,dtype=np.int32);mesh.loop_triangles.foreach_get('vertices',indices)
    triangles=vertices[indices.reshape(-1,3)]
    mask=np.all(triangles.max(axis=1)>=low,axis=1)&np.all(triangles.min(axis=1)<=high,axis=1)
    triangles=triangles[mask]
    if len(triangles):
        double_vectors=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0])
        area=float(np.linalg.norm(double_vectors,axis=1).sum()*.5)
        projected=float(np.abs(double_vectors).sum()*.5)
    else:area=projected=0.0
    rows.append({'object':original.name,'vertices':len(mesh.vertices),'triangles':len(mesh.loop_triangles),
        'triangles_overlapping_capture_aabb':int(mask.sum()),'world_area_m2':area,'sum_three_axis_projected_area_m2':projected})
area=sum(r['world_area_m2'] for r in rows);projected=sum(r['sum_three_axis_projected_area_m2'] for r in rows)
expected=math.ceil(projected*density*density)
report={'status':'READ_ONLY_COMPLETE','source_sha256':EXPECTED,'baked':False,'rendered':False,'saved':False,
    'seconds':time.perf_counter()-start,'capture_bounds':[low.tolist(),high.tolist()],
    'evaluated_mesh_count':len(rows),'evaluated_vertices':sum(r['vertices'] for r in rows),
    'derived_triangles':sum(r['triangles'] for r in rows),
    'triangles_overlapping_capture_aabb':sum(r['triangles_overlapping_capture_aabb'] for r in rows),
    'world_surface_area_m2':area,'sum_three_axis_projected_area_m2':projected,
    'density32_per_m':density,'area_based_expected_surfel_count':expected,
    'surfel_struct_bytes':224,'expected_main_surfel_buffer_bytes':expected*224,
    'planning_allowance_bytes':expected*224*6,
    'planning_method':'Actual world triangles, discard disjoint triangle AABBs, retain full area of crossing triangles. Projected area times density squared estimates raster surface count. Six times main-buffer storage allows approximately2x count uncertainty and3x total-buffer work; not a hard upper bound or measured peak.',
    'largest_projected_area_objects':sorted(rows,key=lambda r:r['sum_three_axis_projected_area_m2'],reverse=True)[:20],
    'all_objects':rows}
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
(ROOT/'qa/eevee-iteration06-density/preflight-refined.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('REFINED_PREFLIGHT '+json.dumps({k:v for k,v in report.items() if k not in ['all_objects','largest_projected_area_objects']}),flush=True)
print('LARGEST '+json.dumps(report['largest_projected_area_objects'][:5]),flush=True)
