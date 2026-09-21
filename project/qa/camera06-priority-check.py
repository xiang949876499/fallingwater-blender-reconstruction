"""Fast exact local support checks for root's pending focus renders."""
import sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import bpy
import camera_review as cr
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene/Fallingwater_iteration06.blend'))
cfg=json.loads((ROOT/'qa/camera05-settings-frozen-v2.json').read_text(encoding='utf-8'))
names=[n for n in cfg if n in ('CAM_MAIN_L1_LIVING_B','CAM_GUEST_L1_LOUNGE_A','CAM_GUEST_L1_LOUNGE_B','CAM_MAIN_B_BATH_A','CAM_MAIN_B_PLUNGE_B','CAM_MAIN_L1_LOGGIA_B')]
report={'scene':bpy.data.filepath,'scope':'Priority points only; per-camera geometry box contains every complete support/body/eye ray, and only disjoint object bounds are culled. No framing or image acceptance.','cameras':[]}
for name in names:
    c=cfg[name];eye=c['location'];ground=c['support_z']
    bounds=(eye[0]-.5,eye[1]-.5,ground-.5,eye[0]+.5,eye[1]+.5,max(ground+1.9,eye[2]+.5))
    geo=cr.Geometry(bpy.context.scene,bounds=bounds)
    issue=geo.clearance(eye,ground);hit=geo.ray((eye[0],eye[1],ground+.16),(0,0,-1),.3)
    if not hit or abs(hit['location'][2]-ground)>.04:issue={'reason':'STORED_GROUND_CHANGED','hit':hit}
    result={'camera':name,'status':'FAIL' if issue else 'POINT_GEOMETRY_ONLY_PASS','issue':issue,'actual_center_support':hit,'bounds':bounds,'geometry':geo.counts}
    report['cameras'].append(result);cr.write_json(ROOT/'qa/camera06-priority-check.json',report)
    print('PRIORITY_CAMERA '+json.dumps(result),flush=True)
report['scene_sha256']=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
cr.write_json(ROOT/'qa/camera06-priority-check.json',report)
