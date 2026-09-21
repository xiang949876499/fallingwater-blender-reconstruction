"""Opt-in Master ceiling topology candidate on frozen iteration10.

No production hook or import-time mutation. The northern/high underside stays
5.0m, the south/low underside4.8468m and the existing break stays C. Columbia
photos plus HABS main10 support a continuous southern low field, not the former
297mm strip. Exact elevations/break position remain C; source graphical step
0.417+/-0.04m differs from this candidate's0.1532m and remains OPEN.
"""
import math
import bpy
from mathutils import Vector, Matrix

CEILING='MAIN_L2_MASTER_ceiling'
STRIP='MASTER_DETAIL10_west_connected_soffit'
LEAF_PREFIX='MAIN_L2_master_south_open_casement_'
LEAF_SUFFIXES=('sill','head','mullion_0','mullion_1','transom_0','glass_0')
LEAF_NAMES=tuple(LEAF_PREFIX+s for s in LEAF_SUFFIXES)+('MAIN_L2_master_south_latch',)
CHANGED=(CEILING,)+LEAF_NAMES
REMOVED=(STRIP,)

def bounds(o):
    p=[o.matrix_world@v.co for v in o.data.vertices]
    return [(min(v[k] for v in p),max(v[k] for v in p)) for k in range(3)]

def inside(p,poly):
    x,y=p;result=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:result=not result
    return result

def unified_ceiling_mesh(high,low,zlow,zhigh,ztop):
    # Full orthogonal coordinate arrangement avoids mismatched edge splits and
    # T-junctions. Emit only exposed cells: no internal coincident faces.
    xs=sorted(set(p[0] for p in high+low));ys=sorted(set(p[1] for p in high+low))
    zs=[zlow,zhigh,ztop];cells=set()
    for i in range(len(xs)-1):
        for j in range(len(ys)-1):
            p=((xs[i]+xs[i+1])/2,(ys[j]+ys[j+1])/2)
            is_low=inside(p,low);is_high=inside(p,high)
            if is_low:cells.add((i,j,0))
            if is_low or is_high:cells.add((i,j,1))
    verts=[];indices={};faces=[]
    def vertex(key):
        if key not in indices:
            indices[key]=len(verts);verts.append((xs[key[0]],ys[key[1]],zs[key[2]]))
        return indices[key]
    # Outward-wound faces for each of the six voxel sides.
    for i,j,k in sorted(cells):
        for delta,keys in [
            ((-1,0,0),[(i,j,k),(i,j,k+1),(i,j+1,k+1),(i,j+1,k)]),
            ((1,0,0),[(i+1,j,k),(i+1,j+1,k),(i+1,j+1,k+1),(i+1,j,k+1)]),
            ((0,-1,0),[(i,j,k),(i+1,j,k),(i+1,j,k+1),(i,j,k+1)]),
            ((0,1,0),[(i,j+1,k),(i,j+1,k+1),(i+1,j+1,k+1),(i+1,j+1,k)]),
            ((0,0,-1),[(i,j,k),(i,j+1,k),(i+1,j+1,k),(i+1,j,k)]),
            ((0,0,1),[(i,j,k+1),(i+1,j,k+1),(i+1,j+1,k+1),(i,j+1,k+1)])]:
            if (i+delta[0],j+delta[1],k+delta[2]) not in cells:faces.append([vertex(q) for q in keys])
    m=bpy.data.meshes.new('MASTER_CEILING11_single_stepped_enclosure')
    m.from_pydata(verts,[],faces);m.update();return m

def apply(*,enabled=False):
    if not enabled:return {'status':'DISABLED_NO_MUTATION'}
    s=bpy.context.scene
    assert CEILING in s.objects and STRIP in s.objects,'Requires unmodified frozen10 Master ceiling'
    assert not s.objects[CEILING].get('master_ceiling11'),'Already applied'
    for n in LEAF_NAMES:assert n in s.objects,n
    ceiling=s.objects[CEILING];old=bounds(ceiling);strip=bounds(s.objects[STRIP])
    assert abs(old[2][0]-5)<2e-6 and abs(old[2][1]-5.018)<2e-6
    assert abs(strip[2][0]-4.8468)<2e-6
    assert abs(strip[1][1]-9.8766)<2e-6
    # Preserve the entire old high-ceiling perimeter in the north. Use actual
    # loaded faces for the new low field: window heads keep their existing5mm
    # ceiling lap, while the west strip reaches full-height stone backing.
    bottom=min(ceiling.data.polygons,key=lambda p:p.normal.z)
    high=[tuple((ceiling.matrix_world@ceiling.data.vertices[i].co)[:2]) for i in bottom.vertices]
    stone=bounds(s.objects['MAIN_L2_master_hearth'])
    tall=bounds(s.objects['MASTER_DETAIL10_hearth_tall_return'])
    split=strip[1][1];east=old[0][1];south=old[1][0];west=old[0][0]
    low=[(tall[0][1],split),(east,split),(east,south),(west,south),
         (west,stone[1][0]),(stone[0][1],stone[1][0]),
         (stone[0][1],tall[1][0]),(tall[0][1],tall[1][0])]
    mats=list(ceiling.data.materials)
    ceiling.data=unified_ceiling_mesh(high,low,4.8468,5.0,old[2][1]);ceiling.matrix_world=Matrix.Identity(4)
    for mat in mats:ceiling.data.materials.append(mat)
    ceiling['master_ceiling11']='B topology, C breakY and Z; source graphical height discrepancy OPEN'
    ceiling['master_ceiling11_low_polygon']=str(low)
    ceiling['master_ceiling11_source']='qa/master-ceiling11-source-review.md'
    bpy.data.objects.remove(s.objects[STRIP],do_unlink=True)
    # The reference leaf opens toward the terrace. Only rigidly rotate the six
    # existing leaf members and its latch about the actual vertical hinge axis.
    # Retain dimensions, mesh identity, materials and fixed window/hinge parts.
    hinges=[s.objects['MAIN_L2_master_south_hinge'],s.objects['MAIN_L2_master_south_hinge.001']]
    h=[o.matrix_world.translation.copy() for o in hinges]
    assert (h[0].xy-h[1].xy).length<1e-5
    pivot=Vector((h[0].x,h[0].y,0))
    free=s.objects[LEAF_PREFIX+'mullion_1'].matrix_world.translation.copy()
    theta=math.atan2(free.y-pivot.y,free.x-pivot.x)
    assert abs(math.degrees(theta)-78)<.01,'Unexpected leaf pose; re-audit required'
    angle=-2*theta
    rot=Matrix.Translation(pivot)@Matrix.Rotation(angle,4,'Z')@Matrix.Translation(-pivot)
    for n in LEAF_NAMES:
        o=s.objects[n];o.matrix_world=rot@o.matrix_world
        o['master_ceiling11_swing']='B outward direction; retained C magnitude78deg and original pivot/size'
    bpy.context.view_layer.update()
    return {'status':'APPLIED_TOPOLOGY_CANDIDATE','changed':list(CHANGED),'removed':list(REMOVED),'added':[],
            'high_polygon_world':high,'low_polygon_world':low,'z':[4.8468,5.0,old[2][1]],
            'break_world_y':split,'hinge_axis_xy':list(pivot)[:2],'leaf_rotation_delta_degrees':math.degrees(angle),
            'fixed_window_members_changed':False,'source_height_status':'OPEN_C0.417+/-0.04_vs_candidate0.1532',
            'camera_registration':'GEO-07_NOT_RUN','route_and_render':'NOT_RUN_BY_HELPER'}
