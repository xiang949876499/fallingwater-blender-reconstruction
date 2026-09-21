"""Future single bake entry point. NOT executed by prepare/reopen/audit."""
import sys, json, time, importlib.util
from pathlib import Path
import bpy

path=Path(__file__).with_name('water10-natural48.py')
spec=importlib.util.spec_from_file_location('natural48',path)
w=importlib.util.module_from_spec(spec); spec.loader.exec_module(w)
assert bpy.app.background
assert sys.argv[sys.argv.index('--')+1:] == ['root-authorized-2400s'], 'Future root authorization argument required'
r=json.loads(w.REPORT.read_text(encoding='utf-8'))
assert r['status']=='PREPARED_XMAX_OPEN_DIAGNOSTIC_REOPEN_PASS_NATIVE_BOUNDARY_HEAD_JOIN_UNVERIFIED'
assert w.sha(w.PILOT)==r['prepared_sha256']
assert not [p for p in w.CACHE.rglob('*') if p.is_file()], 'One attempt only. Preserve partial cache; no automatic retry'
assert not (w.P/'water10-natural48-bake-started.json').exists()
baked=w.ROOT/'scene/Fallingwater_water10_natural48_baked.blend'; assert not baked.exists()
res=w.resources(); assert res['RAM_reserve_12GB_available'] and res['disk_reserve_12GB_available'],res
assert w.manifest()==json.loads((w.P/'water10-natural48-preserved-cache-manifest.json').read_text(encoding='utf-8'))
bpy.ops.wm.open_mainfile(filepath=str(w.PILOT)); r['at_bake_reopen_assertions']=w.validate(r)
o=bpy.context.scene.objects[w.DOMAIN]
for ob in bpy.context.selected_objects: ob.select_set(False)
o.select_set(True); bpy.context.view_layer.objects.active=o
w.dump(w.P/'water10-natural48-bake-started.json',{'prepared_scene_sha256':r['prepared_sha256'],'hard_stop_seconds':2400,'resources':res,'frames':[1,48],'threads':8,'time_unix':time.time()})
r['status']='NATIVE48_BAKING_ONCE_UNDER_EXTERNAL_2400_SECOND_LIMIT'; w.dump(w.REPORT,r)
print('NATURAL48_AUTHORIZED_BAKE_START',flush=True)
t=time.perf_counter()
try:
    result=bpy.ops.fluid.bake_all()
    r['actual_bake_seconds']=time.perf_counter()-t; r['bake_result']=list(result)
    files=[p for p in w.CACHE.rglob('*') if p.is_file()]
    r['actual_cache_files']=len(files); r['actual_cache_bytes']=sum(p.stat().st_size for p in files)
    r['actual_mesh_frame_files']=len(list((w.CACHE/'mesh').glob('*.bobj.gz')))
    bpy.context.scene.frame_set(48); bpy.ops.wm.save_as_mainfile(filepath=str(baked))
    r['baked_scene']=str(baked); r['baked_scene_sha256']=w.sha(baked)
    r['old_caches_unchanged_after_bake']=w.manifest()==json.loads((w.P/'water10-natural48-preserved-cache-manifest.json').read_text(encoding='utf-8'))
    assert r['old_caches_unchanged_after_bake']
    r['status']='NATIVE48_BAKED_RAW_PHYSICS_JOIN_VISUAL_ALL_UNVERIFIED'
    w.dump(w.REPORT,r); print('NATURAL48_BAKE_FINISHED',r['actual_bake_seconds'],r['actual_cache_bytes'],flush=True)
except Exception as e:
    r['status']='NATIVE48_BAKE_FAILED_NO_AUTO_RETRY'; r['failure']=repr(e); r['actual_seconds_before_error']=time.perf_counter()-t
    w.dump(w.REPORT,r); raise
