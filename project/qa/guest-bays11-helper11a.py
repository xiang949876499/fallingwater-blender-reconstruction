"""Local Guest01 2010 theater bay reconstruction, independent candidate only.

Printed spans are A. Plan face identification is B/C, manually registered XY,
heights, return material and window/door subdivision are C. The middle receiving
face is the short unhatched AB return, never a fabricated long masonry face.
No tour, cameras, furniture, global material or production input is modified.
"""
import math
import bpy
from mathutils import Vector
from types import SimpleNamespace
from fwlib import segment, poly_prism, window, tag

PREFIX='GUEST_BAYS11_'
COURSES='GUEST_LAYERED_SANDSTONE_COURSES'
FLOOR=8.4
TOP=10.56

def p(q):
    return Vector((3.4+(q[0]-325)*.05256,37.1+(422-q[1])*.05272))

def source(q):
    return [325+(q[0]-3.4)/.05256,422-(q[1]-37.1)/.05272]

def xy3(q,z=0): return Vector((q[0],q[1],z))

def design():
    a=p((191.7,126.3));d=(p((215.9,167.6))-a).normalized()
    t=Vector((-d.y,d.x));pn=a+d*2.486025;ps=pn+d*.4572
    nw=pn-t*1.3208
    ne1=p((222.52,218.6));nw1=ne1-t*2.025
    ab=[p(q) for q in [(223.32,219.98),(226.5,218.64),(228.7,221.82),(225.34,223.48)]]
    # Make the unhatched AD edge meet the actual stone end cap without moving
    # AB's source receiving edge. A 3 mm construction overlap at D closes the
    # traced line thickness; it is not a new measuring face.
    ab[3]-=t*.003
    dm=(p((223.4,220.5))-p((202.4,185))).normalized()
    ma=p((202.4,185));start=ma+dm*((ps-ma).dot(d)/dm.dot(d))
    u=ab[1]-ab[0];n=Vector((-u.y,u.x)).normalized()
    end=ma+dm*((ab[0]-ma).dot(n)/dm.dot(n))
    return dict(a=a,d=d,t=t,pn=pn,ps=ps,p2=[nw,nw+t*2.045,nw+t*2.045+d*.4572,nw+d*.4572],
                p1=[nw1,ne1,ne1+d*.4572,nw1+d*.4572],ab=ab,mstart=start,mend=end,md=dm)

def _map_core(obj,newa,newb,newthick):
    mw=obj.matrix_world.copy();vs=[mw@v.co for v in obj.data.vertices]
    ot=Vector((mw[0][0],mw[1][0])).normalized();on=Vector((-ot.y,ot.x))
    center=Vector((mw.translation.x,mw.translation.y))
    lo=min(Vector(v[:2]).dot(ot) for v in vs);hi=max(Vector(v[:2]).dot(ot) for v in vs)
    oldthick=max(Vector(v[:2]).dot(on) for v in vs)-min(Vector(v[:2]).dot(on) for v in vs)
    olda=center+ot*(lo-center.dot(ot));oldb=center+ot*(hi-center.dot(ot))
    nt=(newb-newa).normalized();nn=Vector((-nt.y,nt.x))
    def transform(v,relief=False):
        q=Vector(v[:2]);along=(q-olda).dot(ot)/(oldb-olda).length;off=(q-olda).dot(on)
        if relief: off+=math.copysign((newthick-oldthick)/2,off)
        else:off*=newthick/oldthick
        r=newa+(newb-newa)*along+nn*off
        return Vector((r.x,r.y,v.z))
    for vert,v in zip(obj.data.vertices,vs):vert.co=mw.inverted()@transform(v)
    obj.data.update()
    return dict(name=obj.name,olda=olda,oldb=oldb,ot=ot,on=on,oldthick=oldthick,transform=transform)

def apply(scene=None):
    scene=scene or bpy.context.scene
    if any(o.name.startswith(PREFIX) for o in scene.objects):raise RuntimeError('Guest bays11 already applied')
    g=design();a,d,t=g['a'],g['d'],g['t']
    col=bpy.data.objects['GUEST_L1_THEATER_FLOOR'].users_collection[0]
    mats={k:bpy.data.materials[v] for k,v in {'stone':'FW_stone','plaster':'FW_ceiling','red':'FW_red','glass':'FW_glass','wood':'FW_wood'}.items()}
    changed=[];maps=[]
    # Align the whole continuous northern wall to its actually identified inner
    # face. Its far NE return is lengthened only up to the existing first window.
    oldhit=Vector((-3.5398747921,52.5756874084));shift=a-oldhit
    back=[o for o in scene.objects if o.name.startswith('GUEST_L1_THEATER_DIAGONAL_BACK_')]
    for o in back:o.location+=xy3(shift);changed.append(o.name)
    ne=bpy.data.objects['GUEST_L1_THEATER_NORTHEAST_pier_0']
    na=p((275,77));nb=na+(p((325,163))-na)*.1
    maps.append(_map_core(ne,na+shift,nb,.39));changed.append(ne.name)
    for idx,key in [(2,'p2'),(1,'p1')]:
        ob=bpy.data.objects[f'GUEST_L1_CARPORT_RETAINED_PIER_{idx}_pier_end']
        q=g[key];maps.append(_map_core(ob,(q[0]+q[3])/2,(q[1]+q[2])/2,.4572));changed.append(ob.name)
    # Preserve every disjoint non-target stone block byte-for-byte.
    stones=bpy.data.objects[COURSES];me=stones.data;assert len(me.vertices)%8==0
    ba=p((190,126));bb=p((275,77));bt=(bb-ba).normalized();bn=Vector((-bt.y,bt.x))
    selected={m['name']:[] for m in maps};selected['DIAGONAL_BACK']=[]
    for j in range(0,len(me.vertices),8):
        vv=[me.vertices[j+k].co.copy() for k in range(8)]
        if min(v.z for v in vv)<FLOOR-.001 or max(v.z for v in vv)>TOP+.001:continue
        edge=Vector((vv[1]-vv[0])[:2]).normalized();q=sum((Vector(v[:2]) for v in vv),Vector((0,0)))/8
        if abs(edge.dot(bt))>.999999 and -.01<(q-ba).dot(bt)<(bb-ba).length+.01 and .175<abs((q-ba).dot(bn))<.24:
            for k in range(8):me.vertices[j+k].co+=xy3(shift)
            selected['DIAGONAL_BACK'].append(j//8);continue
        for m in maps:
            along=(q-m['olda']).dot(m['ot']);off=abs((q-m['olda']).dot(m['on']))
            if abs(edge.dot(m['ot']))>.999999 and -.01<along<(m['oldb']-m['olda']).length+.01 and m['oldthick']/2-.007<off<m['oldthick']/2+.05:
                for k,v in enumerate(vv):me.vertices[j+k].co=m['transform'](v,True)
                selected[m['name']].append(j//8);break
    assert all(selected.values()),{k:len(v) for k,v in selected.items()}
    me.update();changed.append(COURSES)
    keep={'pier_0','lintel_0','jamb_0_a','jamb_0_b','door_head_0','open_leaf_0','handle_0','pier_1'}
    remove=[o for o in scene.objects if o.name.startswith('GUEST_L1_THEATER_WEST_') and o.name.removeprefix('GUEST_L1_THEATER_WEST_') not in keep]
    removed=[o.name for o in remove]
    for o in remove:bpy.data.objects.remove(o,do_unlink=True)
    created=[]
    def seg(name,aa,bb,z0,z1,thick,mat):
        ob=segment(PREFIX+name,aa,bb,z0,z1,thick,mats[mat],col);created.append(ob);return ob
    # North whole bay contains fixed glazing, a real open door, and a short
    # jamb. Split heights/material are bounded C, distinct from printed span A.
    n0=a+t*.13
    # Original back face is not exactly parallel to pier2; intersect its actual
    # continued plane, rather than leaving a hairline wedge at the new glazing.
    oldbn=bn
    n0+=d*((a-n0).dot(oldbn)/d.dot(oldbn))
    n1=g['pn']+t*.13
    nd=(n1-n0).normalized();length=(n1-n0).length
    qwin=n0+nd*1.22;qdoor=n0+nd*1.295;qend=n0+nd*(length-.29)
    seg('NORTH_window_base',n0,qwin,FLOOR,FLOOR+.22,.16,'plaster')
    seg('NORTH_header',n0,n1,FLOOR+2.10,TOP,.16,'plaster')
    seg('NORTH_divider',qwin,qdoor,FLOOR,TOP,.18,'plaster')
    seg('NORTH_end_return',qend,n1+nd*.003,FLOOR,TOP,.22,'plaster')
    created+=window(PREFIX+'NORTH_window',n0,qwin,FLOOR+.22,FLOOR+2.10,SimpleNamespace(mats=mats),col,2)
    for k,q in [('a',qdoor),('b',qend)]:seg('NORTH_door_jamb_'+k,q-nd*.0225,q+nd*.0225,FLOOR,FLOOR+2.1,.06,'red')
    seg('NORTH_door_head',qdoor,qend,FLOOR+2.075,FLOOR+2.12,.06,'red')
    leafend=qdoor+t*((qend-qdoor).length-.045)
    seg('NORTH_open_leaf',qdoor,leafend,FLOOR+.04,FLOOR+2.055,.033,'wood')
    # Middle AB receiving face is traced, not moved to meet the printed target.
    ret=poly_prism(PREFIX+'MIDDLE_short_return_AB',g['ab'],FLOOR,TOP,mats['plaster'],col);created.append(ret)
    mend=(g['ab'][0]+g['ab'][1])/2
    mstart=mend-g['md']*((mend-g['ps']).dot(d)/g['md'].dot(d))
    seg('MIDDLE_window_base',mstart,mend,FLOOR,FLOOR+.22,.16,'plaster')
    seg('MIDDLE_header',mstart,mend,FLOOR+2.10,TOP,.16,'plaster')
    created+=window(PREFIX+'MIDDLE_window',mstart,mend,FLOOR+.22,FLOOR+2.10,SimpleNamespace(mats=mats),col,3)
    for ob in created:
        tag(ob,room_id='GUEST_L1_THEATER',reference='HABS PA-5346-A guest01 2010; guest-bays11 source annotations',evidence='B/C',role='architecture')
        ob['vertical_material_evidence']='C: existing floor 8.4/top 10.56; return FW_ceiling and subdivisions are construction interpretations'
    bpy.context.view_layer.update()
    return {'changed':changed,'removed':removed,'created':[o.name for o in created],
            'course_block_ids':selected,'north_wall_shift_m':list(shift),
            'floor_geometry_changed':False,'source_plan':{k:[source(q) for q in g[k]] for k in ('p1','p2','ab')},
            'north_source_face':source(a),'north_nominal_m':2.486025,'middle_nominal_m':2.162175,
            'middle_traced_prediction_m':(g['mend']-g['mstart']).length,
            'middle_qualification':'DIAGNOSTIC source short AB return B/C, material/vertical C; independent numeric qualification pending',
            'door_center':list((qdoor+qend)/2),'door_cross_axis':list(t),'north_glazing':[list(n0),list(n1)],'middle_glazing':[list(mstart),list(mend)]}
