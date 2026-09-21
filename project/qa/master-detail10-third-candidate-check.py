"""Independent saved-candidate CPU4 geometry QA. No rendering or route edits."""
import bpy,sys,json,hashlib,array,collections,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import master_detail10 as fix
import main_house as mh
SRC=R/'scene/Fallingwater_main_interface_candidate10c.blend'
OUT=R/'scene/Fallingwater_master_detail_candidate10c.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC)=='f85d813129fab175257f00be12c8d1116505b62d2ca1f9f8a6ffae57926e4a2a'
assert not OUT.exists(),'Preserve previous candidates/failures; choose a new candidate name'
protected=['scripts/main_house.py','scripts/furnishings.py','scripts/camera_review.py','scripts/tour.py','data/main_house.json','data/camera-settings-reviewed.json','data/tour-route.json','config.json']
protected_before={p:sha(R/p) for p in protected}
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene
def settings():
 return {'resolution':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],'frame':s.frame_current,'range':[s.frame_start,s.frame_end], 'camera':s.camera.name,'threads':[s.render.threads_mode,s.render.threads],'engine':s.render.engine,'samples':s.cycles.samples,'device':s.cycles.device,'exposure':s.view_settings.exposure,'world':s.world.name,'filepath':s.render.filepath}
settings_before=settings()
def fingerprints():
 out={};cache={}
 for o in s.objects:
  h=hashlib.sha256(str([list(v) for v in o.matrix_world]).encode())
  if o.type=='MESH':
   k=o.data.as_pointer()
   if k not in cache:
    a=array.array('f',[0.]*(len(o.data.vertices)*3));b=array.array('i',[0]*len(o.data.loops));o.data.vertices.foreach_get('co',a);o.data.loops.foreach_get('vertex_index',b)
    cache[k]=hashlib.sha256(a.tobytes()+b.tobytes()).digest()
   h.update(cache[k])
  if o.type=='CAMERA':h.update(str((o.data.lens,o.data.sensor_width,o.data.sensor_height,o.data.shift_x,o.data.shift_y,o.data.clip_start,o.data.clip_end)).encode())
  if o.type=='LIGHT':h.update(str((o.data.type,o.data.energy,list(o.data.color))).encode())
  h.update(str([m.name if m else None for m in getattr(o.data,'materials',[])]).encode())
  h.update(str((o.hide_render,o.hide_viewport,o.parent.name if o.parent else None)).encode());out[o.name]=h.hexdigest()
 return out
def tree(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();t=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear();return t
def cast(p,d=(0,0,-1),dist=100):
 h,q,n,f,o,mat=s.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector(p),Vector(d),distance=dist)
 return {'object':o.name if h else None,'point':list(q) if h else None,'normal':list(n) if h else None,'face':f if h else None}
def inside(p,poly):
 yes=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:yes=not yes
 return yes
def area(poly):return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1])))/2
before=fingerprints()
oldmasterpoly=[list(v.co)[:2] for v in s.objects['MAIN_L2_MASTER_finish'].data.vertices][:len(s.objects['MAIN_L2_MASTER_finish'].data.vertices)//2]
manifest=fix.apply(False);bpy.context.view_layer.update();after=fingerprints()
assert set(before)-set(after)==set(manifest['removed'])
assert set(after)-set(before)==set(manifest['added'])
actual_changed=sorted(n for n in set(before)&set(after) if before[n]!=after[n])
unexpected=[n for n in actual_changed if n not in manifest['changed']]
assert not unexpected,unexpected
manifest['actual_changed']=actual_changed
assert settings()==settings_before
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));bpy.ops.wm.open_mainfile(filepath=str(OUT));s=bpy.context.scene
assert fingerprints()==after and settings()==settings_before
targets=set(manifest['changed']+manifest['added'])
trees={o.name:tree(o) for o in s.objects if o.type=='MESH' and (o.name in targets or o.name.startswith('MAIN_') and o.name.endswith('_finish'))}
nearby={o.name:tree(o) for o in s.objects if o.type=='MESH' and (o.name.startswith(('MAIN_L2_','MASTER_DETAIL10_','FW_FURN_MAIN_L2_MASTER_','MAIN_floor_threshold_','MAIN_stair2_')))}
meshes=[]
for n in targets:
 o=s.objects[n]
 if o.type!='MESH':continue
 counts=collections.Counter(tuple(sorted(e)) for f in o.data.polygons for e in f.edge_keys)
 o.data.calc_loop_triangles();v=sum(o.data.vertices[t.vertices[0]].co.cross(o.data.vertices[t.vertices[1]].co).dot(o.data.vertices[t.vertices[2]].co)/6 for t in o.data.loop_triangles)
 meshes.append({'object':n,'vertices':len(o.data.vertices),'edge_multiplicity':dict(collections.Counter(counts.values())),'signed_volume':v,'pass':all(k==2 for k in counts.values()) and v>0})
floor=[];p=[mh.xy(q) for q in fix.master_floor_polygon(False)]
for ix in range(100):
 for iy in range(100):
  q=(min(x for x,y in p)+(max(x for x,y in p)-min(x for x,y in p))*(ix+.371)/100,min(y for x,y in p)+(max(y for x,y in p)-min(y for x,y in p))*(iy+.413)/100)
  if not inside(q,p):continue
  layers=[]
  for n,t in trees.items():
   if not n.endswith('_finish'):continue
   h,no,f,d=t.ray_cast(Vector((*q,fix.TOP+.04)),Vector((0,0,-1)),.08)
   if h is not None and abs(h.z-fix.TOP)<.0001:layers.append(n)
  floor.append({'xy':q,'layers':layers,'pass':len(layers)==1})
def body_at(px,py,label,radius=.18):
 xy=mh.xy((px,py));hits=[]
 for dz in (.18,.60,1.10,1.60):
  q=Vector((*xy,fix.TOP+dz))
  for n,t in nearby.items():
   if n.endswith(('_finish','_slab')) or 'threshold' in n:continue
   h,no,f,d=t.find_nearest(q,radius)
   if h is not None:hits.append({'object':n,'z':q.z,'distance':d})
 ground=cast((*xy,fix.TOP+.06),dist=.2)
 return {'label':label,'source':[px,py],'body_hits':hits,'ground':ground,'pass':not hits and ground['point'] is not None and abs(ground['point'][2]-fix.TOP)<.004}
body=[]
# Source-based proposed bypass: north hall -> true door -> west side of bed ->
# south side -> southeast bathroom approach. Existing animated route untouched.
paths={'true_hall_entry':[(359,295),(359,309),(359,320),(359,342)],
       'around_bed_to_bath_approach':[(359,342),(359,388),(397,388),(414,388)],
       'south_terrace_access':[(359,388),(376,394),(376,416)]}
for label,pts in paths.items():
 for i,(a,b) in enumerate(zip(pts,pts[1:])):
  distance=math.dist(mh.xy(a),mh.xy(b));count=max(2,math.ceil(distance/.06))
  for k in range(count+1):body.append(body_at(a[0]+(b[0]-a[0])*k/count,a[1]+(b[1]-a[1])*k/count,label))
cameras=[]
for n in ['CAM_MAIN_L2_MASTER_A','CAM_MAIN_L2_MASTER_B']:
 o=s.objects[n];q=o.matrix_world.translation
 cameras.append({'camera':n,'world_location':list(q),'body':body_at(q.x/mh.SX+327,540-q.y/mh.SY,n),'fingerprint_identical':before[n]==after[n]})
# True east-facing cavity: cast from open room toward the firebox back at
# several Y/Zs. A visible opening must hit the recessed liner, not a front wall.
cavity=[]
for py in (335,338,341,344,347):
 for z in (3.12,3.35,3.58):
  origin=(*mh.xy((345,py)),z);hit=cast(origin,(-1,0,0),3)
  cavity.append({'source_py':py,'z':z,'hit':hit,'pass':hit['object']=='MASTER_DETAIL10_firebox_back_liner'})
route=json.loads((R/'qa/main-interface10-route-snapshot.json').read_text(encoding='utf-8'))
oldroute=[]
target_trees={n:t for n,t in trees.items() if n in targets and not n.endswith(('_slab','_finish'))}
for seg in route['main_segments']+route['supplemental_segments']:
 if not any('MASTER' in r or 'CLOSET_M' in r for r in seg.get('room_ids',[])):continue
 for i,(aa,bb) in enumerate(zip(seg['points'],seg['points'][1:])):
  a,b=Vector(aa),Vector(bb);count=max(2,math.ceil((b-a).length/.1))
  for k in range(count+1):
   eye=a.lerp(b,k/count);hits=[]
   for dz in (0,-.65,-1.3):
    for n,t in target_trees.items():
     h,no,f,d=t.find_nearest(eye+Vector((0,0,dz)),.18)
     if h is not None:hits.append(n)
   if hits:oldroute.append({'segment':seg['id'],'edge':i,'fraction':k/count,'eye':list(eye),'target_hits':sorted(set(hits))})
counts={'target_meshes':len(meshes),'mesh_fails':sum(not x['pass'] for x in meshes),'floor_samples':len(floor),'floor_fails':sum(not x['pass'] for x in floor),'proposed_path_body_samples':len(body),'body_fails':sum(not x['pass'] for x in body),'cavity_samples':len(cavity),'cavity_fails':sum(not x['pass'] for x in cavity),'legacy_route_target_hits':len(oldroute)}
report={'status':'CANDIDATE_SAVED_SCOPED_QA_RECORDED_VISUAL_NOT_RUN','source':str(SRC),'source_sha256':sha(SRC),'candidate':str(OUT),'candidate_sha256':sha(OUT),'candidate_bytes':OUT.stat().st_size,'helper_sha256':sha(R/'scripts/master_detail10.py'),'manifest':manifest,'counts':counts,'settings_unchanged':settings()==settings_before,'non_target_fingerprints_identical':not unexpected,'saved_reopen_fingerprints_identical':True,'protected_hashes_unchanged':{n:sha(R/n)==h for n,h in protected_before.items()},'master_floor_area_m2':{'before':area(oldmasterpoly),'after':area(p)},'mesh_checks':meshes,'floor_samples':floor,'body_samples':body,'camera_checks':cameras,'cavity_checks':cavity,'legacy_route_failures':oldroute,'proposed_paths_source':paths,'limits':['Original120-camera visual review and complete60connection/7584frame tour not run.','Legacy route remains invalid where old door is filled/new furniture placed.','Standing new source paths are only local proposals, not accepted animated routes.','Separate bath candidate not applied; old bath threshold notch remains.']}
(R/'qa/master-detail10-build-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'status':report['status'],'counts':counts,'cameras':cameras,'sha256':report['candidate_sha256'],'protected':report['protected_hashes_unchanged']},indent=2))
