"""Lossless source crops for reading the HABS tower witness line; no model edits."""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageOps
R=Path(__file__).resolve().parents[2];Q=R/'project/qa'
p=R/'research/references/architecture/main-10-original.tif'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(p)=='db6591996c049961a50ba593c002dc394d5708f1c15c5935e1c3671aed1e2ac7'
# The already registered official1-bit scan is exactly241,313,664 pixels.
# Bounded per-process decoder allowance, not a global Pillow setting/file edit.
Image.MAX_IMAGE_PIXELS=250000000
im=Image.open(p);before={'size':list(im.size),'orientation':im.getexif().get(274),'mode':im.mode,'dpi':[float(x) for x in im.info.get('dpi',[])]}
im.load();after={'size':list(im.size),'orientation':im.getexif().get(274),'mode':im.mode}
if im.width<im.height:
    assert before['orientation']==8
    im=im.transpose(Image.Transpose.ROTATE_270);operation='Rotate90deg clockwise, verified visually against official1024px sheet; EXIF8 alone gave wrong upside-down result. Decoder removed EXIF without rotating pixel dimensions.'
else:operation='Pillow TIFF decoder applied EXIF orientation8 during load; no second rotation'
print('ORIENTATION_DIAGNOSTIC',before,after,im.size,flush=True)
assert im.size==(17702,13632)
specs={
 'west-section-context':(440,418,940,662),
 'tower-top-native':(453,423,650,471),
 'tower-line-label-native':(838,424,936,461),
 'tower-line-middle-native':(626,434,851,451),
 'main-zero-label-native':(835,610,938,644),
 'main-zero-end-native':(522,610,640,642),
 'east-zero-native':(817,254,938,286),
 'title-native':(947,386,1010,728),
 'title-date-native':(933,686,1023,789)
}
records=[]
for name,box in specs.items():
    rect=[round(box[0]*im.width/1024),round(box[1]*im.height/789),round(box[2]*im.width/1024),round(box[3]*im.height/789)]
    crop=im.crop(rect);suffix='';resize=None
    if name=='west-section-context':
        crop.thumbnail((2300,1500));resize=list(crop.size);suffix='-overview'
    dest=Q/f'tower-height12-source-{name}{suffix}.png';crop.save(dest)
    records.append({'name':name,'path':str(dest.relative_to(R)),'oriented_native_crop_xyxy':rect,'size':list(crop.size),'source_jpeg_locator_xyxy':box,'resized_to':resize,'sha256':sha(dest),'viewed':False})
out={'source':str(p.relative_to(R)),'source_sha256':sha(p),'raw_before_load':before,'after_decode':after,'orientation_operation':operation,'oriented_size':list(im.size),'JPEG_locator_size':[1024,789],'crops':records,'rights':'HABS reference data; no texture/model material use'}
(Q/'tower-height12-source-crops.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
