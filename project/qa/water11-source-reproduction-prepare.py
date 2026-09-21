"""Factory-only S48 reproduction preparation. No bake or render entry."""
import sys,json,copy,importlib.util,time
from pathlib import Path
import bpy,numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parent
spec=importlib.util.spec_from_file_location('source_helpers',P/'water11-source-prepare.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
ARM='S48_reproduction01'
REPORT=P/'water11-source-reproduction-prepare.json'
SCENE=ROOT/f'scene/Fallingwater_water11_source_{ARM}.blend'
CACHE=ROOT/f'caches/fluid_water11/source_{ARM}'
INCIDENT=P/'water11-source-cache-incident.json'
EXPECTED=json.loads(INCIDENT.read_text(encoding='utf8'))

def guard():
    changed=[]
    for r in EXPECTED['all_current_remaining_cache_hashes']:
        q=Path(r['path'])
        if not q.is_file() or q.stat().st_size!=r['bytes'] or p.w.sha(q)!=r['sha256']:changed.append(r['path'])
    assert not changed,changed
    assert all(not Path(r['path']).exists() for r in EXPECTED['missing_files']),'Never refill original missing S48 paths'
    return {'remaining_cache_files_verified':684,'remaining_cache_bytes':EXPECTED['remaining_bytes'],'original_missing36_still_missing':True}

def domain_path_guard(d):
    assert Path(bpy.path.abspath(d.cache_directory)).resolve()==CACHE.resolve()
    domains=[m for o in bpy.data.objects for m in o.modifiers if m.type=='FLUID' and m.fluid_type=='DOMAIN']
    assert len(domains)==1
    assert Path(bpy.path.abspath(domains[0].domain_settings.cache_directory)).resolve()==CACHE.resolve()

def set_physics(d,owner,key,value):
    domain_path_guard(d)
    before=getattr(owner,key)
    equal=list(before)==value if isinstance(value,list) else before==value
    if not equal:setattr(owner,key,value)
    domain_path_guard(d)

def prepare():
    assert not REPORT.exists() and not SCENE.exists() and not CACHE.exists(),'One independent prepare, preserve existing files'
    assert bpy.app.background
    assert all(not any(m.type=='FLUID' for m in o.modifiers) for o in bpy.data.objects),'Factory process must have no inherited fluid modifiers'
    assert not bpy.data.filepath,'Only factory-startup; never open old scene'
    before=guard();old=json.loads(p.REPORT.read_text(encoding='utf8'))['arms']['S48'];old_scene=Path(old['scene'])
    assert p.w.sha(old_scene)==old['scene_sha256']
    names=tuple([p.JET]+list(old['collider_geometry_hashes']))
    # Mesh datablocks only. Do not load Object, Scene, Collection or Modifier.
    with bpy.data.libraries.load(str(old_scene),link=False) as (src,dst):
        assert all(n in src.meshes for n in names),(names,src.meshes)
        dst.meshes=list(names)
    loaded={m.name:m for m in dst.meshes};assert set(loaded)==set(names),(list(loaded),names)
    assert all(not any(m.type=='FLUID' for m in o.modifiers) for o in bpy.data.objects)
    for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
    s=bpy.context.scene;flows=bpy.data.collections.new('W11_Reproduction_New_Flows');s.collection.children.link(flows)
    rocks=bpy.data.collections.new('W11_Reproduction_New_Effectors');s.collection.children.link(rocks)
    objects={}
    for name,me in loaded.items():
        o=bpy.data.objects.new(name,me);(flows if name==p.JET else rocks).objects.link(o);objects[name]=o
        expected=old['source_geometry_sha256'] if name==p.JET else old['collider_geometry_hashes'][name]
        assert p.w.h.shape_hash(o)==expected,(name,'Mesh-only identity world hash mismatch')
    CACHE.mkdir(parents=True)
    lo,hi=np.array(old['domain_aabb_m']).T
    domain=p.w.cube(p.DOMAIN,lo,hi)
    m=domain.modifiers.new('New isolated reproduction domain','FLUID');m.fluid_type='DOMAIN'
    d=m.domain_settings
    # Bootstrap creates a new domain. This is its first settings assignment.
    d.cache_directory=str(CACHE);domain_path_guard(d)
    for key,value in old['actual_domain'].items():set_physics(d,d,key,value)
    for name,o in objects.items():
        domain_path_guard(d);mod=o.modifiers.new('New isolated source or collision','FLUID')
        if name==p.JET:
            mod.fluid_type='FLOW';f=mod.flow_settings
            for key,value in old['source_flow'].items():set_physics(d,f,key,value)
        else:
            mod.fluid_type='EFFECTOR';e=mod.effector_settings
            for key,value in {'effector_type':'COLLISION','surface_distance':.001,'use_plane_init':False,'use_effector':True}.items():set_physics(d,e,key,value)
        o.hide_render=True
    d.fluid_group=flows;d.effector_group=rocks;domain_path_guard(d)
    s.frame_start=1;s.frame_end=12;s.render.fps=24;s.render.threads_mode='FIXED';s.render.threads=4
    s.use_gravity=True;s.gravity=(0,0,-9.81);s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
    s.frame_set(1);bpy.context.view_layer.update()
    a=copy.deepcopy(old)
    for key in ['before_save_checks','fresh_process_reopen_checks','scene_sha256','prepare_seconds']:a.pop(key,None)
    a.update(scene=str(SCENE),cache=str(CACHE),actual_domain=p.state(d),base_scene=str(old_scene),base_scene_sha256=old['scene_sha256'])
    assert a['actual_domain']==old['actual_domain'],'No physical parameter differences permitted'
    a['before_save_checks']=p.validate(a)
    a['loaded_data_types']=['MESH'];a['loaded_old_fluid_objects']=0;a['new_domain_first_settings_assignment']='isolated cache_directory'
    a['all_fluid_parameter_setters_guarded_by_new_cache_path']=True
    s['water11_status']='S48_REPRODUCTION_NEW_FACTORY_NOT_ORIGINAL_CACHE_NOT_BAKED'
    bpy.ops.wm.save_as_mainfile(filepath=str(SCENE));a['scene_sha256']=p.w.sha(SCENE)
    assert p.w.sha(old_scene)==old['scene_sha256']
    after=guard()
    r={'status':'REPRODUCTION_PREPARED_FRESH_REOPEN_REQUIRED_NO_BAKE','arm':ARM,'arms':{ARM:a},'incident':str(INCIDENT),
       'before_guard':before,'after_guard':after,'no_bake':True,'no_render':True,'physical_differences_from_original_S48':{},
       'original_missing_cache_not_refilled':True,'new_cache_empty':not any(q.is_file() for q in CACHE.rglob('*')),
       'comparison_required':'Compare 36 new files against original missing-file SHA list. Any mismatch is reproduction, not byte restoration.'}
    p.dump(REPORT,r);print('S48_REPRODUCTION_PREPARED',a['scene_sha256'],flush=True)

def reopen():
    r=json.loads(REPORT.read_text(encoding='utf8'));a=r['arms'][ARM]
    assert p.w.sha(SCENE)==a['scene_sha256'];before=guard()
    bpy.ops.wm.open_mainfile(filepath=str(SCENE))
    # Read-only checks after opening only the NEW isolated scene; no RNA assignments.
    a['fresh_process_reopen_checks']=p.validate(a)
    d=next(m.domain_settings for m in bpy.context.scene.objects[p.DOMAIN].modifiers if m.type=='FLUID');domain_path_guard(d)
    assert not any(q.is_file() for q in CACHE.rglob('*'))
    assert p.w.sha(SCENE)==a['scene_sha256']
    r['reopen_before_guard']=before;r['reopen_after_guard']=guard();r['arms'][ARM]=a
    r['status']='REPRODUCTION_FRESH_REOPEN_PASS_NO_BAKE';p.dump(REPORT,r);print('S48_REPRODUCTION_FRESH_REOPEN_PASS',flush=True)

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:]
    if args==['prepare']:prepare()
    elif args==['reopen']:reopen()
    else:raise ValueError('prepare or reopen only; no bake/render')
