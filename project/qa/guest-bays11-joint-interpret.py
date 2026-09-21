import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'qa/guest-bays11-reopen-and-seat-check.json').read_text(encoding='utf-8'))
p=Path(d['scene11b']);assert hashlib.sha256(p.read_bytes()).hexdigest()==d['scene11b_sha256']
bpy.ops.wm.open_mainfile(filepath=str(p));dep=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects['GUEST_L1_CARPORT_RETAINED_PIER_2_pier_end'].evaluated_get(dep);me=o.to_mesh()
bvh=BVHTree.FromPolygons([o.matrix_world@v.co for v in me.vertices],[tuple(q.vertices) for q in me.polygons]);o.to_mesh_clear()
a=json.loads((R/'qa/guest-bays11-build-check.json').read_text(encoding='utf-8'));v0,v1=map(Vector,a['north_glazing']);axis=(v1-v0).normalized();cross=Vector((-axis.y,axis.x))
rows=[]
for r in d['wall_joint_rays']:
 if r['closed']:continue
 q=Vector(r['joint'])+axis*r['along_m'];stations=[]
 for side in (-.4,0,.4):
  xy=q+cross*side;co,no,face,dist=bvh.ray_cast(Vector((*xy,10.8)),Vector((0,0,-1)),3)
  stations.append({'old_ray_station_m':side,'xy':list(xy),'top_hit':None if co is None else {'point':list(co),'normal':list(no),'face':face}})
 co,no,face,dist=bvh.ray_cast(Vector((*(q-cross*3),r['z'])),Vector((*cross,0)),6)
 rows.append({'original_finite_ray_miss':r,'classification':'BOTH_OLD_RAY_ENDPOINTS_INSIDE_CLOSED_PIER_NOT_A_WALL_HOLE','vertical_inside_volume_probes':stations,'long_transverse_surface_hit':None if co is None else {'point':list(co),'normal':list(no),'face':face},'pass':all(s['top_hit'] and abs(s['top_hit']['point'][2]-10.56)<.001 for s in stations) and co is not None})
assert all(r['pass'] for r in rows)
out={'scene11b_sha256':d['scene11b_sha256'],'original_finite_ray_misses_preserved':len(rows),'interpretations':rows,'all_are_occupied_pier_volume_not_gaps':all(r['pass'] for r in rows),'saved':False,'rendered':False}
(R/'qa/guest-bays11-joint-interpret.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({'interpreted':len(rows),'all_closed':out['all_are_occupied_pier_volume_not_gaps']}))
