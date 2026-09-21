"""Second and final camera hypothesis: source-fixed pitch/roll, free vertical principalpoint."""
from pathlib import Path
import json,hashlib,math
import cv2,numpy as np
from scipy.optimize import least_squares
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
obsfile=ROOT/'data/photo-match-points12-guest-exterior.json'
vfile=ROOT/'qa/photo-match12-guest-shift-verticals.json'
outfile=ROOT/'qa/photo-match12-guest-shift-fit.json'
assert not outfile.exists(),'No additional alternative fitting runs'
obs=json.loads(obsfile.read_text(encoding='utf-8'));vertical=json.loads(vfile.read_text(encoding='utf-8'))
old=json.loads((ROOT/'qa/photo-match12-guest-fit.json').read_text(encoding='utf-8'))
assert hashlib.sha256(obsfile.read_bytes()).hexdigest()==old['locked_points_sha256']
contract=vertical['second_fit_contract'];roll=contract['roll_fixed_radians']
ps=obs['points'];xyz=np.array([p['world_m'] for p in ps]);uv=np.array([p['pixel'] for p in ps],float);train=np.array([p['role']=='fit' for p in ps])
def matrix(yaw):
    forward=np.array([math.cos(yaw),math.sin(yaw),0.]);right=np.array([math.sin(yaw),-math.cos(yaw),0.]);down=np.array([0.,0.,-1.])
    return np.array([right*math.cos(roll)+down*math.sin(roll),-right*math.sin(roll)+down*math.cos(roll),forward])
def project(x,pts):
    R=matrix(x[0]);q=(np.array(pts)-x[1:4])@R.T;f=math.exp(x[4]);return q[:,:2]/np.maximum(q[:,2:],.01)*f+np.array([371.,x[5]]),q[:,2]
yaw=math.atan2(old['camera']['forward_world'][1],old['camera']['forward_world'][0])
x0=np.r_[yaw,old['camera']['eye_m'],math.log(old['camera']['focal_px']),638.]
low=np.r_[-math.pi/2,contract['eye_bounds'][0],math.log(contract['focal_bounds_px'][0]),contract['cy_bounds_px'][0]]
high=np.r_[math.pi/2,contract['eye_bounds'][1],math.log(contract['focal_bounds_px'][1]),contract['cy_bounds_px'][1]]
fit=least_squares(lambda x:(project(x,xyz[train])[0]-uv[train]).ravel(),x0,bounds=(low,high),loss='linear',max_nfev=2000)
x=fit.x;R=matrix(x[0]);q,depth=project(x,xyz);errors=np.linalg.norm(q-uv,axis=1);diag=math.hypot(742,1024)
rows=[dict(p,projection_px=pj.tolist(),depth_m=float(z),residual_px=float(e),residual_pct_diagonal=float(e/diag*100)) for p,pj,z,e in zip(ps,q,depth,errors)]
linechecks=[]
for row in vertical['traces']:
    pts=np.array(row['points_xy']);m=math.tan(roll);b=float(np.mean(pts[:,0]-m*pts[:,1]));distance=(pts[:,0]-m*pts[:,1]-b)/math.sqrt(1+m*m)
    linechecks.append({'id':row['id'],'measured_angle_degrees':row['angle_from_vertical_degrees'],'camera_vertical_angle_degrees':math.degrees(roll),
        'angle_residual_degrees':row['angle_from_vertical_degrees']-math.degrees(roll),
        'camera_parallel_direction_rms_px':float(np.sqrt(np.mean(distance**2))),'rms_about_own_line_px':row['line_rms_px'],
        'max_parallel_distance_px':float(max(abs(distance))),'n':len(pts),
        'qualification':'All originaltrace rows retained. V5 trace has5.8pxdeviation; edge-selection ambiguity remains, not a precise camera calibration.'})
result={'status':'UNVERIFIED_ALTERNATIVE_DIAGNOSTIC_NOT_GEO07_PASS','hypothesis':'Exacthorizontalopticalaxis, sourcephoto medianverticalroll fixed, cx371fixed, cyfree; physical mechanismU',
 'source':obs['source'],'source_sha256':obs['source_sha256'],'scene':obs['scene'],'scene_sha256':obs['scene_sha256'],
 'locked_points_sha256':old['locked_points_sha256'],'vertical_measurement_sha256':hashlib.sha256(vfile.read_bytes()).hexdigest(),
 'prior_hypothesis_preserved':'photo-match12-guest-fit.json','camera':{'eye_m':x[1:4].tolist(),'world_to_opencv':R.tolist(),
    'blender_rotation_world':(R.T@np.diag([1,-1,-1])).tolist(),'forward_world':R[2].tolist(),'up_world':(-R[1]).tolist(),
    'yaw_degrees':math.degrees(x[0]),'pitch_degrees':0,'roll_degrees':math.degrees(roll),
    'focal_px':math.exp(x[4]),'lens_mm_36mm_long_edge':math.exp(x[4])*36/1024,'lens_mm_36mm_width':math.exp(x[4])*36/742,
    'principal_point_px':[371.,x[5]],'cy_offset_px_from_scan_center':x[5]-512,'cy_offset_fraction_image_height':(x[5]-512)/1024,
    'resolution_px':[742,1024],'distortion':'none','production_camera_created':False},
 'fit':{'free_parameters':6,'optimized':['yaw','eyeX','eyeY','eyeZ','logFocal','cy'],'rotation_source_fixed':['pitch=0','roll=photo median'],
    'runs_this_hypothesis':1,'all_hypotheses_now':2,'nfev':fit.nfev,'success':bool(fit.success),'message':fit.message,
    'fit_count':old['coverage']['fit'],'holdout_count':old['coverage']['holdout'],'point_roles_unchanged':True,'no_more_camera_trials':True,
    'cy_bounds_px':contract['cy_bounds_px'],'objective':'unweighted fixed8point squaredpixelerror, same7holdoutsneverfit; noindependenttracepoint usedas3Dpoint'},
 'statistics':{'fit_median_px':float(np.median(errors[train])),'fit_max_px':float(errors[train].max()),
    'holdout_median_px':float(np.median(errors[~train])),'holdout_max_px':float(errors[~train].max()),
    'all_median_px':float(np.median(errors)),'all_max_px':float(errors.max()),'behind_camera':int((depth<=0).sum())},
 'points':rows,'independent_vertical_line_checks':linechecks,
 'limitations':['Original same windowpoint occlusion and2010plan registration unresolved.','Photo-onlysixstripgradienttrace is not a calibrated camera; V5ambiguousedge retained.','Verticalprincipaloffset allowed does not prove lensshift or scanning origin.','CannotGEO07PASSfromlowmedian; no modelgeometry adjusted.']}
outfile.write_text(json.dumps(result,indent=2),encoding='utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13)
def header(im,txt):
    c=Image.new('RGB',(742,1064),'white');c.paste(im,(0,40));ImageDraw.Draw(c).text((8,5),txt,font=font,fill='black');return c
im=Image.open(obs['source']).convert('RGB');d=ImageDraw.Draw(im)
for p in rows:
    a,b=p['pixel'],p['projection_px'];color='cyan' if p['role']=='fit' else 'orange'
    d.line([tuple(a),tuple(b)],fill='red',width=2);d.ellipse((a[0]-4,a[1]-4,a[0]+4,a[1]+4),outline=color,width=2)
    d.rectangle((b[0]-3,b[1]-3,b[0]+3,b[1]+3),outline='red',width=2);d.text((a[0]+5,a[1]+5),p['id'],font=font,fill=color,stroke_width=1,stroke_fill='black')
header(im,'QA alt2 |same15points |pitch0 /source-fixedroll /freecy |notPASS').save(ROOT/'qa/photo-match12-guest-shift-points-overlay.png')
segdoc=json.loads((ROOT/'qa/photo-match12-guest-projected-edges.json').read_text(encoding='utf-8'))
im=Image.open(obs['source']).convert('RGB');d=ImageDraw.Draw(im)
for seg in segdoc['segments']:
    p,z=project(x,seg['world_m']);seg['projection_px']=p.tolist();seg['depths_m']=z.tolist()
    if min(z)<=0:continue
    c=(255,35,35) if seg['kind'].startswith('roof') else ((255,170,0) if seg['kind'].startswith('stair') else (0,190,230))
    if np.isfinite(p).all() and max(abs(p).ravel())<1e6:d.line([tuple(v) for v in p],fill=c,width=1)
segdoc['camera_locked_to']=str(outfile);segdoc['visibility']='xraycontinuousedgediagnostic; noalteredscene'
(ROOT/'qa/photo-match12-guest-shift-projected-edges.json').write_text(json.dumps(segdoc,indent=2),encoding='utf-8')
header(im,'QA alt2 actualedges |red roof /cyan windows /orange stairs |no render').save(ROOT/'qa/photo-match12-guest-shift-continuous-edges.png')
print(json.dumps({k:result[k] for k in ['camera','statistics','independent_vertical_line_checks']},indent=2))
