"""Repair only three changed-geometry viewpoints; never mutate scene geometry."""
import sys, json, math, collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import bpy
from mathutils import Vector
import camera_review as cr

bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene/Fallingwater_iteration05.blend'))
scene=bpy.context.scene
geo=cr.Geometry(scene)
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
rm={r['id']:r for r in rooms}
config=json.loads((ROOT/'qa/camera05-composition-supplement-merged.json').read_text(encoding='utf-8'))
original=json.loads((ROOT/'qa/camera04-settings-frozen.json').read_text(encoding='utf-8'))
report={'scene':bpy.data.filepath,'geometry':geo.counts,'scope':'Only MAIN_L3_LINK A/B and GUEST_L1_POOL A changed. Actual render review pending; vegetation excluded. Point clearance is not continuous route validation.','changes':[]}

# The new link polygon represents only the real upper north landing. Both eyes
# must lie on this polygon and at its floor level, never the former canopy roof.
rid='MAIN_L3_LINK';room=rm[rid]
stairs=[]
for obj in geo.objects.values():
    if not obj.name.startswith('MAIN_north_spiral_'):continue
    bb=[obj.matrix_world@Vector(v) for v in obj.bound_box]
    p=sum(bb,Vector())/8;p.z=max(q.z for q in bb)+.025
    if p.z>room['z']-1.05:stairs.append((p,obj.name))
if not stairs:raise RuntimeError('New north spiral witnesses missing')
stairs.sort(key=lambda w:w[0].z)
targets=[(sum((p for p,_ in stairs),Vector())/len(stairs),'spiral')]
# Reverse view follows the actual west end of the upper landing/connector.
targets.append((Vector((*room['entry'][:2],room['z']+.6)),'connector'))
choices=[];failures=collections.Counter()
for xy in cr.points(room,geo):
    if not cr.inside(xy,room['polygon']):continue
    hit,issue=geo.support(xy,room)
    if issue:failures[issue]+=1;continue
    eye=Vector((*xy,hit['location'][2]+1.6))
    issue=geo.clearance(eye,hit['location'][2])
    if issue:failures[issue['reason']]+=1;continue
    for target,kind in targets:
        if math.dist(eye[:2],target[:2])<.55:continue
        forward=(target-eye).normalized()
        right=forward.cross(Vector((0,0,1))).normalized();up=right.cross(forward).normalized()
        visible=[]
        for point,owner in stairs:
            delta=point-eye;depth=delta.dot(forward)
            if depth<=.05:continue
            ux=.5+delta.dot(right)*28/(36*depth);vy=.5+delta.dot(up)*28/(20.25*depth)
            if not(.07<ux<.93 and .07<vy<.93):continue
            cast=geo.ray(eye,delta,delta.length+.12)
            if cast and cast['object'].startswith('MAIN_north_spiral_'):visible.append(owner)
        score,view=geo.view(eye,target,room)
        if kind=='spiral':score+=len(visible)*1.4
        choices.append({'location':cr.plain(eye),'target':cr.plain(target),'support':hit,'view':view,'visible_spiral_treads':visible,'kind':kind,'score':score})
spiral=[c for c in choices if c['kind']=='spiral' and c['visible_spiral_treads']]
if not spiral:raise RuntimeError('No safe upper-landing view of actual spiral')
a=max(spiral,key=lambda c:c['score'])
reverse=[c for c in choices if c['kind']=='connector' and math.dist(c['location'],a['location'])>=.45]
if not reverse:raise RuntimeError('No distinct safe upper-landing reverse view')
b=max(reverse,key=lambda c:c['score']+min(2,math.dist(c['location'],a['location']))*.6)
for suffix,c in zip(('A','B'),(a,b)):
    name='CAM_'+rid+'_'+suffix
    config[name]=dict(original[name],location=c['location'],target=c['target'],lens=28,shift_x=0,shift_y=0,
                      support_z=c['support']['location'][2],support_object=c['support']['object'],outside_room_polygon=False,render_reviewed=False,
                      evidence='Iteration05 actual north upper landing; eye is inside its new polygon and supported by the real floor, with unchanged 1.75m body/0.15m radius tests. '+('A targets the actual north spiral treads.' if suffix=='A' else 'B reverses toward the west connector entrance.')+' Actual image and route review pending.')
    report['changes'].append({'camera':name,'old':original[name],'selected':c,'rejections':dict(failures)})

# Keep the already readable reverse pool camera. Move only A on the same dry
# 8.4002m deck near its old point, away from the new sandstone course collision.
name='CAM_GUEST_L1_POOL_A';room=rm['GUEST_L1_POOL'];old=original[name]
pool_candidates=[];pool_rejections=collections.Counter()
for dx in (-1.3,-1,-.8,-.6,-.45,-.3,-.15,0,.15,.3,.45,.6,.8,1,1.3):
    for dy in (-1,-.8,-.6,-.45,-.3,-.15,0,.15,.3,.45,.6,.8,1):
        xy=(old['location'][0]+dx,old['location'][1]+dy)
        hit,issue=geo.support(xy,room,.32)
        if issue:pool_rejections[issue]+=1;continue
        if abs(hit['location'][2]-old['support_z'])>.04 or not any(k in hit['object'].lower() for k in ('floor','finish','landing')):
            pool_rejections['NOT_SAME_DRY_DECK']+=1;continue
        eye=[*xy,hit['location'][2]+1.6]
        issue=geo.clearance(eye,hit['location'][2])
        if issue:pool_rejections[issue['reason']]+=1;continue
        score,view=geo.view(eye,old['target'],room)
        pool_candidates.append({'location':cr.plain(eye),'target':old['target'],'support':hit,'view':view,
                                'score':score-math.dist(eye,old['location'])*1.2,'move_m':math.dist(eye,old['location'])})
if not pool_candidates:raise RuntimeError('No safe dry pool-deck A repair')
c=max(pool_candidates,key=lambda c:c['score'])
config[name]=dict(old,location=c['location'],support_z=c['support']['location'][2],support_object=c['support']['object'],
                  outside_room_polygon=not cr.inside(c['location'],room['polygon']),render_reviewed=False,
                  evidence='Iteration05 local pool-A correction after new sandstone course body collision. Actual dry floor at the prior deck elevation, unchanged body/foot/eye tests; original target and camera B preserved. Actual render and vegetation review pending.')
report['changes'].append({'camera':name,'old':old,'selected':c,'clear_candidates':len(pool_candidates),'rejections':dict(pool_rejections)})

# These exposure values were selected by root from actual iteration05 focus
# images. Exposure reuse after a changed pose remains explicitly provisional.
for name,ev in {'CAM_MAIN_B_BATH_A':1.6,'CAM_MAIN_B_BATH_B':1.6,'CAM_MAIN_L1_LIVING_B':2.4,'CAM_GUEST_L1_LOUNGE_A':2.8}.items():
    config[name]['exposure']=ev
    config[name]['exposure_evidence']='Root actually viewed iteration05 focus exposure bracket; chosen EV '+str(ev)+'. A changed pose must still be rendered and reviewed.'
report['rays_cast']=geo.calls
cr.write_json(ROOT/'qa/camera05-residual-geometry.json',report)
cr.write_json(ROOT/'qa/camera05-final-candidate.json',config)
print('RESIDUAL_COMPLETE '+json.dumps({'cameras':len(config),'changes':[{'camera':c['camera'],'location':c['selected']['location'],'support':c['selected']['support']['object']} for c in report['changes']]}),flush=True)
