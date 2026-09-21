"""Bounded, measured non-flat camera adjustments after iteration04 support changes."""
import sys,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import bpy
import camera_review as cr
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene/Fallingwater_iteration04.blend'))
scene=bpy.context.scene
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
rm={r['id']:r for r in rooms}
geo=cr.Geometry(scene)
settings=json.loads(cr.SETTINGS.read_text(encoding='utf-8-sig'))
report={'scene':bpy.data.filepath,'scope':'Only three failed non-flat/support-change cameras. Preserve XY and framing where the support alone changed; pool camera moves to measured dry floor. No geometry edits.', 'adjustments':[]}
for name in ('CAM_MAIN_B_FOUNDATION_3_B','CAM_MAIN_L2_TERRACE_W_A'):
    c=settings[name];old=json.loads(json.dumps(c))
    hit=geo.ray((c['location'][0],c['location'][1],c['support_z']+.3),(0,0,-1),.8)
    if not hit:raise RuntimeError(name+' no new support')
    dz=hit['location'][2]-c['support_z']
    c['location'][2]+=dz;c['target'][2]+=dz
    c['support_z']=hit['location'][2];c['support_object']=hit['object']
    problem=geo.clearance(c['location'],c['support_z'])
    if problem:raise RuntimeError(name+' new support unsafe '+str(problem))
    c['evidence']='Iteration04 actual mesh support remeasured. XY and relative framing preserved; vertical shift only. Full independent geometry verification and actual render review remain required.'
    report['adjustments'].append({'camera':name,'old':old,'new':c,'delta_z_m':dz,'support':hit})
name='CAM_GUEST_L1_POOL_A';c=settings[name];old=json.loads(json.dumps(c));room=rm[c['room_id']]
choices=[]
for dx in (-.35,-.5,-.7,-.9,-1.15):
    for dy in (0,.25,-.25,.5,-.5):
        xy=(old['location'][0]+dx,old['location'][1]+dy)
        for offset in (3,.7,.32):
            hit,problem=geo.support(xy,room,offset)
            if problem:continue
            if 'coping' in hit['object'].lower():continue
            eye=[*xy,hit['location'][2]+1.6]
            if geo.clearance(eye,hit['location'][2]):continue
            score,view=geo.view(eye,old['target'],room)
            choices.append((score-math.dist(eye[:2],old['location'][:2])*.7,eye,hit,view))
if not choices:raise RuntimeError('No dry safe replacement near guest pool A')
_,eye,hit,view=max(choices,key=lambda c:c[0])
c['location']=cr.plain(eye);c['support_z']=hit['location'][2];c['support_object']=hit['object']
c['outside_room_polygon']=not cr.inside(eye,room['polygon'])
c['evidence']='Iteration04: former coping position had water under the +13cm footprint. Moved to measured dry floor near the same pool-side view; actual support/body/eye clearance checked. Visual review pending.'
report['adjustments'].append({'camera':name,'old':old,'new':c,'support':hit,'view':view,'dry_candidates':len(choices)})
cr.write_json(cr.SETTINGS,settings)
cr.write_json(ROOT/'qa/camera04-support-adjustments.json',report)
result=cr.verify(scene,rooms)
cr.write_json(ROOT/'qa/camera04-verification.json',result)
cr.write_json(ROOT/'qa/camera04-settings-frozen.json',settings)
print('CAMERA04_FINAL '+json.dumps({'status':result['status'],'failures':[x['camera'] for x in result['cameras'] if x['issue']]}),flush=True)
