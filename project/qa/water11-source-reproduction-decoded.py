"""Archive decoded field hashes for the new cache; old VDB bytes are missing."""
from pathlib import Path
import json,hashlib,gzip
import openvdb,numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parent;CACHE=ROOT/'caches/fluid_water11/source_S48_reproduction01'
out={'status':'NEW_DECODED_HASH_ARCHIVE_OLD_VDB_FULL_ARRAY_REFERENCE_UNAVAILABLE','frames':[],'old_vdb_decoded_equality_claimed':False}
for frame in range(1,13):
    path=CACHE/'data'/f'fluid_data_{frame:04}.vdb';grids=openvdb.readAllGridMetadata(str(path));row={'frame':frame,'vdb_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'grids':[]}
    for meta in grids:
        rec={'name':meta.name,'metadata':{k:str(v) for k,v in meta.metadata.items()}}
        try:g=openvdb.read(str(path),meta.name);typ=g.valueTypeName
        except Exception as e:
            rec['decoded_hash_error']=repr(e);row['grids'].append(rec);continue
        dtype=np.int32 if typ=='int32' else (np.int64 if typ=='int64' else (np.bool_ if typ=='bool' else np.float32))
        shape=(48,48,38,3) if typ in ('vec3s','vec3d','vec3i') else (48,48,38)
        rec['type']=typ
        try:
            a=np.empty(shape,dtype);g.copyToArray(a,(0,0,0));rec.update(shape=list(a.shape),dtype=str(a.dtype),decoded_dense_domain_sha256=hashlib.sha256(a.tobytes()).hexdigest(),min=float(a.min()),max=float(a.max()),finite=bool(np.isfinite(a).all()))
        except Exception as e:rec['decoded_hash_error']=repr(e)
        row['grids'].append(rec)
    out['frames'].append(row)
(P/'water11-source-reproduction-decoded.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print('REPRODUCTION_DECODED_ARCHIVE',len(out['frames']),[(g['name'],g.get('type','UNAVAILABLE')) for g in out['frames'][0]['grids']],flush=True)
