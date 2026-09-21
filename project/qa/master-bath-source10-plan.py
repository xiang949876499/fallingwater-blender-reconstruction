from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]
Image.MAX_IMAGE_PIXELS=300000000
with Image.open(root/'qa/dimension-sources08-main05-original.tif') as im:
    im=im.rotate(-90,expand=True).convert('RGB')
    w,h=im.size
    thumb=im.copy();thumb.thumbnail((1600,1600));thumb.save(root/'qa/master-bath-source10-plan-oriented.png')
    # Calibrated source uses the1024px landscape sheet width.
    box=(400,292,480,435)
    crop=im.crop(tuple(round(v*w/1024) for v in box))
    crop.thumbnail((1100,1800));crop.save(root/'qa/master-bath-source10-plan-crop.png')
    print({'source_wh':[w,h],'normalized_box':box,'crop_wh':crop.size})
