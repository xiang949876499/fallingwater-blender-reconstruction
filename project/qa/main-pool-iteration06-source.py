from PIL import Image
from pathlib import Path
import json,hashlib
Image.MAX_IMAGE_PIXELS=None
R=Path('D:/zx/test/research/references/architecture');Q=Path('D:/zx/test/project/qa')
im=Image.open(R/'main-04-original.tif');w,h=im.size
out=[]
for name,box in [('plan04',(510,328,721,443)),('landing04',(658,340,718,402))]:
 x0,y0,x1,y1=box;rb=(round(y0*w/789),round(h-x1*h/1024),round(y1*w/789),round(h-x0*h/1024))
 crop=im.crop(rb).rotate(-90,expand=True).convert('RGB');crop.thumbnail((2600,1800))
 p=Q/f'main-pool-iteration06-{name}.png';crop.save(p)
 out.append({'artifact':str(p),'source':str(R/'main-04-original.tif'),'normalized_frame':[1024,789],'crop_box':box,'raw_crop':rb,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'kind':'unmarked original crop'})
for n,box in [('03',(500,325,725,440)),('09',(450,345,740,495))]:
 im=Image.open(R/f'main-{n}-sheet.jpg');crop=im.crop(box).resize(((box[2]-box[0])*5,(box[3]-box[1])*5))
 p=Q/f'main-pool-iteration06-plan{n}.png';crop.save(p)
 out.append({'artifact':str(p),'source':str(R/f'main-{n}-sheet.jpg'),'crop_box':box,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'kind':'JPEG enlargement, not increased source precision'})
(Q/'main-pool-iteration06-sources.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print([(r['artifact'],r['crop_box']) for r in out])
