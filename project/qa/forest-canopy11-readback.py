import bpy,sys,json,hashlib,time
from pathlib import Path
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];Q=ROOT/'qa';sys.path[:0]=[str(ROOT/'scripts'),str(Q)]
import shrub08_auditlib as audit
import forest_canopy11 as entry
check=json.loads((Q/'forest-canopy11-check.json').read_text(encoding='utf-8'))
assert check['status']=='PHYSICAL_PASS_VISUAL_NOT_RUN'
target=ROOT/'scene/Fallingwater_forest_canopy_candidate11a.blend'
assert hashlib.sha256(target.read_bytes()).hexdigest()==check['candidate_sha256']
assert hashlib.sha256((ROOT/'scripts/forest_canopy11.py').read_bytes()).hexdigest()==check['helper_sha256']
bpy.ops.wm.open_mainfile(filepath=str(target));start=time.monotonic();report={'status':'RUNNING','candidate_sha256':check['candidate_sha256'],'rendered':False,'saved_again':False}
try:
 expected=json.loads((Q/'forest-canopy11-fingerprint.json').read_text(encoding='utf-8'));snapshot=audit.snapshot()
 assert audit.digest(snapshot)==expected['snapshot_sha256']
 report['full_snapshot_exact']=True
 bpy.context.scene.frame_set(48)
 assert check['protected_physics']=={n:audit.physical_hash(bpy.context.scene.objects[n]) for n in check['protected_physics']}
 report['protected_physical_hashes_exact']=len(check['protected_physics'])
 connection=[]
 for index in entry.SELECTION:
  asset=entry.generate(index);oldb=entry.mesh_bvh(asset['old_branch']);excluded=set(check['pruning']['excluded_by_asset'][str(index)])
  count=0;fail=[]
  for g in asset['groups']:
   if g['id'] in excluded:continue
   child=BVHTree.FromPolygons(g['branch_v'],g['branch_f'],all_triangles=True)
   pairs=oldb.overlap(child)
   if not pairs:fail.append(g['id'])
   count+=1
  row={'asset':index,'retained_new_shoots':count,'actual_triangle_contact_with_original_wood_pass':count-len(fail),'no_triangle_contact_groups':fail};connection.append(row)
  print('FOREST11_READBACK_CONNECTION',row,flush=True)
 report['new_branch_connections']=connection
 report['status']='FRESH_REOPEN_PASS_VISUAL_NOT_RUN' if not any(r['no_triangle_contact_groups'] for r in connection) else 'FRESH_REOPEN_EXACT_BUT_BRANCH_CONTACT_FAIL'
except Exception as e:report['status']='READBACK_FAILED';report['exception']=repr(e);raise
finally:
 report['elapsed_s']=time.monotonic()-start;(Q/'forest-canopy11-readback.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('FOREST11_READBACK',report['status'],flush=True)
