"""Fallingwater guest/service wing, traced from HABS PA-5346-A sheets 1–4.

The data retains drawing coordinates separately from the site registration.  Unknown
fine details are reconstruction choices; the 2010 THEATER is deliberately enclosed.
"""
from pathlib import Path
import json
import math
import random
import bpy
from mathutils import Vector
from fwlib import box, poly_prism, segment, cylinder, beam, window, mesh_object, tag


def build(ctx):
    path = Path(ctx.root) / 'data' / 'guest_house.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    reg = dict(data['registration'])
    reg.update(ctx.config.get('guest_registration', {}))
    sx, sy = reg['meters_per_pixel']
    ox, oy = reg['origin_px']
    wx, wy, gz = reg['world_origin']
    def p(xy):
        return (wx + (xy[0]-ox)*sx, wy + (oy-xy[1])*sy)
    def z(level):
        return gz + data['levels'][level]['offset']
    col = ctx.collection('30_GUEST_SERVICE')
    mats = ctx.mats
    stone = mats['stone']; plaster = mats.get('plaster', mats.get('ceiling',mats['ochre']))
    floor = mats.get('flagstone', mats.get('stone_floor', mats.get('slate', stone)))
    concrete = mats['ochre']; red = mats['red']; wood = mats.get('wood', stone)
    cork = mats.get('cork',floor); roofmat = mats.get('roof', concrete)
    rng = random.Random(2187)
    stone_verts=[]; stone_faces=[]
    def quadstone(a,b,z0,z1,thickness):
        """Thin, independent horizontal stone courses, batched into a single mesh."""
        av,bv=Vector(a),Vector(b); d=bv-av; length=d.length
        if length<.10 or z1-z0<.06:return
        tangent=d.normalized(); normal=Vector((-tangent.y,tangent.x))
        zz=z0+.008
        while zz<z1-.035:
            hh=min(rng.uniform(.065,.155),z1-zz-.004)
            if hh<.02:break
            cursor=0
            while cursor<length-.035:
                width=min(rng.uniform(.24,.92),length-cursor-.008)
                if width<.02:break
                for side in [-1,1]:
                    depth=rng.uniform(.012,.042)
                    mid=av+tangent*(cursor+width/2)+normal*side*(thickness/2+depth/2-.005)
                    corners=[]
                    for zv in (zz,zz+hh):
                        for u,v in [(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]:
                            q=mid+tangent*u+normal*v;corners.append((q.x,q.y,zv))
                    idx=len(stone_verts);stone_verts.extend(corners)
                    stone_faces.extend(tuple(idx+j for j in f) for f in [(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)])
                cursor+=width+.009
            zz+=hh+.009
    def piece(name,a,b,z0,z1,thick,mat):
        if z1-z0<.006 or math.dist(a,b)<.012:return
        obj=segment(name,a,b,z0,z1,thick,mat,col)
        tag(obj,reference='HABS PA-5346-A, traced plan/elevations',evidence='C',role='architecture')
        if mat==stone:quadstone(a,b,z0,z1,thick)
    def wall(rec):
        a,b=p(rec['a']),p(rec['b']);av,bv=Vector(a),Vector(b);d=bv-av
        z0=z(rec['level']);h=rec.get('height',data['levels'][rec['level']]['height'])
        thick=rec.get('thickness',.29);mat=plaster if rec.get('material')=='plaster' else mats.get(rec.get('material','stone'),stone)
        def wall_piece(suffix,aa,bb,low,high):
            piece(rec['id']+suffix,aa,bb,low,high,thick,mat)
            finish=rec.get('interior_finish')
            if not finish or high-low<.006:return
            # One-sided, finite cork lining preserves the plaster/stone substrate
            # and leaves the adjacent corridor face unchanged. Clip shared walls.
            lo,hi=finish.get('span',[0,1])
            start=max(lo,(Vector(aa)-av).dot(d)/d.length_squared)
            end=min(hi,(Vector(bb)-av).dot(d)/d.length_squared)
            if end-start<.001:return
            normal=Vector((-d.y,d.x)).normalized()*finish.get('side',1)
            lining_thickness=finish.get('thickness',.008)
            offset=normal*(thick/2+lining_thickness/2+.001)
            lining=segment(rec['id']+suffix+'_cork_lining',av+d*start+offset,av+d*end+offset,low,high,lining_thickness,mats[finish['material']],col)
            lining['surface_type']='cork_wall_lining'
            tag(lining,room_id=finish['room_id'],reference='Fallingwater preservation history; research/interiors.md S01/S04',evidence='B/C',role='wall_finish')
        intervals=[]
        for op in rec.get('openings',[]):
            t0,t1=op['span'];bot=op.get('sill',0);top=op.get('head',2.12)
            intervals.append((t0,t1,bot,top,op))
        cur=0
        for i,(start,end,bot,top,op) in enumerate(sorted(intervals)):
            wall_piece(f'_pier_{i}',av+d*cur,av+d*start,z0,z0+h)
            aa,bb=av+d*start,av+d*end
            wall_piece(f'_sill_{i}',aa,bb,z0,z0+bot)
            wall_piece(f'_lintel_{i}',aa,bb,z0+top,z0+h)
            if op['type']=='window':
                window(rec['id']+f'_steel_window_{i}',aa,bb,z0+bot,z0+top,ctx,col,op.get('divisions',3))
            elif op['type']=='door':
                # Empty navigable opening, with real jambs and an open leaf at one side.
                for suffix,q in [('a',aa),('b',bb)]:
                    box(rec['id']+f'_jamb_{i}_{suffix}',(q.x,q.y,z0+top/2),(.045,.045,top),red,col,.004)
                segment(rec['id']+f'_door_head_{i}',aa,bb,z0+top-.025,z0+top+.02,.055,red,col)
                if op.get('leaf',True):
                    v=(bb-aa).normalized();n=Vector((-v.y,v.x))*op.get('swing',1)
                    leafend=aa+n*(bb-aa).length*.93
                    segment(rec['id']+f'_open_leaf_{i}',aa,leafend,z0+.04,z0+top-.045,.033,wood,col)
                    handle=aa+n*(bb-aa).length*.82+v*.032
                    box(rec['id']+f'_handle_{i}',(handle.x,handle.y,z0+1.00),(.10,.035,.03),red,col,.005)
            cur=end
        wall_piece('_pier_end',av+d*cur,bv,z0,z0+h)
    def slab(name,polygon,level,dz=0,thickness=.24,mat=None):
        return poly_prism(name,[p(q) for q in polygon],z(level)+dz-thickness,z(level)+dz,mat or floor,col)
    for item in data['slabs']:
        slab(item['id'],item['polygon'],item['level'],item.get('offset',0),item.get('thickness',.24),mats.get(item.get('material','flagstone'),floor))
    for room in data['rooms']:
        if room['kind']=='bath':
            slab(room['id']+'_cork_finish',room['polygon'],room['level'],.009,.011,cork)
    for rec in data['walls']:wall(rec)
    import guest_architectural_detail
    guest_architectural_detail.build(ctx,data,p,gz,col)
    for roof in data['roofs']:
        rz=z(roof['level'])+roof['height']
        polygon=[p(q) for q in roof['polygon']]
        poly_prism(roof['id'],polygon,rz,rz+.19,concrete,col)
        poly_prism(roof['id']+'_weathering',polygon,rz+.19,rz+.235,roofmat,col)
        if roof.get('parapet',False):
            for i in range(len(polygon)):
                piece(roof['id']+f'_parapet_{i}',polygon[i],polygon[(i+1)%len(polygon)],rz+.19,z(roof['level'])+roof.get('parapet_top',roof['height']+.63),.13,concrete)
    # Exact stair voids are omitted from the slab polygons; treads bridge levels.
    def stair(name,a,b,bottom,top,width,count=None):
        a,b=Vector(p(a)),Vector(p(b));d=b-a;rise=top-bottom
        n=count or max(1,math.ceil(abs(rise)/.173));tread=d.length/n
        for i in range(n):
            q=a+d*((i+.5)/n);zt=bottom+rise*(i+1)/n
            ob=box(name+f'_tread_{i:02}',(q.x,q.y,zt-.065),(tread+.012,width,.13),concrete,col,.009)
            ob.rotation_euler.z=math.atan2(d.y,d.x)
        v=d.normalized();normal=Vector((-v.y,v.x))
        for side in (-1,1):
            aa=a+normal*side*width*.47;bb=b+normal*side*width*.47
            beam(name+f'_handrail_{side}',(*aa,bottom+.9),(*bb,top+.9),.021,red,col)
            for t in (.1,.5,.9):
                q=aa+(bb-aa)*t; zz=bottom+rise*t
                cylinder(name+f'_baluster_{side}_{t}',(*q,zz+.45),.017,.9,red,col,10)
    for rec in data['stairs']:
        stair(rec['id'],rec['a'],rec['b'],z(rec['from']),z(rec['to']),rec['width'],rec.get('count'))
    # Pool: rounded concrete shell with a lowered basin, coping and finite water depth.
    pool=data['pool'];px,py=p(pool['center']);w,dep=pool['size_m'];radius=.55
    def rounded(w,d,r):
        pts=[]
        for cx,cy,start in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)]:
            for i in range(9):
                ang=math.radians(start+i*90/8);pts.append((px+cx+r*math.cos(ang),py+cy+r*math.sin(ang)))
        return pts
    coping_width=pool.get('coping_width_m',.145)
    pooltop=gz+.70485;waterz=pooltop-.14;basin=gz-.91;inner=rounded(w,dep,radius);outer=rounded(w+2*coping_width,dep+2*coping_width,radius+coping_width)
    poly_prism('GUEST_POOL_basin',outer,basin-.2,basin,concrete,col)
    for i in range(len(inner)):
        j=(i+1)%len(inner)
        poly_prism('GUEST_POOL_shell_%02d'%i,[inner[i],inner[j],outer[j],outer[i]],basin,pooltop-.07,concrete,col)
        poly_prism('GUEST_POOL_coping_%02d'%i,[inner[i],inner[j],outer[j],outer[i]],pooltop-.07,pooltop,floor,col)
    water=mats.get('water',mats['glass'])
    poolobj=poly_prism('GUEST_POOL_water',rounded(w-.03,dep-.03,radius-.02),waterz-.08,waterz,water,col)
    poolobj['surface_type']='pool_water';poolobj['evidence']='A plan footprint; C depth/water level'
    notch=pool.get('dry_west_notch')
    if notch:
        # Actual source stair / planter projection is dry. Cut the finite water
        # volume, rather than hiding its top behind slabs while water remains in
        # the stair body. Boolean operates only in this fresh build process.
        xx,yy=p((notch['x_max_px'],notch['y_max_px']))
        cut=box('QA_POOL_DRY_NOTCH_CUTTER',((px-w/2-1+xx)/2,(yy+py+dep/2+1)/2,waterz),
                (xx-(px-w/2-1),py+dep/2+1-yy,2),concrete,col)
        bpy.context.view_layer.objects.active=poolobj
        mod=poolobj.modifiers.new('Source_dry_stair_planter_notch','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
        bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
        a,b=Vector(p(notch['stair_from'])),Vector(p(notch['stair_to']));delta=b-a
        count=notch['count'];width=notch['stair_width_m'];normal=Vector((-delta.y,delta.x)).normalized()*width/2
        # Full-depth solids prevent see-through gaps between thin isolated treads.
        for i in range(count):
            aa=a+delta*i/count;bb=a+delta*(i+1)/count;zt=gz+(pooltop-gz)*(i+1)/count
            poly_prism('GUEST_POOL_coping_ascent_tread_%02d'%i,[aa-normal,bb-normal,bb+normal,aa+normal],basin,zt,concrete,col)
        poly_prism('GUEST_POOL_coping_ascent_landing',[p(q) for q in notch['landing_px']],basin,pooltop,floor,col)
    else:
        stair('GUEST_POOL_coping_ascent',(702,443),(723,443),gz,pooltop,1.0,4)
    planter=[p(q) for q in [[697,445],[733,445],[733,477],[697,477]]]
    poly_prism('GUEST_POOL_planter_base',planter,gz-.1,gz+.13,stone,col)
    for i in range(4):piece('GUEST_POOL_planter_side_%d'%i,planter[i],planter[(i+1)%4],gz+.1,gz+.58,.18,stone)
    # Partial pergola over the pool approach, narrow cantilevered concrete strips.
    for i in range(8):
        a,b=p((489+i*19,447)),p((489+i*19,474))
        segment('GUEST_pergola_%02d'%i,a,b,gz+2.17,gz+2.35,.27,concrete,col)
    # The curved link is registered in world coordinates independently of floor plans.
    connector=ctx.config.get('guest_connector',data['connector'])
    route=[Vector(q) for q in connector['points']]
    # Smooth the digitized centerline; paired radial edges share vertices, preventing
    # the triangular holes left by rotating a succession of unrelated rectangles.
    samples=[]
    for i in range(len(route)-1):
        a=route[max(0,i-1)];b=route[i];c=route[i+1];d=route[min(len(route)-1,i+2)]
        for k in range(5):
            t=k/5
            q=.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
            q.z=b.z+(c.z-b.z)*t;samples.append((q,i))
    samples.append((route[-1],len(route)-2))
    normals=[]
    for i,(q,group) in enumerate(samples):
        delta=samples[min(i+1,len(samples)-1)][0]-samples[max(0,i-1)][0]
        normals.append(Vector((-delta.y,delta.x)).normalized())
    width=connector.get('width',1.72)
    canopy_width=connector.get('canopy_width',width+.13)
    for i in range(len(samples)-1):
        a,group=samples[i];b,_=samples[i+1];na,nb=normals[i],normals[i+1]
        al=Vector((a.x,a.y))+na*width/2;ar=Vector((a.x,a.y))-na*width/2
        bl=Vector((b.x,b.y))+nb*width/2;br=Vector((b.x,b.y))-nb*width/2
        top=route[0].z+math.ceil((b.z-route[0].z)/.145)*.145
        top=min(top,route[-1].z)
        poly_prism('GUEST_CONNECTOR_step_%03d'%i,[al,ar,br,bl],top-.20,top,floor,col)
        canz=max(route[group].z,route[group+1].z)+2.42
        cal=Vector((a.x,a.y))+na*canopy_width/2;car=Vector((a.x,a.y))-na*canopy_width/2
        cbl=Vector((b.x,b.y))+nb*canopy_width/2;cbr=Vector((b.x,b.y))-nb*canopy_width/2
        poly_prism('GUEST_CONNECTOR_canopy_%03d'%i,[cal,car,cbr,cbl],canz,canz+.16,concrete,col)
        if i>0 and group!=samples[i-1][1]:
            previous=samples[i-1][1]
            prevz=max(route[previous].z,route[previous+1].z)+2.42
            segment('GUEST_CONNECTOR_roof_riser_%03d'%i,cal,car,min(prevz,canz),max(prevz,canz)+.16,.045,concrete,col)
        segment('GUEST_CONNECTOR_lowwall_%03d'%i,al,bl,min(a.z,b.z)-.08,max(a.z,b.z)+.76,.16,stone,col)
        if i%10==0:
            q=Vector((a.x,a.y))-na*width*.46
            cylinder('GUEST_CONNECTOR_support_%03d'%i,(*q,(a.z+canz)/2),.034,canz-a.z,red,col,12)
    if stone_verts:
        mesh_object('GUEST_LAYERED_SANDSTONE_COURSES',stone_verts,stone_faces,stone,col)
    rooms=[]
    for r in data['rooms']:
        rec=dict(r);rec['building']='GUEST';rec['z']=z(r['level']);rec['height']=r.get('height',data['levels'][r['level']]['height'])
        rec['polygon']=[list(p(q)) for q in r['polygon']]
        rec['center']=[*p(r['center']),rec['z']+r.get('eye_height',1.55)]
        rec['entry']=[*p(r['entry']),rec['z']+.04]
        rec['reference']='HABS PA-5346-A sheet '+str(r.get('sheet',1))
        rec['evidence']=r.get('evidence','A/C')
        rec['furniture']=[]
        for f in r.get('furniture',[]):
            ff=dict(f);ff['center']=[*p(f['center']),rec['z']+f.get('z_offset',0)];rec['furniture'].append(ff)
        rooms.append(rec)
    ctx.config['guest_actual_registration']=reg
    ctx.config['guest_pool_bounds']=[px-w/2,py-dep/2,px+w/2,py+dep/2,gz]
    return rooms
