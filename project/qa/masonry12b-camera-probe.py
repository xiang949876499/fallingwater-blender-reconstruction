"""Check existing external detail framing after height correction; no rendering."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];Q=R/'qa';sys.path[:0]=[str(R/'scripts'),str(Q)]
import masonry_tower12b as entry
record=json.loads((Q/'masonry12b-build-check.json').read_text(encoding='utf-8'))
path=Path(record['candidate']);assert hashlib.sha256(path.read_bytes()).hexdigest()==record['candidate_sha256']
bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.frame_set(48)
cfg=json.loads((Q/'masonry12-camera-settings.json').read_text())['CAM_WATER_DETAIL']
eye=Vector(cfg['location']);look=(Vector(cfg['target'])-eye).normalized();right=look.cross(Vector((0,0,1))).normalized();up=right.cross(look).normalized()
names=list(entry.LOWER)+list(entry.MODIFIED)+record['application']['added']
def roi(lens):
 half=s.objects['CAM_WATER_DETAIL'].data.sensor_width/(lens*2);vhalf=half*540/960;pixels=[]
 for name in names:
  ob=s.objects[name]
  for vertex in ob.data.vertices:
   p=ob.matrix_world@vertex.co-eye;depth=p.dot(look)
   pixels.append([(.5+.5*p.dot(right)/(depth*half))*960,(.5-.5*p.dot(up)/(depth*vhalf))*540])
 return [[min(p[i] for p in pixels),max(p[i] for p in pixels)] for i in range(2)]
original=roi(cfg['lens']);output=original;changed=False
if not (0<=original[0][0]<original[0][1]<=960 and 0<=original[1][0]<original[1][1]<=540):
 cfg['lens']=32.0;output=roi(cfg['lens']);changed=True
assert 0<=output[0][0]<output[0][1]<=960 and 0<=output[1][0]<output[1][1]<=540,output
(Q/'masonry12b-camera-settings.json').write_text(json.dumps({'CAM_WATER_DETAIL':cfg},indent=2),encoding='utf-8')
out={'status':'PASS_TOWER_FRAMING_PROBE_NO_RENDER','source_36mm_roi_960x540':original,'proposed_roi_960x540':output,
     'external_lens_changed_to_keep_corrected_top_in_frame':changed,'settings':cfg,'saved_camera_changed':False,
     'candidate_sha256':record['candidate_sha256'],'rendered':False,
     'comparison_rule':'Apply these identical external settings to12a and12b if comparing detail. Do not compare32mm12b to old36mm12a image. HERO remains its saved camera.'}
(Q/'masonry12b-camera-probe.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
