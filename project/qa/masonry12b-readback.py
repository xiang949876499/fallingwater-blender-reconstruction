import bpy,sys,json,hashlib,time
from pathlib import Path
from types import SimpleNamespace
from collections import Counter
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];Q=R/'qa';sys.path[:0]=[str(R/'scripts'),str(Q)]
import masonry_tower12b as entry
import shrub08_auditlib as audit
report=json.loads((Q/'masonry12b-build-check.json').read_text(encoding='utf-8'))
expected=json.loads((Q/'masonry12b-candidate-fingerprint.json').read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();p=Path(report['candidate'])
assert report['status']=='PASS_PHYSICAL_CANDIDATE_NOT_VISUALLY_ACCEPTED' and sha(p)==report['candidate_sha256']
assert sha(R/'scripts/masonry_tower12b.py')==report['helper_sha256']
start=time.monotonic();bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.scene.frame_set(48)
vs=[];fs=[];owners=[];oriented_bad=[]
for name,components in report['application']['components'].items():
 obj=bpy.context.scene.objects[name]
 for comp in components:
  lo=comp['vertex_start'];hi=lo+comp['vertex_count'];off=len(vs)
  vv=[obj.matrix_world@v.co for v in list(obj.data.vertices)[lo:hi]]
  ff=[tuple(i-lo for i in poly.vertices) for poly in list(obj.data.polygons)[comp['face_start']:comp['face_start']+comp['face_count']]]
  directed=Counter((a,b) for f in ff for a,b in zip(f,f[1:]+f[:1]))
  if any(directed[b,a]!=count for (a,b),count in directed.items()):oriented_bad.append(comp['id'])
  vs+=vv;fs.extend(tuple(off+i for i in f) for f in ff);owners += [name+comp['id']]*len(ff)
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True)
self_cross=[(a,b) for a,b in tree.overlap(tree) if a<b and (owners[a]!=owners[b] or not set(fs[a])&set(fs[b]))]
assert not oriented_bad and not self_cross
before=audit.snapshot();assert audit.digest(before)==expected['snapshot_sha256']
modified_closed=[]
dep=bpy.context.evaluated_depsgraph_get()
for name in entry.MODIFIED:
 obj=bpy.context.scene.objects[name];evaluated=obj.evaluated_get(dep);mesh=evaluated.to_mesh();mesh.calc_loop_triangles()
 vv=[evaluated.matrix_world@v.co for v in mesh.vertices]
 ff=[tuple(t.vertices) for t in mesh.loop_triangles]
 directed=Counter((a,b) for f in ff for a,b in zip(f,f[1:]+f[:1]))
 bad=[(a,b) for (a,b),count in directed.items() if count!=1 or directed[b,a]!=1]
 areas=[(vv[b]-vv[a]).cross(vv[c]-vv[a]).length*.5 for a,b,c in ff]
 volume=sum(vv[a].dot(vv[b].cross(vv[c]))/6 for a,b,c in ff)
 tree=BVHTree.FromPolygons(vv,ff,all_triangles=True)
 self_intersection=[(a,b) for a,b in tree.overlap(tree) if a<b and not set(ff[a])&set(ff[b])]
 assert not bad and not self_intersection and min(areas)>1e-10 and volume>1e-9,(name,bad,self_intersection)
 modified_closed.append({'object':name,'evaluated_triangles':len(ff),'bad_oriented_edges':len(bad),'nonadjacent_self_intersections':len(self_intersection),'minimum_triangle_area_m2':min(areas),'signed_volume_m3':volume})
 evaluated.to_mesh_clear()
assert all(audit.physical_hash(bpy.context.scene.objects[n])==h for n,h in report['protected_physics'].items())
repeat=entry.build(SimpleNamespace(root=R));assert repeat['status']=='SKIPPED_ALREADY_APPLIED'
after=audit.snapshot();assert before==after
out={'status':'PASS_FRESH_PROCESS_EXACT_REOPEN','candidate':str(p),'candidate_sha256':sha(p),'physical_comparison_frame':48,
     'snapshot_exact':True,'repeat_no_mutation':True,'repeat':repeat,'protected_geometry_count':len(report['protected_physics']),
     'camera_count':sum(o.type=='CAMERA' for o in bpy.context.scene.objects),'source_unchanged':sha(Path(report['source']))==report['source_sha256'],
     'helper_sha256':report['helper_sha256'],'rendered':False,'saved':False,'seconds':time.monotonic()-start}
out['oriented_edge_mismatch_components']=oriented_bad;out['nonadjacent_self_or_cross_component_intersections']=self_cross
out['five_modified_evaluated_meshes_closed']=modified_closed
(Q/'masonry12b-readback.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
