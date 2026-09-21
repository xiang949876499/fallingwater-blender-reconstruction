from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
Image.MAX_IMAGE_PIXELS=300000000  # Known locally hashed 17673 x 13632 HABS sheet.
R=Path(__file__).resolve().parents[1];f=R/'data/guest_refs/guest-01-original.tif';im=Image.open(f)
box=(178,112,240,232);scale=15
native=(round(box[0]*im.width/1024),round(box[1]*im.height/790),round(box[2]*im.width/1024),round(box[3]*im.height/790))
crop=im.crop(native).convert('RGB').resize(((box[2]-box[0])*scale,(box[3]-box[1])*scale))
out=Image.new('RGB',(crop.width+440,crop.height+100),'white');out.paste(crop,(0,100));draw=ImageDraw.Draw(out)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19);large=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
def pixel(q):return ((q[0]-box[0])*scale,100+(q[1]-box[1])*scale)
def point(q,label,col,offset=(15,-25)):
 x,y=pixel(q);draw.ellipse((x-5,y-5,x+5,y+5),outline=col,width=3);draw.text((x+offset[0],y+offset[1]),label,font=font,fill=col,stroke_width=1,stroke_fill='white')
def world(q):return np.array([3.4+(q[0]-325)*.05256,37.1+(422-q[1])*.05272])
def source(q):return [325+(q[0]-3.4)/.05256,422-(q[1]-37.1)/.05272]
a=world((191.7,126.3));d=world((215.9,167.6))-a;d/=np.linalg.norm(d);t=np.array([-d[1],d[0]])
pn=a+d*2.486025;ps=pn+d*.4572
ma=world((202.4,185));md=world((223.4,220.5))-ma;md/=np.linalg.norm(md)
ab=[world(q) for q in [(223.32,219.98),(226.5,218.64),(228.7,221.82),(225.34,223.48)]]
start=ma+md*np.dot(ps-ma,d)/np.dot(md,d);u=ab[1]-ab[0];n=np.array([-u[1],u[0]])
end=ma+md*np.dot(ab[0]-ma,n)/np.dot(md,n)
blue='#004fc4';red='#bf0028'
for q,r,c in [(a,pn,blue),(start,end,red)]:draw.line([pixel(source(q)),pixel(source(r))],fill=c,width=3)
point(source(a),'N1: north inner stone face',blue)
point(source(pn),'N2: pier2 north long face',blue,(-250,20))
point(source(start),'Old C locator: pier2 south face',red,(-110,-40))
point(source(end),'Old locator misses finite AB',red,(-310,15))
center=(ab[0]+ab[1])/2;central_start=center-md*np.dot(center-ps,d)/np.dot(md,d)
green='#007744'
draw.line([pixel(source(central_start)),pixel(source(center))],fill=green,width=2)
point(source(center),'AB center station',green,(25,40))
for i,q in enumerate(ab):point(source(q),'ABCD'[i],red,(9,-16))
draw.line([pixel(source(q)) for q in ab+[ab[0]]],fill=red,width=2)
draw.text((12,12),'Guest01 original source: endpoint identity / candidate registration',font=large,fill='black')
draw.text((12,49),'2010 HABS PA-5346-A; source image is unchanged beneath diagnostic lines',font=font,fill='black')
x=crop.width+16;y=120
lines=['NORTH whole framed opening','Printed 8 ft 1 7/8 in = 2.486025 m','N1 / N2: opposing stone faces.','Candidate anchors N2 from N1','using the independently printed span.','','MIDDLE whole framed opening','Printed 7 ft 1 1/8 in = 2.162175 m','M1: pier2 south long face.','M2: short unhatched AB return.','AB is NOT the bay span and is','NOT pier1 north long stone face.','','Red: old C locator misses finite AB.','Extended plane only: %.6f m'%np.linalg.norm(end-start),'Green: parallel station on finite AB.','Faces are not exactly parallel.','Middle stays C diagnostic, NOT PASS.','No AB movement to fit the number.','','A: printed dimensions.','B/C: face identity on source.','C: registered XY / construction.','C/U: return material / height.','','Actual mesh rays are separate.','Numeric agreement is not approval.','Prior middle NOT_RUN is retained.']
for line in lines:draw.text((x,y),line,font=font,fill='black');y+=30
path=R/'qa/guest-bays11-source-endpoints-final.png';out.save(path)
(R/'qa/guest-bays11-source-endpoints-final.json').write_text(json.dumps({'source_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'source_native_crop':native,'normalized_crop':box,'north_source':[source(a),source(pn)],'middle_source':[source(start),source(end)],'ABCD':[source(q) for q in ab],'middle_prediction_m':float(np.linalg.norm(end-start)),'view_status':'CREATED_PENDING_ACTUAL_OPEN'},indent=2))
