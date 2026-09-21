"""Build local bank detail on frozen 07c and measure real mesh/terrain contact."""
import bpy,json,hashlib,struct,sys
from pathlib import Path
from types import SimpleNamespace
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import bank_detail
source=ROOT/'scene/Fallingwater_geology_candidate07c.blend'
source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
assert source_sha=='24a2ca01d276cde137ff3e041ecbf5bdc028289f5b83e8be20167cb4a0c561f3'
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(48)

def mesh_hash(mesh):
    h=hashlib.sha256()
    for v in mesh.vertices:h.update(struct.pack('<3f',*v.co))
    for p in mesh.polygons:
        h.update(struct.pack('<III',len(p.vertices),p.material_index,p.use_smooth))
        for i in p.vertices:h.update(struct.pack('<I',i))
    if mesh.shape_keys:
        for key in mesh.shape_keys.key_blocks:
            for v in key.data:h.update(struct.pack('<3f',*v.co))
    return h.hexdigest()
def snapshot():
    hashes={m.name:mesh_hash(m) for m in bpy.data.meshes if m.users}
    return {o.name:{'type':o.type,'matrix':[list(r) for r in o.matrix_world],'hide_render':o.hide_render,
                    'mesh':hashes[o.data.name] if o.type=='MESH' else None,
                    'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else None} for o in scene.objects}

before=snapshot()
ctx=SimpleNamespace(root=ROOT,config=json.loads((ROOT/'config.json').read_text(encoding='utf8')))
settings={'enabled':True}
result=bank_detail.build(ctx,settings)
after=snapshot();changed=[name for name,value in before.items() if after.get(name)!=value]
assert not changed,changed[:20]
new=sorted(set(after)-set(before))
assert all(bpy.data.objects[name].get('owner')==bank_detail.OWNER for name in new)
terrain=scene.objects['SITE_Continuous_BearRun_Terrain'];bvh=BVHTree.FromObject(terrain,bpy.context.evaluated_depsgraph_get())
def gap(point):
    hit,n,i,d=bvh.ray_cast(Vector((point.x,point.y,50)),Vector((0,0,-1)),100)
    assert hit is not None
    return point.z-hit.z
def describe(values):return {'count':len(values),'min_m':min(values),'max_m':max(values),'mean_m':sum(values)/len(values)} if values else None
contact={};leaf_gaps=[];substrate_gaps=[];stone_bottom=[];exclusion_failures=[]
cfg=json.loads((ROOT/'data/site.json').read_text(encoding='utf8'))
# Reuse precisely the same fully resolved exclusion list for the independent
# post-build world-vertex audit; contact itself comes from actual BVH rays.
import importlib.util
spec=importlib.util.spec_from_file_location('fw_site_bank_audit',ROOT/'scripts/site.py');fw_site=importlib.util.module_from_spec(spec);spec.loader.exec_module(fw_site)
fw_site._resolve_guest(ctx,cfg);fw_site._resolve_main(ctx,cfg)
surf=bank_detail.Surface(scene,cfg,result['settings'])
vertex_count=0
for name in new:
    o=scene.objects[name]
    if o.type!='MESH':continue
    points=[o.matrix_world@v.co for v in o.data.vertices];vertex_count+=len(points)
    for p in points:
        valid,why=surf.allowed(p.x,p.y)
        if not valid:exclusion_failures.append({'object':name,'point':list(p),'reason':why})
    if name=='BANK07_ActualSurface_FallenLeaves':
        leaf_gaps.extend(gap(p) for p in points)
        for face in o.data.polygons:
            pp=[points[i] for i in face.vertices];leaf_gaps.append(gap(sum(pp,Vector())/len(pp)))
    elif name=='BANK07_Organic_Substrate':
        substrate_gaps.extend(gap(p) for p in points)
        for face in o.data.polygons:
            pp=[points[i] for i in face.vertices];substrate_gaps.append(gap(sum(pp,Vector())/len(pp)))
    elif name.startswith('BANK07_Angular_Fragment'):
        stone_bottom.extend(gap(p) for p in points[:7])
contact={'leaf_vertices_and_face_centers':describe(leaf_gaps),'substrate_vertices_and_face_centers':describe(substrate_gaps),
         'embedded_stone_bottom_vertices':describe(stone_bottom),'fern_anchor_records':result['fern_instances'],
         'all_new_world_vertices_exclusion_checked':vertex_count,'exclusion_failures':exclusion_failures,
         'method':'Actual saved-ready mesh world vertices/triangle centers raycast to unchanged triangulated terrain; planned offsets are not substituted for measurements.'}
assert result['leaf_count']>0 and result['substrate_faces']>0
assert not exclusion_failures,exclusion_failures[:10]
assert min(leaf_gaps)>-.0011 and max(leaf_gaps)<.0181
assert min(substrate_gaps)>.0023 and max(substrate_gaps)<.0027
assert min(stone_bottom)>-.0121 and max(stone_bottom)<-.0119
candidate=ROOT/'scene/Fallingwater_bank_candidate07.blend'
scene['bank_detail_status']='CANDIDATE_VISUAL_PENDING_NOT_PRODUCTION';scene['bank_detail_module']='bank_detail.py independent; terrain/core geometry unchanged'
bpy.ops.wm.save_as_mainfile(filepath=str(candidate),compress=True)
report={'status':'PASS_LOCAL_CONTACT_AND_EXCLUSIONS_VISUAL_NOT_RUN','source_scene':str(source),'source_sha256':source_sha,
        'candidate':str(candidate),'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'frame':48,
        'settings_enabled_only_in_candidate':True,'production_integration':False,'result':result,'contact':contact,
        'new_objects':new,'new_object_count':len(new),'original_compared_objects':len(before),'original_changed_objects':changed,
        'bank_module_sha256':hashlib.sha256((ROOT/'scripts/bank_detail.py').read_bytes()).hexdigest(),
        'site_script_sha256':hashlib.sha256((ROOT/'scripts/site.py').read_bytes()).hexdigest(),
        'site_config_sha256':hashlib.sha256((ROOT/'data/site.json').read_bytes()).hexdigest(),
        'limits':['No render or GUI. Same HERO/LivingA/LoggiaB image review required before production integration.',
                  'All original geometry/material bindings/transforms/visibility unchanged; complete navigable-route sweep is not repeated in this local contact test.',
                  'Fern central low-vertex anchor is a C geometric proxy; foliage appearance/alpha/shadows need actual images.']}
(ROOT/'qa/bank07-candidate-check.json').write_text(json.dumps(report,indent=2),encoding='utf8')
(ROOT/'qa/bank07-candidate-settings.json').write_text(json.dumps(result['settings'],indent=2),encoding='utf8')
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha
print(json.dumps({'status':report['status'],'candidate_sha256':report['candidate_sha256'],'leaves':result['leaf_count'],
                  'substrate_faces':result['substrate_faces'],'stones':len(result['angular_stones']),'ferns':len(result['fern_instances']),
                  'new_objects':len(new),'contact':{k:contact[k] for k in ('leaf_vertices_and_face_centers','substrate_vertices_and_face_centers','embedded_stone_bottom_vertices')}} ,indent=2),flush=True)
