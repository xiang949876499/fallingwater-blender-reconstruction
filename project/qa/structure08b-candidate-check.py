"""Seven mesh replacements/two duplicate removals; six diagnosed categories."""
import bpy,json,sys,hashlib,array,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));import main_house
from fwlib import poly_prism,collection
SRC=R/'scene/Fallingwater_floor_core_candidate08.blend';OUT=R/'scene/Fallingwater_structure_candidate08b.blend'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='c78cab9c1d1d3341c72ac926da1abe931902f4c0381e49e956c6c814c930ddc7'
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4
def fingerprints():
    out={};shared={}
    for ob in s.objects:
        h=hashlib.sha256(str(tuple(tuple(row) for row in ob.matrix_world)).encode())
        if ob.type=='MESH':
            ptr=ob.data.as_pointer()
            if ptr not in shared:
                a=array.array('f',[0.])*(len(ob.data.vertices)*3);ob.data.vertices.foreach_get('co',a);b=array.array('i',[0])*len(ob.data.loops);ob.data.loops.foreach_get('vertex_index',b);shared[ptr]=hashlib.sha256(a.tobytes()+b.tobytes()).digest()
            h.update(shared[ptr])
        h.update(str(tuple(m.name if m else None for m in getattr(ob.data,'materials',[]))).encode());out[ob.name]=h.hexdigest()
    return out
def world(ob):return [list(ob.matrix_world@v.co) for v in ob.data.vertices]
def area(p):return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1])))*.5
def inside(x,y,p):
    yes=False
    for a,b in zip(p,p[1:]+p[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:yes=not yes
    return yes
before=fingerprints();servant=main_house.closed_floor_source_polygon('MAIN_L1_SERVANT');rr=next(t[2] for t in main_house.THRESHOLDS if t[0]=='entry_loggia');entry=main_house.physical_threshold_source_polygon('entry_loggia',rr)
specs=[('MAIN_L1_SERVANT_slab',servant,-.12,.1),('MAIN_L1_SERVANT_finish',servant,.1,.122),('MAIN_floor_threshold_entry_loggia',entry,-.08,.1),('MAIN_floor_threshold_entry_loggia_finish',entry,.1,.122),('MAIN_L2_CLOSET_M_ceiling',main_house.closed_ceiling_source_polygon('MAIN_L2_CLOSET_M'),5.,5.018),('MAIN_L2_CLOSET_G_ceiling',main_house.closed_ceiling_source_polygon('MAIN_L2_CLOSET_G'),5.,5.018),('MAIN_L2_guest_corridor_ceiling',main_house.guest_corridor_ceiling_source_polygon(),5.,5.018)]
removed=['MAIN_L2_arc_lower_landing','MAIN_L2_arc_lower_landing_finish'];expected={};old={};polygons={}
for name,p,z0,z1 in specs:
    ob=s.objects[name];old[name]=world(ob);poly=[main_house.xy(a) for a in p];polygons[name]={'source':p,'world':poly,'area_m2':area(poly)}
    temp=poly_prism('QA_08b_rebuild',poly,z0,z1,ob.data.materials[0],collection('QA_08B_TRANSIENT'));bpy.context.view_layer.update();expected[name]=world(temp);ob.data=temp.data.copy();ob.matrix_world=temp.matrix_world.copy();ob['physical_revision']='08b bounded shared floor/ceiling edge repair';bpy.data.objects.remove(temp,do_unlink=True)
for name in removed:old[name]=world(s.objects[name]);bpy.data.objects.remove(s.objects[name],do_unlink=True)
bpy.data.collections.remove(bpy.data.collections['QA_08B_TRANSIENT']);bpy.context.view_layer.update();after=fingerprints();changed=sorted(n for n in before if n in after and before[n]!=after[n]);assert changed==sorted(n for n,_,_,_ in specs);assert sorted(set(before)-set(after))==sorted(removed);assert not set(after)-set(before)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));bpy.ops.wm.open_mainfile(filepath=str(OUT));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();rebuild_error=max(abs(a[k]-b[k]) for n,vv in expected.items() for a,b in zip(world(s.objects[n]),vv) for k in range(3));assert rebuild_error<1e-6
bvhs={};changed_verts=[];changed_faces=[]
for ob in s.objects:
    if ob.type!='MESH' or not ob.name.startswith('MAIN_') or len(ob.data.vertices)>500:continue
    e=ob.evaluated_get(dg);m=e.to_mesh();vv=[e.matrix_world@v.co for v in m.vertices];ff=[tuple(f.vertices) for f in m.polygons]
    bvhs[ob.name]=BVHTree.FromPolygons(vv,ff)
    if ob.name in changed:
        off=len(changed_verts);changed_verts+=vv;changed_faces.extend(tuple(off+i for i in f) for f in ff)
    e.to_mesh_clear()
def ray(o,d,distance=100):
    hit,p,n,f,ob,_=s.ray_cast(dg,Vector(o),Vector(d),distance=distance);return {'hit':ob.name if hit else None,'point':list(p) if hit else None}
s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100
probe=json.loads((R/'qa/structure08b-probe.json').read_text());pixels=[]
for prev in probe['pixels']:
    cam=s.objects[prev['camera']];x,y=prev['pixel'];co=cam.data.view_frame(scene=s);xmin,xmax=min(v.x for v in co),max(v.x for v in co);ymin,ymax=min(v.y for v in co),max(v.y for v in co)
    d=(cam.matrix_world.to_quaternion()@Vector((xmin+(x+.5)/640*(xmax-xmin),ymax-(y+.5)/360*(ymax-ymin),co[0].z))).normalized();hit=ray(cam.matrix_world.translation,d)
    near=[]
    if hit['point']:
        p=Vector(hit['point'])
        for name,bvh in bvhs.items():
            q,n,f,dist=bvh.ray_cast(p-d*.002,d,.004)
            if q is not None and (q-p).length<.0001:near.append(name)
    opening=prev['camera']=='CAM_MAIN_L1_SERVANT_B' and y<50
    accepted=opening or (len(near)==1 and hit['hit'] in near and abs(hit['point'][2]-prev['expected_plane_z'])<.001)
    pixels.append({'camera':prev['camera'],'pixel':prev['pixel'],'before':prev['first'],'after':hit,'same_point_surfaces':near,'source_opening_preserved':opening,'pass_':accepted})
# Direct ceiling mesh coverage: no opaque object is hidden to run these probes.
ceiling_grid=[]
for name in ('MAIN_L2_CLOSET_M_ceiling','MAIN_L2_CLOSET_G_ceiling','MAIN_L2_guest_corridor_ceiling'):
    p=polygons[name]['world'];xlo,xhi=min(a[0] for a in p),max(a[0] for a in p);ylo,yhi=min(a[1] for a in p),max(a[1] for a in p)
    for ix in range(1,18):
        for iy in range(1,18):
            q=Vector((xlo+(xhi-xlo)*ix/18,ylo+(yhi-ylo)*iy/18,4.97))
            if not inside(q.x,q.y,p):continue
            surfaces=[]
            for n,bvh in bvhs.items():
                if 'ceiling' not in n:continue
                h,no,f,dist=bvh.ray_cast(q,Vector((0,0,1)),.08)
                if h is not None and abs(h.z-5)<.001:surfaces.append(n)
            ceiling_grid.append({'owner':name,'xyz':list(q),'surfaces':surfaces,'pass_':len(surfaces)==1})
# Both the eliminated lower-landing pair and the retained terrace have exactly
# the same level and footprint over the former landing. Show actual support.
landing=[]
for ix in range(13):
    for iy in range(35):
        px=468+(ix+.5)/13*6;py=142+(iy+.5)/35*34;q=main_house.xy((px,py));p,n,f,dist=bvhs['MAIN_L2_TERRACE_N_finish'].ray_cast(Vector((*q,2.93)),Vector((0,0,-1)),.2)
        landing.append({'source_px':[px,py],'retained_finish_z':p.z if p is not None else None,'pass_':p is not None and abs(p.z-2.8668)<.001})
# West Servant strip and both Loggia shared-edge joins, including the tiny
# original sloped north corner, keep a floor under every selected position.
support=[]
for i in range(40):
    q=main_house.xy((182.7,230.4+i*.95));r=ray((*q,.19),(0,0,-1),.3);r.update(label='servant_west',pass_=r['point'] is not None and abs(r['point'][2]-.122)<.001);support.append(r)
for py in (306.4,307.2,312,318,325,331.5):
    for px in [508+i*.4 for i in range(79)]:
        q=main_house.xy((px,py));r=ray((*q,.19),(0,0,-1),.3)
        # At py306.4, the original threshold ends atx537 before the sloped
        # Loggia starts. This retained exterior corner is not falsely infilled.
        if py==306.4 and px>537:continue
        r.update(label='loggia_join',source_px=[px,py],pass_=r['point'] is not None and abs(r['point'][2]-.122)<.001);support.append(r)
route=json.loads((R/'data/tour-route.json').read_text());body_tree=BVHTree.FromPolygons(changed_verts,changed_faces);body_n=0;body_hits=[];route_floor=[]
def body(q,label):
    global body_n
    for dz in (0,-.65,-1.3):
        p=Vector(q)+Vector((0,0,dz));h=body_tree.find_nearest(p,.18);body_n+=1
        if h[0] is not None:body_hits.append({'label':label,'point':list(p),'distance':h[3]})
for ob in s.objects:
    if ob.type=='CAMERA':body(ob.matrix_world.translation,ob.name)
for seg in route['main_segments']+route['supplemental_segments']:
    rel=next((rid for rid in seg.get('room_ids',[]) if rid in ('MAIN_L1_SERVANT','MAIN_L1_LOGGIA','MAIN_L2_TERRACE_N')),None)
    for i,(a,b) in enumerate(zip(seg['points'],seg['points'][1:])):
        a,b=Vector(a),Vector(b);n=max(2,math.ceil((b-a).length/.1))
        for k in range(n+1):
            q=a.lerp(b,k/n);body(q,f"{seg['id']}:{i}:{k}")
            if rel:
                floorz=.122 if rel!='MAIN_L2_TERRACE_N' else 2.8668;r=ray((q.x,q.y,floorz+.1),(0,0,-1),.5);r.update(segment=seg['id'],point_on_route=list(q),pass_=r['point'] is not None and abs(r['point'][2]-floorz)<.08);route_floor.append(r)
counts={'changed':len(changed),'removed_duplicates':len(removed),'pixels':len(pixels),'pixel_fails':sum(not r['pass_'] for r in pixels),'ceiling_grid':len(ceiling_grid),'ceiling_grid_fails':sum(not r['pass_'] for r in ceiling_grid),'landing_support':len(landing),'landing_support_fails':sum(not r['pass_'] for r in landing),'local_floor_support':len(support),'local_floor_support_fails':sum(not r['pass_'] for r in support),'body_samples':body_n,'body_hits':len(body_hits),'route_floor_samples':len(route_floor),'route_floor_fails':sum(not r['pass_'] for r in route_floor)}
report={'status':'PASS_LOCAL_STRUCTURE08B_VISUAL_NOT_RUN' if not any(v for k,v in counts.items() if k.endswith(('_fails','_hits'))) else 'FAIL_LOCAL_STRUCTURE08B','candidate':str(OUT),'candidate_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'source_script_sha256':hashlib.sha256((R/'scripts/main_house.py').read_bytes()).hexdigest(),'changed':changed,'removed':removed,'all_non_targets_identical':all(before[n]==after[n] for n in before if n not in changed+removed),'rebuild_max_error_m':rebuild_error,'polygons':polygons,'old_vertices':old,'counts':counts,'pixels':pixels,'ceiling_grid':ceiling_grid,'landing':landing,'support':support,'body_hits':body_hits,'route_floor':route_floor,'route_json_sha256':hashlib.sha256((R/'data/tour-route.json').read_bytes()).hexdigest(),'limits':['Servant northwest narrow source opening was deliberately retained; green pixels there are not repaired as an opaque wall.','No furniture, window, door, stair, light or camera modified. Removed landing was an exact duplicate over existing floor, not removal of access.','Same-view render and complete candidate route acceptance remain for the integrator.']}
(R/'qa/structure08b-candidate-check.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:report[k] for k in ('status','candidate_sha256','source_script_sha256','counts')},indent=2))
