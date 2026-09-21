"""Bounded local evidence around two dark doorway pixels; no rendering."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];out=R/'qa/structure08b-remaining-review.json';report=json.loads(out.read_text());bpy.ops.wm.open_mainfile(filepath=report['source_scene']);s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;dg=bpy.context.evaluated_depsgraph_get()
bvhs={}
for ob in s.objects:
    if ob.type!='MESH' or not ob.name.startswith('MAIN_') or not ob.name.endswith('_finish'):continue
    e=ob.evaluated_get(dg);m=e.to_mesh();bvhs[ob.name]=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(f.vertices) for f in m.polygons]);e.to_mesh_clear()
cam=s.objects['CAM_MAIN_L1_LOGGIA_A'];co=cam.data.view_frame(scene=s);xmin,xmax=min(v.x for v in co),max(v.x for v in co);ymin,ymax=min(v.y for v in co),max(v.y for v in co)
def finishes(p):
    hits=[]
    for nm,bvh in bvhs.items():
        q,n,f,dist=bvh.ray_cast(Vector((p[0],p[1],.19)),Vector((0,0,-1)),.16)
        if q is not None and abs(q.z-.122)<.001:hits.append(nm)
    return hits
neighborhoods=[]
for center in [(494,275),(499,293)]:
    for dy in (-8,0,8):
        for dx in (-8,0,8):
            x,y=center[0]+dx,center[1]+dy;d=(cam.matrix_world.to_quaternion()@Vector((xmin+(x+.5)/960*(xmax-xmin),ymax-(y+.5)/540*(ymax-ymin),co[0].z))).normalized();hit,p,n,f,ob,_=s.ray_cast(dg,cam.matrix_world.translation,d,distance=100);q=cam.matrix_world.translation+d*((.122-cam.matrix_world.translation.z)/d.z)
            neighborhoods.append({'center':list(center),'pixel':[x,y],'first':ob.name if hit else None,'first_point':list(p) if hit else None,'floor_source_px':[q.x/.0524+327,540-q.y/.0531],'finish_layers_at_expected_floor':finishes(q)})
overlaps=[]
for label,rect in [('coat_and_threshold',(495,296,512,300)),('entry_and_threshold',(492,301,510,303))]:
    a,b,c,d=rect;poly=[(a,b),(c,b),(c,d),(a,d)];world=[Vector(((x-327)*.0524,(540-y)*.0531,.122)) for x,y in poly];screen=[]
    for p in world:
        q=world_to_camera_view(s,cam,p);screen.append([q.x*960,(1-q.y)*540])
    mid=((a+c)/2,(b+d)/2);q=((mid[0]-327)*.0524,(540-mid[1])*.0531,.122)
    overlaps.append({'name':label,'source_rect':rect,'area_m2':(c-a)*(d-b)*.0524*.0531,'actual_midpoint_finish_layers':finishes(q),'projected_polygon_pixels':screen})
report['doorway_neighborhoods']=neighborhoods;report['entry_coat_coplanar_regions']=overlaps
out.write_text(json.dumps(report,indent=2));print(json.dumps({'neighborhoods':neighborhoods,'overlap_regions':overlaps},indent=2))
