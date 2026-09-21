"""Root-supervised single reproduction, isolated new scene/cache only."""
import sys,json,time,importlib.util
from pathlib import Path
import bpy
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('isolated_reproduction',P/'water11-source-reproduction-prepare.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
assert sys.argv[sys.argv.index('--')+1:]==['root-approved-reproduction90s'] and bpy.app.background
prep=json.loads(r.REPORT.read_text(encoding='utf8'));assert prep['status']=='REPRODUCTION_FRESH_REOPEN_PASS_NO_BAKE'
a=prep['arms'][r.ARM];out=P/f'water11-source-{r.ARM}-bake.json';baked=r.SCENE.with_name(r.SCENE.stem+'_baked.blend')
assert not out.exists() and not baked.exists() and not any(q.is_file() for q in r.CACHE.rglob('*'))
assert r.p.w.sha(r.SCENE)==a['scene_sha256'];before=r.guard()
resource=r.p.w.resources();assert resource['physical_available_bytes']>3_000_000_000 and resource['disk_free_bytes']>1_073_741_824
bpy.ops.wm.open_mainfile(filepath=str(r.SCENE));checks=r.p.validate(a)
o=bpy.context.scene.objects[r.p.DOMAIN];d=next(m.domain_settings for m in o.modifiers if m.type=='FLUID');r.domain_path_guard(d)
for ob in bpy.context.selected_objects:ob.select_set(False)
o.select_set(True);bpy.context.view_layer.objects.active=o
q={'status':'REPRODUCTION_BAKING_UNDER_ROOT90S','arm':r.ARM,'prepared_sha256':a['scene_sha256'],'prebake_reopen_checks':checks,
   'remaining_guard_before':before,'resources':resource,'threads':4,'frames':[1,12],'no_render':True,'original_S48_path_will_not_be_refilled':True}
r.p.dump(out,q);print('REPRODUCTION_BAKE_START',flush=True);started=time.perf_counter()
try:
    result=bpy.ops.fluid.bake_all();q['bake_seconds']=time.perf_counter()-started;q['result']=list(result)
    files=[f for f in r.CACHE.rglob('*') if f.is_file()];q['cache_files']=len(files);q['cache_bytes']=sum(f.stat().st_size for f in files)
    q['mesh_frames']=len(list((r.CACHE/'mesh').glob('*.bobj.gz')))
    bpy.context.scene.frame_set(12);bpy.ops.wm.save_as_mainfile(filepath=str(baked));q['baked_scene']=str(baked);q['baked_scene_sha256']=r.p.w.sha(baked)
    assert r.p.w.sha(r.SCENE)==a['scene_sha256'];q['remaining_guard_after']=r.guard()
    comparisons=[]
    old_root=r.ROOT/'caches/fluid_water11/source_S48'
    for old in r.EXPECTED['missing_files']:
        relative=Path(old['path']).relative_to(old_root);new=r.CACHE/relative
        h=r.p.w.sha(new) if new.is_file() else None
        comparisons.append({'relative':str(relative),'original_sha256':old['sha256'],'new_sha256':h,'identical_bytes':h==old['sha256']})
    q['original36_comparison']=comparisons
    q['byte_comparison_status']='RECOMPUTED_COPY_MATCHES_ALL_ORIGINAL36_HASHES' if all(v['identical_bytes'] for v in comparisons) else 'REPRODUCTION_NOT_BYTE_RESTORATION'
    q['status']='REPRODUCTION_COMPLETE_REQUIRES_NATIVE_ALL12_AUDIT';r.p.dump(out,q)
    print('REPRODUCTION_BAKE_DONE',q['bake_seconds'],q['byte_comparison_status'],flush=True)
except Exception as e:
    q['status']='REPRODUCTION_FAILED_PRESERVE_NO_RETRY';q['error']=repr(e);q['elapsed_seconds']=time.perf_counter()-started;r.p.dump(out,q);raise
