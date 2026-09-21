"""Verify nonempty generated cache files, SHA-256, and gzip stream integrity."""
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
run=sys.argv[1] if len(sys.argv)>1 else 'run05'
if not re.fullmatch(r'[A-Za-z0-9_-]+',run):
    raise ValueError('Run must be one directory name')
reference=json.loads((root/f'qa/fluid-{run}.json').read_text(encoding='utf-8'))
cache=root/reference['settings']['cache_relative_path']
out={'run':run,'scope':'generated-file hashes, nonzero sizes and gzip integrity; not visual or final portability acceptance','files':[]}
for path in sorted(cache.rglob('*')):
    if not path.is_file():continue
    sha=hashlib.sha256();size=0
    with path.open('rb') as stream:
        while chunk:=stream.read(1024*1024):sha.update(chunk);size+=len(chunk)
    assert size>0,f'Empty cache file: {path}'
    record={'path':str(path.relative_to(cache)),'bytes':size,'sha256':sha.hexdigest()}
    if path.suffix=='.gz':
        decoded=0
        with gzip.open(path,'rb') as stream:
            while chunk:=stream.read(1024*1024):decoded+=len(chunk)
        record.update(gzip_crc='PASS',decompressed_bytes=decoded)
    out['files'].append(record)
out['file_count']=len(out['files']);out['bytes']=sum(p['bytes'] for p in out['files'])
out['mesh_count']=sum(Path(p['path']).parent.name=='mesh' for p in out['files'])
assert out['mesh_count']==reference['settings']['frames'],'Wrong generated mesh frame count'
out['status']='PASS_GENERATED_CACHE_FILES'
(root/f'qa/fluid-cache-{run}.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:out[k] for k in ('run','file_count','bytes','mesh_count','status')}))
