"""Lock photo observations and identities before any12 fit/reprojection."""
from pathlib import Path
import json,hashlib,datetime
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'data/photo-match-points12-guest-exterior.json'
assert not out.exists(),'Frozen observations must not be overwritten'
mesh=json.loads((ROOT/'qa/photo-match12-guest-mesh.json').read_text(encoding='utf-8'))
source=ROOT/'data/photo_refs/guest_exterior_10.jpg'
points=[]
def add(pid,pixel,name,role,identity,vertex=None,edge=None,confidence='B photo/plan topology; C modeled location and height',uncertainty=4):
    obj=mesh['objects'][name];vs=obj['world_vertices']
    if vertex is not None:
        xyz=vs[vertex];locator={'vertex_index':vertex,'adjacent_base_faces':[i for i,f in enumerate(obj['faces']) if vertex in f]}
    else:
        assert any(set(e)==set(edge) for e in obj['edges'])
        xyz=[sum(vs[v][k] for v in edge)/2 for k in range(3)]
        locator={'actual_edge_vertices':edge,'edge_midpoint':True,'adjacent_base_faces':[i for i,f in enumerate(obj['faces']) if set(edge)<=set(f)]}
    points.append({'id':pid,'pixel':pixel,'role':role,'object':name,**locator,'world_m':xyz,
      'identity':identity,'confidence':confidence,'pixel_uncertainty_px':uncertainty,
      'visibility':'Visible structural intersection; small frame/rim thickness contributes pixel uncertainty',
      'independently_reviewed':False,'acceptance':'UNVERIFIED identity candidate, frozen before fit'})
for i,h,s in [(0,(87,95),(87,461)),(2,(245,254),(245,510)),(3,(298,309),(298,530)),(5,(365,378),(365,551)),(7,(407,420),(407,567))]:
    role='fit' if i in (0,3,7) else 'holdout'
    for end,pix,edge in [('H',h,[4,5]),('S',s,[0,1])]:
        add('W%d%s'%(i,end),pix,'GUEST_L1_LOUNGE_FRONT_steel_window_0_mullion_%d'%i,role,
          'Visible sequential south-window post %d of8, west to east; %s outer post/frame meeting. Guest01 locates facade; equal7bay spacing and sill/head heights remain C.'%(i,'upper' if end=='H' else 'lower'),edge=edge)
add('R01',(657,467),'GUEST_LOW_ARM_ROOF','fit','South slab outer elbow: guest02(x488,y488.7), immediately west of first rectangular canopy aperture. Replaces old05 U longitudinal assignment with explicit source-topology hypothesis.',vertex=1,uncertainty=3)
add('R02',(601,469),'GUEST_LOW_ARM_ROOF','fit','South slab concave elbow: guest02(x488,y477.2); short Y-directed step R01-R02, then continuous narrow south canopy beam to east tip.',vertex=2,uncertainty=3)
add('R03',(596,540),'GUEST_LOW_ARM_ROOF','holdout','East/south lower termination of long canopy beam, guest02(x681,y477.2); last transverse canopy member meets this end. Far narrow profile; independent of R01/R02 fit.',vertex=3,uncertainty=4)
add('O0N',(445,475),'GUEST_LOW_ARM_ROOF','holdout','First rectangular aperture west/north lower corner, guest02(x488.7,y441). Same X station as near aperture margin; this is soffit opening, not sky-facing upper rim.',vertex=22,uncertainty=3)
add('O0S',(563,472),'GUEST_LOW_ARM_ROOF','holdout','First rectangular aperture west/south lower corner, guest02(x488.7,y468.5), across same aperture edge from O0N.',vertex=21,uncertainty=3)
doc={'schema':'fallingwater.photo_match12.guest_locked.v1','status':'LOCKED_UNVERIFIED_BEFORE_FIT',
  'locked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':str(source),
  'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'image_size':[742,1024],
  'source_record':'https://www.loc.gov/pictures/item/pa2187.photos.134233p/',
  'source_identity':'HABS PA-5346-A-10; from west along south facade; Jack E. Boucher; caption index1985 February/March, individual day unknown',
  'source_plan_identity':'HABS PA-5346-A guest01/02/04 measured drawings2010; structural-topology comparison across dates, not a2010 photo',
  'scene':mesh['scene'],'scene_sha256':mesh['scene_sha256'],'points':points,
  'fit_contract':{'fit_ids':[p['id'] for p in points if p['role']=='fit'],
     'holdout_ids':[p['id'] for p in points if p['role']=='holdout'],
     'single_interpretation':True,'geometry_changes':False,'residual_based_point_replacement':False,
     'parameters':'Rodrigues rotation3, eye3, log focal1; fixed principal point(371,512), square pixels, no distortion/crop/warp',
     'seed_eye':[1.5046,33.8981,7.8201],'seed_target':[14.,35.3,9.0],
     'seed_focal_px':704.55,'eye_bounds':[[0.,32.,7.],[4.,36.,10.2]],'focal_bounds_px':[222.6,2226.]},
  'excluded':[
   {'id':'W1_NEAR_STAIRS','photo_region':[230,850,640,1000],'identity':'Near west approach step group W1_FRONT_WEST. Group identityB; source/model riser countC; random stone nosing and exposed side irregularities do not define surveyed individual vertex.','role':'continuous-edge diagnostic only'},
   {'id':'W2_FAR_STAIRS','photo_region':[440,638,610,714],'identity':'Far east approach group W2_FRONT_EAST. Photo shows multiple rough nosings; modeled4risers C, individual photographed nosing-to-riser assignment unverified.','role':'continuous-edge diagnostic only'},
   {'id':'PEOPLE_STONE_TEXTURE','identity':'Person/hat and individual rough stone protrusions are not fixed surveyed architectural landmarks.','role':'excluded'}],
  'acceptance':'No correspondence independently reviewed yet; not GEO07 PASS even if numerical residual is small.'}
out.write_text(json.dumps(doc,indent=2),encoding='utf-8')
lock={'file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'point_count':len(points),'fit':8,'holdout':7,'stage':'before any12 projection'}
(ROOT/'qa/photo-match12-guest-observation-lock.json').write_text(json.dumps(lock,indent=2),encoding='utf-8')
im=Image.open(source).convert('RGB');canvas=Image.new('RGB',(1130,1080),'white');canvas.paste(im,(0,30));d=ImageDraw.Draw(canvas)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13)
d.text((12,5),'A10 | 1985 | fixed observations BEFORE fit |12a unchanged',font=font,fill='black')
for n,p in enumerate(points):
    x,y=p['pixel'];y+=30;col=(0,145,200) if p['role']=='fit' else (215,115,0)
    d.ellipse((x-4,y-4,x+4,y+4),outline=col,width=2)
    if p['id'].startswith('W'): labelxy=(x+6,y-16)
    else:labelxy={'R01':(658,472),'R02':(618,506),'R03':(615,566),'O0N':(454,478),'O0S':(516,484)}[p['id']]
    d.line([(x,y),labelxy],fill=col,width=1);d.text(labelxy,p['id'],font=small,fill=col,stroke_width=1,stroke_fill='white')
    d.text((755,48+n*43),p['id']+'  '+p['role']+'  '+str(tuple(p['pixel'])),fill=col,font=font)
    d.text((755,68+n*43),'actual '+('vertex '+str(p.get('vertex_index')) if 'vertex_index' in p else 'edge '+str(p['actual_edge_vertices'])),fill='black',font=small)
d.multiline_text((755,725),'Cyan =8 fitted\nOrange =7 withheld\n\nPixel positions locked first.\nNo image crop or warp in fit.\nModel fixed; no render.\n\nB: visible identity/topology\nC: modeled dimensions/heights\nUNVERIFIED until review.\n\nW1/W2 stair groups shown\nas continuous edges only;\nindividual rough nosings\nare not invented landmarks.',font=font,fill='black',spacing=6)
canvas.save(ROOT/'qa/photo-match12-guest-observed.png')
print(json.dumps(lock,indent=2))
