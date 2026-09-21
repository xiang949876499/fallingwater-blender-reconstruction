"""Actual scene rays across the guest north landing-to-first-tread gap."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import tour
scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
probe=tour.Probe(scene,((1,4),(40,42),(5,13)));probe.step_mode=True
def bounds(obj):
    pp=[obj.matrix_world@Vector(v) for v in obj.bound_box]
    return [[min(p[k] for p in pp),max(p[k] for p in pp)] for k in range(3)]
def ray(p):
    hit,q,n,i,o,m=scene.ray_cast(deps,Vector(p),Vector((0,0,-1)),distance=3.5)
    return {'object':o.name,'point':list(q),'normal':list(n),'face':i} if hit else None
objects={name:bounds(bpy.data.objects[name]) for name in ('GUEST_L1_HALL_NORTH','GUEST_SERVICE_ASCENT_tread_00','GUEST_LAUNDRY_DESCENT_outer_retaining_wall')}
floor_edge=objects['GUEST_L1_HALL_NORTH'][1][0];tread_edge=objects['GUEST_SERVICE_ASCENT_tread_00'][1][1]
samples=[]
for x in (2.56,2.65,2.75,2.85,2.92696,3.02,3.12,3.22):
    for j in range(11):
        y=tread_edge-.025+j*(floor_edge-tread_edge+.050)/10
        samples.append({'origin':[x,y,8.75],'actual_scene_hit':ray((x,y,8.75))})
source_old=json.loads((ROOT/'qa/tour-path-all-adjacency-iteration07-final.json').read_text(encoding='utf-8'))
old=next(e for e in source_old['edges'] if e['from']=='GUEST_L1_STAIR_HALL' and e['to']=='GUEST_L2_HALL')['approaches'][0]['points']
dense=[]
for i,(a,b) in enumerate(zip(old,old[1:])):
    dense.append({'edge':i,'failure':probe.segment(a,b,True,sample_step=.01)})
real_threshold=[[2.85,41.24,10.0],[2.85,40.98,10.0]]
result={'scene':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
    'object_bounds':objects,'clear_y_gap_m':floor_edge-tread_edge,
    'samples':samples,'old07_approach_points':old,'old07_approach_on08_dense_1cm':dense,
    'real_north_threshold':{'points':real_threshold,'dense_1cm_failure':probe.segment(*real_threshold,True,sample_step=.01)},
    'source_reference':'guest-01-service.png actual car court opening to service stair. North floor ends at drawing y351; first flight begins y354 in current data.',
    'claim':'A failed physical support sample cannot be passed by attaching the room graph directly to the first tread. No geometry or route edited.'}
(ROOT/'qa/tour-path-iteration08-stair-gap-probe.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('GAP_PROBE',json.dumps(result),flush=True)
