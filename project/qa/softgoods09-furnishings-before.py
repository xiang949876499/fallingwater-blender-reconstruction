"""Room-specific Fallingwater furnishings in meters.

Furniture silhouettes follow the references enumerated in furnishing-evidence.json.
Unmeasured dimensions, unseen backs, small props and inferred service fittings are C.
The module owns only FW_FURN_* objects and 40_FURNITURE collections.
Explicit room['furniture'] entries use world centers and angle in DEGREES.
"""
import json
import math
import random
from pathlib import Path

import bpy
from mathutils import Vector

from fwlib import box, beam, cylinder, mesh_object


SOURCES = {
    'living': 'https://fallingwater.org/fallingwater-fireside/',
    'kitchen': 'https://fallingwater.org/grant-received-for-kitchen-preservation/',
    'kitchen_photo': 'HABS PA-5346-56 / pa1690.photos.134195p / 1985',
    'study': 'https://fallingwater.org/fallingwater-from-home/',
    'guest_lounge': 'HABS PA-5346-A-11 / pa2187.photos.134234p / 1985',
    'guest_bed': 'https://fallingwater.org/fw_acl_bedrooms_5/',
    'guest_bed_detail': 'HABS PA-5346-A-15 through A-20 / 1985 captions',
    'materials': 'https://fallingwater.org/learn/preservation-and-collections/materials/',
    'main_plan': 'HABS PA-5346 sheets 3–6 and 11 / 2010',
    'guest_plan': 'HABS PA-5346-A sheets 1–2 / 2010',
}

# Enclosed baths and service rooms; dark-room QA motivates visible practicals.
# Fixture identity, shape, location, color and power are explicit C substitutes.
PRACTICAL_FIXTURES = {
    'MAIN_B_BATH': 18., 'MAIN_B_BOILER': 32., 'MAIN_B_WINE': 22., 'MAIN_L1_COAT': 9.,
    'GUEST_B1_BATH': 18., 'GUEST_L2_BATH': 18., 'GUEST_L2_HALL': 22., 'GUEST_B1_LAUNDRY': 30.,
    'MAIN_L2_BATH_N': 12., 'MAIN_L2_BATH_G': 12., 'MAIN_L2_BATH_M': 12.,
    'MAIN_L3_BATH': 12., 'GUEST_L1_BATH': 12.,
    'GUEST_L1_BOILER': 24.,
}


def inside(point, polygon):
    x, y = point
    hit = False
    for i, a in enumerate(polygon):
        b = polygon[(i + 1) % len(polygon)]
        if (a[1] > y) != (b[1] > y):
            if x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]:
                hit = not hit
    return hit


def footprint(center, width, depth, angle):
    ca, sa = math.cos(angle), math.sin(angle)
    return [(center[0] + ca*x-sa*y, center[1]+sa*x+ca*y)
            for x, y in [(-width/2,-depth/2),(width/2,-depth/2),
                         (width/2,depth/2),(-width/2,depth/2)]]


def polygons_overlap(p,q,clearance=.035):
    for polygon in (p,q):
        for i,a in enumerate(polygon):
            b=polygon[(i+1)%len(polygon)];axis=(b[1]-a[1],a[0]-b[0]);length=math.hypot(*axis)
            pp=[x*axis[0]+y*axis[1] for x,y in p];qq=[x*axis[0]+y*axis[1] for x,y in q]
            if min(max(pp),max(qq))-max(min(pp),min(qq)) < -clearance*length: return False
    return True


def occupies_floor(kind):
    return not any(k in kind for k in ('art','lamp','vessel','kettle','bedrock','towel','mirror'))


class Asset:
    """A local XY furniture assembly, +Y is its back, Z=0 is walking surface."""
    def __init__(self, owner, kind, center, width, depth, angle=0,
                 reference='main_plan', evidence='C', placement='C'):
        self.owner, self.ctx = owner, owner.ctx
        self.kind, self.w, self.d = kind, width, depth
        self.ref = SOURCES.get(reference, reference)
        self.evidence = evidence
        self.objects = []
        self.name = f'FW_FURN_{owner.room["id"]}_{kind}_{len(owner.assets):02}'
        self.root = bpy.data.objects.new(self.name, None)
        owner.coll.objects.link(self.root)
        self.root.location = center
        self.root.rotation_euler.z = angle
        self.root.empty_display_size = .12
        self.stamp(self.root)
        self.root['placement_evidence'] = placement
        self.root['footprint_width'] = width
        self.root['footprint_depth'] = depth
        owner.assets.append(self)

    def stamp(self, obj):
        obj['room_id'] = self.owner.room['id']
        obj['component_type'] = 'furniture'
        obj['asset_type'] = self.kind
        obj['asset_id'] = self.name
        obj['reference'] = self.ref
        obj['evidence'] = self.evidence
        obj['dimensions_evidence'] = 'C: photograph-informed, not measured furniture survey'
        return obj

    def add(self, obj):
        obj.parent = self.root
        self.objects.append(self.stamp(obj))
        return obj

    def mat(self, key):
        return self.ctx.mats.get(key, self.ctx.mats['wood'])

    def box(self, label, center, size, mat='wood', bevel=.008, rz=0):
        obj = self.add(box(self.name+'_'+label, center, size, self.mat(mat), self.owner.coll, bevel))
        obj.rotation_euler.z = rz
        return obj

    def cylinder(self, label, center, radius, depth, mat='metal', n=24, rotation=None):
        obj = self.add(cylinder(self.name+'_'+label, center, radius, depth,
                                self.mat(mat), self.owner.coll, n))
        if rotation is not None:
            obj.rotation_euler = rotation
        return obj

    def beam(self, label, a, b, radius=.012, mat='metal'):
        return self.add(beam(self.name+'_'+label, a, b, radius, self.mat(mat), self.owner.coll))

    def lathe(self, label, profile, center=(0,0,0), scale=(1,1,1), mat='ceramic', n=32):
        """Rotational cross-section, explicit rim and inner profile when required."""
        vertices = [(center[0]+r*scale[0]*math.cos(i*math.tau/n),
                     center[1]+r*scale[1]*math.sin(i*math.tau/n),
                     center[2]+z*scale[2]) for r,z in profile for i in range(n)]
        faces=[]
        for j in range(len(profile)-1):
            for i in range(n):
                faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
        return self.add(mesh_object(self.name+'_'+label,vertices,faces,
                                    self.mat(mat),self.owner.coll,True))

    @staticmethod
    def bounded_tube_segments(points, radius):
        """Cubic circular fillets inside the authored polyline envelope.

        AUTO handles on a short return beside a long rail can bow by more than
        the entire return depth. Trim each corner locally instead; straight
        spans stay straight and every junction has a continuous tangent.
        """
        points=[Vector(p) for p in points];segments=[];current=points[0]
        def line(start,end):
            if (end-start).length>1.e-7:
                segments.append((start,start+(end-start)/3,start+(end-start)*2/3,end))
        for i in range(1,len(points)-1):
            previous,p,nextp=points[i-1:i+2]
            incoming=p-previous;outgoing=nextp-p
            li,lo=incoming.length,outgoing.length
            if min(li,lo)<1.e-6:continue
            u,v=incoming/li,outgoing/lo
            angle=math.acos(max(-1.,min(1.,u.dot(v))))
            if angle<1.e-4 or angle>math.pi-.01:
                line(current,p);current=p;continue
            trim=min(radius*3.,li*.33,lo*.33)
            start,end=p-u*trim,p+v*trim
            handle=trim*(4./3.)*math.tan(angle/4)/math.tan(angle/2)
            line(current,start)
            segments.append((start,start+u*handle,end-v*handle,end))
            current=end
        line(current,points[-1])
        return segments

    def tube(self, label, points, radius=.01, mat='metal'):
        # A single curve prevents visible angular joints in taps and bent handles.
        crv=bpy.data.curves.new(self.name+'_'+label,'CURVE')
        crv.dimensions='3D'; crv.resolution_u=12
        bounded=('BATH' in self.owner.room['id'] and
                 self.kind in ('washbasin','water_closet','towel_rail','bath_tub') and
                 label in ('basin_spout','inlet','rail','spout','shower_riser'))
        spl=crv.splines.new('BEZIER')
        if bounded:
            segments=self.bounded_tube_segments(points,radius)
            spl.bezier_points.add(len(segments))
            for p,co in zip(spl.bezier_points,[segments[0][0]]+[s[-1] for s in segments]):
                p.co=co;p.handle_left_type='FREE';p.handle_right_type='FREE'
                p.handle_left=co;p.handle_right=co
            for i,segment in enumerate(segments):
                spl.bezier_points[i].handle_right=segment[1]
                spl.bezier_points[i+1].handle_left=segment[2]
        else:
            spl.bezier_points.add(len(points)-1)
            for p,co in zip(spl.bezier_points,points):
                p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
        crv.bevel_depth=radius; crv.bevel_resolution=2
        crv.materials.append(self.mat(mat))
        obj=bpy.data.objects.new(self.name+'_'+label,crv)
        self.owner.coll.objects.link(obj)
        obj=self.add(obj)
        if bounded:
            obj['tube_shape_revision']='07 bounded tangent fillets; AUTO short/long-span overshoot removed'
            obj['authored_polyline_points']=json.dumps(points)
        return obj


class Room:
    def __init__(self,ctx,room):
        self.ctx,self.room=ctx,room
        self.coll=ctx.collection('40_FURNITURE_'+room['id'])
        self.polygon=room['polygon']
        xs=[p[0] for p in self.polygon]; ys=[p[1] for p in self.polygon]
        self.x0,self.x1,self.y0,self.y1=min(xs),max(xs),min(ys),max(ys)
        self.w,self.d=self.x1-self.x0,self.y1-self.y0
        self.z=room.get('z',room['center'][2])
        self.assets=[]; self.warnings=[]
        self.explicit=[] if room.get('furniture_complete',False) else list(room.get('furniture',[]))

    def point(self,u,v):
        return (self.x0+u*self.w,self.y0+v*self.d,self.z)

    def asset(self,kind,u=.5,v=.5,width=1,depth=.5,angle=0,
              reference='main_plan',evidence='C',center=None,fit=True,placement='C'):
        c=tuple(center) if center is not None else self.point(u,v)
        if len(c)==2: c=(*c,self.z)
        semantic = ('bed' if kind.endswith('_bed') or kind=='single_bed' else
                    'bench' if 'bench' in kind or 'settee' in kind else
                    'table' if 'table' in kind else
                    'cabinet' if 'drawer' in kind or 'casework' in kind else None)
        for p in self.explicit:
            typ='bench' if p['type']=='sofa' else p['type']
            if typ==semantic and not p.get('_consumed'):
                c=tuple(p['center']); width=p.get('width',width); depth=p.get('depth',depth)
                angle=p.get('angle',angle); placement=p.get('placement_evidence','C: architecture-provided placement')
                p['_consumed']=True
                break
        ang=math.radians(angle)
        requested=c
        if fit:
            # Preserve type/size; search only translation. Exact provided locations remain fixed.
            obstacles=[]
            if c[2]<self.z+.2 and occupies_floor(kind):
                for old in self.assets:
                    if old.root.location.z<self.z+.2 and occupies_floor(old.kind):
                        obstacles.append(footprint(old.root.location,old.w,old.d,old.root.rotation_euler.z))
                for p in self.explicit:
                    if not p.get('_consumed') and p.get('center',[0,0,self.z])[2]<self.z+.2:
                        obstacles.append(footprint(p['center'],p.get('width',1),p.get('depth',.5),math.radians(p.get('angle',0))))
            def valid(p):
                fp=footprint(p,width+.08,depth+.08,ang)
                return all(inside(k,self.polygon) for k in fp) and not any(polygons_overlap(fp,obs) for obs in obstacles)
            if not valid(c):
                candidates=[]
                for ix in range(1,31):
                    for iy in range(1,31):
                        p=self.point(ix/31,iy/31)
                        p=(p[0],p[1],c[2])
                        if valid(p): candidates.append(p)
                if candidates:
                    c=min(candidates,key=lambda p:(p[0]-c[0])**2+(p[1]-c[1])**2)
                else:
                    self.warnings.append(f'{kind}: no non-overlapping full footprint fits polygon; manual inspection required')
        a=Asset(self,kind,c,width,depth,ang,reference,evidence,placement)
        if math.dist(c,requested)>.15:
            a.root['placement_adjustment_m']=math.dist(c,requested)
            a.root['placement_note']='C: translated to remain within room and avoid furniture overlap'
        return a


def handle(a,label,x,y,z,width=.13,mat='metal'):
    a.tube(label,[(x-width/2,y+.018,z),(x-width/2,y-.018,z),
                 (x+width/2,y-.018,z),(x+width/2,y+.018,z)],.009,mat)


def cabinet(a,height=.66,doors=3,steel=False,drawers=False,open_back=False):
    w,d=a.w,a.d
    mat='steel_cream' if steel else 'wood'
    a.box('recessed_plinth',(0,0,.07),(w-.14,d-.13,.14),'dark',.004)
    a.box('lower_shelf',(0,0,.16),(w,d,.04),mat)
    a.box('top_board',(0,0,height-.025),(w+.02,d+.02,.05),mat,.012)
    for x in (-w/2+.02,w/2-.02):
        a.box('side',(x,0,height/2+.05),(.04,d,height-.16),mat)
    if not open_back:
        a.box('back',(0,d/2-.012,height/2+.05),(w,.024,height-.15),mat,.002)
    for i in range(doors):
        x=-w/2+(i+.5)*w/doors
        a.box('division',(x-w/doors/2+.012,0,height/2+.06),(.023,d-.04,height-.18),mat,.003)
        if drawers:
            for j in range(3):
                z=.18+(height-.2)*(j+.5)/3
                a.box('drawer',(x,-d/2-.006,z),(w/doors-.015,.027,(height-.2)/3-.012),mat,.004)
                handle(a,'pull',x,-d/2-.029,z,width=min(.13,w/doors*.4),mat='metal' if steel else 'brass')
        else:
            a.box('door',(x,-d/2-.006,(height+.16)/2),(w/doors-.015,.027,height-.19),mat,.004)
            handle(a,'pull',x,-d/2-.029,height-.14,width=min(.13,w/doors*.4),mat='metal' if steel else 'brass')
    if steel:
        a.box('laminate_top',(0,0,height+.016),(w+.035,d+.035,.03),'counter',.006)
        for z in (height-.005,height+.014,height+.032):
            a.box('steel_edge',(0,-d/2-.024,z),(w+.036,.012,.008),'metal',.002)


def bench(a,fabric='cream_fabric',back=True):
    w,d=a.w,a.d
    a.box('cantilevered_low_base',(0,.025,.265),(w,d-.09,.18),'wood',.018)
    a.box('recessed_base',(0,.11,.135),(w-.22,d-.29,.27),'dark',.005)
    count=max(1,round(w/.8)); unit=w/count
    for i in range(count):
        x=-w/2+(i+.5)*unit
        a.box('seat_cushion',(x,-.015,.424),(unit-.012,d-.065,.145),fabric,.055)
        a.box('cushion_piping',(x,-.019,.431),(unit-.006,d-.055,.012),fabric,.02)
        if back:
            p=a.box('back_cushion',(x,d/2-.07,.69),(unit-.018,.17,.38),fabric,.05)
            p.rotation_euler.x=math.radians(8)
    if back:
        a.box('continuous_back_ledge',(0,d/2+.015,.91),(w+.06,.18,.045),'wood',.014)


def table(a,height=.69,pedestal=False,stone=False):
    mat='stone_floor' if stone else 'wood'
    a.box('thick_horizontal_top',(0,0,height-.028),(a.w,a.d,.056),mat,.018)
    if pedestal:
        a.box('cross_foot_x',(0,0,.04),(a.w*.6,.18,.08),'wood',.014)
        a.box('cross_foot_y',(0,0,.045),(.18,a.d*.7,.09),'wood',.014)
        a.box('central_pier',(0,0,height/2),(.22,.25,height-.08),'wood',.008)
    else:
        for x in (-a.w/2+.12,a.w/2-.12):
            for y in (-a.d/2+.10,a.d/2-.10):
                a.box('leg',(x,y,(height-.07)/2),(.054,.054,height-.07),'wood',.01)
        a.box('front_apron',(0,-a.d/2+.09,height-.095),(a.w-.22,.035,.105),'wood',.005)
        a.box('rear_apron',(0,a.d/2-.09,height-.095),(a.w-.22,.035,.105),'wood',.005)


def chair(a,farm=False,sling=False):
    w,d=a.w,a.d
    if sling:
        for x in (-w/2+.035,w/2-.035):
            a.beam('sling_diagonal',(x,-d/2,.05),(x,d/2,.96),.022,'wood')
            a.beam('cross_leg',(x,d/2-.03,.06),(x,-d/2+.10,.63),.023,'wood')
            a.beam('arm',(x,-d/2+.11,.63),(x,d/2,.74),.025,'wood')
        a.box('suspended_seat',(0,-.05,.42),(w-.10,d*.67,.025),'linen',.006)
        b=a.box('sling_canvas_back',(0,d*.21,.685),(w-.105,.024,.54),'linen',.006)
        b.rotation_euler.x=math.radians(-20)
        return
    a.box('seat',(0,-.025,.44),(w-.02,d-.04,.055),'wood' if farm else 'cream_fabric',.02)
    for x in (-w/2+.045,w/2-.045):
        for y in (-d/2+.05,d/2-.05):
            a.box('leg',(x,y,.22),(.04,.04,.44),'wood',.007)
        a.box('back_upright',(x,d/2-.04,.65),(.037,.04,.48),'wood',.006)
    if farm:
        for z in (.59,.71,.83): a.box('horizontal_back_slat',(0,d/2-.04,z),(w-.075,.022,.055),'wood',.01)
        for x in (-w/2+.045,w/2-.045): a.beam('leg_stretcher',(x,-d/2+.05,.18),(x,d/2-.05,.18),.012,'wood')
    else:
        a.box('upholstered_back',(0,d/2-.035,.68),(w-.075,.045,.33),'cream_fabric',.018)


def books(a,z=.8,count=12,x0=None,y=0,span=None):
    rng=random.Random(a.name+str(z)+str(count))
    x=x0 if x0 is not None else -a.w*.42
    limit=x+(span if span is not None else a.w*.82)
    for i in range(count):
        thick=rng.uniform(.023,.055); h=rng.uniform(.17,.28)
        if x+thick>limit: break
        color=('books','book_rust','book_sage','book_ochre','leather')[i%5]
        a.box('book_pages',(x+thick/2,y,z+h/2),(thick-.005,.16,h-.012),'paper',.001)
        for xx in (x+.0015,x+thick-.0015):
            a.box('book_cover',(xx,y,z+h/2),(.003,.172,h),color,.001)
        a.box('book_spine',(x+thick/2,y-.086,z+h/2),(thick,.012,h),color,.002)
        if i%3==0:
            for zz in (z+.026,z+h-.028): a.box('spine_rule',(x+thick/2,y-.092,zz),(thick*.65,.001,.003),'brass',0)
        x+=thick+.007


def bookshelf(a,height=1.58,levels=4,low=False):
    if low: height=.98; levels=3
    a.box('back_board',(0,a.d/2-.013,height/2),(a.w,.026,height),'wood',.005)
    for x in (-a.w/2+.025,a.w/2-.025): a.box('end_panel',(x,0,height/2),(.05,a.d,height),'wood',.008)
    for j in range(levels):
        z=.13+j*(height-.17)/(levels-1)
        a.box('horizontal_cantilever_shelf',(0,-.025,z),(a.w+.08,a.d+.06,.038),'wood',.009)
        if j<levels-1: books(a,z+.02,count=max(3,int(a.w*15)),y=-.045)


def bed(a,guest=False,service=False):
    w,d=a.w,a.d
    a.box('walnut_platform',(0,0,.22),(w+.10,d+.10,.15),'wood',.024)
    a.box('recessed_support',(0,0,.095),(w-.18,d-.2,.19),'dark',.006)
    a.box('mattress',(0,-.025,.39),(w,d,.23),'linen',.07)
    cloth='bluegrey' if guest else ('linen' if service else 'cream_fabric')
    a.box('woven_bedcover',(0,-.065,.513),(w+.045,d-.08,.025),cloth,.018)
    a.box('cover_foot_drop',(0,-d/2-.006,.38),(w+.035,.028,.27),cloth,.016)
    for side in (-1,1): a.box('cover_side_drop',(side*(w/2+.003),-.2,.4),(.025,d-.42,.23),cloth,.01)
    n=1 if w<1.25 else 2
    for i in range(n):
        p=a.box('pillow',(-w/2+(i+.5)*w/n,d/2-.28,.576),(w/n-.11,.46,.14),'linen',.065)
        p.rotation_euler.z=(i*.025)-.015
    a.box('low_horizontal_headboard',(0,d/2+.04,.62),(w+.16,.065,.91),'wood',.025)
    a.box('headboard_top_ledge',(0,d/2+.02,1.085),(w+.26,.20,.04),'wood',.012)
    # Fine stitched hem, not an implausible random blanket deformation.
    for y in (-d/2+.10,-d/2+.125): a.box('cover_hem',(0,y,.529),(w-.03,.004,.002),cloth,0)


def lamp(a,vertical=False):
    if vertical:
        a.box('vertical_walnut_light_standard',(0,0,.72),(.105,.12,1.44),'wood',.014)
        for z in (.30,.63,.96,1.29):
            a.box('projecting_light_shelf',(0,-.055,z),(.27,.30,.03),'wood',.008)
            a.box('diffuser',(0,-.11,z+.095),(.18,.13,.17),'lamp_diffuser',.004)
        a.box('base',(0,0,.025),(.31,.32,.05),'wood',.01)
    else:
        a.cylinder('base',(0,0,.025),.12,.05,'brass')
        a.cylinder('stem',(0,0,.29),.015,.52,'brass')
        a.lathe('shade',[(.19,.0),(.20,.015),(.105,.27),(.098,.27),(.19,.012)],
                center=(0,0,.43),mat='lamp_diffuser')
        a.cylinder('cap',(0,0,.72),.026,.025,'brass')


def pottery(a,z=0,variant=0):
    profiles=[[(.04,0),(.11,.025),(.13,.12),(.10,.22),(.046,.27),(.046,.30),(.037,.30),(.037,.27)],
              [(.08,0),(.16,.035),(.19,.10),(.18,.16),(.17,.16),(.17,.14),(.10,.06),(.04,.04)],
              [(.06,0),(.09,.07),(.085,.22),(.065,.30),(.07,.315),(.061,.315),(.057,.295)]]
    a.lathe('vessel',profiles[variant%3],(0,0,z),mat='ceramic' if variant%2==0 else 'earth_pottery')


def framed_placeholder(a,width=.68,height=.47,z=1.42):
    # Original procedural color fields intentionally do not copy copyrighted paintings.
    a.box('art_backing',(0,.025,z),(width,.018,height),'paper',.001)
    for x in (-width/2,width/2): a.box('frame_vertical',(x,0,z),(.022,.035,height+.04),'wood',.004)
    for zz in (z-height/2,z+height/2): a.box('frame_horizontal',(0,0,zz),(width+.02,.035,.022),'wood',.004)
    a.box('substitute_ochre_field',(-width*.20,.013,z),(width*.45,.002,height*.62),'book_ochre',0)
    a.box('substitute_sage_field',(width*.18,.011,z-.03),(width*.35,.002,height*.47),'book_sage',0)
    for obj in a.objects: obj['artwork_status']='C: original abstract placeholder; not identity or image of archival artwork'


def kettle(a):
    # The real red suspended kettle is spherical; built from an explicit revolved section.
    a.lathe('spherical_red_kettle',[(0,0),(.18,.05),(.31,.18),(.355,.34),(.33,.50),(.25,.64),(.08,.69),(.055,.69)],
            center=(0,0,.48),mat='red',n=48)
    a.lathe('lid',[(0,0),(.08,0),(.09,.015),(.04,.043),(0,.045)],center=(0,0,1.17),mat='red')
    a.cylinder('lid_knob',(0,0,1.235),.027,.05,'dark')
    a.tube('kettle_handle',[(-.22,0,1.06),(-.21,0,1.38),(.21,0,1.38),(.22,0,1.06)],.021,'dark')
    a.box('pivot_post',(-.55,.10,1.01),(.046,.046,1.92),'red',.006)
    a.box('rectangular_swing_arm',(-.26,.10,1.98),(.65,.045,.045),'red',.006)
    a.box('hanging_drop',(.035,.10,1.72),(.033,.033,.53),'red',.004)
    a.beam('hanger_link',(.035,.10,1.47),(0,0,1.37),.013,'dark')
    a.tube('spout',[(.26,-.03,.96),(.39,-.04,1.02),(.43,-.04,1.08)],.028,'red')


def hearth_rock(a):
    """Two non-concentric native-rock lobes, traced from HABS main04 stippling.

    Coordinates use the agreed 1024px main04 registration. Photo PA-5346-48
    establishes the broad irregular surfaces and broken ledges; main11 shows
    their low floor relationship. Elevations, fracture depth and grain are C.
    No fireplace walls, opening, kettle or other room objects are modified.
    """
    from mathutils.geometry import tessellate_polygon
    from mathutils import noise
    # The two independent outlines follow the rock, not surrounding flagstones.
    profiles={
      'north_native_lobe':[(335.5,326),(339,325.5),(342,326),(346,325.8),
        (350,327),(355,328),(360,328),(364,329),(367,331),(369,334),
        (371.5,335.8),(371.3,338.6),(372.5,341),(372,344),(372.2,346.2),
        (371.5,349.1),(368.5,350),(365,349.7),(362,348.2),(357,347.7),
        (354,347.9),(352.2,349.6),(349,350.2),(345,349.4),(341,349.4),
        (338,349),(336,349.9),(335.2,351.1),(334,349),(334.4,346),
        (334.3,338),(335.5,338)],
      'south_native_lobe':[(335.8,352),(338,351.6),(340.5,353.2),(343,353.3),
        (346,352.5),(350,352),(354,352),(356,351.7),(357.5,353.5),
        (359.4,355.9),(359.1,358.8),(360.1,361),(359.7,364.2),
        (360.5,367.2),(360,370.9),(357.5,371.6),(354,371.2),(351.5,372.2),
        (349.2,371.1),(346.8,372.5),(343.2,373.7),(340.4,375.2),
        (337.8,377.6),(334.5,379.1),(331,379.8),(331,365.5),
        (334.1,364.5),(334.5,361),(334,359.2),(335.1,356.5)]}
    material=bpy.data.materials.get('FW_native_hearth_sandstone_C')
    if material is None:
        material=a.mat('rock').copy();material.name='FW_native_hearth_sandstone_C'
        material['evidence']='C: photo-informed dry sandstone color and millimetric grain'
        nodes,links=material.node_tree.nodes,material.node_tree.links
        nodes.clear()
        out=nodes.new('ShaderNodeOutputMaterial');shader=nodes.new('ShaderNodeBsdfPrincipled')
        shader.inputs['Roughness'].default_value=.86
        coord=nodes.new('ShaderNodeTexCoord')
        coarse=nodes.new('ShaderNodeTexNoise');coarse.inputs['Scale'].default_value=2.8
        coarse.inputs['Detail'].default_value=3.2;coarse.inputs['Roughness'].default_value=.66
        links.new(coord.outputs['Object'],coarse.inputs['Vector'])
        ramp=nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].color=(.145,.143,.119,1)
        ramp.color_ramp.elements[0].position=.16
        ramp.color_ramp.elements[1].color=(.32,.304,.251,1)
        ramp.color_ramp.elements[1].position=.84
        links.new(coarse.outputs['Fac'],ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'],shader.inputs['Base Color'])
        grain=nodes.new('ShaderNodeTexNoise');grain.inputs['Scale'].default_value=92
        grain.inputs['Detail'].default_value=2.5
        links.new(coord.outputs['Object'],grain.inputs['Vector'])
        bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.40
        bump.inputs['Distance'].default_value=.0016
        links.new(grain.outputs['Fac'],bump.inputs['Height'])
        links.new(bump.outputs['Normal'],shader.inputs['Normal'])
        links.new(shader.outputs['BSDF'],out.inputs['Surface'])

    def top_height(x,y,north):
        # Broad sloping lobes with isotropic, low-amplitude coherent relief.
        # Periodic sin waves plus flat narrow triangles created false woodgrain
        # in candidate06; the mineral grain remains in the isotropic shader.
        dome=math.exp(-((x-1.10)**2/1.75+(y-(10.73 if north else 9.24))**2/.70))
        strata=.0024*noise.noise(Vector((x*3.7,y*3.7,16.3)))
        return (.135 if north else .105)+(.175 if north else .145)*dome+strata

    def native_block(label,outline,north):
        world=[((x-327)*.0524,(540-y)*.0531) for x,y in outline]
        if sum(world[i][0]*world[(i+1)%len(world)][1]-world[(i+1)%len(world)][0]*world[i][1] for i in range(len(world)))<0:
            world.reverse()
        vertices=[];faces=[];lookup={}
        def vertex(x,y,z):
            key=tuple(round(v,5) for v in (x,y,z))
            if key not in lookup:
                lookup[key]=len(vertices)
                vertices.append((x-a.root.location.x,y-a.root.location.y,z))
            return lookup[key]
        def face(triangle,depth=0):
            if depth<3:
                p,q,r=triangle;pq=(p+q)/2;qr=(q+r)/2;rp=(r+p)/2
                for t in ((p,pq,rp),(pq,q,qr),(rp,qr,r),(pq,qr,rp)):face(t,depth+1)
            else:
                faces.append(tuple(vertex(p.x,p.y,top_height(p.x,p.y,north)) for p in triangle))
        points=[Vector((x,y,0)) for x,y in world]
        for tri in tessellate_polygon([points]):
            face(tuple(points[i] for i in tri) if isinstance(tri[0],int) else tri)
        # A buried base and two uneven fracture horizons make a single sealed
        # monolith. Horizontal offsets vary per edge; they are not scaled rings.
        rings=[]
        boundary=[]
        for i,(x,y) in enumerate(world):
            qx,qy=world[(i+1)%len(world)]
            boundary.extend((x+(qx-x)*j/8,y+(qy-y)*j/8) for j in range(8))
        for layer in range(4):
            ring=[]
            for i,(x,y) in enumerate(boundary):
                h=top_height(x,y,north)
                if layer==0:xx,yy,z=x,y,-.024
                elif layer==3:xx,yy,z=x,y,h
                else:
                    # Spatially coherent seams do not depend on tessellation
                    # index, so extra vertices cannot form repeated saw cuts.
                    xx=x+.0024*noise.noise(Vector((x*2.6,y*2.6,11.7+layer*3.1)))
                    yy=y+.0024*noise.noise(Vector((x*2.6,y*2.6,23.9+layer*3.1)))
                    z=h*(.32 if layer==1 else .69)+.003*noise.noise(Vector((x*2.2,y*2.2,7.4)))
                ring.append(vertex(xx,yy,z))
            rings.append(ring)
        for low,high in zip(rings,rings[1:]):
            for i in range(len(boundary)):
                j=(i+1)%len(boundary);faces.append((low[i],low[j],high[j],high[i]))
        faces.append(tuple(reversed(rings[0])))
        obj=a.add(mesh_object(a.name+'_'+label,vertices,faces,material,a.owner.coll))
        # Vector subdivision uses float32 while authored edge coordinates are
        # float64. Weld only coincident micrometric seams, never fracture gaps.
        import bmesh
        bm=bmesh.new();bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00003)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(obj.data);bm.free();obj.data.update()
        # Smooth only the shallow top: keep its actual silhouette and preserve
        # a crisp fracture edge against the flat-shaded, near-vertical sides.
        for polygon in obj.data.polygons:
            polygon.use_smooth=polygon.normal.z>.65
        obj['reference']='HABS PA-5346 main04 stippled rock outline; main11 elevation; photo PA-5346-48'
        obj['evidence']='C: manually traced plan silhouette, photograph-informed height and fracture faces'
        obj['plan_trace_pixels']=json.dumps(outline)
        obj['buried_base_below_finish_m']=.024
        obj['texture_scale_evidence']='C: 1.6mm bump amplitude, noise frequency 92/m; not measured petrography'
        obj['surface_revision']='06b: smooth top normals, 2.4mm aperiodic spatial relief and coherent fracture edges'

    for label,outline in profiles.items():native_block(label,outline,label.startswith('north'))
    # Hidden root beneath the actual firebox/grate location, ending well short
    # of the two visible lobe edges. It replaces the old stacked circular base.
    root=a.box('buried_firebox_rock_root',(-.32,-.01,.094),(.83,1.29,.24),'rock',0)
    root['evidence']='C: obscured connecting rock, no claim of measured rear geometry'
    a.root['reference']='HABS PA-5346 main04/main11 and photograph PA-5346-48'
    a.root['evidence']='C: source-supported native boulder; manually reconstructed unsurveyed geometry'
    a.root['profile_revision']='06b keeps asymmetric 06 traced lobes; removes tessellation-induced directional striations'
    a.root['anchor_note']='Origin retained for unchanged charred-log positions; actual footprint is recorded per child mesh.'
    for x in (-.31,.03,.23):
        a.beam('unlit_charred_log',(x,-.35,.27),(x+.08,.43,.29),.037,'dark')


def sink(a,kitchen=False):
    if kitchen:
        w,d=a.w,a.d; h=.89
        # Counter is assembled around genuine basin openings.
        a.box('cabinet_plinth',(0,0,.06),(w-.1,d-.1,.12),'dark',.004)
        a.box('cabinet_back',(0,d/2-.02,.46),(w,.04,.78),'steel_cream')
        for x in (-w/2+.025,w/2-.025): a.box('cabinet_side',(x,0,.46),(.05,d,.80),'steel_cream')
        for i in range(2):
            x=(i-.5)*w/2
            a.box('under_sink_door',(x,-d/2,.48),(w/2-.014,.025,.72),'steel_cream',.004)
            handle(a,'door_handle',x,-d/2-.02,.75)
        a.box('counter_front',(0,-d*.40,h),(w,.20,.045),'metal',.009)
        a.box('counter_back',(0,d*.39,h),(w,.22,.045),'metal',.009)
        for x in (-w/2+.07,0,w/2-.07): a.box('counter_bridge',(x,0,h),(.14,d,.045),'metal',.009)
        for x in (-w*.25,w*.25):
            a.lathe('pressed_steel_basin',[(0,-.19),(.09,-.19),(.23,-.14),(.28,0),(.27,.014),(.252,-.014),(.21,-.125),(.08,-.17),(0,-.17)],
                    center=(x,0,h),scale=(min(1,w/1.35),.77,1),mat='metal')
            a.cylinder('drain',(x,0,h-.164),.032,.003,'dark')
        a.tube('wall_gooseneck',[(0,d/2-.02,h+.24),(0,.16,h+.28),(0,-.03,h+.18)],.017,'metal')
        for x in (-.105,.105):
            a.cylinder('tap_base',(x,d/2-.015,h+.18),.035,.025,'metal',rotation=(math.pi/2,0,0))
            a.beam('cross_tap',(x-.035,d/2-.045,h+.18),(x+.035,d/2-.045,h+.18),.006,'metal')
    else:
        h=.80
        a.lathe('pedestal',[(.13,0),(.15,.03),(.095,.15),(.075,.57),(.14,.68)],mat='ceramic')
        a.lathe('washbasin',[(0,-.13),(.12,-.13),(.22,-.08),(.31,0),(.305,.025),(.28,.018),(.23,-.035),(.16,-.10),(0,-.105)],
                center=(0,0,h),scale=(1,.74,1),mat='ceramic')
        a.box('tap_deck',(0,.18,h),(.43,.12,.065),'ceramic',.022)
        a.tube('basin_spout',[(0,.18,h+.03),(0,.16,h+.16),(0,.04,h+.16),(0,.01,h+.10)],.013,'metal')
        for x in (-.13,.13): a.cylinder('hot_cold_tap',(x,.18,h+.04),.028,.04,'metal')
        a.cylinder('drain',(0,0,h-.099),.029,.004,'metal')
        a.box('mirror_frame',(0,.31,1.37),(.56,.035,.65),'metal',.005)
        a.box('mirror',(0,.286,1.37),(.525,.012,.613),'mirror',.002)
        a.box('mirror_glass_shelf',(0,.23,1.035),(.57,.17,.012),'glass',.002)


def toilet(a):
    a.lathe('foot',[(.13,0),(.17,.025),(.17,.06),(.11,.13),(.12,.25),(.20,.31)],
            center=(0,-.045,0),scale=(.86,1.12,1),mat='ceramic')
    a.lathe('bowl_shell',[(.13,.18),(.23,.23),(.27,.34),(.27,.39),(.24,.405),(.205,.385),(.16,.27),(.045,.22)],
            center=(0,-.085,0),scale=(.86,1.22,1),mat='ceramic')
    a.lathe('open_seat',[(.215,.407),(.254,.407),(.261,.425),(.253,.441),(.208,.439),(.202,.424),(.215,.407)],
            center=(0,-.085,0),scale=(.86,1.21,1),mat='ceramic')
    a.box('cistern',(0,.225,.58),(.38,.20,.38),'ceramic',.038)
    a.box('cistern_lid',(0,.222,.782),(.41,.23,.032),'ceramic',.02)
    a.box('flush_lever',(-.16,.107,.715),(.073,.027,.014),'metal',.005)
    a.tube('inlet',[(.14,.27,.22),(.14,.27,.08),(.14,.35,.08)],.012,'metal')


def tub(a):
    w,d=a.w,a.d; h=.53
    # Rectangular enclosure with inner floor and sloped-looking four-sided white bowl.
    a.box('apron',(0,-d/2,h/2),(w,.055,h),'ceramic',.025)
    a.box('back_edge',(0,d/2-.065,h),(w,.13,.06),'ceramic',.025)
    a.box('front_edge',(0,-d/2+.055,h),(w,.15,.06),'ceramic',.025)
    for x in (-w/2+.065,w/2-.065): a.box('end',(x,0,h/2),(.13,d,h),'ceramic',.035)
    a.box('basin_bottom',(0,0,.15),(w-.22,d-.18,.07),'ceramic',.045)
    for y in (-d/2+.105,d/2-.105): a.box('inner_long_wall',(0,y,.33),(w-.22,.07,.36),'ceramic',.032)
    a.cylinder('drain',(-w/2+.23,0,.191),.028,.004,'metal')
    a.tube('spout',[(-w/2+.13,d/2-.015,.63),(-w/2+.22,d/2-.14,.63),(-w/2+.22,d/2-.17,.60)],.018,'metal')
    for x in (-w/2+.12,-w/2+.34): a.cylinder('tap',(x,d/2-.04,.59),.026,.06,'metal')
    a.tube('shower_riser',[(-w/2+.04,d/2,.58),(-w/2+.04,d/2,1.92),(-w/2+.04,d/2-.20,2.02)],.012,'metal')
    a.lathe('shower_rose',[(.012,0),(.065,-.045),(.067,-.06),(.01,-.06)],
            center=(-w/2+.04,d/2-.2,2.02),mat='metal')


def range_aga(a):
    a.box('cast_iron_base',(0,0,.045),(a.w-.04,a.d-.03,.09),'dark',.018)
    a.box('enamel_body',(0,0,.45),(a.w,a.d,.81),'steel_cream',.027)
    a.box('black_top',(0,0,.895),(a.w+.04,a.d+.03,.055),'dark',.015)
    for x in (-a.w*.25,a.w*.25):
        a.cylinder('hotplate_ring',(x,.035,.932),.20,.032,'metal',n=48)
        a.cylinder('polished_hotplate_lid',(x,.035,.953),.176,.025,'dark',n=48)
        a.tube('lid_handle',[(x-.07,.035,.973),(x-.07,.035,1.00),(x+.07,.035,1.00),(x+.07,.035,.973)],.01,'metal')
        for z in (.28,.65):
            a.box('rounded_oven_door',(x,-a.d/2-.018,z),(a.w*.43,.05,.31),'steel_cream',.02)
            a.box('door_inset',(x,-a.d/2-.046,z),(a.w*.34,.006,.22),'steel_shadow',.015)
            handle(a,'oven_handle',x,-a.d/2-.065,z+.05,.17)
    a.box('aga_nameplate',(0,-a.d/2-.049,.86),(.14,.014,.042),'dark',.009)
    a.tube('towel_rail',[(-a.w*.43,-a.d/2-.045,.82),(-a.w*.43,-a.d/2-.115,.82),
                         (a.w*.43,-a.d/2-.115,.82),(a.w*.43,-a.d/2-.045,.82)],.016,'metal')
    a.cylinder('flue',(a.w*.33,a.d*.33,1.45),.075,1.04,'metal')


def fridge(a):
    a.box('rounded_cabinet',(0,0,.94),(a.w,a.d,1.86),'steel_cream',.045)
    a.box('lower_grille',(0,-a.d/2-.015,.105),(a.w-.08,.025,.13),'dark',.003)
    for z in (.06,.08,.10,.12,.14): a.box('grille_slit',(0,-a.d/2-.032,z),(a.w-.12,.006,.009),'metal',.001)
    a.box('single_period_door',(0,-a.d/2-.024,1.015),(a.w-.04,.065,1.67),'steel_cream',.043)
    a.box('door_seal',(0,-a.d/2-.016,1.015),(a.w-.017,.013,1.70),'steel_shadow',.02)
    a.tube('vertical_latch_handle',[(a.w*.32,-a.d/2-.072,.93),(a.w*.32,-a.d/2-.112,1.03),
                                  (a.w*.32,-a.d/2-.11,1.25),(a.w*.32,-a.d/2-.070,1.29)],.014,'metal')
    a.box('brand_badge',(0,-a.d/2-.063,1.68),(.16,.008,.035),'metal',.004)


def dishwasher(a):
    cabinet(a,.87,1,steel=True)
    a.box('appliance_front',(0,-a.d/2-.03,.49),(a.w-.035,.04,.69),'steel_cream',.008)
    a.box('control_strip',(0,-a.d/2-.055,.79),(a.w-.055,.01,.095),'metal',.004)
    handle(a,'latch',0,-a.d/2-.081,.70,.22)
    for x in (-.15,-.09,.13): a.cylinder('control',(x,-a.d/2-.073,.79),.017,.01,'dark',rotation=(math.pi/2,0,0))


def guest_lounge_screen_center(ctx, floor_z):
    """HABS guest01 slat-line center; use the architecture's active registration."""
    data=json.loads((ctx.root/'data/guest_house.json').read_text(encoding='utf-8-sig'))
    config=getattr(ctx,'config',{})
    reg={**data['registration'],**config.get('guest_registration',{}),**config.get('guest_actual_registration',{})}
    ox,oy=reg['origin_px'];sx,sy=reg['meters_per_pixel'];wx,wy,_=reg['world_origin']
    return (wx+(440-ox)*sx,wy+(oy-412)*sy,floor_z)


def room_living(r,guest=False):
    if not guest and r.room['id'].startswith('MAIN') and r.x0 < .2 < r.x1 and r.y0 < 9 < r.y1:
        # Stable main-04 registration from architecture worker. Three distinct zones.
        b=r.asset('south_window_bench',center=(3.3,.64,r.z),width=5.4,depth=.78,angle=180,reference='living',evidence='B'); bench(b)
        b=r.asset('west_window_bench',center=(-.17,6.55,r.z),width=2.55,depth=.76,angle=90,reference='living',evidence='B'); bench(b,'rust_fabric')
        t=r.asset('low_hearth_table',center=(2.13,7.55,r.z),width=1.60,depth=.67,reference='living',evidence='B'); table(t,.40,True)
        dining=(1.38,12.58,r.z)
        t=r.asset('dining_table',center=dining,width=1.66,depth=.86,reference='main_plan',evidence='C'); table(t,.715)
        for i in range(2):
            for y,angle in ((dining[1]-.67,180),(dining[1]+.67,0)):
                c=r.asset('dining_chair',center=(dining[0]-.43+i*.86,y,r.z),width=.44,depth=.47,angle=angle); chair(c)
        b=r.asset('east_cantilever_books',center=(9.71,8.60,r.z),width=2.90,depth=.30,angle=270,reference='study',evidence='B'); bookshelf(b,1.51,4)
        t=r.asset('window_worktable',center=(8.84,3.35,r.z),width=1.85,depth=.68,angle=90,reference='main_plan',evidence='C'); table(t,.71)
        books(t,.74,6,x0=-.75,y=.13,span=.5)
        c=r.asset('work_chair',center=(7.93,3.35,r.z),width=.5,depth=.51,angle=90); chair(c)
        k=r.asset('suspended_red_kettle',center=(.82,10.42,r.z),width=.90,depth=.78,reference='living',evidence='B',fit=False); kettle(k)
        h=r.asset('emergent_hearth_bedrock',center=(.31,9.93,r.z),width=1.5,depth=2.2,reference='living',evidence='B',fit=False); hearth_rock(h)
    else:
        b=r.asset('window_cantilever_bench',.45,.16,min(3.5,r.w*.66),.77,180,reference='guest_lounge' if guest else 'living',evidence='A' if guest else 'B'); bench(b)
        b=r.asset('long_horizontal_bookcase',.53,.88,min(3.3,r.w*.68),.32,reference='guest_lounge' if guest else 'study',evidence='A' if guest else 'B'); bookshelf(b,1.30,4)
        t=r.asset('low_lounge_table',.46,.44,min(1.65,r.w*.35),.63,reference='guest_lounge' if guest else 'living',evidence='A' if guest else 'B'); table(t,.39,True)
        c=r.asset('walnut_armchair',.78,.59,.62,.64,angle=270,reference='guest_lounge',evidence='A'); chair(c)
        if guest:
            if r.room['id']=='GUEST_L1_LOUNGE':
                s=r.asset('walnut_vertical_screen',width=.50,depth=min(1.8,r.d*.38),
                          center=guest_lounge_screen_center(r.ctx,r.z),angle=0,
                          reference='guest_lounge',evidence='A',fit=False,
                          placement='C: HABS guest01 screen line near x440/y394–430, midpoint (440,412); approximately ±2px reading, active site registration')
                s.root['source_screen_line_px']=json.dumps([[440,394],[440,430]])
                s.root['placement_revision']='07 source-based translation from former northwest fireplace position; no automatic re-fit'
                s.root['dimensions_note']='Existing screen/cabinet dimensions retained as C; source line span is not asserted as a measured cabinet size'
                # The old inferred chair occupied the now source-confirmed
                # low-cabinet footprint. Preserve chair form/angle and place
                # it northwest of the fixed screen, clear of the old tour path.
                c.root.location.x=s.root.location.x-.98
                c.root.location.y=s.root.location.y+.91
                c.root['placement_evidence']='C: west/north translation for cabinet/seat and original tour clearance after source-based screen relocation; unchanged chair form and orientation'
                c.root['screen_clearance_revision']='07e: nominal 0.44m between chair seat edge and low cabinet; actual mesh/path validation in qa/guest-screen-placement07e-check.json'
            else:
                s=r.asset('walnut_vertical_screen',.13,.76,.50,min(1.8,r.d*.38),reference='guest_lounge',evidence='A')
            for yy in [(-s.d/2+.06)+i*.12 for i in range(int(s.d/.12))]: s.box('screen_slat',(0,yy,1.02),(.06,.035,2.04),'wood',.006)
            s.box('screen_low_drawercase',(0,0,.29),(.48,s.d,.48),'wood',.016)
    # One restrained ceramic arrangement and one small seated-scale textile accent.
    p=r.asset('ceramic_lounge_vessel',center=tuple(t.root.location),width=.32,depth=.32,reference='living',evidence='C',fit=False); pottery(p,.735 if not guest else .43,1)


def room_kitchen(r):
    if r.x0 < -1 < r.x1 and r.y0 < 14 < r.y1:
        c=r.asset('st_charles_north_drawers',center=(-1.6,16.08,r.z),width=2.0,depth=.59,reference='kitchen',evidence='B'); cabinet(c,.90,3,True,True)
        c=r.asset('west_double_sink',center=(-2.96,14.76,r.z),width=1.42,depth=.60,angle=90,reference='kitchen_photo',evidence='A'); sink(c,True)
        c=r.asset('kitchenaid_dishwasher',center=(-2.96,13.68,r.z),width=.60,depth=.60,angle=90,reference='kitchen',evidence='B'); dishwasher(c)
        c=r.asset('frigidaire_refrigerator',center=(-2.82,12.55,r.z),width=.71,depth=.71,angle=90,reference='kitchen',evidence='B'); fridge(c)
        c=r.asset('aga_range',center=(-.82,12.55,r.z),width=1.0,depth=.69,angle=270,reference='kitchen',evidence='B'); range_aga(c)
        c.root['placement_evidence']='C: inferred appliance location south of corrected HABS kitchen door at source x324/y270–287; integrated iteration04 clearance pending'
        t=r.asset('wright_kitchen_worktable',center=(-1.38,14.86,r.z),width=1.36,depth=.66,angle=90,reference='kitchen',evidence='B'); table(t,.75)
        # Four documented farm chairs are separated along the working table's long axis.
        for x,angle in ((-2.02,90),(-.73,270)):
            for y in (14.54,15.22):
                c=r.asset('farmhouse_chair',center=(x,y,r.z),width=.40,depth=.43,angle=angle,reference='kitchen',evidence='B'); chair(c,True)
        # Wall cabinets were photographed above the west sink. Their underside stays above taps.
        upper=r.asset('st_charles_wall_cabinets',center=(-3.0,14.95,r.z+1.47),width=1.73,depth=.34,angle=90,reference='kitchen_photo',evidence='A'); cabinet(upper,.59,3,True)
    else:
        c=r.asset('st_charles_drawers',.50,.89,min(2.6,r.w*.75),.59,reference='kitchen',evidence='B'); cabinet(c,.9,3,True,True)
        c=r.asset('double_sink',.15,.57,1.3,.6,90,reference='kitchen_photo',evidence='A'); sink(c,True)
        c=r.asset('aga_range',.84,.33,1,.69,270,reference='kitchen',evidence='B'); range_aga(c)
        c=r.asset('frigidaire',.15,.18,.71,.71,180,reference='kitchen',evidence='B'); fridge(c)
        t=r.asset('wright_worktable',.55,.54,1.35,.66,reference='kitchen',evidence='B'); table(t,.75)


def room_bedroom(r,guest=False,service=False,alcove=False):
    w=1.0 if service or alcove else min(1.55,r.w*.47)
    d=min(2.02,r.d*.64)
    b=r.asset('single_bed' if w<1.25 else 'walnut_bed',.37,.61,w,d,reference='guest_bed' if guest else 'main_plan',evidence='B' if guest else 'C'); bed(b,guest,service)
    # Casework and bed share a coherent headboard line, sized to leave the door side free.
    c=r.asset('cantilever_bedside_drawers',.77,.73,min(.75,r.w*.23),.42,reference='guest_bed_detail' if guest else 'materials',evidence='A' if guest else 'B'); cabinet(c,.54,2,drawers=True)
    bedside_center=tuple(c.root.location)
    if guest:
        l=r.asset('vertical_walnut_lamp',.87,.86,.32,.32,reference='guest_bed_detail',evidence='A'); lamp(l,True)
        p=r.asset('bedroom_art_placeholder',.41,.96,.75,.05,reference='guest_bed',evidence='C'); framed_placeholder(p,.75,.5,1.52)
        g=r.asset('woven_gliding_chair',.77,.23,.63,.71,angle=330,reference='guest_bed_detail',evidence='A'); chair(g,False,True)
        for xx in (-.27,.27): g.tube('glider_runner',[(xx,-.39,.05),(xx,-.2,.025),(xx,.27,.025),(xx,.42,.08)],.02,'wood')
    elif not alcove:
        north_door_clearance=.04 if r.room['id']=='GUEST_L2_BEDROOM_NORTH' else 0.
        t=r.asset('bedroom_desk',.72,.18+north_door_clearance,min(1.5,r.w*.43),.50,angle=180,reference='main_plan'); table(t,.72)
        c=r.asset('desk_chair',.72,.34+north_door_clearance,.43,.45,angle=180); chair(c,service)
        if not service:
            p=r.asset('bedside_reading_lamp',width=.25,depth=.25,center=(bedside_center[0],bedside_center[1],r.z+.54),reference='main_plan',fit=False); lamp(p)
    if service:
        if r.room['id']=='GUEST_L2_BEDROOM_NORTH':
            c=r.asset('service_wardrobe',center=(r.x0+.34,r.y0+r.d*.45,r.z),
                      width=min(.85,r.w*.23),depth=.48,angle=90,reference='guest_plan')
            c.root['placement_evidence']='C: moved to west wall to clear the surveyed east door into the shared bath; integrated iteration05 check required'
        else:c=r.asset('service_wardrobe',.85,.45,min(.85,r.w*.23),.48,angle=270,reference='guest_plan')
        cabinet(c,1.82,2)


def room_study(r,dressing=False):
    t=r.asset('cantilever_walnut_desk',.44,.84,min(2.60,r.w*.65),.68,reference='main_plan' if dressing else 'study',evidence='A' if dressing else 'B');
    table(t,.72)
    books(t,.751,8,x0=-t.w*.39,y=.13,span=.5)
    c=r.asset('sling_study_chair',.47,.60,.60,.67,reference='study',evidence='B'); chair(c,False,True)
    s=r.asset('continuous_horizontal_library',.15,.50,min(2.7,r.d*.61),.30,90,reference='study',evidence='B'); bookshelf(s,1.51,4)
    if dressing:
        c=r.asset('dressing_drawercase',.77,.29,min(1.65,r.w*.45),.52,angle=180,reference='main_plan',evidence='A'); cabinet(c,.75,3,drawers=True)
        p=r.asset('dressing_mirror',.76,.07,.67,.06,angle=180,reference='main_plan');
        p.box('mirror_walnut_frame',(0,0,1.32),(.71,.05,.75),'wood',.012)
        p.box('mirror_glass',(0,-.032,1.32),(.65,.01,.69),'mirror',.001)
    else:
        b=r.asset('study_low_bench',.55,.17,min(2.10,r.w*.63),.70,180,reference='study',evidence='B'); bench(b,'rust_fabric')


def room_bath(r):
    # Fixture placement is inferred unless explicit surveyed entries replace it.
    service=('SERVICE' in r.room['id'] or r.room.get('level') in ('B','B1','L2') and 'GUEST' in r.room['id'] or r.room.get('level')=='B')
    has_tub=min(r.w,r.d)>1.45 and r.w*r.d>4.4 and not service
    if has_tub:
        if r.d<1.8:
            c=r.asset('bath_tub',.85,.5,min(1.65,r.d-.17),.71,90,reference='main_plan')
        else:
            c=r.asset('bath_tub',.50,.19,min(1.65,r.w-.25),.71,180,reference='main_plan')
        tub(c)
    if r.room['id']=='MAIN_L2_BATH_G':
        c=r.asset('washbasin',.23,.80,.65,.62,reference='materials',evidence='C'); sink(c)
        c=r.asset('water_closet',center=(6.60,12.04,r.z),width=.51,depth=.75,angle=270,reference='main_plan'); toilet(c)
        c.root['placement_evidence']='C: rotated against northeast wall to clear actual east bathroom doorway; integrated iteration05 check required'
    elif r.room['id']=='GUEST_L1_BATH':
        # Surveyed L-shaped bath: tub in the south bay, basin west, WC in the north-east return.
        c=r.asset('washbasin',.23,.50,.62,.54,reference='guest_plan',evidence='C'); sink(c)
        c=r.asset('water_closet',.76,.80,.51,.75,reference='guest_plan'); toilet(c)
    elif r.w<1.80:
        c=r.asset('washbasin',.50,.19,.65,.62,angle=180,reference='materials',evidence='C'); sink(c)
        c=r.asset('water_closet',.50,.79,.51,.75,reference='main_plan' if 'MAIN' in r.room['id'] else 'guest_plan'); toilet(c)
    else:
        c=r.asset('washbasin',.23,.80,.65,.62,reference='materials',evidence='C'); sink(c)
        c=r.asset('water_closet',.78,.78,.51,.75,reference='main_plan' if 'MAIN' in r.room['id'] else 'guest_plan'); toilet(c)
    if not has_tub:
        c=r.asset('towel_rail',.50,.16,.48,.13,180,reference='main_plan')
        c.tube('rail',[(-.22,0,.88),(-.22,-.09,.88),(.22,-.09,.88),(.22,0,.88)],.012,'metal')
        c.box('folded_towel',(0,-.1,.68),(.33,.035,.40),'linen',.007)


def room_wine(r):
    a=r.asset('wine_storage_rack',.23,.77,min(2.35,r.w*.52),.38,reference='main_plan')
    height=1.72
    for x in (-a.w/2,a.w/2): a.box('rack_upright',(x,0,height/2),(.05,.35,height),'wood',.005)
    for j in range(6):
        z=.18+j*.25
        a.box('bottle_shelf',(0,0,z),(a.w,.37,.028),'wood',.004)
        for i in range(max(1,int(a.w/.13))):
            x=-a.w/2+.08+i*.13
            b=a.lathe('dark_wine_bottle',[(0,0),(.048,0),(.052,.19),(.025,.25),(.018,.26),(.018,.31),(0,.31)],
                      center=(x,.13,z+.07),mat='bottle_glass',n=16)
            # Lathe coordinates are baked; rotate locally about its own base via mesh transform.
            from mathutils import Matrix
            pivot=Vector((x,.13,z+.07))
            b.data.transform(Matrix.Translation(pivot) @ Matrix.Rotation(math.pi/2,4,'X') @ Matrix.Translation(-pivot))
    t=r.asset('cellar_workbench',.73,.29,min(1.25,r.w*.35),.48,180,reference='main_plan'); table(t,.79)


def room_boiler(r):
    compact=r.d<1.30
    b=r.asset('service_boiler',.60 if compact else .28,.5 if compact else .72,
              .74 if compact else .89,.78 if compact else .97,
              reference='main_plan' if 'MAIN' in r.room['id'] else 'guest_plan')
    if compact:
        b.root.scale=(.77,.73,.93)
        b.root['functional_note']='Compact inferred boiler in shallow surveyed equipment niche; inspect from doorway.'
    b.box('equipment_pad',(0,0,.05),(.95,1.03,.1),'stone',.007)
    b.box('cast_boiler_body',(0,0,.62),(.81,.83,1.02),'steel_shadow',.035)
    for x in (-.29,-.145,0,.145,.29): b.box('cast_section_rib',(x,-.425,.67),(.045,.06,.88),'dark',.012)
    b.box('burner_door',(0,-.46,.32),(.39,.08,.30),'dark',.018)
    b.cylinder('flue',(0,.15,1.74),.12,1.26,'metal')
    for x in (-.30,.30):
        b.tube('service_pipe',[(x,.27,1.0),(x,.27,1.61),(x+.21,.27,1.61),(x+.21,.27,2.05)],.028,'metal')
        b.cylinder('valve',(x,.255,1.55),.065,.018,'red',rotation=(math.pi/2,0,0))
    b.cylinder('pressure_gauge',(0,-.445,1.0),.06,.035,'metal',rotation=(math.pi/2,0,0))
    b.cylinder('gauge_face',(0,-.468,1.0),.049,.004,'paper',rotation=(math.pi/2,0,0))
    t=r.asset('service_pressure_vessel',.19 if compact else .77,.5 if compact else .76,.53,.53,reference='main_plan')
    t.lathe('tank',[(0,0),(.19,.03),(.24,.14),(.24,1.2),(.18,1.32),(0,1.35)],mat='steel_shadow')
    t.tube('tank_connection',[(0,0,1.32),(0,0,1.60),(.2,0,1.60)],.021,'metal')


def room_laundry(r):
    a=r.asset('laundry_sink',.22,.81,.78,.67,reference='guest_plan')
    sink(a,False)
    for x in (.55,.78):
        a=r.asset('laundry_appliance',x,.82,.67,.66,reference='guest_plan')
        a.box('enameled_case',(0,0,.46),(.65,.64,.88),'steel_cream',.022)
        a.box('top',(0,0,.92),(.67,.66,.04),'ceramic',.012)
        a.box('controls',(0,.24,1.02),(.64,.15,.16),'steel_shadow',.012)
        a.cylinder('loading_rim',(0,-.338,.48),.225,.04,'metal',rotation=(math.pi/2,0,0))
        a.cylinder('loading_glass',(0,-.363,.48),.185,.012,'dark',rotation=(math.pi/2,0,0))
        for xx in (-.17,.15): a.cylinder('control_dial',(xx,.155,1.02),.032,.018,'dark',rotation=(math.pi/2,0,0))
    a=r.asset('folding_worktable',.55,.27,min(2.1,r.w*.60),.66,180,reference='guest_plan'); table(a,.83)
    for i in range(3): a.box('folded_linen',(-.4+i*.39,0,.89+i*.005),(.33,.43,.07),'linen',.023)
    a=r.asset('wall_drying_rail',width=1.14,depth=.38,center=(*r.point(.24,.88)[:2],r.z+1.56),reference='guest_plan')
    for x in (-.56,.56):
        a.beam('wall_rack_bracket',(x,.18,0),(x,-.18,.30),.014,'metal')
        a.beam('rack_top',(x,.18,.30),(x,-.18,.30),.014,'metal')
    for y in (-.18,-.06,.06,.18): a.beam('drying_bar',(-.56,y,.30),(.56,y,.30),.011,'metal')


def room_theater(r):
    # 2010 survey confirms THEATER; exact current seats/projector are unverified C.
    screen=r.asset('theater_screen',.5,.91,min(3.45,r.w*.75),.12,reference='guest_plan')
    screen.box('screen_frame',(0,0,1.52),(screen.w,.075,1.72),'dark',.006)
    screen.box('screen_cloth',(0,-.042,1.52),(screen.w-.12,.012,1.60),'linen',.001)
    for v in (.30,.43,.56):
        for u in (.24,.36,.64,.76):
            # Rows remain aligned; irregular edge candidates are not relocated into aisles.
            point=r.point(u,v)
            if not all(inside(p,r.polygon) for p in footprint(point,.68,.76,math.pi)): continue
            c=r.asset('theater_seat',center=point,width=.56,depth=.63,angle=180,reference='guest_plan',fit=False)
            chair(c)
            for xx in (-.29,.29): c.box('armrest',(xx,0,.61),(.055,.52,.045),'wood',.012)
    p=r.asset('projection_equipment',.84,.16,.56,.49,reference='guest_plan')
    p.box('projector_pedestal',(0,0,.62),(.34,.34,1.24),'dark',.008)
    p.box('projector',(0,0,1.33),(.46,.35,.17),'steel_shadow',.018)
    p.cylinder('lens',(0,.21,1.34),.05,.12,'dark',rotation=(math.pi/2,0,0))


def room_service_lounge(r):
    a=r.asset('service_settee',.48,.80,min(1.9,r.w*.59),.68,reference='main_plan' if 'MAIN' in r.room['id'] else 'guest_plan'); bench(a,'rust_fabric')
    a=r.asset('small_sitting_table',.50,.45,.91,.55,reference='main_plan'); table(a,.48,True)
    a=r.asset('sitting_room_casework',.18,.24,min(1.3,r.w*.36),.37,180,reference='main_plan'); bookshelf(a,.98,3)


def room_coat(r):
    a=r.asset('coat_storage',.50,.80,min(1.4,r.w*.72),min(.48,r.d*.48),reference='main_plan')
    cabinet(a,1.95,max(1,int(a.w/.5)))
    a.root['functional_note']='Closet interior represented by side/back/shelf; doors closed, inspectable in outliner.'


def room_terrace(r):
    # Sparse documented pottery vocabulary, never every terrace filled with repeated furniture.
    if 'POTTERY' in r.room['id'] or 'pottery' in r.room.get('label','').lower():
        for i in range(3):
            a=r.asset('terrace_pottery',.20+i*.21,.84,.36,.36,reference='living'); pottery(a,0,i)


def make_local_materials(ctx):
    from materials import material, surface
    specs={
      'steel_cream':((.60,.58,.45),.32,0), 'steel_shadow':((.17,.19,.17),.43,.3),
      'counter':((.20,.19,.15),.34,0), 'paper':((.56,.50,.37),.78,0),
      'book_rust':((.27,.075,.035),.72,0), 'book_sage':((.15,.21,.15),.70,0),
      'book_ochre':((.43,.29,.075),.76,0), 'earth_pottery':((.25,.115,.055),.40,0),
      'bottle_glass':((.025,.053,.017),.25,0), 'mirror':((.72,.76,.74),.045,1),
      'lamp_diffuser':((.72,.58,.34),.8,0),
    }
    for key,(color,rough,metalness) in specs.items():
        ctx.mats[key]=material(key,color,rough,metalness)[0]
    ctx.mats['bluegrey']=surface('bluegrey',(.20,.29,.31),.95,95,.20,.0015,'cloth')
    p=ctx.mats['lamp_diffuser'].node_tree.nodes.get('Principled BSDF')
    p.inputs['Emission Color'].default_value=(1,.67,.32,1)
    p.inputs['Emission Strength'].default_value=.12
    # Separate from the archival guest standing-lamp diffuser: lighting.apply
    # intentionally must not overwrite these explicit C service-fixture settings.
    bulb=material('service_clear_bulb_C',(.88,.83,.72),.10,0)[0]
    nodes=bulb.node_tree.nodes;links=bulb.node_tree.links
    p=nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=1.
    p.inputs['IOR'].default_value=1.45
    transparent=nodes.new('ShaderNodeBsdfTransparent');shadow=nodes.new('ShaderNodeLightPath')
    mix=nodes.new('ShaderNodeMixShader');links.new(shadow.outputs['Is Shadow Ray'],mix.inputs[0])
    links.new(p.outputs[0],mix.inputs[1]);links.new(transparent.outputs[0],mix.inputs[2])
    links.new(mix.outputs[0],nodes.get('Material Output').inputs['Surface'])
    ctx.mats['service_clear_bulb_C']=bulb
    filament=material('service_filament_C',(.90,.74,.42),.35,0)[0]
    p=filament.node_tree.nodes.get('Principled BSDF')
    p.inputs['Emission Color'].default_value=(1.,.86,.67,1.)
    p.inputs['Emission Strength'].default_value=12.
    ctx.mats['service_filament_C']=filament


def practical_fixture(r):
    """A visible supported porcelain socket/bulb; never a hidden room fill."""
    watts=PRACTICAL_FIXTURES.get(r.room['id'])
    if watts is None:return None
    scene=bpy.context.scene;bpy.context.view_layer.update()
    depsgraph=bpy.context.evaluated_depsgraph_get()
    expected=r.z+r.room['height'];cx,cy=r.room['center'][:2]
    candidates=[(cx,cy)]+[(r.x0+r.w*u,r.y0+r.d*v) for u in (.35,.5,.65) for v in (.35,.5,.65)]
    candidates.sort(key=lambda p:(p[0]-cx)**2+(p[1]-cy)**2)
    mount=None;attempts=[]
    for x,y in candidates:
        if not all(inside((x+dx,y+dy),r.polygon) for dx,dy in ((0,0),(.14,0),(-.14,0),(0,.14),(0,-.14))):continue
        hit,loc,normal,index,obj,matrix=scene.ray_cast(depsgraph,Vector((x,y,expected-.45)),Vector((0,0,1)),distance=.9)
        structural=bool(hit and obj and not obj.name.startswith('FW_FURN_') and normal.z<-.8 and abs(loc.z-expected)<.30)
        attempts.append({'xy':[x,y],'hit':obj.name if hit else None,'z':float(loc.z) if hit else None,'structural_ceiling':structural})
        if not structural:continue
        # Ensure the whole socket plate touches a flat structural ceiling, and
        # the bulb/small guard occupy free air rather than a cupboard or pipe.
        clear=True
        for dx,dy in ((0,0),(.09,0),(-.09,0),(0,.09),(0,-.09)):
            top=scene.ray_cast(depsgraph,Vector((x+dx,y+dy,loc.z-.21)),Vector((0,0,1)),distance=.26)
            if not top[0] or abs(top[1].z-loc.z)>.012 or top[4].name.startswith('FW_FURN_'):
                clear=False;break
        if clear:mount=(x,y,float(loc.z),obj.name);break
    if mount is None:
        r.warnings.append('C practical fixture skipped: no verified flat ceiling support with free bulb clearance')
        return {'room_id':r.room['id'],'status':'NOT_BUILT_NO_SAFE_SUPPORT','attempts':attempts}
    x,y,z,support=mount
    a=r.asset('practical_ceiling_lamp_C',center=(x,y,z),width=.20,depth=.20,
              reference='C substitute prompted by actual room dark-view QA; archival fixture identity not established',
              evidence='C',placement='C: verified structural ceiling support; not archival fixture placement',fit=False)
    a.root['support_object']=support;a.root['mount_z']=z
    a.cylinder('porcelain_mount',(0,0,-.012),.075,.024,'ceramic',n=32)
    a.cylinder('porcelain_socket',(0,0,-.045),.032,.045,'ceramic',n=24)
    a.cylinder('brass_socket_ring',(0,0,-.067),.024,.016,'brass',n=24)
    bulb=a.lathe('clear_visible_bulb',[(0,-.163),(.035,-.157),(.057,-.137),(.061,-.112),
             (.048,-.088),(.022,-.074),(.019,-.064)],mat='service_clear_bulb_C',n=32)
    bulb['shadow_model']='C: transmissive bulb shell uses transparent shadow rays; not a hidden emitter'
    a.tube('visible_emissive_filament',[(-.017,0,-.101),(-.010,0,-.128),(0,0,-.118),
             (.010,0,-.128),(.017,0,-.101)],.0022,'service_filament_C')
    for dx in (-.075,.075):
        a.tube('protective_metal_guard',[(dx,0,-.019),(dx,0,-.145),(dx*.45,0,-.18),(0,0,-.185)],.003,'metal')
    data=bpy.data.lights.new(a.name+'_bulb_photometric_proxy','POINT')
    data.energy=watts;data.color=(1.,.86,.67);data.shadow_soft_size=.027;data.use_shadow=True
    light=bpy.data.objects.new(data.name,data);r.coll.objects.link(light);a.add(light)
    light.location=(0,0,-.12)
    light['power_evidence']='C: artistic photometric proxy, not a surveyed historical wattage'
    light['visible_source']=bulb.name;light['power_watts']=watts
    light['source_type']='Point inside visible clear bulb; complements tiny emissive filament in Cycles/EEVEE'
    return {'room_id':r.room['id'],'status':'BUILT_C_SUBSTITUTE_GEOMETRIC_SUPPORT_CHECKED',
            'asset':a.name,'mount':[x,y,z],'support_object':support,'bulb_world_center':[x,y,z-.12],
            'power_watts_C':watts,'emission_strength_C':12.,'color_C':[1.,.86,.67],
            'lowest_fixture_z':z-.188,'floor_z':r.z,'ceiling_expected_z':expected,
            'method':'Actual scene upward rays at center and four radial offsets; same flat ceiling, clear 0.21 m fixture volume',
            'visual_status':'NOT_RENDERED_THIS_BUILD','attempts':attempts}


EXPLICIT={
    'bench':lambda a,p:bench(a,p.get('fabric','cream_fabric')),
    'sofa':lambda a,p:bench(a,p.get('fabric','cream_fabric')),
    'cabinet':lambda a,p:cabinet(a,p.get('height',.66),p.get('doors',3),p.get('steel',False),p.get('drawers',False)),
    'table':lambda a,p:table(a,p.get('height',.70),p.get('pedestal',False)),
    'chair':lambda a,p:chair(a,p.get('farm',False),p.get('sling',False)),
    'bed':lambda a,p:bed(a,p.get('guest',False),p.get('service',False)),
    'bookshelf':lambda a,p:bookshelf(a,p.get('height',1.50),p.get('levels',4)),
    'sink':lambda a,p:sink(a,p.get('kitchen',False)),
    'toilet':lambda a,p:toilet(a), 'tub':lambda a,p:tub(a),
    'kettle':lambda a,p:kettle(a), 'aga':lambda a,p:range_aga(a),
    'fridge':lambda a,p:fridge(a), 'dishwasher':lambda a,p:dishwasher(a),
    'lamp':lambda a,p:lamp(a,p.get('vertical',False)),
    'pottery':lambda a,p:pottery(a,p.get('base_height',0),p.get('variant',0)),
    'art_placeholder':lambda a,p:framed_placeholder(a,p.get('width',.68),p.get('height',.47)),
}


def dispatch(r):
    room=r.room
    kind=(room.get('kind','')+' '+room.get('label','')+' '+room['id']).lower().replace('_',' ')
    guest='guest' in room.get('building','').lower() or room['id'].startswith(('GUEST','SERVICE'))
    # Census role wins over embedded words such as "Master Bedroom Terrace".
    role=room.get('kind','').lower()
    if role in ('terrace',): room_terrace(r); return
    if role in ('foundation','pool','stair','water_stair','loggia','entry','hall','circulation','car_court'): return
    if role in ('closet','wardrobe'): room_coat(r); return
    if role=='gallery':
        a=r.asset('gallery_art_placeholder',.5,.91,min(.75,r.w*.35),.05,reference='main_plan'); framed_placeholder(a)
        return
    if 'foundation' in kind or 'pool' in kind or 'car court' in kind or 'stair' in kind: return
    if 'bath' in kind or 'wc' in kind: room_bath(r)
    elif 'kitchen' in kind: room_kitchen(r)
    elif 'wine' in kind: room_wine(r)
    elif 'boiler' in kind or 'mechanical' in kind: room_boiler(r)
    elif 'laundry' in kind: room_laundry(r)
    elif 'theater' in kind or 'theatre' in kind: room_theater(r)
    elif 'dressing' in kind: room_study(r,True)
    elif 'study' in kind: room_study(r)
    elif 'sleeping' in kind or 'alcove' in kind: room_bedroom(r,alcove=True)
    elif 'bedroom' in kind or 'guest room' in kind:
        service=('service' in kind or 'servant' in kind or 'chauffeur' in kind or (guest and room.get('level') in (2,'L2','2')))
        room_bedroom(r,guest and not service,service)
    elif 'servant' in kind or 'chauffeur' in kind or 'sitting' in kind: room_service_lounge(r)
    elif 'living' in kind or 'lounge' in kind: room_living(r,guest)
    elif 'coat' in kind or 'closet' in kind or 'wardrobe' in kind: room_coat(r)
    elif 'terrace' in kind: room_terrace(r)
    elif 'entry' in kind or 'gallery' in kind or 'hall' in kind or 'loggia' in kind:
        # Circulation is kept clear; wall-mounted artwork only for gallery.
        if 'gallery' in kind:
            a=r.asset('gallery_art_placeholder',.5,.91,min(.75,r.w*.35),.05,reference='main_plan'); framed_placeholder(a)
    else:
        r.warnings.append('No furniture program assigned: review room role, do not invent its use.')


def build(ctx,rooms):
    for obj in list(bpy.data.objects):
        if obj.name.startswith('FW_FURN_'): bpy.data.objects.remove(obj,do_unlink=True)
    make_local_materials(ctx)
    built=[]; report=[];fixture_report=[]
    for room in rooms:
        if not room.get('polygon') or len(room['polygon'])<3: continue
        r=Room(ctx,room)
        explicit=room.get('furniture',[])
        if explicit and room.get('furniture_complete',False):
            for p in explicit:
                typ=p['type'].lower()
                if typ not in EXPLICIT:
                    r.warnings.append('Unknown explicit furniture type: '+typ); continue
                a=r.asset(p.get('name',typ),width=p.get('width',1),depth=p.get('depth',.5),
                          center=p['center'],angle=p.get('angle',0),reference=p.get('reference','main_plan'),
                          evidence=p.get('evidence','C'),placement=p.get('placement_evidence','A'),fit=False)
                EXPLICIT[typ](a,p)
        else:
            dispatch(r)
            # Optional extras are deliberate additions; complete schedules should set furniture_complete.
            for p in r.explicit:
                typ=p['type'].lower()
                if typ in EXPLICIT and not p.get('_consumed'):
                    a=r.asset(p.get('name',typ),width=p.get('width',1),depth=p.get('depth',.5),center=p['center'],
                              angle=p.get('angle',0),reference=p.get('reference','main_plan'),evidence=p.get('evidence','C'),fit=False)
                    options=dict(p)
                    if typ=='bed' and room.get('building')=='GUEST': options['guest']=True
                    EXPLICIT[typ](a,options)
        fixture=practical_fixture(r)
        if fixture:fixture_report.append(fixture)
        objs=[o for a in r.assets for o in [a.root]+a.objects]
        built.extend(objs)
        report.append({'room_id':room['id'],'label':room.get('label',''),'asset_count':len(r.assets),
                       'object_count':len(objs),'assets':[{'id':a.name,'type':a.kind,'center':list(a.root.location),
                        'width':a.w,'depth':a.d,'angle_degrees':math.degrees(a.root.rotation_euler.z),
                        'reference':a.ref,'form_evidence':a.evidence,'dimensions_evidence':'C',
                        'placement_evidence':a.root['placement_evidence']} for a in r.assets],
                       'warnings':r.warnings})
    output=Path(ctx.root)/'qa'/'interiors-build.json'
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps({'status':'BUILT_NOT_VISUALLY_ACCEPTED','rooms':report,
                                  'object_count':len(built),'note':'Photograph-informed parametric furniture. All unmeasured dimensions and service fittings are C.'},
                                 ensure_ascii=False,indent=2),encoding='utf-8')
    (output.parent/'interiors-practical-fixtures.json').write_text(json.dumps({'status':'C_SUBSTITUTES_REQUIRE_RENDER_QA',
        'fixtures':fixture_report,'scope':'Visible supported bulbs only; no hidden area fills; all fixture forms, placement and power are C.'},
        ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'FURNISHINGS: {len(built)} objects in {len(report)} room records; {output}')
    return built
