"""Prepare/reopen a single natural-channel candidate. This module cannot bake or render."""
import sys, json, hashlib, time, math, ctypes, shutil, traceback
from pathlib import Path
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import hybrid_water as h

P = ROOT / 'qa'
CONFIG = json.loads((P / 'water10-domain-config.json').read_text(encoding='utf-8'))
SOURCE = Path(CONFIG['source_scene'])
PILOT = ROOT / 'scene/Fallingwater_water10_natural48.blend'
CACHE = ROOT / 'caches/fluid_water10/natural48'
REPORT = P / 'water10-natural48.json'
DOMAIN = 'WATER10_Natural_Channel_Domain'
INIT = 'WATER10_Complete_Connected_Initial_Channel'
JET = 'WATER10_C_Gravity_Branch_Inflow'
COLL = 'WATER10_Exact_Collision_Copies'
FLOWS = 'WATER10_Physical_Flows'
ROI = np.array(CONFIG['domain_aabb_m'], dtype=float)
CELL = .075
KEYS = list(json.loads((P / 'water09-realbed24-control.json').read_text(encoding='utf-8'))['post_bake_assertions']['actual_domain'])
KEYS += ['cache_type', 'cache_resumable', 'cache_frame_start', 'cache_frame_end', 'cache_data_format', 'cache_mesh_format', 'cache_particle_format', 'sndparticle_sampling_wavecrest', 'sndparticle_sampling_trappedair', 'sndparticle_life_min', 'sndparticle_life_max', 'sndparticle_combined_export', 'sndparticle_boundary']
STABLE = json.loads((P / 'water09-realbed24-control.json').read_text(encoding='utf-8'))['post_bake_assertions']['actual_domain']
TARGET = dict(STABLE)
TARGET.update(resolution_max=320, timesteps_max=8, use_foam_particles=True, use_spray_particles=True,
              use_collision_border_left=False, use_collision_border_front=False, use_collision_border_top=False,
              use_collision_border_right=False, use_collision_border_back=True, use_collision_border_bottom=True,
              cache_type='ALL', cache_resumable=True, cache_frame_start=1, cache_frame_end=48,
              cache_data_format='OPENVDB', cache_mesh_format='BOBJECT', cache_particle_format='UNI',
              sndparticle_sampling_wavecrest=8, sndparticle_sampling_trappedair=8,
              sndparticle_life_min=.25, sndparticle_life_max=1.2, sndparticle_combined_export='OFF')
SECONDARY = ('use_foam_particles', 'use_spray_particles', 'use_bubble_particles', 'use_tracer_particles')
FLOW_KEYS = ['flow_type', 'flow_behavior', 'flow_source', 'use_initial_velocity', 'velocity_factor', 'velocity_coord', 'velocity_normal', 'velocity_random', 'surface_distance', 'subframes', 'use_inflow', 'use_plane_init', 'use_texture']

def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        while chunk := stream.read(8 * 1024 * 1024): digest.update(chunk)
    return digest.hexdigest()

def dump(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def manifest():
    bases = ['fluid_water08/static_head24', 'fluid_water09/real_bed_default24', 'fluid_hybrid07/impact36', 'fluid_water09/impact36']
    return [{'path':str(p.relative_to(ROOT / 'caches')), 'bytes':p.stat().st_size, 'sha256':sha(p)}
            for base in bases for p in sorted((ROOT / 'caches' / base).rglob('*')) if p.is_file()]

def resources():
    class MEMORY(ctypes.Structure):
        _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong)] + [(n, ctypes.c_ulonglong) for n in ('total_phys', 'available_phys', 'total_page', 'available_page', 'total_virtual', 'available_virtual', 'extended')]
    mem = MEMORY(); mem.length = ctypes.sizeof(mem)
    assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
    disk = shutil.disk_usage(ROOT)
    return {'physical_total_bytes':mem.total_phys, 'physical_available_bytes':mem.available_phys,
            'memory_load_percent':mem.load, 'disk_free_bytes':disk.free,
            'planning_peak_RAM_bytes_not_measured':[3817440000, 9269760000],
            'planning_cache_bytes_not_measured':[2062451653, 8249806611],
            'RAM_reserve_12GB_available':mem.available_phys >= 12_000_000_000,
            'disk_reserve_12GB_available':disk.free >= 12_000_000_000}

def mesh(name, vertices, faces, collection=None):
    me = bpy.data.meshes.new(name); me.from_pydata(vertices, [], faces); me.update()
    o = bpy.data.objects.new(name, me); (collection or bpy.context.scene.collection).objects.link(o)
    return o

def recalc(o):
    bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    if bm.calc_volume(signed=True) < 0: bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
    bm.to_mesh(o.data); bm.free(); o.data.update()

def arrays(o):
    o.data.calc_loop_triangles()
    return np.array([tuple(o.matrix_world @ v.co) for v in o.data.vertices]), np.array([tuple(t.vertices) for t in o.data.loop_triangles], dtype=int)

def bounds(o):
    v, _ = arrays(o); return np.stack((v.min(0), v.max(0)), 1).tolist()

def cube(name, lo, hi, collection=None):
    v = [(lo[0],lo[1],lo[2]),(hi[0],lo[1],lo[2]),(hi[0],hi[1],lo[2]),(lo[0],hi[1],lo[2]),(lo[0],lo[1],hi[2]),(hi[0],lo[1],hi[2]),(hi[0],hi[1],hi[2]),(lo[0],hi[1],hi[2])]
    return mesh(name, v, [(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)], collection)

def close_terrain(v, f):
    # Duplicate the exact top triangles at an underground bottom. Side walls follow
    # the copied perimeter outside the domain; no visible terrain vertex is moved.
    n = len(v); edges = {}
    for face in f:
        for a, b in zip(face, np.roll(face, -1)):
            key = tuple(sorted((int(a), int(b))))
            edges.setdefault(key, []).append((int(a), int(b)))
    boundary = [e[0] for e in edges.values() if len(e) == 1]
    assert all(len(e) <= 2 for e in edges.values())
    bottom = v.copy(); bottom[:,2] = -9.0
    faces = f.tolist() + [[int(x)+n for x in reversed(t)] for t in f]
    faces += [[b,a,a+n,b+n] for a,b in boundary]
    return np.vstack([v,bottom]), faces, boundary

def stage(x, y):
    cfg = json.loads((ROOT / 'data/site.json').read_text(encoding='utf-8'))
    river = np.array(cfg['river_path'][9:17], dtype=float); river[0,2] = -5.771274
    best = np.full(np.shape(x), np.inf); result = np.full(np.shape(x), np.nan)
    for a,b in zip(river[:-1],river[1:]):
        delta=b[:2]-a[:2]; length2=float(delta@delta)
        u=np.clip(((x-a[0])*delta[0]+(y-a[1])*delta[1])/length2,0,1)
        d=(x-a[0]-u*delta[0])**2+(y-a[1]-u*delta[1])**2
        take=d<best; result[take]=(a[2]+u*(b[2]-a[2]))[take]; best=np.minimum(best,d)
    return result

def initial_prism():
    # Continuous sloping stage, no hidden plane: one closed volume subsequently
    # subtracts exact solid bed/rock copies, so exposed rock remains dry.
    x=np.linspace(ROI[0,0],ROI[0,1],161); y=np.linspace(ROI[1,0],ROI[1,1],155)
    xx,yy=np.meshgrid(x,y); zz=stage(xx,yy)
    v=np.column_stack([xx.ravel(),yy.ravel(),zz.ravel()]); n=len(v)
    bottom=v.copy(); bottom[:,2]=ROI[2,0]+.001
    f=[]; nx=len(x); ny=len(y)
    for j in range(ny-1):
        for i in range(nx-1):
            a=j*nx+i; b=a+1; c=a+1+nx; d=a+nx
            f.extend([(a,b,c),(a,c,d),(a+n,c+n,b+n),(a+n,d+n,c+n)])
    perimeter=list(range(nx))+[j*nx+nx-1 for j in range(1,ny)]+[(ny-1)*nx+i for i in range(nx-2,-1,-1)]+[j*nx for j in range(ny-2,0,-1)]
    for a,b in zip(perimeter,perimeter[1:]+perimeter[:1]): f.append((b,a,a+n,b+n))
    return mesh(INIT,np.vstack([v,bottom]),f)

def select_connected(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    remaining=set(bm.verts); components=[]
    while remaining:
        first=remaining.pop(); group={first}; todo=[first]
        while todo:
            v=todo.pop()
            for edge in v.link_edges:
                other=edge.other_vert(v)
                if other in remaining: remaining.remove(other); group.add(other); todo.append(other)
        ff={f for v in group for f in v.link_faces}
        coords=np.array([v.co[:] for v in group]); volume=0.0
        for f in ff:
            a=f.verts[0].co
            for j in range(1,len(f.verts)-1): volume+=a.dot(f.verts[j].co.cross(f.verts[j+1].co))/6
        components.append({'verts':group,'faces':ff,'volume_m3':volume,'bounds':np.stack((coords.min(0),coords.max(0)),1).tolist()})
    components.sort(key=lambda c:abs(c['volume_m3']),reverse=True)
    report=[{k:(len(v) if k in ('verts','faces') else v) for k,v in c.items()} for c in components]
    if len(components)>1:
        remove=[v for c in components[1:] for v in c['verts']]; bmesh.ops.delete(bm,geom=remove,context='VERTS')
    bm.to_mesh(o.data); bm.free(); o.data.update(); recalc(o)
    return report

def stitch_collinear_boolean_tjunctions(o):
    """Split an existing long face edge at its existing collinear middle vertex.

    Exact Boolean can return A--B beside A--M--B: no finite-area hole exists.
    Keep every vertex and position; do not fill a water gap with a new plane.
    """
    bm=bmesh.new(); bm.from_mesh(o.data); bad={e for e in bm.edges if e.is_boundary}; repairs=[]
    while bad:
        edge=bad.pop(); group={edge}; todo=list(edge.verts)
        while todo:
            point=todo.pop()
            for candidate in point.link_edges:
                if candidate in bad:
                    bad.remove(candidate); group.add(candidate); todo.extend(candidate.verts)
        vertices={v for e in group for v in e.verts}
        assert len(group)==3 and len(vertices)==3,'Only measured collinear three-edge T-junctions are repairable here'
        longest=max(group,key=lambda e:e.calc_length()); a,b=longest.verts
        mid=next(v for v in vertices if v not in longest.verts)
        delta=b.co-a.co; u=(mid.co-a.co).dot(delta)/delta.length_squared
        error=(mid.co-(a.co+delta*u)).length
        assert 0<u<1 and error<1e-6,(u,error)
        face=longest.link_faces[0]; points=list(face.verts); replacement=[]
        for i,v in enumerate(points):
            replacement.append(v)
            if {v,points[(i+1)%len(points)]}=={a,b}: replacement.append(mid)
        repairs.append({'a':a.co[:],'middle':mid.co[:],'b':b.co[:],'collinearity_error_m':error,'fraction':u,'new_vertices':0,'moved_vertices':0,'filled_area_m2':0})
        bm.faces.remove(face); bm.faces.new(replacement)
        if not longest.link_faces: bm.edges.remove(longest)
    bm.to_mesh(o.data); bm.free(); o.data.update(); recalc(o)
    return repairs

def flow(o, behavior, velocity=None):
    m=o.modifiers.new('Physical liquid volume','FLUID'); m.fluid_type='FLOW'; f=m.flow_settings
    f.flow_type='LIQUID'; f.flow_behavior=behavior; f.surface_distance=0
    if velocity is not None:
        f.use_initial_velocity=True; f.velocity_factor=0; f.velocity_coord=velocity
        f.velocity_normal=0; f.velocity_random=0; f.subframes=1
    else: f.use_initial_velocity=False; f.velocity_coord=(0,0,0)
    o.hide_render=True; o.display_type='WIRE'
    return f

def flow_state(o):
    f=next(m.flow_settings for m in o.modifiers if m.type=='FLUID')
    return {k:list(getattr(f,k)) if k=='velocity_coord' else getattr(f,k) for k in FLOW_KEYS}

def validate(r):
    s=bpy.context.scene; o=s.objects[DOMAIN]; d=next(m.domain_settings for m in o.modifiers if m.type=='FLUID')
    assert sha(SOURCE)==CONFIG['source_sha256']
    assert np.max(abs(np.array(bounds(o))-ROI))<2e-6
    for name, sig in r['candidate_geometry_hashes'].items(): assert h.shape_hash(s.objects[name])==sig,name
    actual={k:getattr(d,k) for k in KEYS}
    for k,target in TARGET.items():
        value=getattr(d,k)
        assert abs(value-target)<1e-6 if isinstance(value,float) else value==target,(k,value,target)
    systems=sorted(p.settings.type for p in o.particle_systems); assert systems==['FLIP','FOAM','SPRAY'],systems
    assert list(o.scale)==[1,1,1] and np.max(abs(np.array(o.matrix_world)-np.eye(4)))<1e-8
    assert Path(bpy.path.abspath(d.cache_directory)).resolve()==CACHE.resolve()
    assert set(d.fluid_group.objects.keys())=={INIT,JET} and d.effector_group.name==COLL
    assert s.frame_start==1 and s.frame_end==48 and s.render.fps==24 and s.render.threads==8
    assert s.unit_settings.scale_length==1 and abs(s.gravity.z+9.81)<1e-5
    assert flow_state(s.objects[INIT])==r['initial_flow'] and flow_state(s.objects[JET])==r['source_flow']
    eff=[]
    for ob in d.effector_group.objects:
        f=next(m.effector_settings for m in ob.modifiers if m.type=='FLUID')
        assert f.effector_type=='COLLISION' and not f.use_plane_init and f.use_effector
        assert h.topology(ob)['nonmanifold_edges']==0
        eff.append({'name':ob.name,'surface_distance':f.surface_distance,'use_plane_init':f.use_plane_init,'use_effector':f.use_effector})
    return {'passed':True,'actual_domain':actual,'actual_particle_systems':systems,'actual_effectors':eff,
            'geometry_hashes_verified':len(r['candidate_geometry_hashes']), 'raw_domain_aabb':bounds(o),
            'RNA_domain_resolution_before_solver_allocation':list(d.domain_resolution),
            'estimated_grid_not_yet_solver_observed':[320,307,37], 'candidate_is_separate':True}

def prepare():
    t=time.perf_counter()
    assert not PILOT.exists() and not CACHE.exists(), 'Single new candidate; do not replace a previous prepare'
    assert sha(SOURCE)==CONFIG['source_sha256']
    old=manifest(); dump(P/'water10-natural48-preserved-cache-manifest.json',old)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE)); s=bpy.context.scene; s.frame_set(48)
    s.render.threads_mode='FIXED'; s.render.threads=8
    core=s.objects['SITE_Core_Continuous_Fractured_Sandstone']; assert h.shape_hash(core)==CONFIG['frozen_core_sha256']
    src_records=[]; colliders=[]; extracted=[]; dep=bpy.context.evaluated_depsgraph_get()
    prefix=('SITE_Continuous_BearRun_Terrain','SITE_Core_Continuous','SITE_Cascade_Shoulder','SITE_Secondary_Sandstone','SITE_Split_Talus','SITE_Bank_')
    for original in list(s.objects):
        if original.type!='MESH' or not original.name.startswith(prefix): continue
        ev=original.evaluated_get(dep); me=ev.to_mesh(); me.calc_loop_triangles()
        v=np.array([tuple(original.matrix_world @ p.co) for p in me.vertices]); f=np.array([tuple(t.vertices) for t in me.loop_triangles],dtype=int)
        a=np.stack((v.min(0),v.max(0)),1)
        if any(a[k,1]<ROI[k,0]-1 or a[k,0]>ROI[k,1]+1 for k in (0,1)) or a[2,0]>ROI[2,1]+1 or a[2,1]<ROI[2,0]: ev.to_mesh_clear(); continue
        record={'source_name':original.name,'original_raw_world_sha256':h.shape_hash(original),'source_aabb_m':a.tolist()}
        if original.name=='SITE_Continuous_BearRun_Terrain':
            tri=v[f]; keep=np.ones(len(f),bool)
            for k in (0,1): keep&=(tri[:,:,k].max(1)>=ROI[k,0]-1)&(tri[:,:,k].min(1)<=ROI[k,1]+1)
            chosen=f[keep]; ids=np.unique(chosen); mapping=np.full(len(v),-1,int); mapping[ids]=np.arange(len(ids)); v=v[ids]; f=mapping[chosen]
            original_top=v.copy(); original_faces=f.copy(); v,f,edge=close_terrain(v,f)
            record.update(exact_top_vertices=len(original_top),exact_top_triangles=len(original_faces),closure_bottom_z_m=-9.0,closure_boundary_edges=len(edge))
            p=original_top[np.array(edge).ravel()]; outside=np.any((p[:,:2]<ROI[:2,0])|(p[:,:2]>ROI[:2,1]),axis=1)
            assert outside.all(),'Terrain closure cannot expose a vertical wall inside domain'
            record['all_closure_perimeter_vertices_outside_domain_xy']=bool(outside.all())
        extracted.append((original.name,v,f,record,original_top.copy() if original.name=='SITE_Continuous_BearRun_Terrain' else None))
        ev.to_mesh_clear()
        print('W10_EXTRACTED',original.name,len(v),len(f),flush=True)
    # Every evaluated source mesh is copied before ANY source-scene mutation.
    # This avoids rebuilding the full forest/architecture dependency graph once
    # per new collider. The prior slow prepare was stopped before any scene/cache.
    bpy.ops.wm.read_factory_settings(use_empty=True); s=bpy.context.scene
    s.render.threads_mode='FIXED'; s.render.threads=8
    collider_collection=bpy.data.collections.new(COLL); s.collection.children.link(collider_collection)
    for original_name,v,f,record,original_top in extracted:
        copied=mesh('W10_Collider_'+original_name,v,f,collider_collection); recalc(copied)
        record.update(copy_name=copied.name,copy_world_sha256=h.shape_hash(copied),copy_topology=h.topology(copied))
        assert record['copy_topology']['nonmanifold_edges']==0,(original_name,record['copy_topology'])
        if original_name=='SITE_Continuous_BearRun_Terrain':
            assert np.max(abs(np.array([p.co[:] for p in copied.data.vertices[:len(original_top)]])-original_top))<1e-6
            record['exact_top_preserved']=True
        colliders.append(copied); src_records.append(record)
    assert any(r['source_name']=='SITE_Core_Continuous_Fractured_Sandstone' for r in src_records)
    bpy.context.view_layer.update()
    print('W10_COLLIDERS_READY',len(colliders),flush=True)
    initial=initial_prism(); recalc(initial); prism_volume=h.topology(initial)['signed_volume_m3']
    boolean_log=[]
    for rock in colliders:
        before=len(initial.data.vertices); started=time.perf_counter()
        h.apply_boolean(initial,rock,'DIFFERENCE','Exact exclusion '+rock.name)
        boolean_log.append({'object':rock.name,'before_vertices':before,'after_vertices':len(initial.data.vertices),'seconds':time.perf_counter()-started})
        print('W10_INITIAL_SUBTRACT',rock.name,len(initial.data.vertices),flush=True)
    recalc(initial); components=select_connected(initial); top=h.topology(initial)
    iv, it = arrays(initial)
    np.savez_compressed(P/'water10-natural48-initial-boolean-raw.npz',vertices=iv,triangles=it)
    bm=bmesh.new(); bm.from_mesh(initial.data)
    bad=[{'a':e.verts[0].co[:],'b':e.verts[1].co[:],'length_m':e.calc_length(),'linked_faces':len(e.link_faces)} for e in bm.edges if not e.is_manifold]
    dump(P/'water10-natural48-initial-boolean-boundary.json',{'topology':top,'bad_edges':bad,'components':components})
    bm.free()
    repairs=[]
    if bad:
        diagnostic=ROOT/'scene/Fallingwater_water10_natural48_geometry_diagnostic.blend'
        if not diagnostic.exists(): bpy.ops.wm.save_as_mainfile(filepath=str(diagnostic))
        repairs=stitch_collinear_boolean_tjunctions(initial); top=h.topology(initial)
        dump(P/'water10-natural48-boolean-tjunction-repair.json',{'before':bad,'repairs':repairs,'after_topology':top})
    assert top['nonmanifold_edges']==0 and top['signed_volume_m3']>80,top
    tree=h.render_bvh(initial); seed=Vector((.797341526,-2.211417675,-6.0)); assert all(n%2 for n in h.parity(tree,seed))
    print('W10_INITIAL_READY',json.dumps(top),flush=True)
    flows=bpy.data.collections.new(FLOWS); s.collection.children.link(flows); flows.objects.link(initial); s.collection.objects.unlink(initial)
    source_data=json.loads((P/'water10-domain-source-probe.json').read_text(encoding='utf-8'))
    jet=mesh(JET,source_data['world_vertices'],source_data['triangles'],flows); recalc(jet)
    assert h.topology(jet)['nonmanifold_edges']==0
    source_tree=h.render_bvh(jet); points=np.array(source_data['world_vertices']); ff=np.array(source_data['triangles']); sample=np.vstack([points,points[ff].mean(1)])
    contacts=[]
    for rock in colliders:
        rocktree=h.render_bvh(rock); overlaps=source_tree.overlap(rocktree)
        near=min(rocktree.find_nearest(Vector(p))[3] for p in sample)
        contacts.append({'collider':rock.name,'triangle_overlap_pairs':len(overlaps),'min_sample_clearance_m':near})
        assert not overlaps and near>.075
    assert np.all(points>ROI[:,0]) and np.all(points<ROI[:,1])
    rings=points.reshape(-1,40,3); vel=np.array(source_data['center_velocity_world_m_s']); sections=[]
    for ring in rings:
        area_vector=np.cross(ring,np.roll(ring,-1,axis=0)).sum(0)*.5
        sections.append({'true_area_m2':float(np.linalg.norm(area_vector)),'area_normal_dot_velocity_Q_m3_s':float(abs(area_vector@vel))})
    flow(initial,'GEOMETRY'); flow(jet,'INFLOW',source_data['center_velocity_world_m_s'])
    for rock in colliders:
        m=rock.modifiers.new('Exact solid collision','FLUID'); m.fluid_type='EFFECTOR'; e=m.effector_settings
        e.effector_type='COLLISION'; e.surface_distance=.001; e.use_plane_init=False; rock.hide_render=True; rock.display_type='WIRE'
    domain=cube(DOMAIN,ROI[:,0],ROI[:,1]); m=domain.modifiers.new('Independent natural liquid domain','FLUID'); m.fluid_type='DOMAIN'; d=m.domain_settings
    d.domain_type='LIQUID'; CACHE.mkdir(parents=True); d.cache_directory=str(CACHE)
    setter=[]
    for k,value in TARGET.items():
        before=getattr(d,k)
        if before!=value: setattr(d,k,value)
        if k in SECONDARY: setter.append({'property':k,'before':before,'assigned':before!=value,'after':getattr(d,k)})
    d.fluid_group=flows; d.effector_group=collider_collection
    s.frame_start=1; s.frame_end=48; s.frame_set(1); s.render.fps=24; s.render.threads_mode='FIXED'; s.render.threads=8
    s.unit_settings.system='METRIC'; s.unit_settings.scale_length=1; s.gravity=(0,0,-9.81)
    s['water10_status']='PREPARED_ONLY_NOT_BAKED_NOT_JOINED_NOT_VISUAL_PASS'
    bpy.context.view_layer.update()
    r={'status':'PREPARED_REOPEN_REQUIRED_NOT_BAKED','source_scene':str(SOURCE),'source_sha256':CONFIG['source_sha256'],
       'core_original_raw_world_sha256':CONFIG['frozen_core_sha256'],'candidate':str(PILOT),'cache':str(CACHE),
       'frame_range':[1,48],'fps':24,'threads':8,'resolution':320,'estimated_grid':[320,307,37],'estimated_cell_m':CELL,
       'actual_collision_copies':src_records,'boolean_log':boolean_log,'initial_prism_volume_m3':prism_volume,
       'initial_components_before_retaining_main_channel':components,'initial_connected_topology':top,'boolean_collinear_tjunction_stitch':repairs,
       'initial_volume_relative_quartermeter_proxy':top['signed_volume_m3']/CONFIG['initialization']['volume_proxy_m3']-1,
       'initial_volume_over_cell_cubed_rough_wet_voxels':top['signed_volume_m3']/CELL**3,
       'initial_stage_C':'Nearest existing downstream path9:16 head, mainpool -5.771274; not proven hydraulic equilibrium',
       'initial_flow':flow_state(initial),'source_flow':flow_state(jet),'source_actual_ring_sections':sections,
       'source_Q_C_design_m3_s':source_data['nominal_Q_m3_s'],'source_width_cells':source_data['width_m']/CELL,
       'source_thickness_cells':source_data['thickness_m']/CELL,'source_topology':h.topology(jet),
       'source_aabb_m':bounds(jet),'source_collision_checks':contacts,'source_containment_pass':True,
       'secondary_idempotent_setter':setter,'candidate_geometry_hashes':{o.name:h.shape_hash(o) for o in s.objects if o.type=='MESH'},
       'boundary_axis_mapping':{'left':'world X minimum OPEN','right':'world X maximum OPEN C numerical pressure boundary','front':'world Y minimum OPEN','back':'world Y maximum CLOSED','bottom':'world Z minimum CLOSED','top':'world Z maximum OPEN'},
       'boundary_primary_source':'https://raw.githubusercontent.com/blender/blender/blender-v5.2-release/intern/mantaflow/intern/MANTA_main.cpp lines727-744',
       'C_disclosures':['Complete initial stage is authored, not measured equilibrium.','Only exact copied terrain perimeter and bottom closure are added; closure below -9m and outside domain XY.','Single .24x.23m branch source is author-designed Q .2994137, not full waterfall flow.','Native source has no assembled upstream branch join; production JOIN remains unverified.','Open downstream edges are not constant-head boundaries; 5-10s backwater remains unverified.'],
       'old_water09_Q_70_44percent_FAIL_retained':True,'historical_600s_budget_estimate_unchanged_in':'qa/water10-domain-config.json',
       'future_root_budget_seconds':2400,'future_bake_authorized_this_turn':False,'linear_48_cost_estimate_seconds':1217.5578958,
       'cost_estimate_range_seconds':[608.7789479,3652.6736873], '48frames_in_2400s_not_guaranteed':True,
       'resources_before_save':resources(),'prepare_seconds_before_save':time.perf_counter()-t,'new_bakes':0,'new_renders':0,'production_changed':False}
    r['pre_save_assertions']=validate(r); assert manifest()==old; r['old_cache_manifest_456files_unchanged']=True
    bpy.ops.wm.save_as_mainfile(filepath=str(PILOT)); r['prepared_sha256']=sha(PILOT); r['prepare_seconds']=time.perf_counter()-t
    dump(REPORT,r); print('W10_PREPARED',r['prepared_sha256'],r['prepare_seconds'],flush=True)

def reopen():
    r=json.loads(REPORT.read_text(encoding='utf-8')); assert r['status'] in ('PREPARED_REOPEN_REQUIRED_NOT_BAKED','PREPARED_XMAX_OPEN_REOPEN_REQUIRED_NOT_BAKED')
    xmax_open_alignment=r['status']=='PREPARED_XMAX_OPEN_REOPEN_REQUIRED_NOT_BAKED'
    assert sha(PILOT)==r['prepared_sha256']; bpy.ops.wm.open_mainfile(filepath=str(PILOT))
    r['fresh_process_reopen_assertions']=validate(r)
    assert not [p for p in CACHE.rglob('*') if p.is_file()]
    old=json.loads((P/'water10-natural48-preserved-cache-manifest.json').read_text(encoding='utf-8'))
    assert manifest()==old
    r['preserved_old_cache_files']=len(old); r['preserved_old_cache_bytes']=sum(f['bytes'] for f in old)
    r['source_sha256_after']=sha(SOURCE); r['prepared_scene_sha256_after_readonly_reopen']=sha(PILOT)
    r['resources_after_reopen']=resources(); r['cache_file_count']=0
    r['status']='PREPARED_XMAX_OPEN_DIAGNOSTIC_REOPEN_PASS_NATIVE_BOUNDARY_HEAD_JOIN_UNVERIFIED' if xmax_open_alignment else 'PREPARE_REOPEN_PASS_NOT_BAKED_GEOMETRY_FIELD_AUDIT_PENDING'
    dump(REPORT,r); print('W10_REOPEN_PASS',r['prepared_sha256'],flush=True)

def align_xmax_open():
    r=json.loads(REPORT.read_text(encoding='utf-8'))
    assert r['status']=='PREPARED_REOPEN_GEOMETRY_PASS_HYDRAULIC_PREFLIGHT_FAIL_NOT_BAKED'
    assert sha(PILOT)==r['prepared_sha256'] and not [p for p in CACHE.rglob('*') if p.is_file()]
    checkpoint=ROOT/'scene/Fallingwater_water10_natural48_xmax_closed_checkpoint.blend'
    prior=P/'water10-natural48-xmax-closed-checkpoint.json'
    assert not checkpoint.exists() and not prior.exists()
    shutil.copy2(PILOT,checkpoint); shutil.copy2(REPORT,prior)
    before_hash=sha(PILOT); bpy.ops.wm.open_mainfile(filepath=str(PILOT))
    s=bpy.context.scene; domain=s.objects[DOMAIN]; d=next(m.domain_settings for m in domain.modifiers if m.type=='FLUID')
    before=bool(d.use_collision_border_right); assert before
    if d.use_collision_border_right:d.use_collision_border_right=False
    r['root_authorized_Xmax_open_alignment']={'prior_scene_sha256':before_hash,'checkpoint':str(checkpoint),
        'only_RNA_change':{'use_collision_border_right':[True,False]},'geometry_changed':False,'initial_water_volume_unchanged_m3':r['initial_connected_topology']['signed_volume_m3'],
        'reason':'Original geometry contains a narrowing rock-underbank water cavity at X+ ending by x12, not a natural outlet. Root allowed open X+ as explicit C numerical-pressure diagnostic; no false underwater wall added.',
        'boundary_wave_report':'qa/water10-natural48-boundary-audit.json','native_48_boundary_isolation_NOT_PROVEN':True}
    r['boundary_axis_mapping']['right']='world X maximum OPEN C numerical-pressure diagnostic; not natural outlet'
    r['closed_checkpoint_hydraulic_preflight_failures']=r.pop('hydraulic_preflight_failures')
    r['diagnostic_limitations']=['X+ open cuts an original geometric cavity that closes at x12; artificial C pressure condition, not the real bank outlet.',
        '48 frame native boundary influence is not proven. Local-depth gravity-wave estimate reaches HERO after4.064s, but global-depth straight-line lower bound1.628s is below2s.',
        'Initial C stage contains7 steep wet samples around(-4,-12.5) caused by nearest-segment switch; retain as potential initialization transient, do not call it native impact turbulence.',
        'Full-area volume includes19.254m3 under higher frozen rock surfaces; original highest-bed proxy intentionally did not include those spaces.',
        'No upstream closed-branch join, no constant-head downstream proof, no visual pass or long cache authorization.']
    r['pre_save_assertions']=validate(r); r['status']='PREPARED_XMAX_OPEN_REOPEN_REQUIRED_NOT_BAKED'
    s['water10_status']='XMAX_OPEN_C_NUMERICAL_DIAGNOSTIC_ONLY_NOT_BAKED'; bpy.ops.wm.save_as_mainfile(filepath=str(PILOT))
    r['prepared_sha256']=sha(PILOT); dump(REPORT,r); print('W10_XMAX_OPEN_PREPARED',r['prepared_sha256'],flush=True)

if __name__=='__main__':
    assert bpy.app.background
    action=sys.argv[sys.argv.index('--')+1]
    try: {'prepare':prepare,'reopen':reopen,'align_xmax_open':align_xmax_open}[action]()
    except Exception:
        (P/('water10-natural48-'+action+'-failure.txt')).write_text(traceback.format_exc(),encoding='utf-8')
        raise
