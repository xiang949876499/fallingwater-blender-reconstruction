"""Frozen07 floor defects: actual camera rays and coincident upward surfaces."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];src=R/'scene/Fallingwater_iteration07.blend'
assert hashlib.sha256(src.read_bytes()).hexdigest()=='bf50530009e4a93315915815473188c91d891272ef2d8e9e0169b704bd2e2f16'
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4
s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100;dg=bpy.context.evaluated_depsgraph_get()
groups={'CAM_MAIN_L2_BATH_N_A':[(115,323),(200,277),(266,244),(182,261),(188,300)],'CAM_MAIN_L2_BATH_G_B':[(270,169),(300,174),(200,248),(270,268),(480,316)],'CAM_MAIN_L2_BATH_M_B':[(526,331),(615,242)],'CAM_MAIN_L2_DRESSING_B':[(170,302),(331,295),(416,292),(472,337)],'CAM_MAIN_L3_GALLERY_B':[(390,308),(390,333),(395,277)],'CAM_MAIN_L3_STAIR_B':[(343,180),(320,203)]}
bounds={};floor_bvhs={}
for ob in s.objects:
    if ob.type!='MESH' or not ob.name.startswith(('MAIN_L2_','MAIN_L3_','MAIN_floor_threshold_','MAIN_stone_tower')):continue
    if len(ob.data.vertices)>350:continue
    e=ob.evaluated_get(dg);m=e.to_mesh();vv=[e.matrix_world@v.co for v in m.vertices]
    bb=[[min(v[k] for v in vv),max(v[k] for v in vv)] for k in range(3)]
    bounds[ob.name]=bb
    if any(t in ob.name for t in ('slab','finish','threshold','landing','floor')):
        floor_bvhs[ob.name]=BVHTree.FromPolygons(vv,[tuple(p.vertices) for p in m.polygons])
    e.to_mesh_clear()
out=[]
for name,pixels in groups.items():
    cam=s.objects[name];co=cam.data.view_frame(scene=s);xlo,xhi=min(q.x for q in co),max(q.x for q in co);ylo,yhi=min(q.y for q in co),max(q.y for q in co)
    for x,y in pixels:
        d=(cam.matrix_world.to_quaternion()@Vector((xlo+(x+.5)/640*(xhi-xlo),yhi-(y+.5)/360*(yhi-ylo),co[0].z))).normalized()
        origin=cam.matrix_world.translation;hit,p,n,f,ob,_=s.ray_cast(dg,origin,d,distance=100)
        z=5.28615 if '_L3_' in name else 2.8668;ideal=origin+d*((z-origin.z)/d.z)
        surfaces=[]
        for nm,b in floor_bvhs.items():
            loc,no,face,dist=b.ray_cast(Vector((ideal.x,ideal.y,z+.08)),Vector((0,0,-1)),.16)
            if loc is not None:surfaces.append({'name':nm,'z':loc.z,'normal':list(no)})
        out.append({'camera':name,'pixel':[x,y],'first':ob.name if hit else None,'point':list(p) if hit else None,'normal':list(n) if hit else None,'floor_intersection':list(ideal),'source_px':[ideal.x/.0524+327,540-ideal.y/.0531],'floor_surfaces':surfaces})
(R/'qa/floor08-probe.json').write_text(json.dumps({'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'pixels':out,'bounds':bounds},indent=2))
print(json.dumps(out,indent=2))
