"""Read-only independent bath10b mesh/route/interface audit. No render/save/import of candidate helper."""
from pathlib import Path
import bpy,bmesh,json,hashlib,math,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'scene/Fallingwater_master_bath_candidate10d.blend'
FOLLOWUP='--followup' in sys.argv or '--followup2' in sys.argv
SUFFIX='followup2' if '--followup2' in sys.argv else 'followup' if FOLLOWUP else 'audit'
OUT=ROOT/('qa/master-bath-detail10-independent-d-seams.json' if '--seams' in sys.argv else 'qa/master-bath-detail10-independent-d-audit.json')
EXPECTED='2c7e8259b24936caad76979b985af86e5360548162cba3d666a9c7bd2b9dcca5'
assert not OUT.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=sha(SOURCE);assert before==EXPECTED
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
bpy.context.scene.render.threads_mode='FIXED';bpy.context.scene.render.threads=4
deps=bpy.context.evaluated_depsgraph_get()
verts=[];polys=[];owners=[];face_materials=[];inventory=[];trees={}
for ob in bpy.context.scene.objects:
    if ob.type not in ('MESH','CURVE') or ob.name.startswith(('QA_','REF_')):continue
    corners=[ob.matrix_world@Vector(p) for p in ob.bound_box]
    if any(max(p[k] for p in corners)<lo or min(p[k] for p in corners)>hi
           for k,(lo,hi) in enumerate(((3.8,7.6),(6.3,10.6),(2.5,5.2)))):continue
    ev=ob.evaluated_get(deps);mesh=ev.to_mesh()
    vv=[ob.matrix_world@v.co for v in mesh.vertices]
    ff=[tuple(f.vertices) for f in mesh.polygons]
    if not vv:ev.to_mesh_clear();continue
    trees[ob.name]=BVHTree.FromPolygons(vv,ff,epsilon=0)
    base=len(verts);verts.extend(vv)
    polys.extend(tuple(base+i for i in f) for f in ff);owners.extend([ob.name]*len(ff))
    face_materials.extend(mesh.materials[f.material_index].name if len(mesh.materials)>f.material_index and mesh.materials[f.material_index] else None for f in mesh.polygons)
    bounds=[[min(v[k] for v in vv),max(v[k] for v in vv)] for k in range(3)]
    row={'name':ob.name,'world_bounds':bounds,'hide_render':ob.hide_render,
         'materials':[m.name if m else None for m in mesh.materials]}
    if ob.name.startswith('MASTER_BATH10_') or ob.get('room_id')=='MAIN_L2_BATH_M' or 'bath_master' in ob.name or 'threshold_master_bath' in ob.name:
        bm=bmesh.new();bm.from_mesh(mesh)
        row['evaluated_mesh']={'boundary_edges':sum(e.is_boundary for e in bm.edges),
          'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
          'zero_area_faces':sum(f.calc_area()<1e-12 for f in bm.faces),
          'signed_volume':bm.calc_volume(signed=True)}
        bm.free()
    inventory.append(row);ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(verts,polys,epsilon=0)

def ray(p,d,dist=3):
    co,no,ix,dd=bvh.ray_cast(Vector(p),Vector(d),dist)
    return {'object':owners[ix],'material':face_materials[ix],'point':list(co),'normal':list(no),'distance':dd} if co is not None else None

def xyz(x,y,z=2.8668):return Vector(((x-327)*.0524,(540-y)*.0531,z))
def line_samples(points,spacing=.025):
    result=[]
    for a,b in zip(points,points[1:]):
        n=max(1,math.ceil((b-a).length/spacing))
        result.extend(a+(b-a)*i/n for i in range(n))
    result.append(points[-1]);return result

# These routes are chosen from the source-plan entrance, room clear floor and
# actual fixture identities, independently of the helper's published probe path.
# 35mm shower pan is a real step. Ground is measured first; no upper slab omitted.
routes={
 'SOURCE_DOOR_TO_CLEAR_CENTER':[(408,397.5),(416,397.5),(430,397.5),(443,397.5),(443,387)],
 'CENTER_TO_WC_CLEAR_APPROACH':[(443,387),(443,386),(436,386),(436,370),(432,369)],
 'CENTER_TO_BASIN_FRONT':[(443,387),(451.3,387),(451.3,394.8)],
 'CENTER_TO_SHOWER_PRESTEP':[(443,387),(453.335878,383),(453.335878,374.086629)],
}
if FOLLOWUP:
    # Route correction only: retain the original failed diagonal toward the WC.
    # The west lane keeps the full body clear of the inherited low light guard,
    # then stops before the WC fixture rather than walking into its closed lid.
    routes={'CENTER_TO_WC_CLEAR_APPROACH':[(443,387),(436,387),(436,370),(432,369)]}
if '--followup2' in sys.argv:
    # Followup1 located the projecting open-door pull; route moves53.1mm north
    # before crossing west. No real object, radius or head height is changed.
    routes={'CENTER_TO_WC_CLEAR_APPROACH':[(443,387),(443,386),(436,386),(436,370),(432,369)]}
route_rows=[]
for name,source_points in routes.items():
    points=[xyz(*p) for p in source_points];samples=line_samples(points)
    errors=[];records=[];min_overhead=999
    for index,p in enumerate(samples):
        ground=ray(p+Vector((0,0,.205)),(0,0,-1),.25)
        allowed=[2.8668,2.9018] if name=='CENTER_TO_SHOWER' else [2.8668]
        if not ground or min(abs(ground['point'][2]-z) for z in allowed)>.004 or ground['normal'][2]<.90:
            errors.append({'sample':index,'kind':'GROUND_CENTER_4MM','point':list(p),'hit':ground});continue
        p.z=ground['point'][2]
        for j in range(9):
            angle=j*math.tau/8;rad=0 if j==8 else .10
            g=ray(p+Vector((rad*math.cos(angle),rad*math.sin(angle),.205)),(0,0,-1),.25)
            # At a35mm physical riser foot support on either neighboring tread is valid.
            if not g or min(abs(g['point'][2]-z) for z in allowed)>.004 or g['normal'][2]<.90:
                errors.append({'sample':index,'kind':'FOOT_SUPPORT_4MM','point':list(p),'hit':g});break
        for j in range(33):
            angle=j*math.tau/32;rad=0 if j==32 else .18
            h=ray(p+Vector((rad*math.cos(angle),rad*math.sin(angle),.045)),(0,0,1),2.5)
            if h:
                overhead=h['point'][2]-p.z;min_overhead=min(min_overhead,overhead)
                if overhead<1.95-1e-6:
                    errors.append({'sample':index,'kind':'BODY_HEAD_1_95','point':list(p),'hit':h});break
        # Independent horizontal radial casts catch lateral shell intersections
        # that parallel vertical rays could miss. Same180mm body, not a point camera.
        for iz in range(39):
            z=.05+iz*.05
            for j in range(16):
                d=(math.cos(j*math.tau/16),math.sin(j*math.tau/16),0)
                h=ray(p+Vector((0,0,z)),d,.18)
                if h:
                    errors.append({'sample':index,'kind':'HORIZONTAL_BODY_180MM','point':list(p),'height':z,'hit':h});break
            else:continue
            break
        records.append({'sample':index,'feet':list(p),'ground_object':ground['object']})
    route_rows.append({'id':name,'source_plan_waypoints':source_points,'samples':len(samples),
       'status':'PASS' if not errors else 'FAIL','minimum_vertical_clearance_m':min_overhead,
       'issues':errors,'ground_records':records})

probes=[]
def probe(name,p,d,dist=3):
    probes.append({'id':name,'origin':list(p),'direction':list(d),'hit':ray(p,d,dist)})
for py in (406,407.5,409.5,411.0):
    for z in (3.4,4.0,4.75):probe('SOURCE_WEST_RETURN_WINDOW_'+str((py,z)),xyz(433,py,z),(-1,0,0),1.5)
for py in (394,398,405):
    for z in (3.1,4.0,4.95):probe('EAST_WALL_MIRROR_FINISH_'+str((py,z)),xyz(450,py,z),(1,0,0),1.3)
for px in (424,428,434,445,458,462):
    for py in (350.6,352,395,411.4):probe('CEILING_JOINT_'+str((px,py)),xyz(px,py,4.85),(0,0,1),.3)
for px in (429,435,443,451,458):
    for z in (3.75,4.2,4.85):probe('SOUTH_GLAZING_'+str((px,z)),xyz(px,405,z),(0,-1,0),1.5)
for z in (3.1,4.2,4.8):probe('OLD_FALSE_DOOR_CLOSED_'+str(z),xyz(414,375,z),(1,0,0),1.2)
for z in (3.1,4.2,4.8):probe('REAL_DOOR_MIDLINE_'+str(z),xyz(414,397.5,z),(1,0,0),1.5)
probe('DOOR_THRESHOLD_HEAD',xyz(420,397.5,2.8768),(0,0,1),2.5)
for p in ((5.25,7.10,4.99),(5.26,9.98,4.99),(7.11,9.96,4.99)):
    probe('EDGE_CEILING_'+str(p),p,(0,0,1),.1)
if '--seams' in sys.argv:
    for x in (4.988,4.999,5.003,5.008,5.013,5.017,5.028):
        for z in (3.75,4.0,4.40,4.80,4.95):
            probe('SOUTHWEST_CORNER_JOINT_'+str((x,z)),(x,6.95,z),(0,-1,0),.45)
    for y in (7.10,6.85):
        for x in (5.008,5.04):
            probe('RETURN_HEAD_CEILING_'+str((x,y)),(x,y,4.95),(0,0,1),.15)

# Actual rim/recess readback, not constructor profile expectations.
basin=[]
for sx in range(-5,6):
    for sy in range(-3,4):
        p=xyz(451.3,407.0,4.0)+Vector((sx*.048,sy*.048,0))
        basin.append({'xy':list(p)[:2],'hit':ray(p,(0,0,-1),1.0)})

step_errors=[];step_records=[];step_clearance=999.0
floor_z=2.8668;pan_z=2.9018
foot_offsets=[(x,y) for x in (-.040,0,.040) for y in (-.115,0,.115)]
def check_stance(center,label,phase):
    for ox,oy in foot_offsets:
        p=Vector(center)+Vector((ox,oy,.205));h=ray(p,(0,0,-1),.215)
        if not h or abs(h['point'][2]-center[2])>.004 or h['normal'][2]<.90:
            step_errors.append({'phase':phase,'foot':label,'kind':'STANCE_HEEL_FOREFOOT_4MM_NORMAL_0_9','point':list(p),'hit':h})
        step_records.append({'phase':phase,'foot':label,'kind':'stance_contact','origin':list(p),'hit':h})
def check_body(p,phase):
    global step_clearance
    for j in range(33):
        a=j*math.tau/32;r=0 if j==32 else .18
        h=ray(p+Vector((r*math.cos(a),r*math.sin(a),.045)),(0,0,1),2.5)
        if h:
            clear=h['point'][2]-p.z;step_clearance=min(step_clearance,clear)
            if clear<1.95-1e-6:step_errors.append({'phase':phase,'kind':'BODY_HEAD_1_95','point':list(p),'hit':h})
    for iz in range(39):
        for j in range(16):
            h=ray(p+Vector((0,0,.05+iz*.05)),(math.cos(j*math.tau/16),math.sin(j*math.tau/16),0),.18)
            if h:step_errors.append({'phase':phase,'kind':'BODY_180MM','point':list(p),'hit':h})

# Explicit two-foot step: 80mm wide/230mm long footprints are C QA choices.
# Each loaded foot lands wholly on a real flat tread. Only the swinging foot
# crosses the actual3mm bevel; it must remain clear of geometry. The planted
# foot still uses normal>=.9,4mm height tolerance on every heel/forefoot point.
left0=Vector((6.53,8.80,floor_z));right0=Vector((6.71,8.80,floor_z))
left1=Vector((6.53,9.20,pan_z));right1=Vector((6.71,9.38,pan_z))
for phase,(moving,start,end,planted,fixed,body_a,body_b) in enumerate((
  ('left',left0,left1,'right',right0,Vector((6.62,8.80,floor_z)),Vector((6.62,9.00,(floor_z+pan_z)/2))),
  ('right',right0,right1,'left',left1,Vector((6.62,9.00,(floor_z+pan_z)/2)),Vector((6.62,9.29,pan_z))),
)):
    check_stance(fixed,planted,phase)
    check_stance(start,moving,str(phase)+'_liftoff')
    check_stance(end,moving,str(phase)+'_touchdown')
    for i in range(81):
        t=i/80;p=start.lerp(end,t);p.z+=.085*math.sin(math.pi*t)
        body=body_a.lerp(body_b,t);check_body(body,(phase,i))
        foot_hits=[]
        for ox,oy in foot_offsets:
            sole=p+Vector((ox,oy,0));h=ray(sole+Vector((0,0,.005)),(0,0,-1),.30)
            clearance=sole.z-h['point'][2] if h else None
            if h is None or clearance<-.001:
                step_errors.append({'phase':phase,'index':i,'foot':moving,'kind':'SWING_SOLE_CLEARANCE','sole':list(sole),'hit':h,'clearance_m':clearance})
            foot_hits.append({'sole':list(sole),'hit':h,'clearance_m':clearance})
        step_records.append({'phase':phase,'index':i,'foot':moving,'kind':'swing','center':list(p),'body_base':list(body),'probes':foot_hits})
step={'status':'PASS' if not step_errors else 'FAIL','phase_count':2,'swing_body_stations':162,
      'stance_contact_samples':54,'swing_sole_samples':1458,'body_radius_m':.18,'body_height_m':1.95,
      'minimum_head_clearance_m':step_clearance,'loaded_foot_normal_min':.9,'loaded_foot_tolerance_m':.004,
      'foot_size_m':[.08,.23],'lift_arc_m':.085,'world_floor_z':floor_z,'world_pan_z':pan_z,
      'method':'Independent loaded left/right heel,midfoot,forefoot contacts on flat floor/pan; lifted swing sole checked across bevel;162full body poses. Footpose spacing <=8.3mm. Same geometric poses permit reverse traversal; no biomechanics claim.',
      'errors':step_errors,'records':step_records}

mesh_bad=[r for r in inventory if 'evaluated_mesh' in r and
          (r['evaluated_mesh']['boundary_edges'] or r['evaluated_mesh']['nonmanifold_edges'] or
           r['evaluated_mesh']['zero_area_faces'] or r['evaluated_mesh']['signed_volume']<=0)]
rec={'candidate':str(SOURCE),'candidate_sha256':before,'candidate_unchanged':sha(SOURCE)==before,
     'blender_version':bpy.app.version_string,'no_save_no_render':True,
     'method':'Independent saved evaluated regional meshes.32ring+center vertical columns and624horizontal rays per path station. 180mm body radius,1950mm head, measured feet4mm,25mm route spacing.',
     'regional_meshes':len(inventory),'region_inventory':inventory,'evaluated_mesh_failures':mesh_bad,
     'routes':route_rows,'interface_probes':probes,'basin_surface_probes':basin,
     'shower_two_foot_step':step,
     'limits':['No GUI navigation or whole-house60edge/frame rerun.',
       'Shower step is an explicit C two-foot geometric gait, not physiology validation. Stance contact rules remain normal>=.9 and4mm tolerance.',
       'Visual/source acceptance is independently reported; numeric pass does not establish it.']}
OUT.write_text(json.dumps(rec,indent=2),encoding='utf-8')
print(json.dumps({'candidate_unchanged':rec['candidate_unchanged'],'regional_meshes':len(inventory),
 'mesh_failures':len(mesh_bad),'routes':[{k:r[k] for k in ('id','samples','status','minimum_vertical_clearance_m')} for r in route_rows],
 'first_errors':[r['issues'][:2] for r in route_rows],'shower_step':{k:step[k] for k in ('status','minimum_head_clearance_m','stance_contact_samples','swing_body_stations')},
 'step_first_errors':step_errors[:3]},indent=2))

