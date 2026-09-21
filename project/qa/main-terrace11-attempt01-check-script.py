"""CPU4 independent actual-mesh pre/post checks; never renders."""
import bpy,sys,json,hashlib,array,collections,math,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import main_terrace11 as fix
SRC=R/'scene/Fallingwater_integration_candidate10a.blend'
OUT=R/'scene/Fallingwater_main_terrace_candidate11a.blend'
Q=R/'qa';TAG='main-terrace11-attempt01'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(SRC)=='dc7594d60b68effaf10b85dd1804827fc9cb16dd786656daa4da16c761b33518'
assert not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene
def settings():return {'frame':s.frame_current,'camera':s.camera.name if s.camera else None,'engine':s.render.engine,'resolution':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],'threads':[s.render.threads_mode,s.render.threads],'samples':s.cycles.samples,'device':s.cycles.device,'exposure':s.view_settings.exposure,'world':s.world.name,'render_filepath':s.render.filepath}
settings_before=settings()
def prop_state(obj):
    out=[]
    for p in obj.bl_rna.properties:
        if p.identifier in ('rna_type','name'):continue
        try:
            v=getattr(obj,p.identifier)
            if isinstance(v,(str,int,float,bool)) or v is None:out.append((p.identifier,v))
            elif isinstance(v,bpy.types.ID):out.append((p.identifier,v.name))
            elif getattr(p,'is_array',False):out.append((p.identifier,list(v)))
        except Exception:pass
    return out
def fingerprint():
    out={};mesh_cache={}
    for o in s.objects:
        h=hashlib.sha256(str((o.type,tuple(tuple(r) for r in o.matrix_world),o.hide_render,o.hide_viewport,sorted(o.keys()))).encode())
        if o.type=='MESH':
            ptr=o.data.as_pointer()
            if ptr not in mesh_cache:
                a=array.array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a)
                b=array.array('i',[0])*len(o.data.loops);o.data.loops.foreach_get('vertex_index',b)
                c=array.array('i',[0])*len(o.data.polygons);o.data.polygons.foreach_get('loop_total',c)
                mesh_cache[ptr]=hashlib.sha256(a.tobytes()+b.tobytes()+c.tobytes()).digest()
            h.update(mesh_cache[ptr]);h.update(str([m.name if m else None for m in o.data.materials]).encode())
        elif o.data:h.update(str(prop_state(o.data)).encode())
        h.update(str([prop_state(m) for m in o.modifiers]).encode());out[o.name]=h.hexdigest()
    return out
def materials():
    out={}
    for m in bpy.data.materials:
        rows=[prop_state(m)]
        if m.node_tree:
            for n in m.node_tree.nodes:rows.append((n.name,n.bl_idname,prop_state(n),[(i.name,str(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]))
            rows.append([(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links])
        out[m.name]=hashlib.sha256(str(rows).encode()).hexdigest()
    return out
before_fp=fingerprint();before_mats=materials();print('Fingerprint ready',flush=True)
route_path=R/'qa/tour-path-route-iteration09-attempt01.json';route=json.loads(route_path.read_text(encoding='utf-8'))
route_segs=[seg for seg in route['main_segments']+route['supplemental_segments'] if seg['id'] in ('MAIN_L2_TERRACE_W','MAIN_L2_TERRACE_S')]
protected_files=['scripts/main_house.py','scripts/tour.py','data/main_house.json','data/tour-route.json','dimensions.csv']
protected_hashes={n:sha(R/n) for n in protected_files}
(Q/(TAG+'-helper-snapshot.py')).write_bytes((R/'scripts/main_terrace11.py').read_bytes())
def bbox(o):
    vs=[o.matrix_world@Vector(p) for p in o.bound_box]
    return [[min(p[i] for p in vs),max(p[i] for p in vs)] for i in range(3)]
def local_trees():
    deps=bpy.context.evaluated_depsgraph_get();out={}
    for o in s.objects:
        if o.type!='MESH' or not o.name.startswith(('MAIN_','MASTER_','FW_DETAIL_MAIN_')):continue
        b=bbox(o)
        if b[2][1]<2.2 or b[2][0]>5.1:continue
        west=b[0][1]>-13.6 and b[0][0]<-3.9 and b[1][1]>12.3 and b[1][0]<18.3
        south=b[0][1]>-.8 and b[0][0]<7.5 and b[1][1]>-2.5 and b[1][0]<7.8
        if not (west or south):continue
        e=o.evaluated_get(deps);me=e.to_mesh()
        try:
            if me.vertices:out[o.name]=BVHTree.FromPolygons([e.matrix_world@v.co for v in me.vertices],[tuple(f.vertices) for f in me.polygons])
        finally:e.to_mesh_clear()
    return out
def hit(trees,p,d,limit=20,names=None):
    found=[]
    for name in (names if names is not None else trees):
        if name not in trees:continue
        q,n,f,dist=trees[name].ray_cast(Vector(p),Vector(d).normalized(),limit)
        if q is not None:found.append({'object':name,'face':f,'point':list(q),'normal':list(n),'distance':dist})
    return min(found,key=lambda r:r['distance']) if found else None
def dimension(trees,id,pa,da,na,pb,db,nb,axis,target):
    a=hit(trees,pa,da,50,na);b=hit(trees,pb,db,50,nb);v=abs(b['point'][axis]-a['point'][axis]) if a and b else None
    return {'id':id,'a':a,'b':b,'target_m':target,'actual_m':v,'error_m':v-target if v is not None else None,'tolerance_m':max(.02,.005*target),'pass':v is not None and abs(v-target)<=max(.02,.005*target)}
def dimensions(trees,after=False):
    w0=['MAIN_L2_west_parapet_0'];wn=w0 if after else ['MAIN_L2_west_north_0'];ws=w0 if after else ['MAIN_L2_west_parapet_1']
    s0=['MAIN_L2_south_parapet_0'];se=s0 if after else ['MAIN_L2_south_parapet_2']
    return [dimension(trees,'WEST_X',(-20,14,3.1),(1,0,0),w0,(-10,14,4),(1,0,0),['MAIN_L2_dressing_shell_middle'],0,8.82015),
            dimension(trees,'WEST_Y',(-10,25,3.1),(0,-1,0),wn,(-10,8,3.1),(0,1,0),ws,1,5.343525),
            dimension(trees,'SOUTH_X',(-5,0,3.1),(1,0,0),s0,(15,0,3.1),(-1,0,0),se,0,7.75335)]
def poses():
    out=[]
    for seg in route_segs:
        for j,(a,b) in enumerate(zip(seg['points'],seg['points'][1:])):
            av,bv=Vector(a),Vector(b);count=max(2,math.ceil((bv-av).length/.025))
            for i in range(count+1):
                p=av.lerp(bv,i/count);out.append({'id':f"{seg['id']}:{j}:{i}",'xy':[p.x,p.y]})
    # Door transitions use the documented physical threshold axes, independent
    # from the terrace helper and separate from inspection-route cuts.
    for label,a,b in [('DRESSING_DOOR',(236,289),(259,289)),('MASTER_DOOR',(377,401),(377,420))]:
        aa=Vector(((a[0]-327)*.0524,(540-a[1])*.0531));bb=Vector(((b[0]-327)*.0524,(540-b[1])*.0531));count=max(2,math.ceil((bb-aa).length/.025))
        for i in range(count+1):out.append({'id':f'{label}:{i}','xy':list(aa.lerp(bb,i/count))})
    for o in s.objects:
        if o.type=='CAMERA' and o.name.startswith(('CAM_MAIN_L2_TERRACE_W_','CAM_MAIN_L2_TERRACE_S_')):out.append({'id':o.name,'xy':list(o.matrix_world.translation)[:2]})
    return out
pose_inputs=poses()
def pose_check(trees,row):
    x,y=row['xy'];floor=2.8668;feet=[];fail=[]
    offsets=[(0,0)]+[(.18*math.cos(k*math.tau/8),.18*math.sin(k*math.tau/8)) for k in range(8)]
    for dx,dy in offsets:
        h=hit(trees,(x+dx,y+dy,floor+.08),(0,0,-1),.2)
        good=bool(h and h['normal'][2]>=.9 and abs(h['point'][2]-floor)<=.020)
        feet.append(h)
        if not good:fail.append('FOOT')
    body=[]
    for z in (.10,.50,1.0,1.5,1.95):
        for k in range(8):
            dx,dy=math.cos(k*math.tau/8),math.sin(k*math.tau/8)
            h=hit(trees,(x,y,floor+z),(dx,dy,0),.18)
            if h:body.append({'z':z,'direction':[dx,dy,0],'hit':h})
    heads=[]
    for dx,dy in offsets:
        h=hit(trees,(x+dx,y+dy,floor+.08),(0,0,1),1.87)
        if h:heads.append(h)
    if body:fail.append('BODY');
    if heads:fail.append('HEAD')
    return {**row,'pass':not fail,'failures':sorted(set(fail)),'feet':feet,'body_hits':body,'head_hits':heads}
before_trees=local_trees();before_dims=dimensions(before_trees);before_poses=[pose_check(before_trees,p) for p in pose_inputs]
print('Baseline:',len(before_trees),'meshes',len(before_poses),'poses',sum(not r['pass'] for r in before_poses),'existing pose failures',flush=True)
manifest=fix.apply();after_fp=fingerprint();after_mats=materials();after_trees=local_trees()
changed=sorted(n for n in after_fp if n in before_fp and after_fp[n]!=before_fp[n]);removed=sorted(set(before_fp)-set(after_fp));added=sorted(set(after_fp)-set(before_fp))
scope_ok=changed==sorted(manifest['changed']) and removed==sorted(manifest['removed']) and not added
after_dims=dimensions(after_trees,True);after_poses=[pose_check(after_trees,p) for p in pose_inputs]
regression=[{'id':a['id'],'before':b['failures'],'after':a['failures']} for a,b in zip(after_poses,before_poses) if a['failures'] and not b['failures']]
def topology(name):
    o=s.objects[name];e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh()
    try:
        edges=collections.Counter(tuple(sorted(edge)) for f in me.polygons for edge in f.edge_keys);me.calc_loop_triangles()
        vv=[e.matrix_world@v.co for v in me.vertices];vol=sum(vv[t.vertices[0]].cross(vv[t.vertices[1]]).dot(vv[t.vertices[2]])/6 for t in me.loop_triangles)
        return {'object':name,'vertices':len(vv),'faces':len(me.polygons),'edge_multiplicity':dict(collections.Counter(edges.values())),'signed_volume_m3':vol,'pass':all(v==2 for v in edges.values()) and vol>0}
    finally:e.to_mesh_clear()
mesh_checks=[topology(n) for n in manifest['changed']]
# Clear floor rectangle is derived from measured actual INNER wall faces and
# the unchanged room-side interface, not the helper's generated box collection.
floor_checks=[]
def floor_at(x,y,label):
    hits=[]
    for name in after_trees:
        if not name.endswith('_finish'):continue
        h=hit(after_trees,(x,y,2.9168),(0,0,-1),.10,[name])
        if h and abs(h['point'][2]-2.8668)<1e-4:hits.append(h)
    return {'label':label,'xy':[x,y],'hits':hits,'pass':len(hits)==1 and hits[0]['normal'][2]>=.9}
wi=hit(after_trees,(-10,14,3.1),(-1,0,0),8,['MAIN_L2_west_parapet_0'])['point'][0]
si=hit(after_trees,(-10,14,3.1),(0,-1,0),8,['MAIN_L2_west_parapet_0'])['point'][1]
ni=hit(after_trees,(-10,14,3.1),(0,1,0),8,['MAIN_L2_west_parapet_0'])['point'][1]
e=-4.4744
swi=hit(after_trees,(3,0,3.1),(-1,0,0),8,['MAIN_L2_south_parapet_0'])['point'][0]
sei=hit(after_trees,(3,0,3.1),(1,0,0),8,['MAIN_L2_south_parapet_0'])['point'][0]
ssi=hit(after_trees,(3,0,3.1),(0,-1,0),8,['MAIN_L2_south_parapet_0'])['point'][1]
for label,x0,x1,y0,y1 in [('WEST',wi+.002,e-.003,si+.002,ni-.003),('SOUTH',swi+.002,sei-.002,ssi+.002,6.6075)]:
    nx=math.ceil((x1-x0)/.18);ny=math.ceil((y1-y0)/.18)
    for ix in range(nx+1):
        for iy in range(ny+1):floor_checks.append(floor_at(x0+(x1-x0)*ix/nx,y0+(y1-y0)*iy/ny,label))
floor_fails=[r for r in floor_checks if not r['pass']]
counts={'scope_ok':scope_ok,'dimensions_pass':sum(r['pass'] for r in after_dims),'topology_failures':sum(not r['pass'] for r in mesh_checks),'floor_samples':len(floor_checks),'floor_failures':len(floor_fails),'posture_samples':len(after_poses),'baseline_posture_failures':sum(not r['pass'] for r in before_poses),'candidate_posture_failures':sum(not r['pass'] for r in after_poses),'new_posture_failures':len(regression),'all_materials_unchanged':before_mats==after_mats,'settings_unchanged':settings()==settings_before}
report={'status':'REVIEW_REQUIRED','source':str(SRC),'source_sha256':sha(SRC),'helper_sha256':sha(R/'scripts/main_terrace11.py'),'manifest':manifest,'counts':counts,'dimensions_before':before_dims,'dimensions_after':after_dims,'mesh_checks':mesh_checks,'floor_failures':floor_fails,'floor_checks':floor_checks,'poses_before':before_poses,'poses_after':after_poses,'new_posture_failures':regression,'route_source':str(route_path),'route_sha256':sha(route_path),'route_scope':['MAIN_L2_TERRACE_W','MAIN_L2_TERRACE_S','documented dressing/master terrace thresholds','4 original terrace cameras'],'ground_body_limits':{'foot_radius_m':.18,'foot_normal_min':.9,'allowed_existing_threshold_step_m':.020,'body_radius_m':.18,'head_clearance_m':1.95,'path_spacing_m':.025,'body_vertical_stations_m':[.1,.5,1,1.5,1.95],'local_main_mesh_count':len(after_trees),'exclusions':'Site/vegetation unchanged; no whole-building/all-adjacency claim'},'object_fingerprints_before':before_fp,'object_fingerprints_after':after_fp,'material_fingerprints_before':before_mats,'material_fingerprints_after':after_mats,'settings':settings_before,'protected_files_unchanged':{n:sha(R/n)==h for n,h in protected_hashes.items()},'source_scene_unchanged':sha(SRC)=='dc7594d60b68effaf10b85dd1804827fc9cb16dd786656daa4da16c761b33518','rendered':False,'visual_status':'NOT_RUN'}
ok=scope_ok and all(r['pass'] for r in after_dims) and all(r['pass'] for r in mesh_checks) and not floor_fails and not regression and counts['all_materials_unchanged'] and counts['settings_unchanged']
if ok:
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT));report['candidate']=str(OUT);report['candidate_sha256']=sha(OUT);report['status']='SAVED_GEOMETRY_CANDIDATE_VISUAL_NOT_RUN'
(Q/(TAG+'-check.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'counts':counts,'status':report['status'],'candidate_sha256':report.get('candidate_sha256'),'new_posture_failures':regression,'floor_failure_first20':floor_fails[:20]},indent=2),flush=True)
assert ok,'Evidence retained; no candidate saved on failing local checks'
