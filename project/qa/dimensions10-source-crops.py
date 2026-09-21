"""Local archival crop extraction only; no image synthesis or source alterations."""
from pathlib import Path
from PIL import Image
import json,hashlib
R=Path(__file__).resolve().parents[1];W=R.parent
Image.MAX_IMAGE_PIXELS=300000000
sources={
 'main04':W/'research/references/architecture/main-04-original.tif',
 'main05':R/'qa/dimension-sources08-main05-original.tif',
 'main10':W/'research/references/architecture/main-10-original.tif',
}
crops={
 'main04':[('service',(160,185,280,300)),('southwest',(50,400,355,575)),('south-glyph',(48,450,90,550))],
 'main05':[('topchain',(60,50,725,200)),('westchain',(45,190,330,620)),('eastbottom',(300,295,720,620))],
 'main10':[('section-east',(160,100,705,385)),('section-west',(240,425,690,745))],
}
rows=[]
for key,path in sources.items():
    with Image.open(path) as raw:
        size=raw.size;im=raw.rotate(-90,expand=True) if raw.width<raw.height else raw.copy()
        w,h=im.size
        for label,b in crops[key]:
            dest=R/'qa'/f'dimensions10-{key}-{label}.png'
            if dest.exists():raise RuntimeError(str(dest))
            native=tuple(round(v*w/1024) for v in b)
            pic=im.crop(native).convert('RGB');pic.thumbnail((2000,2000));pic.save(dest)
            rows.append({'id':f'{key}-{label}','source':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
               'source_size':size,'oriented_size':[w,h],'rotate_degrees':-90 if size[0]<size[1] else 0,
               'normalized_box':b,'oriented_native_box':native,'output':str(dest),'output_size':pic.size,
               'view_status':'NOT_YET_VIEWED'})
        del im
(R/'qa/dimensions10-source-crops.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps(rows,indent=2))
