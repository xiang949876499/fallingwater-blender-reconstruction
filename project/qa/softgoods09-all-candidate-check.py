"""Check the production bed hook on every original bed pillow, CPU only."""
import bpy,bmesh,sys,json,hashlib,array,re,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import furnishing_softgoods as soft
SRC=R/'scene/Fallingwater_structure_candidate09.blend';OUT=R/'scene/Fallingwater_softgoods_candidate09_all.blend'
BOTTOM=.513+.025/2-.576;TOP=.14/2
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC)=='4fa1fc1f56795a2da88c97bacc9bd3b2a0730d3d085076173425b00addd744a0'
protected={n:sha(R/'scripts'/n) for n in ('main_house.py','furnishings.py','furnishing_softgoods.py')}
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene
def settings():return (s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.render.engine,s.cycles.samples,s.cycles.device,s.render.threads,s.render.threads_mode,s.render.filepath,s.frame_current,s.frame_start,s.frame_end,s.camera.name if s.camera else None,s.view_settings.exposure)
original_settings=settings()
def fingerprints():
 out={};shared={}
 for ob in s.objects:
  h=hashlib.sha256(str((tuple(tuple(row) for row in ob.matrix_world),ob.parent.name if ob.parent else None,ob.hide_render,ob.hide_viewport)).encode())
  if ob.type=='MESH':
   ptr=ob.data.as_pointer()
   if ptr not in shared:
    a=array.array('f',[0.])*(len(ob.data.vertices)*3);ob.data.vertices.foreach_get('co',a);b=array.array('i',[0])*len(ob.data.loops);ob.data.loops.foreach_get('vertex_index',b);shared[ptr]=hashlib.sha256(a.tobytes()+b.tobytes()).digest()
   h.update(shared[ptr])
  h.update(str(tuple(m.name if m else None for m in getattr(ob.data,'materials',[]))).encode());h.update(str([(m.name,m.type,getattr(m,'width',None),m.show_viewport,m.show_render) for m in ob.modifiers]).encode())
  if ob.type=='CAMERA':h.update(str((ob.data.lens,ob.data.sensor_width,ob.data.shift_x,ob.data.shift_y)).encode())
  if ob.type=='LIGHT':h.update(str((ob.data.energy,tuple(ob.data.color))).encode())
  out[ob.name]=h.hexdigest()
 return out
def evaluated(ob):
 e=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();loc=[list(v.co) for v in m.vertices];world=[list(e.matrix_world@v.co) for v in m.vertices];faces=[tuple(p.vertices) for p in m.polygons];e.to_mesh_clear();return loc,world,faces
def bounds(vv):return [[min(v[k] for v in vv),max(v[k] for v in vv)] for k in range(3)]
targets=sorted([ob for ob in s.objects if ob.type=='MESH' and re.search(r'_pillow(?:\.\d+)?$',ob.name) and ob.get('asset_type') in ('single_bed','walnut_bed','bed')],key=lambda x:x.name)
all_pillows=[ob.name for ob in s.objects if ob.type=='MESH' and re.search(r'_pillow(?:\.\d+)?$',ob.name)]
print(json.dumps({'pillow_discovery':[{'name':n,'asset_type':s.objects[n].get('asset_type'),'parent':s.objects[n].parent.name if s.objects[n].parent else None,'room':s.objects[n].get('room_id')} for n in all_pillows]},indent=2))
assert set(all_pillows)=={ob.name for ob in targets}
before=fingerprints();records=[];bed_cache={}
for ob in targets:
 root=ob.parent;w=float(root['footprint_width']);n=1 if w<1.25 else 2
 cover=s.objects[root.name+'_woven_bedcover'];cl,cw,cf=evaluated(cover);cover_top=max(v[2] for v in cw)
 oldloc,oldworld,_=evaluated(ob);localbounds=bounds(oldloc)
 z_axis=[ob.matrix_world[k][2] for k in range(3)]
 actual_bottom_local=cover_top-ob.matrix_world.translation.z
 difference=actual_bottom_local-BOTTOM
 hook_ok=abs(difference)<2e-6 and abs(z_axis[2]-1)<1e-7 and abs(z_axis[0])+abs(z_axis[1])<1e-7 and abs((localbounds[0][1]-localbounds[0][0])-(w/n-.11))<2e-6 and abs((localbounds[1][1]-localbounds[1][0])-.46)<2e-6
 records.append({'target':ob.name,'bed':root.name,'room':ob.get('room_id'),'bed_width':w,'pillow_count_formula':n,'hook_width':w/n-.11,'hook_bottom_local':BOTTOM,'actual_bottom_local':actual_bottom_local,'bottom_constant_difference_m':difference,'hook_assumptions_pass':hook_ok,'cover':cover.name,'cover_top_world_z':cover_top,'old_local_bounds':localbounds,'old_world_bounds':bounds(oldworld),'old_matrix_world':[list(v) for v in ob.matrix_world],'old_matrix_local':[list(v) for v in ob.matrix_local],'old_materials':[m.name for m in ob.data.materials]})
 if root.name not in bed_cache:
  bed_cache[root.name]={'cover_tree':BVHTree.FromPolygons([Vector(v) for v in cw],cf),'mattress_top':max(v[2] for v in evaluated(s.objects[root.name+'_mattress'])[1]),'platform_top':max(v[2] for v in evaluated(s.objects[root.name+'_walnut_platform'])[1])}
baseline={'source_sha256':sha(SRC),'protected_source_hashes':protected,'all_pillows_count':len(targets),'beds_count':len(bed_cache),'records':records}
(R/'qa/softgoods09-all-baseline.json').write_text(json.dumps(baseline,indent=2))
if not all(r['hook_assumptions_pass'] for r in records):
 print(json.dumps({'status':'HOOK_ASSUMPTION_FAILED_NO_CANDIDATE_SAVED','failed':[r for r in records if not r['hook_assumptions_pass']]}));raise RuntimeError('Notify integrator: actual support differs from production hook')
geometries={}
for r in records:geometries[r['target']]=soft.replace_pillow_mesh(s.objects[r['target']],r['hook_width'],.46,BOTTOM,TOP)
bpy.context.view_layer.update();after=fingerprints();changed=sorted(n for n in before if before[n]!=after[n])
assert set(before)==set(after) and changed==sorted(r['target'] for r in records);assert settings()==original_settings
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));bpy.ops.wm.open_mainfile(filepath=str(OUT));s=bpy.context.scene;assert settings()==original_settings
for r in records:
 ob=s.objects[r['target']];geo=geometries[ob.name];loc,world,faces=evaluated(ob);nb,wb=bounds(loc),bounds(world)
 repro=max(abs(a[k]-b[k]) for a,b in zip(loc,geo['vertices']) for k in range(3))
 pose=r['old_matrix_world']==[list(v) for v in ob.matrix_world] and r['old_matrix_local']==[list(v) for v in ob.matrix_local] and ob.parent.name==r['bed'];mats=r['old_materials']==[m.name for m in ob.data.materials]
 bm=bmesh.new();bm.from_mesh(ob.data);bm.normal_update();manifold=all(e.is_manifold and e.is_contiguous for e in bm.edges);volume=bm.calc_volume(signed=True);zero=sum(f.calc_area()<1e-12 for f in bm.faces);euler=len(bm.verts)-len(bm.edges)+len(bm.faces)
 visited=set();components=0
 for v in bm.verts:
  if v.index in visited:continue
  components+=1;stack=[v]
  while stack:
   q=stack.pop()
   if q.index in visited:continue
   visited.add(q.index);stack.extend(e.other_vert(q) for e in q.link_edges)
 bm.free();count=(geo['parameters']['columns']-1)*(geo['parameters']['rows']-1)
 normals=all(p.normal.z>0 for p in ob.data.polygons[:count]) and all(p.normal.z<0 for p in ob.data.polygons[count:count*2])
 tree=BVHTree.FromPolygons([Vector(v) for v in loc],faces);intersections=[]
 for a,b in tree.overlap(tree):
  if a>=b or set(faces[a])&set(faces[b]):continue
  intersections.append([a,b])
 contact=[];under=[];support=bed_cache[r['bed']]['cover_tree'];contactset=set(geo['groups']['contact'])
 for i in geo['groups']['bottom']:
  p=Vector(world[i]);q,no,f,d=support.ray_cast(p+Vector((0,0,.03)),Vector((0,0,-1)),.15);gap=p.z-q.z if q is not None else None
  u={'vertex':i,'cover_gap_m':gap,'over_cover':q is not None,'not_penetrating':gap is None or gap>=-2e-6}
  under.append(u)
  if i in contactset:contact.append(dict(u,pass_=gap is not None and abs(gap)<2e-6))
 envelope=all(nb[k][0]>=r['old_local_bounds'][k][0]-2e-6 and nb[k][1]<=r['old_local_bounds'][k][1]+2e-6 for k in range(3)) and all(wb[k][0]>=r['old_world_bounds'][k][0]-2e-6 and wb[k][1]<=r['old_world_bounds'][k][1]+2e-6 for k in range(3))
 clearances={k:wb[2][0]-bed_cache[r['bed']][k] for k in ('mattress_top','platform_top')}
 passed=pose and mats and envelope and manifold and normals and volume>0 and zero==0 and euler==2 and components==1 and not intersections and all(x['pass_'] for x in contact) and all(x['not_penetrating'] for x in under) and all(x>0 for x in clearances.values()) and repro<1e-6
 r.update({'new_local_bounds':nb,'new_world_bounds':wb,'pose_and_parent_unchanged':pose,'materials_unchanged':mats,'inside_original_envelope':envelope,'manifold_winding':manifold,'normals_consistent':normals,'signed_volume_m3':volume,'zero_area_faces':zero,'euler_characteristic':euler,'connected_components':components,'nonadjacent_intersections':intersections,'vertices':len(loc),'faces':len(faces),'contact':contact,'underside':under,'bed_clearances_m':clearances,'source_rebuild_error_m':repro,'pass_':passed})
# Evaluate existing guest A/B cameras, with no movement or camera changes.
guest_views=[];dg=bpy.context.evaluated_depsgraph_get()
for r in records:
 if not r['room'].startswith('GUEST_'):continue
 ob=s.objects[r['target']];g=geometries[ob.name];cols=g['parameters']['columns'];rows=g['parameters']['rows']
 for cam in [c for c in s.objects if c.type=='CAMERA' and c.name in ('CAM_'+r['room']+'_A','CAM_'+r['room']+'_B')]:
  visible=0;in_frame=0;proj=[]
  for j in (8,12,16,20,24):
   for i in (12,18,24,30,36):
    p=ob.matrix_world@Vector(g['vertices'][j*cols+i]);v=world_to_camera_view(s,cam,p);proj.append([v.x,1-v.y]);inside=v.z>0 and 0<v.x<1 and 0<v.y<1
    if not inside:continue
    in_frame+=1;direction=(p-cam.matrix_world.translation).normalized();hit,q,no,f,first,_=s.ray_cast(dg,cam.matrix_world.translation,direction,distance=(p-cam.matrix_world.translation).length+.01)
    if hit and first.name==ob.name:visible+=1
  guest_views.append({'room':r['room'],'target':r['target'],'camera':cam.name,'samples':25,'in_frame':in_frame,'first_hit_target':visible,'projected_sample_bounds':[[min(p[k] for p in proj),max(p[k] for p in proj)] for k in range(2)]})
source_unchanged={n:sha(R/'scripts'/n)==h for n,h in protected.items()}
counts={'beds':len(bed_cache),'pillows':len(records),'changed_objects':len(changed),'pillow_fails':sum(not r['pass_'] for r in records),'hook_assumption_fails':sum(not r['hook_assumptions_pass'] for r in records),'flat_contact_vertices':sum(len(r['contact']) for r in records),'contact_fails':sum(not c['pass_'] for r in records for c in r['contact']),'underside_vertices':sum(len(r['underside']) for r in records),'underside_penetrations':sum(not c['not_penetrating'] for r in records for c in r['underside']),'nonadjacent_intersections':sum(len(r['nonadjacent_intersections']) for r in records),'max_hook_support_difference_m':max(abs(r['bottom_constant_difference_m']) for r in records),'max_source_rebuild_error_m':max(r['source_rebuild_error_m'] for r in records)}
report={'status':'PASS_ALL_BED_PILLOW_GEOMETRY_VISUAL_PENDING' if not counts['pillow_fails'] and all(source_unchanged.values()) else 'FAIL_ALL_BED_PILLOW_GEOMETRY','source':str(SRC),'source_sha256':sha(SRC),'candidate':str(OUT),'candidate_sha256':sha(OUT),'protected_source_hashes':protected,'protected_sources_unchanged':source_unchanged,'changed':changed,'all_non_targets_identical':all(before[n]==after[n] for n in before if n not in changed),'saved_settings_unchanged':settings()==original_settings,'hook_parameters':{'width':'bed_width/(1 if bed_width<1.25 else 2)-.11','depth':.46,'bottom_z':BOTTOM,'top_z':TOP},'counts':counts,'pillows':records,'guest_view_checks':guest_views,'limits':['Every original bed pillow in the frozen structure09 scene was replaced; no other target class is inferred.','No production source was edited by this check; current hook constants tested against actual evaluated covers.','A central compressed underside contacts the cover; lifted edge portions beyond cover bounds may lie above mattress.','Single Alcove pillow visual improvement accepted by integrator; other pillows still require representative original-camera view inspection.']}
(R/'qa/softgoods09-all-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ('status','candidate_sha256','counts','guest_view_checks')},indent=2))
