"""Acquire one CC0 leaf-scan candidate; checksum exact official 2K files."""
import json, hashlib
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
import requests
ROOT=Path(__file__).resolve().parents[1];QA=ROOT/'qa';AID='leaves_forest_ground'
session=requests.Session();session.headers['User-Agent']='Fallingwater-research/1.0 (local material study)'
meta={}
for key in ('info','files'):
    url=f'https://api.polyhaven.com/{key}/{AID}'
    response=session.get(url,timeout=45);response.raise_for_status();meta[key]=response.json()
    (QA/f'terrain-material08-{AID}-{key}.json').write_text(json.dumps(meta[key],indent=2),encoding='utf8')
print('ASSET_INFO',json.dumps(meta['info']),flush=True)
rows=[]
for channel,suffix,fmt in [('Diffuse','diff','jpg'),('Rough','rough','jpg'),('Displacement','disp','png')]:
    record=meta['files'][channel]['2k'][fmt]
    assert urlsplit(record['url']).hostname=='dl.polyhaven.org'
    assert 0<record['size']<30_000_000
    target=ROOT/'assets/textures'/f'{AID}_{suffix}_2k.{fmt}'
    if not target.exists():
        response=session.get(record['url'],timeout=60);response.raise_for_status();data=response.content
        assert len(data)==record['size'] and hashlib.md5(data).hexdigest()==record['md5']
        target.write_bytes(data)
    data=target.read_bytes()
    assert len(data)==record['size'] and hashlib.md5(data).hexdigest()==record['md5']
    rows.append({'channel':channel,'path':target.relative_to(ROOT).as_posix(),'bytes':len(data),
                 'md5':record['md5'],'sha256':hashlib.sha256(data).hexdigest(),'url':record['url']})
report={'status':'DOWNLOADED_VERIFIED_NOT_YET_VISUALLY_REVIEWED','asset':AID,
        'retrieved_utc':datetime.now(timezone.utc).isoformat(),'asset_url':f'https://polyhaven.com/a/{AID}',
        'api_info_url':f'https://api.polyhaven.com/info/{AID}','api_files_url':f'https://api.polyhaven.com/files/{AID}',
        'license':'CC0','license_url':'https://polyhaven.com/license',
        'license_evidence':'Official asset page labels CC0; official license permits sharing assets with projects and standalone redistribution.',
        'info':meta['info'],'files':rows,'total_bytes':sum(r['bytes'] for r in rows),
        'production_manifest_changed':False,'old_asset_files_changed':False,'paid_purchase':False,
        'limits':'Raw asset files only. Preview renders, logos and website text are not included in the CC0 asset claim.'}
(QA/'terrain-material08-asset-download.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('ASSET_DOWNLOAD',json.dumps({'files':rows,'total_bytes':report['total_bytes']}),flush=True)
