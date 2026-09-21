"""One practical MAIN_L3 coverage/lattice/density configuration, not a causal test."""
import ast,ctypes,hashlib,itertools,json,math,sys,time
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import eevee_glass
SOURCE=ROOT/'scene/Fallingwater_preview_iteration06.blend'
EXPECTED='e317241899808995f049e8d3343eac96c591cbecfddaa980949d6babb51ccce6'
OUT=ROOT/'qa/eevee-iteration06-practical';OUT.mkdir(exist_ok=True)
REPORT=OUT/'report.json';PNG=OUT/'CAM_MAIN_L3_STUDY_B_EV2p4.png'
BLEND=OUT/'Fallingwater_main_l3_coverage_candidate.blend';TARGET='FW_PROBE_MAIN_L3'
tree=ast.parse((ROOT/'qa/eevee-iteration06-coverage.py').read_text(encoding='utf-8'))
names={'sha','properties','light_state','probe_state','object_state','bounds'}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'inspection_helpers','exec'))
tree=ast.parse((ROOT/'qa/eevee-iteration06-density.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='MemoryStatus'],type_ignores=[]),'memory_inspection','exec'))
assert sha(SOURCE)==EXPECTED and not PNG.exists() and not BLEND.exists()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s=bpy.context.scene;s.frame_set(1)
assert s.render.engine=='BLENDER_EEVEE' and s.eevee.use_raytracing and not s.eevee.use_fast_gi
s.camera=s.objects['CAM_MAIN_L3_STUDY_B'];s.view_settings.exposure=2.4
s.eevee.taa_render_samples=32;s.render.threads_mode='FIXED';s.render.threads=4
s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage=960,540,100
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
probe=s.objects[TARGET];original_bounds=bounds(probe);original_scale=list(probe.scale)
original_resolution=[probe.data.resolution_x,probe.data.resolution_y,probe.data.resolution_z]
before_lights=light_state(s);before_probes=probe_state(s);before_objects=object_state(s)
before_cycles=eevee_glass.cycles_signature();before_geometry=eevee_glass.geometry_signature(s)
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
room_ids={r['id'] for r in rooms if r['building']=='MAIN' and r['level']=='L3'}
floor=bounds(s.objects['MAIN_L3_STUDY_slab'].evaluated_get(deps),list(s.objects['MAIN_L3_STUDY_slab'].evaluated_get(deps).bound_box))[0][2]
geometry=[]
for original in s.objects:
    if original.type!='MESH' or original.hide_render:continue
    if not (original.name.startswith('MAIN_L3') or original.get('room_id') in room_ids):continue
    obj=original.evaluated_get(deps);bb=bounds(obj,list(obj.bound_box))
    if bb[1][2]<floor-.001:continue
    original_low=bb[0][2]
    bb[0][2]=max(bb[0][2],floor)
    geometry.append({'object':original.name,'bounds':bb,'room_id':original.get('room_id'),
        'cross_level_geometry_clipped_to_actual_slab_bottom':original_low<floor-.001})
assert len(geometry)>20
base_low=[min(g['bounds'][0][i] for g in geometry) for i in range(3)]
base_high=[max(g['bounds'][1][i] for g in geometry) for i in range(3)]
# Preserve existing level's XY domain, then include the actual saved camera.
for i in range(2):
    base_low[i]=min(base_low[i],original_bounds[0][i])
    base_high[i]=max(base_high[i],original_bounds[1][i])
for i in range(3):
    base_low[i]=min(base_low[i],s.camera.location[i]);base_high[i]=max(base_high[i],s.camera.location[i])
target_spacing=[.8,.8,.32]
margin=[1.35*v+.05 for v in target_spacing]
planned_low=[v-m for v,m in zip(base_low,margin)];planned_high=[v+m for v,m in zip(base_high,margin)]
planned_scale=[(b-a)/2 for a,b in zip(planned_low,planned_high)]
planned_resolution=[max(4,math.ceil((b-a)/h)-1) for a,b,h in zip(planned_low,planned_high,target_spacing)]
planned_spacing=[(b-a)/(r+1) for a,b,r in zip(planned_low,planned_high,planned_resolution)]
assert all(new<=old+1e-7 for new,old in zip(planned_spacing,target_spacing))
assert max(planned_resolution)<=64 and math.prod(planned_resolution)<=40000
worst_bias=abs(probe.data.normal_bias)+abs(probe.data.view_bias)
required=[(1+worst_bias)*d for d in planned_spacing]
assert all(m>r+.04 for m,r in zip(margin,required))
profile={'schema':'fw.eeveel3.practical.v1','source_sha256':EXPECTED,'probe':TARGET,
    'base_actual_geometry_bounds':[base_low,base_high],'bounds':[planned_low,planned_high],
    'resolution':planned_resolution,'nominal_spacing_m':planned_spacing,'surfel_density':32,
    'requested_max_spacing_m':target_spacing,'margin_m':margin,'minimum_bias_safe_margin_m':required,
    'coverage_rule':'margin >= (1+abs(normal_bias)+abs(view_bias))*actual_spacing; sufficient to avoid padding interpolation for enclosed domain.',
    'world_padding_source':'https://raw.githubusercontent.com/blender/blender/v5.2.1/source/blender/draw/engines/eevee/shaders/eevee_lightprobe_volume_load.bsl.hh',
    'sampling_source':'https://raw.githubusercontent.com/blender/blender/v5.2.1/source/blender/draw/engines/eevee/shaders/eevee_lightprobe_volume.bsl.hh',
    'geometry_selection':'All renderable MAIN_L3-prefixed meshes or objects tagged to actual L3 rooms; cross-level geometry below the evaluated Study slab bottom is clipped for this L3 domain. Prior probe XY domain retained. Includes saved StudyB camera.',
    'actual_floor_slab_bottom_z':floor,'selected_geometry':geometry,
    'scope':'Combined practical candidate: coverage, nominal resolution and density; not a single-variable causal claim.'}
# Confirm the critical original wall hits and camera are beyond padding+normal bias.
old_inspection=json.loads((ROOT/'qa/eevee-iteration06-volume-inspect.json').read_text(encoding='utf-8'))
points=[{'label':p['label'],'world':p['camera_hit']['point']} for p in old_inspection['study_pixels']]
points.append({'label':'StudyB_camera','world':list(s.camera.location)})
for p in points:
    p['distance_to_nearest_bound_in_cells']=[min(v-a,b-v)/d for v,a,b,d in zip(p['world'],planned_low,planned_high,planned_spacing)]
    assert min(p['distance_to_nearest_bound_in_cells'])>1+worst_bias
profile['critical_point_margin_checks']=points
(OUT/'profile.json').write_text(json.dumps(profile,indent=2),encoding='utf-8')
print('PRACTICAL_PROFILE '+json.dumps({k:v for k,v in profile.items() if k not in ['selected_geometry']}),flush=True)
# World-space triangle projection estimate before any probe mutation/bake.
cap_low=np.asarray(planned_low)-probe.data.capture_distance;cap_high=np.asarray(planned_high)+probe.data.capture_distance
rows=[]
for original in s.objects:
    if original.type!='MESH' or original.hide_render:continue
    obj=original.evaluated_get(deps);bb=np.asarray([obj.matrix_world@Vector(p) for p in obj.bound_box])
    if np.any(bb.max(axis=0)<cap_low) or np.any(bb.min(axis=0)>cap_high):continue
    mesh=obj.data
    if not mesh.polygons:continue
    mesh.calc_loop_triangles()
    v=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',v)
    m=np.asarray(obj.matrix_world,dtype=np.float64);v=v.reshape(-1,3)@m[:3,:3].T+m[:3,3]
    idx=np.empty(len(mesh.loop_triangles)*3,dtype=np.int32);mesh.loop_triangles.foreach_get('vertices',idx)
    tri=v[idx.reshape(-1,3)]
    mask=np.all(tri.max(axis=1)>=cap_low,axis=1)&np.all(tri.min(axis=1)<=cap_high,axis=1);tri=tri[mask]
    projected=float(np.abs(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])).sum()*.5) if len(tri) else 0
    rows.append({'object':original.name,'vertices':len(mesh.vertices),'triangles':len(mesh.loop_triangles),
        'overlapping_triangles':int(mask.sum()),'projected_area_m2':projected})
converted_density=32/max(planned_scale);projected=sum(r['projected_area_m2'] for r in rows)
surfel_count=math.ceil(projected*converted_density**2);allowance=surfel_count*224*6+math.prod(planned_resolution)*1024
memory=MemoryStatus();memory.length=ctypes.sizeof(memory)
assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory))
guard=min(8*1024**3,int(memory.available*.35))
budget={'source_sha256':EXPECTED,'capture_bounds':[cap_low.tolist(),cap_high.tolist()],
    'mesh_count':len(rows),'vertices':sum(r['vertices'] for r in rows),'triangles':sum(r['triangles'] for r in rows),
    'overlapping_triangles':sum(r['overlapping_triangles'] for r in rows),'projected_area_m2':projected,
    'density32_per_m':converted_density,'estimated_surfels':surfel_count,'surfel_bytes':224,
    'planning_allowance_bytes':allowance,'guard_bytes':guard,'available_physical_bytes':memory.available,
    'grid_sample_count':math.prod(planned_resolution),
    'method':'World triangle projected area, capture-AABB culling;6x main surfel buffer plus1024B per grid sample. Planning estimate, not hard/observed GPU bound.'}
(OUT/'preflight.json').write_text(json.dumps(budget,indent=2),encoding='utf-8')
print('PRACTICAL_PREFLIGHT '+json.dumps(budget),flush=True)
if allowance>guard:raise RuntimeError('Resource preflight rejected before bake')
probe.location=[(a+b)/2 for a,b in zip(planned_low,planned_high)];probe.scale=planned_scale
probe.data.resolution_x,probe.data.resolution_y,probe.data.resolution_z=planned_resolution
probe.data.surfel_density=32
bpy.context.view_layer.update()
after_probes=probe_state(s);after_objects=object_state(s)
assert light_state(s)==before_lights
expected=json.loads(json.dumps(before_probes[TARGET]));expected['matrix']=after_probes[TARGET]['matrix']
for i,k in enumerate(['resolution_x','resolution_y','resolution_z']):expected['properties'][k]=planned_resolution[i]
expected['properties']['surfel_density']=32
assert expected==after_probes[TARGET]
for name,p in before_probes.items():
    if name!=TARGET:assert p==after_probes[name]
diffs={n:{'before':v,'after':after_objects[n]} for n,v in before_objects.items() if v!=after_objects[n]}
assert set(diffs)=={TARGET}
report={'status':'READY_TO_BAKE','source_sha256':EXPECTED,'production_saved':False,'profile':profile,'resource_preflight':budget,
    'camera':s.camera.name,'camera_location':list(s.camera.location),'camera_rotation':list(s.camera.rotation_euler),
    'lens':s.camera.data.lens,'frame':1,'exposure':2.4,'resolution':[960,540],'samples':32,'cpu_preparation_threads':4,
    'raytracing':True,'fast_gi':False,'before_probe_state':before_probes,'after_probe_state':after_probes,
    'light_settings_and_links_unchanged':True,'before_light_state':before_lights,'object_differences':diffs,
    'cycles_glass_signature':before_cycles,'glazing_geometry_signature':before_geometry,
    'original_bounds':original_bounds,'original_scale':original_scale,'original_resolution':original_resolution,
    'before_surfel_spacing_m':max(original_scale)/8,'after_surfel_spacing_m':max(probe.scale)/32,
    'actual_surface_bias_m':probe.data.surface_bias*min(v/r for v,r in zip(probe.scale,planned_resolution)),
    'actual_escape_bias_m':probe.data.escape_bias*min(v/r for v,r in zip(probe.scale,planned_resolution))}
REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
for o in bpy.context.selected_objects:o.select_set(False)
probe.select_set(True);bpy.context.view_layer.objects.active=probe;assert bpy.context.selected_objects==[probe]
print('PRACTICAL_BAKE_START',flush=True)
start=time.perf_counter();result=bpy.ops.object.lightprobe_cache_bake(subset='ACTIVE')
report['bake_seconds']=time.perf_counter()-start;report['bake_operator_result']=sorted(result);assert result=={'FINISHED'}
report['status']='BAKED';REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PRACTICAL_BAKE_COMPLETE '+str(report['bake_seconds']),flush=True)
assert light_state(s)==before_lights and probe_state(s)==after_probes
assert eevee_glass.cycles_signature()==before_cycles and eevee_glass.geometry_signature(s)==before_geometry
s.render.filepath=str(PNG);print('PRACTICAL_RENDER_START',flush=True)
start=time.perf_counter();bpy.ops.render.render(write_still=True)
report.update(status='RENDERED',render_seconds=time.perf_counter()-start,png=str(PNG),png_sha256=sha(PNG),visual_acceptance='NOT_REVIEWED')
s['fw_eevee_coverage_profile_json']=json.dumps({k:v for k,v in profile.items() if k!='selected_geometry'})
s['fw_eevee_candidate_scope']='MAIN_L3 combined coverage/resolution/density candidate only; all other lights/probes retained. Only StudyB tested.'
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
report['candidate_blend']=str(BLEND);report['candidate_sha256']=sha(BLEND)
assert sha(SOURCE)==EXPECTED;report['source_unchanged']=True
REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PRACTICAL_COMPLETE '+json.dumps({k:report[k] for k in ['bake_seconds','render_seconds','png_sha256','candidate_sha256']}),flush=True)
