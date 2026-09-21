"""Local animated-water quality and shore sampling, no mutations."""
import bpy,math,hashlib,struct
import numpy as np
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import shrub08_auditlib as shared


def key_state(mesh):
    key=mesh.shape_keys
    if not key:return None
    ad=key.animation_data
    drivers=[]
    if ad:
        for fc in ad.drivers:
            d=fc.driver
            drivers.append({'path':fc.data_path,'index':fc.array_index,'mute':fc.mute,
                'type':d.type,'expression':d.expression,'use_self':d.use_self,
                'variables':[{'name':v.name,'type':v.type,'targets':[shared.props(t) for t in v.targets]} for v in d.variables]})
    return {'key_properties':shared.props(key),'animation':shared.props(ad) if ad else None,'drivers':drivers,
            'blocks':[{'name':k.name,'value':k.value,'relative':k.relative_key.name if k.relative_key else None} for k in key.key_blocks]}


def evaluate(obj):
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();mesh.calc_loop_triangles()
    verts=[ev.matrix_world@v.co for v in mesh.vertices]
    faces=[tuple(p.vertices) for p in mesh.polygons]
    tris=[tuple(t.vertices) for t in mesh.loop_triangles]
    xyz=np.asarray([list(v) for v in verts],dtype=np.float32)
    tri_xyz=xyz[np.asarray(tris,dtype=np.int32)]
    areas=np.linalg.norm(np.cross(tri_xyz[:,1]-tri_xyz[:,0],tri_xyz[:,2]-tri_xyz[:,0]),axis=1)*.5
    counts=Counter(tuple(sorted((a,b))) for p in faces for a,b in zip(p,p[1:]+p[:1]))
    quality={'vertices':len(verts),'polygons':len(faces),'triangles':len(tris),
             'open_edges':sum(n==1 for n in counts.values()),'nonmanifold_edges':sum(n!=2 for n in counts.values()),
             'zero_area_triangles':int(np.sum(areas<1e-10)),
             'zero_area_polygons':sum(p.area<1e-10 for p in mesh.polygons),
             'finite':bool(np.isfinite(xyz).all()),'physical_triangles_sha256':hashlib.sha256(tri_xyz.tobytes()).hexdigest()}
    ev.to_mesh_clear()
    # Use Blender's evaluated loop triangles, not BVH's independent polygon
    # tessellator (which chooses a different diagonal on nonplanar quads).
    bvh=BVHTree.FromPolygons(verts,tris,all_triangles=True)
    # This large box only excludes the local edit neighborhood from a
    # preservation test. It is NEVER used as the geometry trimming mask.
    outside=(xyz[:,0]<23.20)|(xyz[:,0]>31.46)|(xyz[:,1]<-4.20)|(xyz[:,1]>-2.40)|(xyz[:,2]<-3.55)|(xyz[:,2]>.53)
    used=np.zeros(len(verts),dtype=np.bool_)
    used[np.asarray(tris,dtype=np.int32).ravel()]=True
    quality['unused_vertices']=int(np.sum(~used))
    far=set(np.ascontiguousarray(xyz[outside & used]).view(np.dtype((np.void,12))).ravel().tolist())
    return {'quality':quality,'bvh':bvh,'far_vertices':far,'verts':verts,'faces':faces}


def exact_core(source,boundary_count):
    # The actual fan-capped source core, not a bounding rectangle.
    verts=[source.matrix_world@v.co for v in list(source.data.vertices)[:2*boundary_count+2]]
    faces=[tuple(p.vertices) for p in list(source.data.polygons)[:3*boundary_count]]
    return BVHTree.FromPolygons(verts,faces)


def inside_core(point,bvh,margin=.003):
    pos,normal,index,distance=bvh.find_nearest(point)
    return pos is not None and distance>margin and (point-pos).dot(normal)<-margin


def shore_samples(before,cores):
    # Dense, deterministic points at the actual original animated water top.
    samples=[]
    for side,x0,x1 in [('SW',23.20,25.47),('SE',29.43,31.47)]:
        for x in np.arange(x0,x1+.001,.10):
            for y in np.arange(-4.21,-2.40+.001,.10):
                p,n,index,dist=before['bvh'].ray_cast(Vector((float(x),float(y),1)),Vector((0,0,-1)),6)
                if p is None or n.z<.25:continue
                core=cores[side];near,nn,ii,dd=core.find_nearest(p)
                interior=inside_core(p,core)
                # Exterior strip is at least .025m clear of the true core,
                # safely beyond the actual <=.019m source stone projections.
                exterior=near is not None and dd>=.026 and (p-near).dot(nn)>.025
                if interior or exterior:
                    samples.append({'side':side,'xyz':list(p),'kind':'DRY_INSIDE' if interior else 'WET_OUTSIDE',
                                    'distance_to_core_m':dd})
    for x in np.arange(25.50,29.41,.20):
        for y in np.arange(-4.30,-2.29,.20):
            p,n,idx,dist=before['bvh'].ray_cast(Vector((float(x),float(y),1)),Vector((0,0,-1)),6)
            if p is not None and n.z>.25:samples.append({'side':'CHANNEL','xyz':list(p),'kind':'WET_CHANNEL','distance_to_core_m':None})
    return samples


def shore_compare(samples,after):
    failures=[];counts=Counter();maxwet=0.0
    for row in samples:
        p=Vector(row['xyz']);counts[row['kind']]+=1
        if row['kind']=='DRY_INSIDE':
            radius=max(.0005,min(.035,row['distance_to_core_m']-.001))
            hit=after['bvh'].find_nearest(p,radius)[0]
            if hit is not None:failures.append({**row,'failure':'WATER_REMAINS_STRICTLY_INSIDE_CORE','candidate_nearest':list(hit)})
        else:
            hit,n,idx,dist=after['bvh'].ray_cast(p+Vector((0,0,.12)),Vector((0,0,-1)),.25)
            error=abs(hit.z-p.z) if hit is not None else math.inf
            maxwet=max(maxwet,error)
            if error>.00015:failures.append({**row,'failure':'WET_SURFACE_REMOVED_OR_MOVED','height_error_m':error})
    return {'counts':dict(counts),'sample_count':len(samples),'max_retained_wet_height_error_m':maxwet,
            'failures':failures,'method':'Dry: no candidate water surface in a sphere strictly inside actual closed core. Wet/channel: original animated surface height unchanged outside real stone projections. Normal shore contact is not a failure.'}


def endpoint_faces(objects):
    rows=[]
    for obj,plane,count in objects:
        selected=[];bad=[];adjacent_caps=[]
        for p in obj.data.polygons:
            if all(abs(obj.data.vertices[i].co.x-plane)<1e-5 for i in p.vertices):
                selected.append(p.index)
                if p.index>=3*count:
                    ys=[obj.data.vertices[i].co.y for i in p.vertices]
                    # Actual terminal caps of perpendicular facade stones are
                    # <=44mm wide, unlike the removed broad zero-projection
                    # end panels. Do not misidentify them as those panels.
                    if max(ys)-min(ys)>.08:bad.append(p.index)
                    else:adjacent_caps.append(p.index)
        rows.append({'object':obj.name,'finished_x':plane,'core_only_planar_faces':selected,
                     'duplicate_zero_projection_panel_faces':bad,'adjacent_stone_terminal_caps':adjacent_caps,'pass':bool(selected) and not bad,
                     'material':[m.name for m in obj.data.materials]})
    return rows
