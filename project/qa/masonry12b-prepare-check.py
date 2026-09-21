"""Reuse the previously passed bounded QA with explicit12b target semantics."""
from pathlib import Path
Q=Path(__file__).resolve().parent
text=(Q/'masonry12-build-check.py').read_text(encoding='utf-8')
text=text.replace('import masonry_tower12 as entry','import masonry_tower12b as entry\nimport masonry_tower12 as base')
text=text.replace("SOURCE=R/'scene/Fallingwater_iteration10.blend';SHA='1e7b17d9c2396513f005724e50788bf834097eedb401b91a7f1030825e2c4ed9'", "SOURCE=R/'scene/Fallingwater_masonry_tower_candidate12a.blend';SHA='b267636a9cbbe297513968f08f3b85930c0302cae1ebb75ed775043250e11a48'")
text=text.replace('Fallingwater_masonry_tower_candidate12a.blend\'\nsha=', 'Fallingwater_masonry_tower_candidate12b.blend\'\nsha=')
text=text.replace("raw=(Q/'integration10-navigation-workspace/data/tour-route.json').read_bytes()", "raw=(Q/'masonry12-frozen-route.json').read_bytes()")
text=text.replace("'masonry12-", "'masonry12b-")
text=text.replace("scripts/masonry_tower12.py", "scripts/masonry_tower12b.py")
text=text.replace('MASONRY12','MASONRY12b')
text=text.replace('entry.TARGETS+entry.GUARDS','entry.LOWER+entry.MODIFIED')
text=text.replace('+list(entry.GUARDS)', '+list(entry.LOWER)')
text=text.replace("newobjects=[s.objects[n] for n in app['added']];new,newowners=audit.world_bvh(newobjects,True)", "newobjects=[s.objects[n] for n in app['added']];new,newowners=audit.world_bvh(newobjects,True)\n changed=[s.objects[n] for n in app['added']+list(entry.MODIFIED)+list(entry.LOWER)];navigation_new,navigation_owners=audit.world_bvh(changed,True)")
text=text.replace("audit.route_regression(route,old,_oldowners,new,newowners)", "audit.route_regression(route,old,_oldowners,navigation_new,navigation_owners)")
text=text.replace('hit,n,ix,d=new.find_nearest(pt)', 'hit,n,ix,d=navigation_new.find_nearest(pt)')
text=text.replace("'owner':newowners[ix]", "'owner':navigation_owners[ix]")
text=text.replace('hit,n,ix,d=new.find_nearest(point)', 'hit,n,ix,d=navigation_new.find_nearest(point)')
text=text.replace("'target':newowners[ix]", "'target':navigation_owners[ix]")
text=text.replace("assert removed==set(entry.TARGETS) and added==set(app['added'])", "assert not removed and added==set(app['added'])")
text=text.replace("assert all(v==after['objects'][n] for n,v in before['objects'].items() if n not in removed)", "assert all(v==after['objects'][n] for n,v in before['objects'].items() if n not in entry.MODIFIED)\n for name in entry.MODIFIED:\n  a=before['objects'][name];b=after['objects'][name]\n  assert all(v==b[k] for k,v in a.items() if k not in ('data_hash','properties')),name\n  assert all(v==b['properties'][k] for k,v in a['properties'].items() if k!='data'),name")
text=text.replace("len(before['objects'])-len(removed)", "len(before['objects'])-len(entry.MODIFIED)")
text=text.replace("'original_shared_meshes_unchanged':True", "'original_shared_meshes_unchanged':True,'only_five_named_object_data_changes':list(entry.MODIFIED)")
# Source12a route filename must remain its actual existing record.
text=text.replace("raw=(Q/'masonry12b-frozen-route.json').read_bytes()", "raw=(Q/'masonry12-frozen-route.json').read_bytes()")
marker=" report['component_checks']=component_checks\n"
addition="""
 # Check actual new high-volume surfaces against every saved neighboring mesh,
 # including vegetation. Clip structural wall triangles above their old top;
 # old lower window/wall contacts are outside this newly extended volume.
 def clip_above(poly,z):
  out=[]
  for a,b in zip(poly,poly[1:]+poly[:1]):
   ina=a.z>=z;inb=b.z>=z
   if ina:out.append(a)
   if ina!=inb:out.append(a+(b-a)*((z-a.z)/(b.z-a.z)))
  return out
 highv=[];highf=[]
 dep=bpy.context.evaluated_depsgraph_get()
 for name in entry.MODIFIED:
  ob=s.objects[name];ev=ob.evaluated_get(dep);mesh=ev.to_mesh();mesh.calc_loop_triangles()
  verts=[ev.matrix_world@v.co for v in mesh.vertices]
  for tri in mesh.loop_triangles:
   polygon=[verts[i] for i in tri.vertices]
   if name.startswith('MAIN_stone_tower_'):polygon=clip_above(polygon,9.4601)
   if len(polygon)<3:continue
   off=len(highv);highv+=polygon
   highf.extend((off,off+i,off+i+1) for i in range(1,len(polygon)-1))
  ev.to_mesh_clear()
 high_tree=BVHTree.FromPolygons(highv,highf,all_triangles=True)
 extended_bounds=[[min(v[i] for v in highv),max(v[i] for v in highv)] for i in range(3)]
 allowed=set(entry.MODIFIED)|set(entry.LOWER)|set(app['added'])
 high_neighbors=[o for o in s.objects if o.type=='MESH' and not o.hide_render and o.name not in allowed and base.overlap(base.bounds(o),extended_bounds)]
 report['extended_volume_actual_neighbors']=[o.name for o in high_neighbors]
 if high_neighbors:
  hb,ho=audit.world_bvh(high_neighbors,True);hits=hb.overlap(high_tree)
  report['extended_volume_intersections']=[ho[a] for a,b in hits[:50]]
  assert not hits,('New high tower hits saved geometry',report['extended_volume_intersections'])
 else:report['extended_volume_intersections']=[]
 lower_delta=[]
 for record in app['changed_vertex_records']:
  ob=s.objects[record['object']]
  ids={v['id'] for v in record['changed_vertices']}
  if record['object'].startswith('MAIN_stone_tower_'):
   assert len(ids)==4
   assert all(abs(v['before'][2]-9.46)<1e-5 for v in record['changed_vertices'])
  for v in record['changed_vertices']:
   actual=ob.matrix_world@ob.data.vertices[v['id']].co
   assert abs(actual.x-v['before'][0])<1e-6 and abs(actual.y-v['before'][1])<1e-6
   assert abs(actual.z-v['before'][2]-app['correction_m'])<2e-6
  lower_delta.append({'object':record['object'],'changed_vertex_count':len(ids),'xy_unchanged':True})
 report['bounded_vertex_change_checks']=lower_delta
 actual_top=entry.top(s.objects['MAIN_chimney_cap'])
 actual_datum=entry.top(s.objects['MAIN_L1_TERRACE_W_finish'])
 report['actual_nominal_anchor']={'upper':actual_top,'lower':actual_datum,'relative':actual_top-actual_datum,'error_m':actual_top-actual_datum-entry.NOMINAL_M}
 assert abs(report['actual_nominal_anchor']['error_m'])<2e-6
 report['legacy_outlets_status']=app['outlet_status']
 report['legacy_cap_plan_status']=app['cap_status']
"""
assert marker in text
text=text.replace(marker,marker+addition)
(Q/'masonry12b-build-check.py').write_text(text,encoding='utf-8')

r=(Q/'masonry12-readback.py').read_text(encoding='utf-8')
r=r.replace('import masonry_tower12 as entry','import masonry_tower12b as entry')
r=r.replace("'masonry12-", "'masonry12b-").replace('scripts/masonry_tower12.py','scripts/masonry_tower12b.py')
(Q/'masonry12b-readback.py').write_text(r,encoding='utf-8')
print('Created two12b QA scripts; originals unchanged')
