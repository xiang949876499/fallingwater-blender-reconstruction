"""Read-only source overlays for the six bounded anomaly categories."""
from pathlib import Path
import sys
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));import main_house
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
def canvas(sheet,crop,scale,title,subtitle):
    src=Image.open(R.parent/f'research/references/architecture/main-{sheet}-sheet.jpg').convert('RGB');im=Image.new('RGB',((crop[2]-crop[0])*scale,(crop[3]-crop[1])*scale+64),(250,250,246));im.paste(src.crop(crop).resize((im.width,im.height-64),Image.Resampling.LANCZOS),(0,64));d=ImageDraw.Draw(im,'RGBA');d.text((10,8),title,font=font,fill=(25,25,25,255));d.text((10,34),subtitle,font=small,fill=(25,25,25,255))
    def q(p):return ((p[0]-crop[0])*scale,(p[1]-crop[1])*scale+64)
    def line(poly,col,w=3):d.line([q(p) for p in poly+[poly[0]]],fill=col,width=w)
    return im,d,q,line
blue=(25,90,220,255);red=(215,32,25,255);green=(0,140,65,255)
im,d,q,line=canvas('04',(164,204,250,275),8,'MAIN04 / Servant wall-side floor only','Blue census / Red physical floor / Green source slot retained (C trace)')
line(next(r[3] for r in main_house.ROOM_SPECS if r[0]=='MAIN_L1_SERVANT'),blue);line(main_house.closed_floor_source_polygon('MAIN_L1_SERVANT'),red);d.rectangle([q((177,225)),q((187,233))],outline=green,width=3);im.save(R/'qa/structure08b-servant-overlay.png')
im,d,q,line=canvas('05',(327,300,541,350),5,'MAIN05 / shared wardrobe and corridor ceilings','Blue former individual outlines / Red shared construction edges / floor Z unchanged')
for rid in ('MAIN_L2_CLOSET_M','MAIN_L2_CLOSET_G'):
    line(next(r[3] for r in main_house.ROOM_SPECS if r[0]==rid),blue);line(main_house.closed_ceiling_source_polygon(rid),red)
line([(468,301),(536,301),(536,328),(484,328),(484,344),(468,344)],blue);line(main_house.guest_corridor_ceiling_source_polygon(),red);im.save(R/'qa/structure08b-ceiling-overlay.png')
im,d,q,line=canvas('04',(497,300,579,342),8,'MAIN04 / Entry-Loggia shared floor edge','Blue original threshold / Red remaining connection / Green Loggia floor')
rr=next(t[2] for t in main_house.THRESHOLDS if t[0]=='entry_loggia');line(main_house.rect(*rr),blue);line(main_house.physical_threshold_source_polygon('entry_loggia',rr),red);line(next(r[3] for r in main_house.ROOM_SPECS if r[0]=='MAIN_L1_LOGGIA'),green);im.save(R/'qa/structure08b-loggia-overlay.png')
im,d,q,line=canvas('05',(425,121,486,182),10,'MAIN05 / lower arc landing duplicate','Blue retained terrace floor / Red duplicated rectangle removed; stairs unchanged')
line(next(r[3] for r in main_house.ROOM_SPECS if r[0]=='MAIN_L2_TERRACE_N'),blue);line(main_house.rect(468,142,474,176),red);im.save(R/'qa/structure08b-landing-overlay.png')
