"""Confirm selected diagnostic view witnesses with Blender scene.ray_cast."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
source=json.loads((ROOT/'qa/guest-stair-wall08b-camera-probe2.json').read_text(encoding='utf-8'))
selected=[('CAM_GUEST_B1_STAIR_A','south_high',1.6),('CAM_GUEST_B1_STAIR_B','north_door_stairs',3.0)]
settings={};records=[]
for camera_name,choice_id,exposure in selected:
    choice=next(r for r in source['records'] if r['id']==choice_id)
    settings[camera_name]={k:choice[k] for k in ('location','target','lens')}
    settings[camera_name].update(shift_x=0,shift_y=0,exposure=exposure,exposure_verified=False,
        purpose='ADDITIONAL_STAIR_WALL_DIAGNOSTIC_NOT_ROOM120_REPLACEMENT',render_reviewed=False,
        source_scene_sha256=source['source_sha256'])
    origin=Vector(choice['location']);witnesses=[]
    for w in choice['witnesses']:
        if not w['framed'] or not w['unoccluded']:continue
        delta=Vector(w['point'])-origin
        found,point,normal,index,obj,matrix=scene.ray_cast(deps,origin,delta.normalized(),distance=delta.length+.003)
        unobstructed=not found or (point-origin).length>=delta.length-.012
        witnesses.append({'part':w['part'],'target':w['point'],'projected':w['projected'],
            'status':'PASS' if unobstructed else 'FAIL','first_hit':{'name':obj.name,'point':list(point),'distance':(point-origin).length} if found else None})
    records.append({'camera_name':camera_name,'selected':choice_id,'camera_clearance_failure':choice['camera_clearance_failure'],
        'witnesses':witnesses,'witness_count':len(witnesses),'failed_count':sum(w['status']=='FAIL' for w in witnesses)})
result={'status':'PASS' if all(not r['failed_count'] and not r['camera_clearance_failure'] for r in records) else 'FAIL',
        'scene':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
        'records':records,'scope':'Actual projected unobstructed named-surface witnesses. No render, no visual acceptance, no changes to room120 cameras saved.'}
(ROOT/'qa/guest-stair-wall08b-diagnostic-camera-settings.json').write_text(json.dumps(settings,indent=2),encoding='utf-8')
(ROOT/'qa/guest-stair-wall08b-camera-final.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('DIAGNOSTIC_CAMERA_FINAL',json.dumps(result),flush=True)
