"""Source-only, singlefacade annotation; no projection or model mutation."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
Image.MAX_IMAGE_PIXELS=300000000
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
src=ROOT/'data/guest_refs/guest-01-original.tif';im=Image.open(src);scale=im.width/1024
# Source registration manually read on originalnative drawing and its normalized
# grid, before reading numeric model deviations. Uncertainty is0.25normalizedpx.
stations=[('J_W',329.80,'west90deg glass return/corner','W0','B corner candidate'),
 ('P1',342.20,'large round principalpost with cross/jamb detail','W1','B alternating principalpost'),
 ('M1',356.80,'small secondary mullion symbol','W2','B alternating secondarymullion'),
 ('P2',371.35,'large round principalpost with cross/jamb detail','W3','B alternating principalpost'),
 ('M2',385.90,'small secondary mullion symbol','W4','B alternating secondarymullion'),
 ('P3',400.35,'large round principalpost with cross/jamb detail','W5','B alternating principalpost'),
 ('M3',414.90,'small secondary mullion symbol','W6','B alternating secondarymullion'),
 ('P4',429.45,'large round principalpost with cross/jamb detail','W7','B alternating principalpost'),
 ('J_E',440.90,'east90deg return into adjacent entrywall','E_RETURN','B planreturn; U exactA10pixel contour')]
window_y=444.35
points=[]
for name,x,identity,photo,confidence in stations:
    y=window_y;wx=3.4+(x-325)*.05256;wy=37.1+(422-y)*.05272
    points.append({'source_id':name,'normalized_plan_xy':[x,y],'original_plan_pixel_xy':[x*scale,y*scale],
        'plan_tracing_uncertainty_normalized_px':.25,'world_plan_xy_m':[wx,wy],'plan_identity':identity,
        'photo_column_candidate':photo,'confidence':confidence,'dimensions_status':'Traced B/C coordinates; no newprinted dimension anchor'})
record={'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source_size_px':list(im.size),
 'normalization':'nativeX/nativewidth*1024; nativeY divided by sameXscale; no rotate; normalizedheight789.866approximately',
 'native_pixels_per_normalized_pixel':scale,'world_transform':{'origin_normalized_px':[325,422],'origin_world_m':[3.4,37.1],'meters_per_px':[.05256,.05272],'Y_direction':'reversed'},
 'source_date':'2010 HABS guest01; not1985 photo','points':points,
 'counting':'Seven intermediate verticalsymbols =four principalposts plus three secondarymullions; with westcornerthisgives eightA10candidateverticals. Eastterminalreturnis a ninthplanstation, not anotherfree-standingpost. Betweenbothreturns eightglazingintervals; oldmodelhas7equalintervals/eightgenericposts.',
 'facade_scope':'GuestLounge southfront only; westernreturn endpoint and easternglass terminationare boundarycontrols, not wholeadjacentwall edits',
 'historical_caveat':'Alternatingprincipal/secondary sequence also visibleA10but precise1985to2010coordinateequality notproved. Neverinferrenovationfromdatesalone.'}
(ROOT/'qa/guest-window12-source-registration-sources.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
rect=(323,430,449,453);fac=14
crop=im.crop(tuple(round(v*scale) for v in rect)).convert('RGB').resize((int((rect[2]-rect[0])*fac),int((rect[3]-rect[1])*fac)))
d=ImageDraw.Draw(crop)
for p in points:
    x,y=p['normalized_plan_xy'];x=(x-rect[0])*fac;y=(y-rect[1])*fac
    d.ellipse((x-5,y-5,x+5,y+5),outline='red',width=2);d.text((x-15,y+12),p['source_id'],font=font,fill='red',stroke_width=1,stroke_fill='white')
can=Image.new('RGB',(crop.width,crop.height+44),'white');can.paste(crop,(0,44));ImageDraw.Draw(can).text((8,6),'2010 guest01 actual symbols | J=return, P=principalpost, M=secondarymullion | no modeledwindow overlay',font=font,fill='black');can.save(ROOT/'qa/guest-window12-source-registration-source-posts.png')
photo=Image.open(ROOT/'data/photo_refs/guest_exterior_10.jpg').convert('RGB')
photo.crop((10,55,205,490)).resize((585,1305)).save(ROOT/'qa/guest-window12-source-registration-photo-west-corner.png')
draw=ImageDraw.Draw(photo)
photo_centers=[(87,150),(174,250),(245,320),(298,378),(336,413),(365,445),(388,464),(407,489)]
for p,(x,y) in zip(points,photo_centers):
    draw.ellipse((x-4,y-4,x+4,y+4),outline='cyan',width=2)
    draw.text((x+5,y),p['photo_column_candidate']+' /'+p['source_id'],font=font,fill='cyan',stroke_width=1,stroke_fill='black')
can=Image.new('RGB',(1042,1064),'white');can.paste(photo,(0,40));d=ImageDraw.Draw(can)
d.text((10,6),'1985 A10 | eightvisiblecolumns: corner +4principal +3secondary | identitycandidate, no newfit',font=font,fill='black')
for i,p in enumerate(points):d.multiline_text((755,100+i*90),'%s -> %s\nplanx %.2f'%(p['photo_column_candidate'],p['source_id'],p['normalized_plan_xy'][0]),font=font,fill='black',spacing=5)
can.save(ROOT/'qa/guest-window12-source-registration-photo-columns.png')
print(json.dumps({'source_stations':len(points),'free_posts':7,'corner_and_free_photo_candidates':8,'glazing_intervals':8,'sources_sha256':hashlib.sha256((ROOT/'qa/guest-window12-source-registration-sources.json').read_bytes()).hexdigest()},indent=2))
