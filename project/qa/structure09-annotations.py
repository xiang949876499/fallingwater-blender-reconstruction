"""Source-plan construction-edge annotations, not generated reference images."""
import sys,json
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import main_house as mh
def line(d,p,transform,color,width=3):
 pp=[transform(x) for x in p];d.line(pp+[pp[0]],fill=color,width=width)
# Original TIFF crop has normalized source bounds 487,280..546,346.
im=Image.open(R/'qa/structure08b-remaining-main04-original-crop.png').convert('RGB');d=ImageDraw.Draw(im)
tr=lambda p:((p[0]-487)*im.width/59,(p[1]-280)*im.height/66)
line(d,mh.entry_east_corner_source_polygon(),tr,'#e33131',5)
for p,label,color in [((529.3135,333.0027),'L-core repaired','#e33131'),((534.7675,300.7277),'Right boundary unresolved','#0033ee')]:
 x,y=tr(p);d.ellipse((x-5,y-5,x+5,y+5),outline=color,width=3);d.text((x-175,y+12),label,fill=color)
d.rectangle((8,8,540,53),fill='white');d.text((15,15),'MAIN04 original crop / red: bounded core infill',fill='black');d.text((15,32),'Blue point stays unresolved; no broad floor patch',fill='black')
im.save(R/'qa/structure09-entry-core-source-overlay.png')
im=Image.open(R.parent/'research/references/architecture/main-06-sheet.jpg').convert('RGB').crop((326,229,479,311)).resize((1224,656));d=ImageDraw.Draw(im);tr=lambda p:((p[0]-326)*8,(p[1]-229)*8)
for rid in ('MAIN_L3_BATH','MAIN_L3_ALCOVE'):
 old=next(r[3] for r in mh.ROOM_SPECS if r[0]==rid)
 line(d,old,tr,'#225cdb',2);line(d,mh.closed_floor_source_polygon(rid),tr,'#e33131',3)
line(d,mh.physical_threshold_source_polygon('gallery_alcove',(432,291,438,304)),tr,'#179951',3)
for p,label in [((400,280),'stair retained'),((420,280),'stair retained')]:
 x,y=tr(p);d.ellipse((x-4,y-4,x+4,y+4),outline='#d28800',width=2);d.text((x-40,y+8),label,fill='#946000')
d.rectangle((8,598,930,649),fill='white');d.text((16,606),'MAIN06 / blue: inset census floor; red: bounded physical floor; green: shared threshold',fill='black');d.text((16,625),'Bath north pocket is enclosed; Alcove only gains the north corner. Stair void is retained.',fill='black')
im.save(R/'qa/structure09-l3-physical-floor-overlay.png')
im=Image.open(R.parent/'research/references/architecture/main-05-sheet.jpg').convert('RGB').crop((329,302,374,329)).resize((900,540));d=ImageDraw.Draw(im);tr=lambda p:((p[0]-329)*20,(p[1]-302)*20)
line(d,mh.rect(337,308,366,323),tr,'#225cdb',3)
line(d,mh.closed_floor_source_polygon('MAIN_L2_CLOSET_M'),tr,'#e33131',4)
line(d,mh.closed_ceiling_source_polygon('MAIN_L2_CLOSET_M'),tr,'#179951',2)
d.rectangle((8,440,882,532),fill='white');d.text((16,451),'MAIN05 / blue: old closet slab overlapping Master below y312',fill='black');d.text((16,476),'Red: retained floor strip; Master supplies the rest at unchanged floor Z',fill='black');d.text((16,501),'Green: ceiling extends only x366..368 to existing adjacent soffit',fill='black')
im.save(R/'qa/structure09-master-source-overlay.png')
print('Three source overlays saved; inspection required.')
