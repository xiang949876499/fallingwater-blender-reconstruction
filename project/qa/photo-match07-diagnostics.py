"""Two predeclared identity diagnostics only; never production camera or GEO-07 PASS."""
from pathlib import Path
import json, hashlib, math
import numpy as np
import cv2
from scipy.optimize import least_squares
from PIL import Image, ImageDraw

R=Path(__file__).resolve().parents[1]
points_path=R/'data/photo-match-points-iteration07-main87-candidate.json'
mesh=json.loads((R/'qa/photo-match07-mesh.json').read_text())
objects={o['name']:o for o in mesh['objects']}
audit=json.loads(points_path.read_text(encoding='utf-8'))
im=Image.open(R/'data/photo_refs/main_sw_87.jpg').convert('RGB')
W,H=im.size
families=[('L1W','MAIN_L1_west_parapet_','#ff6666'),('L1E','MAIN_L1_east_parapet_','#ffbb33'),('L1F','MAIN_L1_south_fascia','#bb6633'),('L2S','MAIN_L2_south_parapet_','#44ffff'),('L3','MAIN_L3_terrace_parapet_','#dd66ff'),('CAP','MAIN_chimney_cap','#aaff55')]
outputs=[]
for photo in audit['photos']:
    pts=photo['points'];xyz=np.array([objects[p['object']]['vertices'][p['vertex']] for p in pts]);uv=np.array([p['photo_px'] for p in pts]);train=np.array([p['role']=='fit' for p in pts])
    eye=np.array(photo['camera_seed']['eye'],float);target=np.array(photo['camera_seed']['target'],float)
    forward=(target-eye)/np.linalg.norm(target-eye);right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right);down=np.cross(forward,right)
    rvec=cv2.Rodrigues(np.array([right,down,forward]))[0].ravel()
    def projection(x,points):
        rot=cv2.Rodrigues(x[:3])[0];c=(points-x[3:6])@rot.T
        return c[:,:2]/np.maximum(c[:,2,None],.01)*np.exp(x[6])+[W/2,H/2],c[:,2]
    initial=np.r_[rvec,eye,np.log(photo['camera_seed']['focal_pixels'])]
    low=np.r_[[-np.inf]*3,[-50,-50,-12],np.log(W*.3)]
    high=np.r_[[np.inf]*3,[-5.1,-.5,1],np.log(W*3)]
    fit=least_squares(lambda x:(projection(x,xyz[train])[0]-uv[train]).ravel(),initial,bounds=(low,high),loss='linear',max_nfev=3000)
    x=fit.x;pred,depth=projection(x,xyz);error=np.linalg.norm(pred-uv,axis=1);diag=math.hypot(W,H)
    rot=cv2.Rodrigues(x[:3])[0]
    camera={'location':x[3:6].tolist(),'rotation_world_to_opencv':rot.tolist(),'focal_pixels':float(np.exp(x[6])),'principal_point':[W/2,H/2],'resolution':[W,H],'lens_mm_for_36mm_long_edge':float(np.exp(x[6])*36/max(W,H)),'vertical_forward_component':float(rot[2,2]),'blender_matrix_world_rotation':(rot.T@np.diag([1,-1,-1])).tolist()}
    rows=[dict(p,world=pos.tolist(),projection_px=q.tolist(),depth_m=float(z),residual_px=float(e),residual_percent_diagonal=float(e/diag*100)) for p,pos,q,z,e in zip(pts,xyz,pred,depth,error)]
    result={'id':photo['id'],'status':'DIAGNOSTIC_UNVERIFIED_NOT_GEO07','scene_sha256':mesh['sha256'],'points_sha256':hashlib.sha256(points_path.read_bytes()).hexdigest(),'solver_success':bool(fit.success),'nfev':fit.nfev,'cost':float(fit.cost),'fit_median_px':float(np.median(error[train])),'holdout_median_px':float(np.median(error[~train])),'fit_median_percent_diagonal':float(np.median(error[train])/diag*100),'holdout_median_percent_diagonal':float(np.median(error[~train])/diag*100),'fit_world_rank':int(np.linalg.matrix_rank(xyz[train]-xyz[train].mean(axis=0))),'points_behind_camera':int(sum(depth<=0)),'bound_hit':{'eye_x':bool(abs(x[3]-high[3])<.001 or abs(x[3]-low[3])<.001),'eye_y':bool(abs(x[4]-high[4])<.001 or abs(x[4]-low[4])<.001),'eye_z':bool(abs(x[5]-high[5])<.001 or abs(x[5]-low[5])<.001),'focal':bool(abs(x[6]-high[6])<.001 or abs(x[6]-low[6])<.001)},'camera':camera,'points':rows,'geometry_edges':[]}
    overlay=im.copy().convert('RGBA');wire=Image.new('RGBA',im.size,(0,0,0,0));d=ImageDraw.Draw(wire)
    for label,prefix,col in families:
        for name,o in objects.items():
            if not name.startswith(prefix):continue
            q,z=projection(x,np.array(o['vertices']))
            for ai,bi in o['edges']:
                if min(z[ai],z[bi])<=0:continue
                a,b=q[ai],q[bi]
                d.line([tuple(a),tuple(b)],fill=col+'aa',width=1)
                result['geometry_edges'].append({'object':name,'vertex_pair':[ai,bi],'world_a':o['vertices'][ai],'world_b':o['vertices'][bi],'projected_a':a.tolist(),'projected_b':b.tolist()})
    overlay=Image.alpha_composite(overlay,wire);d=ImageDraw.Draw(overlay)
    d.rectangle((0,0,W,64),fill='black');d.text((8,4),photo['id']+' - DIAGNOSTIC / identities unverified',fill='white')
    d.text((8,21),'All mesh edges, including hidden. Red L1W; orange L1E; cyan L2S; purple L3.',fill='white')
    d.text((8,39),f'Fit median {result["fit_median_px"]:.2f}px; frozen holdout median {result["holdout_median_px"]:.2f}px',fill='white')
    for p in rows:
        a=p['photo_px'];b=p['projection_px'];c='#66ff66' if p['role']=='fit' else '#ffff00'
        d.line([tuple(a),tuple(b)],fill='white',width=1);d.ellipse((a[0]-4,a[1]-4,a[0]+4,a[1]+4),outline=c,width=2);d.rectangle((b[0]-4,b[1]-4,b[0]+4,b[1]+4),outline=c,width=2);d.text((a[0]+5,a[1]+5),p['id'],fill=c)
    overlay.convert('RGB').save(R/f'qa/photo-match07-{photo["id"]}-edges.png')
    (R/f'qa/photo-match07-{photo["id"]}-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    outputs.append({k:result[k] for k in ('id','fit_median_px','holdout_median_px','points_behind_camera','bound_hit','camera')})
print(json.dumps(outputs,indent=2))
