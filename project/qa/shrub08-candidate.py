"""Authorized sixteen-instance isolated candidate. CPU4, no render/production."""
import bpy,sys,json,hashlib,time,re,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'qa'))
import understory_detail08 as asset
import shrub08_auditlib as audit
SOURCE=ROOT/'scene/Fallingwater_iteration08.blend'
TARGET=ROOT/'scene/Fallingwater_shrub_candidate08.blend'
SOURCE_SHA='c5cd501e4c8ae0205ecb2437cd2d06d0c92bcc9a87e7d93d3986aeef976070d7'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE)==SOURCE_SHA
assert not TARGET.exists(),'Never overwrite an existing candidate'
design_raw=(ROOT/'qa/terrain-material08-shrub-design.json').read_bytes()
design=json.loads(design_raw);assert design['source_sha256']==SOURCE_SHA
route_raw=(ROOT/'qa/tour-path-route-iteration08-attempt01.json').read_bytes()
route=json.loads(route_raw);assert route['source_scene_sha256']==SOURCE_SHA
(ROOT/'qa/shrub08-frozen-route.json').write_bytes(route_raw)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene;frame=scene.frame_current;scene.frame_set(frame);bpy.context.view_layer.update()
inputs={k.replace('\\','/'):v for k,v in json.loads(bpy.data.texts['FW_BUILD_INPUTS.json'].as_string()).items()}
frozen_site=ROOT/'qa/bank08-frozen-context/data/site.json'
assert sha(frozen_site)==inputs['data/site.json'],'Use source-matched exclusion data only'
site_data=json.loads(frozen_site.read_text())
exclusion=next(x for x in site_data['building_exclusions'] if x['name']=='main_plunge_and_stair')
report={'status':'RUNNING','source_sha256':SOURCE_SHA,'candidate':str(TARGET),'rendered':False,'production_integration':False,
        'source_frame':frame,'comparison_frame':48,'design_sha256':hashlib.sha256(design_raw).hexdigest(),
        'frozen_route_sha256':hashlib.sha256(route_raw).hexdigest(),'frozen_site_sha256':sha(frozen_site),
        'helper_sha256':sha(ROOT/'scripts/understory_detail08.py'),'audit_helper_sha256':sha(ROOT/'qa/shrub08_auditlib.py'),
        'script_sha256':sha(Path(__file__))}
start=time.monotonic()
def write():
    (ROOT/'qa/shrub08-candidate-check.json').write_text(json.dumps(report,indent=2),encoding='utf8')
try:
    selection=design['selection']
    targets={r[k] for r in selection for k in ('leaf_object','branch_object')}
    assert len(selection)==16 and len(targets)==32
    count=lambda:len([o for o in scene.objects if re.fullmatch(r'TREE_Understory_\d{4}_Leaves',o.name)])
    before_count=count();assert before_count==2400
    print('SHRUB08_STAGE before_fingerprint',flush=True)
    before=audit.snapshot()
    (ROOT/'qa/shrub08-source-snapshot.json').write_text(json.dumps(before,separators=(',',':')),encoding='utf8')
    print('SHRUB08_STAGE source_fingerprint_done',len(before['objects']),flush=True)
    source_terrain_material=[m.name for m in scene.objects['SITE_Continuous_BearRun_Terrain'].data.materials]
    assert source_terrain_material==['FW_Continuous_Forest_Floor']
    original_meshes={name:scene.objects[name].data for name in targets}
    scene.frame_set(48);bpy.context.view_layer.update()
    physics_names=[o.name for o in scene.objects if o.type=='MESH' and o.name.startswith(('SITE_Core_','SITE_Cascade_Shoulder_Continuous','WATER_'))]
    physics_before={name:audit.physical_hash(scene.objects[name]) for name in physics_names}
    old_bvh,old_owners=audit.world_bvh([scene.objects[name] for name in sorted(targets)],True)
    generated={};details={}
    prune_raw=(ROOT/'qa/shrub08-prune-plan.json').read_bytes()
    pruning=json.loads(prune_raw);assert pruning['source_sha256']==SOURCE_SHA
    report['prune_plan_sha256']=hashlib.sha256(prune_raw).hexdigest()
    for index in (2,3):
        old_bark=bpy.data.meshes[f'TREE_Understory_{index}_Stems']
        old_leaf=bpy.data.meshes[f'TREE_Understory_{index}_Leaves']
        bark,leaf,record=asset.make_asset(index,old_bark.materials[0],list(old_leaf.materials),pruning['removed_design_leaf_ids'][str(index)])
        generated[index]=(bark,leaf);details[str(index)]=record
    report['assets']=details
    for row in selection:
        branch,leaf=scene.objects[row['branch_object']],scene.objects[row['leaf_object']]
        assert list(leaf.matrix_world.translation)==row['root']
        assert branch.matrix_world==leaf.matrix_world
        assert list(leaf.scale)==row['scale']
        assert not branch.modifiers and not leaf.modifiers
        branch.data,leaf.data=generated[row['asset']]
    bpy.context.view_layer.update()
    print('SHRUB08_STAGE actual_contacts',flush=True)
    contacts=audit.contact_checks(selection,details,exclusion)
    report['contact_checks']=contacts
    failures=[{'object':r['object'],'failures':r['failures']} for r in contacts if r['failures']]
    if failures:
        report['status']='FAILED_PHYSICAL_PREFLIGHT_NO_SCENE_SAVED';report['failures']=failures;write()
        raise AssertionError(('Physical candidates failed; do not save',failures))
    print('SHRUB08_STAGE route',flush=True)
    new_bvh,new_owners=audit.world_bvh([scene.objects[name] for name in sorted(targets)],True)
    nav=audit.route_regression(route,old_bvh,old_owners,new_bvh,new_owners)
    report['route_regression']=nav
    assert not nav['new_obstacles'] and nav['candidate_target_hits']==0,nav
    physics_after={name:audit.physical_hash(scene.objects[name]) for name in physics_names}
    assert physics_before==physics_after,'Frozen core/shoulder/water evaluated triangles changed'
    report['frozen_physics']=physics_after
    scene.frame_set(frame);bpy.context.view_layer.update()
    print('SHRUB08_STAGE after_fingerprint',flush=True)
    after=audit.snapshot()
    (ROOT/'qa/shrub08-candidate-snapshot.json').write_text(json.dumps(after,separators=(',',':')),encoding='utf8')
    changed=audit.compare_snapshots(before,after,targets)
    assert set(changed)==targets,(len(changed),len(targets))
    assert count()==before_count
    report.update({'status':'PASS_ISOLATED_16_SHRUB_PHYSICAL_CHECKS_VISUAL_NOT_RUN',
                   'changed_objects':sorted(changed),'compared_objects':len(before['objects']),
                   'only_object_mutation':'data pointer on 32 approved objects; data_hash and computed dimensions change with the new geometry',
                   'total_understory_instances_before_after':[before_count,count()],
                   'original_shared_meshes_materials_lights_cameras_config_unchanged':True,
                   'source_terrain_material_unchanged':source_terrain_material,
                   'candidate_snapshot_sha256':audit.digest(after),
                   'selection':selection,'new_mesh_names':[m.name for pair in generated.values() for m in pair],
                   'limitations':'Physical candidate only. Species/cultivar U; exact roots and geometry C. Existing environment and far60m Living ground still rejected. No GUI or new adjacency acceptance.'})
    (ROOT/'qa/shrub08-candidate-snapshot.json').write_text(json.dumps(after,separators=(',',':')),encoding='utf8')
    assert sha(SOURCE)==SOURCE_SHA
    bpy.ops.wm.save_as_mainfile(filepath=str(TARGET),compress=True)
    report['candidate_sha256']=sha(TARGET);report['elapsed_s']=time.monotonic()-start
    write()
    print('SHRUB08_DONE',json.dumps({k:report[k] for k in ('status','candidate','candidate_sha256','compared_objects','elapsed_s')}),flush=True)
except Exception as exc:
    report['exception']=repr(exc);report['elapsed_s']=time.monotonic()-start
    if report['status']=='RUNNING':report['status']='FAILED_NO_ACCEPTANCE'
    write()
    raise
