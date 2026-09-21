from pathlib import Path
import json,hashlib
from PIL import Image
Image.MAX_IMAGE_PIXELS=300_000_000
ROOT=Path('D:/zx/test/project');records=[]
for name,source,crop in [
    ('plan','guest-01-original.tif',(270,610,325,725)),
    ('section','guest-04-upright.png',(118,455,309,623)),
    ('south','guest-03-upright.png',(116,470,325,637))]:
    path=ROOT/'data/guest_refs'/source
    image=Image.open(path)
    raw=[round(crop[i]*image.size[i%2]/(1024 if i%2==0 else 790)) for i in range(4)]
    output=ROOT/f'qa/guest-stair-wall08-source-{name}.png'
    image.crop(raw).save(output)
    records.append({'id':name,'source':str(path),'source_size':list(image.size),'normalized_crop':crop,
                    'raw_crop':raw,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'output':str(output)})
(ROOT/'qa/guest-stair-wall08-source-crops.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
