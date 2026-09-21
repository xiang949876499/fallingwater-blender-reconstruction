"""Read four public Columbia panorama page/config files as reference data."""
from pathlib import Path
import urllib.request, urllib.parse, re, json, hashlib

out=Path(__file__).resolve().parent/'panorama10'
out.mkdir(exist_ok=True)
base='https://projects.mcah.columbia.edu/ha/panos/Fallingwater/'
pages={
 'guest-entrance':'Guest-House/Guest-House-Entrance/',
 'guest-living':'Guest-House/Guest-House-Living-Room/',
 'master-bedroom':'Master-Bedroom/',
 'master-bathroom':'Master-Bathroom/',
}
records=[]
for label,tail in pages.items():
    url=base+tail
    record={'id':label,'url':url,'source':'Columbia MCAH institutional panorama',
            'distribution':'REFERENCE_ONLY_EXCLUDE_PUBLIC_PACKAGE','images_viewed':False}
    try:
        payload=urllib.request.urlopen(url,timeout=25).read(2000000)
        (out/(label+'.html')).write_bytes(payload)
        html=payload.decode('utf-8',errors='replace')
        record['html_sha256']=hashlib.sha256(payload).hexdigest()
        record['scripts']=re.findall(r'<script[^>]+src=[\"\']([^\"\']+)',html)
        record['config_candidates']=re.findall(r'[\"\']([^\"\']+\.xml(?:\?[^\"\']*)?)[\"\']',html)
        record['config_calls']=[line.strip() for line in html.splitlines() if any(t in line for t in ('readConfig','images/','embedpano','createPano'))]
        for i,config in enumerate(record['config_candidates']):
            config_url=urllib.parse.urljoin(url,config)
            data=urllib.request.urlopen(config_url,timeout=25).read(3000000)
            (out/(label+f'-config{i}.xml')).write_bytes(data)
            record.setdefault('configs',[]).append({'url':config_url,'path':label+f'-config{i}.xml','bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'excerpt':data[:1800].decode('utf-8',errors='replace')})
        record['status']='PAGE_CONFIG_DOWNLOADED_IMAGES_NOT_VIEWED'
    except Exception as exc:
        record.update(status='FAILED',error=str(exc))
    records.append(record)
(out/'discovery.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(records,ensure_ascii=False,indent=2))
