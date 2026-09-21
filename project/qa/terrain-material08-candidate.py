"""Copy one terrain material on frozen08; no geometry, lights or camera edits."""
import bpy, json, hashlib, struct, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'scene/Fallingwater_iteration08.blend'
SOURCE_SHA='c5cd501e4c8ae0205ecb2437cd2d06d0c92bcc9a87e7d93d3986aeef976070d7'
TARGET=ROOT/'scene/Fallingwater_terrain_material_candidate08.blend'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(SOURCE)==SOURCE_SHA
assert not TARGET.exists(),'Preserve the first isolated candidate; do not overwrite without review'
asset=json.loads((ROOT/'qa/terrain-material08-asset-download.json').read_text(encoding='utf8'))
review=json.loads((ROOT/'qa/terrain-material08-asset-view.json').read_text(encoding='utf8'))
assert review['status']=='SOURCE_DIFFUSE_AND_HEIGHT_ACTUALLY_VIEWED_SUITABLE_FOR_SINGLE_CANDIDATE'
for r in asset['files']:assert sha(ROOT/r['path'])==r['sha256']
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene

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
                    'type':o.type,'hide_render':o.hide_render,
                    'mesh':hashes[o.data.name] if o.type=='MESH' else None,
                    'slots':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else None,
                    'camera':{'lens':o.data.lens,'shift':[o.data.shift_x,o.data.shift_y],
                              'clip':[o.data.clip_start,o.data.clip_end],
                              'properties':{k:str(v) for k,v in o.items()}} if o.type=='CAMERA' else None}
            for o in scene.objects}
def material_hash(material):
    tree=material.node_tree
    nodes=[(n.name,n.bl_idname,n.mute,[(i.identifier,str(i.default_value)) for i in n.inputs if hasattr(i,'default_value')],
            n.image.filepath if n.bl_idname=='ShaderNodeTexImage' and n.image else None) for n in tree.nodes]
    links=[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in tree.links]
    return hashlib.sha256(repr((nodes,links)).encode()).hexdigest()
def lighting_state():
    return {'world':material_hash(scene.world),
            'lights':[(o.name,o.data.type,o.data.energy,list(o.data.color)) for o in scene.objects if o.type=='LIGHT'],
            'frame':scene.frame_current,'view':[scene.view_settings.view_transform,scene.view_settings.look,scene.view_settings.exposure],
            'camera':scene.camera.name if scene.camera else None}

start=time.monotonic();before=snapshot();lighting_before=lighting_state()
old_materials={m.name:material_hash(m) for m in bpy.data.materials if m.node_tree}
old_images={i.name:(i.filepath,i.colorspace_settings.name) for i in bpy.data.images}
terrain=scene.objects['SITE_Continuous_BearRun_Terrain'];source_mat=terrain.data.materials[0]
assert source_mat.name=='FW_Continuous_Forest_Floor'
assert len(terrain.data.materials)==1
mat=source_mat.copy();mat.name='FW_LeafLitter_Scan08_Candidate'
nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes['Principled BSDF']
files={r['channel']:ROOT/r['path'] for r in asset['files']}
for channel in ('Diffuse','Rough','Displacement'):
    tex=nodes['PH_'+channel];tex.image=bpy.data.images.load(str(files[channel]),check_existing=False)
    tex.image.filepath='//../'+files[channel].relative_to(ROOT).as_posix()
    tex.image.colorspace_settings.name='sRGB' if channel=='Diffuse' else 'Non-Color'
    tex.label='leaves_forest_ground / '+channel
width_m=sum(asset['info']['dimensions'])/2000
assert 1.259<width_m<1.261
nodes['Vector Math.001'].inputs['Scale'].default_value=1/width_m
# Preserve the actual scan color; no gray tint or artistic desaturation.
nodes['Mix (Legacy)'].inputs[2].default_value=(1,1,1,1)
links.new(nodes['PH_Rough'].outputs['Color'],p.inputs['Roughness'])
# Authored shading relief, not scanned z amplitude or actual displacement.
nodes['Bump.001'].inputs['Strength'].default_value=.5
nodes['Bump.001'].inputs['Distance'].default_value=.020
assert not nodes['Material Output'].inputs['Displacement'].is_linked
mat['texture_source']=asset['asset_url'];mat['license']='CC0';mat['texture_width_m']=width_m
mat['surface_evidence']='Poly Haven photographed leaf-litter scan; location/species match to Fallingwater remains C/U'
mat['height_evidence']='C authored bump Distance=.020m and Strength=.5; no measured height amplitude provided and no geometry displacement'
mat['candidate_status']='NOT_RENDERED_NOT_ACCEPTED'
terrain.data.materials[0]=mat
after=snapshot();different=[name for name in set(before)|set(after) if before.get(name)!=after.get(name)]
assert different==[terrain.name],different
assert {k:v for k,v in before[terrain.name].items() if k!='slots'}=={k:v for k,v in after[terrain.name].items() if k!='slots'}
assert lighting_before==lighting_state()
assert old_materials=={name:material_hash(bpy.data.materials[name]) for name in old_materials}
assert old_images=={name:(bpy.data.images[name].filepath,bpy.data.images[name].colorspace_settings.name) for name in old_images}
report={'status':'PASS_MATERIAL_ONLY_CANDIDATE_VISUAL_NOT_RUN','source_sha256':SOURCE_SHA,
        'source':str(SOURCE),'candidate':str(TARGET),'asset':asset['asset'],
        'source_texture_dimensions_mm':asset['info']['dimensions'],'tile_width_m':width_m,
        'copied_material':mat.name,'original_material':source_mat.name,
        'material_changes':{'images':{k:str(v.relative_to(ROOT)) for k,v in files.items()},
                            'object_mapping_scale':1/width_m,'box_blend':nodes['PH_Diffuse'].projection_blend,
                            'color_multiply':[1,1,1],'roughness':'source map direct, not compressed .7..1',
                            'bump_distance_m':.020,'bump_strength':.5,'bump_height_evidence':'C authored; not a scan z measurement'},
        'compared_objects':len(before),'only_changed_object_property':'terrain material slot 0',
        'all_geometry_topology_transforms_smooth_flags_unchanged':True,'camera_light_exposure_frame_unchanged':True,
        'all_original_materials_and_images_unchanged':True,'lighting_state':lighting_before,
        'scene_snapshot_sha256':hashlib.sha256(json.dumps(after,sort_keys=True).encode()).hexdigest(),
        'physical_terrain_mesh_sha256':after[terrain.name]['mesh'],
        'rendered':False,'no_new_leaf_tree_rock_objects':True,'script_sha256':sha(Path(__file__)),
        'limits':'Single material experiment. Existing macro terrain, sparse canopy and high room exposure remain. Root must view same three frame48 images before acceptance.'}
scene['terrain_material08_candidate']=json.dumps({k:report[k] for k in ('source_sha256','asset','tile_width_m','copied_material','status')})
bpy.ops.wm.save_as_mainfile(filepath=str(TARGET),compress=True)
report['candidate_sha256']=sha(TARGET);report['elapsed_s']=time.monotonic()-start
assert sha(SOURCE)==SOURCE_SHA
bpy.ops.wm.open_mainfile(filepath=str(TARGET));scene=bpy.context.scene
assert after==snapshot()
assert lighting_before==lighting_state()
assert all(sha(ROOT/r['path'])==r['sha256'] for r in asset['files'])
report['saved_readback_snapshot_equal']=True
(ROOT/'qa/terrain-material08-candidate-check.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('TERRAIN_MATERIAL08_CANDIDATE',json.dumps({k:report[k] for k in ('status','candidate','candidate_sha256','tile_width_m','compared_objects','saved_readback_snapshot_equal','elapsed_s')}),flush=True)
