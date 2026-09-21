from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
Q=Path('D:/zx/test/project/qa')
im=Image.open(Q/'main-pool-iteration06-plan04.png').convert('RGB');dr=ImageDraw.Draw(im)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
def p(x,y):return ((x-510)*im.width/211,(y-328)*im.height/115)
for x in [533,568,575,628,674,695,706]:
 xx,_=p(x,328);dr.line((xx,0,xx,im.height),fill=(0,140,255),width=2);dr.text((xx+3,5),str(x),font=font,fill=(0,100,220))
for y in [340,352,359,367,376,379,387,420,431]:
 _,yy=p(510,y);dr.line((0,yy,im.width,yy),fill=(0,140,255),width=2);dr.text((5,yy+2),str(y),font=font,fill=(0,100,220))
im.save(Q/'main-pool-iteration06-plan04-grid.png')
