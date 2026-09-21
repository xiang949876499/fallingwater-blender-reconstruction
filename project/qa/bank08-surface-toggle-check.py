"""In-memory default-material regression; never saves a Blender scene or renders."""
import bpy, hashlib, json, struct, sys, time
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
frozen=json.loads((ROOT/'qa/bank08-frozen-inputs.json').read_text(encoding='utf8'))
FROZEN=Path(frozen['frozen_context'])
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(FROZEN/'scripts'))
import near_terrain_detail as near

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def mesh_hash(mesh):
    h=hashlib.sha256()
    for v in mesh.vertices:h.update(struct.pack('<3f',*v.co))
    for p in mesh.polygons:
        h.update(struct.pack('<III',len(p.vertices),p.material_index,p.use_smooth))
        for i in p.vertices:h.update(struct.pack('<I',i))
    return h.hexdigest()
def snapshot():
    hashes={m.name:mesh_hash(m) for m in bpy.data.meshes if m.users}
    return {o.name:{'matrix':[list(r) for r in o.matrix_world],
                     'hide_render':o.hide_render,'type':o.type,
                     'mesh':hashes[o.data.name] if o.type=='MESH' else None}
            for o in bpy.context.scene.objects}
def material_state(material):
    return {'name':material.name,'pointer':material.as_pointer(),
            'nodes':[(n.name,n.bl_idname,[(i.name,str(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in material.node_tree.nodes],
            'links':[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in material.node_tree.links]}

source=ROOT/'scene/Fallingwater_iteration07.blend'
candidate=ROOT/'scene/Fallingwater_bank_candidate08.blend'
candidate_sha='b1d2085191e24132c76ce1765aad414b7298cd67ca3ea8ed392014bb4f490257'
assert sha(source)==frozen['source_sha256']
assert sha(candidate)==candidate_sha
for dependency in frozen['dependencies']:
    assert sha(FROZEN/dependency['file'])==dependency['sha256']
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.scene.frame_set(48)
ctx=SimpleNamespace(root=FROZEN,config=frozen['source_embedded_config'])
terrain=bpy.context.scene.objects['SITE_Continuous_BearRun_Terrain']
source_materials=[material_state(m) for m in terrain.data.materials]
source_attributes=sorted((a.name,a.data_type,a.domain) for a in terrain.data.attributes)
source_material_count=len(bpy.data.materials)
assert near.build_bridge_front08(ctx)=={'status':'NOT_RUN_DISABLED'}
assert not terrain.get('fw_bridge08_applied')
def forbidden_tint(_surface):raise AssertionError('Default geometry-only path invoked material mutation')
near.ground_material=forbidden_tint
start=time.monotonic()
result=near.build_bridge_front08(ctx,{'enabled':True})
assert result['options']['surface_tint'] is False
assert result['material']=={'status':'UNCHANGED_SOURCE_MATERIAL','surface_tint':False}
assert source_materials==[material_state(m) for m in terrain.data.materials]
assert source_material_count==len(bpy.data.materials)
new_attributes=sorted((a.name,a.data_type,a.domain) for a in terrain.data.attributes)
print('BANK08_ATTRIBUTES',json.dumps({'before':source_attributes,'after':new_attributes}),flush=True)
added_attributes=sorted(set(new_attributes)-set(source_attributes))
removed_attributes=sorted(set(source_attributes)-set(new_attributes))
assert not added_attributes,added_attributes
# BMesh removes a redundant all-smooth sharp_face layer; polygon use_smooth
# is included in the independent legacy-candidate fingerprint below.
assert not set(removed_attributes)-{('sharp_face','BOOLEAN','FACE')},removed_attributes
assert 'bank08_litter_weight' not in terrain.data.attributes
assert 'bank07b_litter_weight' not in terrain.data.attributes
applied=snapshot();marker=terrain['fw_bridge08_applied']
try:near.build_bridge_front08(ctx,{'enabled':True})
except ValueError as error:repeat_error=str(error)
else:raise AssertionError('Repeated mutation was not rejected')
assert applied==snapshot()
assert marker==terrain['fw_bridge08_applied']
bpy.ops.wm.open_mainfile(filepath=str(candidate));bpy.context.scene.frame_set(48)
legacy=snapshot()
different=[name for name in set(applied)|set(legacy) if applied.get(name)!=legacy.get(name)]
assert not different,different
try:near.build_bridge_front08(ctx,{'enabled':True})
except ValueError as error:legacy_error=str(error)
else:raise AssertionError('Unmarked legacy grey candidate was not rejected')
assert legacy==snapshot()
assert sha(source)==frozen['source_sha256'] and sha(candidate)==candidate_sha
report={'status':'PASS_DEFAULT_SOURCE_MATERIAL_GEOMETRY_EQUAL_LEGACY08_REPEAT_BLOCKED',
        'source_sha256':frozen['source_sha256'],'legacy_candidate_sha256':candidate_sha,
        'helper_sha256':sha(ROOT/'scripts/near_terrain_detail.py'),
        'compared_objects':len(applied),'object_geometry_matrix_render_flag_differences':different,
        'default_surface_tint':False,'source_material_slots_nodes_links_unchanged':True,
        'material_datablock_count_unchanged':True,'added_mesh_attributes':added_attributes,
        'removed_redundant_mesh_attributes':removed_attributes,
        'ground_material_function_never_called':True,'repeated_call_rejected_before_mutation':repeat_error,
        'legacy_candidate_rejected_before_mutation':legacy_error,
        'source_and_legacy_blend_files_unchanged':True,'new_blend_saved':False,'rendered':False,
        'max_lowering_m':result['max_lowering_m'],'terrain_counts':result['terrain_vertices_before_after'],
        'tree_pairs':len(result['vegetation']['tree_pairs']),'elapsed_s':time.monotonic()-start,
        'limits':'Local path structure accepted by root; entire environment remains visually rejected. No new rendered appearance implied.'}
(ROOT/'qa/bank08-surface-toggle-check.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('BANK08_SURFACE_TOGGLE',json.dumps(report),flush=True)
