"""Actual bounded Blender mesh audit; saves no-water baseline and candidate only."""
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path
import bpy
import bmesh

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('fw_site',ROOT/'scripts/site.py')
site=importlib.util.module_from_spec(spec);spec.loader.exec_module(site)
source=ROOT/'scene/Fallingwater_iteration06.blend'
source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
assert source_sha=='172b76340d1224a2b98f415b21042d19ad7fba4d849543d7156beb17e5fcf055'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
scene.frame_set(48)
targets={'SITE_Core_Continuous_Fractured_Sandstone'}|{f'SITE_Cascade_Shoulder_{s}_{j}' for s in (0,1) for j in range(4)}

def mesh_hash(mesh):
    h=hashlib.sha256()
    for v in mesh.vertices:h.update(struct.pack('<3f',*v.co))
    for p in mesh.polygons:
        h.update(struct.pack('<I',len(p.vertices)))
        for v in p.vertices:h.update(struct.pack('<I',v))
    if mesh.shape_keys:
        for key in mesh.shape_keys.key_blocks:
            h.update(key.name.encode())
            for v in key.data:h.update(struct.pack('<3f',*v.co))
    return h.hexdigest()

def snapshot():
    meshes={m.name:mesh_hash(m) for m in bpy.data.meshes if m.users}
    out={}
    for o in scene.objects:
        props={'type':o.type,'matrix':list(sum((tuple(r) for r in o.matrix_world),())),
               'hide_render':o.hide_render,'collections':sorted(c.name for c in o.users_collection)}
        if o.type=='MESH':
            props['mesh_sha256']=meshes[o.data.name]
            props['materials']=[m.name if m else None for m in o.data.materials]
        out[o.name]=props
    return out

water=[o for o in scene.objects if o.name.startswith('WATER_') or o.name=='SITE_Remote_Upstream_Creek_Continuation']
hidden=[o.name for o in water if not o.hide_render]
for o in water:o.hide_render=True
scene['geology_review_water_hidden']=json.dumps(hidden)
baseline=ROOT/'scene/Fallingwater_geology_baseline06b_frame48_no_water.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(baseline),compress=True)
before=snapshot()
core=bpy.data.objects['SITE_Core_Continuous_Fractured_Sandstone']
old_top=[tuple(v.co) for v in core.data.vertices[:53]]
old_bottom=[tuple(v.co) for v in core.data.vertices[-53:]]
old_top_z=max(p[2] for p in old_top)
old_caps={}
for side in (0,1):
    old=bpy.data.objects[f'SITE_Cascade_Shoulder_{side}_0']
    n=(len(old.data.vertices)-1)//3
    old_caps[side]=[tuple(v.co) for v in old.data.vertices[2*n:3*n]]+[tuple(old.data.vertices[-1].co)]
cfg=json.loads((ROOT/'data/site.json').read_text(encoding='utf-8'))
cfg['core_bedrock_revision']='discontinuous_beds_v2'
result=site.refine_core_bedrock(cfg)
bpy.context.view_layer.update()
after=snapshot()
new_names=set(result['revised_objects'])
unrelated_changes=[name for name,p in before.items() if name not in targets and after.get(name)!=p]
unexpected_new=sorted(set(after)-set(before)-new_names)
assert not unrelated_changes,(unrelated_changes[:20])
assert not unexpected_new,unexpected_new
assert old_top==[tuple(v.co) for v in core.data.vertices[:53]],'Upper core perimeter changed'
assert old_bottom==[tuple(v.co) for v in core.data.vertices[result['core_lower_cap_start_vertex']:result['core_lower_cap_start_vertex']+53]],'Lower core perimeter changed'

geometry=[]
for name in result['revised_objects']:
    o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data)
    record={'object':name,'mesh_sha256':mesh_hash(o.data),'vertices':len(o.data.vertices),
            'faces':len(o.data.polygons),'boundary_edges':sum(e.is_boundary for e in bm.edges),
            'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
            'signed_volume_m3':bm.calc_volume(signed=True),
            'bounds':[[min(v.co[k] for v in o.data.vertices),max(v.co[k] for v in o.data.vertices)] for k in range(3)]}
    bm.free()
    assert record['boundary_edges']==0 and record['nonmanifold_edges']==0,record
    assert record['signed_volume_m3']>0,record
    geometry.append(record)
for side in (0,1):
    ob=bpy.data.objects[f'SITE_Cascade_Shoulder_Continuous_{side}']
    cap=old_caps[side];n=len(cap)-1
    assert cap[:-1]==[tuple(v.co) for v in ob.data.vertices[:n]]
    assert cap[-1]==tuple(ob.data.vertices[-1].co)

platform=bpy.data.objects.get('MAIN_B_lower_platform')
platform_bounds=None
if platform:
    world=[platform.matrix_world@v.co for v in platform.data.vertices]
    platform_bounds=[[min(p[k] for p in world),max(p[k] for p in world)] for k in range(3)]
candidate=ROOT/'scene/Fallingwater_geology_candidate07b.blend'
scene['bedrock_revision']='discontinuous_beds_v2 VISUAL_PENDING'
scene['fluid_cache_warning']='Collision meshes changed. Old run01-run06 are diagnostics and may not be installed as valid new caches.'
bpy.ops.wm.save_as_mainfile(filepath=str(candidate),compress=True)
report={'status':'PASS_BOUNDED_GEOMETRY_VISUAL_NOT_RUN','frame':48,'reference_annotation':'qa/core-geology-07b-reference-annotations.png','source':str(source),'source_sha256':source_sha,
        'baseline_no_water':str(baseline),'baseline_no_water_sha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),
        'candidate':str(candidate),'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),
        'site_script_sha256':hashlib.sha256((ROOT/'scripts/site.py').read_bytes()).hexdigest(),
        'site_config_sha256':hashlib.sha256((ROOT/'data/site.json').read_bytes()).hexdigest(),
        'revision_result':result,'geometry':geometry,'old_core_mesh_sha256':before[core.name]['mesh_sha256'],
        'new_core_mesh_sha256':after[core.name]['mesh_sha256'],'upper_cap_53_vertices_equal':True,
        'lower_cap_53_vertices_equal':True,'shoulder_upper_caps_equal':True,
        'old_core_max_top_z':old_top_z,'unrelated_changed_objects':unrelated_changes,
        'unexpected_new_objects':unexpected_new,'compared_objects':len(before),
        'program_water_hidden_for_both_review_scenes':hidden,'water_mesh_data_unchanged':True,
        'lower_platform_bounds':platform_bounds,'geometry_scope':'Core and eight old shoulders only; upper and lower core caps and shoulder top caps retained. No terrain/routes/exclusions/river/water mesh changed.',
        'limits':['No render performed. Macro form needs same-camera HERO and WATER_DETAIL comparison.',
                  'Manifold and positive volume do not establish shape fidelity or collision-free unions.',
                  'Building and water-platform mesh signatures unchanged; full navigation regression remains required before production integration.',
                  'Existing full fluid caches invalid for changed collision geometry.']}
(ROOT/'qa/core-geology-candidate07b-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha
print(json.dumps({k:report[k] for k in ('status','candidate','candidate_sha256','new_core_mesh_sha256','compared_objects')},indent=2),flush=True)
