"""Read-only bridge10/old-river intersection coordinates and interior water area."""
import bpy,sys,json,hashlib,math
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];Q=ROOT/'qa'
check=json.loads((Q/'bridge10-candidate-check.json').read_text())
SOURCE=Path(check['candidate'])
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==check['candidate_sha256']
if Path(bpy.data.filepath)!=SOURCE:bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
bpy.context.scene.frame_set(48);bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
def geometry(obj):
    ev=obj.evaluated_get(deps);m=ev.to_mesh();m.calc_loop_triangles()
    verts=[ev.matrix_world@v.co for v in m.vertices]
    faces=[tuple(t.vertices) for t in m.loop_triangles]
    normals=[list(t.normal) for t in m.loop_triangles]
    ev.to_mesh_clear()
    return verts,faces,normals
def aabb(points):
    return [f(p[i] for p in points) for i in range(3) for f in (min,max)] if points else None
def clip(poly,axis,limit,greater):
    result=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        da=a[axis]-limit;db=b[axis]-limit
        ia=da>=-1e-8 if greater else da<=1e-8
        ib=db>=-1e-8 if greater else db<=1e-8
        if ia:result.append(a)
        if ia != ib:
            t=da/(da-db);result.append(a+(b-a)*t)
    return result
def rectangle_clip(poly,box):
    for axis,lim,greater in ((0,box[0],True),(0,box[1],False),(1,box[2],True),(1,box[3],False)):
        if not poly:break
        poly=clip(poly,axis,lim,greater)
    return poly
def area_xy(poly):
    return abs(sum(a.x*b.y-b.x*a.y for a,b in zip(poly,poly[1:]+poly[:1])))/2 if len(poly)>=3 else 0
def plane_clip(poly,fn):
    result=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        da,db=fn(a),fn(b);ia,ib=da>=-1e-8,db>=-1e-8
        if ia:result.append(a)
        if ia != ib:result.append(a+(b-a)*(da/(da-db)))
    return result
def triangle_column_clip(poly,base):
    # CCW bottom triangle; retain the vertical column above its actual plane.
    for a,b in zip(base,base[1:]+base[:1]):
        if not poly:return []
        poly=plane_clip(poly,lambda p,a=a,b=b:(b.x-a.x)*(p.y-a.y)-(b.y-a.y)*(p.x-a.x))
    if not poly:return []
    normal=(base[1]-base[0]).cross(base[2]-base[0])
    assert normal.z>0
    poly=plane_clip(poly,lambda p:(p-base[0]).dot(normal))
    return clip(poly,2,.515,False) if poly else []
def triangle_intersections(a,b):
    result=[]
    for tri,other in ((a,b),(b,a)):
        for p,q in zip(tri,tri[1:]+tri[:1]):
            d=q-p
            if d.length<1e-9:continue
            hit=intersect_ray_tri(other[0],other[1],other[2],d,p,True)
            if hit is None:continue
            t=(hit-p).dot(d)/d.length_squared
            if -1e-6<=t<=1+1e-6:result.append(hit)
    return result
water=bpy.context.scene.objects['WATER_BearRun_Continuous_Upstream_Downstream']
wv,wf,wn=geometry(water);wb=BVHTree.FromPolygons(wv,wf,all_triangles=True)
water_xyz=np.asarray([list(p) for p in wv],dtype=np.float64)[np.asarray(wf,dtype=np.int32)]
water_low=water_xyz.min(axis=1);water_high=water_xyz.max(axis=1)
rects={
 'SITE_Bridge10_Stone_Return_SW':[(23.255,23.855,-4.15,-2.475),(23.855,25.43044,-3.075,-2.475)],
 'SITE_Bridge10_Stone_Return_SE':[(30.81,31.41,-4.15,-2.475),(29.46904,30.81,-3.075,-2.475)],
 'SITE_Bridge10_Stone_Return_NW':[(23.465,24.065,6.3275,7.98),(24.065,25.38,6.3275,6.9275)],
 'SITE_Bridge10_Stone_Return_NE':[(30.81,31.41,6.3275,7.98),(29.46904,30.81,6.3275,6.9275)]}
records=[]
for name,boxes in rects.items():
    obj=bpy.context.scene.objects[name];sv,sf,sn=geometry(obj);sb=BVHTree.FromPolygons(sv,sf,all_triangles=True)
    record=next(r for r in check['application']['stone_returns'] if r['name']==name)
    count=record['contact_outline_samples'];center=sv[2*count]
    base_triangles=[[sv[i],sv[(i+1)%count],center] for i in range(count)]
    pairs=sb.overlap(wb);points={};water_ids=set()
    for si,wi in pairs:
        aa=[sv[i] for i in sf[si]];bb=[wv[i] for i in wf[wi]]
        hits=triangle_intersections(aa,bb)
        if hits:water_ids.add(wi)
        for p in hits:points[tuple(round(float(v),6) for v in p)]=list(p)
    inside=[];total_area=0;up_area=0
    bbox=aabb(sv)
    candidates=np.flatnonzero((water_high[:,0]>=bbox[0]) & (water_low[:,0]<=bbox[1]) &
                             (water_high[:,1]>=bbox[2]) & (water_low[:,1]<=bbox[3]) &
                             (water_high[:,2]>=bbox[4]) & (water_low[:,2]<=bbox[5]))
    for wi in candidates:
        wi=int(wi);face=wf[wi]
        poly=[wv[i] for i in face]
        for base in base_triangles:
            clipped=triangle_column_clip(poly,base)
            area=area_xy(clipped)
            if area<=1e-8:continue
            total_area+=area
            if wn[wi][2]>.25:up_area+=area
            inside.append({'water_triangle':wi,'upward_facing':wn[wi][2]>.25,'area_xy_m2':area,'clipped_xyz':[list(p) for p in clipped]})
    xyz=list(points.values());inside_xyz=[p for r in inside for p in r['clipped_xyz']]
    record={'bridge_object':name,'actual_intersection_points_xyz':xyz,'actual_intersection_aabb_xyz_pairs':aabb(xyz),
            'exact_crossing_water_triangles':sorted(water_ids),'candidate_bvh_pair_count':len(pairs),
            'water_triangles_after_spatial_prefilter':len(candidates),
            'retained_water_inside_core_footprint_area_xy_m2':total_area,'upward_water_inside_core_area_xy_m2':up_area,
            'interior_area_method':'Water triangles clipped to every actual lower core triangle vertical column and above its sloping bottom plane, then below +.515m cap. Exact piecewise linear closed core volume; panels excluded from area but included in intersection points. Both surface orientations summed separately.',
            'inside_water_aabb_xyz_pairs':aabb(inside_xyz),'inside_clipped_triangles':inside,
            'C_core_footprint_rectangles_xy_pairs':boxes,'masonry_cap_z':.515,
            'surface_panels':'Use evaluated bridge solid for final trim; shallow face projections extend up to .019m outside these core rectangles. Inward SOUTH end planes must remain x25.43044/29.46904.',
            'water_above_finished_paving':any(p[2]>.012 for p in xyz+inside_xyz),
            'water_above_existing_deck_bottom':any(p[2]>-.555 for p in xyz+inside_xyz)}
    records.append(record)
output={'status':'READ_ONLY_SPATIAL_DIAGNOSIS','candidate_sha256':check['candidate_sha256'],'source_full09_sha256':check['source_sha256'],
        'frame':48,'water_object':water.name,'water_bounds_xyz_pairs':aabb(wv),'water_triangles':len(wf),'targets':records,
        'interpretation':'A water surface meeting a bank is normal. Nonzero clipped water area inside the closed masonry core is actual untrimmed geometric penetration, not merely contact. All crossing elevations are reported relative to unchanged paving/deck; this does not claim visibility from a rendered camera.',
        'future_cut_boundary':'Restrict future water trim to these evaluated SW/SE masonry volumes where intersection is nonempty, at existing water level. Do not remove the bridge, lower terrain/core, or cut the entire AABB rectangle. Subdivide crossing water triangles and keep their portion outside actual masonry; preserve unobstructed central stream and all elevations.',
        'water_changed':False,'core_or_terrain_changed':False,'rendered':False}
views=[]
for name,location,target,lens in [
    ('QA_BRIDGE10_SOUTH_APPROACH',(27.45,-10.5,1.8),(27.45,2.0,.25),28),
    ('QA_BRIDGE10_HOUSE_SIDE',(18.0,1.0,3.8),(27.45,1.5,-.25),28)]:
    p=Vector(location);near=[]
    for d in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
        hit,loc,norm,idx,obj,mat=bpy.context.scene.ray_cast(deps,p,Vector(d),distance=.20)
        if hit:near.append({'object':obj.name,'xyz':list(loc)})
    samples=[]
    for t in [Vector(target),Vector((25.045,-2.2,.25)),Vector((25.045,6.1,.25))]:
        direction=t-p
        hit,loc,norm,idx,obj,mat=bpy.context.scene.ray_cast(deps,p,direction.normalized(),distance=direction.length+.05)
        samples.append({'aim_xyz':list(t),'first_hit':obj.name if hit else None,'hit_xyz':list(loc) if hit else None,'distance_m':(loc-p).length if hit else None})
    views.append({'name':name,'location_C_xyz':location,'target_C_xyz':target,'lens_mm_C':lens,'near_0_20m_hits':near,'line_of_sight_samples':samples,
                  'purpose':'Temporary QA camera suggestion only; not created or added to saved scene; apply same view to source09 and candidate, frame48, unchanged exposure'})
output['root_double_view_suggestions']=views
(Q/'bridge10-water-spatial-mask.json').write_text(json.dumps(output,indent=2),encoding='utf8')
summary={'candidate_sha256':output['candidate_sha256'],'water_bounds':output['water_bounds_xyz_pairs'],'targets':[{k:r[k] for k in ('bridge_object','actual_intersection_aabb_xyz_pairs','retained_water_inside_core_footprint_area_xy_m2','upward_water_inside_core_area_xy_m2','inside_water_aabb_xyz_pairs','water_above_finished_paving','water_above_existing_deck_bottom')} for r in records]}
(Q/'bridge10-water-spatial-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
print('BRIDGE10_WATER_SPATIAL',json.dumps(summary),flush=True)
