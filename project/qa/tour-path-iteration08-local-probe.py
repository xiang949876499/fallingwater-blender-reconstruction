"""Read-only tests of source-supported north landing anchors, not geometry edits."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import tour
scene=bpy.context.scene;rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string());byid={r['id']:r for r in rooms}
probe=tour.Probe(scene,((-7,8),(30,49),(5,15)))
ids=['GUEST_L1_CAR_COURT','GUEST_L1_STAIR_HALL','GUEST_L2_HALL']
candidates={rid:tour.room_candidates(byid[rid],probe,True) for rid in ids}
points=[(x,y,10.0) for x in (2.65,2.78,2.85,2.93,3.02) for y in (41.40,41.24,41.10,40.98,40.84)]
tests=[]
for p in points:
    tests.append({'point':p,'inside':[rid for rid in ids if tour.inside(p,byid[rid]['polygon'])],
                  'failure':probe.point(p,True),'ground':probe.ray((p[0],p[1],8.7),(0,0,-1),.7)})
low=Vector(tour.stair_mesh_points(scene,'GUEST_SERVICE_ASCENT_tread_',False)[0])
before_candidates={rid:[list(p) for p in ps] for rid,ps in candidates.items()}
candidates['GUEST_L1_STAIR_HALL'].append(low)
first=tour.connection(byid[ids[0]],byid[ids[1]],probe,candidates,max_nodes=1800)
second=tour.stair_connection(scene,byid[ids[1]],byid[ids[2]],probe,candidates,'GUEST_SERVICE_ASCENT_tread_')
explicit=[[(2.85,41.24,10.0),(2.85,40.98,10.0),list(low)],[(2.93,41.24,10.0),(2.93,40.98,10.0),list(low)]]
old=probe.step_mode;probe.step_mode=True
paths=[{'points':p,'failure':probe.path(p,True)} for p in explicit];probe.step_mode=old
result={'source':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
    'scope':'No edits; actual tread-anchor tests within original plan passage and current room polygons',
    'existing_candidates':before_candidates,'north_landing_point_tests':tests,'actual_low_tread_anchor':list(low),
    'carcourt_to_hall_with_tread_anchor':first,'hall_to_upper_with_tread_anchor':second,'explicit_approach_tests':paths}
(ROOT/'qa/tour-path-iteration08-local-probe.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('LOCAL_PROBE',json.dumps(result),flush=True)
