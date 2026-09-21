"""Read-only independent bath10b mesh/route/interface audit. No render/save/import of candidate helper."""
from pathlib import Path
import bpy,bmesh,json,hashlib,math,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'scene/Fallingwater_master_bath_candidate10b.blend'
FOLLOWUP='--followup' in sys.argv or '--followup2' in sys.argv
SUFFIX='followup2' if '--followup2' in sys.argv else 'followup' if FOLLOWUP else 'audit'
OUT=ROOT/('qa/master-bath-detail10-independent-'+SUFFIX+'.json')
EXPECTED='cf93125a6de7deb0b66a0fb32b295f5c9f208614ed2254b652ef2f03f94dd6eb'
assert not OUT.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=sha(SOURCE);assert before==EXPECTED
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
bpy.context.scene.render.threads_mode='FIXED';bpy.context.scene.render.threads=4
deps=bpy.context.evaluated_depsgraph_get()
verts=[];polys=[];owners=[];inventory=[];trees={}
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
    return {'object':owners[ix],'point':list(co),'normal':list(no),'distance':dd} if co is not None else None

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
 'CENTER_TO_WC_FRONT':[(443,387),(438,379),(432,375),(431,367)],
 'CENTER_TO_BASIN_FRONT':[(443,387),(451.3,387),(451.3,394.8)],
 'CENTER_TO_SHOWER':[(443,387),(452,383),(452,376),(452,365)],
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
probe('DOOR_THRESHOLD_HEAD',xyz(420,397.5,2.8668),(0,0,1),2.5)
for p in ((5.25,7.10,4.99),(5.26,9.98,4.99),(7.11,9.96,4.99)):
    probe('EDGE_CEILING_'+str(p),p,(0,0,1),.1)

# Actual rim/recess readback, not constructor profile expectations.
basin=[]
for sx in range(-5,6):
    for sy in range(-3,4):
        p=xyz(451.3,407.0,4.0)+Vector((sx*.048,sy*.048,0))
        basin.append({'xy':list(p)[:2],'hit':ray(p,(0,0,-1),1.0)})

mesh_bad=[r for r in inventory if 'evaluated_mesh' in r and
          (r['evaluated_mesh']['boundary_edges'] or r['evaluated_mesh']['nonmanifold_edges'] or
           r['evaluated_mesh']['zero_area_faces'] or r['evaluated_mesh']['signed_volume']<=0)]
rec={'candidate':str(SOURCE),'candidate_sha256':before,'candidate_unchanged':sha(SOURCE)==before,
     'blender_version':bpy.app.version_string,'no_save_no_render':True,
     'method':'Independent saved evaluated regional meshes.32ring+center vertical columns and624horizontal rays per path station. 180mm body radius,1950mm head, measured feet4mm,25mm route spacing.',
     'regional_meshes':len(inventory),'region_inventory':inventory,'evaluated_mesh_failures':mesh_bad,
     'routes':route_rows,'interface_probes':probes,'basin_surface_probes':basin,
     'limits':['No GUI navigation or whole-house60edge/frame rerun.',
       'Step joint foot support may span the physical35mm shower riser. All other routes single flat finish.',
       'Visual/source acceptance is independently reported; numeric pass does not establish it.']}
OUT.write_text(json.dumps(rec,indent=2),encoding='utf-8')
print(json.dumps({'candidate_unchanged':rec['candidate_unchanged'],'regional_meshes':len(inventory),
 'mesh_failures':len(mesh_bad),'routes':[{k:r[k] for k in ('id','samples','status','minimum_vertical_clearance_m')} for r in route_rows],
 'first_errors':[r['issues'][:2] for r in route_rows]},indent=2))
