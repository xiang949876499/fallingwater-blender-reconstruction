"""Independent frozen09 bridge candidate, fingerprints and physical evidence."""
import bpy,sys,json,hashlib,time,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'qa'))
import bridge_detail10 as detail
import shrub08_auditlib as audit
SOURCE=ROOT/'scene/Fallingwater_iteration09.blend'
TARGET=ROOT/'scene/Fallingwater_bridge_candidate10_meshclean.blend'
Q=ROOT/'qa'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(SOURCE)==detail.SOURCE_SHA256
assert not TARGET.exists(),'Never overwrite an existing independent candidate'
manifest=json.loads((Q/'bridge10-source-probe.json').read_text())
oldnames=manifest['exact_replace_names']
route=json.loads((Q/'bridge10-frozen-route09.json').read_text())
assert route['source_scene_sha256']==detail.SOURCE_SHA256
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene
source_frame=scene.frame_current
report={'status':'RUNNING','source_sha256':sha(SOURCE),'candidate':str(TARGET),'source_frame':source_frame,
        'comparison_frame':48,'rendered':False,'production_changed':False,
        'dependencies':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'scripts/bridge_detail10.py',Q/'shrub08_auditlib.py',Q/'bridge10-source-probe.json',Q/'bridge10-frozen-route09.json']}}
start=time.monotonic()
try:
    print('BRIDGE10 before fingerprint',flush=True)
    before=audit.snapshot()
    oldmesh={scene.objects[n].data.name for n in oldnames}
    scene.frame_set(48);bpy.context.view_layer.update()
    physics_names=[o.name for o in scene.objects if o.type=='MESH' and o.name.startswith(('SITE_Core_','SITE_Cascade_Shoulder_Continuous','WATER_'))]
    physics_before={n:audit.physical_hash(scene.objects[n]) for n in physics_names}
    ob,oo=audit.world_bvh([scene.objects[n] for n in oldnames],True)
    print('BRIDGE10 apply construction candidate',flush=True)
    application=detail.apply(oldnames);report['application']=application
    new=[scene.objects[n] for n in detail.NEW_NAMES]
    nb,no=audit.world_bvh(new,True)
    nav=audit.route_regression(route,ob,oo,nb,no);nav['scope']='Frozen full09 route versus removed and added bridge meshes; all retained scene objects fingerprinted.'
    report['route_regression']=nav
    print('BRIDGE10 route new obstacles',len(nav['new_obstacles']),flush=True)
    camera=[]
    for obj in scene.objects:
        if obj.type!='CAMERA':continue
        p=obj.matrix_world.translation
        h,n,i,d=nb.find_nearest(p)
        camera.append({'name':obj.name,'frame':48,'location':list(p),'nearest_bridge_object':no[i] if h else None,
                       'clearance_m':d,'passes_0_20m_clearance':d is None or d>=.20})
    report['camera_clearance']=camera
    # Actual evaluated ray hits on the opposing stone END FACES, not object bounds.
    stone=[scene.objects[n] for n in detail.NEW_NAMES[2:6]]
    sb,so=audit.world_bvh(stone,True)
    stations=[]
    for y in (-2.95,-2.80,-2.60):
        for z in (.10,.30,.48):
            origin=Vector((27.44974,y,z));a,an,ai,ad=sb.ray_cast(origin,Vector((-1,0,0)),6)
            b,bn,bi,bd=sb.ray_cast(origin,Vector((1,0,0)),6)
            row={'y':y,'z':z,'left':list(a) if a else None,'right':list(b) if b else None,
                 'left_owner':so[ai] if a else None,'right_owner':so[bi] if b else None,
                 'left_normal':list(an) if an else None,'right_normal':list(bn) if bn else None,
                 'gap_m':b.x-a.x if a is not None and b is not None else None}
            row['pass']=row['gap_m'] is not None and abs(row['gap_m']-4.0386)<.00002 and an.x>.999 and bn.x<-.999
            stations.append(row)
    report['south_source_nominal_endpoint_rays']=stations
    # New bridge intersections against every old water surface, terrain excluded.
    water_overlap=[]
    for obj in [scene.objects[n] for n in physics_names if n.startswith('WATER_')]:
        if not any(audit.box_overlap(audit.bounds(obj),audit.bounds(o)) for o in new):continue
        wb,wo=audit.world_bvh([obj],True)
        pairs=nb.overlap(wb)
        if pairs:
            by={}
            for a,b in pairs:by[no[a]]=by.get(no[a],0)+1
            water_overlap.append({'water_object':obj.name,'triangle_or_polygon_overlap_pairs':len(pairs),'bridge_owners':by})
    report['old_water_surface_intersections']=water_overlap
    # Evaluate actual lower terrain contact at each foundation boundary vertex.
    terrain=scene.objects['SITE_Continuous_BearRun_Terrain'];tb,_=audit.world_bvh([terrain],True)
    support=[]
    for obj,record in zip(stone,application['stone_returns']):
        count=record['contact_outline_samples'];gaps=[]
        for vert in list(obj.data.vertices)[:count]:
            p=obj.matrix_world@vert.co
            hit=tb.ray_cast(Vector((p.x,p.y,30)),Vector((0,0,-1)),80)[0]
            gaps.append(p.z-hit.z)
        support.append({'object':obj.name,'boundary_samples':count,'base_gap_range_m':[min(gaps),max(gaps)],
                        'pass':all(-.02001<=v<=-.01999 for v in gaps)})
    report['actual_terrain_support']=support
    # Original deck, flags, deep abutments, path vertices, all core/water triangles frozen.
    assert physics_before=={n:audit.physical_hash(scene.objects[n]) for n in physics_names}
    report['protected_physics']=physics_before
    report['new_physical_hashes']={o.name:audit.physical_hash(o) for o in new}
    scene.frame_set(source_frame);bpy.context.view_layer.update()
    print('BRIDGE10 after fingerprint',flush=True)
    after=audit.snapshot()
    removed=set(before['objects'])-set(after['objects']);added=set(after['objects'])-set(before['objects'])
    assert removed==set(oldnames),(removed^set(oldnames))
    assert added==set(detail.NEW_NAMES),(added^set(detail.NEW_NAMES))
    retained=set(before['objects'])-removed
    changed=[n for n in retained if before['objects'][n]!=after['objects'][n]]
    assert not changed,changed
    assert before['global']==after['global'],'Global material/light/camera/scene settings changed'
    assert all(after['meshes'].get(n)==v for n,v in before['meshes'].items() if n not in oldmesh),'Protected original mesh changed'
    report['fingerprint']={'retained_object_count':len(retained),'unchanged_all_retained':True,'removed':sorted(removed),'added':sorted(added),
                           'retained_bridge_names':manifest['retain_names'],'original_globals_equal':True,'snapshot_sha256':audit.digest(after)}
    compact={'snapshot_sha256':audit.digest(after),'objects':{k:audit.digest(v) for k,v in after['objects'].items()},
             'global':audit.digest(after['global']),'meshes':after['meshes']}
    (Q/'bridge10-candidate-fingerprint.json').write_text(json.dumps(compact,separators=(',',':')),encoding='utf8')
    # Preserve a reviewable negative candidate if contact or route checks fail.
    issues=[]
    if nav['new_obstacles']:issues.append('NEW_ROUTE_OBSTACLE')
    if any(not r['passes_0_20m_clearance'] for r in camera):issues.append('CAMERA_CLEARANCE')
    if not all(r['pass'] for r in stations):issues.append('SOUTH_ENDPOINT_MEASUREMENT')
    if not all(r['pass'] for r in support):issues.append('TERRAIN_SUPPORT')
    if water_overlap:issues.append('NEW_MASONRY_INTERSECTS_OLD_WATER_SURFACE')
    report['issues']=issues
    report['status']='PHYSICAL_CHECK_ISSUES_REVIEW_ONLY' if issues else 'PASS_PHYSICAL_AND_FINGERPRINT_NO_VISUAL_ACCEPTANCE'
    assert sha(SOURCE)==detail.SOURCE_SHA256
    bpy.ops.wm.save_as_mainfile(filepath=str(TARGET),compress=True)
    report['candidate_sha256']=sha(TARGET)
except Exception as error:
    report['status']='FAILED_NO_PRODUCTION_INTEGRATION';report['exception']=repr(error)
    raise
finally:
    report['elapsed_s']=time.monotonic()-start
    (Q/'bridge10-candidate-check.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print('BRIDGE10_RESULT',json.dumps({k:report.get(k) for k in ('status','candidate','candidate_sha256','issues','elapsed_s')}),flush=True)
