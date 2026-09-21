"""Prepare the single approved primary-radius control; no bake or render."""
import sys,json,copy,importlib.util
from pathlib import Path
import bpy
P=Path(__file__).resolve().parent;ROOT=P.parent
spec=importlib.util.spec_from_file_location('source_helpers',P/'water11-source-prepare.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
ARM='S48_R075';REPORT=P/'water11-source-r075-prepare.json';SCENE=ROOT/f'scene/Fallingwater_water11_source_{ARM}.blend';CACHE=ROOT/f'caches/fluid_water11/source_{ARM}'
MANIFEST=P/'water11-source-r075-preserved-cache-manifest.json'

def manifest():
 out=p.preserved_manifest()
 for arm in ['S24','S48']:
  for f in sorted((ROOT/f'caches/fluid_water11/source_{arm}').rglob('*')):
   if f.is_file():out.append({'path':str(f),'bytes':f.stat().st_size,'sha256':p.w.sha(f)})
 return out

def prepare():
 raise RuntimeError('PAUSED after S48 cache invalidation incident. Do not reuse this copy-and-mutate path; see water11-source-cache-incident.md. A factory-only replacement requires a separate root decision.')
 assert not REPORT.exists() and not SCENE.exists() and not CACHE.exists(),'One new candidate, do not overwrite'
 old=json.loads(p.REPORT.read_text(encoding='utf8'))['arms']['S48'];assert p.w.sha(Path(old['scene']))==old['scene_sha256']
 protected=manifest();p.dump(MANIFEST,protected)
 bpy.ops.wm.open_mainfile(filepath=old['scene']);before=p.validate(old);s=bpy.context.scene;o=s.objects[p.DOMAIN];d=next(m.domain_settings for m in o.modifiers if m.type=='FLUID')
 assert abs(d.particle_radius-1)<1e-8;d.particle_radius=.75;CACHE.mkdir(parents=True);d.cache_directory=str(CACHE)
 a=copy.deepcopy(old)
 for key in ['before_save_checks','fresh_process_reopen_checks','scene_sha256','prepare_seconds']:a.pop(key,None)
 a.update(scene=str(SCENE),cache=str(CACHE),actual_domain=p.state(d),control_base_scene=old['scene'],control_base_sha256=old['scene_sha256'],threads=4)
 changes={k:[before['actual_domain'][k],v] for k,v in a['actual_domain'].items() if before['actual_domain'][k]!=v}
 assert changes=={'particle_radius':[1.,.75]},changes
 a['only_primary_physics_difference']=changes;a['before_save_checks']=p.validate(a)
 assert abs(d.mesh_particle_radius-1.25)<1e-8
 s['water11_status']='S48_R075_SINGLE_PARAMETER_CONTROL_PREPARED_NOT_BAKED'
 bpy.ops.wm.save_as_mainfile(filepath=str(SCENE));a['scene_sha256']=p.w.sha(SCENE)
 r={'status':'PREPARED_R075_FRESH_REOPEN_REQUIRED_NO_BAKE','arm':ARM,'arms':{ARM:a},'source_pair_report':str(p.REPORT),
  'base_S48_raw_flow_fail_retained':True,'only_primary_parameter_change':changes,'preserved_cache_manifest':str(MANIFEST),
  'old_cache_files':len(protected),'old_cache_bytes':sum(f['bytes'] for f in protected),'no_bake':True,'no_render':True,'production_changed':False,
  'first_frame_and_all12_audit_required':True,'source_geometry_not_scaled':True}
 assert manifest()==protected and p.w.sha(Path(old['scene']))==old['scene_sha256'];r['old_cache_hashes_unchanged']=True
 p.dump(REPORT,r);print('R075_PREPARED',a['scene_sha256'],changes,flush=True)

def reopen():
 raise RuntimeError('R075 is paused pending root review of water11-source-cache-incident.md; no Blender/RNA work is authorized in this entry.')
 r=json.loads(REPORT.read_text(encoding='utf8'));a=r['arms'][ARM];assert p.w.sha(SCENE)==a['scene_sha256']
 bpy.ops.wm.open_mainfile(filepath=str(SCENE));a['fresh_process_reopen_checks']=p.validate(a)
 assert not any(f.is_file() for f in CACHE.rglob('*'))
 r['status']='PREPARED_R075_REOPEN_PASS_NO_BAKE';r['arms'][ARM]=a;p.dump(REPORT,r);print('R075_FRESH_REOPEN_PASS',flush=True)

if __name__=='__main__':
 assert bpy.app.background
 args=sys.argv[sys.argv.index('--')+1:]
 if args==['prepare']:prepare()
 elif args==['reopen']:reopen()
 else:raise ValueError('prepare or reopen only; no bake/render')
