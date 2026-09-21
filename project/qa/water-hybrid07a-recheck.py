"""Read-only contact check on the saved prototype using exact render triangles."""
import sys,json,hashlib,time
from pathlib import Path
import bpy
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import hybrid_water as h
import water_integration as wi
scene_path=ROOT/'scene/Fallingwater_water_hybrid07a.blend'
bpy.ops.wm.open_mainfile(filepath=str(scene_path));bpy.context.scene.frame_set(48)
branch=bpy.data.objects['WATER_Hybrid07a_Closed_Branch'];branch.hide_set(False)
core=bpy.data.objects['SITE_Core_Continuous_Fractured_Sandstone'];bpy.context.view_layer.update()
def render_tree(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles()
 verts=[o.matrix_world@v.co for v in me.vertices];faces=[tuple(t.vertices) for t in me.loop_triangles]
 tree=BVHTree.FromPolygons(verts,faces,all_triangles=True);ev.to_mesh_clear();return tree,verts,faces
tree,rv,rf=render_tree(core);oldtree=wi._bvh(core)
bt,bv,bf=render_tree(branch)
samples=[('vertex',i,p) for i,p in enumerate(bv)]+[('triangle_centroid',i,sum((bv[v] for v in f),bv[f[0]]*0)/3) for i,f in enumerate(bf)]
inside=[];uncertain=[];near=[];normals=[]
for typ,i,p in samples:
 hit=tree.find_nearest(p)
 if hit[3]<.01:near.append(hit[3])
 if hit[3]<.0005 or (p-hit[0]).dot(hit[1])>=0:continue
 counts=h.parity(tree,p)
 record={'type':typ,'index':i,'point':list(p),'depth_m':hit[3],'crossing_counts':counts}
 if all(c%2 for c in counts):inside.append(record)
 elif any(c%2 for c in counts):uncertain.append(record)
previous=json.loads((ROOT/'qa/water-hybrid07a-geometry.json').read_text(encoding='utf-8'))
counterexamples=[]
from mathutils import Vector
for p in previous['new_branch_rock_check']['inside_examples']:
 v=Vector(p['point']);hit=tree.find_nearest(v);old=oldtree.find_nearest(v)
 counterexamples.append({'point':list(v),'previous_polygon_bvh_depth_m':old[3],'render_triangle_distance_m':hit[3],
 'render_triangle_parity':h.parity(tree,v),'render_normal_projection_m':(v-hit[0]).dot(hit[1])})
continuous=bpy.data.objects['WATER_Hybrid07a_Continuous_River_Branch_Pool'];original=bpy.data.objects[wi.SURFACE]
original.hide_set(False);bpy.context.view_layer.update()
program=h.render_bvh(original);union=h.render_bvh(continuous)
joins=[]
for i in range(31):
 s=-.8+.6*i/30
 for j in range(41):
  c=-2+1.2*j/40;p=h.point(s,c,0);down=Vector((0,0,-1))
  a=program.ray_cast(p,down,10);b=union.ray_cast(p,down,10)
  if a[0] is None or b[0] is None:continue
  joins.append({'s':s,'c':c,'original_top_m':a[0].z,'new_top_m':b[0].z,'delta_m':b[0].z-a[0].z,
   'normal_angle_deg':__import__('math').degrees(a[1].angle(b[1]))})
unchanged=[p for p in joins if abs(p['delta_m'])<.0005]
raised=[p for p in joins if p['delta_m']>.0005]
thinner=[p for p in joins if p['delta_m']<-.0005]
join_report={'window':'s[-0.8,-0.2],c[-2,-0.8];31x41vertical rays; actual render triangles of evaluated source and union',
 'matching_rays':len(joins),'unchanged_within0_5mm':len(unchanged),'locally_raised_count':len(raised),'lowered_count':len(thinner),
 'top_delta_m':h.stats(p['delta_m'] for p in joins),'normal_angle_deg':h.stats(p['normal_angle_deg'] for p in joins),
 'largest_deltas':sorted(joins,key=lambda p:abs(p['delta_m']),reverse=True)[:12],
 'interpretation':'Original source surface and its keys are untouched; any positive union delta here is a local authored branch crest, not a global upstream head change'}
report={'source':str(scene_path),'sha256':hashlib.sha256(scene_path.read_bytes()).hexdigest(),'frame':bpy.context.scene.frame_current,
 'core_world_geometry_sha256':h.shape_hash(core),'method':'Exact evaluated render loop_triangles for both rock and water; all branch vertices and all rendered triangle centroids; parity for negative nearest normal;0.5mm contact tolerance',
 'sample_count':len(samples),'branch_triangles':len(bf),'core_triangles':len(rf),'confirmed_inside_count':len(inside),'uncertain_count':len(uncertain),
 'inside_examples':inside[:30],'uncertain_examples':uncertain[:30],'contact_distance_within1cm_m':h.stats(near),
 'prior_test_counterexamples':counterexamples,'continuous_topology':h.topology(continuous),'branch_topology':h.topology(branch),
 'visible_water':{'continuous_hide_render':continuous.hide_render,'continuous_hide_viewport':continuous.hide_get(),'old_surface_hide_render':original.hide_render},
 'status':'PASS_RENDER_TRIANGLE_CONTACT_CHECK' if not inside and not uncertain else 'FAIL_OR_UNRESOLVED_RENDER_TRIANGLE_CONTACT',
 'limitations':'Vertex and triangle-centroid sampling does not prove every point of every triangle is outside; no rendered visual review or animation pass',
 'candidate_modified':False,'render_started':False,'bake_started':False}
report['actual_upstream_join']=join_report
if '--stamp-status' in sys.argv:
 assert not inside and not uncertain
 assert not h.topology(continuous)['nonmanifold_edges']
 previous['superseded_polygon_bvh_contact_check']=previous['new_branch_rock_check']
 previous['new_branch_rock_check']={'method':report['method'],'sample_count':len(samples),
 'confirmed_inside_count':len(inside),'uncertain_count':len(uncertain),'actual_render_triangle_recheck':'qa/water-hybrid07a-recheck.json'}
 previous['actual_upstream_join']=join_report
 previous['status']='PASS_STATIC_SPATIAL_GEOMETRY_VISUAL_PENDING'
 previous['render_triangle_check_correction']='Previous3submillimeter indications lie on rendered rock triangles; raw counterexamples retained in superseded field and recheck'
 continuous['status']=previous['status'];bpy.context.scene['hybrid_water_status']=previous['status']
 original.hide_set(True);branch.hide_set(True)
 bpy.ops.wm.save_as_mainfile(filepath=str(scene_path))
 previous['output_sha256']=hashlib.sha256(scene_path.read_bytes()).hexdigest()
 h.write(ROOT/'qa/water-hybrid07a-geometry.json',previous)
 report['pre_metadata_stamp_sha256']=report['sha256'];report['sha256']=previous['output_sha256']
 report['candidate_modified']='Status metadata only; source and all prototype mesh coordinates unchanged'
h.write(ROOT/'qa/water-hybrid07a-recheck.json',report)
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
