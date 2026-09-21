"""Filesystem-only incident inventory. Never imports or starts Blender."""
from pathlib import Path
import json, hashlib, datetime

P=Path(__file__).resolve().parent
ROOT=P.parent
OUT=P/'water11-source-cache-incident.json'
assert not OUT.exists(), 'Preserve the first incident inventory'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while chunk:=f.read(8*1024*1024): h.update(chunk)
    return h.hexdigest()
def row(p): return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
old=json.loads((P/'water11-source-r075-preserved-cache-manifest.json').read_text(encoding='utf8'))
current=[];missing=[];changed=[]
for r in old:
    p=Path(r['path'])
    if not p.is_file(): missing.append(r);continue
    n=row(p);current.append(n)
    if n!=r:changed.append({'before':r,'after':n})
scenes=sorted((ROOT/'scene').glob('Fallingwater_water11_source_*.blend*'))
artifacts=sorted(p for p in P.glob('water11-source*') if p.is_file())
artifact_rows=[row(p) for p in scenes+artifacts]
missing_sizes={r['bytes'] for r in missing};missing_hashes={r['sha256'] for r in missing}
matches=[]
for p in ROOT.rglob('*'):
    if p.is_file() and p.stat().st_size in missing_sizes:
        h=sha(p)
        if h in missing_hashes:matches.append({'path':str(p),'sha256':h})
counts={}
for r in current:
    prefix=str(Path(r['path']).relative_to(ROOT/'caches')).replace('\\','/').split('/')
    key='/'.join(prefix[:2]);counts.setdefault(key,{'files':0,'bytes':0})
    counts[key]['files']+=1;counts[key]['bytes']+=r['bytes']
r={'status':'INCIDENT_S48_ORIGINAL_CACHE_MISSING_R075_PAUSED',
   'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
   'cause_observed':'After opening original S48 prepared blend, primary particle_radius assigned before changing cache_directory; subsequent protection audit found all 36 original S48 cache files missing. No explicit delete command was used.',
   'cause_inference':'Blender fluid RNA parameter update invalidated and removed cache at the still-original path. Exact callback was not independently traced.',
   'before_manifest':str(P/'water11-source-r075-preserved-cache-manifest.json'),
   'before_files':len(old),'before_bytes':sum(x['bytes'] for x in old),
   'remaining_files':len(current),'remaining_bytes':sum(x['bytes'] for x in current),
   'remaining_by_cache':counts,'remaining_hash_changes':changed,
   'missing_files':missing,'missing_bytes':sum(x['bytes'] for x in missing),
   'all_current_remaining_cache_hashes':current,'surviving_scenes_and_source_artifact_hashes':artifact_rows,
   'project_backup_search':'All project files with matching missing-file byte lengths were SHA256 checked; no matching backup was found unless listed.',
   'matching_project_backups':matches,
   'recovery_bake_run':False,'r075_bake_run':False,'r075_fresh_reopen_run':False,
   'r075_saved_candidate_not_ready':str(ROOT/'scene/Fallingwater_water11_source_S48_R075.blend'),
   'historical_S48_metrics_still_archived_but_raw_recheck_currently_unavailable':True,
   'prohibited_claims':['old cache unchanged','recomputed files are originals without per-file identity comparison','historical flow failure is now passed']}
assert len(missing)==36 and r['missing_bytes']==7748027 and not changed
assert all('source_S48\\' in x['path'] for x in missing)
OUT.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:r[k] for k in ['status','before_files','remaining_files','missing_bytes','remaining_by_cache','matching_project_backups']},ensure_ascii=False))
