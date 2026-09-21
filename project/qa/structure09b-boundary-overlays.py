"""Measured QA annotations, not a candidate render or generated reference."""
from pathlib import Path
import sys,json,hashlib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import main_house as mh
Image.MAX_IMAGE_PIXELS=300_000_000
manifest=[]
def outline(draw,points,tr,color,width=3):
 q=[tr(p) for p in points];draw.line(q+[q[0]],fill=color,width=width)
source=R.parent/'research/references/architecture/main-04-original.tif'
im=Image.open(source);w,h=im.size;box=(522,288,568,313);x0,y0,x1,y1=box
raw=(round(y0*w/789),round(h-x1*h/1024),round(y1*w/789),round(h-x0*h/1024))
base=im.crop(raw).rotate(-90,expand=True).convert('RGB');p=R/'qa/structure09b-main04-native.png';base.save(p)
manifest.append(dict(path=str(p),source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),normalized_source_box=box,raw_crop=raw,rotation=-90))
draw=ImageDraw.Draw(base);tr=lambda p:((p[0]-x0)*base.width/(x1-x0),(p[1]-y0)*base.height/(y1-y0))
outline(draw,mh.coat_east_source_polygon(),tr,'#d22222',3)
outline(draw,mh.closed_floor_source_polygon('MAIN_L1_LOGGIA'),tr,'#1569c7',3)
x,y=tr((534.7675,300.7277));draw.ellipse((x-5,y-5,x+5,y+5),outline='#e400df',width=3)
draw.rectangle((4,4,base.width-4,48),fill='white');draw.text((10,9),'MAIN04 native TIFF / red: stone / blue: floor',fill='black');draw.text((10,26),'Source traces C; magenta: original failing plane point',fill='black')
base.save(R/'qa/structure09b-main04-boundary.png')
source6=R.parent/'research/references/architecture/main-06-sheet.jpg'
box=(416,249,444,307);x0,y0,x1,y1=box
base=Image.open(source6).convert('RGB').crop(box).resize(((x1-x0)*14,(y1-y0)*14))
draw=ImageDraw.Draw(base);tr=lambda p:((p[0]-x0)*14,(p[1]-y0)*14)
outline(draw,mh.closed_floor_source_polygon('MAIN_L3_ALCOVE'),tr,'#d22222',3)
outline(draw,[(432,259),(435,259),(435,291),(432,291)],tr,'#116dc0',2)
x,y=tr((433,265));draw.ellipse((x-6,y-6,x+6,y+6),outline='#e400df',width=3)
draw.rectangle((4,4,base.width-4,68),fill='white');draw.text((9,9),'MAIN06 JPEG enlargement, NOT high-res',fill='black');draw.text((9,26),'Blue: restored strip. Red: final floor.',fill='black');draw.text((9,43),'Stair void x<432 remains open. C +/-1px.',fill='black')
base.save(R/'qa/structure09b-main06-boundary.png')
manifest.append(dict(path='qa/structure09b-main06-boundary.png',source=str(source6),source_sha256=hashlib.sha256(source6.read_bytes()).hexdigest(),normalized_source_box=box,scale=14,precision_note='Enlargement adds no detail. Original TIFF official URL returned403 and was not downloaded.'))
data=json.loads((R/'qa/structure09b-candidate-check.json').read_text())
for camera,box in [('CAM_MAIN_L1_LOGGIA_A',(520,315,710,460)),('CAM_MAIN_L3_ALCOVE_B',(45,350,265,540))]:
 src=R/'renders/previews/iteration09-structure'/f'{camera}.png';im=Image.open(src).convert('RGB');d=ImageDraw.Draw(im)
 for p in data['projections']:
  if p['camera']!=camera or p['label']=='stair void':continue
  x,y=p['pixel_960x540'];d.ellipse((x-6,y-6,x+6,y+6),outline='#ed00ff',width=2);d.text((x+8,y-16),p['label'],fill='#f600ff')
 crop=im.crop(box).resize(((box[2]-box[0])*3,(box[3]-box[1])*3));canvas=Image.new('RGB',(crop.width,crop.height+48),'white');canvas.paste(crop,(0,48));d=ImageDraw.Draw(canvas)
 d.text((8,7),'FROZEN09 IMAGE + checked09b target projection',fill='black');d.text((8,25),'Diagnostic boundary crop only. Candidate is NOT rendered.',fill='black')
 out=R/'qa'/f'structure09b-{camera}-boundary.png';canvas.save(out)
 manifest.append(dict(path=str(out),baseline_image=str(src),candidate_sha256=data['candidate_sha256'],meaning='Old rendered image with mathematically projected new target points; not a candidate render.',crop_pixels=box))
(R/'qa/structure09b-boundary-manifest.json').write_text(json.dumps(manifest,indent=2))
print('Four explicit QA boundary overlays saved; inspection required.')
