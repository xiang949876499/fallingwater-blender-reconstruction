"""Nominal evaluated core vs real projecting course faces; neither is hidden."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));import guest_bays11 as h
a=json.loads((R/'qa/guest-bays11-build-check.json').read_text(encoding='utf-8'));b=json.loads((R/'qa/guest-bays11-reopen-and-seat-check.json').read_text(encoding='utf-8'))
src=Path(b['scene11b']);assert hashlib.sha256(src.read_bytes()).hexdigest()==b['scene11b_sha256']
bpy.ops.wm.open_mainfile(filepath=str(src));dep=bpy.context.evaluated_depsgraph_get();stone=bpy.data.objects[h.COURSES]
def wall(core,blocks):
 ob=bpy.data.objects[core].evaluated_get(dep);me=ob.to_mesh();vs=[ob.matrix_world@v.co for v in me.vertices];fs=[tuple(p.vertices) for p in me.polygons];owners=[core]*len(fs);ob.to_mesh_clear()
 faces=[(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
 for block in blocks:
  off=len(vs);vs.extend(stone.matrix_world@stone.data.vertices[block*8+i].co for i in range(8));fs.extend(tuple(off+i for i in f) for f in faces);owners.extend([h.COURSES+':block'+str(block)]*6)
 return BVHTree.FromPolygons(vs,fs),owners
left=wall('GUEST_L1_THEATER_DIAGONAL_BACK_pier_0',a['course_block_ids']['DIAGONAL_BACK']);right=wall('GUEST_L1_CARPORT_RETAINED_PIER_2_pier_end',a['course_block_ids']['GUEST_L1_CARPORT_RETAINED_PIER_2_pier_end'])
pa,pb=h.p((191.7,126.3)),h.p((215.9,167.6));d=h.xy3((pb-pa).normalized());mid=(pa+pb)/2;rows=[]
for z in (8.8,9.15,9.5,9.85,10.3):
 hits=[]
 for (tree,owners),axis in [(left,-d),(right,d)]:
  co,no,face,dist=tree.ray_cast(h.xy3(mid,z),axis,5);hits.append({'object':owners[face],'point':list(co),'normal':list(no)})
 value=(Vector(hits[1]['point'])-Vector(hits[0]['point'])).dot(d);rows.append({'z':z,'actual_visible_mesh_hits':hits,'span_m':value,'signed_difference_from_printed_nominal_m':value-2.486025})
out={'scene_sha256':b['scene11b_sha256'],'nominal_core_span_m':a['measurements'][0]['actual_evaluated_mesh_m'],'visible_surface_samples':rows,'qualification':'Printed source interpreted nominal masonry boundary. C rough courses project beyond core; actual visible clearance is separately retained and must not be called 2.486m finished-face PASS. Independent dimension qualification remains reviewer-owned.','saved':False,'rendered':False}
(R/'qa/guest-bays11-finished-face-probe.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print([r['span_m'] for r in rows])
