"""Full original preservation and actual local surfaces/window/nav checks."""
import bpy,sys,json,hashlib,time,math
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'scripts'),str(R/'qa')]
import masonry_wall12 as helper
import shrub08_auditlib as audit
SOURCE=R/'scene/Fallingwater_navigation_candidate10a.blend'
SHA='1e7b17d9c2396513f005724e50788bf834097eedb401b91a7f1030825e2c4ed9'
TARGET=R/'scene/Fallingwater_masonry_wall_candidate12a.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,data):(R/'qa'/name).write_text(json.dumps(data,indent=2),encoding='utf8')
def snapshot():return json.loads(json.dumps(audit.snapshot()))
def strict_integer_regression(scene,app):
    """Saved FCurves versus added static finish; original actions unchanged."""
    route=json.loads((R/'qa/masonry-wall12-frozen-route.json').read_text())
    tree,owners=audit.world_bvh([scene.objects[n] for n in app['new_objects']],True)
    failures=[];rays=0;frames=0;segments=[]
    def ray(p,d,length,label,frame,method):
        nonlocal rays
        rays+=1;hit,n,i,dist=tree.ray_cast(p,d,length)
        if hit is not None:failures.append({'segment':label,'frame':frame,'method':method,'new_object':owners[i],'point':list(hit)})
    for name,shots in ((route['main_camera'],route['main_segments']),(route['supplemental_camera'],route['supplemental_segments'])):
        cam=scene.objects[name];assert not cam.parent and not cam.constraints and not cam.animation_data.drivers
        curves=[c for l in cam.animation_data.action.layers for st in l.strips for bag in st.channelbags for c in bag.fcurves]
        assert all(k.interpolation=='LINEAR' for c in curves for k in c.keyframe_points)
        index={(c.data_path,c.array_index):c for c in curves}
        for shot in shots:
            walking=bool(shot.get('body_clearance_tested',shot['mode'].startswith('NORMAL')));previous=None;count=0
            for fr in range(shot['start_frame'],shot['end_frame']+1):
                p=Vector([index['location',i].evaluate(fr) for i in range(3)]);frames+=1;count+=1
                for d in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):ray(p,Vector(d),.18,shot['id'],fr,'CAMERA_ENVELOPE')
                if walking:
                    bottom=.24 if 'STAIRS' in shot['mode'] else .09
                    for x,y in ((0,0),(-.18,0),(.18,0),(0,-.18),(0,.18)):
                        ray(p+Vector((x,y,-1.6+bottom)),Vector((0,0,1)),1.95-bottom,shot['id'],fr,'BODY_1.95m')
                if previous is not None:
                    delta=p-previous
                    if delta.length>1e-7:
                        cross=Vector((-delta.y,delta.x,0));cross=cross.normalized() if cross.length>1e-9 else Vector((1,0,0))
                        offsets=[cross*side+Vector((0,0,h-1.6)) for side in (-.18,0,.18) for h in (.3,.72,1.13,1.95)] if walking else [Vector(),cross*.18,-cross*.18]
                        for offset in offsets:ray(previous+offset,delta.normalized(),delta.length,shot['id'],fr,'INTEGER_FRAME_SWEEP')
                previous=p
            segments.append({'id':shot['id'],'frames':count,'body_height_m':1.95 if walking else None,'body_radius_m':.18 if walking else None})
    result={'status':'PASS' if not failures else 'FAIL','frames':frames,'rays':rays,'failures':failures,'segments':segments,
            'method':'Every integer saved linear FCurve camera location plus per-frame body/head and inter-frame sweeps against only new static finish. Original action/matrix fingerprints are unchanged. Window is not relabeled a walking connection.'}
    assert frames==7584
    dump('masonry-wall12-reopen-integer-frames.json',result);assert not failures,('Added finish obstructs strict saved-frame body',failures[:12])
    return result

def physical(scene,app):
    records=[];vv=[];ff=[];identities=[];bad=[]
    added=[scene.objects[n] for n in app['new_objects']];finish,owners=audit.world_bvh(added,True)
    for face in app['faces']:
        ob=scene.objects[face['object']];substrate,_=audit.world_bvh([scene.objects[face['substrate']]],True)
        for c in face['stones']:
            st,n=c['vertex_start'],c['vertex_count'];f0,fn=c['face_start'],c['face_count']
            v=[ob.matrix_world@q.co for q in list(ob.data.vertices)[st:st+n]]
            f=[tuple(i-st for i in p.vertices) for p in list(ob.data.polygons)[f0:f0+fn]]
            edges=Counter(tuple(sorted((a,b))) for p in f for a,b in zip(p,p[1:]+p[:1]))
            volume=sum(v[a].dot(v[b].cross(v[d]))/6 for a,b,d in f)
            minarea=min((v[b]-v[a]).cross(v[d]-v[a]).length/2 for a,b,d in f)
            assert all(i==2 for i in edges.values()) and volume>1e-9 and minarea>1e-10,(ob.name,c['id'],volume,minarea)
            contact=[]
            for pt in [*v[15:],Vector((c['plane_x']+helper.EMBED,(c['yz_rectangle'][0]+c['yz_rectangle'][1])/2,(c['yz_rectangle'][2]+c['yz_rectangle'][3])/2))]:
                hit,normal,idx,d=substrate.find_nearest(pt);signed=(pt-hit).dot(normal)
                contact.append(signed)
            assert min(contact)>-.00105 and max(contact)<-.00055,(ob.name,c['id'],contact)
            for q in v:
                if not all(face['envelope_xyz'][2*i]-.000002<=q[i]<=face['envelope_xyz'][2*i+1]+.000002 for i in range(3)):raise AssertionError('Finish envelope')
            records.append({'object':ob.name,'id':c['id'],'vertices':n,'triangles':fn,'closed_oriented':True,'signed_volume_m3':volume,
                            'minimum_triangle_area_m2':minarea,'back_contact_signed_range_m':[min(contact),max(contact)],'contact_samples':len(contact)})
            off=len(vv);vv+=v;ff.extend(tuple(off+i for i in p) for p in f);identities.extend([ob.name+':'+c['id']]*len(f))
    whole=BVHTree.FromPolygons(vv,ff,all_triangles=True)
    cross=[(a,b) for a,b in whole.overlap(whole) if a<b and identities[a]!=identities[b]]
    assert not cross,('Stone component overlaps',cross[:10])
    # Every non-target actual mesh potentially meeting added finish. Source
    # substrate contact is intentional; all other surfaces must remain clear.
    neighbors=[];envelopes=[f['envelope_xyz'] for f in app['faces']]
    for o in scene.objects:
        if o.type!='MESH' or o.name in helper.TARGETS or o.name in app['new_objects'] or o.hide_render:continue
        if any(helper.overlap(helper.bounds(o),b) for b in envelopes):neighbors.append(o)
    if neighbors:
        tree,onames=audit.world_bvh(neighbors,True);hits=tree.overlap(finish)
        bad=[{'neighbor':onames[a],'finish':owners[b]} for a,b in hits]
    assert not bad,('Protected mesh intersection',bad[:20])
    core_object=scene.objects[helper.TARGETS[1]]
    evaluated=core_object.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh();mesh.calc_loop_triangles()
    cv=[evaluated.matrix_world@v.co for v in mesh.vertices]
    ce=Counter(tuple(sorted((a,b))) for p in mesh.polygons for a,b in zip(list(p.vertices),list(p.vertices)[1:]+list(p.vertices)[:1]))
    volume=sum(cv[t.vertices[0]].dot(cv[t.vertices[1]].cross(cv[t.vertices[2]]))/6 for t in mesh.loop_triangles)
    original_bounds=app['window_cut']['source_bounds']
    assert all(n==2 for n in ce.values()) and volume>0,'Core after genuine aperture is not closed/oriented'
    assert all(original_bounds[2*i]-.000002<=p[i]<=original_bounds[2*i+1]+.000002 for p in cv for i in range(3))
    core_report={'evaluated_vertices':len(cv),'evaluated_triangles':len(mesh.loop_triangles),'closed_edges_degree_two':True,
                 'signed_volume_m3':volume,'outer_bounds_preserved':True}
    evaluated.to_mesh_clear()
    core,_=audit.world_bvh([core_object],True)
    y0,y1,z0,z1=helper.OPENING;opening=[];frame=[];bb=app['window_cut']['source_bounds']
    for j in range(9):
        y=y0+.035+(y1-y0-.07)*j/8
        for k in range(7):
            z=z0+.04+(z1-z0-.08)*k/6
            for direction in (-1,1):
                p=Vector((bb[0]-.10 if direction>0 else bb[1]+.10,y,z));hit,normal,index,d=core.ray_cast(p,Vector((direction,0,0)),bb[1]-bb[0]+.20)
                assert hit is None,('Window still blocked',list(p),list(hit))
                f_hit=finish.ray_cast(Vector((bb[0]-.10,y,z)),Vector((1,0,0)),bb[1]-bb[0]+.20)[0]
                assert f_hit is None,'Finish covers window'
                opening.append({'from':list(p),'direction':[direction,0,0],'core_hit':False,'finish_hit':False})
    x=-4.2444
    for j in range(7):
        z=z0+.08+(z1-z0-.16)*j/6
        frame.extend([Vector((x,y0-.010,z)),Vector((x,y1+.010,z))])
    for j in range(7):
        y=y0+.055+(y1-y0-.11)*j/6
        frame.extend([Vector((x,y,z0-.010)),Vector((x,y,z1+.010))])
    seating=[]
    for p in frame:
        h,n,i,d=core.find_nearest(p);signed=(p-h).dot(n)
        assert -.011<signed<-.009,('Frame perimeter lost substrate support',list(p),signed)
        seating.append({'point':list(p),'signed_inside_stone_m':signed})
    return {'stone_checks':records,'core_topology':core_report,'contact_samples':sum(r['contact_samples'] for r in records),'cross_component_intersections':0,
            'protected_objects_checked':[o.name for o in neighbors],'protected_mesh_intersections':0,
            'actual_window_core_and_finish_rays':opening,'frame_seating_points':seating,'window_body_passage_claim':False,
            'window_note':'A glazed/operable window, not a walking connection; rays test core aperture separately from retained glass/frame.'}

assert sha(SOURCE)==SHA
if '--readback' in sys.argv:
    report=json.loads((R/'qa/masonry-wall12-check.json').read_text());assert sha(TARGET)==report['candidate_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(TARGET));s=bpy.context.scene
    expected=json.loads((R/'qa/masonry-wall12-candidate-fingerprint.json').read_text());actual=snapshot()
    if actual!=expected:dump('masonry-wall12-reopen-differences.json',{k:[n for n in set(actual[k])|set(expected[k]) if actual[k].get(n)!=expected[k].get(n)] for k in actual})
    assert actual==expected,'Saved snapshot mismatch'
    result=physical(s,report['application']);dump('masonry-wall12-reopen-physical.json',result)
    movie=strict_integer_regression(s,report['application'])
    out={'status':'PASS_INDEPENDENT_REOPEN_LOCAL_PHYSICS','candidate_sha256':report['candidate_sha256'],'snapshot_exact':True,
         'stone_count':len(result['stone_checks']),'contact_samples':result['contact_samples'],'window_rays':len(result['actual_window_core_and_finish_rays']),
         'frame_seating_points':len(result['frame_seating_points']),'source_unchanged':sha(SOURCE)==SHA,'rendered':False,'visual_status':'NOT_RUN'}
    out['integer_frames']=movie['frames'];out['strict_integer_body_sweep_rays']=movie['rays'];out['integer_frame_failures']=len(movie['failures'])
    dump('masonry-wall12-reopen.json',out);print(json.dumps(out),flush=True)
else:
    assert not TARGET.exists(),'Preserve candidate checkpoint'
    report={'status':'RUNNING','source_sha256':SHA,'candidate':str(TARGET),'rendered':False};t=time.monotonic()
    try:
        bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;original_frame=s.frame_current;bpy.context.view_layer.update()
        print('WALL12_SOURCE_SNAPSHOT',flush=True);before=snapshot()
        old,oldowners=audit.world_bvh([s.objects[n] for n in helper.TARGETS],True)
        app=helper.apply(s);report['application']=app;print('WALL12_CREATED',app['component_count'],flush=True)
        report['physical']=physical(s,app)
        route_path=R/'qa/integration10-navigation-workspace/data/tour-route.json';raw=route_path.read_bytes();route=json.loads(raw)
        dump('masonry-wall12-frozen-route.json',route);report['route_sha256']=sha(route_path)
        new,newowners=audit.world_bvh([s.objects[n] for n in [*helper.TARGETS,*app['new_objects']]],True)
        report['route_changed_geometry_regression']=audit.route_regression(route,old,oldowners,new,newowners)
        assert not report['route_changed_geometry_regression']['new_obstacles']
        finish,owners=audit.world_bvh([s.objects[n] for n in app['new_objects']],True)
        cameras=[]
        for c in [o for o in s.objects if o.type=='CAMERA']:
            h,n,i,d=finish.find_nearest(c.matrix_world.translation);cameras.append({'name':c.name,'nearest_new_finish_m':d,'owner':owners[i]})
        assert len(cameras)==131 and min(c['nearest_new_finish_m'] for c in cameras)>.18
        report['all_131_cameras']=cameras;movies=[]
        for name,segs in ((route['main_camera'],route['main_segments']),(route['supplemental_camera'],route['supplemental_segments'])):
            cam=s.objects[name];assert cam.parent is None and not cam.constraints and not cam.animation_data.drivers
            curves=[c for l in cam.animation_data.action.layers for strip in l.strips for bag in strip.channelbags for c in bag.fcurves]
            index={(c.data_path,c.array_index):c for c in curves};minimum=1e6;count=0;matrix_error=0
            for seg in segs:
                for fr in range(seg['start_frame'],seg['end_frame']+1):
                    p=Vector([index['location',i].evaluate(fr) for i in range(3)]);h,n,i,d=finish.find_nearest(p);minimum=min(minimum,d);count+=1
                for fr in (seg['start_frame'],seg['end_frame']):
                    s.frame_set(fr);p=Vector([index['location',i].evaluate(fr) for i in range(3)])
                    matrix_error=max(matrix_error,(cam.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation-p).length)
            assert minimum>.18 and matrix_error<1e-5;movies.append({'camera':name,'frames':count,'minimum_new_finish_clearance_m':minimum,'evaluated_matrix_error':matrix_error})
        report['movie_frame_positions']=movies;assert sum(m['frames'] for m in movies)==7584
        s.frame_set(original_frame);bpy.context.view_layer.update();after=snapshot()
        changed=[n for n,v in before['objects'].items() if after['objects'].get(n)!=v]
        assert changed==[helper.TARGETS[1]],changed
        a=json.loads(json.dumps(before['objects'][changed[0]]));b=json.loads(json.dumps(after['objects'][changed[0]]))
        for row in (a,b):row.pop('data_hash');row['properties'].pop('data',None)
        assert a==b,'Core object changed outside explicit mesh hole'
        added=set(after['objects'])-set(before['objects']);assert added==set(app['new_objects'])
        oldmesh=before['objects'][helper.TARGETS[1]]['properties']['data']
        for n,v in before['meshes'].items():
            if n in after['meshes']:assert after['meshes'][n]==v
        for field,a in before['global'].items():
            b=after['global'][field]
            if field in ('materials','collections'):assert all(b.get(n)==v for n,v in a.items()),field
            else:assert a==b,field
        report.update(status='PASS_LOCAL_PHYSICAL_AND_CHANGED_OBJECT_REGRESSION_VISUAL_NOT_RUN',
                      original_objects_unchanged=len(before['objects'])-1,changed_original_objects=changed,
                      new_objects=sorted(added),shared_materials_images_cameras_world_lights_unchanged=True,
                      original_source_frame_preserved=original_frame,helper_sha256=sha(R/'scripts/masonry_wall12.py'))
        dump('masonry-wall12-candidate-fingerprint.json',after)
        bpy.ops.wm.save_as_mainfile(filepath=str(TARGET),compress=True);report['candidate_sha256']=sha(TARGET)
        assert sha(SOURCE)==SHA
    except Exception as exc:
        report['status']='FAIL_PRESERVED_LOCAL_CANDIDATE_ATTEMPT';report['exception']=repr(exc);raise
    finally:
        report['seconds']=time.monotonic()-t;dump('masonry-wall12-check.json',report)
        print('WALL12_RESULT',report['status'],report.get('exception'),report['seconds'],flush=True)
