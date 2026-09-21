"""Check all120 saved current poses, independently of historical pose files."""
from pathlib import Path
import bpy,sys,json,hashlib,statistics
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import camera_review as review
SRC=ROOT/'scene/Fallingwater_navigation_candidate11a.blend'
SHA='d66ded0f23b7d19c20b81d2f59f94aa5aa77747be4568e85e1d105395fc219ff'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SHA
bpy.ops.wm.open_mainfile(filepath=str(SRC));scene=bpy.context.scene
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
old=json.loads((ROOT/'data/camera-settings-reviewed.json').read_text(encoding='utf8'))
changed=json.loads((ROOT/'data/camera-settings-iteration10-overrides.json').read_text(encoding='utf8'))
geo=review.Geometry(scene)
rows=[]
for room in rooms:
    for name in room['qa_cameras']:
        ob=scene.objects[name];eye=list(ob.matrix_world.translation)
        ground=eye[2]-1.6 if name in changed else old[name]['support_z']
        hit=geo.ray((eye[0],eye[1],ground+.16),(0,0,-1),.30)
        issue=geo.clearance(eye,ground)
        if not hit or abs(hit['location'][2]-ground)>.04:issue={'reason':'GROUND_CHANGED','actual':hit}
        if hit and (hit['normal'][2]<.65 or geo.objects[hit['object']].get('component_type')=='furniture'):
            issue={'reason':'UNSAFE_CENTER_SUPPORT','actual':hit}
        frame=ob.data.view_frame(scene=scene)
        xmin=min(v.x/-v.z for v in frame);xmax=max(v.x/-v.z for v in frame)
        ymin=min(v.y/-v.z for v in frame);ymax=max(v.y/-v.z for v in frame)
        rays=[]
        for u in (.10,.30,.50,.70,.90):
            for v in (.15,.50,.85):
                direction=ob.matrix_world.to_quaternion()@Vector((xmin+(xmax-xmin)*u,ymin+(ymax-ymin)*v,-1)).normalized()
                result=geo.ray(eye,direction,30)
                rays.append({'image_uv':[u,v],'hit':result})
        rows.append({'camera':name,'room_id':room['id'],'status':'FAIL' if issue else 'PASS_SAMPLED_GEOMETRY_ONLY',
                     'issue':issue,'support':hit,'expected_ground_z':ground,'eye_height_m':eye[2]-ground,
                     'lens_mm':ob.data.lens,'shift':[ob.data.shift_x,ob.data.shift_y],
                     'lens_scope':'DIAGNOSTIC_WIDE_LENS_REVIEW_PENDING' if ob.data.lens<24 else 'PHOTOGRAPHY_VISUAL_REVIEW_PENDING',
                     'outside_room_polygon':not review.inside(eye,room['polygon']),
                     'rays_under045m':sum(r['hit'] is not None and r['hit']['distance']<.45 for r in rays),
                     'rays':rays})
report={'scene_sha256':SHA,'cameras':len(rows),'pass':sum(r['issue'] is None for r in rows),
        'fail':sum(r['issue'] is not None for r in rows),'actual_saved_poses_used':True,
        'changed_vs09':len(changed),'geometry':geo.counts,'rays':geo.calls,'rows':rows,
        'limits':['Legacy1.75m/radius.15m sampled camera body envelope; changed zones have additional strict proofs',
                  'Vegetation excluded here; canopy wrapper separately tested all131 cameras',
                  '15 framing rays use actual lens/shift; numerical framing is not visual acceptance',
                  'Wide diagnostic cameras under24mm not accepted as final room photography'],
        'status':'PASS_GEOMETRY_VISUAL_PENDING' if all(r['issue'] is None for r in rows) else 'FAIL_RETAINED'}
out=ROOT/'qa/camera11-actual-check.json';assert not out.exists()
out.write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({k:report[k] for k in ('status','cameras','pass','fail','changed_vs09','rays')}),flush=True)
print(json.dumps([{'camera':r['camera'],'issue':r['issue']} for r in rows if r['issue']]),flush=True)
