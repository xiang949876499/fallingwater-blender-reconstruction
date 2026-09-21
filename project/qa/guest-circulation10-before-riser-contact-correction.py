"""Reversible guest circulation C hypothesis; independent frozen-scene adapter.

Never called by build_scene.py. apply() replaces only its explicit whitelist in
an already-loaded frozen09 scene. No production room/data/tour mutation. The
run counts, inferred platforms, rail details and absolute south datum remain C.
"""
import hashlib
import json
import math
from pathlib import Path
from types import SimpleNamespace

import bpy
from mathutils import Vector
from fwlib import collection, poly_prism, segment, beam, cylinder, window, tag, box

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA = '489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331'
PREFIX = 'GUEST_C10_'
FIXED_WALL = 'GUEST_LAUNDRY_DESCENT_outer_retaining_wall'
MUTATE_EXACT = {FIXED_WALL, 'SITE_Continuous_BearRun_Terrain',
                'GUEST_CONNECTOR_canopy_042', 'GUEST_CONNECTOR_canopy_043', 'GUEST_CONNECTOR_canopy_044'}
REMOVE_EXACT = {
    'GUEST_L1_MAIN_FLOOR', 'GUEST_L1_HALL_SOUTH', 'GUEST_L1_HALL_NORTH',
    'GUEST_B1_STAIR_LANDING', 'GUEST_L1_CHAUFFEUR_DOOR_LANDING',
    'GUEST_L2_CORRIDOR_FLOOR', 'GUEST_L2_STAIR_TOP_LANDING',
    'GUEST_L2_STAIR_PASSAGE', 'GUEST_L1_WEST_LOUNGE_jamb_1_a',
    'GUEST_L1_WEST_LOUNGE_jamb_1_b', 'GUEST_L1_WEST_LOUNGE_door_head_1',
}
REMOVE_PREFIX = ('GUEST_SERVICE_ASCENT_', 'GUEST_LAUNDRY_DESCENT_',
                 'GUEST_CONNECTOR_step_', 'GUEST_CONNECTOR_lowwall_',
                 'GUEST_CONNECTOR_support_')


def removable(name):
    return name != FIXED_WALL and (name in REMOVE_EXACT or name.startswith(REMOVE_PREFIX))


def source_point(p):
    return (3.4 + (p[0]-325)*.05256, 37.1 + (422-p[1])*.05272)


def world_point(p):
    return (*source_point(p), 8.4+p[2])


def clip(poly, axis, value, keep_less):
    """Exact straight-line half-plane partition; no boolean slivers."""
    result=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        ia=(a[axis]<=value) if keep_less else (a[axis]>=value)
        ib=(b[axis]<=value) if keep_less else (b[axis]>=value)
        if ia:result.append(list(a))
        if ia != ib:
            t=(value-a[axis])/(b[axis]-a[axis])
            result.append([a[k]+t*(b[k]-a[k]) for k in range(2)])
    return result


def apply():
    if any(o.name.startswith(PREFIX) for o in bpy.data.objects):
        raise RuntimeError('Candidate already installed: reopen pristine frozen09 before applying')
    design=json.loads((ROOT/'qa/guest-circulation10-design.json').read_text(encoding='utf-8'))
    data=json.loads((ROOT/'data/guest_house.json').read_text(encoding='utf-8'))
    col=collection('31_GUEST_CIRCULATION10_CANDIDATE')
    mats={k:bpy.data.materials['FW_'+k] for k in ('stone_floor','ochre','stone','red','glass')}
    ctx=SimpleNamespace(mats=mats)
    made=[];removed=[];flights=[];platforms=[]
    for o in list(bpy.context.scene.objects):
        if removable(o.name):
            removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
    missing=REMOVE_EXACT-set(removed)
    if missing:raise RuntimeError('Frozen source target mismatch: '+str(sorted(missing)))
    def record(o,component,reference='guest01/02/03; guest-circulation10-design.json'):
        tag(o,reference=reference,evidence='C explicit construction hypothesis',role='architecture')
        o['component_type']=component;o['candidate_only']=True;made.append(o)
        return o
    def slab(name,poly,z,th=.21):
        o=record(poly_prism(PREFIX+name,[source_point(q) for q in poly],8.4+z-th,8.4+z,mats['stone_floor'],col),'candidate_platform')
        platforms.append({'id':name,'polygon_px':poly,'z_relative':z,'thickness':th,'object':o.name})
        return o
    # Split the old main slab at the actual southern facade. Retain its complete
    # east and north extent; only the source two descending west bands change.
    main=next(s for s in data['slabs'] if s['id']=='GUEST_L1_MAIN_FLOOR')['polygon']
    north=clip(main,1,444,True)
    slab('MAIN_FLOOR_NORTH_RETAINED',north,0,.23)
    south=clip(main,1,444,False)
    slab('MAIN_FLOOR_EAST_RETAINED',clip(south,0,448,False),0,.23)
    for s in design['surfaces']:
        name=s['name'];x0,x1,y0,y1=s['rect_px']
        if name=='P_FRONT_EAST':continue  # already exact old main slab partition
        if name=='P_L2_NORTH':x0=287;y0=204  # preserve adjacent bedroom seam at287
        poly=[[x0,y0],[x1,y0],[x1,y1],[x0,y1]]
        if name=='P_SOUTH_LOW':
            # W1 first riser is324, not326: shared boundary at the true step.
            poly=[[284,405.5],[326,405.5],[326,450],[324,450],[324,472],[284,472]]
        slab(name,poly,s['z'],s['thickness'])

    def prism_world(name,poly,z0,z1,mat='ochre',kind='candidate_stair'):
        return record(poly_prism(PREFIX+name,poly,z0,z1,mats[mat],col),kind)
    # Six flights: each has N actual risers and N-1 horizontal goings. The thin
    # upper treads retain headroom; closed vertical riser pieces unite the
    # successive plates instead of leaving gaps between isolated thin slabs.
    for f in design['flights']:
        a=Vector(source_point(f['source_start_px']));b=Vector(source_point(f['source_end_px']))
        d=(b-a).normalized();normal=Vector((-d.y,d.x));length=(b-a).length
        n=f['risers'];rise=f['riser_m'];going=length/(n-1);z0=8.4+f['z0']
        tread_rows=[]
        def footprint(ta,tb,top):
            pts=[a+d*ta-normal*f['width_m']/2,a+d*tb-normal*f['width_m']/2,
                 a+d*tb+normal*f['width_m']/2,a+d*ta+normal*f['width_m']/2]
            pts=[list(q) for q in pts]
            if f['id']=='F3_UPPER_LEFT_SOUTH' and top<9.20+.13:
                # Fixed2ft5 retaining wall owns its volume; trim the inferred
                # upper construction, never displace its finish plane/anchors.
                pts=clip(pts,0,2.1627,True)
            return pts
        for j in range(n-1):
            top=z0+(j+1)*rise;ta=j*going;tb=(j+1)*going
            ob=prism_world(f['id']+'_TREAD_%02d'%j,footprint(ta,tb,top),top-.13,top)
            tread_rows.append({'object':ob.name,'a':list(a+d*ta),'b':list(a+d*tb),
                               'top':top,'going':going,'center':[*(a+d*((ta+tb)/2)),top]})
        for j in range(n):
            t=j*going;low=z0+j*rise;high=low+rise
            ta,tb=(0,.024) if j==0 else (t-.024,t)
            prism_world(f['id']+'_RISER_%02d'%j,footprint(ta,tb,high),low-.13,high)
        for side in (-1,1):
            # Source retaining wall substitutes for the basement east railing.
            if f['id']=='F1_B1_LEFT_SOUTH' and (normal*side).x>0:continue
            offset=normal*side*(f['width_m']/2-.040)
            aa=a+offset;bb=b+offset
            if f['id']=='F3_UPPER_LEFT_SOUTH' and offset.x>0:
                aa.x=bb.x=2.1627-.025
            record(beam(PREFIX+f['id']+'_RAIL_%s'%side,(*aa,z0+.90),(*bb,z0+n*rise+.90),.020,mats['red'],col),'candidate_handrail')
            for j in sorted(set((0,(n-2)//2,n-2))):
                t=(j+.5)*going;pt=a+d*t+(aa-a);top=z0+(j+1)*rise
                rail_z=z0+.90+(t/length)*n*rise
                record(cylinder(PREFIX+f['id']+'_POST_%s_%02d'%(side,j),(*pt,(top+rail_z)/2),.016,rail_z-top,mats['red'],col,12),'candidate_baluster')
        flights.append({**f,'treads':tread_rows,'actual_goings':n-1,'actual_risers':n})

    # The west Lounge outline is fixed glazing in the source plan. Keep its
    # surrounding fireplace/pier geometry and use the adjacent front sill/head
    # as explicitly C height/grid, not a fabricated entrance above a1.18m drop.
    a=source_point((330,415.36));b=source_point((330,435.38))
    sill=record(segment(PREFIX+'WEST_LOUNGE_WINDOW_SILL',a,b,8.4,8.68,.32,mats['stone'],col),'source_window_sill')
    for ob in [sill]+window(PREFIX+'WEST_LOUNGE_WINDOW',a,b,8.68,10.5,ctx,col,3):
        if ob not in made:made.append(ob)
        ob['candidate_only']=True;ob['evidence']='A plan: continuous corner window; C sill/head/mullion spacing'
        ob['reference']='guest01 original g01-west-context and g01-south-paving actually inspected; parent source ruling'
    # Newly inspected MCAH panorama and native guest01 crop identify the real
    # entrance south of the screen, not the west corner. Open leaf follows the
    # drawn northward swing against the bathroom-side wall; pose/detail remainC.
    ent_a,ent_b=source_point((457,430)),source_point((476,430))
    side_a,side_b=source_point((444,430)),source_point((457,430))
    record(segment(PREFIX+'SOUTHEAST_ENTRY_SIDELIGHT_SILL',side_a,side_b,8.4,9.00,.14,mats['stone'],col),'source_entry_sidelight')
    for ob in window(PREFIX+'SOUTHEAST_ENTRY_SIDELIGHT',side_a,side_b,9.00,10.45,ctx,col,2):
        made.append(ob);ob['evidence']='A plan entry/side-light identity; B MCAH2001 photo; C heights/grid'
    for suffix,q in [('WEST',ent_a),('EAST',ent_b)]:
        record(cylinder(PREFIX+'SOUTHEAST_ENTRY_JAMB_'+suffix,(*q,9.425),.022,2.05,mats['red'],col,4),'source_entry_frame')
    record(segment(PREFIX+'SOUTHEAST_ENTRY_HEAD',ent_a,ent_b,10.43,10.47,.05,mats['red'],col),'source_entry_frame')
    leaf_a,leaf_b=source_point((476,430)),source_point((476,411))
    for ob in window(PREFIX+'SOUTHEAST_ENTRY_OPEN_GLASS_LEAF',leaf_a,leaf_b,8.44,10.41,ctx,col,1):
        made.append(ob);ob['evidence']='A door identity and north swing from guest01; B MCAH entrance-face3; C open operational pose/details'
    # Support the exposed side of unchanged Lounge floor rather than leaving
    # its slab floating above the newly interpreted lower southern paving.
    record(segment(PREFIX+'WEST_LOUNGE_EXPOSED_PLINTH',source_point((330,405.5)),source_point((330,440)),7.01,8.4,.32,mats['stone'],col),'candidate_exposed_foundation')
    record(segment(PREFIX+'FRONT_LOUNGE_EXPOSED_PLINTH',source_point((331,442)),source_point((444,442)),7.50,8.17,.18,mats['stone'],col),'candidate_exposed_foundation')

    # Preserve the exact digitized XY and old canopy. Lower only the walking
    # profile/low wall and extend its visible posts to supported candidate feet.
    oldroute=[Vector(q) for q in data['connector']['points']]
    newroute=[Vector(q) for q in design['connector_C']['proposed_world_points']]
    samples=[]
    for i in range(len(newroute)-1):
        a,b,c,d=newroute[max(0,i-1)],newroute[i],newroute[i+1],newroute[min(i+2,len(newroute)-1)]
        for k in range(5):
            t=k/5;q=.5*(2*b+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
            q.z=b.z+(c.z-b.z)*t;samples.append((q,i))
    samples.append((newroute[-1],len(newroute)-2))
    normals=[]
    for i,(q,g) in enumerate(samples):
        diff=samples[min(i+1,len(samples)-1)][0]-samples[max(i-1,0)][0]
        normals.append(Vector((-diff.y,diff.x)).normalized())
    width=data['connector']['width'];connector=[]
    # The final actual paving joins the west edge of the low south platform.
    # Finish the inferred14rises before that overlap, not underneath its floor.
    finish_start=5.28615;total_rise=7.22-finish_start;count=14;rr=total_rise/count
    profile_end=samples[41][0].z;prevtop=finish_start
    for i in range(len(samples)-1):
        a,g=samples[i];b,_=samples[i+1];na,nb=normals[i],normals[i+1]
        al=Vector(a[:2])+na*width/2;ar=Vector(a[:2])-na*width/2
        bl=Vector(b[:2])+nb*width/2;br=Vector(b[:2])-nb*width/2
        # First zone shares main landing height, final zone shares south7.22.
        level=round(((a.z+b.z)/2-newroute[0].z)/(profile_end-newroute[0].z)*count)
        top=finish_start+max(0,min(count,level))*rr
        ob=prism_world('CONNECTOR_TREAD_%03d'%i,[al,ar,br,bl],min(top,prevtop)-.20,top,'stone_floor','candidate_connector')
        connector.append({'object':ob.name,'center':[(a.x+b.x)/2,(a.y+b.y)/2,top],'top':top,'polygon_world':[list(p) for p in (al,ar,br,bl)],
                          'a':[a.x,a.y,top],'b':[b.x,b.y,top],'group':g})
        record(segment(PREFIX+'CONNECTOR_WALL_%03d'%i,al,bl,min(top,prevtop)-.08,top+.76,.16,mats['stone'],col),'candidate_connector_lowwall')
        if i%10==0:
            q=Vector(a[:2])-na*width*.46;canz=max(oldroute[g].z,oldroute[g+1].z)+2.42
            record(cylinder(PREFIX+'CONNECTOR_POST_%03d'%i,(*q,(top+canz)/2),.034,canz-top,mats['red'],col,12),'candidate_connector_support')
        prevtop=top
    # Union the same-height terminal paving with the low platform. This removes
    # the overlapping coincident top sheets rather than merely hiding them.
    landing=bpy.data.objects[PREFIX+'P_SOUTH_LOW']
    terminal_union=[]
    for t in connector:
        if abs(t['top']-7.22)>.000001:continue
        ob=bpy.data.objects[t['object']]
        bpy.context.view_layer.objects.active=landing
        mod=landing.modifiers.new('TERMINAL_PAVING_UNION','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=ob
        bpy.ops.object.modifier_apply(modifier=mod.name)
        terminal_union.append(ob.name);made.remove(ob);bpy.data.objects.remove(ob,do_unlink=True)
        t['merged_into']=landing.name;t['object']=landing.name
    # Parent-authorized corrections of prior C assumptions. These operations
    # are explicit geometry edits to this independent candidate, never hide flags.
    modifications=[]
    def difference(ob,lo,hi,label):
        cutter=box(PREFIX+'CUTTER_'+label,[(a+b)/2 for a,b in zip(lo,hi)],
                   [b-a for a,b in zip(lo,hi)],mats['ochre'],col,0)
        before=len(ob.data.vertices)
        bpy.context.view_layer.objects.active=ob
        mod=ob.modifiers.new(label,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(cutter,do_unlink=True)
        modifications.append({'object':ob.name,'operation':'closed_exact_difference','box':[lo,hi],
                              'vertices_before':before,'vertices_after':len(ob.data.vertices),'evidence':'C inferred interface correction'})
    # Only the north transverse return under the L1 approach is lowered. Its
    # new core cap joins the slab underside; visible walking finish remains8.4.
    # The long rounded side wall and every basement2ft5 measuring face retainXY.
    wall=bpy.data.objects[FIXED_WALL]
    difference(wall,[-10,40.00,8.19],[2.1627,42.0,10.0],'L1_NORTH_RETURN_UNDER_FINISH')
    wall['candidate_C_north_return']='North transverse return core trimmed toL1-.21 under retained8.4 walking finish; long side/rounded end and2ft5 faces untouched'
    # guest02 canopy reaches the south building face; its former width envelope
    # must not continue inside the upper stairwell. Keep its absolute roofZ.
    x0=source_point((284,421))[0];x1=source_point((326,421))[0];cuty=source_point((284,421))[1]
    for i in (42,43,44):
        ob=bpy.data.objects['GUEST_CONNECTOR_canopy_%03d'%i]
        difference(ob,[x0,cuty,9.9],[x1,40,13.0],'SOURCE_BUILDING_FACE_%03d'%i)
        ob['candidate_C_clip']='guest02 south service facade atY421: roof closed at physical building envelope; no global raising'
    for i in (42,43,44):
        ob=bpy.data.objects[PREFIX+'CONNECTOR_WALL_%03d'%i]
        difference(ob,[x0,cuty,5],[x1,40,10],'WALK_ARRIVAL_EDGE_%03d'%i)

    # Local construction trench in the existing C soil surface. Densify only
    # local existing triangles, preserving original interpolation outside this
    # footprint, then lower vertices below the actual slabs with a0.30m blend.
    import bmesh
    from mathutils.bvhtree import BVHTree
    terrain=bpy.data.objects['SITE_Continuous_BearRun_Terrain'];oldmesh=terrain.data
    oldbvh=BVHTree.FromPolygons([v.co for v in oldmesh.vertices],[tuple(p.vertices) for p in oldmesh.polygons])
    zones=[]
    for t in connector:zones.append({'id':t['object'],'poly':t['polygon_world'],'cap':t['top']-.26})
    for f in flights:
        if f['id']!='W1_FRONT_WEST':continue
        aa=Vector(source_point(f['source_start_px']));bb=Vector(source_point(f['source_end_px']));nn=Vector((0,f['width_m']/2))
        for t in f['treads']:
            a,b=Vector(t['a']),Vector(t['b'])
            zones.append({'id':t['object'],'poly':[list(a-nn),list(b-nn),list(b+nn),list(a+nn)],'cap':t['top']-.26})
    for s in platforms:
        if s['id'] in {'P_SOUTH_LOW','P_FRONT_MIDDLE'}:
            zones.append({'id':s['id'],'poly':[source_point(q) for q in s['polygon_px']],'cap':8.4+s['z_relative']-.26})
    def nearpoly(x,y,poly):
        inside=False;dist=1e20
        for a,b in zip(poly,poly[1:]+poly[:1]):
            if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
            dx,dy=b[0]-a[0],b[1]-a[1]
            u=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/max(1e-12,dx*dx+dy*dy)))
            dist=min(dist,math.hypot(x-a[0]-u*dx,y-a[1]-u*dy))
        return 0.0 if inside else dist
    bm=bmesh.new();bm.from_mesh(oldmesh)
    edges=[e for e in bm.edges if all(-5<v.co.x<10 and 29<v.co.y<38.5 for v in e.verts)]
    bmesh.ops.subdivide_edges(bm,edges=edges,cuts=7,use_grid_fill=True)
    changed=[]
    for v in bm.verts:
        x,y,z=v.co
        if not(-5.5<x<10.5 and 22.5<y<39):continue
        target=z
        for zone in zones:
            dist=nearpoly(x,y,zone['poly'])
            if dist>=.40 or zone['cap']>=z:continue
            blend=max(0,min(1,(dist-.10)/.30));blend=blend*blend*(3-2*blend)
            target=min(target,zone['cap']*(1-blend)+z*blend)
        if target<z-.000001:
            changed.append([float(x),float(y),float(z),float(target)]);v.co.z=target
    mesh=bpy.data.meshes.new('SITE_Continuous_BearRun_Terrain_C10_LOCAL_TRENCH');bm.to_mesh(mesh);bm.free();mesh.update()
    for mat in oldmesh.materials:mesh.materials.append(mat)
    for f in mesh.polygons:f.use_smooth=True
    terrain.data=mesh;terrain['candidate_C_trench']='Exact C candidate slab footprints+0.10m construction margin+0.30m blended side bank; no bedrock/river modification'
    newbvh=BVHTree.FromPolygons([v.co for v in mesh.vertices],[tuple(p.vertices) for p in mesh.polygons])
    seating=[]
    for ob in bpy.context.scene.objects:
        if not ob.name.endswith('_Branches') or not(-5.5<ob.location.x<10.5 and 29<ob.location.y<39):continue
        p=Vector((ob.location.x,ob.location.y,30));oldhit=oldbvh.ray_cast(p,Vector((0,0,-1)),40)[0];newhit=newbvh.ray_cast(p,Vector((0,0,-1)),40)[0]
        if oldhit is not None and newhit is not None and abs(oldhit.z-newhit.z)>.005:
            seating.append({'object':ob.name,'root':list(ob.location),'ground_before':oldhit.z,'ground_after':newhit.z,'status':'NEEDS_LOCAL_RESEATING_REVIEW_NOT_MOVED'})
    excavation={'zones':zones,'changed_vertices':len(changed),'vertex_changes':changed,
                'maximum_lowering_m':max((q[2]-q[3] for q in changed),default=0),
                'changed_xy_bounds':[[min(q[a] for q in changed),max(q[a] for q in changed)] for a in (0,1)],
                'plant_contacts':seating,'river_bedrock_objects_untouched':True}
    adjacency=[];retracted=[]
    for edge in data['adjacency']:
        item=dict(edge)
        if {edge['from'],edge['to']}=={'GUEST_L1_TERRACE','GUEST_L1_LOUNGE'}:
            old=dict(item);old['status']='RETRACTED_FALSE_WEST_ROUTE_IDENTITY';old['reason']='West corner is glazing. Same room pair has a real southeast door evidenced by guest01 and MCAH2001 entrance panorama.';retracted.append(old)
            item['connection']='southeast glazed entrance door';item['source_threshold_px']=[[466,434],[466,424]]
            item['candidate_validation']='PENDING_LOCAL_PHYSICAL_CHECKS';item['evidence']='A guest01 plan door/swing; B MCAH entrance-face3; C detailed frame/pose';adjacency.append(item)
        else:
            if {edge['from'],edge['to']}=={'GUEST_L1_STAIR_HALL','GUEST_L1_TERRACE'}:
                item['connection']='two stepped front groups via low south arrival'
                item['evidence']='A two source DOWN groups; C3+4risers and relative south-1.18m'
            item['candidate_validation']='PENDING_LOCAL_PHYSICAL_CHECKS';adjacency.append(item)
    result={'schema':'fallingwater.guest_circulation10.physical_candidate.v1','source_sha256':SOURCE_SHA,
            'classification':'C construction hypothesis; source window identity A, heights/grid C',
            'removed_objects':sorted(removed),'created_objects':[o.name for o in made],
            'fixed_retaining_wall':FIXED_WALL,'flights':flights,'platforms':platforms,'connector':connector,
            'explicit_mutations':modifications,'excavation':excavation,
            'terminal_paving_union_removed':terminal_union,'connector_actual_riser_m':rr,
            'adjacency':adjacency,'retracted_adjacency':retracted,
            'production_data_untouched':True,'full_navigation_status':'NOT_RUN_LOCAL_CANDIDATE_ONLY'}
    text=bpy.data.texts.new('FW_GUEST_CIRCULATION10_CANDIDATE.json');text.write(json.dumps(result,indent=2))
    bpy.context.view_layer.update()
    return result
