"""One MAIN_L3 Z-coverage bake and matched Study render; isolated candidate only."""
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import eevee_glass
SOURCE=ROOT/'scene/Fallingwater_preview_iteration06.blend'
EXPECTED='e317241899808995f049e8d3343eac96c591cbecfddaa980949d6babb51ccce6'
OUT=ROOT/'qa/eevee-iteration06-coverage'
PNG=OUT/'CAM_MAIN_L3_STUDY_B_EV2p4.png'
BLEND=OUT/'Fallingwater_study_coverage_candidate.blend'
REPORT=OUT/'report.json'
TARGET='FW_PROBE_MAIN_L3'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def properties(data):
    result={}
    for p in data.bl_rna.properties:
        if p.type not in {'BOOLEAN','INT','FLOAT','STRING','ENUM'}:
            continue
        value=getattr(data,p.identifier)
        result[p.identifier]=list(value) if getattr(p,'is_array',False) else value
    return result

def light_state(scene):
    return {o.name:{'matrix':[list(r) for r in o.matrix_world], 'properties':properties(o.data),
        'blocker_collection':o.light_linking.blocker_collection.name if o.light_linking.blocker_collection else None}
        for o in scene.objects if o.type=='LIGHT'}

def probe_state(scene):
    return {o.name:{'matrix':[list(r) for r in o.matrix_world],'properties':properties(o.data)}
        for o in scene.objects if o.type=='LIGHT_PROBE'}

def object_state(scene):
    return {o.name:{'matrix':[list(r) for r in o.matrix_world], 'hide_render':o.hide_render,
        'hide_viewport':o.hide_viewport,'data':o.data.name if o.data else None}
        for o in scene.objects}

def bounds(obj,local_corners=None):
    corners=[obj.matrix_world@Vector(p) for p in (local_corners or itertools.product((-1,1),repeat=3))]
    return [[min(p[i] for p in corners) for i in range(3)], [max(p[i] for p in corners) for i in range(3)]]

assert sha(SOURCE)==EXPECTED
assert not PNG.exists() and not BLEND.exists(),'Existing evidence preserved'
OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s=bpy.context.scene; s.frame_set(1)
assert s.render.engine=='BLENDER_EEVEE' and s.eevee.use_raytracing and not s.eevee.use_fast_gi
s.camera=s.objects['CAM_MAIN_L3_STUDY_B']; s.view_settings.exposure=2.4
s.eevee.taa_render_samples=32
s.render.threads_mode='FIXED';s.render.threads=4
s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage=960,540,100
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
bpy.context.view_layer.update()
before_lights=light_state(s);before_probes=probe_state(s);before_objects=object_state(s)
before_cycles=eevee_glass.cycles_signature();before_geometry=eevee_glass.geometry_signature(s)
probe=s.objects[TARGET];before_bounds=bounds(probe);before_scale=list(probe.scale)
deps=bpy.context.evaluated_depsgraph_get()
surface_names=['MAIN_L3_study_core_1','MAIN_L3_STUDY_ceiling']
surfaces={}
for name in surface_names:
    obj=s.objects[name].evaluated_get(deps)
    surfaces[name]=bounds(obj,list(obj.bound_box))
wall_bounds=surfaces['MAIN_L3_study_core_1']
floor_z=wall_bounds[0][2];wall_top=wall_bounds[1][2]
assert abs(floor_z-5.26415)<.002 and abs(wall_top-7.6)<.002,surfaces
# Keep visible wall points away from the padded cell's World blending region.
# The existing XY maximum scale stays fixed, preserving physical surfel density.
new_low=floor_z-.75
new_high=max(wall_top,surfaces['MAIN_L3_STUDY_ceiling'][1][2])+.50
probe.location.z=(new_low+new_high)/2
probe.scale.z=(new_high-new_low)/2
bpy.context.view_layer.update()
after_bounds=bounds(probe)
assert list(probe.scale)[:2]==before_scale[:2] and max(probe.scale)==max(before_scale)
after_probes=probe_state(s);after_objects=object_state(s)
assert light_state(s)==before_lights
for name,state in before_probes.items():
    if name==TARGET:
        assert after_probes[name]['properties']==state['properties']
    else:
        assert after_probes[name]==state
assert set(after_objects)==set(before_objects)
object_diffs={n:{'before':v,'after':after_objects[n]} for n,v in before_objects.items() if v!=after_objects[n]}
assert set(object_diffs)=={TARGET},list(object_diffs)
resolution=[probe.data.resolution_x,probe.data.resolution_y,probe.data.resolution_z]
report={'status':'READY_TO_BAKE','source_sha256':EXPECTED,'production_saved':False,
    'camera':s.camera.name,'camera_location':list(s.camera.location),'camera_rotation':list(s.camera.rotation_euler),
    'lens':s.camera.data.lens,'frame':1,'exposure':2.4,'resolution':[960,540],'samples':32,'cpu_preparation_threads':4,
    'raytracing':s.eevee.use_raytracing,'fast_gi':s.eevee.use_fast_gi,
    'evaluated_geometry_bounds':surfaces,'before_bounds':before_bounds,'after_bounds':after_bounds,
    'grid_resolution':resolution,'before_nominal_spacing_m':[(b-a)/(r+1) for a,b,r in zip(*before_bounds,resolution)],
    'after_nominal_spacing_m':[(b-a)/(r+1) for a,b,r in zip(*after_bounds,resolution)],
    'before_scale':before_scale,'after_scale':list(probe.scale),
    'rna_surfel_density':probe.data.surfel_density,
    'physical_surfel_spacing_m':max(probe.scale)/probe.data.surfel_density,'physical_surfel_density_unchanged':True,
    'light_properties_and_links_unchanged':True,'before_light_state':before_lights,
    'all_probe_data_properties_unchanged':True,'other_six_volume_transforms_unchanged':True,
    'before_probe_state':before_probes,'object_differences':object_diffs,
    'cycles_glass_signature':before_cycles,'glazing_geometry_signature':before_geometry,
    'spacing_consequence':'Z nominal spacing increases with expanded bounds at fixed four samples; XY and maxScale-dependent surface capture density are unchanged.',
    'helper_sha256':{n:sha(ROOT/'scripts'/n) for n in ['eevee_preview.py','eevee_glass.py']}}
REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
for obj in bpy.context.selected_objects:obj.select_set(False)
probe.select_set(True);bpy.context.view_layer.objects.active=probe
assert bpy.context.selected_objects==[probe]
print('COVERAGE_BAKE_START '+json.dumps({'target':TARGET,'bounds':after_bounds}),flush=True)
start=time.perf_counter();result=bpy.ops.object.lightprobe_cache_bake(subset='ACTIVE')
report['bake_seconds']=time.perf_counter()-start;report['bake_operator_result']=sorted(result)
assert result=={'FINISHED'}
report['status']='BAKED'
REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('COVERAGE_BAKE_COMPLETE '+str(report['bake_seconds']),flush=True)
assert light_state(s)==before_lights
assert probe_state(s)==after_probes
assert eevee_glass.cycles_signature()==before_cycles and eevee_glass.geometry_signature(s)==before_geometry
s.render.filepath=str(PNG)
print('COVERAGE_RENDER_START',flush=True)
start=time.perf_counter();bpy.ops.render.render(write_still=True)
report.update(status='RENDERED',render_seconds=time.perf_counter()-start,png=str(PNG),png_sha256=sha(PNG),visual_acceptance='NOT_REVIEWED')
# Preserve original seven-bake records as provenance, and record the actual
# replacement separately; this candidate must not masquerade as a production bake.
s['fw_eevee_study_coverage_candidate_json']=json.dumps({k:report[k] for k in
    ['source_sha256','before_bounds','after_bounds','bake_seconds','bake_operator_result','grid_resolution','after_nominal_spacing_m']})
s['fw_eevee_candidate_scope']='Only MAIN_L3 Z coverage changed and actively rebaked. Other six caches retained; visual candidate, not production approval.'
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
report['candidate_blend']=str(BLEND);report['candidate_sha256']=sha(BLEND)
assert sha(SOURCE)==EXPECTED
report['source_unchanged']=True
REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('COVERAGE_COMPLETE '+json.dumps({k:report[k] for k in ['bake_seconds','render_seconds','png_sha256','candidate_sha256']}),flush=True)
