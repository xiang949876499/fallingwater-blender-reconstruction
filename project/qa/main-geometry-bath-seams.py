import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
P=Path('D:/zx/test/project');sys.path.insert(0,str(P/'scripts'))
import main_house
scene=P/'qa/main-geometry-smoke.blend'
bpy.ops.wm.open_mainfile(filepath=str(scene));s=bpy.context.scene
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
settings=json.loads((P/'qa/camera04-review-render-settings.json').read_text(encoding='utf-8'))['CAM_MAIN_B_BATH_B']
cd=bpy.data.cameras.new('bath_seam_probe');cam=bpy.data.objects.new('bath_seam_probe',cd);s.collection.objects.link(cam)
cam.location=settings['location'];cam.rotation_euler=(Vector(settings['target'])-cam.location).to_track_quat('-Z','Y').to_euler()
cd.lens=settings['lens'];cd.shift_x=settings['shift_x'];cd.shift_y=settings['shift_y'];cd.sensor_width=36
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
def hit(a,d,dist=50):
 ok,p,n,i,o,m=s.ray_cast(dg,Vector(a),Vector(d).normalized(),distance=dist)
 return {'object':o.name,'world':list(p),'source_px':[p.x/.0524+327,540-p.y/.0531],'z':p.z} if ok else None
frame=cd.view_frame(scene=s);xmin,xmax=min(v.x for v in frame),max(v.x for v in frame);ymin,ymax=min(v.y for v in frame),max(v.y for v in frame)
pixels=[]
for x,y in [(552,423),(602,480),(639,519),(726,392),(778,449),(871,511)]:
 d=(cam.matrix_world.to_3x3()@Vector((xmin+(x+.5)/960*(xmax-xmin),ymax-(y+.5)/540*(ymax-ymin),frame[0].z))).normalized()
 t=(-2.128-cam.location.z)/d.z;p=cam.location+d*t
 pixels.append({'pixel':[x,y],'projected_floor_source_px':[p.x/.0524+327,540-p.y/.0531],'image_ray_hit':hit(cam.location,d),'downward_hit':hit((p.x,p.y,-2.0),(0,0,-1),5)})
grid=[]
for ix in range(81):
 for iy in range(109):
  px=282+ix*.2;py=253+iy*.25;g=hit(main_house.xyz((px,py),-1.98),(0,0,-1),5)
  # Full opening and adjoining jamb-floor seams; solid walls count as supported.
  grid.append({'source_px':[round(px,2),round(py,2)],'hit':g,'status':'PASS' if g and g['z']>=-2.16 else 'FAIL'})
out={'scene_sha256':hashlib.sha256(scene.read_bytes()).hexdigest(),'camera':settings,'pixels':pixels,'grid':grid,'summary':{'samples':len(grid),'failures':sum(r['status']=='FAIL' for r in grid)},'limits':'Downward support audit over source x282..298,y253..280. Architecture only; over-jamb samples may first hit walls. No photometric acceptance inferred.'}
name='main-geometry-bath-seams-after.json' if '--after' in sys.argv else 'main-geometry-bath-seams-before.json'
(P/'qa'/name).write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'pixels':pixels,'summary':out['summary'],'failure_examples':[r for r in grid if r['status']=='FAIL'][:10]},indent=2))
