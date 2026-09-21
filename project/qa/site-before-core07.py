"""Bear Run, layered sandstone and linked-mesh forest. Coordinates are metres.

This is an authored, photograph-informed landscape (evidence C), not a survey.
Only this module's SITE_/TREE_/WATER_ objects are replaced on rebuild.
"""
import bpy
import json
import math
import random
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from fwlib import box, poly_prism, mesh_object, segment, tag

TAU = 2 * math.pi
OWNER = 'fw_site'


def _mesh(name, vertices, faces, material, coll, smooth=False):
    obj = mesh_object(name, vertices, faces, material, coll, smooth)
    obj['owner'] = OWNER
    obj['evidence'] = 'C'
    return obj


def _owned(obj, role):
    obj['owner'] = OWNER
    obj['evidence'] = 'C'
    obj['role'] = role
    return obj


def _inside(x, y, bbox, margin=0):
    return bbox[0]-margin < x < bbox[1]+margin and bbox[2]-margin < y < bbox[3]+margin


def _segment_near(x, y, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    t = max(0, min(1, ((x-a[0])*dx + (y-a[1])*dy) / max(1e-8, dx*dx+dy*dy)))
    qx, qy = a[0]+dx*t, a[1]+dy*t
    return math.hypot(x-qx, y-qy), t


def _river_near(x, y, river):
    best = (1e20, 0, river[0][2], river[0][3], 0)
    for i, (a, b) in enumerate(zip(river, river[1:])):
        dist, t = _segment_near(x, y, a, b)
        if dist < best[0]:
            best = dist, t, a[2]+(b[2]-a[2])*t, a[3]+(b[3]-a[3])*t, i
    return best


def _height(x, y, cfg):
    # Wide forested hills around a continuously carved creek channel.
    z = 0.10 + 0.205*max(y, 0) + 0.035*max(abs(x)-14, 0)
    z += .62*math.sin(x*.093+y*.035) + .31*math.sin(y*.137-x*.048)
    z += .14*math.sin(x*.81+y*.47) + .085*math.cos(x*1.92-y*.63)
    if y < -3: z -= min(3.0, (-y-3)*.095)
    radius=math.hypot(x-5,y-10)
    far=max(0,min(1,(radius-105)/180));far=far*far*(3-2*far)
    # Continue a gently folded wooded valley instead of an infinite tilted plane.
    far_z=12+7*math.sin(x*.012)+5.5*math.cos(y*.009)+4.3*math.sin((x+y)*.016)
    far_z+=8*max(0,math.tanh(y/250))-.008*max(0,-y)
    z=z*(1-far)+far_z*far
    dist, t, water_z, width, i = _river_near(x, y, cfg.get('_terrain_river_path',cfg['river_path']))
    bed = water_z - .53 - .19*math.sin(x*.66+y*.7)
    edge = width*.5
    if dist < edge: z = bed + .34*(dist/edge)**5
    shoulder=5.5+min(15,max(0,radius-70)*.15)
    shoulder+=min(1,max(0,(radius-75)/40))*(1.8+1.5*math.sin(x*.052-y*.031))
    if edge<dist<edge+shoulder:
        blend = (dist-edge)/shoulder
        blend = blend*blend*(3-2*blend)
        z = bed+.22 + (z-bed-.22)*blend
    # Bedrock occupies this volume; soil must not bury its exposed waterfall face.
    lip=cfg['river_path'][8];end=cfg['river_path'][9]
    dx,dy=end[0]-lip[0],end[1]-lip[1];length=math.hypot(dx,dy);dx/=length;dy/=length
    along=(x-lip[0])*dx+(y-lip[1])*dy;cross=(x-lip[0])*(-dy)+(y-lip[1])*dx
    if -8.5<along<2.2 and abs(cross)<6.7:
        blend=min(1,max(0,(6.7-abs(cross))/1.1),max(0,(along+8.5)/.8),max(0,(2.2-along)/.6))
        z=min(z,z*(1-blend)+(-6.5)*blend)
    # Building interiors remain free of terrain; surrounding terrain remains continuous.
    for zone in cfg['building_exclusions']:
        x0,x1,y0,y1=zone['bbox']
        outside=math.hypot(max(x0-x,0,x-x1),max(y0-y,0,y-y1))
        if outside<3.2:
            target=min(z,zone['ground_cap'])
            blend=min(1,outside/3.2);blend=blend*blend*(3-2*blend)
            z=target*(1-blend)+z*blend
    for route in cfg['paths']:
        for a, b in zip(route['points'], route['points'][1:]):
            d, u = _segment_near(x, y, a, b)
            if d < route['width']*.7:
                rz = a[2]+(b[2]-a[2])*u-.07
                w = max(0, 1-(d/(route['width']*.7))**4)
                z = z*(1-w)+rz*w
    # Where a route passes over a cellar/plunge terrace the soil stays below the
    # actual lower floor; its paving can bridge the space independently.
    for zone in cfg['building_exclusions']:
        if _inside(x,y,zone['bbox']):z=min(z,zone['ground_cap'])
    return z


def _axis(lo, hi):
    vals = [float(lo)]
    while vals[-1] < hi:
        a = vals[-1]
        if -35<a<58:step=.65
        elif -112<a<132:step=2.15
        elif -290<a<310:step=7
        else:step=22
        vals.append(min(hi, a+step))
    return vals


def _terrain(ctx, cfg, rng, coll):
    xmin, xmax, ymin, ymax = cfg['terrain_bounds']
    xx, yy = _axis(xmin,xmax), _axis(ymin,ymax)
    verts = [(x,y,_height(x,y,cfg)) for y in yy for x in xx]
    faces=[]; n=len(xx)
    for j in range(len(yy)-1):
        for i in range(n-1):
            q=j*n+i
            faces.extend([(q,q+1,q+n+1),(q,q+n+1,q+n)])
    ground=ctx.mats['earth'].copy();ground.name='FW_Continuous_Forest_Floor'
    ns,ls=ground.node_tree.nodes,ground.node_tree.links;p=ns.get('Principled BSDF')
    tc=ns.new('ShaderNodeTexCoord');tex=ns.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=1.6;tex.inputs['Detail'].default_value=4.4
    ls.new(tc.outputs['Object'],tex.inputs['Vector'])
    ramp=ns.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.20;ramp.color_ramp.elements[0].color=(.045,.029,.013,1)
    ramp.color_ramp.elements[1].position=.83;ramp.color_ramp.elements[1].color=(.040,.068,.018,1)
    mid=ramp.color_ramp.elements.new(.45);mid.color=(.074,.093,.032,1)
    ls.new(tex.outputs['Fac'],ramp.inputs[0]);ls.new(ramp.outputs['Color'],p.inputs['Base Color'])
    terrain = _mesh('SITE_Continuous_BearRun_Terrain',verts,faces,ground,coll,True)
    return terrain


def _slab(ctx, coll, name, center, size, rng, wet=False):
    x,y,z=center; sx,sy,h=size
    # Unequal angular fracture facets, a shallow dip and eroded margins replace
    # repeated chamfered rectangles. Geometry remains bedded rather than rounded.
    count=rng.randint(9,13);angles=sorted([j*TAU/count+rng.uniform(-.13,.13) for j in range(count)])
    outline=[(math.cos(a)*sx*.5*rng.uniform(.75,1.08),math.sin(a)*sy*.5*rng.uniform(.78,1.06)) for a in angles]
    dipx=rng.uniform(-.035,.035);dipy=rng.uniform(-.027,.027);verts=[];faces=[]
    for ring,t in enumerate((-0.5,-.05,.5)):
        for j,(u,v) in enumerate(outline):
            cut=rng.uniform(.82,.97) if ring in (0,2) else rng.uniform(.96,1.05)
            height=z+h*t+u*dipx+v*dipy+rng.uniform(-h*.10,h*.10)
            verts.append((x+u*cut,y+v*cut,height))
    for ring in range(2):
        for j in range(count):
            k=ring*count+j;kn=ring*count+(j+1)%count
            faces.extend([(k,kn,kn+count),(k,kn+count,k+count)])
    faces.append(tuple(reversed(range(count))))
    verts.append((x,y,z+h*.49));center_index=len(verts)-1
    for j in range(count):faces.append((center_index,2*count+j,2*count+(j+1)%count))
    obj=_mesh(name,verts,faces,ctx.mats['wet_rock' if wet else 'rock'],coll)
    _owned(obj,'angular fractured bedrock with varied dip and eroded margins')
    return obj


def _geology(ctx, cfg, rng, coll):
    count=0
    # Broad ledges underpin the south cantilever and frame the two real-scale cascades.
    lip=Vector(cfg['river_path'][8][:2]);down=(Vector(cfg['river_path'][9][:2])-lip).normalized()
    across=Vector((-down.y,down.x))
    rockmats={False:ctx.mats['rock'],True:ctx.mats['wet_rock']}
    # A single continuous outcrop avoids the artificial dark voids and identical
    # slab corners of the former stack. Unequal geological beds merge at their
    # eroded boundaries, with local vertical joints interrupting the long bands.
    bounds=[-3.06,-3.24,-3.61,-3.71,-4.19,-4.49,-4.62,-5.21,-5.61,-6.38]
    layer_rows=[]
    for k,(top,bottom) in enumerate(zip(bounds,bounds[1:])):
        layer_rows.extend([(top,k,-.040),((top+bottom)*.5,k,.085),(bottom+.014,k,-.025)])
    perimeter_c=[-6.2+j*12.4/48 for j in range(49)]
    verts=[];faces=[];front_count=len(perimeter_c);row_count=front_count+4
    for row,(z,bed,erode) in enumerate(layer_rows):
        layer_offset=rng.uniform(-.17,.11);layer_dip=rng.uniform(-.014,.014)
        points=[]
        for j,c in enumerate(perimeter_c):
            protrusion=.36 if abs(c)>3.55 and bed in (2,3,6) else 0
            fissure=sum(-.12*math.exp(-((c-f)/.10)**2) for f in (-3.6,.43,3.15))
            irregular=.045*math.sin(c*6.8+bed*.9)+.055*math.sin(c*2.2-bed*.7)
            s=-.13-bed*.055+_lip_shift(c)+layer_offset+erode+protrusion+fissure+irregular
            p=lip+across*c+down*s
            zz=z+c*layer_dip+.035*math.sin(c*1.3+bed*.75)+rng.uniform(-.012,.012)
            if row==0:zz=min(zz,-3.055)
            points.append((p.x,p.y,zz))
        for c,s in [(6.2,-3),(5.9,-8),(-5.9,-8),(-6.2,-3)]:
            p=lip+across*c+down*s;points.append((p.x,p.y,z+.018*math.sin(c+s)))
        verts.extend(points)
    for row in range(len(layer_rows)-1):
        for j in range(row_count):
            q=row*row_count+j;qn=row*row_count+(j+1)%row_count
            faces.extend([(q,qn,qn+row_count),(q,qn+row_count,q+row_count)])
    faces.append(tuple(reversed(range(row_count))))
    last=(len(layer_rows)-1)*row_count;faces.append(tuple(last+j for j in range(row_count)))
    faces=[tuple(reversed(face)) for face in faces]
    core=_mesh('SITE_Core_Continuous_Fractured_Sandstone',verts,faces,rockmats[True],coll)
    core.data.materials.append(rockmats[False])
    for polygon in core.data.polygons:
        if abs((polygon.center.x-lip.x)*across.x+(polygon.center.y-lip.y)*across.y)>4.0:polygon.material_index=1
    _owned(core,'continuous sandstone outcrop: unequal beds, shallow dip, erosion and vertical joints')
    count+=1
    # Broad fractured shoulders stand exposed beside the flow, with overhangs and
    # horizontal bedding continuing into the stone foundation under the house.
    for shoulder,cross0 in enumerate((-5.3,4.9)):
        z=-3.28
        for j in range(4):
            thickness=rng.uniform(.48,.88)
            p=lip+across*(cross0+rng.uniform(-.40,.40))+down*rng.uniform(-.6,.7)
            obj=_slab(ctx,coll,f'SITE_Cascade_Shoulder_{shoulder}_{j}',(p.x,p.y,z-thickness*.5),
                      (rng.uniform(3.1,5.0),rng.uniform(2.3,4.2),thickness),rng,wet=j<3)
            z-=thickness*.79
            obj.data.materials[0]=rockmats[j<3];count+=1
    beds=[((-7.2,-4.65,-6.27),(9.2,4.1,.44)),((11,-7.1,-4.1),(8.0,3.0,.46))]
    for i,(c,s) in enumerate(beds):
        _slab(ctx,coll,f'SITE_Secondary_Sandstone_Ledge_{i:02}',c,s,rng,wet=i<5); count+=1
    # Stream-bank ledges follow the channel, rather than random boulders in the water.
    river=cfg['river_path']
    for i,(a,b) in enumerate(zip(river,river[1:])):
        if min(math.hypot(a[0],a[1]),math.hypot(b[0],b[1]))>90:continue
        length=math.hypot(b[0]-a[0],b[1]-a[1])
        if length<1.3: continue
        normal=Vector((-(b[1]-a[1]),b[0]-a[0])); normal.normalize()
        for k in range(max(1,int(length/3.1))):
            t=(k+.35)/max(1,int(length/3.1)); t=min(t,.98)
            width=a[3]+(b[3]-a[3])*t
            for side in (-1,1):
                x=a[0]+(b[0]-a[0])*t+normal.x*width*.54*side
                y=a[1]+(b[1]-a[1])*t+normal.y*width*.54*side
                if any(_inside(x,y,q['bbox'],.2) for q in cfg['building_exclusions']): continue
                wz=a[2]+(b[2]-a[2])*t
                layers=rng.randint(2,4)
                for j in range(layers):
                    h=rng.uniform(.19,.37)
                    z=wz-.10+j*.25
                    obj=_slab(ctx,coll,f'SITE_Bank_{count:04}',(x+rng.uniform(-.2,.2),y,z),
                          (rng.uniform(1.9,4.1),rng.uniform(1.2,2.6),h),rng,wet=j==0)
                    obj.data.materials[0]=rockmats[j==0]
                    count+=1
    # Low split talus stones and shallow submerged slabs are flattened, never spherical.
    for k in range(105):
        x=rng.uniform(-21,38); y=rng.uniform(-17,18)
        if any(_inside(x,y,q['bbox'],.3) for q in cfg['building_exclusions']): continue
        dist,_,wz,width,_=_river_near(x,y,river)
        if dist>width*.65+3: continue
        z=_height(x,y,cfg)+rng.uniform(.04,.12)
        _slab(ctx,coll,f'SITE_Split_Talus_{k:03}',(x,y,z),(rng.uniform(.3,1.2),rng.uniform(.25,.8),rng.uniform(.12,.35)),rng,wet=z<wz+.1)
        count+=1
    return count


def _lip_shift(c):
    return .18*math.sin(c*1.7)+.105*math.sin(c*4.8)+.055*math.cos(c*7.1)


def _route_mesh(ctx,route,coll):
    verts=[]
    for i,p in enumerate(route['points']):
        a=Vector(route['points'][max(0,i-1)][:2]); b=Vector(route['points'][min(len(route['points'])-1,i+1)][:2])
        tangent=(b-a).normalized(); normal=Vector((-tangent.y,tangent.x))*route['width']*.5
        verts.extend([(p[0]+normal.x,p[1]+normal.y,p[2]-.022),(p[0]-normal.x,p[1]-normal.y,p[2]-.022)])
    faces=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(route['points'])-1)]
    return _mesh('SITE_Path_'+route['name'],verts,faces,ctx.mats['gravel'],coll)


def _bridge(ctx,cfg,rng,coll):
    bridge=cfg['bridge']; x0,x1,y0,y1=bridge['bbox']; z=bridge['deck_z']
    _owned(box('SITE_BearRun_Bridge_Structural_Deck',((x0+x1)/2,(y0+y1)/2,z-.28),(x1-x0,y1-y0,.55),ctx.mats['ochre'],coll,.03),'bridge deck')
    # Individually laid, mortar-separated flagstones on the deck.
    yy=y0+.025; row=0
    while yy<y1-.1:
        dep=min(rng.uniform(.42,.66),y1-yy-.02); xx=x0+.025
        while xx<x1-.09:
            width=min(rng.uniform(.52,.90),x1-xx-.02)
            pts=[(xx+.012,yy+.012),(xx+width-.018,yy+.01),(xx+width-.005,yy+dep-.018),(xx+.016,yy+dep-.005)]
            _owned(poly_prism(f'SITE_Bridge_Flag_{row:03}',pts,z-.01,z+.012,ctx.mats['stone_floor'],coll),'bridge paving'); row+=1
            xx+=width
        yy+=dep
    for side,x in enumerate((x0+.13,x1-.13)):
        for j in range(3):
            yy=y0-.05
            while yy<y1:
                length=min(rng.uniform(.62,1.20),y1-yy+.05)
                _owned(box(f'SITE_Bridge_Parapet_{side}_{j}_{yy:.2f}',(x,yy+length*.5,z+.14+j*.205),
                           (.31+rng.uniform(-.025,.025),length-.014,.195),ctx.mats['stone'],coll,.011),'bridge masonry parapet')
                yy+=length
        # Stone abutments at both dry banks support the full crossing.
        for y in (y0+.65,y1-.65):
            _owned(box(f'SITE_Bridge_Abutment_{side}_{y:.1f}',(x,y,-1.65),(.42,1.8,3.1),ctx.mats['stone'],coll,.016),'bridge stone abutment')
    for route in cfg['paths']: _route_mesh(ctx,route,coll)


def _shader_water(ctx):
    # Clone the shared material: site animation must not mutate guest swimming-pool water.
    mat=ctx.mats['water'].copy(); mat.name='FW_BearRun_Looping_Water'
    nt=mat.node_tree; p=nt.nodes.get('Principled BSDF')
    tc=nt.nodes.new('ShaderNodeTexCoord')
    p.inputs['Base Color'].default_value=(.39,.47,.42,1)
    p.inputs['Roughness'].default_value=.085
    for node in nt.nodes:
        if node.bl_idname=='ShaderNodeTexNoise' and node.noise_dimensions=='4D':
            nt.links.new(tc.outputs['Object'],node.inputs['Vector'])
            node.inputs['W'].driver_add('default_value').driver.expression='0.32*sin((frame-1)*6.28318530718/240)'
            node.inputs['Scale'].default_value=5.2
        if node.bl_idname=='ShaderNodeBump':
            node.inputs['Distance'].default_value=.036
            node.inputs['Strength'].default_value=.22
        if node.bl_idname=='ShaderNodeVolumeAbsorption': node.inputs['Density'].default_value=.085
    return mat


def _cascade_material(mat):
    result=mat.copy();result.name='FW_BearRun_Aerated_Cascade'
    ns,ls=result.node_tree.nodes,result.node_tree.links;p=ns.get('Principled BSDF')
    tc=ns.new('ShaderNodeTexCoord');scale=ns.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(4,4,1.1)
    ls.new(tc.outputs['Object'],scale.inputs[0])
    noise=ns.new('ShaderNodeTexNoise');noise.noise_dimensions='4D';noise.inputs['Scale'].default_value=22;noise.inputs['Detail'].default_value=3
    noise.inputs['W'].driver_add('default_value').driver.expression='0.65*sin((frame-1)*6.28318530718/240)'
    ls.new(scale.outputs[0],noise.inputs['Vector'])
    ramp=ns.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.20;ramp.color_ramp.elements[0].color=(.15,.24,.20,1)
    ramp.color_ramp.elements[1].position=.82;ramp.color_ramp.elements[1].color=(.58,.68,.61,1)
    ls.new(noise.outputs['Fac'],ramp.inputs[0]);ls.new(ramp.outputs['Color'],p.inputs['Base Color'])
    p.inputs['Transmission Weight'].default_value=.74;p.inputs['Roughness'].default_value=.095
    return result


def _periodic_surface(obj, coordinates, amplitude=.026, scale=2.2):
    obj.shape_key_add(name='Basis')
    for key_name,fn,trig in [('Flow sine',math.sin,'cos'),('Flow cosine',math.cos,'sin')]:
        sk=obj.shape_key_add(name=key_name); sk.slider_min=-1; sk.slider_max=1
        for i,(distance,cross,weight) in enumerate(coordinates):
            sk.data[i].co.z += amplitude*fn(distance*scale+cross*1.7)*weight
        sign='-' if trig=='sin' else ''
        sk.driver_add('value').driver.expression=f'{sign}{trig}((frame-1)*6.28318530718/240)'
    obj['animation_period_frames']=240
    obj['animation_method']='smooth periodic advection basis; frame1 == frame241'


def _water(ctx,cfg,rng,coll):
    mat=_shader_water(ctx); river=cfg['river_path']
    vertices=[];faces=[];params=[]; rows=[]; distance=0
    # Denser samples around ledges; falls remain deliberately broken into separate ribbons.
    for idx,(a,b) in enumerate(zip(river,river[1:])):
        length=math.hypot(b[0]-a[0],b[1]-a[1]); drop=abs(b[2]-a[2])
        steps=max(2,int(length/.4))
        if drop>1: steps=18
        for j in range(steps):
            t=j/steps; rows.append((a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t,a[3]+(b[3]-a[3])*t,distance+length*t,drop>1))
        distance+=length
    rows.append((*river[-1],distance,False))
    across=30
    lip_distance=sum(math.hypot(q[0]-p[0],q[1]-p[1]) for p,q in zip(river[:8],river[1:9]))
    for i,p in enumerate(rows):
        a=rows[max(0,i-1)]; b=rows[min(len(rows)-1,i+1)]
        tangent=Vector((b[0]-a[0],b[1]-a[1])).normalized(); normal=Vector((-tangent.y,tangent.x))
        for k in range(across+1):
            cross=(k/across-.5)*p[3]
            jag=.10*math.sin(p[4]*1.4+k*.25)*(abs(k/across-.5)*2)**8
            x=p[0]+normal.x*(cross+jag); y=p[1]+normal.y*(cross+jag)
            lip_offset=_lip_shift(cross)*math.exp(-abs(p[4]-lip_distance)/1.7)
            x+=tangent.x*lip_offset;y+=tangent.y*lip_offset
            wave=.009*math.sin(p[4]*4.1+cross*3.6)
            vertices.append((x,y,p[2]+wave)); params.append((p[4],cross,.28 if p[5] else .6))
    for i in range(len(rows)-1):
        # The main cascade gets thin, disconnected ribbons instead of an opaque single sheet.
        if rows[i][5]: continue
        for k in range(across):
            q=i*(across+1)+k;faces.append((q,q+1,q+across+2,q+across+1))
    surface=_mesh('WATER_BearRun_Continuous_Upstream_Downstream',vertices,faces,mat,coll,True)
    _periodic_surface(surface,params)
    solid=surface.modifiers.new('Physical water volume','SOLIDIFY');solid.thickness=.075;solid.offset=-1
    # Segmented falling curtains follow the under-cantilever ledge.
    a=Vector(river[8][:3]); b=Vector(river[9][:3]); d=Vector((b.x-a.x,b.y-a.y,0)).normalized(); n=Vector((-d.y,d.x,0))
    all_verts=[];all_faces=[];all_params=[]
    stream_groups=[(-3.85,.23,.12,-.18),(-3.19,.40,.22,.11),(-2.52,.14,.16,-.10),
                   (-1.94,.72,.40,.08),(-.89,1.02,.34,-.13),(.27,.19,.3,.12),
                   (.96,.49,.53,.17),(1.85,.83,.62,.28),(3.18,.24,.19,-.13)]
    for i,(cross,width,throw,side_drift) in enumerate(stream_groups):
        first=len(all_verts);phase=rng.uniform(0,TAU);nu=max(3,math.ceil(width/.075));nv=56
        for j in range(nv):
            t=j/(nv-1)
            # Rock-controlled water packets have unequal width, sideward flow and
            # irregular air holes. Large exposed gaps retain readable ledge rock.
            for k in range(nu+1):
                u=k/nu-.5
                edgewidth=width*(1-.18*math.sin(math.pi*t))*(1+.04*math.sin(t*31+phase))
                c=cross+u*edgewidth+side_drift*t+.018*math.sin(t*47+phase+u*4)
                position=a.lerp(b,t)+n*c+d*(_lip_shift(cross)+throw*math.sin(math.pi*t*.8))
                position.z=a.z+(b.z-a.z)*t**(1.34+(i%3)*.06)
                position+=d*(.011*math.sin(t*48+u*13+phase)*math.sin(math.pi*t))
                all_verts.append(tuple(position));all_params.append((t*13+phase,c,math.sin(math.pi*t)))
                if j<nv-1 and k<nu:
                    f=first+j*(nu+1)+k
                    broken=(j>18 and rng.random()<(.09+.20*t) and 0<k<nu-1)
                    ragged=(k in (0,nu-1) and j>34 and rng.random()<.15)
                    if not broken and not ragged:all_faces.append((f,f+1,f+nu+2,f+nu+1))
    falls=_mesh('WATER_Broken_Sandstone_Ledge_Cascades',all_verts,all_faces,_cascade_material(mat),coll,True)
    _periodic_surface(falls,all_params,.011,4)
    thickness=falls.modifiers.new('Thin falling water','SOLIDIFY');thickness.thickness=.008
    falls['flow_groups']=len(stream_groups)
    # Narrow strands at the lip and fan-shaped foam traces grounded on the impact water.
    foamverts=[];foamfaces=[];foamparams=[]
    for i in range(170):
        group=rng.choice(stream_groups);c=rng.gauss(group[0]+group[3],group[1]*.30)
        origin=b+n*c+d*rng.uniform(.15,2.0)
        width=rng.uniform(.016,.070); length=rng.uniform(.12,.65)
        start=len(foamverts)
        for j in range(7):
            t=j/6; center=origin+d*(t*length)+n*.07*math.sin(t*5+i)
            dist,_,zz,ww,_=_river_near(center.x,center.y,river)
            for side in (-1,1):
                point=center+n*side*width*.5*math.sin(math.pi*(.08+.84*t))
                foamverts.append((point.x,point.y,zz+.025));foamparams.append((i*.72+t*3,c,.8))
            if j<6:
                k=start+j*2;foamfaces.append((k,k+1,k+3,k+2))
    foam=_mesh('WATER_Impact_Foam_Rivulets',foamverts,foamfaces,ctx.mats['foam'],coll,True)
    _periodic_surface(foam,foamparams,.012,1.9)
    foam['placement']='on impact pool, never uniformly over calm upper water'
    # Open arcs and dispersed elongated spume marks expand from actual impact packets.
    rv=[];rf=[];rp=[]
    for i in range(115):
        group=rng.choice(stream_groups);cross=group[0]+group[3]+rng.uniform(-group[1]*.45,group[1]*.45)
        center=b+n*cross+d*rng.uniform(.18,1.3);radius=rng.uniform(.10,.57);theta0=rng.uniform(0,TAU)
        segments=rng.randint(5,10);sweep=rng.uniform(.6,1.7);width=rng.uniform(.007,.024);start=len(rv)
        for j in range(segments+1):
            theta=theta0+sweep*j/segments
            for side in (-1,1):
                q=center+n*math.cos(theta)*(radius+side*width)+d*math.sin(theta)*(radius+side*width)*.55
                z=_river_near(q.x,q.y,river)[2]+.018
                rv.append((q.x,q.y,z));rp.append((i*.6+theta,cross,.6))
            if j<segments:
                f=start+j*2;rf.append((f,f+1,f+3,f+2))
    rings=_mesh('WATER_Dispersed_Impact_Arcs',rv,rf,ctx.mats['foam'],coll,True);_periodic_surface(rings,rp,.009,2.5)
    # Advect small foam traces downstream. Each is faded to zero at its local wrap,
    # with periods dividing 240 frames; motion never reverses up the creek.
    for i in range(55):
        width=rng.uniform(.014,.055);length=rng.uniform(.14,.44)
        vv=[(-width*.35,-length*.5,0),(width*.35,-length*.5,0),(width*.5,length*.15,.004),
            (0,length*.5,0),(-width*.5,length*.15,.004)]
        patch=_mesh(f'WATER_Downstream_Advecting_Foam_{i:02}',vv,[(0,1,2,3,4)],ctx.mats['foam'],coll,True)
        group=rng.choice(stream_groups);c=group[0]+group[3]+rng.uniform(-group[1]*.5,group[1]*.5);origin=b+n*c+d*rng.uniform(.05,.8)
        _,_,zz,_,_=_river_near(origin.x,origin.y,river)
        patch.location=(origin.x,origin.y,zz+.035)
        patch.rotation_euler.z=math.atan2(d.y,d.x)-math.pi*.5
        period=rng.choice((48,60,80));phase=rng.randrange(period);travel=rng.uniform(1.7,3.1)
        expr=f'(((frame-1+{phase})%{period})/{period})'
        for axis,originvalue,delta in ((0,origin.x,d.x*travel),(1,origin.y,d.y*travel)):
            patch.driver_add('location',axis).driver.expression=f'{originvalue:.8f}+{delta:.8f}*{expr}'
        heights=[_river_near(origin.x+d.x*travel*k/4,origin.y+d.y*travel*k/4,river)[2]+.023 for k in range(5)]
        zexpr=f'{heights[0]:.8f}'+''.join(f'+({heights[k+1]-heights[k]:.8f})*min(1,max(0,4*{expr}-{k}))' for k in range(4))
        patch.driver_add('location',2).driver.expression=zexpr
        for axis in (0,1,2):patch.driver_add('scale',axis).driver.expression=f'sin(3.14159265358979*{expr})'
        patch['animation_method']='downstream constant velocity with concealed zero-scale periodic wrap'
    # Small falling droplets use local looping displacement; motion is periodic without teleportation.
    dv=[];df=[];dp=[]
    for i in range(110):
        t=rng.uniform(.35,.98);group=rng.choice(stream_groups);c=group[0]+group[3]*t+rng.uniform(-group[1]*.55,group[1]*.55)
        p=a.lerp(b,t)+n*c+d*rng.uniform(.10,.40);p.z=a.z+(b.z-a.z)*t**1.25
        r=rng.uniform(.008,.022);h=rng.uniform(.025,.070);off=len(dv)
        dv.extend([(p.x-r,p.y,p.z),(p.x,p.y-r,p.z),(p.x+r,p.y,p.z),(p.x,p.y+r,p.z),(p.x,p.y,p.z+h),(p.x,p.y,p.z-h)])
        df.extend([(off+4,off+j,off+(j+1)%4) for j in range(4)]+[(off+5,off+(j+1)%4,off+j) for j in range(4)])
        dp.extend([(t*12+i*.83,c,.65)]*6)
    droplets=_mesh('WATER_Aerated_Droplets',dv,df,mat,coll,True);_periodic_surface(droplets,dp,.12,2)
    return {'water_objects':60,'loop_frames':[1,241],'duration_seconds':10,'continuous_water_vertices':len(vertices),'cascade_flow_groups':len(stream_groups),'foam_rivulets':170,'impact_arcs':115,'advecting_foam_traces':55}


def _tube(vertices, faces, a, b, r0, r1, sides=7):
    a,b=Vector(a),Vector(b);delta=b-a
    if delta.length<1e-5:return
    axis=delta.normalized();u=axis.cross(Vector((0,0,1)))
    if u.length<.05:u=axis.cross(Vector((0,1,0)))
    u.normalize();v=axis.cross(u).normalized();base=len(vertices)
    for center,radius in ((a,r0),(b,r1)):
        for j in range(sides):vertices.append(tuple(center+radius*(math.cos(j*TAU/sides)*u+math.sin(j*TAU/sides)*v)))
    for j in range(sides):faces.append((base+j,base+(j+1)%sides,base+(j+1)%sides+sides,base+j+sides))
    faces.append(tuple(base+j for j in reversed(range(sides))))
    faces.append(tuple(base+sides+j for j in range(sides)))


def _leaf(verts,faces,indices,center,direction,length,width,rng,mat_index=None):
    u=Vector(direction).normalized();normal=Vector((rng.uniform(-.28,.28),rng.uniform(-.28,.28),rng.uniform(.55,1))).normalized()
    v=normal.cross(u)
    if v.length<.001:v=Vector((1,0,0))
    v.normalize();p=Vector(center);base=len(verts)
    # Lanceolate six-triangle leaf with raised midrib: readable from above and below.
    outline=[p-u*length*.4,p-u*length*.12-v*width*.45,p+u*length*.25-v*width*.34,p+u*length*.6,
             p+u*length*.25+v*width*.34,p-u*length*.12+v*width*.45]
    verts.extend(tuple(q) for q in outline);verts.append(tuple(p+normal*length*.05))
    for j in range(6):faces.append((base+6,base+j,base+(j+1)%6))
    material=mat_index if mat_index is not None else rng.choices([0,1,2],[.57,.28,.15])[0]
    indices.extend([material]*6)


def _data_mesh(name,vertices,faces,materials,indices=None):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
    for m in materials:mesh.materials.append(m)
    if 'Branches' in name or 'Stems' in name:
        for polygon in mesh.polygons:polygon.use_smooth=True
    if indices:
        for poly,idx in zip(mesh.polygons,indices):poly.material_index=idx
    if 'Leaves' in name:
        uv=mesh.uv_layers.new(name='Individual leaf surface')
        coords=[(0,.5),(.28,.05),(.68,.16),(1,.5),(.68,.84),(.28,.95),(.44,.5)]
        for polygon in mesh.polygons:
            for li in polygon.loop_indices:uv.data[li].uv=coords[mesh.loops[li].vertex_index%7]
    return mesh


def _leaf_material(ctx,key):
    name='FW_Site_Textured_'+key
    if bpy.data.materials.get(name):return bpy.data.materials[name]
    mat=ctx.mats[key].copy();mat.name=name
    ns,ls=mat.node_tree.nodes,mat.node_tree.links;p=ns.get('Principled BSDF')
    p.inputs['Roughness'].default_value=.56
    uv=ns.new('ShaderNodeTexCoord');sep=ns.new('ShaderNodeSeparateXYZ');ls.new(uv.outputs['UV'],sep.inputs[0])
    shift=ns.new('ShaderNodeMath');shift.operation='SUBTRACT';shift.inputs[1].default_value=.5;ls.new(sep.outputs['Y'],shift.inputs[0])
    ab=ns.new('ShaderNodeMath');ab.operation='ABSOLUTE';ls.new(shift.outputs[0],ab.inputs[0])
    vein=ns.new('ShaderNodeMath');vein.operation='LESS_THAN';vein.inputs[1].default_value=.015;ls.new(ab.outputs[0],vein.inputs[0])
    micro=ns.new('ShaderNodeTexNoise');micro.inputs['Scale'].default_value=42;micro.inputs['Detail'].default_value=2;ls.new(uv.outputs['UV'],micro.inputs['Vector'])
    bump=ns.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.24;bump.inputs['Distance'].default_value=.0007;ls.new(vein.outputs[0],bump.inputs['Height']);ls.new(bump.outputs[0],p.inputs['Normal'])
    base=tuple(mat.diffuse_color);ramp=ns.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color=tuple(v*.72 for v in base[:3])+(1,)
    ramp.color_ramp.elements[1].color=tuple(v*1.16 for v in base[:3])+(1,)
    ls.new(micro.outputs['Fac'],ramp.inputs[0]);ls.new(ramp.outputs['Color'],p.inputs['Base Color'])
    translucent=ns.new('ShaderNodeBsdfTranslucent');translucent.inputs['Color'].default_value=tuple(min(.75,v*1.85) for v in base[:3])+(1,)
    mix=ns.new('ShaderNodeMixShader');mix.inputs[0].default_value=.30;ls.new(p.outputs[0],mix.inputs[1]);ls.new(translucent.outputs[0],mix.inputs[2]);ls.new(mix.outputs[0],ns.get('Material Output').inputs['Surface'])
    return mat


def _tree_asset(ctx, rng, index, detail=True, small=False):
    barkv, barkf, leafv, leaff, indices = [], [], [], [], []
    H = rng.uniform(12.0, 19.0) if not small else rng.uniform(4.2, 7.6)
    radius = H * rng.uniform(.018, .024)
    fork_height = H * rng.uniform(.22, .34) if not small else H * rng.uniform(.15, .25)
    fork_count = rng.choice((3, 4)) if not small else rng.choice((2, 3))
    drift = Vector((rng.uniform(-.55, .55), rng.uniform(-.48, .48), 0))
    turn = rng.uniform(0, TAU)

    def curve(a, b, c, t):
        return a * ((1-t)**2) + b * (2*t*(1-t)) + c * (t*t)

    def woody_curve(a, b, c, start_radius, end_radius, segments, sides):
        # One ring is shared across each adjacent pair of segments. The frame
        # follows the curve by its minimum tangent rotation, avoiding the
        # independently capped cylinders and visible staircase collars.
        first = len(barkv)
        previous_tangent = None
        normal = None
        for n in range(segments+1):
            t = n / segments
            point = curve(a, b, c, t)
            tangent = (2*(1-t)*(b-a) + 2*t*(c-b)).normalized()
            if tangent.length < 1e-6:
                tangent = (c-a).normalized()
            if previous_tangent is None:
                helper = Vector((0, 0, 1)) if abs(tangent.z) < .9 else Vector((0, 1, 0))
                normal = tangent.cross(helper).normalized()
            else:
                normal = previous_tangent.rotation_difference(tangent) @ normal
                normal = (normal-tangent*normal.dot(tangent)).normalized()
            binormal = tangent.cross(normal).normalized()
            radius_here = end_radius+(start_radius-end_radius)*((1-t)**1.12)
            for j in range(sides):
                angle = j*TAU/sides
                barkv.append(tuple(point+radius_here*(normal*math.cos(angle)+binormal*math.sin(angle))))
            if n:
                lower = first+(n-1)*sides
                upper = first+n*sides
                for j in range(sides):
                    after = (j+1)%sides
                    barkf.append((lower+j, lower+after, upper+after, upper+j))
            previous_tangent = tangent
        # Caps exist only at the two ends of the whole continuous curve.
        barkf.append(tuple(first+j for j in reversed(range(sides))))
        barkf.append(tuple(first+segments*sides+j for j in range(sides)))

    # A short, bending bole ends at the crotch. There is NO upright central
    # leader continuing to the crown tip, and no spiral of radial branch tiers.
    base = Vector((0, 0, 0))
    crotch = drift + Vector((0, 0, fork_height+H*.08))
    bend = drift * -.28 + Vector((rng.uniform(-.18, .18), rng.uniform(-.18, .18), crotch.z*.46))
    woody_curve(base, bend, crotch, radius*1.16, radius*.48, 12, 14 if detail else 11)
    for root in range(6):
        theta = turn + root*TAU/6 + rng.uniform(-.32, .32)
        spread = radius*rng.uniform(3.7, 6.1)
        end = Vector((math.cos(theta)*spread, math.sin(theta)*spread, .015))
        elbow = end*.48 + Vector((0, 0, radius*.24))
        woody_curve(base+Vector((0, 0, radius*.70)), elbow, end,
                    radius*rng.uniform(.25, .41), .013, 3, 7 if detail else 5)

    # Different crown heights, unequal horizontal reach and unequal branch
    # thickness keep the lobes asymmetric. One lobe sets the reported height.
    lobes = []
    tallest = rng.randrange(fork_count)
    first_fork_actual = H
    for j in range(fork_count):
        theta = turn + j*TAU/fork_count + rng.uniform(-.45, .45)
        radial = Vector((math.cos(theta), math.sin(theta), 0))
        tangent = Vector((-radial.y, radial.x, 0))
        reach = H*rng.uniform(.22, .34) * (.92 if small else 1)
        top = H*(.915 if j == tallest else rng.uniform(.69, .88))
        # Unequal insertion heights avoid several equal limbs meeting as a Y.
        insertion = .67 + .29*j/max(1, fork_count-1) + rng.uniform(-.035, .025)
        attachment = curve(base, bend, crotch, insertion)
        first_fork_actual = min(first_fork_actual, attachment.z)
        parent_radius = radius*.48+(radius*1.16-radius*.48)*((1-insertion)**1.12)
        # Sink the start and its end cap inside the parent bole.
        fork_start = attachment-radial*parent_radius*.30
        endpoint = attachment + radial*reach + tangent*rng.uniform(-.8, .8)
        endpoint.z = top
        control = attachment + radial*reach*rng.uniform(.20, .52)
        control += tangent*rng.uniform(-.55, .55)
        control.z = attachment.z+(top-attachment.z)*rng.uniform(.37, .63)
        branch_radius = min(parent_radius*.86, radius*rng.uniform(.70, .91)/math.sqrt(fork_count))
        woody_curve(fork_start, control, endpoint, branch_radius, .016 if not small else .007,
                    11 if detail else 8, 12 if detail else 9)
        lobes.append((fork_start, control, endpoint, radial, tangent, branch_radius))

    scaffold_count = 8 if detail and not small else (6 if small else 7)
    shoot_count = 9 if detail and not small else 6
    twig_count = 3 if detail and not small else 2
    leaf_nodes = 12 if detail and not small else 10
    # Maximum detailed case: 4 * 8 * 9 * 3 * 12 * 2 = 20,736 leaves.
    # Maximum far case: 4 * 7 * 6 * 2 * 10 * 2 = 6,720 leaves.
    for a, b, c, radial, tangent, fork_radius in lobes:
        for k in range(scaffold_count):
            t = .20 + .77*(k+rng.uniform(.08, .87))/scaffold_count
            start = curve(a, b, c, t)
            # Unordered local directions, rather than golden-angle trunk whorls.
            yaw = rng.uniform(-2.5, 2.5)
            direction = radial*math.cos(yaw) + tangent*math.sin(yaw)
            span = H*rng.uniform(.105, .175) * (.98 if small else 1)
            # Crown shoulders remain broad at the top; no conical falloff.
            end = start + direction*span + Vector((0, 0, span*rng.uniform(-.09, .35)))
            end.z = min(end.z, H*.94)
            elbow = start.lerp(end, .50) + tangent*rng.uniform(-.25, .25)
            elbow.z -= span*rng.uniform(.02, .12)
            parent_radius = .016+(fork_radius-.016)*((1-t)**1.12)
            r0 = max(.014, parent_radius*rng.uniform(.27, .43))
            buried_start = start-direction*parent_radius*.45
            woody_curve(buried_start, elbow, end, r0, .007 if not small else .003,
                        5, 8 if detail else 6)
            along = (end-start).normalized()
            across = Vector((-along.y, along.x, 0)).normalized()
            for s in range(shoot_count):
                u = rng.uniform(.26, .99)
                origin = curve(start, elbow, end, u)
                side = -1 if s % 2 else 1
                shoot_dir = (along*rng.uniform(.22, .70) + across*side*rng.uniform(.35, .95)
                             + Vector((0, 0, rng.uniform(-.18, .58)))).normalized()
                shoot_length = rng.uniform(.70, 1.28)*(H/15 if not small else H/6*.76)
                shoot_end = origin + shoot_dir*shoot_length
                # Leafy fans have distinct nodal shoots and twigs, not filled
                # sphere meshes or scattered leaves floating around a volume.
                shoot_mid = origin.lerp(shoot_end, .50) + Vector((0, 0, -.045*shoot_length))
                woody_curve(origin, shoot_mid, shoot_end, .007 if not small else .004,
                            .0027 if not small else .0017, 2, 5 if detail else 4)
                local_side = Vector((-shoot_dir.y, shoot_dir.x, 0)).normalized()
                for q in range(twig_count):
                    v = .36 + .62*(q+rng.uniform(.15, .85))/twig_count
                    twig_start = curve(origin, shoot_mid, shoot_end, v)
                    sign = -1 if q % 2 else 1
                    twig_dir = (shoot_dir*.47 + local_side*sign*rng.uniform(.40, .90)
                                + Vector((0, 0, rng.uniform(-.32, .40)))).normalized()
                    length = rng.uniform(.44, .69)*(H/15 if not small else H/6*.95)
                    twig_end = twig_start + twig_dir*length
                    _tube(barkv, barkf, twig_start, twig_end,
                          .0031 if not small else .0021, .00085, 4)
                    leaf_axis = Vector((-twig_dir.y, twig_dir.x, 0)).normalized()
                    for n in range(leaf_nodes):
                        w = (n+.30+rng.uniform(0, .22))/leaf_nodes
                        node = twig_start.lerp(twig_end, w)
                        for sign in (-1, 1):
                            leaf_dir = (leaf_axis*sign + twig_dir*rng.uniform(.15, .70)
                                        + Vector((0, 0, rng.uniform(-.43, .26)))).normalized()
                            # 11–19 cm blades in the detailed forest. Background
                            # blades remain below 22 cm rather than giant cards.
                            leaf_length = rng.uniform(.11, .19)*(1 if detail else 1.12)
                            if small:
                                leaf_length *= .88
                            petiole = node + twig_dir*rng.uniform(-.025, .025)
                            center = petiole + leaf_dir*leaf_length*.39
                            _leaf(leafv, leaff, indices, center, leaf_dir, leaf_length,
                                  leaf_length*rng.uniform(.65, .88), rng)

    bark = _data_mesh(f'TREE_Asset_{index}_Woody_Branches', barkv, barkf, [ctx.mats['bark']])
    for polygon in bark.polygons:
        polygon.use_smooth = True
    foliage = _data_mesh(f'TREE_Asset_{index}_Individual_Leaves', leafv, leaff,
                        [_leaf_material(ctx, key) for key in ('leaf', 'leaf_dark', 'leaf_light')], indices)
    # Useful both for integration QA and asset-budget inspection.
    bark['growth_form'] = 'forked broadleaf: irregular branch-supported crown lobes'
    bark['major_forks'] = fork_count
    bark['first_fork_height_m'] = first_fork_actual
    bark['branch_mesh_method'] = 'continuous shared rings with minimum-rotation frames; end caps only'
    foliage['individual_leaf_count'] = len(leafv)//7
    foliage['vertex_budget_including_bark'] = len(leafv)+len(barkv)
    foliage['no_foliage_blobs'] = True
    actual_height = max(vertex[2] for vertex in barkv + leafv)
    return bark, foliage, actual_height


def _plant_asset(ctx,rng,index,fern=False):
    verts=[];faces=[];indices=[];bv=[];bf=[]
    if fern:
        for j in range(9):
            a=j*2.39996;length=rng.uniform(.45,.88);direction=Vector((math.cos(a),math.sin(a),0))
            last=Vector((0,0,.02))
            for k in range(11):
                t=(k+1)/11;p=direction*length*t+Vector((0,0,math.sin(math.pi*t*.82)*length*.6))
                _tube(bv,bf,last,p,.006*(1-t*.7),.003*(1-t*.7),4);last=p
                for side in (-1,1):
                    v=Vector((-direction.y,direction.x,0))*side+direction*.35
                    L=length*.28*math.sin(math.pi*(.10+.87*t))
                    _leaf(verts,faces,indices,p+v*L*.32,v,L,L*.20,rng,0)
    else:
        for j in range(13):
            a=j*2.39996;h=rng.uniform(.35,1.45);end=Vector((math.cos(a)*h*.35,math.sin(a)*h*.35,h))
            _tube(bv,bf,(0,0,0),end,.014,.003,5)
            for k in range(7):
                t=.2+k*.105;p=end*t;dir=Vector((math.cos(a+k*2.4),math.sin(a+k*2.4),.12))
                L=rng.uniform(.12,.22)
                _leaf(verts,faces,indices,p+dir*L*.25,dir,L,L*.49,rng)
    return (_data_mesh(f'TREE_Understory_{index}_Stems',bv,bf,[ctx.mats['bark']]),
            _data_mesh(f'TREE_Understory_{index}_Leaves',verts,faces,[_leaf_material(ctx,k) for k in ('leaf','leaf_dark','leaf_light')],indices))


def _instance(ctx,name,asset,location,angle,scale,coll):
    objects=[]
    for suffix,mesh in zip(('Branches','Leaves'),asset[:2]):
        obj=bpy.data.objects.new(name+'_'+suffix,mesh);coll.objects.link(obj)
        obj.location=location;obj.rotation_euler.z=angle;obj.scale=scale
        _owned(obj,'linked-mesh vegetation '+suffix.lower());obj['plant_asset']=mesh.name
        objects.append(obj)
    return objects


def _far_tree_lod(ctx,asset,index,coll):
    """Distance-only leaf and branch reduction, retaining the source crown outline."""
    source_bark,source_leaves,height=asset
    temp=bpy.data.objects.new(f'SITE_Temporary_LOD_{index}',source_bark);coll.objects.link(temp)
    modifier=temp.modifiers.new('Distance branch simplification','DECIMATE');modifier.ratio=.22
    deps=bpy.context.evaluated_depsgraph_get()
    bark=bpy.data.meshes.new_from_object(temp.evaluated_get(deps));bark.name=f'TREE_DistantLOD_{index}_Branches'
    bpy.data.objects.remove(temp,do_unlink=True)
    for polygon in bark.polygons:polygon.use_smooth=True
    vertices=[];faces=[];indices=[]
    for group in range(0,len(source_leaves.vertices)//7,2):
        center=source_leaves.vertices[group*7+6].co
        start=len(vertices)
        for corner in (0,1,3,5):
            vertices.append(tuple(center+(source_leaves.vertices[group*7+corner].co-center)*1.35))
        faces.extend([(start,start+1,start+2),(start,start+2,start+3)])
        indices.extend([source_leaves.polygons[group*6].material_index]*2)
    leaves=_data_mesh(f'TREE_DistantLOD_{index}_Canopy',vertices,faces,list(source_leaves.materials),indices)
    uv=leaves.uv_layers.new(name='Distance leaf surfaces');coords=[(0,.5),(.42,.06),(1,.5),(.42,.94)]
    for poly in leaves.polygons:
        for loop in poly.loop_indices:uv.data[loop].uv=coords[leaves.loops[loop].vertex_index%4]
    leaves['lod_minimum_distance_m']=85;leaves['source_crown_mesh']=source_leaves.name
    return bark,leaves,height


def _distant_forest(ctx,cfg,rng,coll,far,saplings,allowed):
    settings=cfg.get('distant_environment',{})
    if not settings:return {}
    lod=[_far_tree_lod(ctx,asset,index,coll) for index,asset in enumerate(far[:3])]
    count=0;ring_counts=[];positions=[]
    for ring_index,ring in enumerate(settings['forest_rings']):
        outer=ring['max'];inner=ring['min'];spacing=ring['spacing'];actual=0
        columns=math.ceil(outer*2/spacing)
        for row in range(columns+1):
            for col in range(columns+1):
                x=-outer+col*spacing+rng.uniform(-.43,.43)*spacing
                y=-outer+row*spacing+rng.uniform(-.43,.43)*spacing
                radius=math.hypot(x-5,y-10)
                if not inner<radius<outer or not allowed(x,y,1.5,True):continue
                if rng.random()<.075:continue
                s=rng.uniform(*ring.get('scale',[.85,1.24]));height=_height(x,y,cfg)
                objs=_instance(ctx,f'TREE_Distance_Ring{ring_index}_{actual:04}',lod[(row+col)%len(lod)],(x,y,height),rng.uniform(0,TAU),(s,s,s*rng.uniform(.85,1.12)),coll)
                for obj in objs:obj['distance_level']=ring_index+1;obj['evidence']='C distant authored forest, not individual tree survey'
                positions.append((x,y,height));actual+=1;count+=1
        ring_counts.append(actual)
    # A lower woodland layer outside measured rooms closes bright gaps beneath
    # distant tall crowns while preserving every existing near landmark tree.
    slope_count=0
    for attempt in range(settings.get('understory_additions',0)*50):
        if slope_count>=settings.get('understory_additions',0):break
        x=rng.uniform(-48,67);y=rng.uniform(-34,88)
        if not allowed(x,y,1.05,True):continue
        if math.hypot(x-5,y-10)<18:continue
        s=rng.uniform(.75,1.22)
        _instance(ctx,f'TREE_Slope_Understory_{slope_count:03}',saplings[slope_count%len(saplings)],(x,y,_height(x,y,cfg)),rng.uniform(0,TAU),(s,s,s),coll)
        slope_count+=1
    return {'distant_tree_instances':count,'distant_forest_ring_counts':ring_counts,'distant_tree_lod_assets':len(lod),
            'slope_understory_tree_instances':slope_count,'distant_forest_positions':positions,
            'distant_evidence':'C authored valley/forest continuation; 85m+ tree LOD approximates leaf density, not exact individual trees'}


def _upstream_background(ctx,cfg):
    """Only remote water continuation beyond x=90m; core water code is untouched."""
    path=cfg.get('river_upstream_extension',[])
    if len(path)<2:return 0
    verts=[];faces=[];width_segments=10;rows=[]
    for a,b in zip(path,path[1:]):
        steps=max(2,math.ceil(math.hypot(b[0]-a[0],b[1]-a[1])/2.2))
        for k in range(steps):
            t=k/steps;rows.append(tuple(a[j]+(b[j]-a[j])*t for j in range(4)))
    rows.append(tuple(path[-1]))
    for index,p in enumerate(rows):
        a=rows[max(0,index-1)];b=rows[min(len(rows)-1,index+1)];dx,dy=b[0]-a[0],b[1]-a[1];d=math.hypot(dx,dy);nx,ny=-dy/d,dx/d
        for k in range(width_segments+1):
            cross=(k/width_segments-.5)*p[3]
            verts.append((p[0]+nx*cross,p[1]+ny*cross,p[2]+.004*math.sin(index*.57+k*.6)))
    for i in range(len(rows)-1):
        for j in range(width_segments):
            q=i*(width_segments+1)+j;faces.append((q,q+width_segments+1,q+width_segments+2,q+1))
    source=bpy.data.objects.get('WATER_BearRun_Continuous_Upstream_Downstream')
    mat=source.data.materials[0] if source else ctx.mats['water']
    obj=_mesh('SITE_Remote_Upstream_Creek_Continuation',verts,faces,mat,ctx.collection('60_WATER'),True)
    obj['role']='C distant upstream extension beyond original 90m edge; core waterfall unchanged'
    return len(verts)


def _vegetation(ctx,cfg,rng,coll):
    forest=cfg['forest'];library=Path(ctx.root)/cfg.get('near_tree_library','assets/models/site_near_trees.blend')
    if cfg.get('preserved_vegetation') and library.exists():
        with bpy.data.libraries.load(str(library),link=False) as (src,dst):
            dst.meshes=[n for n in src.meshes if n.startswith('TREE_Asset_')]
        assets=[]
        for index in range(9):
            bark=bpy.data.meshes[f'TREE_Asset_{index}_Woody_Branches']
            leaves=bpy.data.meshes[f'TREE_Asset_{index}_Individual_Leaves']
            bark.materials.clear();bark.materials.append(ctx.mats['bark'])
            leaves.materials.clear()
            for key in ('leaf','leaf_dark','leaf_light'):leaves.materials.append(_leaf_material(ctx,key))
            assets.append((bark,leaves,max(v.co.z for v in leaves.vertices)))
        near,far,saplings=assets[:3],assets[3:7],assets[7:]
    else:
        near=[_tree_asset(ctx,rng,i,True) for i in range(3)]
        far=[_tree_asset(ctx,rng,i+3,False) for i in range(4)]
        saplings=[_tree_asset(ctx,rng,i+7,False,True) for i in range(2)]
    plants=[_plant_asset(ctx,rng,i,i<2) for i in range(4)]
    placed=[]
    def allowed(x,y,radius=1,tree=False):
        if any(_inside(x,y,z['bbox'],radius+1.0) for z in cfg['building_exclusions']):return False
        if _inside(x,y,cfg['bridge']['bbox'],2):return False
        dist,_,wz,width,_=_river_near(x,y,cfg.get('_terrain_river_path',cfg['river_path']))
        if dist<width*.5+radius*.75:return False
        for route in cfg['paths']:
            for a,b in zip(route['points'],route['points'][1:]):
                if _segment_near(x,y,a,b)[0]<route['width']*.5+radius:return False
        if tree:
            # Preserve the documented open downstream lookout and clear the camera
            # volume; no clipping of leaf cards or branches through the lens.
            if _segment_near(x,y,(-27,-30),(1,-1))[0]<6.8:return False
            if _segment_near(x,y,(-8,-14),(4,-1))[0]<4.4:return False
        return True
    # Landmark trunks form the creek-side frame without blocking the architectural core.
    landmarks=[(-9.8,7.0,1.02),(-12.5,18.5,1.08),(21.5,18.3,1.12),
               (24,-13.0,1.0),(-21.0,-4.0,1.18),(41.0,10.0,1.13),(-14.0,29.0,.95)]
    preserved=cfg.get('preserved_vegetation',[])
    if preserved:
        all_assets=near+far+saplings
        for entry in preserved:
            _instance(ctx,entry['name'],all_assets[entry['asset']],entry['location'],entry['angle'],entry['scale'],coll)
            placed.append(tuple(entry['location'][:2]))
    else:
        for i,(x,y,s) in enumerate(landmarks):
            if allowed(x,y,.8,True):
                _instance(ctx,f'TREE_Landmark_{i:02}',near[i%3],(x,y,_height(x,y,cfg)),rng.uniform(0,TAU),(s,s,s),coll);placed.append((x,y))
    for mode,count,assets in [('Near',forest['near_tree_count'],near),('Far',forest['far_tree_count'],far),('Sapling',forest['sapling_count'],saplings)]:
        if preserved and mode in ('Near','Sapling'):continue
        actual=0;attempt=0
        while actual<count and attempt<count*90:
            attempt+=1
            if mode=='Near':x=rng.uniform(-38,52);y=rng.uniform(-28,61)
            elif mode=='Far':x=rng.uniform(-84,95);y=rng.uniform(-70,101)
            else:x=rng.uniform(-42,58);y=rng.uniform(-33,69)
            # Leave the classical downstream view open as in the reference clearing.
            if -29<x<5 and -33<y<-11 and mode!='Sapling':continue
            if mode=='Far' and -34<x<48 and -26<y<62:continue
            radius=.45 if mode=='Sapling' else 2.8
            if not allowed(x,y,radius,True):continue
            if any(math.hypot(x-px,y-py)<(1.45 if mode=='Sapling' else 3.15) for px,py in placed):continue
            s=rng.uniform(.82,1.17);asset=assets[actual%len(assets)]
            _instance(ctx,f'TREE_{mode}_{actual:03}',asset,(x,y,_height(x,y,cfg)),rng.uniform(0,TAU),(s*rng.uniform(.88,1.10),s,s*rng.uniform(.90,1.1)),coll)
            placed.append((x,y));actual+=1
    under=0
    for k in range(forest['understory_count']*10):
        if under>=forest['understory_count']:break
        x=rng.uniform(-36,54);y=rng.uniform(-26,70)
        if not allowed(x,y,.25):continue
        s=rng.uniform(.68,1.45)
        _instance(ctx,f'TREE_Understory_{under:04}',plants[under%len(plants)],(x,y,_height(x,y,cfg)+.012),rng.uniform(0,TAU),(s,s,s),coll);under+=1
    ground=_groundcover(ctx,cfg,rng,coll,allowed)
    distant=_distant_forest(ctx,cfg,rng,coll,far,saplings,allowed)
    return {'linked_tree_instances':len(placed),'understory_instances':under,'tree_mesh_assets':9,'understory_mesh_assets':4,
            'leaf_geometry':'forked broadleaf crowns on curved branches and twigs; individual UV-mapped six-triangle leaves, no spherical crowns',
            'tree_positions':placed,'preserved_near_tree_instances':len(preserved),**ground,**distant}


def _groundcover(ctx,cfg,rng,coll,allowed):
    # Thin, topography-following moss patches and clustered old broadleaf litter.
    # Both are real ground surfaces, not billboards or rounded foliage masses.
    mv=[];mf=[];lv=[];lf=[];li=[];moss_count=0;leaf_count=0
    for i in range(1350):
        x=rng.uniform(-33,47);y=rng.uniform(-22,61)
        if not allowed(x,y,.05):continue
        radius=rng.uniform(.24,.92)
        # Moss is low living filament geometry rather than a flat green polygon
        # visibly pasted over the photographed forest-floor surface.
        for tuft in range(20):
            a=rng.uniform(0,TAU);r=radius*math.sqrt(rng.random())
            xx=x+math.cos(a)*r;yy=y+math.sin(a)*r*.7;zz=_height(xx,yy,cfg)+.003
            for blade in range(3):
                direction=rng.uniform(0,TAU);w=rng.uniform(.008,.018);h=rng.uniform(.016,.052)
                offset=len(mv);dx=math.cos(direction);dy=math.sin(direction)
                mv.extend([(xx-dy*w*.5,yy+dx*w*.5,zz),(xx+dy*w*.5,yy-dx*w*.5,zz),(xx+dx*h*.35,yy+dy*h*.35,zz+h)])
                mf.append((offset,offset+1,offset+2))
        moss_count+=1
    moss=_mesh('TREE_Forest_Floor_Moss_Patches',mv,mf,ctx.mats['moss'],coll,True)
    for cluster in range(520):
        x=rng.uniform(-29,43);y=rng.uniform(-20,54)
        if not allowed(x,y,.04):continue
        radius=rng.uniform(.35,1.15)
        for j in range(28):
            xx=x+rng.uniform(-radius,radius);yy=y+rng.uniform(-radius,radius)
            if not allowed(xx,yy,.01):continue
            angle=rng.uniform(0,TAU);length=rng.uniform(.075,.155)
            center=(xx,yy,_height(xx,yy,cfg)+.024)
            _leaf(lv,lf,li,center,(math.cos(angle),math.sin(angle),rng.uniform(-.06,.08)),length,length*.65,rng)
            leaf_count+=1
    materials=[]
    for i,color in enumerate(((.115,.075,.025),(.067,.044,.021),(.18,.13,.059))):
        mat=ctx.mats['earth'].copy();mat.name=f'FW_Weathered_Forest_Litter_{i}'
        p=mat.node_tree.nodes.get('Principled BSDF')
        for link in list(p.inputs['Base Color'].links):mat.node_tree.links.remove(link)
        p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.87;materials.append(mat)
    litter=_data_mesh('TREE_Fallen_Leaves_Ground_Litter',lv,lf,materials,li)
    obj=bpy.data.objects.new('TREE_Fallen_Leaves_Ground_Litter',litter);coll.objects.link(obj);_owned(obj,'fallen weathered leaf litter')
    return {'moss_ground_patches':moss_count,'fallen_leaf_meshes':leaf_count}


def _resolve_guest(ctx,cfg):
    """Honor current guest registration and avoid cutting a huge provisional hollow."""
    guest_path=Path(ctx.root)/'data'/'guest_house.json'
    if not guest_path.exists():return
    data=json.loads(guest_path.read_text(encoding='utf-8'));reg=dict(data['registration'])
    reg.update(ctx.config.get('guest_registration',{}))
    ox,oy,oz=reg['world_origin'];px,py=reg['origin_px'];sx,sy=reg['meters_per_pixel']
    cfg['building_exclusions']=[z for z in cfg['building_exclusions'] if not z['name'].startswith('guest')]
    for room in data['rooms']:
        points=[(ox+(p[0]-px)*sx,oy+(py-p[1])*sy) for p in room['polygon']]
        xs=[p[0] for p in points];ys=[p[1] for p in points]
        offset=data['levels'][room['level']]['offset']
        cap=oz+offset-.32
        if room['kind']=='pool':cap=oz-1.45
        cfg['building_exclusions'].append({'name':'guest_'+room['id'],'bbox':[min(xs)-.15,max(xs)+.15,min(ys)-.15,max(ys)+.15],'ground_cap':cap})
    # Canopy is owned by guest module; only a narrow under-route tree exclusion is needed.
    cfg['building_exclusions'].append({'name':'guest_canopy','bbox':[-5,8.4,23,oy+1],'ground_cap':oz-.7})


def _resolve_main(ctx,cfg):
    """Read final world-space room footprints, including revised kitchen bay."""
    source=Path(ctx.root)/'data'/'main_house.json'
    if not source.exists():return
    data=json.loads(source.read_text(encoding='utf-8'))
    for room in data['rooms']:
        xs=[p[0] for p in room['polygon']];ys=[p[1] for p in room['polygon']]
        cfg['building_exclusions'].append({'name':'main_final_'+room['id'],
            'bbox':[min(xs)-.12,max(xs)+.12,min(ys)-.12,max(ys)+.12],
            'ground_cap':room['z']-.32})


def _seat_vegetation(terrain,coll):
    """Ground stems on the actual triangulated surface, not the height formula."""
    deps=bpy.context.evaluated_depsgraph_get();bvh=BVHTree.FromObject(terrain,deps)
    count=0;largest=0
    for obj in coll.objects:
        if not obj.name.endswith('_Branches') or obj.get('owner')!=OWNER:continue
        hit,_,_,_=bvh.ray_cast(Vector((obj.location.x,obj.location.y,250)),Vector((0,0,-1)),500)
        if hit is None:continue
        delta=hit.z-.012-obj.location.z
        obj.location.z+=delta
        foliage=bpy.data.objects.get(obj.name[:-9]+'_Leaves')
        if foliage:foliage.location.z+=delta
        obj['terrain_contact_z_correction_m']=delta
        largest=max(largest,abs(delta));count+=1
    return {'grounded_vegetation_instances':count,'max_vegetation_seating_correction_m':largest}


def build(ctx):
    """Build site-owned objects and return a serializable, honest summary."""
    for obj in list(bpy.data.objects):
        if obj.get('owner')==OWNER:bpy.data.objects.remove(obj,do_unlink=True)
    path=Path(ctx.root)/'data'/'site.json'
    cfg=json.loads(path.read_text(encoding='utf-8'))
    cfg.update(ctx.config.get('site',{}))
    _resolve_guest(ctx,cfg)
    _resolve_main(ctx,cfg)
    # Terrain follows both remote continuations; waterfall node indexing in the
    # original water generator stays exactly the same.
    cfg['_terrain_river_path']=list(reversed(cfg.get('river_upstream_extension',[])[1:]))+cfg['river_path']
    rng=random.Random(cfg['seed'])
    sitecoll=ctx.collection('10_SITE');vegcoll=ctx.collection('50_VEGETATION');watercoll=ctx.collection('60_WATER')
    terrain=_terrain(ctx,cfg,rng,sitecoll)
    rock_count=_geology(ctx,cfg,rng,sitecoll)
    _bridge(ctx,cfg,rng,sitecoll)
    water=_water(ctx,cfg,rng,watercoll)
    remote_water_vertices=_upstream_background(ctx,cfg)
    vegetation=_vegetation(ctx,cfg,rng,vegcoll)
    seating=_seat_vegetation(terrain,vegcoll)
    summary={'module':'site','evidence':'C','seed':cfg['seed'],'terrain_vertices':len(terrain.data.vertices),
             'rock_strata_objects':rock_count,**water,**vegetation,**seating,'limitations':cfg['limitations'],
             'remote_upstream_vertices':remote_water_vertices,'terrain_bounds':cfg['terrain_bounds'],
             'near_tree_library':cfg.get('near_tree_library'),'river_near_baseline_unchanged':cfg['river_path'][:16]==cfg.get('river_near_baseline'),
             'suggested_views':cfg['suggested_views'],'visual_validation':'PENDING rendered review by scene integrator'}
    qa=Path(ctx.root)/'qa';qa.mkdir(exist_ok=True)
    (qa/'site_build.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    return summary
