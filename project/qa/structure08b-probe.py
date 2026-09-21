"""Six bounded anomaly categories; exact first hits and near-coincident geometry."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];src=R/'scene/Fallingwater_floor_core_candidate08.blend';assert hashlib.sha256(src.read_bytes()).hexdigest()=='c78cab9c1d1d3341c72ac926da1abe931902f4c0381e49e956c6c814c930ddc7'
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100;dg=bpy.context.evaluated_depsgraph_get()
groups={'CAM_MAIN_L1_SERVANT_B':[(158,120),(198,104),(245,86),(294,25),(294,44)],'CAM_MAIN_L1_LOGGIA_A':[(300,280),(315,278),(233,290)],'CAM_MAIN_L2_TERRACE_N_B':[(314,317),(315,314),(307,309)],'CAM_MAIN_L2_CLOSET_G_A':[(230,83),(226,80),(239,94)],'CAM_MAIN_L2_GUEST_A':[(58,29),(138,46),(145,37),(200,42)],'CAM_MAIN_L2_MASTER_A':[(170,60),(240,64),(115,58),(301,66)]}
bvhs={};bounds={}
for ob in s.objects:
    if ob.type!='MESH' or not ob.name.startswith(('MAIN_','FW_FURN_MAIN_')) or len(ob.data.vertices)>500:continue
    e=ob.evaluated_get(dg);m=e.to_mesh();vv=[e.matrix_world@v.co for v in m.vertices];bounds[ob.name]=[[min(p[k] for p in vv),max(p[k] for p in vv)] for k in range(3)]
    bvhs[ob.name]=BVHTree.FromPolygons(vv,[tuple(f.vertices) for f in m.polygons]);e.to_mesh_clear()
out=[]
for name,pixels in groups.items():
    cam=s.objects[name];co=cam.data.view_frame(scene=s);xmin,xmax=min(v.x for v in co),max(v.x for v in co);ymin,ymax=min(v.y for v in co),max(v.y for v in co)
    for x,y in pixels:
        d=(cam.matrix_world.to_quaternion()@Vector((xmin+(x+.5)/640*(xmax-xmin),ymax-(y+.5)/360*(ymax-ymin),co[0].z))).normalized();o=cam.matrix_world.translation
        hit,p,n,face,ob,_=s.ray_cast(dg,o,d,distance=100)
        close=[]
        if hit:
            for nm,bvh in bvhs.items():
                q,nn,fi,dist=bvh.ray_cast(p-d*.03,d,.06)
                if q is not None:close.append({'name':nm,'point':list(q),'distance_from_hit_m':(q-p).length,'normal':list(nn)})
        plane_z=.122 if '_SERVANT_' in name or '_LOGGIA_' in name else (2.8668 if '_TERRACE_N_' in name else 5.)
        expected=o+d*((plane_z-o.z)/d.z)
        out.append({'camera':name,'pixel':[x,y],'first':ob.name if hit else None,'point':list(p) if hit else None,'normal':list(n) if hit else None,'face':face,'near_surfaces':close,'expected_plane_z':plane_z,'plane_intersection':list(expected),'plane_source_px':[expected.x/.0524+327,540-expected.y/.0531]})
(R/'qa/structure08b-probe.json').write_text(json.dumps({'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'pixels':out,'bounds':bounds},indent=2));print(json.dumps(out,indent=2))
