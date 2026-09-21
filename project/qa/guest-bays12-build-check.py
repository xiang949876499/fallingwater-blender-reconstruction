import bpy,sys,json,hashlib,array,ast,math,bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import guest_bays11 as h
import guest_bays12 as fix
tree=ast.parse((R/'qa/guest-bays11-build-check.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<own inherited QA functions>','exec'))
S=R/'scene/Fallingwater_guest_bays_candidate11b.blend';expected='c025c0e1d6adc55077d4bcaa0c3d028174eb5643aa002f466e9c162067c17f74';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(S)==expected
protected=[S,R/'scripts/guest_bays11.py',R/'scripts/guest_house.py',R/'scripts/furnishings.py',R/'data/guest_house.json'];ph={str(p):sha(p) for p in protected}
bpy.ops.wm.open_mainfile(filepath=str(S));scene=bpy.context.scene
before={o.name:signature(o) for o in scene.objects};matrices={o.name:list(map(list,o.matrix_world)) for o in scene.objects};courses=[tuple(v.co) for v in scene.objects[fix.COURSES].data.vertices]
saved_settings=(scene.frame_current,scene.frame_start,scene.frame_end,scene.camera.name,scene.view_settings.exposure,scene.render.resolution_x,scene.render.resolution_y)
report=fix.apply(scene)
after={o.name:signature(o) for o in scene.objects};changed=[n for n in before if after.get(n)!=before[n]]
assert set(changed)==set(report['changed_objects']),(changed,report['changed_objects'])
assert set(before)==set(after)
assert all(matrices[o.name]==list(map(list,o.matrix_world)) for o in scene.objects)
selected={v for b in report['selected_course_blocks'] for v in range(b*8,b*8+8)};actual=scene.objects[fix.COURSES].data.vertices
assert all(tuple(actual[i].co)==v for i,v in enumerate(courses) if i not in selected)
# Complete blocks preserve all tangential coordinates, layer elevations and
# the ordering of their former relief depths; only normal allocation changes.
block_checks=[]
for panel in report['panels']:
 n=Vector(panel['normal_into_bay']);axis=Vector((-n.y,n.x,0))
 for b in panel['course_block_ids']:
  old=[Vector(courses[b*8+k]) for k in range(8)];new=[actual[b*8+k].co.copy() for k in range(8)]
  block_checks.append({'block':b,'max_z_change_m':max(abs(v.z-w.z) for v,w in zip(old,new)),'max_tangent_change_m':max(abs((v-w).dot(axis)) for v,w in zip(old,new)),'new_depth_m':max(v.dot(n) for v in new)-min(v.dot(n) for v in new)})
assert all(x['max_z_change_m']<.000001 and x['max_tangent_change_m']<.000005 and x['new_depth_m']>.006 for x in block_checks)
dep=bpy.context.evaluated_depsgraph_get();stone=scene.objects[fix.COURSES]
def component(name,blocks=None):
 ob=scene.objects[name].evaluated_get(dep);me=ob.to_mesh();vv=[ob.matrix_world@v.co for v in me.vertices];ff=[tuple(p.vertices) for p in me.polygons];owners=[name]*len(ff);ob.to_mesh_clear()
 for b in blocks or []:
  off=len(vv);vv.extend(stone.matrix_world@stone.data.vertices[b*8+i].co for i in range(8));ff.extend(tuple(off+i for i in f) for f in [(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]);owners.extend([fix.COURSES+':block'+str(b)]*6)
 return BVHTree.FromPolygons(vv,ff),owners
left=component(fix.PANELS[0][0],report['panels'][0]['course_block_ids']);right=component(fix.PANELS[1][0],report['panels'][1]['course_block_ids'])
g=h.design();d=h.xy3(g['d']);t=h.xy3(g['t']);mid=h.xy3((h.p((191.7,126.3))+h.p((215.9,167.6)))/2)
samples=[]
for station in (-.02,0,.04,.08,.10,.12,.16,.20,.24,.28,.32,.36):
 for step in range(213):
  z=8.42+.01*step;origin=mid+t*station;origin.z=z;hits=[]
  for (bvh,owners),direction in [(left,-d),(right,d)]:
   co,no,face,dist=bvh.ray_cast(origin,direction,5);hits.append(None if co is None else {'point':list(co),'normal':list(no),'face':face,'object':owners[face]})
  value=(Vector(hits[1]['point'])-Vector(hits[0]['point'])).dot(d) if all(hits) else None
  samples.append({'station_m':station,'z':z,'hits':hits,'completed_face_span_m':value,'error_m':None if value is None else value-2.486025,'pass_20mm':value is not None and abs(value-2.486025)<=.02})
assert all(x['pass_20mm'] for x in samples),[x for x in samples if not x['pass_20mm']][:8]
index=make_bvh();oldcam=json.loads((R/'qa/guest-bays11-camera-proposal.json').read_text(encoding='utf-8'));camera_checks=[]
for proposal in oldcam['proposals']:
 chosen=proposal['chosen'];fail=body(index,chosen['eye'],8.4);pathfails=[]
 for a,b in zip(proposal['local_approach']['eyes'],proposal['local_approach']['eyes'][1:]):
  a,b=Vector(a),Vector(b);steps=max(1,math.ceil((b-a).length/.02))
  for i in range(steps+1):
   p=a+(b-a)*i/steps;issue=body(index,p,8.4)
   if issue:pathfails.append({'point':list(p),'failure':issue})
 camera_checks.append({'bay':proposal['bay'],'eye':chosen['eye'],'target':chosen['target'],'failure':fail,'approach_failures':pathfails})
assert not any(x['failure'] or x['approach_failures'] for x in camera_checks)
oldroute=json.loads((R/'qa/guest-bays11-route-reopen.json').read_text(encoding='utf-8'));routes=[];sweeps=[]
for s in oldroute['reports']['after11b']['checks']:
 q=s['eye'];routes.append({'kind':s['kind'],'id':s['id'],'eye':q,'failure':body(index,q,q[2]-1.6)})
for s in oldroute['reports']['after11b']['sweeps']:
 a,b=Vector(s['from']),Vector(s['to']);v=(b-a).normalized();side=Vector((-v.y,v.x,0)).normalized();origin=a+side*s['side_m']+Vector((0,0,s['height_m']-1.6));sweeps.append({'id':s['id'],'hit':ray(index,origin,v,(b-a).length)})
assert not any(x['failure'] for x in routes) and not any(x['hit'] for x in sweeps)
oldfloor=json.loads((R/'qa/guest-bays11-reopen-and-seat-check.json').read_text(encoding='utf-8'));support=[]
for s in oldfloor['floor_support']:
 q=s['xy'];co,no,face,dist=index[2]['GUEST_L1_THEATER_FLOOR'].ray_cast(Vector((*q,8.5)),Vector((0,0,-1)),.3)
 support.append({'xy':q,'hit':None if co is None else list(co),'pass':co is not None and abs(co.z-8.4)<.004})
door=[{'xy':q['xy'],'failure':body(index,q['xy'])} for q in oldfloor['north_door_regression']]
assert all(x['pass'] for x in support) and not any(x['failure'] for x in door)
# Re-run whole connection rays with endpoints outside the complete panels.
joints=[]
aa=json.loads((R/'qa/guest-bays11-build-check.json').read_text(encoding='utf-8'))
for key in ('north_glazing','middle_glazing'):
 a,b=map(Vector,aa[key]);v=(b-a).normalized();cross=Vector((-v.y,v.x))
 for end in (a,b):
  for offset in (-.015,0,.015):
   q=end+v*offset
   for z in (8.42,8.45,8.6,8.8,9.5,10.45,10.54):
    hit=ray(index,(*(q-cross*3),z),(*cross,0),6);joints.append({'group':key,'xy':list(q),'z':z,'hit':hit})
assert all(x['hit'] for x in joints)
meshqa=[]
for name in report['changed_objects']:
 ob=scene.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);meshqa.append({'object':name,'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume':bm.calc_volume(signed=True)});bm.free()
assert all(x['nonmanifold_edges']==0 and x['signed_volume']>0 for x in meshqa)
assert saved_settings==(scene.frame_current,scene.frame_start,scene.frame_end,scene.camera.name,scene.view_settings.exposure,scene.render.resolution_x,scene.render.resolution_y)
out=R/'scene/Fallingwater_guest_bays_candidate12a.blend';assert not out.exists();bpy.ops.wm.save_as_mainfile(filepath=str(out),check_existing=False)
result={'source11b_sha256':expected,'candidate':str(out),'candidate_sha256':sha(out),'candidate_bytes':out.stat().st_size,'helper_sha256':sha(R/'scripts/guest_bays12.py'),'report':report,'actual_complete_surface_samples':samples,'complete_surface_sample_count':len(samples),'all_complete_surface_samples_pass_20mm':True,'completed_surface_min_m':min(s['completed_face_span_m'] for s in samples),'completed_surface_max_m':max(s['completed_face_span_m'] for s in samples),'changed_objects':changed,'all_other_object_fingerprints_identical':True,'all_object_matrices_identical':True,'course_blocks_changed':len(report['selected_course_blocks']),'unselected_course_vertices_unchanged':len(courses)-len(selected),'per_block_shape_preservation':block_checks,'camera_proposals':camera_checks,'accepted10_numeric_route_samples':routes,'accepted10_numeric_route_sweeps':sweeps,'floor_support':support,'north_door_checks':door,'wall_joint_rays':joints,'mesh_closure':meshqa,'scene_settings_preserved':True,'protected_files_unchanged':{str(p):sha(p)==ph[str(p)] for p in protected},'rendered':False,'qualification':'Actual complete surface dimensional tests include both backing and rough-course geometry. Source nominal boundary controls positions; normal relief amplitude and backing allocation remain C. This is not stone-by-stone archival or visual acceptance.'}
assert all(result['protected_files_unchanged'].values())
(R/'qa/guest-bays12-build-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:result[k] for k in ['candidate_sha256','candidate_bytes','helper_sha256','complete_surface_sample_count','completed_surface_min_m','completed_surface_max_m','course_blocks_changed']},indent=2),flush=True)
