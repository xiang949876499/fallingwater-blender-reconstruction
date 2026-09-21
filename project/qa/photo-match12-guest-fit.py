"""One locked, non-robust7-parameter diagnostic; never imports Blender or edits mesh."""
from pathlib import Path
import json,hashlib,math
import cv2,numpy as np
from scipy.optimize import least_squares
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'data/photo-match-points12-guest-exterior.json'
lock=json.loads((ROOT/'qa/photo-match12-guest-observation-lock.json').read_text(encoding='utf-8'))
assert hashlib.sha256(path.read_bytes()).hexdigest()==lock['sha256']
outfile=ROOT/'qa/photo-match12-guest-fit.json'
assert not outfile.exists(),'Only one fitting run for this locked interpretation'
data=json.loads(path.read_text(encoding='utf-8'));mesh=json.loads((ROOT/'qa/photo-match12-guest-mesh.json').read_text(encoding='utf-8'))
ps=data['points'];xyz=np.array([p['world_m'] for p in ps]);uv=np.array([p['pixel'] for p in ps],float)
fit=np.array([p['role']=='fit' for p in ps]);config=data['fit_contract'];eye=np.array(config['seed_eye'])
forward=np.array(config['seed_target'])-eye;forward/=np.linalg.norm(forward)
right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right);down=np.cross(forward,right)
rvec=cv2.Rodrigues(np.array([right,down,forward]))[0].ravel();principal=np.array([371.,512.])
def project(x,v):
    R=cv2.Rodrigues(x[:3])[0];q=(np.array(v)-x[3:6])@R.T
    return q[:,:2]/np.maximum(q[:,2:],.01)*math.exp(x[6])+principal,q[:,2]
x0=np.r_[rvec,eye,math.log(config['seed_focal_px'])]
res=least_squares(lambda x:(project(x,xyz[fit])[0]-uv[fit]).ravel(),x0,loss='linear',max_nfev=2000,
    bounds=(np.r_[[-np.inf]*3,config['eye_bounds'][0],math.log(config['focal_bounds_px'][0])],
            np.r_[[np.inf]*3,config['eye_bounds'][1],math.log(config['focal_bounds_px'][1])]))
x=res.x;pred,depth=project(x,xyz);error=np.linalg.norm(pred-uv,axis=1);diag=math.hypot(742,1024)
R=cv2.Rodrigues(x[:3])[0]
rows=[dict(p,projection_px=q.tolist(),depth_m=float(z),residual_px=float(e),residual_pct_diagonal=float(e/diag*100)) for p,q,z,e in zip(ps,pred,depth,error)]
result={'status':'UNVERIFIED_DIAGNOSTIC_NOT_GEO07_PASS','source':data['source'],'source_sha256':data['source_sha256'],
 'source_date':'1985 February/March caption batch; drawings2010, no inferred date equivalence',
 'scene':data['scene'],'scene_sha256':data['scene_sha256'],'locked_points_sha256':lock['sha256'],
 'optimization':{'runs':1,'function_evaluations':res.nfev,'success':bool(res.success),'message':res.message,
    'objective':'unweighted squared pixel errors on fixed8fitpoints; holdouts never included; no outlier deletion'},
 'camera':{'eye_m':x[3:6].tolist(),'world_to_opencv':R.tolist(),'blender_rotation_world':(R.T@np.diag([1,-1,-1])).tolist(),
    'focal_px':math.exp(x[6]),'lens_mm_36mm_long_edge':math.exp(x[6])*36/1024,'lens_mm_36mm_width':math.exp(x[6])*36/742,
    'principal_point_px':principal.tolist(),'resolution_px':[742,1024],'up_world':(-R[1]).tolist(),'forward_world':R[2].tolist(),
    'distortion':'not fitted; original lens/camera calibration unknown','production_camera_created':False},
 'coverage':{'fit':int(fit.sum()),'holdout':int((~fit).sum()),'fit_world_rank':int(np.linalg.matrix_rank(xyz[fit]-xyz[fit].mean(axis=0),tol=.002)),
    'world_span_m':np.ptp(xyz,axis=0).tolist(),'observed_hull_pct':cv2.contourArea(cv2.convexHull(uv.astype(np.float32)))/(742*1024)*100,
    'behind_camera':int((depth<=0).sum())},
 'statistics':{'fit_median_px':float(np.median(error[fit])),'fit_max_px':float(error[fit].max()),
    'holdout_median_px':float(np.median(error[~fit])),'holdout_max_px':float(error[~fit].max()),
    'all_median_px':float(np.median(error)),'all_max_px':float(error.max()),'one_percent_diagonal_px':diag*.01},'points':rows,
 'scope':'Fixed mesh; no image warp/crop, no rendered image, no scene or productioncamera save; numericalfit not independent historical verification.'}
outfile.write_text(json.dumps(result,indent=2),encoding='utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
im=Image.open(data['source']).convert('RGB');draw=ImageDraw.Draw(im)
for p in rows:
    a=p['pixel'];q=p['projection_px'];col='cyan' if p['role']=='fit' else 'orange'
    draw.line([tuple(a),tuple(q)],fill=(255,40,40),width=2)
    draw.ellipse((a[0]-4,a[1]-4,a[0]+4,a[1]+4),outline=col,width=2)
    draw.rectangle((q[0]-3,q[1]-3,q[0]+3,q[1]+3),outline='red',width=2)
    draw.text((a[0]+4,a[1]+5),p['id'],font=font,fill=col,stroke_width=1,stroke_fill='black')
def with_header(image,text):
    canvas=Image.new('RGB',(742,1064),'white');canvas.paste(image,(0,40));d=ImageDraw.Draw(canvas);d.text((8,5),text,font=font,fill='black');return canvas
with_header(im,'QA ONLY |1985 A10 |12a fixed | cyan fit / orange holdout / red projected').save(ROOT/'qa/photo-match12-guest-points-overlay.png')
segments=[]
def edge(name,a,b,kind):
    ob=mesh['objects'][name];vs=ob['world_vertices'];segments.append({'object':name,'vertices':[a,b],'world_m':[vs[a],vs[b]],'kind':kind})
roof='GUEST_LOW_ARM_ROOF'
for a,b in [(0,1),(1,2),(2,3)]:edge(roof,a,b,'roof outer continuous soffit boundary')
ob=mesh['objects'][roof]
# Actual lower opening perimeters only; no arbitrary fitted geometry.
for e in ob['edges']:
    a,b=e
    if a>=20 and b>=20 and abs(ob['world_vertices'][a][2]-10.56)<.001 and abs(ob['world_vertices'][b][2]-10.56)<.001:
        edge(roof,a,b,'roof lower aperture edge')
for i in range(8):
    name='GUEST_L1_LOUNGE_FRONT_steel_window_0_mullion_%d'%i
    edge(name,0,4,'window post west outer edge');edge(name,1,5,'window post east outer edge')
for n,o in mesh['objects'].items():
    if n.startswith(('GUEST_C10_W1_FRONT','GUEST_C10_W2_FRONT')) and '_TREAD_' in n:
        for a,b in [(4,7),(4,5),(5,6)]:edge(n,a,b,'stair going edge C geometry; individual nosing not independently matched')
    if n.startswith('GUEST_L1_LOUNGE_FRONT_steel_window_0_') and any(s in n for s in ['sill','head']):
        for a,b in o['edges']:edge(n,a,b,'window horizontal frame')
im=Image.open(data['source']).convert('RGB');draw=ImageDraw.Draw(im)
for seg in segments:
    q,z=project(x,seg['world_m']);seg['projection_px']=q.tolist();seg['depths_m']=z.tolist()
    if min(z)<=0:continue
    color=(255,35,35) if seg['kind'].startswith('roof') else ((255,170,0) if seg['kind'].startswith('stair') else (0,190,230))
    if np.isfinite(q).all() and np.max(np.abs(q))<1e6:draw.line([tuple(v) for v in q],fill=color,width=1)
with_header(im,'QA x-ray edges |red roof /cyan windows /orange stairs |no render').save(ROOT/'qa/photo-match12-guest-continuous-edges.png')
(ROOT/'qa/photo-match12-guest-projected-edges.json').write_text(json.dumps({'camera_locked_to':str(outfile),'segments':segments,'visibility':'x-ray projection; independent actual occlusion check follows'},indent=2),encoding='utf-8')
print(json.dumps({k:result[k] for k in ['camera','coverage','statistics']},indent=2))
