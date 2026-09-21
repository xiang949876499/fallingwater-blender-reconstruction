"""Stable review pages from frozen camera IDs; never include partly-written PNGs."""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
settings=json.loads((ROOT/'qa/camera04-settings-frozen.json').read_text(encoding='utf-8'))
names=sorted(settings,key=lambda n:(n.startswith('CAM_GUEST'),n))
out=ROOT/'qa/camera04-contact-sheets';out.mkdir(exist_ok=True)
folder=ROOT/'renders/rooms/iteration04'
font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',17)
pages=[]
for start in range(0,len(names),12):
    batch=names[start:start+12];paths=[folder/(n+'.png') for n in batch]
    if not all(p.exists() for p in paths):continue
    images=[];meta=[]
    try:
        for p in paths:
            with Image.open(p) as im:
                im.load();images.append(im.convert('RGB'))
                meta.append({'image':str(p.resolve()),'dimensions':list(im.size),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    except OSError:continue
    sheet=Image.new('RGB',(1280,1064),(22,25,28));draw=ImageDraw.Draw(sheet)
    for i,(n,im) in enumerate(zip(batch,images)):
        x,y=(i%3)*426,(i//3)*266
        sheet.paste(im.resize((426,240),Image.Resampling.LANCZOS),(x,y))
        draw.text((x+5,y+243),n.removeprefix('CAM_'),fill='white',font=font)
    p=out/f'page_{start//12+1:02d}.jpg';sheet.save(p,quality=94)
    pages.append({'sheet':str(p.resolve()),'images':meta})
(out/'index.json').write_text(json.dumps(pages,indent=2),encoding='utf-8')
print(json.dumps({'complete_pages':len(pages),'images':sum(len(p['images']) for p in pages)}))
