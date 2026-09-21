"""Shared meter-scale mesh primitives. No context-dependent selection required."""
import math
import bpy
from mathutils import Vector


def collection(name):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll


def _link(name, mesh, material, coll):
    obj = bpy.data.objects.new(name, mesh)
    (collection(coll) if isinstance(coll, str) else coll).objects.link(obj)
    if material is not None:
        mesh.materials.append(material)
    return obj


def mesh_object(name, vertices, faces, material, coll, smooth=False):
    mesh = bpy.data.meshes.new(name + '_mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    if smooth:
        for polygon in mesh.polygons:
            polygon.use_smooth = True
    return _link(name, mesh, material, coll)


def box(name, center, size, material, collection, bevel=0.02):
    sx, sy, sz = (max(abs(float(v)), 0.0001) / 2 for v in size)
    verts = [(-sx,-sy,-sz),(sx,-sy,-sz),(sx,sy,-sz),(-sx,sy,-sz),
             (-sx,-sy,sz),(sx,-sy,sz),(sx,sy,sz),(-sx,sy,sz)]
    faces = [(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
    obj = mesh_object(name, verts, faces, material, collection)
    obj.location = center
    if bevel and min(sx, sy, sz) > 0.001:
        mod = obj.modifiers.new('Crafted edges', 'BEVEL')
        mod.width = min(float(bevel), min(sx,sy,sz)*0.4)
        mod.segments = 2
        mod.limit_method = 'ANGLE'
    return obj


def poly_prism(name, points_xy, z0, z1, material, collection):
    pts = [(float(p[0]),float(p[1])) for p in points_xy]
    if len(pts)>2 and pts[0] == pts[-1]: pts.pop()
    area = sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))
    if area<0: pts.reverse()
    n=len(pts)
    verts=[(x,y,z0) for x,y in pts]+[(x,y,z1) for x,y in pts]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh_object(name,verts,faces,material,collection)


def segment(name, a, b, z0, z1, thickness, material, collection):
    a,b=Vector(a[:2]),Vector(b[:2]); d=b-a
    obj=box(name,((a.x+b.x)/2,(a.y+b.y)/2,(z0+z1)/2),(d.length,thickness,z1-z0),material,collection,bevel=0.007)
    obj.rotation_euler.z=math.atan2(d.y,d.x)
    return obj


def cylinder(name,center,radius,depth,material,collection,vertices=16):
    n=int(vertices); verts=[]
    for z in (-depth/2,depth/2):
        verts.extend([(radius*math.cos(i*2*math.pi/n),radius*math.sin(i*2*math.pi/n),z) for i in range(n)])
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    obj=mesh_object(name,verts,faces,material,collection)
    obj.location=center
    for p in obj.data.polygons:
        if len(p.vertices)==4: p.use_smooth=True
    return obj


def beam(name,a,b,radius,material,collection):
    a,b=Vector(a),Vector(b); d=b-a
    obj=cylinder(name,(a+b)/2,radius,max(d.length,.001),material,collection,12)
    obj.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    return obj


def stairs(name,start,end,width,rise,material,collection):
    """start/end xyz, rise is total height; endpoint XY determines run."""
    a=Vector(start); b=Vector(end); run=Vector((b.x-a.x,b.y-a.y,0))
    n=max(1,math.ceil(abs(rise)/.175)); step=run.length/n
    result=[]
    for i in range(n):
        p=a+run*((i+.5)/n); top=a.z+rise*(i+1)/n
        base=min(a.z,top)-.08
        o=box(f'{name}_{i:02}',(p.x,p.y,(base+top)/2),(step+.008,width,top-base),material,collection,.009)
        o.rotation_euler.z=math.atan2(run.y,run.x); result.append(o)
    return result


def window(name,a,b,bottom,top,ctx,collection,divisions=4,open_panel=False):
    a=Vector((a[0],a[1])); b=Vector((b[0],b[1])); d=b-a
    n=max(1,int(divisions)); out=[]; bar=.038; depth=.06
    for suffix,z in [('sill',bottom),('head',top)]:
        out.append(segment(name+'_'+suffix,a,b,z-bar/2,z+bar/2,depth,ctx.mats['red'],collection))
    for i in range(n+1):
        p=a+d*(i/n)
        out.append(box(f'{name}_mullion_{i}',(p.x,p.y,(bottom+top)/2),(bar,bar,top-bottom),ctx.mats['red'],collection,.004))
    trans=bottom+(top-bottom)*.72
    for i in range(n):
        if open_panel and i==n//2: continue
        out.append(segment(f'{name}_transom_{i}',a+d*(i/n),a+d*((i+1)/n),trans-.013,trans+.013,depth*.8,ctx.mats['red'],collection))
    for i in range(n):
        if open_panel and i==n//2: continue
        p=a+d*((i+.5)/n)
        pane=box(f'{name}_glass_{i}',(p.x,p.y,(top+bottom)/2),(max(.04,d.length/n-bar),.008,top-bottom-bar),ctx.mats['glass'],collection,0)
        pane.rotation_euler.z=math.atan2(d.y,d.x)
        pane['surface_type']='glazing'; out.append(pane)
    return out


def tag(objects,room_id=None,reference=None,evidence='C',role=None):
    if isinstance(objects,bpy.types.Object): objects=[objects]
    for o in objects:
        if room_id: o['room_id']=room_id
        if reference: o['reference']=reference
        if role: o['role']=role
        o['evidence']=evidence
    return objects
