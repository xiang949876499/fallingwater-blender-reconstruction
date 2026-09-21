"""Read-only exact 960x540 remaining render defects; no scene/source mutation."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];SRC=R/'scene/Fallingwater_iteration08.blend'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='c5cd501e4c8ae0205ecb2437cd2d06d0c92bcc9a87e7d93d3986aeef976070d7'
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;dg=bpy.context.evaluated_depsgraph_get()
groups={'CAM_MAIN_L3_BATH_A':[(163,318),(270,275),(384,229),(411,195),(874,478)],'CAM_MAIN_L3_ALCOVE_B':[(104,410)],'CAM_MAIN_L3_STAIR_A':[(625,327)]}
bvhs={};bounds={}
for ob in s.objects:
    if ob.type!='MESH' or not ob.name.startswith(('MAIN_','FW_FURN_MAIN_')) or len(ob.data.vertices)>500:continue
    e=ob.evaluated_get(dg);m=e.to_mesh();vv=[e.matrix_world@v.co for v in m.vertices]
    bounds[ob.name]=[[min(p[k] for p in vv),max(p[k] for p in vv)] for k in range(3)];bvhs[ob.name]=BVHTree.FromPolygons(vv,[tuple(f.vertices) for f in m.polygons]);e.to_mesh_clear()
out=[]
for name,pixels in groups.items():
    cam=s.objects[name];co=cam.data.view_frame(scene=s);xmin,xmax=min(v.x for v in co),max(v.x for v in co);ymin,ymax=min(v.y for v in co),max(v.y for v in co)
    for x,y in pixels:
        origin=cam.matrix_world.translation;d=(cam.matrix_world.to_quaternion()@Vector((xmin+(x+.5)/960*(xmax-xmin),ymax-(y+.5)/540*(ymax-ymin),co[0].z))).normalized()
        hit,p,n,f,ob,_=s.ray_cast(dg,origin,d,distance=100);near=[]
        if hit:
            for nm,bvh in bvhs.items():
                q,no,face,dist=bvh.ray_cast(p-d*.035,d,.070)
                if q is not None:near.append({'name':nm,'point':list(q),'distance_from_first_m':(q-p).length,'normal':list(no)})
        z=5.28615;expected=origin+d*((z-origin.z)/d.z);plane_surfaces=[]
        for nm,bvh in bvhs.items():
            if not any(t in nm for t in ('finish','slab','threshold','ceiling','stair','pier','entry','loggia')):continue
            direction=Vector((0,0,1)) if z==5. else Vector((0,0,-1));q,no,face,dist=bvh.ray_cast(expected-direction*.10,direction,.20)
            if q is not None:plane_surfaces.append({'name':nm,'z':q.z,'normal':list(no)})
        spatial=[]
        for nm,b in bounds.items():
            if not nm.startswith('MAIN_') or nm.endswith(('slab','finish')):continue
            if b[0][0]-.12<=expected.x<=b[0][1]+.12 and b[1][0]-.12<=expected.y<=b[1][1]+.12 and b[2][0]<=z+.15 and b[2][1]>=z-.15:spatial.append(nm)
        out.append({'camera':name,'pixel':[x,y],'camera_origin':list(origin),'ray_direction':list(d),'first_object':ob.name if hit else None,'first_point':list(p) if hit else None,'first_normal':list(n) if hit else None,'first_face':f,'first_material':ob.data.materials[ob.data.polygons[f].material_index].name if hit and ob.type=='MESH' and f<len(ob.data.polygons) and len(ob.data.materials) else None,'near_surfaces':near,'expected_z':z,'expected_plane_point':list(expected),'source_px':[expected.x/.0524+327,540-expected.y/.0531],'vertical_surfaces_at_expected_plane':plane_surfaces,'nearby_architecture':spatial})
result={'status':'READ_ONLY_DIAGNOSTIC_PENDING_SOURCE_CLASSIFICATION','source_scene':str(SRC),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'source_script_sha256':hashlib.sha256((R/'scripts/main_house.py').read_bytes()).hexdigest(),'render_resolution':[960,540],'actual_images_opened':list(groups),'results':out,'bounds':bounds}
(R/'qa/structure09-extra-probe.json').write_text(json.dumps(result,indent=2));print(json.dumps([{k:r[k] for k in ('camera','pixel','first_object','first_point','source_px','vertical_surfaces_at_expected_plane','nearby_architecture')} for r in out],indent=2))
