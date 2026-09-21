"""Review annotation on the saved Main06 source; no synthetic reference image."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]
j=json.loads((R/'qa/photo-match07-study-floor-check.json').read_text())
source=Image.open(R.parent/'research/references/architecture/main-06-sheet.jpg').convert('RGB')
crop=(220,212,447,344);scale=5;pad=90
out=Image.new('RGB',((crop[2]-crop[0])*scale,(crop[3]-crop[1])*scale+pad),(248,248,244))
out.paste(source.crop(crop).resize(((crop[2]-crop[0])*scale,(crop[3]-crop[1])*scale),Image.Resampling.LANCZOS),(0,pad))
d=ImageDraw.Draw(out,'RGBA')
f=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
fs=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
def q(p):return ((p[0]-crop[0])*scale,(p[1]-crop[1])*scale+pad)
old=[(253,237),(310,237),(310,267),(319,267),(319,322),(253,322)]
new=j['physical_source_polygon']
d.polygon([q(p) for p in new],fill=(255,70,65,24))
d.line([q(p) for p in new+[new[0]]],fill=(202,28,31,255),width=3)
d.line([q(p) for p in old+[old[0]]],fill=(30,89,218,255),width=3)
threshold=[(318,278),(333,278),(333,303),(318,303),(318,278)]
d.line([q(p) for p in threshold],fill=(0,140,77,255),width=3)
d.rectangle([q((367,270)),q((432,304))],outline=(180,112,0,255),width=3)
d.text((15,10),'MAIN06 original plan / Study physical floor closure 07',font=f,fill=(25,25,25,255))
d.text((15,39),'Blue: inset census   Red: actual wall-face floor   Green: unchanged doorway threshold',font=fs,fill=(25,25,25,255))
d.text((15,62),'C trace evidence; 5 mm wall lap is construction tolerance, not survey accuracy. Orange: stair excluded.',font=fs,fill=(25,25,25,255))
for text,at in [('North wall inner face', (252,217)),('Existing threshold',(336,308)),('Stepped chimney return',(267,335)),('Stair unchanged',(369,259))]:
    pos=q(at);b=d.textbbox(pos,text,font=fs);d.rectangle((b[0]-3,b[1]-2,b[2]+3,b[3]+2),fill=(250,250,246,220));d.text(pos,text,font=fs,fill=(30,30,30,255))
out.save(R/'qa/photo-match07-study-floor-source-overlay.png')
