"""Verify merge serialization and retained evidence after the completed mesh run."""
from pathlib import Path
import csv,hashlib,json,re
R=Path(__file__).resolve().parents[1];Q=R/'qa';P='dimensions12-integration12a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
j=json.loads((Q/(P+'-merged.json')).read_text(encoding='utf8'))
with (Q/(P+'-merge-proposal.csv')).open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
assert len(rows)==50 and len({r['component_id'] for r in rows})==50
assert {r['component_id'] for r in rows}=={r['id'] for r in j['measurements']}
assert sum(r['strict_independent_nominal_anchor']=='True' for r in rows)==21
assert sum(r['standard_result']=='SOURCE_PRECISION_LIMIT' for r in rows)==8
assert sum(r['standard_result']=='NOT_RUN' for r in rows)==21
for r in rows:
    actual=next(x for x in j['measurements'] if x['id']==r['component_id'])['actual_mesh_m']
    assert (r['model_m']=='' and actual is None) or float(r['model_m'])==actual
unchanged={p:sha(p)==value for p,value in j['protected_files_unchanged'].items()};assert all(unchanged.values())
assert j['full_scene_snapshot_unchanged'] and not j['central_csv_written']
review=Q/'dimensions12-review.md';missing=[p for p in re.findall(r'\]\((D:/[^)]+)\)',review.read_text(encoding='utf8')) if not Path(p).exists()];assert not missing
e=json.loads((Q/(P+'-extra.json')).read_text(encoding='utf8'))['anchors'][0]
assert len(e['stations'])==2556 and all(s['status']=='PASS' for s in e['stations'])
hit_counts={}
for s in e['stations']:
    for hit in (s['left'],s['right']):hit_counts[hit['object']]=hit_counts.get(hit['object'],0)+1
viewed=['guest-bays11-source-north.png','guest-bays11-source-endpoints-final.png','master-ceiling12-source-west-tower-labelled.png']
out={'status':'PASS_MERGE_SERIALIZATION_AND_READONLY_PROTECTION','scene_sha256':j['scene_sha256'],
     'scene_measurement_status':'21 independent printed nominal PASS; GEO02 INCOMPLETE',
     'merged_rows':50,'unique_source_ids':50,'qualified_nominal_pass':21,'source_precision_limit':8,'not_run':21,
     'finished_bay_samples':2556,'actual_hit_object_counts':hit_counts,
     'csv_actual_values_exactly_equal_json':True,'full_scene_snapshot_unchanged':True,
     'protected_files_still_unchanged':unchanged,'all_review_local_links_exist':True,
     'source_crops_actually_viewed_this_task':[{'path':str(Q/n),'sha256':sha(Q/n)} for n in viewed],
     'artifacts':[{'path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(Q.glob('dimensions12-*')) if p.is_file() and p.name!='dimensions12-verification.json']}
(Q/'dimensions12-verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in out.items() if k not in ('artifacts','protected_files_still_unchanged','source_crops_actually_viewed_this_task')},indent=2))
