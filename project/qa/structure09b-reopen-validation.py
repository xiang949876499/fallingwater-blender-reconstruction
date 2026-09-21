"""Independent frozen09b reopen, evaluated source match and cap-overlap test."""
import bpy, json,sys,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import main_house as mh
from fwlib import poly_prism,collection
SRC=R/'scene/Fallingwater_structure_candidate09.blend';OUT=R/'scene/Fallingwater_structure_candidate09b.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC)=='4fa1fc1f56795a2da88c97bacc9bd3b2a0730d3d085076173425b00addd744a0'
assert sha(OUT)=='852b4f3c50ed7530bbba0f9957e2af4e4717496a4129a9169d17a234c86665a1'
def eval_geo(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh()
 v=[e.matrix_world@p.co for p in m.vertices];f=[tuple(q.vertices) for q in m.polygons];e.to_mesh_clear();return v,f
def cap_grid(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4
 trees={}
 for n in ('MAIN_L1_coat_0','MAIN_L1_coat_1','MAIN_L1_coat_2'):
  v,f=eval_geo(s.objects[n]);trees[n]=BVHTree.FromPolygons(v,f)
 result=[]
 for ix in range(103):
  for iy in range(264):
   p=mh.xy((525.9+(ix+.37)*.1,277.9+(iy+.43)*.1))
   for z,dz in ((.1,1),(2.5,-1)):
    hits=[]
    for n,t in trees.items():
     q,no,face,dist=t.ray_cast(Vector((p[0],p[1],z-dz*.025)),Vector((0,0,dz)),.05)
     if q is not None and abs(q.z-z)<1e-5 and abs(no.z)>.99:hits.append(n)
    result.append(dict(xy=p,z=z,hits=hits))
 return result
before=cap_grid(SRC);after=cap_grid(OUT);s=bpy.context.scene
new_duplicates=[dict(point=a['xy'],z=a['z'],before=b['hits'],after=a['hits']) for b,a in zip(before,after) if len(a['hits'])>1 and len(b['hits'])<2]
match=[]
for rid,z in [('MAIN_L1_LOGGIA',.1),('MAIN_L3_ALCOVE',5.26415)]:
 for suffix,lo,hi in [('_slab',z-.22,z),('_finish',z,z+.022)]:
  name=rid+suffix;old=s.objects[name];tmp=poly_prism('QA09b_source_rebuild',[mh.xy(p) for p in mh.closed_floor_source_polygon(rid)],lo,hi,old.data.materials[0],collection('QA09b_validation_only'))
  bpy.context.view_layer.update();a,af=eval_geo(old);b,bf=eval_geo(tmp);err=max((p-q).length for p,q in zip(a,b))
  match.append(dict(object=name,vertices_same=len(a)==len(b),faces_same=af==bf,max_error_m=err));bpy.data.objects.remove(tmp,do_unlink=True)
old=s.objects['MAIN_L1_coat_1'];tmp=poly_prism('QA09b_source_rebuild',[mh.xy(p) for p in mh.coat_east_source_polygon()],.1,2.5,old.data.materials[0],collection('QA09b_validation_only'))
m=tmp.modifiers.new('Crafted edges','BEVEL');m.width=.007;m.segments=2;m.limit_method='ANGLE'
bpy.context.view_layer.update();a,af=eval_geo(old);b,bf=eval_geo(tmp);err=max((p-q).length for p,q in zip(a,b))
match.append(dict(object=old.name,vertices_same=len(a)==len(b),faces_same=af==bf,max_error_m=err));bpy.data.objects.remove(tmp,do_unlink=True)
bpy.data.collections.remove(bpy.data.collections['QA09b_validation_only']);bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
def cast(p,d):
 h,q,n,f,o,_=s.ray_cast(dg,Vector(p),Vector(d),distance=100)
 return dict(object=o.name if h else None,point=list(q) if h else None,normal=list(n) if h else None)
target=[]
for label,p,z in [('Alcove floor',(433,265),5.28615),('Loggia solid corner',(534.767522972,300.727693806),.122),('Loggia paving',(534,304),.122)]:
 xy=mh.xy(p);target.append(dict(label=label,source_px=p,down=cast((*xy,z+.06),(0,0,-1)),up=cast((*xy,z+.12),(0,0,1))))
r=json.loads((R/'qa/structure09b-candidate-check.json').read_text());counts=r['counts']
assert all(counts[k]==0 for k in ('unique_floor_fails','new_body_hits','stair_fails','threshold_regression_fails'))
assert all(m['vertices_same'] and m['faces_same'] and m['max_error_m']<1e-6 for m in match)
assert not new_duplicates
assert target[0]['down']['object']=='MAIN_L3_ALCOVE_finish'
assert target[1]['down']['object']=='MAIN_L1_coat_1' and target[1]['up']['object']=='MAIN_L1_coat_1'
assert target[1]['up']['normal'][2]>.99
assert target[2]['down']['object']=='MAIN_L1_LOGGIA_finish'
assert all(c['ceiling_unchanged'] for c in r['controls'] if c['label']!='Loggia_corner')
assert all(c['source_opening_preserved'] for c in r['controls'] if c['source_opening_preserved'] is not None)
report=dict(status='PASS_SCOPED_STRUCTURE09B_INDEPENDENT_REOPEN_VISUAL_NOT_RUN',source_sha256=sha(SRC),candidate_sha256=sha(OUT),source_script_sha256=sha(R/'scripts/main_house.py'),evaluated_source_match=match,cap_grid_samples=len(after),previous_duplicate_cap_samples=sum(len(a['hits'])>1 for a in before),candidate_duplicate_cap_samples=sum(len(a['hits'])>1 for a in after),new_duplicate_cap_samples=new_duplicates,actual_reopen_targets=target,initial_assertion_failure_preserved='qa/structure09b-initial-assertion-fail.json/log/py',assertion_correction='Source-classified solid point is no longer a free-ceiling sample; it correctly intersects the solid cap from inside. Other walking/opening ceiling controls stay unchanged.',candidate_not_resaved=True)
(R/'qa/structure09b-reopen-validation.json').write_text(json.dumps(report,indent=2))
r['status']='PASS_SCOPED_STRUCTURE09B_GEOMETRY_VISUAL_NOT_RUN';r['independent_reopen_report']='qa/structure09b-reopen-validation.json';r['source_script_sha256']=report['source_script_sha256'];r['solid_control_classification']=report['assertion_correction']
(R/'qa/structure09b-candidate-check.json').write_text(json.dumps(r,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='actual_reopen_targets'},indent=2))
