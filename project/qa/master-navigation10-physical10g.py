"""Root-authorized one-object C soffit correction; no other physical changes."""
import bpy,sys,json,hashlib,array,collections,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import main_house as mh
import master_detail10 as md
SRC=R/'scene/Fallingwater_master_detail_candidate10f.blend';OUT=R/'scene/Fallingwater_master_detail_candidate10g.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC)=='f7ff5b0ab1317b0d375b884b651497bbc26e573cceebe5a9d15139a9c8e9ba5c';assert not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene
def fp():
 out={};cache={}
 for o in s.objects:
  h=hashlib.sha256(str([list(r) for r in o.matrix_world]).encode())
  if o.type=='MESH':
   k=o.data.as_pointer()
   if k not in cache:
    a=array.array('f',[0.]*(len(o.data.vertices)*3));b=array.array('i',[0]*len(o.data.loops));o.data.vertices.foreach_get('co',a);o.data.loops.foreach_get('vertex_index',b);cache[k]=hashlib.sha256(a.tobytes()+b.tobytes()).digest()
   h.update(cache[k])
  h.update(str([m.name if m else None for m in getattr(o.data,'materials',[])]).encode())
  if o.type=='CAMERA':h.update(str((o.data.lens,o.data.shift_x,o.data.shift_y,o.data.clip_start)).encode())
  if o.type=='LIGHT':h.update(str((o.data.energy,list(o.data.color))).encode())
  out[o.name]=h.hexdigest()
 return out
def settings():return (s.frame_current,s.frame_start,s.frame_end,s.camera.name,s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.view_settings.exposure,s.cycles.samples,s.render.threads,s.render.threads_mode,s.render.filepath)
before=fp();settings0=settings();name='MASTER_DETAIL10_west_connected_soffit';o=s.objects[name]
old=[list(o.matrix_world@v.co) for v in o.data.vertices]
o.data=o.data.copy()
for v in o.data.vertices:
 if abs(v.co.z-4.79)<.0001:v.co.z=4.8468
o.data.update();o['ceiling_identity']='B visible high/low ceiling break; standalone narrow beam form U/C, not survey confirmed'
o['physical_revision']='10g root-authorized C1.98m clear construction assumption; top and XY unchanged'
bpy.context.view_layer.update();after=fp();diff=[n for n in before if before[n]!=after[n]]
assert diff==[name] or sorted(diff)==[name];assert before.keys()==after.keys()
expected=md.mesh_for('SOURCE_REPRO_CHECK',md.rect(326.2,354,417.3,359.6),4.8468,5.005,list(o.data.materials))
error=max((a.co-b.co).length for a,b in zip(o.data.vertices,expected.vertices));assert error<1e-7
bpy.data.meshes.remove(expected)
assert settings()==settings0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));bpy.ops.wm.open_mainfile(filepath=str(OUT));s=bpy.context.scene
assert fp()==after and settings()==settings0
dep=bpy.context.evaluated_depsgraph_get();oldprobe=json.loads((R/'qa/master-navigation10-beam-probe.json').read_text(encoding='utf-8'));rows=[]
for oldrow in oldprobe['failures']:
 xy=mh.xy(oldrow['source_xy']);h,g,gn,gf,go,mat=s.ray_cast(dep,Vector((*xy,2.9268)),Vector((0,0,-1)),distance=.15)
 hh,p,n,f,ob,mat=s.ray_cast(dep,Vector((*xy,2.9568)),Vector((0,0,1)),distance=2.5)
 clear=p.z-g.z if h and hh else None
 rows.append({'source_xy':oldrow['source_xy'],'ground':{'object':go.name if h else None,'point':list(g) if h else None},'up':{'object':ob.name if hh else None,'point':list(p) if hh else None},'old_clear_m':oldrow['clear_height_m'],'new_clear_m':clear,'pass':h and hh and go.name=='MAIN_L2_MASTER_finish' and ob.name==name and abs(g.z-2.8668)<.004 and clear>=1.95 and abs(clear-1.98)<.0001})
o=s.objects[name];verts=[list(o.matrix_world@v.co) for v in o.data.vertices];counts=collections.Counter(tuple(sorted(e)) for f in o.data.polygons for e in f.edge_keys)
report={'status':'FROZEN_SINGLE_C_CEILING_CLEARANCE_CORRECTION_NOT_PHOTO_SHAPE_ACCEPTANCE','source':str(SRC),'source_sha256':sha(SRC),'candidate':str(OUT),'candidate_sha256':sha(OUT),'candidate_bytes':OUT.stat().st_size,'helper_sha256':sha(R/'scripts/master_detail10.py'),'only_changed_object':name,'objects_added_removed':False,'all_other_object_fingerprints_identical':True,'saved_settings_identical':True,'saved_reopen_fingerprints_identical':True,'source_repro_max_vertex_error':error,'old_vertices':old,'new_vertices':verts,'closed_edges_all_two':all(v==2 for v in counts.values()),'rows':rows,'old18FAIL_preserved':'qa/master-navigation10-beam-probe.json','limits':['C1.98m clear construction hypothesis, not measured beam.','Source more strongly supports ceiling level break than an independently confirmed narrow beam box.','No room routes/cameras/adjacency were validated by this one-object physical check.','No render, production hook or other physical change.']}
assert all(r['pass'] for r in rows) and report['closed_edges_all_two']
(R/'qa/master-navigation10-physical10g-freeze.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:report[k] for k in ('status','candidate_sha256','candidate_bytes','helper_sha256','only_changed_object','source_repro_max_vertex_error')},indent=2))
