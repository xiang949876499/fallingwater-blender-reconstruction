"""Four bounded, source-informed lounge wide views. No rendering/model changes."""
import sys,json,hashlib,math,collections,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import bpy
from mathutils import Vector
import camera_review as cr
scene_path=ROOT/'scene/Fallingwater_furniture_candidate07e.blend'
assert hashlib.sha256(scene_path.read_bytes()).hexdigest()=='d6084c1ebca7e1328f1a008b673d86e55c738da4b5ee8a52c5b7e5ce86b8eadd'
bpy.ops.wm.open_mainfile(filepath=str(scene_path));scene=bpy.context.scene;geo=cr.Geometry(scene)
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string());rm={r['id']:r for r in rooms};room=rm['GUEST_L1_LOUNGE']
base=json.loads((ROOT/'qa/camera06-settings-candidate-frozen.json').read_text(encoding='utf-8'))
bookcase=next(o for o in scene.objects if o.type=='EMPTY' and o.get('room_id')==room['id'] and o.get('asset_type')=='long_horizontal_bookcase')
report={'scene':str(scene_path),'scene_sha256':hashlib.sha256(scene_path.read_bytes()).hexdigest(),'geometry':geo.counts,
        'source':'Actually viewed HABS A11 photo and guest01 grid. Match their relational view from entrance toward west: south glazing/seating left, northern bookshelf right, NW fireplace beyond. These are C camera viewpoints, not calibrated photo matches.',
        'scope':'Exactly4 nominal viewing regions, maximum13 local offsets within0.16m each. No global search, no geometry edits, no production JSON mutation, no rendering. All geometry rays exclude vegetation.',
        'variants':[],'base_support_checks':[]}
nominals=[('entrance_front',(9.0,38.70),(4.9,38.65),-.07),('north_front',(8.70,39.10),(4.9,38.60),-.08),('seating_side',(8.85,37.45),(4.9,38.15),-.08),('gallery_entrance',(10.15,39.20),(5.0,38.45),-.07)]
offsets=[(0,0),(0,.08),(0,-.08),(-.08,0),(.08,0),(-.08,.08),(.08,.08),(-.08,-.08),(.08,-.08),(0,.16),(0,-.16),(-.16,0),(.16,0)]
def bb(o):return [o.matrix_world@Vector(v) for v in o.bound_box]
hood=bb(scene.objects['GUEST_FIREPLACE_corner_hood']);hearth=bb(scene.objects['GUEST_FIREPLACE_hearth'])
lo=[min(q[i] for q in hood) for i in range(3)];hi=[max(q[i] for q in hood) for i in range(3)]
bottom=max(q.z for q in hearth)+.018;top=lo[2]-.018
apertures={'east':[(hi[0]+.005,lo[1]+.018,bottom),(hi[0]+.005,hi[1]-.018,bottom),(hi[0]+.005,hi[1]-.018,top),(hi[0]+.005,lo[1]+.018,top)],
           'south':[(lo[0]+.018,lo[1]-.005,bottom),(hi[0]-.018,lo[1]-.005,bottom),(hi[0]-.018,lo[1]-.005,top),(lo[0]+.018,lo[1]-.005,top)]}
subjects=collections.defaultdict(list)
for name,obj in geo.objects.items():
    if obj.get('room_id')==room['id'] and obj.get('component_type')=='furniture':
        kind=obj.get('asset_type','')
        if any(k in kind for k in ('bench','bookcase','armchair','table')):subjects[obj.get('asset_id',name)].append((name,sum(bb(obj),Vector())/8))
    if name.startswith('GUEST_L1_LOUNGE_FRONT') and 'glass' in name.lower():subjects['SOUTH_GLAZING'].append((name,sum(bb(obj),Vector())/8))
for index,(label,xy,aim,shift) in enumerate(nominals,1):
    failures=[];chosen=None
    for dx,dy in offsets:
        point=(xy[0]+dx,xy[1]+dy);hit,problem=geo.support(point,room,.32)
        if problem:failures.append({'xy':point,'issue':problem});continue
        eye=Vector((*point,hit['location'][2]+1.6));problem=geo.clearance(eye,hit['location'][2])
        if problem:failures.append({'xy':point,'issue':problem});continue
        local_eye=bookcase.matrix_world.inverted()@eye
        if local_eye.y>=-.32/2-.20:failures.append({'xy':point,'issue':'NOT_CLEARLY_ON_BOOKSHELF_FRONT_SIDE'});continue
        chosen=(eye,hit,cr.plain(local_eye));break
    if not chosen:
        report['variants'].append({'variant':label,'status':'NO_SAFE_LOCAL_POINT','failures':failures});continue
    eye,support,bookcase_local=chosen;target=Vector((*aim,eye.z));lens=28
    f=(target-eye).normalized();right=f.cross(Vector((0,0,1))).normalized();up=right.cross(f).normalized()
    def project(q):
        d=Vector(q)-eye;depth=d.dot(f)
        if depth<=.01:return None
        return [.5+d.dot(right)*lens/(36*depth),.5+d.dot(up)*lens/(20.25*depth)-shift*36/20.25]
    ap=[]
    for side,corners in apertures.items():
        uvs=[project(q) for q in corners]
        all_in=all(q is not None and .02<q[0]<.98 and .02<q[1]<.98 for q in uvs)
        area=abs(sum(uvs[i][0]*uvs[(i+1)%4][1]-uvs[(i+1)%4][0]*uvs[i][1] for i in range(4)))*.5 if all(q for q in uvs) else 0
        clear=0;blocked=collections.Counter();framed=0
        for i in range(7):
            for j in range(7):
                q=Vector(corners[0])+(Vector(corners[1])-Vector(corners[0]))*((i+.5)/7)+(Vector(corners[3])-Vector(corners[0]))*((j+.5)/7)
                uv=project(q)
                if uv is None or not(.02<uv[0]<.98 and .02<uv[1]<.98):continue
                framed+=1;delta=q-eye;h=geo.ray(eye,delta,delta.length-.014)
                if h:blocked[h['object']]+=1
                else:clear+=1
        ap.append({'side':side,'whole_aperture_in_frame':all_in,'area_fraction':area,'framed_samples':framed,'clear_samples':clear,'total_samples':49,'occluders':dict(blocked),'corners_uv':uvs})
    visibility=[]
    for asset,parts in subjects.items():
        seen=[];in_frame=0
        for name,q in parts:
            uv=project(q)
            if uv is None or not(.03<uv[0]<.97 and .03<uv[1]<.97):continue
            in_frame+=1;delta=q-eye;h=geo.ray(eye,delta,delta.length+.1)
            if h and (h['object']==name or geo.objects[h['object']].get('asset_id')==asset):seen.append(uv)
        visibility.append({'subject':asset,'framed_points':in_frame,'visible_points':len(seen),'visible_uv_bounds':([min(q[0] for q in seen),min(q[1] for q in seen),max(q[0] for q in seen),max(q[1] for q in seen)] if seen else None)})
    # Jitter a denser image-plane sample to avoid repeated slat/gap aliasing.
    rng=random.Random(710+index);hits=collections.Counter();near=0;grid=[]
    for i in range(29):
        for j in range(17):
            ux=(i+.15+.70*rng.random())/29;vy=(j+.15+.70*rng.random())/17
            ray=f+right*((ux-.5)*36/lens)+up*(((vy-.5)*20.25+shift*36)/lens)
            h=geo.ray(eye,ray,40)
            if h:hits[h['object']]+=1;near+=int(h['distance']<.8)
            grid.append({'uv':[round(ux,5),round(vy,5)],'hit':h})
    values=dict(base['CAM_GUEST_L1_LOUNGE_A'],location=cr.plain(eye),target=cr.plain(target),lens=lens,shift_x=0,shift_y=shift,exposure=3.6,
                support_object=support['object'],support_z=support['location'][2],outside_room_polygon=not cr.inside(eye,room['polygon']),render_reviewed=False,
                evidence='07e bounded '+label+' broad room candidate based on A11 relational composition; actual support and body rays tested, bookshelf front side required. DiagEV3.6; actual render pending.')
    rel=f'qa/camera07e-wide-{index}-{label}.json';cr.write_json(ROOT/rel,{'CAM_GUEST_L1_LOUNGE_A':values})
    merged=dict(base);merged['CAM_GUEST_L1_LOUNGE_A']=values
    # Persist both separately so the root can render one identical camera name
    # into distinct output directories. Base retains the Loggia/Plunge repairs.
    cr.write_json(ROOT/f'qa/camera07e-wide-{index}-merged.json',merged)
    rec={'variant':label,'status':'GEOMETRY_SAFE_CANDIDATE_RENDER_PENDING','settings':rel,'settings_sha256':hashlib.sha256((ROOT/rel).read_bytes()).hexdigest(),
         'values':values,'bookcase_local_eye':bookcase_local,'nominal_xy':xy,'local_rejections':failures,'apertures':ap,'subjects':visibility,
         'jittered_grid_samples':493,'near_under08_samples':near,'near_under08_fraction':near/493,'screen_samples':sum(v for k,v in hits.items() if 'walnut_vertical_screen' in k),
         'bookshelf_back_samples':sum(v for k,v in hits.items() if 'long_horizontal_bookcase' in k and 'back_board' in k),
         'dominant_first_hits':hits.most_common(10),'jittered_grid':grid}
    report['variants'].append(rec)
    print('WIDE07E '+json.dumps({'variant':label,'location':values['location'],'apertures':[{k:q[k] for k in ('side','area_fraction','clear_samples','framed_samples')} for q in ap],'near_fraction':near/493,'screen_samples':rec['screen_samples'],'back_samples':rec['bookshelf_back_samples']}),flush=True)
for name in ('CAM_MAIN_L1_LOGGIA_A','CAM_MAIN_B_PLUNGE_A','CAM_GUEST_L1_LOUNGE_B'):
    c=base[name];problem=geo.clearance(c['location'],c['support_z']);h=geo.ray((c['location'][0],c['location'][1],c['support_z']+.16),(0,0,-1),.3)
    if not h or abs(h['location'][2]-c['support_z'])>.04:problem={'reason':'STORED_GROUND_CHANGED','hit':h}
    report['base_support_checks'].append({'camera':name,'status':'FAIL' if problem else 'GEOMETRY_ONLY_PASS','issue':problem,'actual_support':h})
report['rays_cast']=geo.calls;cr.write_json(ROOT/'qa/camera07e-wide-candidates-report.json',report)
assert sum(r['status']=='GEOMETRY_SAFE_CANDIDATE_RENDER_PENDING' for r in report['variants'])>=2,'Fewer than2 bounded safe candidates; do not expand unboundedly'
