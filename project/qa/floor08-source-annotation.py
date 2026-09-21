"""Annotate saved source drawings with explicit construction versus census edges."""
from pathlib import Path
import sys,json
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));import main_house
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
sets=[('05',(238,215,477,422),4,['MAIN_L2_DRESSING','MAIN_L2_BATH_N','MAIN_L2_BATH_G','MAIN_L2_BATH_M'],['dressing_bath','guest_bath','master_bath','hall_dressing','dressing_terrace']),('06',(316,267,439,312),8,['MAIN_L3_GALLERY'],['gallery_bath'])]
for sheet,crop,scale,rooms,tids in sets:
    src=Image.open(R.parent/f'research/references/architecture/main-{sheet}-sheet.jpg').convert('RGB');h=85
    out=Image.new('RGB',((crop[2]-crop[0])*scale,(crop[3]-crop[1])*scale+h),(250,250,246));out.paste(src.crop(crop).resize((out.width,out.height-h),Image.Resampling.LANCZOS),(0,h));d=ImageDraw.Draw(out,'RGBA')
    def q(p):return ((p[0]-crop[0])*scale,(p[1]-crop[1])*scale+h)
    d.text((12,9),f'MAIN{sheet} saved source / floor revision08',font=font,fill=(20,20,20,255))
    d.text((12,36),'Blue: original census   Red: physical floor   Green: doorway connection',font=small,fill=(20,20,20,255))
    d.text((12,59),'C trace evidence / same floor Z / walls, doors and stairs unchanged',font=small,fill=(20,20,20,255))
    for rid in rooms:
        old=next(r[3] for r in main_house.ROOM_SPECS if r[0]==rid);new=main_house.closed_floor_source_polygon(rid)
        d.line([q(p) for p in old+[old[0]]],fill=(34,100,225,255),width=2)
        d.line([q(p) for p in new+[new[0]]],fill=(210,25,31,255),width=3)
        center=next(r[4] for r in main_house.ROOM_SPECS if r[0]==rid);label=rid.replace('MAIN_L2_','').replace('MAIN_L3_','');at=q(center);bb=d.textbbox(at,label,font=small);d.rectangle(bb,fill=(255,255,255,200));d.text(at,label,font=small,fill=(10,10,10,255))
    for tid in tids:
        rr=next(t[2] for t in main_house.THRESHOLDS if t[0]==tid);nr=main_house.physical_threshold_source_rect(tid,rr);p=main_house.rect(*nr)
        d.polygon([q(a) for a in p],fill=(0,180,95,35));d.line([q(a) for a in p+[p[0]]],fill=(0,130,66,255),width=3)
    if sheet=='06':
        d.rectangle([q((367,270)),q((433,290))],outline=(150,99,0,255),width=3);d.text(q((373,273)),'STAIR UNCHANGED',font=small,fill=(120,65,0,255))
    out.save(R/f'qa/floor08-main{sheet}-source-overlay.png')

src=Image.open(R.parent/'research/references/architecture/main-05-sheet.jpg').convert('RGB')
crop=(301,295,343,337);scale=15;header=84
out=Image.new('RGB',(630,714),(250,250,246));out.paste(src.crop(crop).resize((630,630),Image.Resampling.LANCZOS),(0,header));d=ImageDraw.Draw(out,'RGBA')
def q(p):return ((p[0]-crop[0])*scale,(p[1]-crop[1])*scale+header)
p=main_house.core_north_backing_source_polygon();d.polygon([q(a) for a in p],fill=(235,60,40,28));d.line([q(a) for a in p+[p[0]]],fill=(205,30,25,255),width=4)
d.line([q((316,305)),q((316,325))],fill=(30,90,205,255),width=4)
d.rectangle([q((311,304)),q((324,320))],outline=(0,140,70,255),width=3)
d.text((10,10),'MAIN05 / stepped core backing, revision08',font=font,fill=(20,20,20,255))
d.text((10,35),'Red: solid core trace   Green: recess kept open',font=small,fill=(20,20,20,255))
d.text((10,57),'Blue: unsupported straight relief removed (py305..325)',font=small,fill=(20,20,20,255))
out.save(R/'qa/floor08-core-source-overlay.png')
