"""Read-only 11b saved geometry and accepted10 numeric local route regression."""
import bpy,sys,json,hashlib,array,ast,math,bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));import guest_bays11 as helper
tree=ast.parse((R/'qa/guest-bays11-build-check.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<own QA functions>','exec'))
d=json.loads((R/'qa/guest-bays11-reopen-and-seat-check.json').read_text(encoding='utf-8'))
scene_path=Path(d['scene11b']);assert hashlib.sha256(scene_path.read_bytes()).hexdigest()==d['scene11b_sha256']
W=R/'qa/integration10-navigation-workspace';rp=W/'data/tour-route.json';ap=W/'qa/tour-path-all-adjacency.json'
route=json.loads(rp.read_text(encoding='utf-8'));adj=json.loads(ap.read_text(encoding='utf-8'))
assert route['scene_file'].endswith('Fallingwater_integration_candidate10a.blend')
segments=[s for k in ('main_segments','supplemental_segments') for s in route[k] if 'GUEST_L1_THEATER' in s.get('room_ids',[])]
edges=[e for e in adj['edges'] if e['from']=='GUEST_L1_THEATER' or e['to']=='GUEST_L1_THEATER']
samples=[]
for s in segments:
 a,b=map(Vector,s['points']);count=s['end_frame']-s['start_frame']+1
 for i in range(count):samples.append({'kind':'accepted10_numeric_film_route','id':s['id'],'frame':s['start_frame']+i,'eye':list(a+(b-a)*i/(count-1))})
for e in edges:
 for i,(a,b) in enumerate(zip(e['points'],e['points'][1:])):
  a,b=Vector(a),Vector(b);steps=max(1,math.ceil((b-a).length/.02))
  for j in range(steps+1):samples.append({'kind':'accepted10_numeric_adjacency','id':e['id'],'piece':i,'eye':list(a+(b-a)*j/steps)})
reports={}
for label,src in [('before10a',R/'scene/Fallingwater_integration_candidate10a.blend'),('after11b',scene_path)]:
 bpy.ops.wm.open_mainfile(filepath=str(src));scene=bpy.context.scene;index=make_bvh();checks=[]
 for sample in samples:checks.append(dict(sample,failure=body(index,sample['eye'],sample['eye'][2]-1.6)))
 sweeps=[]
 for chain in segments+edges:
  for aa,bb in zip(chain['points'],chain['points'][1:]):
   a,b=Vector(aa),Vector(bb);delta=b-a;length=delta.length;direction=delta.normalized();side=Vector((-direction.y,direction.x,0)).normalized()
   for shift in (-.18,0,.18):
    for h in (.10,.40,.80,1.20,1.60,1.95):
     origin=a+side*shift+Vector((0,0,h-1.6));hit=ray(index,origin,direction,length)
     sweeps.append({'id':chain['id'],'from':aa,'to':bb,'side_m':shift,'height_m':h,'hit':hit})
 reports[label]={'checks':checks,'sweeps':sweeps,'saved_tour_cameras':[{'name':o.name,'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None} for o in scene.objects if o.name.startswith('CAM_TOUR')]}
 if label=='before10a':
  helper_report=helper.apply(scene)
  reproduction={o.name:signature(o) for o in scene.objects}
 else:
  saved={o.name:signature(o) for o in scene.objects}
  reproduction_changes=sorted(n for n in set(saved)|set(reproduction) if saved.get(n)!=reproduction.get(n))
  assert not reproduction_changes,reproduction_changes
 print(label,'point failures',sum(bool(x['failure']) for x in checks),'sweep hits',sum(bool(x['hit']) for x in sweeps),flush=True)
newfails=[{'before':x,'after':y} for x,y in zip(reports['before10a']['checks'],reports['after11b']['checks']) if not x['failure'] and y['failure']]
newsweeps=[{'before':x,'after':y} for x,y in zip(reports['before10a']['sweeps'],reports['after11b']['sweeps']) if not x['hit'] and y['hit']]
result={'scene11b_sha256':d['scene11b_sha256'],'helper_sha256':hashlib.sha256((R/'scripts/guest_bays11.py').read_bytes()).hexdigest(),'source_reproduction_all_object_fingerprints_identical':not reproduction_changes,'numeric_route_source':str(rp),'numeric_route_sha256':hashlib.sha256(rp.read_bytes()).hexdigest(),'adjacency_source':str(ap),'adjacency_sha256':hashlib.sha256(ap.read_bytes()).hexdigest(),'interpretation':'10a physical input has no assurance of installed latest10 route keys. These are read-only actual geometry tests of frozen accepted10 numeric route points, not a saved7584 animation claim. No camera/path data applied or saved.','local_sample_count':len(samples),'film_integer_samples':sum(s['kind']=='accepted10_numeric_film_route' for s in samples),'adjacency_samples':sum(s['kind']=='accepted10_numeric_adjacency' for s in samples),'new_point_failures':newfails,'new_sweep_intersections':newsweeps,'reports':reports,'scene_saved':False,'rendered':False,'source11b_unchanged':hashlib.sha256(scene_path.read_bytes()).hexdigest()==d['scene11b_sha256']}
(R/'qa/guest-bays11-route-reopen.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('REGRESSION',len(newfails),len(newsweeps),flush=True)
