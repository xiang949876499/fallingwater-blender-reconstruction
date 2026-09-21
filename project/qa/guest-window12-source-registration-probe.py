"""Read-only saved12a front-window/evaluated masonry section registration."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
SCENE=ROOT/'scene/Fallingwater_guest_bays_candidate12a.blend'
SHA='ebe6748261e9716ea9f9bd07e9137da1955798a7b3356bedc0d6a14d06638548'
assert hashlib.sha256(SCENE.read_bytes()).hexdigest()==SHA
bpy.ops.wm.open_mainfile(filepath=str(SCENE));dg=bpy.context.evaluated_depsgraph_get()
src=json.loads((ROOT/'qa/guest-window12-source-registration-sources.json').read_text(encoding='utf-8'))
prefixes=('GUEST_L1_LOUNGE_FRONT','GUEST_L1_WEST_LOUNGE','GUEST_C10_WEST_LOUNGE_WINDOW','GUEST_C10_FRONT_LOUNGE_EXPOSED_PLINTH','GUEST_C10_WEST_LOUNGE_EXPOSED_PLINTH')
objects={};bvhs={};course_ob=bpy.data.objects['GUEST_LAYERED_SANDSTONE_COURSES']
def bbox(vs):return [[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)]
for ob in bpy.context.scene.objects:
    if ob.type!='MESH' or not (ob.name.startswith(prefixes) or ob==course_ob):continue
    ev=ob.evaluated_get(dg);me=ev.to_mesh();world=[ob.matrix_world@v.co for v in me.vertices]
    faces=[list(p.vertices) for p in me.polygons]
    if ob==course_ob:
        valid={i for i,v in enumerate(world) if 3.25<v.x<10.1 and 35.6<v.y<36.7 and 7.3<v.z<10.7}
        faces=[f for f in faces if all(v in valid for v in f)];used=sorted({v for f in faces for v in f});lut={v:i for i,v in enumerate(used)}
        world=[world[v] for v in used];faces=[[lut[v] for v in f] for f in faces]
        name=ob.name+'[bounded_south_front_region]'
    else:name=ob.name
    if world and faces:
        bvhs[name]=BVHTree.FromPolygons(world,faces,all_triangles=False)
        objects[name]={'evaluated_bounds':bbox(world),'evaluated_vertex_count':len(world),'evaluated_face_count':len(faces),
          'materials':[m.name if m else None for m in ob.data.materials],
          'props':{k:str(ob[k]) for k in ob.keys()},
          'base_world_bounds':bbox([ob.matrix_world@v.co for v in ob.data.vertices]),
          'matrix_world':[list(r) for r in ob.matrix_world]}
        if ob!=course_ob:objects[name]['evaluated_world_vertices']=[list(v) for v in world];objects[name]['evaluated_faces']=faces
    ev.to_mesh_clear()
def cast_only(name,x,z):
    hit,n,face,d=bvhs[name].ray_cast(Vector((x,35.0,z)),Vector((0,1,0)),2)
    return None if hit is None else {'object':name,'evaluated_face_index':face,'position_m':list(hit),'normal':list(n),'from_Y35_distance_m':d}
def front(names,x,z):
    hits=[cast_only(name,x,z) for name in names];hits=[h for h in hits if h]
    return min(hits,key=lambda h:h['position_m'][1]) if hits else None
stone=[n for n in bvhs if n.startswith('GUEST_LAYERED') or (n.startswith('GUEST_L1_LOUNGE_FRONT') and '_steel_window' not in n)]
windows=[n for n in bvhs if n.startswith('GUEST_L1_LOUNGE_FRONT_steel_window')]
modelposts=[]
for i in range(8):
    name='GUEST_L1_LOUNGE_FRONT_steel_window_0_mullion_%d'%i;b=objects[name]['evaluated_bounds'];center=[(a+c)/2 for a,c in b]
    norm=[325+(center[0]-3.4)/.05256,422-(center[1]-37.1)/.05272]
    nearest=min(src['points'],key=lambda p:abs(p['normalized_plan_xy'][0]-norm[0]))
    samples=[]
    for z in (8.5,8.60,8.64,8.67,8.68,8.70,9.0,10.48,10.50):
        hit=front(stone,center[0],z);window=front(windows,center[0],z)
        samples.append({'z':z,'stone_first_hit':hit,'window_first_hit':window,
             'frame_outerY_minus_stone_frontY_m':b[1][0]-hit['position_m'][1] if hit else None})
    modelposts.append({'index':i,'object':name,'evaluated_bounds':b,'center_world_m':center,'center_plan_normalized':norm,
       'nearest_plan_station_in_X_only':nearest['source_id'],'X_difference_to_nearest_source_m':center[0]-nearest['world_plan_xy_m'][0],
       'nearest_note':'Distance diagnostic only; nearest station is NOT an assertedphoto/modelidentity.',
       'crosssections':samples})
# Cores/opening extents taken from their actualevaluated objects, not data enums.
core_names=[n for n in objects if n.startswith('GUEST_L1_LOUNGE_FRONT') and '_steel_window' not in n]
column_match=[]
for k,p in enumerate(src['points']):
    entry=dict(p)
    if k<8:
        # Same index is intentionally labelled oldA10assignment, not accepted.
        old=modelposts[k];entry['old_A10_index_assignment']=old['object'];entry['old_assignment_delta_XY_m']=[old['center_world_m'][j]-p['world_plan_xy_m'][j] for j in range(2)]
        entry['old_assignment_status']='Historical15point file pairedphotoWindex with genericmodelindex; that correspondence is NOT a sourcequalifiedmapping.'
    column_match.append(entry)
out={'scene':str(SCENE),'scene_sha256':SHA,'source_records':src,'objects':objects,'model_posts':modelposts,
 'source_stations_with_old_index_assignment_for_audit':column_match,'front_core_names':core_names,
 'actual_counts':{'front_generic_mullions':8,'front_glass_meshes':sum('_glass_' in n for n in windows),'plan_intermediate_posts':7,'plan_boundary_returns':2,'plan_glazing_intervals':8},
 'measurement_scope':'Actualevaluated12a meshes; course subregion only X3.25..10.1,Y35.6..36.7,Z7.3..10.7; normalsandfaceIDsrefercompactevaluatedprobe meshes. No scene save, no camera projection/fit, no material mutation.'}
(ROOT/'qa/guest-window12-source-registration-probe.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'objects':len(objects),'core_names':core_names,'posts':[{k:p[k] for k in ('index','center_plan_normalized','nearest_plan_station_in_X_only','X_difference_to_nearest_source_m')} for p in modelposts]},indent=2))
assert hashlib.sha256(SCENE.read_bytes()).hexdigest()==SHA
