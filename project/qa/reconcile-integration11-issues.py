from pathlib import Path
import csv,io,hashlib,json
root=Path(__file__).resolve().parents[1];p=root/'qa/issues.csv';data=p.read_bytes()
backup=root/'qa/issues-before-integration11-review.csv';assert not backup.exists()
r=csv.DictReader(io.StringIO(data.decode('utf-8-sig')));fields=r.fieldnames;rows=list(r)
updates={
'FW-002':('candidate11','OPEN','INCOMPLETE','Combined11 saved120 cameras pass sampled3720 rays. Full120 actual images pending; guest12 bay details do not replace complete Theater coverage.','project/qa/camera11-actual-check.json'),
'FW-005':('candidate12','OPEN','FAIL','Two west wall faces and true Study aperture accepted in actual local images. Tower12 wrapped courses and source-height correction reviewed separately; remaining masonry too uniform.','project/qa/masonry-wall12-root-visual.md'),
'FW-016':('candidate11/12','OPEN','FAIL','Combined canopy and soil improve locally; broad bare banks still nonphotographic. Actual leaf-litter12 images rejected as uniform fragments with hard boundary; not installed.','project/qa/integration11-root-visual.md'),
'FW-023':('candidate11','OPEN','INCOMPLETE','Continuous south low field and outward casement accepted locally. Fixed-torso doorway and96terrace frames pass; exact source high/low elevations unresolved and being independently reread.','project/qa/master-navigation11-review.md'),
'FW-024':('water11-S48','OPEN','ORIGINAL_CACHE_MISSING','Original36files remain missing. Isolated reproduction24config/mesh files byte-identical and12VDB differ; historical12frame measurements equal. Old full VDB arrays unavailable; no original restoration claim.684otherfiles unchanged.','project/qa/water11-source-reproduction-review.md'),
'FW-025':('iteration10;camera12','OPEN','INCOMPLETE','Old overview fails tree obstruction; new35mm birdseye actually viewed and locally accepted, preserving trees. Not yet saved to working scene or accepted as source-photo match.','project/qa/overview12-root-visual.md'),
}
for row in rows:
    if row['issue_id'] in updates:
        for key,value in zip(('scene_version','issue_state','result','description','evidence_path'),updates[row['issue_id']]):row[key]=value
assert 'FW-026' not in {r['issue_id'] for r in rows}
new=('FW-026','P1','GEO-06;VIS-01','candidate11/terrace12','L2 slab-parapet exterior interfaces','OPEN','INCOMPLETE',
     'Combined11 actual HERO/overview show new black bands; rays prove coincident outward slab/parapet faces. Interface12 removes overlapping slab volumes and actual HERO is now clear. Independent evaluated union/seam checks pending.',
     'project/qa/terrace12-blackband-probe.json',
     'Same-camera actual render plus independent topology, occupied union, structural support and unchanged source dimensions')
rows.append(dict(zip(fields,new)));backup.write_bytes(data)
with p.open('w',encoding='utf8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
print(json.dumps({'rows':len(rows),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
