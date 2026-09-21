"""Frozen-camera evidence and independent preview scoring, no rendering."""
from pathlib import Path
import json,hashlib,math
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
mesh=json.loads((R/'qa/photo-match-mesh-iteration05.json').read_text(encoding='utf-8'))
objs={o['name']:o for o in mesh['objects']}
prior=json.loads((R/'qa/photo-match-results-iteration04-interior-diagnostic.json').read_text(encoding='utf-8'))
cam=next(x['camera'] for x in prior['results'] if x['id']=='main_living_48')
obj=objs['MAIN_L1_south_stone_pier_1']
pts=np.array(obj['vertices']);rot=np.array(cam['rotation_world_to_opencv']);v=(pts-np.array(cam['location']))@rot.T
uv=v[:,:2]/v[:,2,None]*cam['focal_pixels']+np.array(cam['principal_point'])
im=Image.open(R/'data/photo_refs/main_living_48.jpg').convert('RGB');d=ImageDraw.Draw(im)
d.rectangle((0,0,1024,45),fill='#111111');d.text((10,7),'QA ONLY - locked iteration04 ceiling camera, NO new fit',fill='white');d.text((10,25),'Orange: observed pier region. Red: actual iteration05 substrate wireframe.',fill='white')
d.rectangle((265,215,310,396),outline='orange',width=3)
for a,b in obj['edges']:d.line([tuple(uv[a]),tuple(uv[b])],fill='red',width=2)
for i,q in enumerate(uv):d.text(tuple(q),str(i),fill='red')
im.save(R/'qa/photo-match-main_living_48-iteration05-pier-locked.png')
evidence=dict(scene_sha256=mesh['sha256'],camera_unchanged=cam,camera_source='qa/photo-match-results-iteration04-interior-diagnostic.json',object=obj['name'],vertices=pts.tolist(),projected_vertices=uv.tolist(),observed_region=[265,215,310,396],status='NOT_RUN',reason='Observed rectangular region is not a measured geometric point. Vertex-to-visible-face identity unresolved; no random rock corner promoted to holdout.',wireframe_bbox=[*uv.min(axis=0).tolist(),*uv.max(axis=0).tolist()])
(R/'qa/photo-match-main_living_48-iteration05-pier-locked.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
names=['CAM_MAIN_B_BATH_B_EV1p6.png','CAM_MAIN_L1_LIVING_B_EV2p4.png','CAM_GUEST_L1_LOUNGE_A_EV2p4.png','CAM_GUEST_POOL.png','CAM_MAIN_B_BATH_A_EV1p6.png']
scores=[[3,2,3,2,2],[2,2,3,3,2],[2,2,2,2,2],[3,2,3,2,2],[3,2,3,2,2]]
notes=[
 'Two previous wide black floor strips are absent in this view; doorway floor continuity visually improved. Sink basin/faucet readable. Pedestal cut by frame; room geometry beyond view unassessed. Generic fixture profile and flat broad material response remain.',
 'Fireplace opening and masonry relief readable; dominant hearth is a clean concentric stepped plinth rather than the visibly irregular natural exposed bedrock of photo48. Stone courses are nearly machine-regular. Ceiling panel cropped, dark dining corner, flat smooth kettle.',
 'View faces the bookcase and timber screen; new northwest fireplace entirely outside frame. Cannot approve the fireplace or compare to A11 from this image. Books are repeated blocks; furniture and stone remain simplified; deep shadows hide corner construction.',
 'Pool, slab, retaining wall and building relationship readable. Water is dominated by a broad pale reflection with little visible depth/edge detail at this resolution. Vegetation silhouette repeats and large near leaves frame architecture heavily. No claim of below-water geometry or dynamic-water continuity.',
 'Toilet and washbasin visible at useful scale but both cropped. Warm cork enclosure coherent; generic highly smooth porcelain lacks drain/seat-detail evidence. This does not independently verify fixture dimensions or original historical model.'
]
rows=[]
for name,ss,note in zip(names,scores,notes):
 p=R/'renders/previews/iteration05-focus'/name
 rows.append(dict(file=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),image_size=list(Image.open(p).size),actually_viewed=True,scores=dict(zip(['architecture','materials','lighting','environment_context','photographic_realism'],ss)),observations=note,status='VISUAL_NOT_ACCEPTED'))
report={'scene_sha256':mesh['sha256'],'reviewer':'independent photo05 agent','review_scope':'Five actual CPU Cycles 960x540 24-sample preview PNGs, all opened; 4K, motion, dimensions and hidden geometry not assessed','scale':{'1':'major unreadability or blockout','2':'readable prototype with obvious artificial form/material','3':'plausible intermediate scene; needs improvement','4':'near-photographic quality with small defects','5':'finished photographic acceptance'},'result':'NOT_ACCEPTED','items':rows,'source_photos_actually_viewed':['main_living_48.jpg','guest_living_11.jpg','guest_exterior_10.jpg'],'priority_findings':[{'priority':'P1','issue':'Main hearth visible natural bedrock identity not established by stepped manufactured plinth','action':'Compare main11/hearth drawings and archival views, confirm whether current visible object substitutes the exposed boulder; source-supported rebuild of outline if confirmed. Do not hide discrepancy with camera crop.'},{'priority':'P1','issue':'Guest lounge focus view excludes newly built fireplace','action':'Render a confirmed east-to-west structural view that contains open corner, west window return and floor/ceiling connections; current image cannot close this QA item.'},{'priority':'P1','issue':'A10 noncoplanar soffit fails independent candidate projection by 18.386% diagonal despite low planar window residual','action':'Verify low-arm roof polygon from guest02 before changing geometry. R01 station is unconfirmed, so residual alone is not a measured offset.'}]}
(R/'qa/photo-match-iteration05-visual-review.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print('Frozen pier bbox',evidence['wireframe_bbox']);print('Saved independent five-view scoring')
