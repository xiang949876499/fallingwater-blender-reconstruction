"""Single candidate build or independent readback; no rendering."""
import bpy,json,hashlib,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'qa'))
import forest_floor11 as helper
import shrub08_auditlib as audit
SOURCE=ROOT/'scene/Fallingwater_bridge10_endfix.blend'
SOURCE_SHA='2a7630b8024c37bd768e563236807f8049469172c7e44b03379a450f91637063'
TARGET=ROOT/'scene/Fallingwater_forest_floor_candidate11a.blend'
REPORT=ROOT/'qa/forest-floor11-check.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,data):Path(p).write_text(json.dumps(data,indent=2),encoding='utf8')
def material_shape(mesh):
    # Complete mesh fingerprint includes its material list; remove only that
    # pointer difference by hashing actual topology/attributes separately.
    return {'vertices':audit.block_hash(mesh.vertices,'co',3,'float32'),
            'edges':audit.block_hash(mesh.edges,'vertices',2,'int32'),
            'loops':audit.block_hash(mesh.loops,'vertex_index',1,'int32'),
            'polygon_material':audit.block_hash(mesh.polygons,'material_index',1,'int32'),
            'smooth':audit.block_hash(mesh.polygons,'use_smooth',1,'bool'),
            'attributes':[(a.name,a.domain,a.data_type,len(a.data))for a in mesh.attributes]}
def clean_target(row):
    row=json.loads(json.dumps(row));row.pop('data_hash');row.pop('material_slots')
    row['properties'].pop('active_material',None)
    return row
def read_shader(scene):
    obj=scene.objects[helper.TERRAIN];mat=obj.data.materials[0]
    assert mat.name==helper.MATERIAL
    nodes=mat.node_tree.nodes
    output=nodes['Forest Floor Output'];p=nodes['Forest Floor Principled']
    assert not output.inputs['Displacement'].is_linked
    assert p.inputs['Emission Strength'].default_value==0
    assert p.inputs['Metallic'].default_value==0 and p.inputs['Coat Weight'].default_value==0
    reachable=set()
    def walk(node):
        if node.name in reachable:return
        reachable.add(node.name)
        for socket in node.inputs:
            for link in socket.links:walk(link.from_node)
    walk(output)
    images=[]
    for n in nodes:
        if n.bl_idname!='ShaderNodeTexImage':continue
        im=n.image;path=Path(bpy.path.abspath(im.filepath));size=list(im.size)
        assert path.exists() and im.has_data and size==[2048,2048]
        assert n.name in reachable
        images.append({'name':n.name,'path':str(path),'sha256':sha(path),
                       'size':size,'space':im.colorspace_settings.name,'box_blend':n.projection_blend})
    assert len(images)==6
    assert all(l.is_valid for l in mat.node_tree.links)
    return {'images':images,'nodes':len(nodes),'output_reachable_nodes':len(reachable),
            'links':len(mat.node_tree.links),'displacement':False,'emission':False,
            'graph_sha256':audit.digest(audit.node_tree_state(mat.node_tree))}

assert sha(SOURCE)==SOURCE_SHA
if '--readback' in sys.argv:
    report=json.loads(REPORT.read_text(encoding='utf8'))
    assert sha(TARGET)==report['candidate_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(TARGET))
    after=json.loads(json.dumps(audit.snapshot()))
    frozen=json.loads((ROOT/'qa/forest-floor11-candidate-fingerprint.json').read_text(encoding='utf8'))
    expected=json.loads(json.dumps(frozen))
    # Blender drops the unreferenced old, terrain-only material on save. It is
    # not shared by another source object and remains intact in frozen source.
    baseline=json.loads((ROOT/'qa/forest-floor11-before-fingerprint.json').read_text(encoding='utf8'))
    old=report['original_material']
    references=[name for name,row in baseline['objects'].items() if any(slot[1]==old for slot in row['material_slots'])]
    assert references==[helper.TERRAIN],references
    assert old not in after['global']['materials']
    expected['global']['materials'].pop(old)
    normalized_images=[]
    for name,row in expected['global']['images'].items():
        if name.startswith('FLOOR11_'):
            a=row[0].replace('\\','/');b=after['global']['images'][name][0].replace('\\','/')
            assert a==b
            row[0]=after['global']['images'][name][0];normalized_images.append(name)
    if after!=expected:
        differences={}
        for section in expected:
            a,b=expected[section],after[section]
            for name in set(a)|set(b):
                if a.get(name)!=b.get(name):
                    differences.setdefault(section,{})[name]={'before':a.get(name),'after':b.get(name)}
        write(ROOT/'qa/forest-floor11-reopen-differences.json',differences)
        write(ROOT/'qa/forest-floor11-reopen-fingerprint.json',after)
        print('FLOOR11_READBACK_DIFFERENCES',json.dumps({k:list(v)for k,v in differences.items()}),flush=True)
    assert after==expected
    shader=read_shader(bpy.context.scene)
    assert shader==report['shader']
    assert sha(TARGET)==report['candidate_sha256'] and sha(SOURCE)==SOURCE_SHA
    result={'status':'PASS_FRESH_REOPEN_MATERIAL_SLOT_AND_DEPENDENCIES',
            'candidate_sha256':report['candidate_sha256'],'full_snapshot_equal_after_explicit_save_normalization':True,
            'serialization_differences':{'new_image_path_slashes':normalized_images,
                'unreferenced_source_material_not_saved':old,'source_material_referenced_only_by':references,
                'original_material_preserved_in_frozen_source_sha256':SOURCE_SHA},
            'shader_equal':True,'image_files_unchanged':True,'rendered':False,'saved':False}
    write(ROOT/'qa/forest-floor11-reopen.json',result)
    print('FLOOR11_REOPEN',json.dumps(result),flush=True)
else:
    assert not TARGET.exists(),'Preserve the single candidate'
    started=time.monotonic();bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene=bpy.context.scene
    print('FLOOR11_BASELINE_SNAPSHOT',flush=True)
    before=audit.snapshot();obj=scene.objects[helper.TERRAIN];physical=material_shape(obj.data)
    result=helper.apply(scene)
    print('FLOOR11_APPLIED',json.dumps({'nodes':result['nodes'],'path_segments':len(result['path_segments']),'bank_groups':len(result['bank_stack_masks'])}),flush=True)
    after=audit.snapshot()
    changed=[name for name in before['objects'] if before['objects'][name]!=after['objects'].get(name)]
    assert changed==[helper.TERRAIN],changed
    assert set(before['objects'])==set(after['objects'])
    assert clean_target(before['objects'][helper.TERRAIN])==clean_target(after['objects'][helper.TERRAIN])
    assert material_shape(obj.data)==physical
    for name,h in before['meshes'].items():
        if name!=obj.data.name:assert after['meshes'][name]==h,name
    for field,value in before['global'].items():
        if field in ('materials','images'):
            assert all(after['global'][field].get(k)==v for k,v in value.items()),field
        else:assert after['global'][field]==value,field
    assert len(after['global']['materials'])==len(before['global']['materials'])+1
    assert len(after['global']['images'])==len(before['global']['images'])+6
    shader=read_shader(scene)
    result.update(status='PASS_ONE_MATERIAL_SLOT_ONLY_VISUAL_NOT_RUN',source=str(SOURCE),source_sha256=SOURCE_SHA,
                  candidate=str(TARGET),helper_sha256=sha(ROOT/'scripts/forest_floor11.py'),
                  compared_objects=len(before['objects']),unchanged_object_count=len(before['objects'])-1,
                  changed_properties=['SITE_Continuous_BearRun_Terrain.material_slots[0]'],
                  terrain_physical_data_unchanged=True,all_other_meshes_and_objects_unchanged=True,
                  original_materials_images_lights_cameras_actions_globals_unchanged=True,
                  candidate_snapshot_sha256=audit.digest(after),terrain_physical_data=physical,shader=shader,
                  saved_frame=scene.frame_current,rendered=False,visual_status='NOT_RUN')
    write(ROOT/'qa/forest-floor11-before-fingerprint.json',before)
    write(ROOT/'qa/forest-floor11-candidate-fingerprint.json',after)
    bpy.ops.wm.save_as_mainfile(filepath=str(TARGET),compress=True)
    result['candidate_sha256']=sha(TARGET);result['elapsed_s']=time.monotonic()-started
    assert sha(SOURCE)==SOURCE_SHA
    write(REPORT,result)
    print('FLOOR11_RESULT',json.dumps({k:result[k]for k in ('status','candidate_sha256','compared_objects','nodes','elapsed_s')}),flush=True)
