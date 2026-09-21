"""Root-only single-arm bake entry. Never invoked by prepare. No rendering."""
import sys,json,time,importlib.util
from pathlib import Path
import bpy
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('source_prepare',P/'water11-source-prepare.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
assert bpy.app.background
args=sys.argv[sys.argv.index('--')+1:];assert len(args)==2 and args[0]=='root-authorized-90s' and args[1] in ['S24','S48','S48_R075']
arm=args[1]
if arm=='S48_R075':
 spec2=importlib.util.spec_from_file_location('radius_control',P/'water11-source-r075-prepare.py');rp=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(rp)
 r=json.loads(rp.REPORT.read_text(encoding='utf8'));assert r['status']=='PREPARED_R075_REOPEN_PASS_NO_BAKE'
 assert rp.manifest()==json.loads(rp.MANIFEST.read_text(encoding='utf8'))
else:
 r=json.loads(p.REPORT.read_text(encoding='utf8'));assert r['status']=='PREPARED_TWO_ARMS_REOPEN_PASS_NO_BAKE'
a=r['arms'][arm];scene=Path(a['scene']);cache=Path(a['cache']);out=P/f'water11-source-{arm}-bake.json';baked=scene.with_name(scene.stem+'_baked.blend')
assert not out.exists() and not baked.exists() and not any(q.is_file() for q in cache.rglob('*')),'One attempt only, preserve previous/partial results'
assert p.w.sha(scene)==a['scene_sha256']
if arm!='S48_R075':assert p.preserved_manifest()==json.loads((P/'water11-source-preserved-cache-manifest.json').read_text(encoding='utf8'))
resource=p.w.resources();assert resource['physical_available_bytes']>3_000_000_000 and resource['disk_free_bytes']>1_073_741_824,resource
bpy.ops.wm.open_mainfile(filepath=str(scene));checks=p.validate(a);o=bpy.context.scene.objects[p.DOMAIN]
for ob in bpy.context.selected_objects:ob.select_set(False)
o.select_set(True);bpy.context.view_layer.objects.active=o
q={'status':'BAKING_UNDER_ROOT_EXTERNAL90S','arm':arm,'prepared_sha256':a['scene_sha256'],'prebake_reopen_checks':checks,'resources':resource,'time_unix_start':time.time(),'threads':4,'frames':[1,12],'no_render':True}
p.dump(out,q);print('WATER11_SOURCE_BAKE_START',arm,flush=True);t=time.perf_counter()
try:
 result=bpy.ops.fluid.bake_all();q['bake_seconds']=time.perf_counter()-t;q['result']=list(result)
 files=[f for f in cache.rglob('*') if f.is_file()];q['cache_files']=len(files);q['cache_bytes']=sum(f.stat().st_size for f in files)
 q['mesh_frames']=len(list((cache/'mesh').glob('*.bobj.gz')))
 bpy.context.scene.frame_set(12);bpy.ops.wm.save_as_mainfile(filepath=str(baked));q['baked_scene']=str(baked);q['baked_scene_sha256']=p.w.sha(baked)
 q['prepared_scene_unchanged']=p.w.sha(scene)==a['scene_sha256'];assert q['prepared_scene_unchanged']
 q['status']='BAKED_REQUIRES_FRAME1_AND_ALL12_NATIVE_AUDIT';p.dump(out,q);print('WATER11_SOURCE_BAKE_DONE',arm,q['bake_seconds'],q['mesh_frames'],flush=True)
except Exception as e:
 q['status']='FAILED_NO_RETRY';q['exception']=repr(e);q['seconds_until_error']=time.perf_counter()-t;p.dump(out,q);raise
