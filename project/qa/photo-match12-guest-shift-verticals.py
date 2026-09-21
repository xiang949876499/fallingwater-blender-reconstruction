"""Independent photo-only vertical direction observations, before alternative fit."""
from pathlib import Path
import json,hashlib,math
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'qa/photo-match12-guest-shift-verticals.json'
assert not out.exists(),'Do not change traces after camera fit'
source=ROOT/'data/photo_refs/guest_exterior_10.jpg'
im=np.array(Image.open(source).convert('L'),float)
dx=cv2.Sobel(cv2.GaussianBlur(im,(3,3),.6),cv2.CV_64F,1,0,ksize=3)
# Six fixed facade post-edge strips, excluding heads/sills/old point endpoints.
# Intersections are excluded by contiguousROI choice before camera optimization;
# every row in eachROI is retained, no residual-based trace filtering.
rois=[('V2',(248,255,278,486)),('V3',(298,305,337,510)),('V4',(335,342,375,523)),
      ('V5',(364,371,407,535)),('V6',(388,395,430,546)),('V7',(406,414,447,552))]
rows=[]
for name,(x0,x1,y0,y1) in rois:
    pts=[]
    for y in range(y0,y1+1):
        values=np.abs(dx[y]);k=x0+int(np.argmax(values[x0:x1+1]))
        # Quadratic local derivative peak, bounded within one halfpixel.
        a,b,c=values[k-1:k+2];den=a-2*b+c
        frac=float(np.clip(.5*(a-c)/den,-.5,.5)) if abs(den)>1e-10 else 0
        pts.append((k+frac,y))
    p=np.array(pts);slope,intercept=np.polyfit(p[:,1],p[:,0],1);res=p[:,0]-slope*p[:,1]-intercept
    rows.append({'id':name,'roi_xyxy':[x0,y0,x1,y1],'points_xy':p.tolist(),
        'slope_dx_dy':float(slope),'angle_from_vertical_degrees':math.degrees(math.atan(slope)),
        'intercept_x':float(intercept),'line_rms_px':float(np.sqrt(np.mean(res**2))),
        'max_deviation_px':float(max(abs(res))),'rows_retained':len(p),'pixel_uncertainty_px':1.5,
        'role':'photo-only orientation measurement; not used as new3D correspondence or to change old points'})
slopes=np.array([r['slope_dx_dy'] for r in rows]);roll=math.atan(float(np.median(slopes)))
record={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'method':'absolute horizontalSobelpeak in preselected contiguouspost-edge strips; subpixel quadratic; unweighted all-row linear regression',
  'traces':rows,'roll_fixed_radians':roll,'roll_fixed_degrees':math.degrees(roll),'pitch_fixed_degrees':0,
  'pitch_basis':'Parallel/near-vertical architectural edge hypothesis, bounded alternative to upward11.52deg fixedprincipal model. Exact0deg is C camera model assumption, not historical measurement.',
  'vertical_principal_point_evidence':'U. Image geometry permits testing vertical opticalcenter offset; cannot distinguish architectural lensshift, camera back movement or unknownscan origin.',
  'vertical_span_px':[min(r['roi_xyxy'][1] for r in rows),max(r['roi_xyxy'][3] for r in rows)],
  'lens_fit_not_run_yet':True,'source_point_set_unchanged':True,
  'second_fit_contract':{'parameters':['yaw','eyeX','eyeY','eyeZ','logFocal','cy'],'cx_fixed':371,
    'pitch_fixed_degrees':0,'roll_fixed_radians':roll,'eye_bounds':[[0,32,7],[4,36,10.2]],
    'focal_bounds_px':[222.6,2226],'cy_bounds_px':[0,1024],'distortion':'none','point_roles':'same8fit/7holdout; no resampling or replacement'},
  'historical_camera_status':'UNVERIFIED'}
out.write_text(json.dumps(record,indent=2),encoding='utf-8')
canvas=Image.open(source).convert('RGB');d=ImageDraw.Draw(canvas);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13)
colors=['cyan','yellow','lime','orange','magenta','red']
for row,c in zip(rows,colors):
    pts=row['points_xy'];d.line([tuple(q) for q in pts],fill=c,width=1)
    x0,y0,x1,y1=row['roi_xyxy'];d.rectangle((x0,y0,x1,y1),outline=c,width=1)
    x=row['intercept_x']+row['slope_dx_dy']*y0;d.text((x+8,y0),row['id'],font=font,fill=c,stroke_width=1,stroke_fill='black')
wide=Image.new('RGB',(1100,1064),'white');wide.paste(canvas,(0,40));dd=ImageDraw.Draw(wide);dd.text((8,5),'A10 photo-only vertical traces BEFORE alternative fit; every row retained',font=font,fill='black')
for i,row in enumerate(rows):
    dd.multiline_text((755,90+i*116),'%s\nangle %.5f deg\nline RMS %.4f px\n%d retained rows'%(row['id'],row['angle_from_vertical_degrees'],row['line_rms_px'],row['rows_retained']),fill='black',font=font,spacing=5)
dd.multiline_text((755,850),'Fixed roll median %.5f deg\nPitch hypothesis exactly0 deg\nOnlycy will vary; cx stays371\nPhoto camera mechanism unknown'%math.degrees(roll),font=font,fill='black',spacing=5)
wide.save(ROOT/'qa/photo-match12-guest-shift-verticals-observed.png')
print(json.dumps({'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'roll_deg':math.degrees(roll),'traces':[{k:v for k,v in r.items() if k!='points_xy'} for r in rows]},indent=2))
