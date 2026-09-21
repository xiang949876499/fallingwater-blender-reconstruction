"""Record manually inspected dimension witnesses; annotation never changes source."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
Q=Path(__file__).resolve().parent
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23)
def annotated(src,dst,lines,points,labels):
    base=Image.open(Q/src).convert('RGB');out=Image.new('RGB',(base.width,base.height+100),'white');out.paste(base,(0,0));d=ImageDraw.Draw(out)
    for line in lines:d.line(line,fill=(12,142,72),width=3)
    for x,y in points:d.ellipse((x-10,y-10,x+10,y+10),outline=(202,32,22),width=3)
    for i,label in enumerate(labels):d.text((18,base.height+10+28*i),label,font=font,fill='black')
    out.save(Q/dst)
    return {'source_excerpt':src,'sha256':hashlib.sha256((Q/src).read_bytes()).hexdigest(),'annotation':dst,'green_lines':'manually selected SOURCE witness/face planes','red_circles':'printed dimension ticks and physical faces','source_face_points_excerpt_pixels':points,'explanations':labels,'view_status':'NOT_YET_VIEWED'}
rows=[]
rows.append(annotated('dimensions10-main05-westchain.png','dimensions10-main05-west-witnesses-annotated.png',[(137,40,137,1950),(918,150,918,1940),(65,55,630,55),(110,526,920,526)],[(116,55),(116,526),(400,55),(400,526),(137,1913),(918,1913),(137,300),(918,400)],['17 ft 6 3/8 in: NORTH outer face -> SOUTH outer face (not centre/clear span).','28 ft 11 1/4 in: WEST terrace outer face -> dressing stone WEST face.','Green source planes are chosen from the drawing, not fitted to mesh values.']))
rows.append(annotated('dimensions10-main05-southwidth-detail.png','dimensions10-main05-southwidth-annotated.png',[(82,0,82,310),(785,0,785,310)],[(82,288),(785,288),(82,100),(785,100)],['25 ft 5 1/4 in: opposite OUTER parapet faces.','Both witness marks align with the exterior corner/edge.']))
rows.append(annotated('dimensions10-main04-service.png','dimensions10-main04-service-witnesses-annotated.png',[(284,820,284,1780),(1336,750,1336,1780)],[(284,1726),(1336,1726),(284,940),(1336,900)],['10 ft 11 in: WEST pier OUTSIDE face -> kitchen stone WEST face.','Not room net width; west pier thickness is included. Existing plaster substitute is C.']))
(Q/'dimensions10-witness-annotations.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print('3 annotated witness sheets written')
