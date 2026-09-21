"""Frozen single-camera diagnostics, evaluated triangles; no scene changes/save."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
fit=json.loads((ROOT/'qa/photo-match12-guest-shift-fit.json').read_text(encoding='utf-8'))
source=Path(fit['scene']);assert hashlib.sha256(source.read_bytes()).hexdigest()==fit['scene_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
eye=Vector(fit['camera']['eye_m']);R=Matrix(fit['camera']['world_to_opencv']);f=fit['camera']['focal_px'];cx,cy=fit['camera']['principal_point_px']
def cast(a,d,length=500):
    hit,loc,norm,idx,obj,matrix=scene.ray_cast(dg,Vector(a),Vector(d).normalized(),distance=length)
    if not hit:return {'hit':False}
    return {'hit':True,'object':obj.name,'evaluated_face_index':idx,'position_m':list(loc),'normal':list(norm),'distance_m':(loc-Vector(a)).length}
rows=[]
for p in fit['points']:
    target=Vector(p['world_m']);distance=(target-eye).length
    projected=cast(eye,target-eye,distance+.10)
    px,py=p['pixel'];direction=R.transposed()@Vector(((px-cx)/f,(py-cy)/f,1))
    observed=cast(eye,direction)
    blockage=cast(eye,target-eye,max(.01,distance-.025))
    projected['distance_to_landmark_m']=(Vector(projected['position_m'])-target).length if projected['hit'] else None
    rows.append({'id':p['id'],'target_object':p['object'],'target_world_m':list(target),
       'model_projection_first_hit':projected,'observed_pixel_first_hit':observed,
       'blocking_before_target_25mm':blockage,'visibility_status':'EARLIER_OBSTRUCTION' if blockage['hit'] else 'NO_OBSTRUCTION_MORE_THAN25MM_BEFORE_TARGET'})
support=[]
for dx,dy in [(0,0),(.18,0),(-.18,0),(0,.18),(0,-.18)]:
    q=eye+Vector((dx,dy,0));row=cast(q,(0,0,-1),20);row['offset_xy_m']=[dx,dy]
    if row['hit']:row['eye_height_above_first_support_m']=eye.z-row['position_m'][2]
    support.append(row)
# Actual boundary vertices are checked against evaluated mesh vertices; bevels
# may trim a corner so report distance, never silently substitute a different one.
geometry=[]
for p in fit['points']:
    ob=bpy.data.objects[p['object']];ev=ob.evaluated_get(dg);me=ev.to_mesh();target=Vector(p['world_m'])
    nearest=min(((ob.matrix_world@v.co-target).length,i) for i,v in enumerate(me.vertices))
    geometry.append({'id':p['id'],'target_to_nearest_evaluated_vertex_m':nearest[0],'nearest_evaluated_vertex':nearest[1],
        'base_face_locator':p.get('adjacent_base_faces'),'note':'For edge-midpoints nearest vertex distance is not a surface gap; whole original edge is verified in locked locator.'})
    ev.to_mesh_clear()
out={'scene_sha256':fit['scene_sha256'],'camera_source':'photo-match12-guest-shift-fit.json','rows':rows,'support_probes':support,
     'evaluated_vertex_checks':geometry,'scope':'All evaluated scene meshes and actual saved geometry, scene.ray_cast; no collision exclusions, no camera or mesh changes/save.',
     'caveat':'First-hit glass is a physical intersected surface but may be optically transparent; report material/object identity before treating as visual occlusion.'}
(ROOT/'qa/photo-match12-guest-shift-rays.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'support':support,'earlier_occlusions':[(r['id'],r['blocking_before_target_25mm'].get('object')) for r in rows if r['blocking_before_target_25mm']['hit']]},indent=2))
assert hashlib.sha256(source.read_bytes()).hexdigest()==fit['scene_sha256']
