"""Actual06 support repairs and image-driven guest-lounge composition repair."""
import sys,json,math,collections,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import bpy
from mathutils import Vector
import camera_review as cr
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene/Fallingwater_iteration06.blend'))
scene=bpy.context.scene;geo=cr.Geometry(scene)
cfg=json.loads((ROOT/'qa/camera05-settings-frozen-v2.json').read_text(encoding='utf-8'))
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string());rm={r['id']:r for r in rooms}
report={'scene':bpy.data.filepath,'geometry':geo.counts,'scope':'Only camera selection, no geometry mutation; all four revisions require actual images.','embedded_camera_checks':[],'repairs':[]}
for name,c in cfg.items():
    cam=scene.objects[name];actual=cam.rotation_euler.to_matrix()@Vector((0,0,-1));wanted=(Vector(c['target'])-Vector(c['location'])).normalized()
    match=(cam.location-Vector(c['location'])).length<.0001 and actual.dot(wanted)>.999999 and abs(cam.data.lens-c['lens'])<.0001 and abs(cam.data.shift_y-c.get('shift_y',0))<.00001
    report['embedded_camera_checks'].append({'camera':name,'matches_v2_pose':match,'position_error':(cam.location-Vector(c['location'])).length,'forward_dot':actual.dot(wanted),'actual_shift_y':cam.data.shift_y})
def bbox(o):return [o.matrix_world@Vector(q) for q in o.bound_box]
def frame(eye,target,lens,shift):
    f=(Vector(target)-Vector(eye)).normalized();r=f.cross(Vector((0,0,1))).normalized();u=r.cross(f).normalized()
    def uv(q):
        d=Vector(q)-Vector(eye);depth=d.dot(f)
        if depth<=.01:return None
        return (.5+d.dot(r)*lens/(36*depth),.5+d.dot(u)*lens/(20.25*depth)-shift*36/20.25)
    return f,r,u,uv
def grid(eye,target,lens,shift):
    f,r,u,_=frame(eye,target,lens,shift);hits=[]
    for ix in range(11):
        for iy in range(7):
            direction=f+r*((((ix+.5)/11)-.5)*36/lens)+u*(((((iy+.5)/7)-.5)*20.25+shift*36)/lens)
            h=geo.ray(eye,direction,40)
            if h:hits.append(h)
    return {'near_under08':sum(h['distance']<.8 for h in hits),'screen_rays':sum('walnut_vertical_screen' in h['object'] for h in hits),'hits':hits}
def store(name,c,description):
    old=cfg[name]
    cfg[name]=dict(old,location=cr.plain(c['eye']),target=cr.plain(c['target']),lens=c.get('lens',old['lens']),shift_x=0,shift_y=c.get('shift',0),
                  support_object=c['support']['object'],support_z=c['support']['location'][2],outside_room_polygon=not cr.inside(c['eye'],rm[old['room_id']]['polygon']),
                  render_reviewed=False,evidence=description+' Actual06 geometric checks only; new render review pending.')
    report['repairs'].append({'camera':name,'before':old,'selected':{k:(cr.plain(v) if isinstance(v,Vector) else v) for k,v in c.items()},'description':description})

# Keep each previous target; move only the lost foot/support viewpoints.
for name in ('CAM_MAIN_L1_LOGGIA_A','CAM_MAIN_B_PLUNGE_A'):
    old=cfg[name];candidates=[];rejected=collections.Counter()
    if name.endswith('LOGGIA_A'):
        points=[(old['location'][0]+dx,old['location'][1]+dy) for dx in (0,-.08,-.15,-.23,-.32) for dy in (0,.08,.15,.23,.32)]
    else:
        points=[(x,y) for x in (18.7,18.95,19.2,19.4,19.58) for y in (10.04,10.18,10.3)]
    points+=cr.points(rm['MAIN_L1_LOGGIA'],geo)
    for xy in points:
        support,support_issue=geo.support(xy,rm['MAIN_L1_LOGGIA'],.32)
        if support_issue:rejected[support_issue]+=1;continue
        if support['object']!='MAIN_L1_LOGGIA_finish':rejected['OTHER_SUPPORT:'+support['object']]+=1;continue
        eye=Vector((*xy,support['location'][2]+1.6))
        body_issue=geo.clearance(eye,support['location'][2])
        if body_issue:rejected[body_issue['reason']+':'+body_issue['hit']['object']]+=1;continue
        target=Vector(old['target']);score,view=geo.view(eye,target,rm[old['room_id']])
        candidates.append({'eye':eye,'target':target,'support':support,'view':view,'score':score-math.dist(eye,old['location'])*1.2})
    report.setdefault('support_searches',[]).append({'camera':name,'clear_candidates':len(candidates),'rejections':dict(rejected)})
    cr.write_json(ROOT/'qa/camera06-repair-progress.json',report)
    if not candidates:raise RuntimeError('No local support repair: '+name)
    chosen=max(candidates,key=lambda c:c['score'])
    store(name,chosen,'06 support repair: '+('shift inward on actual loggia finish after terrain removal exposes an unsupported old foot.' if name.endswith('LOGGIA_A') else 'move from the removed bridge approach to the actual upper loggia floor, preserving the pool target. This is an adjacent upper dry observation point, not pool-room floor occupancy.'))

# Aperture rectangles come from the real hood and hearth, not centers of the
# entire fireplace mass. An unobstructed firebox mouth is required for A.
hood=bbox(scene.objects['GUEST_FIREPLACE_corner_hood']);hearth=bbox(scene.objects['GUEST_FIREPLACE_hearth'])
lo=[min(q[i] for q in hood) for i in range(3)];hi=[max(q[i] for q in hood) for i in range(3)]
z0=max(q.z for q in hearth)+.018;z1=lo[2]-.018
apertures={'south':[(lo[0]+.018,lo[1]-.005,z0),(hi[0]-.018,lo[1]-.005,z0),(hi[0]-.018,lo[1]-.005,z1),(lo[0]+.018,lo[1]-.005,z1)],
           'east':[(hi[0]+.005,lo[1]+.018,z0),(hi[0]+.005,hi[1]-.018,z0),(hi[0]+.005,hi[1]-.018,z1),(hi[0]+.005,lo[1]+.018,z1)]}
room=rm['GUEST_L1_LOUNGE'];options=[];wide_options=[];reject=collections.Counter();aperture_diagnostics=[]
lounge_points=cr.points(room,geo)
lounge_points += [(4.3+i*.07,36.22+j*.07) for i in range(14) for j in range(48) if cr.inside((4.3+i*.07,36.22+j*.07),room['polygon'])]
lounge_points += [(4.10+i*.01,36.25+j*.04) for i in range(13) for j in range(20)]
for xy in lounge_points:
    support,problem=geo.support(xy,room,.32)
    if problem:continue
    eye=Vector((*xy,support['location'][2]+1.6))
    if geo.clearance(eye,support['location'][2]):continue
    for side,corners in apertures.items():
        if side=='south' and eye.y>=lo[1]-.25 or side=='east' and eye.x<=hi[0]+.25:continue
        midpoint=sum((Vector(q) for q in corners),Vector())/4
        distance=math.dist(eye[:2],midpoint[:2])
        if distance<1.5:continue
        # Center the whole fireplace vertically, so the aperture does not fit
        # merely by clipping away the hood or hearth.
        visual_z=(min(q.z for q in hearth)+hi[2])*.5
        target=Vector((midpoint.x,midpoint.y,eye.z));lens=28
        shift=max(-.40,min(.05,(visual_z-eye.z)*lens/(36*distance)))
        f,r,u,uv=frame(eye,target,lens,shift)
        projected=[uv(q) for q in corners]
        if any(q is None or not(.07<q[0]<.93 and .07<q[1]<.93) for q in projected):continue
        area=abs(sum(projected[i][0]*projected[(i+1)%4][1]-projected[(i+1)%4][0]*projected[i][1] for i in range(4)))*.5
        if area<.028:continue
        full=[uv(q) for q in hood+hearth]
        if any(q is None or not(.04<q[0]<.96 and .04<q[1]<.96) for q in full):continue
        clear=0;blocked=collections.Counter();panel=[]
        for ix in range(7):
            for iz in range(7):
                q=Vector(corners[0])+(Vector(corners[1])-Vector(corners[0]))*((ix+.5)/7)+(Vector(corners[3])-Vector(corners[0]))*((iz+.5)/7)
                delta=q-eye;hit=geo.ray(eye,delta,delta.length-.014)
                if hit:blocked[hit['object']]+=1
                else:clear+=1
                panel.append({'point':cr.plain(q),'clear_to_opening':hit is None,'hit':hit})
        aperture_diagnostics.append({'eye':cr.plain(eye),'target':cr.plain(target),'shift':shift,'side':side,'area':area,'clear':clear,'blocked':dict(blocked)})
        if clear<45:reject['APERTURE_OCCLUDED']+=1
        g=grid(eye,target,lens,shift)
        if g['near_under08']>7 or g['screen_rays']>12:reject['NEAR_FOREGROUND']+=1;continue
        score=area*120+clear*.15-g['near_under08']*.4-g['screen_rays']*.08+min(distance,3.8)*.25
        candidate={'eye':eye,'target':target,'support':support,'lens':lens,'shift':shift,'side':side,'aperture_fraction_of_frame':area,
                        'aperture_clear_samples':clear,'aperture_total_samples':49,'aperture_corners_uv':projected,'aperture_panel':panel,
                        'full_fireplace_bounds_uv':full,'frame_grid':g,'score':score}
        if clear>=45:options.append(candidate)
        if clear>=35:wide_options.append(candidate)
report['lounge_first_search']={'clear_candidates':len(options),'rejections':dict(reject),'best_rejected':sorted(aperture_diagnostics,key=lambda c:-c['clear'])[:30]}
cr.write_json(ROOT/'qa/camera06-repair-progress.json',report)
if not options and not wide_options:raise RuntimeError('No useful full-hood room candidate, including explicitly limited ones')
best=max(options or wide_options,key=lambda c:c['score'])
store('CAM_GUEST_L1_LOUNGE_A',best,('Actual06 full-hood/hearth room candidate, with >=45/49 clear mouth samples.' if options else 'LIMITED wide room/fireplace candidate: complete hood/hearth projection fits, but the existing screen occludes part of the aperture. This does NOT pass the full-firebox requirement; a separate detail view is mandatory.')+' Aperture projection and actual obstruction rays are recorded; image review pending.')

# A complementary room view must sit on the room side of the screen and have
# no near-screen barrier. Score table, bookcase and chair as whole assemblies.
furniture=collections.defaultdict(list)
for name,obj in geo.objects.items():
    if obj.get('room_id')==room['id'] and obj.get('component_type')=='furniture' and any(k in obj.get('asset_type','') for k in ('table','bookcase','armchair','bench')):
        furniture[obj.get('asset_id',name)].append((obj,sum(bbox(obj),Vector())/8))
targets=[sum((q for _,q in parts),Vector())/len(parts) for parts in furniture.values()]
targets.append(Vector((*room['center'][:2],room['z']+1)))
secondary=[]
for xy in cr.points(room,geo):
    if xy[0]<5.45:continue
    support,problem=geo.support(xy,room,.32)
    if problem:continue
    eye=Vector((*xy,support['location'][2]+1.6))
    if geo.clearance(eye,support['location'][2]) or (eye-best['eye']).length<1:continue
    for aim in targets:
        distance=math.dist(eye[:2],aim[:2])
        if distance<1.5:continue
        target=Vector((aim.x,aim.y,eye.z));shift=max(-.28,min(0,(aim.z-eye.z)*28/(36*distance)))
        f,r,u,uv=frame(eye,target,28,shift);visible=collections.Counter();covered={}
        for asset,parts in furniture.items():
            pts=[]
            for obj,q in parts:
                loc=uv(q)
                if not loc or not(.08<loc[0]<.92 and .08<loc[1]<.92):continue
                delta=q-eye;hit=geo.ray(eye,delta,delta.length+.12)
                if hit and geo.objects[hit['object']].get('asset_id')==asset:visible[asset]+=1;pts.append(loc)
            if pts:covered[asset]=[min(q[0] for q in pts),min(q[1] for q in pts),max(q[0] for q in pts),max(q[1] for q in pts)]
        if len(visible)<2:continue
        g=grid(eye,target,28,shift)
        if g['near_under08']>5 or g['screen_rays']>9:continue
        score=len(visible)*3+sum(min(v,6) for v in visible.values())*.3-g['near_under08']*.6-g['screen_rays']*.12
        secondary.append({'eye':eye,'target':target,'support':support,'lens':28,'shift':shift,'visible_furniture_parts':dict(visible),'visible_part_bounds_uv':covered,'frame_grid':g,'score':score})
if not secondary:raise RuntimeError('No unobstructed complementary room view')
chosen=max(secondary,key=lambda c:c['score'])
store('CAM_GUEST_L1_LOUNGE_B',chosen,'Actual06 image-driven complementary room view from the east side of the existing screen; near foreground limited to <=5/77 rays, screen <=9/77. Furnishing visibility counts supplement but never replace the required new image.')

# A third diagnostic can prove the unobstructed chamber without pretending
# that a close crop replaces the two required room views. Keep it separate.
details=[]
for x in (5.32,5.4,5.48,5.56,5.7,5.85,6.0):
    for y in (39.96,40.0,40.04,40.08,40.10):
        support,problem=geo.support((x,y),room,.32)
        if problem:continue
        eye=Vector((x,y,support['location'][2]+1.6))
        if geo.clearance(eye,support['location'][2]):continue
        corners=apertures['east'];midpoint=sum((Vector(q) for q in corners),Vector())/4
        target=midpoint;lens=28;shift=0
        f,r,u,uv=frame(eye,target,lens,shift);projected=[uv(q) for q in corners]
        if any(q is None or not(.05<q[0]<.95 and .05<q[1]<.95) for q in projected):continue
        area=abs(sum(projected[i][0]*projected[(i+1)%4][1]-projected[(i+1)%4][0]*projected[i][1] for i in range(4)))*.5
        clear=0;interior=collections.Counter();panel=[]
        for ix in range(7):
            for iz in range(7):
                q=Vector(corners[0])+(Vector(corners[1])-Vector(corners[0]))*((ix+.5)/7)+(Vector(corners[3])-Vector(corners[0]))*((iz+.5)/7)
                delta=q-eye;hit=geo.ray(eye,delta,delta.length-.014)
                beyond=geo.ray(eye,delta,delta.length+1.5)
                if not hit:clear+=1
                if not hit and beyond:interior[beyond['object']]+=1
                panel.append({'point':cr.plain(q),'clear_to_opening':hit is None,'obstruction':hit,'interior_first_hit':beyond})
        if clear<45 or area<.06:continue
        visible_chamber=sum(v for k,v in interior.items() if k.startswith(('GUEST_FIREPLACE_firebrick','GUEST_FIREPLACE_hearth','GUEST_FIREPLACE_west_back','GUEST_FIREPLACE_north_mass')))
        if visible_chamber<35:continue
        details.append({'eye':eye,'target':target,'support':support,'lens':lens,'shift':shift,'area':area,'clear_samples':clear,
                        'interior_surface_samples':visible_chamber,'interior_hit_objects':dict(interior),'aperture_panel':panel,'score':clear+visible_chamber+area*10})
report['detail_candidates_found']=len(details)
if not details:raise RuntimeError('No unobstructed firebox detail found; wide partial image is not accepted in its place')
detail=max(details,key=lambda c:c['score']);base=dict(cfg['CAM_GUEST_L1_LOUNGE_A'])
base.update(location=cr.plain(detail['eye']),target=cr.plain(detail['target']),lens=28,shift_x=0,shift_y=0,support_z=detail['support']['location'][2],support_object=detail['support']['object'],
            outside_room_polygon=not cr.inside(detail['eye'],room['polygon']),evidence='Separate third QA detail: actual unobstructed firebox aperture and chamber surface rays; it does not replace the two room views. Actual image pending.',view_role='EXTRA_FIREBOX_DETAIL')
cr.write_json(ROOT/'qa/camera06-firebox-detail-settings.json',{'CAM_GUEST_L1_LOUNGE_A':base})
report['firebox_detail']={k:(cr.plain(v) if isinstance(v,Vector) else v) for k,v in detail.items()}
report['lounge_aperture_geometry']={'bounds':{'hood_min':lo,'hood_max':hi,'hearth_top':z0-.018},'apertures':apertures,'clear_candidates':len(options),'rejections':dict(reject)}
report['rays_cast']=geo.calls
cr.write_json(ROOT/'qa/camera06-repair-geometry.json',report)
cr.write_json(ROOT/'qa/camera06-repair-merged.json',cfg)
cr.write_json(ROOT/'qa/camera06-repair-candidates.json',{r['camera']:cfg[r['camera']] for r in report['repairs']})
print('REPAIR06_COMPLETE '+json.dumps({'camera_count':len(cfg),'embedded_mismatches':[r['camera'] for r in report['embedded_camera_checks'] if not r['matches_v2_pose']],
                                     'repairs':[{'camera':r['camera'],'location':r['selected']['eye'],'aperture_area':r['selected'].get('aperture_fraction_of_frame'),'clear':r['selected'].get('aperture_clear_samples')} for r in report['repairs']]}),flush=True)
