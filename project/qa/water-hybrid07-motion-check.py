"""Check actual evaluated new water geometry at every short-cache frame; no render."""
import sys,json,hashlib,math
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import hybrid_water as h
import hybrid_motion as hm
import hybrid_impact as hi
bpy.ops.wm.open_mainfile(filepath=str(hm.OUTPUT));scene=bpy.context.scene
scene.render.threads_mode='FIXED';scene.render.threads=4
water=scene.objects['WATER_Hybrid07a_Continuous_River_Branch_Pool'];core=scene.objects['SITE_Core_Continuous_Fractured_Sandstone'];coretree=h.render_bvh(core)
report=json.loads(hm.REPORT.read_text(encoding='utf-8'));me=water.data;me.calc_loop_triangles()
faces=np.array([tuple(t.vertices) for t in me.loop_triangles],dtype=np.int32)
base=np.array([tuple(v.co) for v in me.shape_keys.key_blocks[0].data]);tri0=base[faces]
n0=np.cross(tri0[:,1]-tri0[:,0],tri0[:,2]-tri0[:,0]);areas=np.linalg.norm(n0,axis=1)
fall=np.array([v.value for v in me.attributes['H07_fall'].data]);pond=np.array([v.value for v in me.attributes['H07_pond'].data])
active=np.where((fall>0)|(pond>0))[0];fixed=np.where((fall==0)&(pond==0))[0]
inside_baseline=set()
def penetration(p):
 hit=coretree.find_nearest(Vector(p))
 if hit[3]<.0005 or (Vector(p)-hit[0]).dot(hit[1])>=0:return None
 parity=h.parity(coretree,Vector(p))
 return hit[3] if all(k%2 for k in parity) else None
for i in active:
 if penetration(base[i]) is not None:inside_baseline.add(int(i))
frames=[]
for frame in range(1,37):
 scene.frame_set(frame);bpy.context.view_layer.update();ev=water.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
 verts=np.zeros(len(mesh.vertices)*3,np.float32);mesh.vertices.foreach_get('co',verts);verts=verts.reshape((-1,3)).astype(np.float64);tris=verts[faces]
 normals=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]);length=np.linalg.norm(normals,axis=1)
 cosine=np.sum(n0*normals,axis=1)/np.maximum(areas*length,1e-30)
 valid=areas>1e-9;flip=int(np.sum((cosine<0)&valid));angles=np.degrees(np.arccos(np.clip(cosine[valid],-1,1)))
 stabletris=tris-np.array([0,0,-5]);vol=float(np.sum(np.einsum('ij,ij->i',stabletris[:,0],np.cross(stabletris[:,1],stabletris[:,2])))/6)
 new_inside=[]
 for i in active:
  depth=penetration(verts[i])
  if depth is not None and i not in inside_baseline:new_inside.append({'index':int(i),'depth_m':depth,'point':list(map(float,verts[i]))})
 # Taper outer ring is inactive; checking every fixed vertex is stronger than a few perimeter rays.
 fixed_delta=float(np.max(np.abs(verts[fixed]-base[fixed])))
 active_delta=np.linalg.norm(verts[active]-base[active],axis=1)
 inpond=(pond>0)&(base[:,2]<-5.48)
 localtris=np.any(inpond[faces],axis=1)&valid
 local_angles=np.degrees(np.arccos(np.clip(cosine[localtris],-1,1)))
 info={'frame':frame,'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'signed_volume_m3':vol,
 'topology_counts_match':len(mesh.vertices)==len(base) and len(mesh.polygons)==len(me.polygons),
 'maximum_fixed_join_vertex_displacement_m':fixed_delta,'max_active_displacement_m':float(np.max(active_delta)),
 'flipped_nondegenerate_triangles':flip,'max_normal_angle_deg':float(np.max(angles)),
 'pool_normal_change_deg':h.stats(local_angles.tolist()),'new_core_inside_vertices':len(new_inside),'new_inside_examples':new_inside[:10]}
 frames.append(info);ev.to_mesh_clear();print('HYBRID_FRAME_CHECK',json.dumps(info),flush=True)
domain=scene.objects[hi.DOMAIN]
native=[]
for frame in (1,18,36):
 scene.frame_set(frame);bpy.context.view_layer.update();ev=domain.evaluated_get(bpy.context.evaluated_depsgraph_get())
 native.append({'frame':frame,'systems':[{'type':p.settings.type,'count':len(p.particles),'render_type':p.settings.render_type,
 'instance_materials':[m.name for m in p.settings.instance_object.data.materials] if p.settings.instance_object else []} for p in ev.particle_systems]})
passed=all(f['topology_counts_match'] and f['signed_volume_m3']>0 and f['maximum_fixed_join_vertex_displacement_m']<1e-6 and not f['flipped_nondegenerate_triangles'] and not f['new_core_inside_vertices'] for f in frames)
result={'status':'PASS_36FRAME_GEOMETRY_VISUAL_PENDING' if passed else 'FAIL_36FRAME_GEOMETRY_KEEP_DIAGNOSTIC',
 'source':str(hm.OUTPUT),'sha256':hashlib.sha256(hm.OUTPUT.read_bytes()).hexdigest(),'core_world_geometry_sha256':h.shape_hash(core),
 'base_topology':h.topology(water),'checked_frame_range':[1,36],'new_shape_key_count':len(water.data.shape_keys.key_blocks),
 'old3keys_transferred':False,'active_vertex_count':len(active),'fixed_join_and_external_vertex_count':len(fixed),
 'baseline_active_inside_vertices':len(inside_baseline),'frames':frames,'native_particle_reopen':native,
 'raw_liquid_emitter_mesh_rendered':domain.show_instancer_for_render,
 'foot_camera':list(scene.objects['CAM_WATER_FOOT'].location),
 'limitations':['Sampling all active vertices does not prove all interiors of triangle faces collision-free',
 'Raw pool boundary drift and amplitude mapping/clipping are recorded separately; geometry pass is not physical or visual acceptance',
 '36frames only; no10-second or finalphotoreal claim; rendered sequence NOT_RUN']}
root07=ROOT/'scene/Fallingwater_iteration07.blend'
with bpy.data.libraries.load(str(root07),link=False) as (available,loaded):
 loaded.objects=['SITE_Core_Continuous_Fractured_Sandstone']
imported=loaded.objects[0]
result['frozen_root07_crosscheck']={'scene':str(root07),'scene_sha256':hashlib.sha256(root07.read_bytes()).hexdigest(),
 'root_supplied_sha256':'bf50530009e4a93315915815473188c91d891272ef2d8e9e0169b704bd2e2f16',
 'core_world_geometry_sha256':h.shape_hash(imported),'core_matches_our_frozen_source':h.shape_hash(imported)==h.shape_hash(core)}
bpy.data.objects.remove(imported,do_unlink=True)
h.write(ROOT/'qa/water-hybrid07-motion-check.json',result)
report['geometry_check']=result['status'];report['geometry_check_report']='qa/water-hybrid07-motion-check.json';h.write(hm.REPORT,report)
print('HYBRID_ALLFRAMES_RESULT',result['status'],flush=True)
