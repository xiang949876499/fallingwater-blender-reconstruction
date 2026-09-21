"""Crops and explicit analytical overlays, never represented as source arrows."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,math
P=Path('D:/zx/test/project/qa');SRC=Path('D:/zx/test/research/references/architecture/main-04-original.tif')
Image.MAX_IMAGE_PIXELS=300000000
im=Image.open(SRC).rotate(-90,expand=True).convert('RGB')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',21)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
data=json.loads(Path('D:/zx/test/project/data/main_house.json').read_text(encoding='utf-8'))
rooms={r['id']:r for r in data['rooms']}
panels=[
 dict(id='MAIN_LIVING_NOMINAL_WIDTH',name='living-width',crop=(300,250,541,546),room='MAIN_L1_LIVING',
  title='33 ft 8 in: un-arrowed room annotation, not maximum floor bounding width',
  lines=[([(314,424),(528,424)],'red','Current whole-floor X extrema: 11.2136 m'), ([(328,400),(514.5,400)],'blue','Seat-front / stone-face diagnostic: 9.7726 m; NOT a proven label span')],
  conclusion='No OCR error. The plan is stepped and includes fixed furniture. The visible seat-front-to-pier-face diagnostic and full bounding width measure different things, and neither is identified by source arrows for33ft8in. No scaling or wall shift applied.'),
 dict(id='MAIN_KITCHEN_NOMINAL_LENGTH',name='kitchen-length',crop=(245,216,340,338),room='MAIN_L1_KITCHEN',
  title='15 ft 9 in: core body and projecting south window bay are distinct spans',
  lines=[([(300,230),(300,321)],'blue','Core diagnostic Y230-321: 4.8321 m; label endpoints not specified'), ([(290,230),(290,331)],'red','Full floor now includes traced bay: 5.3631 m')],
  conclusion='No OCR error. Corrected original floor-end trace and real projecting glazing bay; full bounding length includes a projection and cannot certify the nominal label. Main core span is measured separately; +31.5mm exceeds GEO-02 24.0mm if that span were established, which it is not.'),
 dict(id='MAIN_SERVANT_NOMINAL_LENGTH',name='servant-length',crop=(170,195,269,291),room='MAIN_L1_SERVANT',
  title='11 ft 5 in: no X/Y arrows; missing north bay restored from rock/stair edges',
  lines=[([(183.5,222),(244.5,222)],'blue','Corrected floor X extrema: 3.1964 m; nominal-axis meaning unresolved')],
  conclusion='No OCR error. Prior X assignment was an assumption. The 10 ft11in extension-line dimension below the room is a separate outside span and must not be relabeled as room length. Restored the missing bay without stretching any wall to satisfy 11ft5in.'),
 dict(id='MAIN_SERVANT_NOMINAL_WIDTH',name='servant-width',crop=(170,195,269,291),room='MAIN_L1_SERVANT',
  title='9 ft 4 in: old lower rectangle omitted northern room floor',
  lines=[([(222,214.7),(222,269)],'blue','Corrected floor Y extrema: 2.88333 m; old span was 2.0709 m')],
  conclusion='No OCR error. Room continues north to the stair partition at about y214.7, following the natural rock edge. Corrected actual Y span differs +38.53mm from9ft4in, beyond GEO-02 20mm; the room label still provides no endpoints/axis assignment, so this remains an unresolved comparison, not PASS.'),
]
manifest=[]
for pan in panels:
 l,t,r,b=pan['crop'];box=(round(l*im.width/1024),round(t*im.height/789),round(r*im.width/1024),round(b*im.height/789))
 cr=im.crop(box);cr.thumbnail((1500,1600));w,h=cr.size
 canvas=Image.new('RGB',(w,max(h+130,300)),'white');canvas.paste(cr,(0,130));d=ImageDraw.Draw(canvas)
 d.text((10,6),pan['id'],fill='black',font=font)
 d.text((10,34),'OVERLAYS ARE ANALYST TRACES (C), NOT ORIGINAL DIMENSION ARROWS',fill=(160,20,20),font=small)
 d.text((10,58),pan['title'],fill='black',font=small)
 def pt(p):return ((p[0]-l)/(r-l)*w,130+(p[1]-t)/(b-t)*h)
 poly=rooms[pan['room']]['source_polygon'];d.line([pt(p) for p in poly+[poly[0]]],fill=(20,160,75),width=3)
 for n,(points,color,label) in enumerate(pan['lines']):
  cc=(195,30,30) if color=='red' else (25,65,215)
  d.line([pt(p) for p in points],fill=cc,width=3)
  for p in points:
   q=pt(p);d.ellipse((q[0]-5,q[1]-5,q[0]+5,q[1]+5),fill=cc)
   d.text((q[0]+7,q[1]+4),str(p),fill=cc,font=small)
  d.text((10,82+n*21),label,fill=cc,font=small)
 path=P/('main-dimension-resolution-'+pan['name']+'-annotated.png');canvas.save(path)
 manifest.append(dict(**pan,source=str(SRC),source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),upright_size=im.size,
                      original_upright_crop=box,normalized_frame=[1024,789],artifact=str(path),artifact_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                      annotation_evidence='C interpretation; neither source arrows nor measured survey points'))
(P/'main-dimension-resolution-evidence.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print([m['artifact'] for m in manifest])
