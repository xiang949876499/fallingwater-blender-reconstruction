"""Frozen10 pre/post actual-mesh audit. CPU4. Never renders or edits production."""
import bpy,sys,json,hashlib,array,collections,math,ast,copy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];Q=R/'qa';sys.path.insert(0,str(R/'scripts'))
import master_ceiling11 as fix
import master_navigation10 as nav
SRC=R/'scene/Fallingwater_iteration10.blend';OUT=R/'scene/Fallingwater_master_ceiling_candidate11b.blend'
SHA='1e7b17d9c2396513f005724e50788bf834097eedb401b91a7f1030825e2c4ed9'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(SRC)==SHA and not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene

def prop_state(obj):
    out=[]
    for p in obj.bl_rna.properties:
        if p.identifier in ('rna_type','name','users') or p.is_readonly:continue
        try:
            v=getattr(obj,p.identifier)
            if isinstance(v,(str,int,float,bool)) or v is None:out.append((p.identifier,v))
            elif isinstance(v,bpy.types.ID):out.append((p.identifier,v.name))
            elif p.is_array:out.append((p.identifier,list(v)))
        except Exception:pass
    return out

def fingerprint():
    out={};cache={}
    for o in s.objects:
        h=hashlib.sha256(str((o.type,tuple(tuple(r) for r in o.matrix_world),o.hide_render,o.hide_viewport,[(k,str(o[k])) for k in sorted(o.keys())])).encode())
        if o.type=='MESH':
            ptr=o.data.as_pointer()
            if ptr not in cache:
                a=array.array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a)
                b=array.array('i',[0])*len(o.data.loops);o.data.loops.foreach_get('vertex_index',b)
                c=array.array('i',[0])*len(o.data.polygons);o.data.polygons.foreach_get('loop_total',c)
                d=array.array('i',[0])*len(o.data.polygons);o.data.polygons.foreach_get('material_index',d)
                cache[ptr]=hashlib.sha256(a.tobytes()+b.tobytes()+c.tobytes()+d.tobytes()).digest()
            h.update(cache[ptr]);h.update(str([m.name if m else None for m in o.data.materials]).encode())
        elif o.data:h.update(str(prop_state(o.data)).encode())
        h.update(str([prop_state(m) for m in o.modifiers]).encode());out[o.name]=h.hexdigest()
    return out

def materials():
    out={}
    def val(x):
        if isinstance(x,(str,int,float,bool)) or x is None:return x
        if isinstance(x,bpy.types.ID):return x.name
        try:return list(x)
        except TypeError:return str(x)
    for m in bpy.data.materials:
        rows=[prop_state(m)]
        if m.node_tree:
            for n in m.node_tree.nodes:rows.append((n.name,n.bl_idname,prop_state(n),[(i.name,val(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]))
            rows.append([(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links])
        out[m.name]=hashlib.sha256(str(rows).encode()).hexdigest()
    return out

def settings():
    return {'frame':s.frame_current,'range':[s.frame_start,s.frame_end],'camera':s.camera.name,'render':prop_state(s.render),'cycles':prop_state(s.cycles),'view':prop_state(s.view_settings),'world':s.world.name}

def evaluated(name):
    e=s.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh()
    try:return [e.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]
    finally:e.to_mesh_clear()

def mesh_metrics(name):
    v,f=evaluated(name);edges=collections.Counter(tuple(sorted((p[i],p[(i+1)%len(p)]))) for p in f for i in range(len(p)))
    origin=sum(v,Vector())/len(v)
    vv=[p-origin for p in v]
    volume=sum(vv[p[0]].cross(vv[p[i]]).dot(vv[p[i+1]])/6 for p in f for i in range(1,len(p)-1))
    # Face components sharing actual edges.
    adj=collections.defaultdict(set);ef=collections.defaultdict(list)
    for k,p in enumerate(f):
        for i in range(len(p)):ef[tuple(sorted((p[i],p[(i+1)%len(p)])))].append(k)
    for fs in ef.values():
        for a in fs:adj[a].update(fs)
    rem=set(range(len(f)));groups=[]
    while rem:
        todo=[rem.pop()];n=0
        while todo:
            a=todo.pop();n+=1
            for b in adj[a]&rem:rem.remove(b);todo.append(b)
        groups.append(n)
    return {'name':name,'vertices':len(v),'faces':len(f),'edge_multiplicity':dict(collections.Counter(edges.values())),'components':groups,'signed_volume_m3':volume,'pass':all(k==2 for k in edges.values()) and volume>0 and len(groups)==1}

def paths(probe):
    spec=nav.design();rows=[]
    for key,r in spec['paths'].items():rows.append({'id':key,'failure':probe.path(nav.eyes(r['feet']))})
    for key,r in spec['room_moves'].items():rows.append({'id':'ROOM_MOVE_'+key,'failure':probe.path(nav.eyes(r['feet']))})
    # Actual saved viewpoints, not reapplied poses.
    for o in s.objects:
        if o.type=='CAMERA' and o.name.startswith(('CAM_MAIN_L2_MASTER_','CAM_MAIN_L2_BATH_M_','CAM_MAIN_L2_TERRACE_S_')):
            rows.append({'id':o.name,'eye':list(o.matrix_world.translation),'failure':probe.point(o.matrix_world.translation,True)})
    return rows

def collision_pairs():
    # Surface contact is reported rather than automatically called a volume
    # collision; pivot/frame contacts may be intentional. No mesh is excluded
    # merely for an inconvenient name. Broadphase is the local changed volume.
    names=list(fix.CHANGED);trees={};bbs={}
    for o in s.objects:
        if o.type!='MESH' or o.hide_render:continue
        p=[o.matrix_world@Vector(v) for v in o.bound_box]
        b=[(min(v[k] for v in p),max(v[k] for v in p)) for k in range(3)]
        if b[0][1]<-1 or b[0][0]>5.2 or b[1][1]<5.8 or b[1][0]>12.6 or b[2][1]<2.89 or b[2][0]>5.1:continue
        bbs[o.name]=b
    def tree(n):
        if n not in trees:
            v,f=evaluated(n);trees[n]=BVHTree.FromPolygons(v,f)
        return trees[n]
    out=[]
    for a in names:
        for b in bbs:
            if a==b or (b in names and b<a):continue
            if any(bbs[a][k][1]<=bbs[b][k][0]+1e-5 or bbs[b][k][1]<=bbs[a][k][0]+1e-5 for k in range(3)):continue
            hits=tree(a).overlap(tree(b))
            if hits:out.append({'a':a,'b':b,'triangle_surface_contacts':len(hits)})
    return out

protected=[SRC]+[R/'scripts'/n for n in ('main_house.py','tour.py','master_detail10.py','master_bath_detail10.py','master_navigation10.py')]
protected0={str(p):sha(p) for p in protected}
fp0=fingerprint();mat0=materials();set0=settings();leaf0={n:{'metrics':mesh_metrics(n),'matrix':[list(v) for v in s.objects[n].matrix_world]} for n in fix.LEAF_NAMES}
print('Baseline fingerprints ready',flush=True)
probe0=nav.StrictProbe(s);path0=paths(probe0);step0=nav.sill_step(probe0);contacts0=collision_pairs()
print('Baseline paths and gait ready',flush=True)
manifest=fix.apply(enabled=True);fp1=fingerprint();mat1=materials();probe1=nav.StrictProbe(s);path1=paths(probe1);step1=nav.sill_step(probe1)
print('Candidate paths and original gait checked',flush=True)
# Additional, explicitly different C gait: torso remains at the unchanged
# supporting-floor datum, while all original swing feet, legs and 1.95m body
# tests remain unchanged. It is evidence, not a production navigation edit.
tree=ast.parse((R/'scripts/master_navigation10.py').read_text(encoding='utf-8'))
fn=copy.deepcopy(next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='sill_step'));fn.name='sill_step_fixed_torso_C'
changed_assignment=0
for n in ast.walk(fn):
    if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='body_floor' for t in n.targets):n.value=ast.Name(id='TOP',ctx=ast.Load());changed_assignment+=1
assert changed_assignment==1
module=ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[]));env=dict(vars(nav));exec(compile(module,'<QA-only fixed torso C gait>','exec'),env)
stepC=env['sill_step_fixed_torso_C'](probe1)
stepC['independent_C_change']='Only torso floor datum held at actual stationary support floor2.8668. Foot motions,15-point sole checks,4mm normals/radius0.18/HEAD1.95 and sweeps unchanged.'
stepC['source_identity']='B outward leaf and real raised track; C numerical gait. No source gait claim.'
for label,result in [('baseline-step',step0),('original-gait-fail',step1),('fixed-torso-gait-C',stepC)]:
    (Q/('master-ceiling11-'+label+'.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')

metrics=[mesh_metrics(n) for n in fix.CHANGED];contacts1=collision_pairs()
previous={(r['a'],r['b']) for r in contacts0};newcontacts=[r for r in contacts1 if (r['a'],r['b']) not in previous]
v,f=evaluated(fix.CEILING);roof=BVHTree.FromPolygons(v,f);sample_rows=[]
for ix in range(26):
    x=-.45+ix*.20
    for iy in range(27):
        y=6.90+iy*.20
        p,n,face,d=roof.ray_cast(Vector((x,y,4.7)),Vector((0,0,1)),.5)
        if p is not None:sample_rows.append({'xy':[x,y],'z':p.z,'normal':list(n)})
low_samples=[r for r in sample_rows if r['xy'][1]<manifest['break_world_y']-1e-5]
lowbad=[r for r in low_samples if abs(r['z']-4.8468)>2e-6 or r['normal'][2]>-.99]
changed=sorted(n for n in fp1 if n in fp0 and fp1[n]!=fp0[n]);removed=sorted(set(fp0)-set(fp1));added=sorted(set(fp1)-set(fp0))
scope=changed==sorted(fix.CHANGED) and removed==sorted(fix.REMOVED) and not added
regress=[{'id':a['id'],'baseline':b['failure'],'candidate':a['failure']} for a,b in zip(path1,path0) if a['failure'] and not b['failure']]
top=max(p.z for p in v);upper=[]
for n in ('MAIN_L2_elongated_roof','MAIN_L3_TERRACE_slab'):
    vv,_=evaluated(n);bottom=min(p.z for p in vv);upper.append({'object':n,'bottom_z':bottom,'candidate_top_z':top,'vertical_gap_m':bottom-top,'pass':bottom-top>0})
leaf_size_ok=all(abs(mesh_metrics(n)['signed_volume_m3']-leaf0[n]['metrics']['signed_volume_m3'])<2e-6 for n in fix.LEAF_NAMES)
counts={'scope_pass':scope,'objects_before':len(fp0),'objects_after':len(fp1),'outside_protected':len(fp0)-len(fix.CHANGED)-len(fix.REMOVED),'unchanged_materials':mat0==mat1,'unchanged_settings':set0==settings(),'closed_positive_all':all(r['pass'] for r in metrics),'single_stepped_ceiling':metrics[0]['components']==[metrics[0]['faces']],'low_plane_sample_count':len(low_samples),'low_plane_fail_count':len(lowbad),'new_path_failures':len(regress),'old_gait_pass':step0['status'].startswith('PASS'),'new_original_gait_pass':step1['status'].startswith('PASS'),'new_fixed_torso_gait_C_pass':stepC['status'].startswith('PASS'),'leaf_rigid_volumes_preserved':leaf_size_ok,'upper_gap_positive':all(r['pass'] for r in upper)}
report={'source':str(SRC),'source_sha256':SHA,'helper_sha256':sha(R/'scripts/master_ceiling11.py'),'manifest':manifest,'counts':counts,'metrics':metrics,'paths_before':path0,'paths_after':path1,'new_path_failures':regress,'upper_separation':upper,'contacts_before':contacts0,'contacts_after':contacts1,'new_surface_contacts':newcontacts,'low_plane_bad':lowbad,'low_plane_samples':sample_rows,'leaf_before':leaf0,'leaf_after':{n:{'metrics':mesh_metrics(n),'matrix':[list(r) for r in s.objects[n].matrix_world]} for n in fix.LEAF_NAMES},'fingerprints_before':fp0,'fingerprints_after':fp1,'material_fingerprints_before':mat0,'material_fingerprints_after':mat1,'settings_before':set0,'settings_after':settings(),'protected_files_unchanged':{p:sha(p)==v for p,v in protected0.items()},'rendered':False,'visual_status':'NOT_RUN','GEO07':'NOT_RUN','height_discrepancy':'OPEN','navigation_limit':'Original10 raised-torso gait retained as separate failure if roof hits. QA-only fixed-torso gait is not installed into saved tour or production data.'}
ok=scope and mat0==mat1 and set0==settings() and counts['closed_positive_all'] and not lowbad and not regress and leaf_size_ok and counts['upper_gap_positive']
if ok:
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT));report.update(candidate=str(OUT),candidate_sha256=sha(OUT),status='SAVED_LOCAL_CANDIDATE_GAIT_AND_VISUAL_REVIEW_REQUIRED')
else:report['status']='FAIL_NOT_SAVED'
(Q/'master-ceiling11-build-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'counts':counts,'status':report['status'],'candidate':report.get('candidate'),'sha256':report.get('candidate_sha256'),'new_surface_contacts':newcontacts,'regressions':regress},indent=2),flush=True)
assert ok
