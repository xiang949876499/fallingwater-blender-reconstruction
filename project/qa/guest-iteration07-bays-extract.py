import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path('D:/zx/test/project');src=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else root/'scene/Fallingwater_iteration06.blend'
bpy.ops.wm.open_mainfile(filepath=str(src));d=json.loads((root/'data/guest_house.json').read_text(encoding='utf8'));r=d['registration'];sx,sy=r['meters_per_pixel'];ox,oy=r['origin_px'];wx,wy,gz=r['world_origin']
def P(p):return Vector((wx+(p[0]-ox)*sx,wy+(oy-p[1])*sy,gz+.95))
names=['GUEST_L1_THEATER_DIAGONAL_BACK','GUEST_L1_CARPORT_RETAINED_PIER_2','GUEST_L1_CARPORT_RETAINED_PIER_1','GUEST_L1_CARPORT_RETAINED_PIER_0']
meshes={};lines=[];deps=bpy.context.evaluated_depsgraph_get()
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not any(o.name.startswith(n) for n in names+['GUEST_L1_THEATER_WEST']):continue
 if any(q in o.name for q in ['steel_window','leaf','handle','jamb','door_head']):continue
 ev=o.evaluated_get(deps);m=ev.to_mesh();v=[o.matrix_world@t.co for t in m.vertices]
 if v and m.polygons:
  meshes[o.name]=BVHTree.FromPolygons(v,[tuple(f.vertices) for f in m.polygons],all_triangles=False)
  lines.append({'object':o.name,'edges_world':[[list(v[e.vertices[0]]),list(v[e.vertices[1]])] for e in m.edges]})
 ev.to_mesh_clear()
srcdata=json.loads((root/'qa/dimension-source-gap-iteration07.json').read_text(encoding='utf8'))
records=[]
for i,c in enumerate(srcdata['candidates'][:3]):
 a,b=[P(q) for q in c['dimension_tick_points_normalized_px_approx']];axis=(b-a).normalized()
 # Same source bay plane moved inward from the parallel external dimension line;
 # known wall faces rather than glass or programmable opening width are hit.
 transverse=Vector((-axis.y,axis.x,0));origin=(a+b)/2+transverse*.22
 hits=[]
 for side,prefix in [(-1,names[i]),(1,names[i+1])]:
  options=[]
  for n,bvh in meshes.items():
   if not n.startswith(prefix):continue
   loc,normal,face,dist=bvh.ray_cast(origin,axis*side,8)
   if loc is not None:options.append((dist,n,loc,normal,face))
  if options:
   dist,n,loc,normal,face=min(options,key=lambda x:x[0]);hits.append({'object':n,'xyz':list(loc),'normal':list(normal),'face_index':face,'distance':dist})
  else:hits.append(None)
 value=(Vector(hits[1]['xyz'])-Vector(hits[0]['xyz'])).dot(axis) if all(hits) else None
 records.append({'id':c['id'],'source_label':c['printed_label'],'target_m':c['reference_m'],'axis_world':list(axis),'ray_origin':list(origin),'source_plane_inset_m':.22,'endpoints':hits,'actual_m':value,'delta_m':value-c['reference_m'] if value is not None else None,'initial_numeric_comparison':('PASS' if abs(value-c['reference_m'])<=.02 else 'FAIL') if value is not None else 'NOT_RUN','status':'DIAGNOSTIC_ONLY' if value is not None else 'NOT_RUN','standard_result':'NOT_RUN','endpoint_mapping_confidence':'UNRESOLVED_AT_SOUTH_JAMB_DETAIL'})
kind='candidate' if 'candidate' in src.name else 'baseline'
report={'scene':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'records':records,'method':'Actual evaluated stone mesh opposed rays parallel to original printed bay dimension line; not glazing-width substitution. .22m transverse locator is C and must lie within both end reveal polygons.','standard_result':'NOT_RUN_SOURCE_TO_MESH_ENDPOINT_IDENTITY_UNRESOLVED','correction':'Numeric mesh distance is real for selected faces. End witness may refer to jamb/rebate at inner pier end; coarse stone faces are not yet demonstrated to represent printed endpoints. Do not promote numeric comparison to a standard dimension FAIL/PASS.'}
(root/f'qa/guest-iteration07-bays-{kind}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
(root/f'qa/guest-iteration07-bays-{kind}-edges.json').write_text(json.dumps(lines),encoding='utf8')
print(json.dumps(report))
