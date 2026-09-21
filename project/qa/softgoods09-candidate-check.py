"""Single-pillow replacement from frozen structure09; no render or global hook."""
import bpy,bmesh,sys,json,hashlib,array,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import furnishing_softgoods as soft
SRC=R/'scene/Fallingwater_structure_candidate09.blend';OUT=R/'scene/Fallingwater_softgoods_candidate09.blend'
TARGET='FW_FURN_MAIN_L3_ALCOVE_single_bed_00_pillow'
COVER='FW_FURN_MAIN_L3_ALCOVE_single_bed_00_woven_bedcover'
MATTRESS='FW_FURN_MAIN_L3_ALCOVE_single_bed_00_mattress'
PLATFORM='FW_FURN_MAIN_L3_ALCOVE_single_bed_00_walnut_platform'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC)=='4fa1fc1f56795a2da88c97bacc9bd3b2a0730d3d085076173425b00addd744a0'
protected={n:sha(R/'scripts'/n) for n in ('main_house.py','furnishings.py')}
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene
def settings():
 return (s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.render.engine,s.cycles.samples,s.cycles.device,s.render.threads,s.render.threads_mode,s.render.filepath,s.frame_current,s.frame_start,s.frame_end,s.camera.name if s.camera else None,s.view_settings.exposure)
original_settings=settings()
def fingerprints():
 out={};shared={}
 for ob in s.objects:
  h=hashlib.sha256(str((tuple(tuple(row) for row in ob.matrix_world),ob.parent.name if ob.parent else None,ob.hide_render,ob.hide_viewport)).encode())
  if ob.type=='MESH':
   ptr=ob.data.as_pointer()
   if ptr not in shared:
    a=array.array('f',[0.])*(len(ob.data.vertices)*3);ob.data.vertices.foreach_get('co',a)
    b=array.array('i',[0])*len(ob.data.loops);ob.data.loops.foreach_get('vertex_index',b)
    shared[ptr]=hashlib.sha256(a.tobytes()+b.tobytes()).digest()
   h.update(shared[ptr])
  h.update(str(tuple(m.name if m else None for m in getattr(ob.data,'materials',[]))).encode())
  h.update(str([(m.name,m.type,getattr(m,'width',None),m.show_viewport,m.show_render) for m in ob.modifiers]).encode())
  if ob.type=='CAMERA':h.update(str((ob.data.lens,ob.data.sensor_width,ob.data.shift_x,ob.data.shift_y)).encode())
  if ob.type=='LIGHT':h.update(str((ob.data.energy,tuple(ob.data.color))).encode())
  out[ob.name]=h.hexdigest()
 return out
def evaluated(ob):
 e=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh()
 loc=[list(v.co) for v in m.vertices];world=[list(e.matrix_world@v.co) for v in m.vertices];faces=[tuple(p.vertices) for p in m.polygons];e.to_mesh_clear()
 return loc,world,faces
def bounds(vv):return [[min(v[k] for v in vv),max(v[k] for v in vv)] for k in range(3)]
before=fingerprints();obj=s.objects[TARGET];oldloc,oldworld,oldfaces=evaluated(obj)
oldbounds=bounds(oldloc);oldworldbounds=bounds(oldworld);matrix=[list(r) for r in obj.matrix_world];localmatrix=[list(r) for r in obj.matrix_local];mats=[m.name for m in obj.data.materials];parent=obj.parent.name
assert abs(obj.matrix_world[2][2]-1)<1e-7 and abs(obj.matrix_world[2][0])+abs(obj.matrix_world[2][1])<1e-7
cl,cw,cf=evaluated(s.objects[COVER]);cover_top=max(v[2] for v in cw)
cover_tree=BVHTree.FromPolygons([Vector(v) for v in cw],cf)
width=oldbounds[0][1]-oldbounds[0][0];depth=oldbounds[1][1]-oldbounds[1][0]
bottom_z=cover_top-obj.matrix_world.translation.z;top_z=oldbounds[2][1]
geo=soft.replace_pillow_mesh(obj,width,depth,bottom_z,top_z)
bpy.context.view_layer.update();after=fingerprints()
assert set(before)==set(after);changed=[n for n in before if before[n]!=after[n]];assert changed==[TARGET]
assert settings()==original_settings
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));bpy.ops.wm.open_mainfile(filepath=str(OUT));s=bpy.context.scene;obj=s.objects[TARGET]
assert settings()==original_settings
loc,world,faces=evaluated(obj);nb=bounds(loc);wb=bounds(world)
repro=max(abs(a[k]-b[k]) for a,b in zip(loc,geo['vertices']) for k in range(3))
pose_unchanged=matrix==[list(r) for r in obj.matrix_world] and localmatrix==[list(r) for r in obj.matrix_local] and parent==obj.parent.name
materials_unchanged=mats==[m.name for m in obj.data.materials]
bm=bmesh.new();bm.from_mesh(obj.data);bm.normal_update()
manifold=all(e.is_manifold and e.is_contiguous for e in bm.edges)
volume=bm.calc_volume(signed=True);zero_faces=sum(f.calc_area()<1e-12 for f in bm.faces)
edges=len(bm.edges);euler=len(bm.verts)-edges+len(bm.faces)
visited=set();components=0
for v in bm.verts:
 if v.index in visited:continue
 components+=1;stack=[v]
 while stack:
  q=stack.pop()
  if q.index in visited:continue
  visited.add(q.index);stack.extend(e.other_vert(q) for e in q.link_edges)
bm.free()
top_face_count=(geo['parameters']['columns']-1)*(geo['parameters']['rows']-1)
top_normals_ok=all(p.normal.z>0 for p in obj.data.polygons[:top_face_count])
bottom_normals_ok=all(p.normal.z<0 for p in obj.data.polygons[top_face_count:2*top_face_count])
mesh_tree=BVHTree.FromPolygons([Vector(v) for v in loc],faces)
# Independent non-neighbour face intersection check; shared-edge/vertex pairs are intentional.
nonlocal_pairs=[]
for a,b in mesh_tree.overlap(mesh_tree):
 if a>=b or set(faces[a])&set(faces[b]):continue
 nonlocal_pairs.append([a,b])
contact=[];underside=[]
for i in geo['groups']['bottom']:
 p=Vector(world[i]);q,n,f,d=cover_tree.ray_cast(p+Vector((0,0,.03)),Vector((0,0,-1)),.15)
 gap=p.z-q.z if q is not None else None
 entry={'vertex':i,'world':list(p),'cover_gap_m':gap,'over_cover':q is not None,'not_penetrating':gap is None or gap>=-2e-6}
 underside.append(entry)
 if i in geo['groups']['contact']:
  contact.append(dict(entry,pass_=gap is not None and abs(gap)<2e-6))
bed_clearances={}
for name in (MATTRESS,PLATFORM):
 _,vv,_=evaluated(s.objects[name]);bed_clearances[name]=min(v[2] for v in world)-max(v[2] for v in vv)
envelope_ok=all(nb[k][0]>=oldbounds[k][0]-2e-6 and nb[k][1]<=oldbounds[k][1]+2e-6 for k in range(3)) and all(wb[k][0]>=oldworldbounds[k][0]-2e-6 and wb[k][1]<=oldworldbounds[k][1]+2e-6 for k in range(3))
counts={'changed_objects':len(changed),'vertices':len(loc),'faces':len(faces),'edges':edges,'connected_components':components,'euler_characteristic':euler,'zero_area_faces':zero_faces,'nonadjacent_intersecting_face_pairs':len(nonlocal_pairs),'flat_contact_vertices':len(contact),'contact_fails':sum(not r['pass_'] for r in contact),'underside_vertices':len(underside),'underside_penetrations':sum(not r['not_penetrating'] for r in underside),'underside_edge_vertices_beyond_cover':sum(not r['over_cover'] for r in underside)}
ok=manifold and volume>0 and euler==2 and components==1 and zero_faces==0 and not nonlocal_pairs and all(r['pass_'] for r in contact) and all(r['not_penetrating'] for r in underside) and envelope_ok and pose_unchanged and materials_unchanged and top_normals_ok and bottom_normals_ok and all(v>0 for v in bed_clearances.values()) and repro<1e-6
report={'status':'PASS_SINGLE_PILLOW_GEOMETRY_VISUAL_NOT_RUN' if ok else 'FAIL_SINGLE_PILLOW_GEOMETRY','source':str(SRC),'source_sha256':sha(SRC),'candidate':str(OUT),'candidate_sha256':sha(OUT),'helper_sha256':sha(R/'scripts/furnishing_softgoods.py'),'protected_sources_unchanged':{n:sha(R/'scripts'/n)==h for n,h in protected.items()},'protected_source_hashes':protected,'target':TARGET,'all_other_objects_identical':all(before[n]==after[n] for n in before if n!=TARGET),'saved_settings_unchanged':settings()==original_settings,'target_pose_unchanged':pose_unchanged,'target_materials_unchanged':materials_unchanged,'target_materials':mats,'original_local_bounds':oldbounds,'new_local_bounds':nb,'original_world_bounds':oldworldbounds,'new_world_bounds':wb,'inside_original_envelope':envelope_ok,'support_world_z':cover_top,'old_bottom_penetration_below_cover_top_m':cover_top-oldworldbounds[2][0],'bed_vertical_clearances_m':bed_clearances,'manifold_and_consistent_winding':manifold,'signed_volume_m3':volume,'top_normals_up':top_normals_ok,'bottom_normals_down':bottom_normals_ok,'source_rebuild_error_m':repro,'counts':counts,'parameters':geo['parameters'],'contact':contact,'underside':underside,'nonadjacent_intersections':nonlocal_pairs,'groups':geo['groups'],'limits':['One Alcove pillow only; production furnishings.py is not hooked or edited.','Cloth and seam shape is restrained C-level approximation, not historic pillow reconstruction.','A central flat contact patch rests on actual evaluated bedcover; some lifted rear edge lies beyond bedcover but above the existing mattress.','Original pillow pose, linen material, bed and all other objects retained. Target primitive-box bevel retired because its replacement shell provides the full shape.','Integrator must inspect the same Alcove_B render before promoting visual quality.']}
assert all(report['protected_sources_unchanged'].values())
(R/'qa/softgoods09-candidate-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(R/'qa/softgoods09-mesh.json').write_text(json.dumps(geo),encoding='utf-8')
print(json.dumps({k:report[k] for k in ('status','candidate_sha256','helper_sha256','counts','new_world_bounds','support_world_z','signed_volume_m3')},indent=2))
