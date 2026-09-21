"""Fetch the four horizontal800px original faces of four public panoramas."""
from pathlib import Path
import urllib.request, urllib.parse, json, hashlib
from concurrent.futures import ThreadPoolExecutor
import xml.etree.ElementTree as ET
from PIL import Image

root=Path(__file__).resolve().parent/'panorama10'
records=json.loads((root/'discovery.json').read_text(encoding='utf-8'))
jobs=[]
for rec in records:
    tree=ET.fromstring((root/rec['configs'][0]['path']).read_bytes())
    alt=next(node for node in tree.findall('altinput') if node.get('tilesize')=='800')
    attribution=tree.find('userdata').attrib
    for face in range(4):
        jobs.append({'panorama_id':rec['id'],'face':face,'url':urllib.parse.urljoin(rec['url'],alt.attrib[f'tile{face}url']),
                     'page':rec['url'],'attribution':attribution,'tilescale':float(alt.attrib['tilescale']),
                     'distribution':'REFERENCE_ONLY_EXCLUDE_PUBLIC_PACKAGE','actual_view':'NOT_VIEWED'})

def fetch(rec):
    rec=dict(rec)
    path=root/(rec['panorama_id']+f'-face{rec["face"]}.jpg')
    try:
        assert not path.exists(),'Preserve original existing file'
        data=urllib.request.urlopen(rec['url'],timeout=25).read(5000000)
        path.write_bytes(data)
        with Image.open(path) as im:
            rec['dimensions']=list(im.size);im.verify()
        rec.update(status='DOWNLOADED_IMAGE_VERIFIED',path=path.name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
    except Exception as exc:
        rec.update(status='FAILED',error=str(exc))
    return rec
with ThreadPoolExecutor(max_workers=4) as pool:
    result=list(pool.map(fetch,jobs))
(root/'faces-manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'files':len(result),'success':sum(r['status']=='DOWNLOADED_IMAGE_VERIFIED' for r in result),'bytes':sum(r.get('bytes',0) for r in result)}))
