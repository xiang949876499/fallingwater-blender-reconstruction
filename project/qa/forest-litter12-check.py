"""Build/independently reopen one local litter candidate; no renderer."""
import bpy,json,sys,time,hashlib,math
from pathlib import Path
from collections import Counter
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'scripts'),str(R/'qa')]
import forest_litter12 as helper
import shrub08_auditlib as audit
SOURCE=R/'scene/Fallingwater_forest_floor_candidate11a.blend'
SOURCE_SHA='5bc4e480237bfa202b205370aea647e4501797ec46e8e335b5106f4ca9fc1d27'
TARGET=R/'scene/Fallingwater_forest_litter_candidate12a.blend'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(name,data):(R/'qa'/name).write_text(json.dumps(data,indent=2),encoding='utf8')
def full_snapshot():return json.loads(json.dumps(audit.snapshot()))
def contacts(scene):
    ground=helper.Ground(scene);rows=[];bad=[];total=0;pathbad=[];protected=[]
    for o in scene.objects:
        if not o.name.startswith('LITTER12_') or o.type!='MESH':continue
        mesh=o.data;isfern=o.name.startswith('LITTER12_Fern_');isleaf='Fallen_Leaves'in o.name
        minc=1e6;maxc=-1e6;count=0;rootmin=1e6;frondmin=1e6
        def examine(local,label):
            nonlocal minc,maxc,count,total,rootmin,frondmin
            q=o.matrix_world@local;h,n=ground.hit(q.x,q.y)
            if h is None:bad.append({'object':o.name,'point':list(q),'reason':'NO_GROUND'});return
            c=q.z-h.z;minc=min(minc,c);maxc=max(maxc,c);count+=1;total+=1
            if ground.forbidden_xy(q.x,q.y,.23):
                if len(pathbad)<30:pathbad.append({'object':o.name,'point':list(q),'reason':'FORBIDDEN_XY'})
            if ground.blocks.find_nearest(q,.002)[0]is not None:
                if len(protected)<30:protected.append({'object':o.name,'point':list(q),'reason':'PROTECTED_MESH_WITHIN_2mm'})
            root=isfern and local.z<.045 and math.hypot(local.x,local.y)<.14
            if isfern:
                if root:rootmin=min(rootmin,c)
                else:frondmin=min(frondmin,c)
            if c<(-.045 if root else -.001) or (isleaf and c>.0255):
                if len(bad)<30:bad.append({'object':o.name,'point':list(q),'clearance_m':c,'type':label,'root_zone':root})
        for v in mesh.vertices:examine(v.co,'VERTEX')
        for f in mesh.polygons:examine(sum((mesh.vertices[k].co for k in f.vertices),Vector())/len(f.vertices),'FACE_CENTER')
        rows.append({'object':o.name,'samples':count,'min_terrain_clearance_m':minc,'max_terrain_clearance_m':maxc,
                     'root_min_m':rootmin if rootmin<1e6 else None,'fern_frond_min_m':frondmin if frondmin<1e6 else None})
    return {'sample_count':total,'objects':rows,'contact_failures':bad,'road_building_footprint_failures':pathbad,
            'protected_mesh_contact_failures':protected,
            'terrain_unchanged':True,'method':'Actual saved vertices and polygon centers, real terrain BVH; source root stems alone allow45mm embedding. Exact path polygons +230mm exclusion.'}

assert sha(SOURCE)==SOURCE_SHA
if '--readback'in sys.argv:
    report=json.loads((R/'qa/forest-litter12-check.json').read_text())
    assert sha(TARGET)==report['candidate_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    # The11a source retained these zero-user legacy IDs after replacing its
    # terrain-only material. Active FLOOR11 image copies point to the same
    # unchanged files; only the unused ID cleanup is allowed on the next save.
    orphan_names=['forrest_ground_01_diff_2k.jpg','forrest_ground_01_disp_2k.jpg','forrest_ground_01_rough_2k.jpg']
    orphan_users={name:bpy.data.images[name].users for name in orphan_names}
    assert all(n==0 for n in orphan_users.values()),orphan_users
    bpy.ops.wm.open_mainfile(filepath=str(TARGET));s=bpy.context.scene
    snap=full_snapshot();expected=json.loads((R/'qa/forest-litter12-candidate-fingerprint.json').read_text())
    # Blender rewrites slash separators on the new relative CC0 image paths.
    normalization=[]
    for name,row in expected['global']['images'].items():
        if name.startswith('LITTER12_'):
            assert row[0].replace('\\','/')==snap['global']['images'][name][0].replace('\\','/')
            row[0]=snap['global']['images'][name][0];normalization.append(name)
    for name in orphan_names:
        assert name not in snap['global']['images'];expected['global']['images'].pop(name)
    matrix_error=0;dimension_error=0
    for name,row in expected['objects'].items():
        if not name.startswith('LITTER12_Fern_'):continue
        for key in ('matrix_world','matrix_local'):
            a=row['properties'][key];b=snap['objects'][name]['properties'][key]
            error=max(abs(x-y)for aa,bb in zip(a,b)for x,y in zip(aa,bb))
            assert error<1e-6 and all(a[i][3]==b[i][3]for i in range(4))
            matrix_error=max(matrix_error,error);row['properties'][key]=b
        a=row['world_matrix'];b=snap['objects'][name]['world_matrix']
        assert max(abs(x-y)for aa,bb in zip(a,b)for x,y in zip(aa,bb))<1e-6
        row['world_matrix']=b
        a=row['properties']['dimensions'];b=snap['objects'][name]['properties']['dimensions']
        error=max(abs(x-y)for x,y in zip(a,b));assert error<1e-6
        dimension_error=max(dimension_error,error);row['properties']['dimensions']=b
    if snap!=expected:
        differences={section:[k for k in set(snap[section])|set(expected[section])if snap[section].get(k)!=expected[section].get(k)]for section in snap}
        dump('forest-litter12-reopen-differences.json',differences)
    assert snap==expected,'Unexpected saved snapshot difference; see forest-litter12-reopen-differences.json'
    print('LITTER12_SAVED_SNAPSHOT_PASS_BEGIN_PHYSICAL_CONTACTS',flush=True)
    actual=contacts(s)
    dump('forest-litter12-reopen-contacts.json',actual)
    assert not actual['contact_failures'] and not actual['road_building_footprint_failures'] and not actual['protected_mesh_contact_failures']
    assert sha(TARGET)==report['candidate_sha256'] and sha(SOURCE)==SOURCE_SHA
    out={'status':'PASS_FRESH_REOPEN_LOCAL_CONTACT_AND_PROTECTION','candidate_sha256':report['candidate_sha256'],
         'full_snapshot_equal_after_explicit_serialization_normalization':True,'normalized_new_images':normalization,
         'source_zero_user_legacy_image_ids_omitted':orphan_users,
         'new_fern_matrix_save_recomposition_max_element_error':matrix_error,
         'new_fern_derived_dimensions_max_error_m':dimension_error,
         'new_fern_translation_exact':True,
         'contact_samples':actual['sample_count'],'contact_failures':0,'road_building_footprint_failures':0,
         'protected_mesh_contact_failures':0,
         'rendered':False,'saved':False,'visual_status':'NOT_RUN'}
    dump('forest-litter12-reopen.json',out);print('LITTER12_REOPEN',json.dumps(out),flush=True)
else:
    assert not TARGET.exists(),'Do not overwrite a candidate'
    t=time.monotonic();bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene
    print('LITTER12_BASELINE_SNAPSHOT',flush=True);before=full_snapshot()
    print('LITTER12_APPLY',flush=True);manifest=helper.apply(s)
    print('LITTER12_CREATED',json.dumps({'leaves':manifest['leaves']['leaf_count'],'ferns':manifest['ferns']['count'],'twigs':manifest['twigs']['count']}),flush=True)
    after=full_snapshot()
    assert all(after['objects'].get(k)==v for k,v in before['objects'].items()),'Original object changed'
    assert all(after['meshes'].get(k)==v for k,v in before['meshes'].items()),'Original mesh changed'
    for field,a in before['global'].items():
        b=after['global'][field]
        if field in ('materials','images','collections'):
            assert all(b.get(k)==v for k,v in a.items()),field
        else:assert a==b,field
    added=set(after['objects'])-set(before['objects']);assert added==set(manifest['new_objects'])
    images=[]
    for im in bpy.data.images:
        if not im.name.startswith('LITTER12_'):continue
        path=Path(bpy.path.abspath(im.filepath));size=list(im.size)
        assert path.exists() and im.has_data and size==[2048,2048]
        images.append({'image':im.name,'path':str(path),'sha256':sha(path),'colorspace':im.colorspace_settings.name})
    report={'status':'PASS_ORIGINAL_SCENE_UNCHANGED_NEW_LOCAL_MORPHOLOGY_VISUAL_NOT_RUN',
            'source_sha256':SOURCE_SHA,'candidate':str(TARGET),'helper_sha256':sha(R/'scripts/forest_litter12.py'),
            'original_objects_unchanged':len(before['objects']),'original_meshes_unchanged':len(before['meshes']),
            'original_materials_images_cameras_lights_world_actions_unchanged':True,
            'new_objects':sorted(added),'new_images':images,'manifest':manifest,
            'source_frame_preserved':s.frame_current,'rendered':False,'visual_status':'NOT_RUN'}
    dump('forest-litter12-source-fingerprint.json',before);dump('forest-litter12-candidate-fingerprint.json',after)
    bpy.ops.wm.save_as_mainfile(filepath=str(TARGET),compress=True)
    report['candidate_sha256']=sha(TARGET);report['elapsed_s']=time.monotonic()-t
    assert sha(SOURCE)==SOURCE_SHA
    dump('forest-litter12-check.json',report)
    print('LITTER12_RESULT',json.dumps({k:report[k]for k in ('status','candidate_sha256','original_objects_unchanged','elapsed_s')}),flush=True)
