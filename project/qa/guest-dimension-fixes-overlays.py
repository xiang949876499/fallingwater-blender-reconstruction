from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,math,hashlib
Image.MAX_IMAGE_PIXELS=None
p=Path('D:/zx/test/project');q=p/'qa'
r=json.loads((q/'guest-dimension-fixes-measured.json').read_text(encoding='utf-8'));e=json.loads((q/'guest-dimension-fixes-projection.json').read_text(encoding='utf-8'))
reg=r['coordinate_registration'];sx,sy=reg['meters_per_pixel'];ox,oy=reg['origin_px'];wx,wy,gz=reg['world_origin'];fz=r['floor_datum_actual']['coordinate_m']
font='C:/Windows/Fonts/arial.ttf'
def f(n):return ImageFont.truetype(font,n)
meta=[]
def make(kind,source,crop,scale,title,subtitle,mapping,formula,scope,notes):
 src=p/'data/guest_refs'/source
 im=Image.open(src).convert('L');w,h=im.size;srcbox=(crop[0]*w/1024,crop[1]*h/790,crop[2]*w/1024,crop[3]*h/790)
 outsz=(round((crop[2]-crop[0])*scale),round((crop[3]-crop[1])*scale))
 bg=im.resize(outsz,Image.Resampling.LANCZOS,box=srcbox).point(lambda v:125+int(v*.51)).convert('RGB')
 layer=Image.new('RGBA',outsz,(0,0,0,0));dr=ImageDraw.Draw(layer);seen=set();count=0
 def xy(v):
  a,b=mapping(v);return ((a-crop[0])*scale,(b-crop[1])*scale)
 for ob in e[kind]:
  for va,vb in ob['edges_world']:
   a,b=xy(va),xy(vb)
   if (a[0]<0 and b[0]<0)or(a[1]<0 and b[1]<0)or(a[0]>outsz[0] and b[0]>outsz[0])or(a[1]>outsz[1] and b[1]>outsz[1]):continue
   if math.dist(a,b)<.6:continue
   k=tuple(sorted((tuple(round(x,1) for x in a),tuple(round(x,1) for x in b))))
   if k in seen:continue
   seen.add(k);dr.line((a,b),fill=(215,39,39,150),width=1);count+=1
 # Diagnostic measured segments are separate cyan lines; do not replace structural projection.
 if kind=='plan':
  for key in ['GUEST_POOL_LENGTH','GUEST_POOL_WIDTH','GUEST_BOILER_DIM_1','GUEST_BOILER_DIM_2','GUEST_GUEST_ROOM_LENGTH','GUEST_GUEST_ROOM_DEPTH']:
   rec=next(t for t in r['measurements'] if t['id']==key);a,b=[xy(x['point_m']) for x in rec['endpoints']]
   dr.line((a,b),fill=(0,100,190,255),width=3)
   for v in [a,b]:dr.ellipse((v[0]-5,v[1]-5,v[0]+5,v[1]+5),fill=(0,100,190,255))
 else:
  # Reference level and observed top are both drawn in the margin left of the pointed terrace.
  rec=next(t for t in r['measurements'] if t['id']=='GUEST_TOP_STONE');topz=rec['endpoints'][1]['point_m'][2]
  ay=mapping([wx,wy,topz])[1];ry=mapping([wx,wy,fz+rec['reference_m']])[1]
  x=(235-crop[0])*scale;y1=(ay-crop[1])*scale;y2=(ry-crop[1])*scale
  dr.line(((x,y1),(x,y2)),fill=(0,100,190,255),width=4)
  for yy in [y1,y2]:dr.line(((x-9,yy),(x+9,yy)),fill=(0,100,190,255),width=3)
 bg=Image.alpha_composite(bg.convert('RGBA'),layer).convert('RGB')
 header=128;footer=212 if kind=='plan' else 242
 out=Image.new('RGB',(outsz[0],outsz[1]+header+footer),'white');out.paste(bg,(0,header));dout=ImageDraw.Draw(out)
 dout.text((24,16),title,font=f(32),fill='#1a2632');dout.text((24,61),subtitle,font=f(22),fill='#435463')
 dout.line((24,103,86,103),fill='#d72727',width=3);dout.text((96,87),'Actual evaluated mesh edges',font=f(21),fill='#333333')
 dout.line((482,103,544,103),fill='#7d7d7d',width=2);dout.text((554,87),'Original HABS drawing',font=f(21),fill='#333333')
 dout.line((892,103,954,103),fill='#0064be',width=4);dout.text((964,87),'Measured segment / level difference',font=f(21),fill='#333333')
 y=outsz[1]+header+17
 for line in [formula,scope]+notes+[f'Blender 5.2.1 | corrected guest module | SHA256 {r["source_scene_sha256"][:24]}... | {len(e[kind])} objects / {count} unique projected edges']:
  dout.text((24,y),line,font=f(20),fill='#303d48');y+=33
 path=q/f'guest-dimension-fixes-{kind}-overlay.png';out.save(path)
 meta.append({'kind':kind,'path':str(path),'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'normalized_source_size':[1024,790],'source_crop_normalized_px':crop,'output_scale':scale,'mapping':formula,'scope':scope,'notes':notes,'objects':[o['object'] for o in e[kind]],'edge_count_after_2d_deduplication':count,'hidden_line_removal':False,'mesh_projection_sha256':hashlib.sha256((q/'guest-dimension-fixes-projection.json').read_bytes()).hexdigest(),'view_status':'PENDING_VISUAL_REVIEW'})
make('plan','guest-01-upright.png',[155,65,947,548],3,'GUEST HOUSE | FIRST FLOOR: ORIGINAL + ACTUAL MESH','Independent geometry audit - exact mesh projection; no per-object fitting',lambda v:(ox+(v[0]-wx)/sx,oy-(v[1]-wy)/sy),'Mapping: px = 325 + (X - 3.4) / 0.05256; py = 422 - (Y - 37.1) / 0.05272. Units: m.', 'Scope: L1 floors, walls and windows; pool shell/coping; service and laundry stair meshes.', ['X-ray projection: roofs, L2, basement enclosure, furnishings and ashlar courses excluded.','Registration from guest sheet 1; tracing uncertainty ~1 px (53 mm). Blue lines are real face-to-face ray hits.'])
esx=20.177125/(606.0-221.5);esz=2.352675/(243.0-199.0)
make('west','guest-04-upright.png',[205,127,856,305],3.5,'GUEST HOUSE | WEST ELEVATION: ORIGINAL + ACTUAL MESH','Corrected service enclosure: actual 4.511676 m; printed top of stone wall 4.511675 m',lambda v:(577-(v[1]-wy)/esx,243-(v[2]-fz)/esz),f'Mapping: px = 577 - (Y - 37.1) / {esx:.9f}; py = 243 - (Z - {fz:.7f}) / {esz:.9f}.', 'Scope: west/service envelope, upper terrace walls, selected slabs/roofs and connector canopy.', ['Independent scale: horizontal 66 ft 2 3/8 in across 384.5 px; vertical 7 ft 8 5/8 in across 44 px.','Anchor: service SE corner at px 577 (+/-2 px); guest datum at py 243. Scale witnesses +/-1 px.','X-ray projection with no occlusion removal; no object moved to force agreement. Original top datum now matches the corrected wall top; no vertical rescaling.'])
r['overlays']=meta
(q/'guest-dimension-fixes-measured.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([{'path':m['path'],'objects':len(m['objects']),'edges':m['edge_count_after_2d_deduplication']} for m in meta]))
