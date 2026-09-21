"""Independent 2D furniture placement diagnostic; proxy overlaps are not solid collision tests."""
import json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
records=json.loads((ROOT/'qa/interiors-build.json').read_text(encoding='utf-8'))['rooms']
main=json.loads((ROOT/'data/main_house.json').read_text(encoding='utf-8'))['rooms']
data=json.loads((ROOT/'data/guest_house.json').read_text(encoding='utf-8'))
reg=data['registration']; origin=reg['origin_px']; scale=reg['meters_per_pixel']; world=reg['world_origin']
def xy(p): return [world[0]+(p[0]-origin[0])*scale[0],world[1]+(origin[1]-p[1])*scale[1]]
rooms={r['id']:r for r in main}
for src in data['rooms']:
    r=dict(src);r['polygon']=[xy(p) for p in r['polygon']];r['z']=world[2]+data['levels'][r['level']]['offset']
    r['entry']=xy(r['entry']);rooms[r['id']]=r
def rect(a):
    angle=math.radians(a['angle_degrees']);ca,sa=math.cos(angle),math.sin(angle);x,y=a['center'][:2]
    return [(x+ca*xx-sa*yy,y+sa*xx+ca*yy) for xx,yy in [(-a['width']/2,-a['depth']/2),(a['width']/2,-a['depth']/2),(a['width']/2,a['depth']/2),(-a['width']/2,a['depth']/2)]]
def overlap(p,q):
    for polygon in (p,q):
        for i,a in enumerate(polygon):
            b=polygon[(i+1)%len(polygon)];axis=(b[1]-a[1],a[0]-b[0])
            p1=[x*axis[0]+y*axis[1] for x,y in p];q1=[x*axis[0]+y*axis[1] for x,y in q]
            if min(max(p1),max(q1))-max(min(p1),min(q1))<.001: return False
    return True
selected=[r for r in records if r['asset_count']]
W,H=1440,math.ceil(len(selected)/4)*320
im=Image.new('RGB',(W,H),'#f4f0e7');d=ImageDraw.Draw(im)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',11)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',9)
warnings=[]
for idx,report in enumerate(selected):
    col,row=idx%4,idx//4;left,top=col*360,row*320
    r=rooms[report['room_id']];poly=r['polygon'];xs=[p[0] for p in poly];ys=[p[1] for p in poly]
    x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys);s=min(310/(x1-x0),265/(y1-y0))
    def px(p): return (left+25+(p[0]-x0)*s,top+290-(p[1]-y0)*s)
    d.text((left+9,top+7),r['id'],font=font,fill='#332d25')
    d.polygon([px(p) for p in poly],fill='#fffdf6',outline='#151e1d',width=2)
    e=px(r['entry']);d.ellipse((e[0]-4,e[1]-4,e[0]+4,e[1]+4),fill='#27793d')
    for n,a in enumerate(report['assets']):
        color=('#c4b08d' if a['center'][2]<r['z']+.2 else '#a4c1b5')
        d.polygon([px(p) for p in rect(a)],fill=color,outline='#74634c')
        d.text(px(a['center']),str(n),font=small,fill='#14231d')
    # Exclude intentionally superposed surface props from proxy floor collisions.
    floor=[a for a in report['assets'] if a['center'][2]<r['z']+.2 and not any(k in a['type'] for k in ('art','lamp','vessel','kettle','bedrock','towel'))]
    for i,a in enumerate(floor):
        for b in floor[i+1:]:
            if overlap(rect(a),rect(b)):
                warnings.append({'room_id':r['id'],'asset_a':a['type'],'asset_b':b['type'],'severity':'PROXY_OVERLAP_REVIEW'})
    d.text((left+9,top+302),' '.join(f'{n}:{a["type"][:12]}' for n,a in enumerate(report['assets']))[:58],font=small,fill='#514b40')
im.save(ROOT/'qa/interiors-plan-contact.png')
(ROOT/'qa/interiors-layout-findings.json').write_text(json.dumps({'status':'PROXY_CHECK_NOT_SOLID_COLLISION_VALIDATION','overlaps':warnings},indent=2),encoding='utf-8')
print(json.dumps(warnings,indent=2))
