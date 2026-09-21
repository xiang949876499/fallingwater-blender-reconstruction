"""One static frame48 diagnostic from real run06. No bake/render/production install."""
import bpy, bmesh, hashlib, json, math, statistics, sys, time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import water_integration as wi
import fluid_water as fw
from fwlib import mesh_object,collection
SOURCE=ROOT/'scene/Fallingwater_iteration06.blend'
OUTPUT=ROOT/'scene/Fallingwater_water_compare06b.blend'
REPORT=ROOT/'qa/water-compare06b.json'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='172b76340d1224a2b98f415b21042d19ad7fba4d849543d7156beb17e5fcf055'
assert not OUTPUT.exists(),'Preserve existing candidate; do not silently overwrite'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene
scene.frame_set(48);scene.render.threads_mode='FIXED';scene.render.threads=8
lip=Vector((2.4,-2.83,0));down=Vector((-.882352948,-.470588356,0));cross=Vector((.470588356,-.882352948,0))
def xy(s,c):return lip+down*s+cross*c
def local(p):return (p-lip).dot(down),(p-lip).dot(cross)
def geometry_hash(o):
 return hashlib.sha256(json.dumps({'v':[list(o.matrix_world@v.co) for v in o.data.vertices],'p':[list(p.vertices) for p in o.data.polygons]},separators=(',',':')).encode()).hexdigest()
def summary(values):
 a=[v for v in values if v is not None]
 return {'count':len(a),'min':min(a) if a else None,'max':max(a) if a else None,'mean':sum(a)/len(a) if a else None}
def top(tree,s,c):
 p=xy(s,c);return tree.ray_cast(Vector((p.x,p.y,0)),Vector((0,0,-1)),10)
def write():fw._write(REPORT,report)
started=time.perf_counter()
surface=scene.objects[wi.SURFACE];core=scene.objects['SITE_Core_Continuous_Fractured_Sandstone']
assert geometry_hash(core)=='eefa8bda5ac8596f6411100a3d559bc49bd8b9fc85bf3ffcf2ca9f04b219fb55'
original_signature=wi._geometry_signature(surface)
original_normals=wi._normal_stats(surface);assert original_normals['downward']==0
program=wi._bvh(surface);rock=wi._bvh(core);points=wi._water_shape_vertices(surface)
loaded=fw.install(scene,ROOT/'scene/Fallingwater_fluid_run06.blend')
domain=next(o for o in loaded.objects if o.name.startswith('WATER_Mantaflow'))
scene.frame_set(48);dg=bpy.context.evaluated_depsgraph_get();dg.update()
settings=next(m.domain_settings for m in domain.modifiers if m.type=='FLUID')
cached_core=next(o for o in settings.effector_group.objects if o.name.startswith('SITE_Core_Continuous'))
assert geometry_hash(cached_core)==geometry_hash(core)
water=wi._bvh(domain)
report={'status':'BUILDING_ONE_STATIC_UNVERIFIED_CANDIDATE','source':str(SOURCE),'frame':48,
 'cache_frame_range':[settings.cache_frame_start,settings.cache_frame_end],
 'cache_source':str(ROOT/'scene/Fallingwater_fluid_run06.blend'),
 'scope':'Static evaluated real-cache mesh and actual secondary particles at frame48 only; no animated seam acceptance',
 'evidence':'C authored contour selection and static cropping; actual liquid and particles from existing run06',
 'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'core_sha256':geometry_hash(core),
 'core_matches_cache':True,'program_normals':original_normals,'production_guard_used':False,
 'future07_use':'INVALID if the planned core rock macrogeometry changes; this candidate is old06 only',
 'front_samples':[],'back_samples':[],'counterexamples':[]}
# Find actual crosswise open edges of the final upstream program row.
edge_counts={}
for face in surface.data.polygons:
 for a,b in zip(face.vertices,list(face.vertices[1:])+[face.vertices[0]]):
  key=tuple(sorted((a,b)));edge_counts[key]=edge_counts.get(key,0)+1
rows={}
for (a,b),count in edge_counts.items():
 if count!=1 or a//31!=b//31:continue
 p=(points[a]+points[b])*.5;s,c=local(p)
 if -.9<s<.9 and -3.16<p.z<-2.94:rows.setdefault(a//31,set()).update((a,b))
assert rows,'No real upstream water edge found'
row=max(rows,key=lambda r:len(rows[r]));edge=sorted((local(points[i])[1],points[i]) for i in rows[row])
def edge_point(c):
 for (ca,a),(cb,b) in zip(edge,edge[1:]):
  if ca<=c<=cb:return a.lerp(b,(c-ca)/(cb-ca))
 return edge[0][1].copy() if c<edge[0][0] else edge[-1][1].copy()
cs=[-4.2+i*8.4/120 for i in range(121)]
front=[];back=[]
for c in cs:
 p=edge_point(c);ps,_=local(p);target=p.z-.003
 candidates=[];last=None
 for j in range(101):
  s=-.41+j*1.11/100;h=top(water,s,c)
  if h[0] is None or not -3.4<h[0].z<-2.7:last=None;continue
  value=h[0].z-target
  if last and last[1]>=0 and value<=0:
   lo,hi=last[0],s
   for _ in range(16):
    mid=(lo+hi)*.5;hh=top(water,mid,c)
    if hh[0] is None or hh[0].z<target:hi=mid
    else:lo=mid
   ss=(lo+hi)*.5;hh=top(water,ss,c)
   if hh[0] is not None and abs(hh[0].z-target)<.005:candidates.append((abs(ss-ps),ss,hh))
  last=(s,value)
 if candidates:
  _,s,h=min(candidates,key=lambda v:v[0]);front.append(s)
  pn=program.find_nearest(h[0]);rn=rock.find_nearest(h[0])
  report['front_samples'].append({'cross_m':c,'along_m':s,'method':'actual free-top root at original lip height minus3mm',
   'original_edge':list(p),'cached_top':list(h[0]),'height_delta_m':h[0].z-p.z,
   'along_gap_from_program_edge_m':s-ps,'edge_endpoint_distance_m':(h[0]-p).length,
   'nearest_program_surface_distance_m':pn[3],
   'normal_angle_deg':math.degrees(h[1].angle(pn[1])) if pn[1] is not None else None,
   'nearest_core_distance_m':rn[3],'root_candidates':len(candidates)})
 else:
  s=.45;front.append(s)
  report['front_samples'].append({'cross_m':c,'along_m':s,'method':'NO_MATCH_crop_only_counterexample',
   'original_edge':list(p),'cached_top':None,'height_delta_m':None,'along_gap_from_program_edge_m':None})
 choices=[]
 for j in range(81):
  s=3.45+j*1.8/80;h=top(water,s,c);p2=top(program,s,c)
  if h[0] is None or p2[0] is None:continue
  if not -6.3<h[0].z<-5.45:continue
  delta=h[0].z-p2[0].z
  choices.append((abs(delta)+.005*abs(s-4.3),s,delta,h,p2))
 if choices:
  _,s,delta,h,p2=min(choices,key=lambda v:v[0]);back.append(s)
  report['back_samples'].append({'cross_m':c,'along_m':s,'height_delta_m':delta,
    'normal_angle_deg':math.degrees(h[1].angle(p2[1])),'cached_top':list(h[0]),'program_top':list(p2[0])})
 else:back.append(4.3);report['back_samples'].append({'cross_m':c,'along_m':4.3,'height_delta_m':None,'method':'NO_MATCH_counterexample'})
report['program_upstream_edge_row']=row
report['front_root_count']=sum(p['cached_top'] is not None for p in report['front_samples'])
report['front_height_error_m']=summary(p['height_delta_m'] for p in report['front_samples'])
report['front_along_gap_m']=summary(p['along_gap_from_program_edge_m'] for p in report['front_samples'])
report['front_normal_angle_deg']=summary(p.get('normal_angle_deg') for p in report['front_samples'])
report['back_height_error_m']=summary(p['height_delta_m'] for p in report['back_samples'])
report['back_normal_angle_deg']=summary(p.get('normal_angle_deg') for p in report['back_samples'])
write();print('CONTOUR_MEASURED',report['front_root_count'],flush=True)
def curve(c,values):
 t=max(0,min(120,(c+4.2)/8.4*120));i=min(119,int(t));return values[i]*(1-(t-i))+values[i+1]*(t-i)
def inside(p):
 s,c=local(p);return -4.2<=c<=4.2 and curve(c,front)<=s<=curve(c,back)
# Preserve the actual cached triangles; one closed variable-front/back crop.
ev=domain.evaluated_get(dg)
particle_snapshots=[]
for ps in ev.particle_systems:
 if ps.settings.type not in {'FOAM','SPRAY'}:continue
 locs=[];sizes=[]
 for p in ps.particles:
  v=p.location.copy()
  if inside(v) and -7<v.z<-2.96:
   locs.append(tuple(v));sizes.append(float(p.size))
 particle_snapshots.append({'type':ps.settings.type,'original_count':len(ps.particles),'locations':locs,'sizes':sizes})
mesh=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=dg)
coll=collection('60_WATER_COMPARE06B_STATIC_UNVERIFIED')
liquid=bpy.data.objects.new('WATER_Run06_Frame048_ContourCrop_UNVERIFIED',mesh);coll.objects.link(liquid)
liquid.matrix_world=domain.matrix_world.copy();liquid['frame48_only']=True
liquid.data.materials.clear();liquid.data.materials.append(surface.data.materials[0])
for f in liquid.data.polygons:f.use_smooth=True
outline=[xy(s,c) for s,c in zip(front,cs)]+[xy(s,c) for s,c in reversed(list(zip(back,cs)))]
verts=[(p.x,p.y,z) for z in (-8,0) for p in outline];n=len(outline)
faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
envelope=mesh_object('WATER_Contour_Envelope_Frame048',verts,faces,None,coll)
bm=bmesh.new();bm.from_mesh(envelope.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(envelope.data);bm.free()
envelope.hide_render=True;envelope.display_type='WIRE'
mod=liquid.modifiers.new('Actual cached mesh intersect contour envelope','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=envelope
fw._select(liquid);bpy.ops.object.modifier_apply(modifier=mod.name)
envelope.hide_set(True);domain.hide_render=True;domain.hide_set(True)
domain['diagnostic_cache_reference_only']=True
for obj in loaded.objects:
 if obj!=domain:obj.hide_render=True;obj.hide_set(True)
dg.update();clipped=wi._bvh(liquid)
report['clipped_mesh']={'vertices':len(liquid.data.vertices),'polygons':len(liquid.data.polygons)}
assert len(liquid.data.vertices)>1000,'Unexpected empty crop'
print('CROP_APPLIED',report['clipped_mesh'],flush=True)
# Only remove faces under actual cropped water at this fixed frame; no vertex/shape-key edits.
bm=bmesh.new();bm.from_mesh(surface.data);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table()
removed=[];boundary={};cut=set()
for f in bm.faces:
 p=sum((points[v.index] for v in f.verts),Vector())/len(f.verts)
 remove=False
 if inside(p):
  s,c=local(p);h=top(clipped,s,c)
  remove=h[0] is not None and -.35<h[0].z-p.z<.6
 for e in f.edges:
  key=tuple(sorted(v.index for v in e.verts))
  if remove:cut.add(key)
  else:boundary[key]=boundary.get(key,0)+1
 if remove:removed.append(f)
bmesh.ops.delete(bm,geom=removed,context='FACES_ONLY');bm.to_mesh(surface.data);bm.free();surface.data.update()
assert wi._geometry_signature(surface)==original_signature,'Unexpected program vertex/key change'
seams=[]
for a,b in cut.intersection(boundary):
 p=(points[a]+points[b])*.5;s,c=local(p);h=top(clipped,s,c);near=clipped.find_nearest(p)
 seams.append({'point':list(p),'along_m':s,'cross_m':c,'nearest_liquid_distance_m':near[3],
  'top_height_delta_m':h[0].z-p.z if h[0] is not None else None})
report['program_removed_faces']=len(removed);report['program_vertices_keys_unchanged']=True
report['seam_samples']=seams;report['seam_nearest_distance_m']=summary(p['nearest_liquid_distance_m'] for p in seams)
report['seam_top_error_m']=summary(p['top_height_delta_m'] for p in seams)
# Sample actual clipped mesh against the unchanged closed core, not against an invented collision proxy.
sampled=[];stride=max(1,len(liquid.data.vertices)//5000)
for v in list(liquid.data.vertices)[::stride]:
 p=liquid.matrix_world@v.co;near=rock.find_nearest(p)
 if near[0] is None:continue
 signed=(p-near[0]).dot(near[1]);sampled.append({'point':list(p),'nearest_core_distance_m':near[3],'signed_normal_distance_m':signed})
penetrations=[q for q in sampled if q['signed_normal_distance_m']<-.002]
report['core_contact_probe']={'method':'Uniform vertex-index sample nearest point / oriented core normal; negative is penetration indication, not exact intersection volume',
 'sample_count':len(sampled),'penetration_over_2mm_count':len(penetrations),
 'signed_distance_m':summary(q['signed_normal_distance_m'] for q in sampled),
 'counterexamples':sorted(penetrations,key=lambda q:q['signed_normal_distance_m'])[:20]}
report['hidden_program_objects']=[]
for o in scene.objects:
 if o.name in {'WATER_Broken_Sandstone_Ledge_Cascades','WATER_Impact_Foam_Rivulets','WATER_Dispersed_Impact_Arcs','WATER_Aerated_Droplets'}:
  o.hide_render=True;o.hide_set(True);report['hidden_program_objects'].append(o.name)
 elif o.name.startswith('WATER_Downstream_Advecting_Foam_'):
  if inside(sum((o.matrix_world@v.co for v in o.data.vertices),Vector())/len(o.data.vertices)):
   o.hide_render=True;o.hide_set(True);report['hidden_program_objects'].append(o.name)
# Actual frame48 secondary particles, compact instanced point meshes; no authored foam traces.
write()
foam_mat=scene.objects['WATER_Impact_Foam_Rivulets'].data.materials[0]
proto_mesh=bpy.data.meshes.new('WATER_ActualParticle_UnitIco');bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=1,radius=1);bm.to_mesh(proto_mesh);bm.free()
proto=bpy.data.objects.new('WATER_ActualParticle_Prototype_HIDDEN',proto_mesh);coll.objects.link(proto);proto.data.materials.append(foam_mat);proto.hide_render=True;proto.hide_set(True)
report['particles']=[]
for snapshot in particle_snapshots:
 locs=snapshot['locations'];sizes=snapshot['sizes']
 obj=mesh_object('WATER_Run06_Actual_'+snapshot['type']+'_Frame048',locs,[],None,coll)
 attr=obj.data.attributes.new(name='actual_radius',type='FLOAT',domain='POINT')
 for val,radius in zip(attr.data,sizes):val.value=radius
 group=bpy.data.node_groups.new(obj.name+'_Instances','GeometryNodeTree')
 group.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
 group.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
 nodes=group.nodes;links=group.links
 gi=nodes.new('NodeGroupInput');go=nodes.new('NodeGroupOutput');inst=nodes.new('GeometryNodeInstanceOnPoints')
 info=nodes.new('GeometryNodeObjectInfo');info.inputs['Object'].default_value=proto;info.transform_space='ORIGINAL'
 rad=nodes.new('GeometryNodeInputNamedAttribute');rad.data_type='FLOAT';rad.inputs['Name'].default_value='actual_radius'
 links.new(gi.outputs['Geometry'],inst.inputs['Points']);links.new(info.outputs['Geometry'],inst.inputs['Instance'])
 links.new(rad.outputs['Attribute'],inst.inputs['Scale']);links.new(inst.outputs['Instances'],go.inputs['Geometry'])
 obj.modifiers.new('Actual cached particle instances','NODES').node_group=group
 report['particles'].append({'type':snapshot['type'],'original_count':snapshot['original_count'],'retained_count':len(locs),'actual_radius_m':summary(sizes),
  'coordinate_note':'Particle.location world coordinates; no scene transform/velocity remapping'})
report['status']='UNVERIFIED_STATIC_DIAGNOSTIC_WITH_RECORDED_CONTACT_ERRORS'
report['acceptance']={'frame48_geometry':'CANDIDATE_NOT_VISUAL_PASS','animated_seams':'NOT_RUN','five_to_ten_seconds':'NOT_RUN','render':'ROOT_SCHEDULED_NOT_RUN_BY_THIS_SCRIPT'}
report['counterexamples']=sorted([q for q in report['front_samples'] if q.get('edge_endpoint_distance_m') is not None],key=lambda q:q['edge_endpoint_distance_m'],reverse=True)[:12]
report['limitations']=['No up-river raise, no connector/filler sheet, no inverse slope authoring. Any positive upstream endpoint gap remains visible and unverified.',
 'Curve chosen independently across width only for frame48. It does not claim fixed or dynamic all-frame matching.',
 'Missing free-top roots use an explicitly unmatched downstream crop at s=.45; these columns are counterexamples, not accepted natural dry rock.',
 'Original cached source/particle system hidden as provenance; displayed liquid and particles are true evaluated frame48 snapshots.',
 'Side boundary c=+-4.2 and nearest downstream-height cuts can leave visible cap/thickness seams; see metrics and actual root renders.',
 'Old06 core only. Changed07 rock invalidates physical reuse of this cache.']
scene.frame_set(48);scene.camera=scene.objects['CAM_HERO'];scene.view_settings.exposure=.8
scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.cycles.samples=64;scene.cycles.device='CPU'
scene['water_compare_status']='UNVERIFIED STATIC FRAME48 ONLY; real run06 cache range1-72; NOT 07-compatible if rock changes'
scene['water_compare_report']='qa/water-compare06b.json'
report['seconds']=time.perf_counter()-started;write()
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
report['output']=str(OUTPUT);report['output_bytes']=OUTPUT.stat().st_size;write()
print('WATER_COMPARE06B_SAVED',json.dumps({k:report[k] for k in ('status','seconds','front_root_count','front_along_gap_m','clipped_mesh','particles','output')}),flush=True)
