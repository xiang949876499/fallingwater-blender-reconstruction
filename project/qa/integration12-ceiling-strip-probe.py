from pathlib import Path
import hashlib,json
import bpy
from mathutils import Vector

root=Path(__file__).resolve().parents[1]
source=root/'scene/Fallingwater_integration_candidate12a.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='50e0a8fc0bab10fdec0e0b9d26c4ef4a4c71fa56aea6401e75197787c8c0e75a'
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene;s.frame_set(48)
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
cam=s.objects['CAM_GUEST_L1_THEATER_A'];s.camera=cam
frame=cam.data.view_frame(scene=s)
xmin=min(v.x for v in frame);xmax=max(v.x for v in frame)
ymin=min(v.y for v in frame);ymax=max(v.y for v in frame)
dep=bpy.context.evaluated_depsgraph_get()
rows=[]
for x,y in [(440,40),(600,75),(800,117),(925,144),(600,55),(600,98),(800,100),(800,138)]:
    local=Vector((xmin+(x+.5)/1280*(xmax-xmin),ymax-(y+.5)/720*(ymax-ymin),frame[0].z))
    direction=(cam.matrix_world.to_quaternion()@local).normalized()
    origin=cam.matrix_world.translation.copy();hits=[]
    for i in range(6):
        hit,p,n,idx,ob,matrix=s.ray_cast(dep,origin,direction,distance=100)
        if not hit:break
        eval_ob=ob.evaluated_get(dep)
        poly=eval_ob.data.polygons[idx] if eval_ob.type=='MESH' and 0<=idx<len(eval_ob.data.polygons) else None
        mat=(eval_ob.data.materials[poly.material_index].name if poly is not None and poly.material_index<len(eval_ob.data.materials) and eval_ob.data.materials[poly.material_index] else None)
        hits.append({'object':ob.name,'position':list(p),'normal':list(n),'distance_from_eye':(p-cam.matrix_world.translation).length,'face':idx,'material':mat})
        origin=p+direction*.00001
    rows.append({'pixel':[x,y],'hits':hits})
(root/'qa/integration12-ceiling-strip-probe.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'camera':cam.name,'rows':rows},indent=2),encoding='utf-8')
print(json.dumps(rows),flush=True)
