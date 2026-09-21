"""Bounded composition repair after actual images, with room-owned target witnesses."""
import sys,json,math,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import bpy
from mathutils import Vector
import camera_review as cr
scene_path=Path(sys.argv[sys.argv.index('--scene')+1]).resolve() if '--scene' in sys.argv else ROOT/'scene/Fallingwater_iteration04.blend'
bpy.ops.wm.open_mainfile(filepath=str(scene_path))
scene=bpy.context.scene;geo=cr.Geometry(scene)
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string());rm={r['id']:r for r in rooms}
frozen=json.loads((ROOT/'qa/camera04-settings-frozen.json').read_text())
extra='--extra' in sys.argv
selected=sys.argv[sys.argv.index('--selected')+1].split(',') if '--selected' in sys.argv else None
prefix='camera04-composition-refined' if selected else ('camera04-composition-extended' if extra else 'camera04-composition')
if '--output-prefix' in sys.argv:prefix=sys.argv[sys.argv.index('--output-prefix')+1]
stair_prefix={'MAIN_L1_STAIR':'MAIN_stair1_','MAIN_L2_STAIR':'MAIN_stair2_','MAIN_L1_SERVICE_STAIR':'MAIN_service_stair_',
              'GUEST_B1_STAIR':'GUEST_LAUNDRY_DESCENT_tread_','MAIN_L1_HATCH':'MAIN_water_stair_','MAIN_L3_STAIR':'MAIN_stair2_',
              'MAIN_B_STAIR':'MAIN_service_stair_','GUEST_L1_STAIR_HALL':'GUEST_SERVICE_ASCENT_tread_'}
requested=('MAIN_L3_BATH','GUEST_B1_BATH','GUEST_L1_BATH','GUEST_L2_BATH','GUEST_B1_STAIR','MAIN_L1_HATCH','MAIN_L3_STAIR','GUEST_L1_BOILER') if extra else ('MAIN_B_BATH','MAIN_L1_SERVANT','MAIN_L2_BATH_G','MAIN_L2_BATH_M','MAIN_L2_BATH_N','MAIN_L1_STAIR','MAIN_L2_STAIR','MAIN_L1_SERVICE_STAIR')
if selected:requested=tuple(selected)
settings=json.loads((ROOT/'qa/camera04-composition-extended-candidates.json').read_text()) if selected else (json.loads((ROOT/'qa/camera04-composition-candidates.json').read_text()) if extra else {})
if '--base-settings' in sys.argv:settings=json.loads(Path(sys.argv[sys.argv.index('--base-settings')+1]).read_text(encoding='utf-8-sig'))
report={'scene':bpy.data.filepath,'geometry':geo.counts,'scope':'Post-image composition candidates, not visual acceptance. Stored 120-camera render settings remain unchanged. Framing emphasizes real room-owned fittings or the named stair flight; contains explicit safe support/body checks. Normal-room views use level camera with negative lens shift to include low furnishings.', 'rooms':[]}
if extra:report['rooms']=json.loads((ROOT/'qa/camera04-composition-geometry.json').read_text())['rooms']
if selected:report['rooms']=[r for r in json.loads((ROOT/'qa/camera04-composition-extended-geometry.json').read_text())['rooms'] if r['room_id'] not in selected]
if '--base-report' in sys.argv:report['rooms']=[r for r in json.loads(Path(sys.argv[sys.argv.index('--base-report')+1]).read_text(encoding='utf-8-sig'))['rooms'] if r['room_id'] not in requested]
def bbox(obj):
    return [obj.matrix_world@Vector(q) for q in obj.bound_box]
for rid in requested:
    room=rm[rid];is_stair=rid in stair_prefix;witness=[];targets=[]
    seats=[o for o in scene.objects if o.type=='EMPTY' and o.get('room_id')==rid and 'settee' in o.get('asset_type','')]
    if is_stair:
        objs=[o for o in geo.objects.values() if o.name.startswith(stair_prefix[rid]) and o.type=='MESH' and not any(k in o.name.lower() for k in ('rail','baluster','soffit'))]
        for ob in objs:
            bb=bbox(ob);point=sum(bb,Vector())/8;point.z=max(q.z for q in bb)+.025
            witness.append((point,ob.name));targets.append(point+Vector((0,0,.10)))
        zmin=min(q.z for q,_ in witness)-.05;zmax=max(q.z for q,_ in witness)+.2
    else:
        for ob in geo.objects.values():
            if rid=='GUEST_L1_LOUNGE' and ob.name.startswith('GUEST_FIREPLACE'):
                witness.append((sum(bbox(ob),Vector())/8,'GUEST_FIREPLACE'));continue
            if ob.get('room_id')!=rid or ob.get('component_type')!='furniture':continue
            if 'lamp' in ob.get('asset_type',''):continue
            bb=bbox(ob);point=sum(bb,Vector())/8
            witness.append((point,ob.get('asset_id',ob.name)))
        # Cap each assembly's repeated parts so many handles do not dominate a WC.
        groups=collections.defaultdict(list)
        for point,owner in witness:groups[owner].append(point)
        witness=[]
        for owner,points in groups.items():
            ordered=sorted(points,key=lambda p:p.z)
            samples=[ordered[round(i*(len(ordered)-1)/6)] for i in range(7)]
            witness.extend((q,owner) for q in samples)
            targets.append(sum(points,Vector())/len(points))
        targets.append(Vector((*room['center'][:2],room['z']+.8)))
    candidates=[];rejected=collections.Counter()
    xy_points=cr.points(room,geo)
    if is_stair:
        xy_points.extend((q.x,q.y) for q,_ in witness)
        ex,ey=room['entry'][:2]
        xy_points.extend((ex+dx,ey+dy) for dx,dy in ((.3,0),(-.3,0),(0,.3),(0,-.3),(.6,0),(-.6,0),(0,.6),(0,-.6)))
        ordered=sorted((q for q,_ in witness),key=lambda q:q.z)
        for endpoint,inside_point in ((ordered[0],ordered[-1]),(ordered[-1],ordered[0])):
            outward=Vector((endpoint.x-inside_point.x,endpoint.y-inside_point.y,0)).normalized()
            side=Vector((-outward.y,outward.x,0))
            for length in (.25,.45,.65,.85):
                for sideways in (0,-.15,.15):
                    q=endpoint+outward*length+side*sideways;xy_points.append((q.x,q.y))
    for xy in xy_points:
        for offset in ([3,.32,-.5,-1.3,-2.1] if is_stair else [.32]):
            hit,issue=geo.support(xy,room,offset)
            if issue:rejected[issue]+=1;continue
            if is_stair and not (zmin<=hit['location'][2]<=zmax and (hit['object'].startswith(stair_prefix[rid]) or any(k in hit['object'].lower() for k in ('landing','threshold','finish','floor')))):
                continue
            eye=Vector((*xy,hit['location'][2]+1.6))
            if seats and any((seat.matrix_world.inverted()@eye).y>-.05 for seat in seats):
                rejected['SEATING_REAR_VIEW']+=1;continue
            problem=geo.clearance(eye,hit['location'][2])
            if problem:rejected[problem['reason']]+=1;continue
            for aim in targets:
                distance=math.dist(eye[:2],aim[:2])
                if distance<.45:continue
                target=aim if is_stair else Vector((aim.x,aim.y,eye.z))
                forward=(target-eye).normalized();right=forward.cross(Vector((0,0,1))).normalized();up=right.cross(forward).normalized()
                shift=0 if is_stair else max(-.58,min(.12,(aim.z-eye.z)*28/(36*distance)))
                visible=collections.Counter();framed=0;hidden=collections.Counter()
                for q,owner in witness:
                    delta=q-eye;depth=delta.dot(forward)
                    if depth<=.05:continue
                    ux=.5+delta.dot(right)*28/(36*depth);vy=.5+delta.dot(up)*28/(20.25*depth)-shift*36/20.25
                    if not(.07<ux<.93 and .06<vy<.94):continue
                    framed+=1;cast=geo.ray(eye,delta,delta.length+.12)
                    if cast and (cast['object']==owner or geo.objects[cast['object']].get('asset_id')==owner or owner=='GUEST_FIREPLACE' and cast['object'].startswith(owner)):visible[owner]+=1
                    elif cast:hidden[cast['object']]+=1
                grid=collections.Counter()
                for u in (-.65,0,.65):
                    for v in (-.65,0,.65):
                        ray=forward+right*(u*18/28)+up*((v*10.125+shift*36)/28)
                        cast=geo.ray(eye,ray,15)
                        if cast:
                            ob=geo.objects[cast['object']]
                            if cast['object']=='SITE_Continuous_BearRun_Terrain':grid['terrain']+=1
                            if cast['distance']<.6:grid['near_surface']+=1
                            if ob.get('room_id')==rid:grid['room_owned']+=1
                score=sum(min(n,4) for n in visible.values())*1.1+len(visible)*2+framed*.035-grid['terrain']*.65-grid['near_surface']*.9
                if not visible:continue
                candidates.append({'location':cr.plain(eye),'target':cr.plain(target),'lens':28,'shift_y':round(shift,5),'shift_x':0,
                                   'support_z':hit['location'][2],'support_object':hit['object'],'outside_room_polygon':not cr.inside(eye,room['polygon']),
                                   'score':score,'visible_witnesses':dict(visible),'framed_witnesses':framed,'hidden_by':hidden.most_common(5),'frame_grid':dict(grid)})
    if not candidates:
        report['rooms'].append({'room_id':rid,'status':'NO_USEFUL_CAMERA_FOUND','rejections':dict(rejected)});continue
    candidates.sort(key=lambda c:-c['score']);a=candidates[0];va=(Vector(a['target'])-Vector(a['location'])).normalized()
    others=[c for c in candidates if math.dist(c['location'],a['location'])>=.55]
    if is_stair:
        lower=[c for c in others if c['support_z']<a['support_z']-.5 and (Vector(c['target'])-Vector(c['location'])).normalized().z>-.25]
        if lower:others=lower
    def complement(c):
        vb=(Vector(c['target'])-Vector(c['location'])).normalized()
        unseen={k:n for k,n in c['visible_witnesses'].items() if k not in a['visible_witnesses']}
        novel=sum(min(n,4) for n in unseen.values())*2.5+len(unseen)*3 if not is_stair else 0
        return c['score']+min(3,math.dist(c['location'],a['location']))*.8+(1-va.dot(vb))*1.5+novel
    chosen=[a,max(others,key=complement)] if others else [a]
    for suffix,c in zip(('A','B'),chosen):
        name='CAM_'+rid+'_'+suffix
        if name in ('CAM_MAIN_L1_HATCH_B','CAM_GUEST_L1_STAIR_HALL_B'):
            settings[name]=dict(frozen[name])
            settings[name]['evidence']+=' Retained actually readable iteration04 image direction; recheck against rebuilt geometry. This point was not blindly replaced by the new composition search.'
            continue
        settings[name]={k:c[k] for k in ('location','target','lens','shift_x','shift_y','support_z','support_object','outside_room_polygon')}
        settings[name].update(exposure=frozen[name]['exposure'],room_id=rid,evidence='Post-image candidate using '+Path(bpy.data.filepath).name+'. Measured support/body/eye clearance; actual room-owned fitting or named-stair witnesses in shifted camera frame. Actual render review pending.',render_reviewed=False)
    possible={}
    for c in candidates:
        for key,n in c['visible_witnesses'].items():possible[key]=max(possible.get(key,0),n)
    report['rooms'].append({'room_id':rid,'source_scene':bpy.data.filepath,'status':'CANDIDATE_RENDER_PENDING' if len(chosen)==2 else 'ONLY_ONE_DISTINCT_SAFE_COMPOSITION',
                           'clear_compositions':len(candidates),'selected':chosen,'max_visible_witnesses_per_target':possible,'rejections':dict(rejected)})
    print('COMPOSITION '+json.dumps({'room':rid,'candidates':len(candidates),'chosen':[{k:c[k] for k in ('location','target','shift_y','visible_witnesses')} for c in chosen]}),flush=True)
    cr.write_json(ROOT/f'qa/{prefix}-candidates.json',settings)
    cr.write_json(ROOT/f'qa/{prefix}-geometry.json',report)
merged=dict(frozen);merged.update(settings)
if selected and scene_path.name=='Fallingwater_iteration04.blend':
    c=merged['CAM_MAIN_B_BATH_B'];eye=Vector(c['location']);forward=(Vector(c['target'])-eye).normalized();right=forward.cross(Vector((0,0,1))).normalized();up=right.cross(forward).normalized()
    probes=[]
    for x,y in ((574,480),(601,520),(812,470),(895,526),(710,430),(380,480)):
        u=(x/960-.5)*36/c['lens'];v=((1-y/540)-.5)*20.25/c['lens']+c.get('shift_y',0)*36/c['lens']
        hit=geo.ray(eye,forward+right*u+up*v,40)
        probes.append({'pixel':[x,y],'hit':hit,'floor_z':c['support_z']})
    cr.write_json(ROOT/'qa/camera04-bath-threshold-rays.json',{'scene':bpy.data.filepath,'source_image':'renders/previews/camera04-review/CAM_MAIN_B_BATH_B.png','camera_settings':c,'scope':'Pixel rays from actually observed dark threshold strips; surface hit is evidence, not an automatic hole classification.','probes':probes})
if 'MAIN_B_BATH' in requested and 'CAM_MAIN_B_BATH_A' in settings:
    # Both actual04 and same-pose05 previews clip the WC base at the automatic
    # -.44966 shift. Preserve this manual correction across scene rebuilds.
    settings['CAM_MAIN_B_BATH_A']['shift_y']=-.55
    settings['CAM_MAIN_B_BATH_A']['evidence']+=' Actual04/05 preview clipped WC base; retained manual shift_y -.55. This lower frame still requires a new image.'
    merged.update(settings)
    cr.write_json(ROOT/f'qa/{prefix}-candidates.json',settings)
cr.write_json(ROOT/f'qa/{prefix}-merged.json',merged)
report['rays_cast']=geo.calls
cr.write_json(ROOT/f'qa/{prefix}-geometry.json',report)
