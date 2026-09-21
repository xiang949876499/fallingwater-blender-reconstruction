"""Read source TIFF and export lossless native inspection crops, no retouching."""
import json,hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT.parent/'research/references/architecture/main-04-original.tif'
Image.MAX_IMAGE_PIXELS=None
sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
assert sha=='3db8199eeb84cd4226cfbae2ea9192880454c1012afa6e33bf84bae6449d8d56'
im=Image.open(SOURCE);im.load();records=[]
crops={'north_west':(13280,6810,14480,7610),'south_west':(13100,9900,14500,10840),
       'south_east':(15110,9900,16310,10840),'south_dimension':(13810,11100,15550,11480)}
for name,box in crops.items():
    x0,y0,x1,y1=box;raw=(y0,im.height-x1,y1,im.height-x0)
    crop=im.crop(raw).transpose(Image.Transpose.ROTATE_270).convert('RGB')
    path=ROOT/f'qa/bridge10-native-{name}.png';crop.save(path)
    records.append({'id':name,'upright_native_box':box,'raw_native_box':raw,'output':str(path),'size':crop.size})
(ROOT/'qa/bridge10-source-crops.json').write_text(json.dumps({'source':str(SOURCE),'source_sha256':sha,'source_raw_size':im.size,
    'upright_conversion':'CW90: upright=(17682-raw_y, raw_x); crop edge coordinates use H minus edge',
    'edits':'none; lossless crop and quarter-turn only','crops':records},indent=2),encoding='utf8')
print(json.dumps(records),flush=True)
