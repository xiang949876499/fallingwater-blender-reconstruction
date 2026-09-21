"""Read-only finished-face decomposition and two bounded photography proposals."""
import bpy,sys,json,hashlib,ast,array,math,bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));import guest_bays11 as h
tree=ast.parse((R/'qa/guest-bays11-build-check.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<own bounded readonly probes>','exec'))
f=json.loads((R/'qa/guest-bays11-freeze.json').read_text(encoding='utf-8'));a=json.loads((R/'qa/guest-bays11-build-check.json').read_text(encoding='utf-8'))
S=R/'scene/Fallingwater_guest_bays_candidate11b.blend';before=hashlib.sha256(S.read_bytes()).hexdigest();assert before==f['candidate11b_sha256']
bpy.ops.wm.open_mainfile(filepath=str(S));scene=bpy.context.scene;dep=bpy.context.evaluated_depsgraph_get();stone=bpy.data.objects[h.COURSES]
def component(name,blocks=None):
 ob=bpy.data.objects[name].evaluated_get(dep);me=ob.to_mesh();vs=[ob.matrix_world@v.co for v in me.vertices];fs=[tuple(p.vertices) for p in me.polygons];owners=[name]*len(fs);ob.to_mesh_clear()
 for block in blocks or []:
  off=len(vs);vs.extend(stone.matrix_world@stone.data.vertices[block*8+i].co for i in range(8));fs.extend(tuple(off+i for i in face) for face in [(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]);owners.extend([h.COURSES+':block'+str(block)]*6)
 return BVHTree.FromPolygons(vs,fs),owners
def hit(tree,origin,dr):
 co,no,face,dist=tree[0].ray_cast(origin,dr,5)
 return None if co is None else {'point':list(co),'normal':list(no),'face':face,'object':tree[1][face]}
cores=[component('GUEST_L1_THEATER_DIAGONAL_BACK_pier_0'),component('GUEST_L1_CARPORT_RETAINED_PIER_2_pier_end')]
visible=[component('GUEST_L1_THEATER_DIAGONAL_BACK_pier_0',a['course_block_ids']['DIAGONAL_BACK']),component('GUEST_L1_CARPORT_RETAINED_PIER_2_pier_end',a['course_block_ids']['GUEST_L1_CARPORT_RETAINED_PIER_2_pier_end'])]
g=h.design();d=h.xy3(g['d']);t=h.xy3(g['t']);mid=h.xy3((h.p((191.7,126.3))+h.p((215.9,167.6)))/2);rows=[]
for station in (0,.10,.20):
 for step in range(186):
  z=8.55+step*.01;origin=mid+t*station;origin.z=z
  cc=[hit(cores[0],origin,-d),hit(cores[1],origin,d)];vv=[hit(visible[0],origin,-d),hit(visible[1],origin,d)]
  if not all(cc+vv):rows.append({'station_m':station,'z':z,'core_hits':cc,'visible_hits':vv,'status':'MISSING_FINITE_FACE'});continue
  span=(Vector(cc[1]['point'])-Vector(cc[0]['point'])).dot(d);clear=(Vector(vv[1]['point'])-Vector(vv[0]['point'])).dot(d)
  offsets=[(Vector(vv[0]['point'])-Vector(cc[0]['point'])).dot(d),(Vector(cc[1]['point'])-Vector(vv[1]['point'])).dot(d)]
  rows.append({'station_m':station,'z':z,'core_span_m':span,'visible_span_m':clear,'north_additive_projection_m':offsets[0],'pier2_additive_projection_m':offsets[1],'projection_sum_m':sum(offsets),'residual_gap_minus_projection_m':span-clear-sum(offsets),'north_hit':vv[0]['object'],'pier2_hit':vv[1]['object']})
valid=[q for q in rows if 'core_span_m' in q]
summary={}
for field in ('core_span_m','visible_span_m','north_additive_projection_m','pier2_additive_projection_m','projection_sum_m','residual_gap_minus_projection_m'):
 vals=[q[field] for q in valid];summary[field]={'min':min(vals),'max':max(vals),'mean':sum(vals)/len(vals)}
model={'construction_origin':'guest_house.py quadstone: random depth .012..042 m, midpoint thickness/2+depth/2-.005; outer face therefore always .007..037 m beyond existing wall core','source_interpretation':'Guest01 arrow witnesses reach the hatched masonry outline; no separate substrate/veneer or mean/peak convention identified. Printed-to-hidden-core interpretation is not established by source.','photo_limit':'HABS A10 actually viewed supports varied projecting real sandstone courses but is a different Guest wall/view and cannot measure Theater north bay or establish the survey datum.','diagnosis':'The entire sampled nominal-to-visible deficit decomposes into the two additive C course projections. Not evidence of a new wrong bay-axis correspondence.','non_mutating_proposal':'Rebase the structural backing and bay-facing relief around a stated finished masonry datum instead of stacking an all-positive extra layer outside the already traced masonry outline. Preserve every course depth and row silhouette; do not flat-cut peaks or translate source walls to make a selected ray pass. Datum choice remains C pending field/source clarification.'}
finish={'scene_sha256':before,'helper_sha256':hashlib.sha256((R/'scripts/guest_bays11.py').read_bytes()).hexdigest(),'samples':rows,'valid_samples':len(valid),'summary':summary,'model_analysis':model,'saved':False,'rendered':False}
(R/'qa/guest-bays11-finish-source-probe.json').write_text(json.dumps(finish,indent=2),encoding='utf-8');print('FINISH_SAMPLES',len(valid),summary,flush=True)
index=make_bvh();proposals=[]
plans=[('NORTH',[(.6,51.8),(1.0,52.1),(.6,52.3),(.1,52.0)],a['north_glazing']),('MIDDLE',[(.4,49.9),(0,49.0),(-.2,48.3),(.2,47.9),(.5,48.5)],a['middle_glazing'])]
for bay,candidates,endpoints in plans:
 aa,bb=map(Vector,endpoints);target=(aa+bb)/2;target=h.xy3(target,9.48);tests=[]
 for xy in candidates:
  eye=Vector((*xy,10.0));failure=body(index,eye,8.4);near=[ray(index,eye,dr,.13) for dr in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]]
  quat=(target-eye).to_track_quat('-Z','Y');inv=quat.inverted();samples=[]
  for frac in (.10,.30,.50,.70,.90):
   for z in (8.75,9.25,9.85,10.35):
    q=h.xy3(aa+(bb-aa)*frac,z);v=inv@(q-eye);screen=[v.x/(-v.z)*(24/36)*2,v.y/(-v.z)*(24/(36*9/16))*2] if v.z<0 else [99,99]
    delta=q-eye;first=ray(index,eye,delta.normalized(),delta.length+.06)
    own=bool(first and first['object'].startswith('GUEST_BAYS11_'+bay))
    samples.append({'bay_fraction':frac,'z':z,'screen_ndc':screen,'inside_frame':abs(screen[0])<1 and abs(screen[1])<1,'first_hit':first,'target_bay_first':own})
  corners=[]
  for xycorner in (aa,bb):
   for cz in (8.4,10.56):
    q=h.xy3(xycorner,cz);v=inv@(q-eye);screen=[v.x/(-v.z)*(24/36)*2,v.y/(-v.z)*(24/(36*9/16))*2]
    corners.append({'point':list(q),'screen_ndc':screen,'inside_frame':v.z<0 and abs(screen[0])<.98 and abs(screen[1])<.98})
  tests.append({'eye':list(eye),'target':list(target),'lens_mm':24,'sensor_width_mm':36,'aspect':[16,9],'normal_eye_height_m':1.6,'body_failure':failure,'near_camera_hits':[x for x in near if x],'visible_in_frame_samples':sum(x['inside_frame'] and x['target_bay_first'] for x in samples),'full_bay_floor_to_top_corners':corners,'whole_bay_framed':all(x['inside_frame'] for x in corners),'samples':samples})
 acceptable=[q for q in tests if not q['body_failure'] and not q['near_camera_hits'] and q['whole_bay_framed']]
 chosen=max(acceptable,key=lambda q:q['visible_in_frame_samples']) if acceptable else None
 proposals.append({'bay':bay,'candidate_tests':tests,'chosen':chosen})
for proposal in proposals:
 chosen=proposal['chosen'];assert chosen is not None
 goal=chosen['eye']
 if proposal['bay']=='NORTH':chain=[[-.29519,50.2696,10.0],[.055,50.2,10.0],[.055,51.65,10.0],goal]
 else:chain=[[-.54,49.0,10.0],[.055,49.0,10.0],[.055,49.95,10.0],goal]
 samples=[];sweeps=[]
 for aa,bb in zip(chain,chain[1:]):
  aa,bb=Vector(aa),Vector(bb);delta=bb-aa;steps=max(1,math.ceil(delta.length/.02));dr=delta.normalized();side=Vector((-dr.y,dr.x,0)).normalized()
  for k in range(steps+1):
   q=aa+delta*k/steps;samples.append({'eye':list(q),'failure':body(index,q,8.4)})
  for off in (-.18,0,.18):
   for z in (.1,.4,.8,1.2,1.6,1.95):sweeps.append({'hit':ray(index,aa+side*off+Vector((0,0,z-1.6)),dr,delta.length),'height_m':z,'side_m':off})
 proposal['local_approach']={'eyes':chain,'samples':samples,'sweeps':sweeps,'pass':not any(x['failure'] for x in samples) and not any(x['hit'] for x in sweeps)}
out={'scene_sha256':before,'camera_objects_created':False,'camera_values_applied':False,'scene_saved':False,'rendered':False,'proposals':proposals,'qualified_claim':'Standing/body/near-camera and local approach checked on actual11b evaluated geometry. Visibility is geometric ray/frustum coverage; composition and lighting remain unrendered C photography proposals, not photo-match PASS.','input_sha_unchanged':hashlib.sha256(S.read_bytes()).hexdigest()==before}
(R/'qa/guest-bays11-camera-proposal.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('CAMERAS',[(p['bay'],p['chosen']['eye'],p['chosen']['visible_in_frame_samples'],p['local_approach']['pass']) for p in proposals],flush=True)
