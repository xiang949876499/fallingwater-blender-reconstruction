"""Original bounds, one MAIN_L3 surfel-density32 bake and one Study image."""
import ast,ctypes,hashlib,json,math,sys,time
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import eevee_glass
SOURCE=ROOT/'scene/Fallingwater_preview_iteration06.blend'
EXPECTED='e317241899808995f049e8d3343eac96c591cbecfddaa980949d6babb51ccce6'
OUT=ROOT/'qa/eevee-iteration06-density'
OUT.mkdir(exist_ok=True)
REPORT=OUT/'report.json';PNG=OUT/'CAM_MAIN_L3_STUDY_B_EV2p4.png'
BLEND=OUT/'Fallingwater_study_density32_candidate.blend'
TARGET='FW_PROBE_MAIN_L3'
# Reuse only audited pure inspection functions, without executing the old task.
tree=ast.parse((ROOT/'qa/eevee-iteration06-coverage.py').read_text(encoding='utf-8'))
functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in
    {'sha','properties','light_state','probe_state','object_state','bounds'}]
import itertools
exec(compile(ast.Module(body=functions,type_ignores=[]),'coverage_inspection_functions','exec'))

class MemoryStatus(ctypes.Structure):
    _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong),('total',ctypes.c_ulonglong),
        ('available',ctypes.c_ulonglong),('total_page',ctypes.c_ulonglong),('available_page',ctypes.c_ulonglong),
        ('total_virtual',ctypes.c_ulonglong),('available_virtual',ctypes.c_ulonglong),('extended',ctypes.c_ulonglong)]

assert sha(SOURCE)==EXPECTED
assert not PNG.exists() and not BLEND.exists(),'Preserve completed evidence'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s=bpy.context.scene;s.frame_set(1)
assert s.render.engine=='BLENDER_EEVEE' and s.eevee.use_raytracing and not s.eevee.use_fast_gi
s.camera=s.objects['CAM_MAIN_L3_STUDY_B'];s.view_settings.exposure=2.4
s.eevee.taa_render_samples=32;s.render.threads_mode='FIXED';s.render.threads=4
s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage=960,540,100
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
bpy.context.view_layer.update()
before_lights=light_state(s);before_probes=probe_state(s);before_objects=object_state(s)
before_cycles=eevee_glass.cycles_signature();before_geometry=eevee_glass.geometry_signature(s)
probe=s.objects[TARGET];probe_bounds=bounds(probe)
assert probe.data.surfel_density==8
resolution=[probe.data.resolution_x,probe.data.resolution_y,probe.data.resolution_z]
report={'status':'PREFLIGHT','source_sha256':EXPECTED,'production_saved':False,
    'camera':s.camera.name,'camera_location':list(s.camera.location),'camera_rotation':list(s.camera.rotation_euler),
    'lens':s.camera.data.lens,'frame':1,'exposure':2.4,'resolution':[960,540],'samples':32,'cpu_preparation_threads':4,
    'probe_bounds':probe_bounds,'grid_resolution':resolution,
    'nominal_spacing_m':[(b-a)/(r+1) for a,b,r in zip(*probe_bounds,resolution)],
    'raytracing':s.eevee.use_raytracing,'fast_gi':s.eevee.use_fast_gi,
    'before_light_state':before_lights,'before_probe_state':before_probes,
    'cycles_glass_signature':before_cycles,'glazing_geometry_signature':before_geometry}
# Estimate from actual evaluated meshes overlapping the capture box. Summing
# full mesh area is conservative for objects partially outside that box.
capture_bounds=[[v-probe.data.capture_distance for v in probe_bounds[0]],
                [v+probe.data.capture_distance for v in probe_bounds[1]]]
deps=bpy.context.evaluated_depsgraph_get();mesh_count=vertices=polygons=triangles=0;area=0.0
for original in s.objects:
    if original.type!='MESH' or original.hide_render:continue
    obj=original.evaluated_get(deps);bb=bounds(obj,list(obj.bound_box))
    if any(bb[1][i]<capture_bounds[0][i] or bb[0][i]>capture_bounds[1][i] for i in range(3)):continue
    mesh=obj.data;mesh_count+=1;vertices+=len(mesh.vertices);polygons+=len(mesh.polygons)
    triangles+=sum(max(1,len(p.vertices)-2) for p in mesh.polygons)
    area+=sum(p.area for p in mesh.polygons)*max(obj.matrix_world.to_scale())**2
converted_density=32/max(probe.scale)
area_surfel_estimate=math.ceil(math.sqrt(3)*area*converted_density**2)
surfel_budget=area_surfel_estimate+3*triangles
# Official packed Surfel has 80 base bytes + three48-byte radiance records.
surfel_bytes=224
incremental_allowance=surfel_budget*surfel_bytes*3
memory=MemoryStatus();memory.length=ctypes.sizeof(memory)
assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory))
budget_limit=min(8*1024**3,int(memory.available*.35))
budget={'capture_bounds':capture_bounds,'evaluated_mesh_count':mesh_count,'evaluated_vertices':vertices,
    'evaluated_polygons':polygons,'derived_triangle_count':triangles,'conservative_surface_area_m2':area,
    'surface_density_ratio':4,'expected_surface_count_ratio':16,
    'density32_per_m':converted_density,'area_based_surfel_estimate':area_surfel_estimate,
    'triangle_boundary_allowance':3*triangles,'surfel_budget':surfel_budget,
    'surfel_struct_bytes_from_source':surfel_bytes,'incremental_budget_bytes':incremental_allowance,
    'total_physical_memory_bytes':memory.total,'available_physical_memory_bytes':memory.available,
    'guard_limit_bytes':budget_limit,
    'limit':'Planning allowance, not a measured GPU allocation or rigorous upper bound. Includes three times surfel storage for auxiliary work; scene geometry already loaded.'}
report['resource_preflight']=budget
REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('DENSITY_PREFLIGHT '+json.dumps(budget),flush=True)
if incremental_allowance>budget_limit:
    report['status']='STOPPED_RESOURCE_PREFLIGHT';REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
    raise RuntimeError('Planning allowance exceeds bounded memory guard; no bake/render started')
probe.data.surfel_density=32
bpy.context.view_layer.update()
after_probes=probe_state(s)
assert object_state(s)==before_objects and light_state(s)==before_lights
for name,before in before_probes.items():
    after=after_probes[name]
    if name==TARGET:
        expected=json.loads(json.dumps(before));expected['properties']['surfel_density']=32
        assert after==expected
    else:assert after==before
assert bounds(probe)==probe_bounds
report.update(status='READY_TO_BAKE',property_difference={'object':TARGET,'property':'surfel_density','before':8,'after':32},
    object_transforms_and_visibility_unchanged=True,all_light_properties_and_links_unchanged=True,
    all_other_probe_properties_unchanged=True,
    before_physical_surfel_interval_m=max(probe.scale)/8,after_physical_surfel_interval_m=max(probe.scale)/32,
    actual_surface_bias_m=probe.data.surface_bias*min(v/r for v,r in zip(probe.scale,resolution)),
    actual_escape_bias_m=probe.data.escape_bias*min(v/r for v,r in zip(probe.scale,resolution)))
REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
for obj in bpy.context.selected_objects:obj.select_set(False)
probe.select_set(True);bpy.context.view_layer.objects.active=probe
assert bpy.context.selected_objects==[probe]
print('DENSITY_BAKE_START',flush=True)
start=time.perf_counter();result=bpy.ops.object.lightprobe_cache_bake(subset='ACTIVE')
report['bake_seconds']=time.perf_counter()-start;report['bake_operator_result']=sorted(result)
assert result=={'FINISHED'}
report['status']='BAKED';REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('DENSITY_BAKE_COMPLETE '+str(report['bake_seconds']),flush=True)
assert probe_state(s)==after_probes and light_state(s)==before_lights
assert eevee_glass.cycles_signature()==before_cycles and eevee_glass.geometry_signature(s)==before_geometry
s.render.filepath=str(PNG);print('DENSITY_RENDER_START',flush=True)
start=time.perf_counter();bpy.ops.render.render(write_still=True)
report.update(status='RENDERED',render_seconds=time.perf_counter()-start,png=str(PNG),png_sha256=sha(PNG),visual_acceptance='NOT_REVIEWED')
s['fw_eevee_study_density_candidate_json']=json.dumps({k:report[k] for k in
    ['source_sha256','property_difference','probe_bounds','grid_resolution','bake_seconds','bake_operator_result']})
s['fw_eevee_candidate_scope']='Only MAIN_L3 surfel density8 to32 and its active cache changed. Original bounds/resolution/light settings. Unaccepted visual candidate.'
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
report['candidate_blend']=str(BLEND);report['candidate_sha256']=sha(BLEND)
assert sha(SOURCE)==EXPECTED;report['source_unchanged']=True
REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('DENSITY_COMPLETE '+json.dumps({k:report[k] for k in ['bake_seconds','render_seconds','png_sha256','candidate_sha256']}),flush=True)
