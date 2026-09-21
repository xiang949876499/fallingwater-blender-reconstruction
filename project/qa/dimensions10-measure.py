"""Independent, read-only evaluated-mesh probes. No production imports/data writes.

Run with a fresh CPU4 Blender, --scene PATH --sha SHA --output QA.json.
Targets and source-reading qualifications live in dimensions10-source-review.json.
Pixel coordinates below only locate rays; every reported distance uses mesh hits.
"""
import argparse, hashlib, json, sys
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ap=argparse.ArgumentParser();ap.add_argument('--scene',required=True);ap.add_argument('--sha',required=True);ap.add_argument('--output',required=True)
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
p=Path(args.scene);before=hashlib.sha256(p.read_bytes()).hexdigest()
assert before==args.sha,(before,args.sha)
bpy.ops.wm.open_mainfile(filepath=str(p));deps=bpy.context.evaluated_depsgraph_get()
cache={};inventory={}
def read(name):
    if name not in cache:
        ob=bpy.data.objects[name].evaluated_get(deps);me=ob.to_mesh()
        try:
            v=[ob.matrix_world @ x.co for x in me.vertices]
            f=[tuple(x.vertices) for x in me.polygons]
            cache[name]=BVHTree.FromPolygons(v,f,all_triangles=False)
            inventory[name]={'vertices':len(v),'faces':len(f),'locator_bounds_only':[[min(x[i] for x in v),max(x[i] for x in v)] for i in range(3)]}
        finally:ob.to_mesh_clear()
    return cache[name]
def names(prefix):return sorted(x.name for x in bpy.context.scene.objects if x.type=='MESH' and x.name.startswith(prefix))
def ray(prefix,origin,direction,length=50):
    nn=names(prefix) if isinstance(prefix,str) else prefix;d=Vector(direction).normalized();hits=[]
    for name in nn:
        co,no,face,dist=read(name).ray_cast(Vector(origin),d,length)
        if co is not None:hits.append({'object':name,'face':face,'point':list(co),'normal':list(no),'distance_from_origin':dist})
    hit=min(hits,key=lambda h:h['distance_from_origin']) if hits else None
    return {'selectors':nn,'origin':list(origin),'direction':list(d),'max_distance':length,'hit':hit}
def pair(id,a,b,axis,target=None):
    ha,hb=a['hit'],b['hit'];r={'id':id,'ray_a':a,'ray_b':b,'axis':axis,'reference_m':target}
    if ha and hb:
        va,vb=Vector(ha['point']),Vector(hb['point']);value=abs((vb-va).dot(Vector(axis).normalized()))
        r.update(actual_mesh_m=value,signed_error_m=None if target is None else value-target,
                 tolerance_m=None if target is None else max(.02,.005*target),
                 numeric_result='GRAPHICAL_ONLY' if target is None else ('PASS' if abs(value-target)<=max(.02,.005*target) else 'FAIL'))
    else:r.update(actual_mesh_m=None,numeric_result='MISSING_SOURCE_RAY_ENDPOINT')
    return r
rows=[]
# Straight outer faces, clear of rounded corners. Projected distances permit
# distinct stations on the SAME source witness plane, not a component bbox.
rows.append(pair('MAIN10_L2_WEST_TERRACE_X',ray('MAIN_L2_west_parapet_0',(-20,14,3.1),(1,0,0)),ray('MAIN_L2_dressing_shell_middle',(-10,14.0,4.0),(1,0,0)),(1,0,0),8.82015))
rows.append(pair('MAIN10_L2_WEST_TERRACE_Y',ray('MAIN_L2_west_north',(-10,25,3.1),(0,-1,0)),ray('MAIN_L2_west_parapet_1',(-10,8,3.1),(0,1,0)),(0,1,0),5.343525))
rows.append(pair('MAIN10_L2_SOUTH_TERRACE_X',ray('MAIN_L2_south_parapet_0',(-5,0,3.1),(1,0,0)),ray('MAIN_L2_south_parapet_2',(15,0,3.1),(-1,0,0)),(1,0,0),7.75335))
rows.append(pair('MAIN10_L1_SERVICE_OUTER_X',ray('MAIN_L1_servant_wall_0',(-12,15.9,1.4),(1,0,0)),ray('MAIN_L1_kitchen_west_0',(-6,15.9,1.4),(1,0,0)),(1,0,0),3.3274))
# West-looking section: L2 south free lip to the south face of the first
# full-height L1 masonry pier, not the window/low seat closer to the edge.
rows.append(pair('MAIN10_GRAPHICAL_L2_SOUTH_CANTILEVER',ray('MAIN_L2_south_parapet_1',(0,-6,2.70),(0,1,0)),ray('MAIN_L1_south_stone_pier_0',(-.45,1,2.0),(0,1,0)),(0,1,0)))
top=ray('MAIN_L1_south_stone_pier_0',(-.20,4.5666,4),(0,0,-1))
slab=ray('MAIN_L2_TERRACE_S_slab',(-.20,4.5666,1),(0,0,1))
connection={'pier_top':top,'slab_underside':slab,'vertical_gap_m':None}
if top['hit'] and slab['hit']:connection['vertical_gap_m']=slab['hit']['point'][2]-top['hit']['point'][2]
fascia_top=ray('MAIN_L1_south_stone_pier_0',(-.45,4.5666,4),(0,0,-1))
fascia_bottom=ray('MAIN_L2_south_parapet_0',(-.45,4.5666,1),(0,0,1))
connection['adjacent_fascia']={'pier_top':fascia_top,'fascia_underside':fascia_bottom,'vertical_gap_m':None}
if fascia_top['hit'] and fascia_bottom['hit']:connection['adjacent_fascia']['vertical_gap_m']=fascia_bottom['hit']['point'][2]-fascia_top['hit']['point'][2]
# Independent source bay axes, transformed only for locating rays. Each
# paired ray hits the expected masonry face; missing or wrong direction stays negative.
def guest(point,z=9.5):return Vector((3.4+(point[0]-325)*.05256,37.1+(422-point[1])*.05272,z))
bay_specs=[('GUEST10_THEATER_NORTH_BAY',(191.7,126.3),(215.9,167.6),'GUEST_L1_THEATER_DIAGONAL_BACK','GUEST_L1_CARPORT_RETAINED_PIER_2',2.486025),
           ('GUEST10_THEATER_MIDDLE_BAY',(202.4,185.0),(223.4,220.5),'GUEST_L1_CARPORT_RETAINED_PIER_2','GUEST_L1_CARPORT_RETAINED_PIER_1',2.162175)]
for id,pa,pb,sa,sb,target in bay_specs:
    a,b=guest(pa),guest(pb);d=(b-a).normalized();mid=(a+b)*.5
    rr=pair(id,ray(sa,mid,-d,10),ray(sb,mid,d,10),list(d),target)
    rr['source_locator_endpoints_world']=[list(a),list(b)]
    rr['source_direction_normal_dot']=[None if rr[k]['hit'] is None else abs(Vector(rr[k]['hit']['normal']).dot(d)) for k in ('ray_a','ray_b')]
    # Retain actual existing facade relation as a separate diagnostic. It is
    # NOT substituted for the source bay dimension.
    rr['existing_straight_facade_diagnostic']=[ray('GUEST_L1_THEATER_WEST',mid,(-d.y,d.x,0),5),ray('GUEST_L1_THEATER_WEST',mid,(d.y,-d.x,0),5)]
    rows.append(rr)
for prefix in ('GUEST_L1_CARPORT_RETAINED_PIER','GUEST_L1_THEATER_WEST','GUEST_L1_THEATER_DIAGONAL_BACK','MAIN_L1_south_stone_pier','MAIN_L2_TERRACE_S_slab'):
    for name in names(prefix):read(name)
after=hashlib.sha256(p.read_bytes()).hexdigest()
out={'scene':str(p),'scene_sha256':before,'after_sha256':after,'scene_unchanged':before==after,'blender_version':bpy.app.version_string,'rendered':False,'saved_scene':False,'method':'evaluated mesh BVH intersections; bounds are locator-only','measurements':rows,'support_interface':connection,'inventory':inventory}
Path(args.output).write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'rows':[{k:v for k,v in r.items() if k in ('id','actual_mesh_m','signed_error_m','numeric_result')} for r in rows],'support_vertical_gap_m':connection['vertical_gap_m'],'scene_unchanged':out['scene_unchanged']},indent=2))
