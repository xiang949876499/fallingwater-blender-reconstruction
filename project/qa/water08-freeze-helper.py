"""Bounded 155-point freeze candidate and actual evaluated diagnostics; never bake/render."""
import sys, json, hashlib, time
from pathlib import Path
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import hybrid_water as h

SOURCE = ROOT / 'scene/Fallingwater_water_hybrid07_motion36.blend'
SOURCE_SHA = '3c7638bd5866f48eca88a2c184cc958cae3bdfb578892e7e58a59e9c967f55d7'
OUTPUT = ROOT / 'scene/Fallingwater_water_hybrid08_freeze155.blend'
NPZ = ROOT / 'qa/water08-normal-freeze-arrays.npz'
REPORT = ROOT / 'qa/water08-freeze-review.json'
NAME = 'WATER_Hybrid07a_Continuous_River_Branch_Pool'
CORE = 'SITE_Core_Continuous_Fractured_Sandstone'
THRESHOLD = 1e-9

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def coords(data):
    a = np.empty(len(data) * 3, np.float32)
    data.foreach_get('co', a)
    return a.reshape((-1, 3)).astype(np.float64)

def hash_array(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()

def bounds(a):
    return [[float(a[:, k].min()), float(a[:, k].max())] for k in range(3)] if len(a) else None

def stats(a):
    a = np.asarray(a, dtype=float)
    return {'count':len(a), 'min':float(a.min()) if len(a) else None,
            'max':float(a.max()) if len(a) else None, 'median':float(np.median(a)) if len(a) else None,
            'mean':float(a.mean()) if len(a) else None}

def write(data):
    REPORT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def faces_of(mesh):
    mesh.calc_loop_triangles()
    return np.array([tuple(t.vertices) for t in mesh.loop_triangles], np.int32)

def normals(v, f):
    t = v[f]
    return np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])

def world(v, matrix):
    m = np.array(matrix, np.float64)
    return v @ m[:3, :3].T + m[:3, 3]

def tree_for(v, f):
    return BVHTree.FromPolygons(v.tolist(), f.tolist(), all_triangles=True, epsilon=0.0)

def attribute_values(me, key):
    a = np.empty(len(me.attributes[key].data), np.float32)
    me.attributes[key].data.foreach_get('value', a)
    return a

def build():
    assert bpy.app.background
    assert digest(SOURCE) == SOURCE_SHA
    assert not OUTPUT.exists(), 'One candidate only; preserve existing evidence'
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene = bpy.context.scene
    obj = scene.objects[NAME]
    me = obj.data
    keys = me.shape_keys.key_blocks
    base = coords(keys[0].data)
    source_mesh_hash = hash_array(coords(me.vertices))
    source_base_hash = hash_array(base)
    f = faces_of(me)
    ring = np.load(NPZ)['ring_vertices'].astype(np.int32)
    assert len(ring) == 155 and len(np.unique(ring)) == 155
    assert len(keys) == 37
    active = (attribute_values(me, 'H07_fall') > 0) | (attribute_values(me, 'H07_pond') > 0)
    assert int(active.sum()) == 6620 and active[ring].all()
    mask = np.zeros(len(base), bool)
    mask[ring] = True
    canceled = []
    unchanged_hashes = []
    for frame in range(1, 37):
        key = keys[f'C_flow_and_real_impact_{frame:03}']
        a = coords(key.data)
        canceled.append(float(np.linalg.norm(a[ring] - base[ring], axis=1).max()))
        old_outside_hash = hash_array(a[~mask])
        # These are the only geometry mutations in the candidate.
        for i in ring:
            key.data[int(i)].co = base[int(i)]
        after = coords(key.data)
        assert hash_array(after[~mask]) == old_outside_hash
        assert np.array_equal(after[ring], base[ring])
        unchanged_hashes.append(old_outside_hash)
    assert hash_array(coords(me.vertices)) == source_mesh_hash
    assert hash_array(coords(keys[0].data)) == source_base_hash
    scene['water08_freeze_status'] = 'DIAGNOSTIC_GEOMETRY_ONLY'
    scene['water08_freeze_source_sha256'] = SOURCE_SHA
    scene['water08_freeze_count'] = 155
    scene['water08_freeze_production_installed'] = False
    scene['water08_freeze_note'] = 'Only 155 specified vertices in 36 water shape keys held at Basis; head and visual failures unresolved.'
    obj['water08_freeze_status'] = 'DIAGNOSTIC_GEOMETRY_ONLY'
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    result = {
        'status':'CANDIDATE_SAVED_EVALUATION_PENDING', 'candidate_metadata':'DIAGNOSTIC_GEOMETRY_ONLY',
        'source':str(SOURCE), 'source_sha256':SOURCE_SHA, 'source_unchanged_after_save':digest(SOURCE)==SOURCE_SHA,
        'candidate':str(OUTPUT), 'candidate_sha256':digest(OUTPUT), 'selection_npz':str(NPZ), 'selection_sha256':digest(NPZ),
        'mutations':'Exactly ring_vertices in all 36 C_flow_and_real_impact shape keys reset to Basis, plus diagnostic custom metadata',
        'bake_run':False, 'render_run':False, 'production_installed':False,
        'build':{'source_mesh_coordinates_sha256':source_mesh_hash, 'source_basis_sha256':source_base_hash,
                 'source_render_triangles_sha256':hash_array(f), 'source_core_world_sha256':h.shape_hash(scene.objects[CORE]),
                 'unchanged_outside_ring_key_hashes':unchanged_hashes, 'maximum_canceled_displacement_m':max(canceled),
                 'canceled_maximum_by_frame_m':canceled, 'shape_key_count':len(keys),
                 'fall_attribute_sha256':hash_array(attribute_values(me,'H07_fall')),
                 'pond_attribute_sha256':hash_array(attribute_values(me,'H07_pond')),
                 'water_materials':[m.name for m in me.materials], 'water_modifiers':[(m.name,m.type) for m in obj.modifiers],
                 'objects_count':len(scene.objects), 'scene_frame_saved':scene.frame_current,
                 'animation_action':me.shape_keys.animation_data.action.name,
                 'all_other_geometry_and_scene_settings':'No other mutation operators or property assignments used'},
        'frames':[]}
    write(result)
    print('FREEZE08_BUILD', json.dumps({k:result[k] for k in ('status','candidate_sha256','source_unchanged_after_save')}), flush=True)

def inspect():
    started = time.perf_counter()
    assert bpy.app.background and digest(SOURCE) == SOURCE_SHA
    result = json.loads(REPORT.read_text(encoding='utf-8'))
    result['frames'] = []
    assert digest(OUTPUT) == result['candidate_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT))
    scene = bpy.context.scene
    obj = scene.objects[NAME]
    me = obj.data
    base_local = coords(me.shape_keys.key_blocks[0].data)
    base = world(base_local, obj.matrix_world)
    f = faces_of(me)
    ring = np.load(NPZ)['ring_vertices'].astype(np.int32)
    fall = attribute_values(me, 'H07_fall')
    pond = attribute_values(me, 'H07_pond')
    active = (fall > 0) | (pond > 0)
    fixed = ~active
    ringmask = np.zeros(len(base), bool)
    ringmask[ring] = True
    active_faces = np.flatnonzero(np.any(active[f], axis=1))
    adjacent_faces = np.flatnonzero(np.any(ringmask[f], axis=1))
    n0 = normals(base, f)
    cross0 = np.linalg.norm(n0, axis=1)
    valid = cross0 > THRESHOLD
    ring_rel = base[ring] - np.array(h.LIP)
    ring_sc = np.column_stack((ring_rel @ np.array(h.DOWN), ring_rel @ np.array(h.CROSS), base[ring, 2]))
    topological_edges = np.concatenate((f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]))
    topological_edges.sort(axis=1)
    _, edge_counts = np.unique(topological_edges,axis=0,return_counts=True)
    immutable = result['build']
    assert hash_array(coords(me.vertices)) == immutable['source_mesh_coordinates_sha256']
    assert hash_array(base_local) == immutable['source_basis_sha256']
    assert hash_array(f) == immutable['source_render_triangles_sha256']
    assert hash_array(fall) == immutable['fall_attribute_sha256']
    assert hash_array(pond) == immutable['pond_attribute_sha256']
    assert h.shape_hash(scene.objects[CORE]) == immutable['source_core_world_sha256']
    for i in range(1,37):
        a = coords(me.shape_keys.key_blocks[i].data)
        assert hash_array(a[~ringmask]) == immutable['unchanged_outside_ring_key_hashes'][i-1]
        assert np.array_equal(a[ring],base_local[ring])
    result['reopen_preservation'] = {'base_mesh_and_basis_unchanged':True, 'render_triangle_indices_unchanged':True,
        'all_36_keys_outside_ring_unchanged':True, 'fall_pond_attributes_unchanged':True,
        'core_world_geometry_unchanged':True, 'source_file_unchanged':digest(SOURCE)==SOURCE_SHA,
        'water_materials_unchanged':[m.name for m in me.materials]==immutable['water_materials'],
        'water_modifiers_unchanged':[list((m.name,m.type)) for m in obj.modifiers]==immutable['water_modifiers'],
        'scene_objects_count_unchanged':len(scene.objects)==immutable['objects_count'],
        'shape_key_action_name_unchanged':me.shape_keys.animation_data.action.name==immutable['animation_action']}
    result['geometry'] = {'vertices':len(base),'polygons':len(me.polygons),'render_triangles':len(f),
        'active_vertices':int(active.sum()),'fixed_external_vertices':int(fixed.sum()), 'frozen_vertices':len(ring),
        'frozen_fraction_of_active':float(len(ring)/active.sum()), 'frozen_world_bounds_m':bounds(base[ring]),
        'frozen_local_s_c_z_bounds_m':bounds(ring_sc), 'freeze_adjacent_triangles':len(adjacent_faces),
        'freeze_adjacent_basis_area_m2':float(cross0[adjacent_faces].sum()/2),
        'all_active_related_triangles':len(active_faces),'normal_base_cross_magnitude_threshold':THRESHOLD,
        'normal_failure_rule':'Basis cross magnitude > 1e-9 and dot(Basis cross, evaluated cross) < 0',
        'basis_boundary_edges':int((edge_counts==1).sum()), 'basis_nonmanifold_edges':int((edge_counts!=2).sum())}
    result['status'] = 'ACTUAL_EVALUATION_RUNNING'
    write(result)

    # Actual render-triangle rock BVHs; omit distant rocks by active-region AABB.
    active_bounds = np.array(bounds(base[np.unique(f[active_faces])]))
    rock_prefixes = ('SITE_Core_Continuous','SITE_Cascade_Shoulder_Continuous','SITE_Secondary_Sandstone','SITE_Split_Talus','SITE_Bank_')
    rocks = []
    for rock in scene.objects:
        if rock.type!='MESH' or not rock.name.startswith(rock_prefixes):
            continue
        box=np.array(h.aabb(rock))
        if not np.all((box[:,1] >= active_bounds[:,0]-.06)&(box[:,0] <= active_bounds[:,1]+.06)):
            continue
        rocks.append((rock.name,h.render_bvh(rock),box))
    result['collision_method'] = {
        'rocks':[r[0] for r in rocks], 'faces':'Every render triangle touching any of 6620 active vertices',
        'samples_per_face':4, 'sample_locations':['centroid','edge01_midpoint','edge12_midpoint','edge20_midpoint'],
        'classification':'Actual rock render-triangle BVH nearest point plus 3-direction parity for negative signed side; >0.5 mm = confirmed inside; nearer samples retained as contact/uncertainty, never silently pass',
        'baseline':'Same face id and barycentric sample at immutable Basis; inherited contacts retained separately',
        'limitation':'Four samples per triangle do not prove continuous triangle interiors or edges have no unsampled intersection; no exact all-pairs intersection proof'}

    bary = np.array([[1/3,1/3,1/3],[.5,.5,0],[0,.5,.5],[.5,0,.5]],np.float64)
    contact_epsilon = .0005
    def sample_collision(v):
        triangles = v[f[active_faces]]
        samples = np.einsum('sj,fjk->fsk',bary,triangles).reshape((-1,3))
        inside = {}
        near = {}
        uncertain = {}
        for name, tree, box in rocks:
            eligible = np.flatnonzero(np.all((samples>=box[:,0]-.001)&(samples<=box[:,1]+.001),axis=1))
            for sid in eligible:
                p=Vector(samples[sid])
                hit=tree.find_nearest(p)
                if hit[0] is None:
                    continue
                signed=(p-hit[0]).dot(hit[1])
                token=(name,int(sid))
                if hit[3] <= contact_epsilon:
                    near[token]=float(hit[3])
                elif signed < 0:
                    par=h.parity(tree,p)
                    if all(k%2 for k in par):
                        inside[token]=float(hit[3])
                    elif any(k%2 for k in par):
                        uncertain[token]={'nearest_m':float(hit[3]),'parity':par}
        return inside,near,uncertain,samples

    def collision_examples(items,samples,limit=20):
        out=[]
        for (rock,sid),detail in list(items.items())[:limit]:
            out.append({'rock':rock,'triangle':int(active_faces[sid//4]), 'sample_kind':int(sid%4),
                        'world_point_m':samples[sid].tolist(),'detail':detail})
        return out

    base_inside,base_near,base_uncertain,base_samples=sample_collision(base)
    basis_collision_cache={hash_array(f):(base_inside,base_near,base_uncertain,base_samples)}
    result['basis_face_contact']={'inside_samples':len(base_inside),'near_contact_samples':len(base_near),
        'uncertain_parity_samples':len(base_uncertain),'inside_examples':collision_examples(base_inside,base_samples),
        'near_examples':collision_examples(base_near,base_samples),'uncertain_examples':collision_examples(base_uncertain,base_samples)}
    print('FREEZE08_BASE_COLLISION', json.dumps({k:v for k,v in result['basis_face_contact'].items() if not k.endswith('examples')}), flush=True)
    np.savez_compressed(ROOT/'qa/water08-freeze-sampling.npz',ring_vertices=ring,active_triangles=active_faces,
        render_triangles=f,freeze_adjacent_triangles=adjacent_faces,barycentric_samples=bary)

    # Probe vertical pairs at every upward pond triangle centroid and an independent 31x31 patch grid.
    tri0=base[f]
    cents=tri0.mean(axis=1)
    pond_faces=np.any((pond>0)[f],axis=1)&valid&(n0[:,2]/np.maximum(cross0,1e-30)>.35)&(cents[:,2]<-5.48)
    pond_xy=cents[pond_faces,:2]
    bb=np.array(bounds(base[ring]))
    gx,gy=np.meshgrid(np.linspace(bb[0,0]-.02,bb[0,1]+.02,31),np.linspace(bb[1,0]-.02,bb[1,1]+.02,31))
    xy=np.unique(np.round(np.vstack((pond_xy,np.column_stack((gx.ravel(),gy.ravel())))),8),axis=0)
    def vertical_hits(tree,p):
        origin=Vector((float(p[0]),float(p[1]),-5.40))
        direction=Vector((0,0,-1))
        hits=[]
        for _ in range(16):
            hit=tree.ray_cast(origin,direction,max(0,float(origin.z+6.4)))
            if hit[0] is None:break
            hits.append((float(hit[0].z),float(hit[1].z),int(hit[2])))
            origin=hit[0]+direction*.000002
        return hits
    def pond_pair(hits):
        # A falling branch can add crossings above the pond. Measure the actual
        # lowest pond entry/exit pair, not an unrelated branch crossing.
        candidates=[(hits[j],hits[j+1]) for j in range(len(hits)-1)
                    if -.20>hits[j+1][1] and hits[j][1]>.20
                    and -5.95<hits[j][0]<-5.48 and hits[j][0]>hits[j+1][0]]
        return candidates[-1] if candidates else None
    base_tree=tree_for(base,f)
    baseline_hits=[vertical_hits(base_tree,p) for p in xy]
    baseline_pairs=[pond_pair(q) for q in baseline_hits]
    pair_mask=np.array([q is not None for q in baseline_pairs])
    baseline_thick=np.array([q[0][0]-q[1][0] for q in baseline_pairs if q is not None])
    pair_xy=xy[pair_mask]
    np.savez_compressed(ROOT/'qa/water08-freeze-thickness-sampling.npz',probe_xy_m=pair_xy,
        basis_vertical_thickness_m=baseline_thick,all_candidate_xy_m=xy,baseline_pair_mask=pair_mask)

    # Inward normal rays on all nondegenerate freeze-adjacent faces provide another actual shell-thickness measurement.
    inward_faces=adjacent_faces[valid[adjacent_faces]]
    def inward_probe(tree,v):
        ns=normals(v,f[inward_faces]);length=np.linalg.norm(ns,axis=1)
        cent=v[f[inward_faces]].mean(axis=1)
        values=[]; failures=[]
        for j,tid in enumerate(inward_faces):
            if length[j]<=1e-15:
                failures.append({'triangle':int(tid),'reason':'degenerate_evaluated'});continue
            direction=Vector(-ns[j]/length[j]);p=Vector(cent[j])+direction*.000002
            hit=tree.ray_cast(p,direction,1.5)
            if hit[0] is None:
                failures.append({'triangle':int(tid),'reason':'no_opposite_hit_within_1.5m'});continue
            exit_dot=hit[1].dot(direction)
            thickness=float(hit[3]+.000002)
            if exit_dot<=0:
                failures.append({'triangle':int(tid),'reason':'opposite_hit_not_exit','distance_m':thickness,'dot':exit_dot,'hit_triangle':int(hit[2])})
            else:values.append((int(tid),thickness))
        return values,failures
    base_inward,base_inward_bad=inward_probe(base_tree,base)
    result['thickness_method']={'vertical_candidates':len(xy),'baseline_regular_top_bottom_pairs':len(pair_xy),
        'baseline_unpaired_or_multilayer_excluded':int((~pair_mask).sum()),'vertical_probe_xy_bounds_m':bounds(np.column_stack((pair_xy,np.zeros(len(pair_xy))))),
        'ray_from_z_m':-5.4,'ray_to_z_m':-6.4,'ray_advance_epsilon_m':.000002,
        'pair_rule':'Lowest consecutive entry nz > 0.20 / exit nz < -0.20 with top z in (-5.95,-5.48), ordered z(top) > z(bottom); separate overlying branch crossings counted',
        'baseline_probes_with_additional_overlying_hits':sum(len(q)>2 for q,ok in zip(baseline_hits,pair_mask) if ok),
        'basis_vertical_thickness_m':stats(baseline_thick),'inward_probe_faces':len(inward_faces),
        'basis_inward_thickness_m':stats([q[1] for q in base_inward]),'basis_inward_failures':base_inward_bad,
        'limits':['Vertical probes only where Basis has a regular pond top/bottom pair; disconnected overlying branch crossings do not represent pond thickness and are counted separately',
                  'Normal rays can be affected by micron triangles or concave shell shape; baseline exceptions retained',
                  'Finite ray samples are actual local measurements, not a proof of all continuous surface thickness or global self-intersection absence']}
    print('FREEZE08_BASE_THICKNESS',json.dumps({k:v for k,v in result['thickness_method'].items() if k in ('vertical_candidates','baseline_regular_top_bottom_pairs','basis_vertical_thickness_m','inward_probe_faces','basis_inward_thickness_m')}),flush=True)
    base_bad_inward={q['triangle'] for q in base_inward_bad}
    base_inward_dict=dict(base_inward)
    basis_inward_cache={hash_array(f):(base_inward,base_inward_bad)}
    original_f=f.copy()
    original_poly_loops=np.array([l.vertex_index for l in me.loops],np.int32)
    result['render_triangulation_variants']=[]
    write(result)

    for frame in range(1,37):
        scene.frame_set(frame);bpy.context.view_layer.update()
        ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
        actual_f=faces_of(mesh)
        v_local=coords(mesh.vertices);v=world(v_local,obj.matrix_world)
        assert actual_f.shape==original_f.shape and len(mesh.polygons)==len(me.polygons)
        assert np.array_equal(np.array([l.vertex_index for l in mesh.loops],np.int32),original_poly_loops), 'Polygon topology changed'
        f=actual_f
        active_faces=np.flatnonzero(np.any(active[f],axis=1))
        adjacent_faces=np.flatnonzero(np.any(ringmask[f],axis=1))
        n0=normals(base,f);cross0=np.linalg.norm(n0,axis=1);valid=cross0>THRESHOLD
        inward_faces=adjacent_faces[valid[adjacent_faces]]
        variant=hash_array(f)
        if variant not in basis_collision_cache:
            basis_collision_cache[variant]=sample_collision(base)
            basis_inward_cache[variant]=inward_probe(tree_for(base,f),base)
            ted=np.concatenate((f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]));ted.sort(axis=1)
            _,count=np.unique(ted,axis=0,return_counts=True)
            assert (count==2).all(), 'Evaluated triangles no longer manifold'
            result['render_triangulation_variants'].append({'first_frame':frame,'sha256':variant,
                'different_from_original_triangle_indices':np.flatnonzero(np.any(f!=original_f,axis=1)).tolist(),
                'boundary_edges':int((count==1).sum()),'nonmanifold_edges':int((count!=2).sum())})
        base_inside,base_near,base_uncertain,base_samples=basis_collision_cache[variant]
        base_inward,base_inward_bad=basis_inward_cache[variant]
        base_bad_inward={q['triangle'] for q in base_inward_bad};base_inward_dict=dict(base_inward)
        nv=normals(v,f);length=np.linalg.norm(nv,axis=1);dot=np.einsum('ij,ij->i',n0,nv)
        bad=np.flatnonzero(valid&(dot<0))
        inside,near,uncertain,samples=sample_collision(v)
        new_inside={k:d for k,d in inside.items() if k not in base_inside}
        worsened={k:{'basis_m':base_inside[k],'frame_m':d} for k,d in inside.items() if k in base_inside and d>base_inside[k]+.00001}
        new_near={k:d for k,d in near.items() if k not in base_near}
        new_uncertain={k:d for k,d in uncertain.items() if k not in base_uncertain}
        tree=tree_for(v,f)
        vals=[];pair_failures=[];ratio=[];min_record=None;extra_crossings=0
        for i,p in enumerate(pair_xy):
            hits=vertical_hits(tree,p)
            pair=pond_pair(hits)
            if pair is None:
                pair_failures.append({'probe':i,'xy_m':p.tolist(),'hits':hits})
            else:
                if len(hits)>2:extra_crossings+=1
                thick=pair[0][0]-pair[1][0];vals.append(thick);ratio.append(thick/baseline_thick[i])
                if min_record is None or thick<min_record['thickness_m']:
                    min_record={'probe':i,'xy_m':p.tolist(),'thickness_m':thick,'basis_thickness_m':float(baseline_thick[i]),'pond_pair':pair,'all_hits':hits}
        iv,ibad=inward_probe(tree,v)
        inewbad=[q for q in ibad if q['triangle'] not in base_bad_inward]
        iratios=[d/base_inward_dict[tid] for tid,d in iv if tid in base_inward_dict]
        info={'frame':frame,'vertices':len(v),'polygons':len(mesh.polygons),'polygon_topology_matches_basis':True,
              'render_triangulation_matches_basis':np.array_equal(f,original_f),
              'render_triangles_changed_from_basis':int(np.any(f!=original_f,axis=1).sum()),
              'boundary_edges':int((edge_counts==1).sum()),'nonmanifold_edges':int((edge_counts!=2).sum()),
              'fixed_207943_max_move_m':float(np.abs(v[fixed]-base[fixed]).max()),
              'frozen_155_max_move_m':float(np.abs(v[ring]-base[ring]).max()),
              'normal_flipped_triangles':bad.tolist(),'new_degenerate_triangles':int((valid&(length<=1e-15)).sum()),
              'max_remaining_active_move_m':float(np.linalg.norm(v[active]-base[active],axis=1).max()),
              'face_collision':{'inside_samples':len(inside),'inherited_inside_samples':len(inside)-len(new_inside),
                  'new_inside_samples':len(new_inside),'new_inside_examples':collision_examples(new_inside,samples),
                  'worsened_inherited_inside_samples':len(worsened),'worsened_examples':collision_examples(worsened,samples),
                  'near_contact_samples':len(near),'new_near_samples':len(new_near),'new_near_examples':collision_examples(new_near,samples),
                  'uncertain_samples':len(uncertain),'new_uncertain_samples':len(new_uncertain),'new_uncertain_examples':collision_examples(new_uncertain,samples)},
              'vertical_thickness_m':stats(vals),'vertical_ratio_to_basis':stats(ratio),'minimum_vertical_pair':min_record,
              'vertical_probes_with_additional_overlying_hits':extra_crossings,
              'vertical_pair_failures':len(pair_failures),'vertical_pair_failure_examples':pair_failures[:20],
              'inward_normal_thickness_m':stats([q[1] for q in iv]),'inward_ratio_to_basis':stats(iratios),
              'inward_probe_failures':len(ibad),'new_inward_probe_failures':len(inewbad),'new_inward_failure_examples':inewbad[:20]}
        result['frames'].append(info)
        write(result)
        print('FREEZE08_FRAME',json.dumps({'frame':frame,'normal_flips':len(bad),'new_inside':len(new_inside),
              'vertical_pair_failures':len(pair_failures),'vertical_min_m':info['vertical_thickness_m']['min'],
              'new_inward_failures':len(inewbad)}),flush=True)
        ev.to_mesh_clear()
    frames=result['frames']
    normals_pass=all(not q['normal_flipped_triangles'] and not q['new_degenerate_triangles'] for q in frames)
    fixed_pass=all(q['fixed_207943_max_move_m']==0 and q['frozen_155_max_move_m']==0 for q in frames)
    collisions_pass=all(q['face_collision']['new_inside_samples']==0 and q['face_collision']['worsened_inherited_inside_samples']==0 and q['face_collision']['new_uncertain_samples']==0 for q in frames)
    thickness_pass=all(q['vertical_pair_failures']==0 and q['new_inward_probe_failures']==0 and q['vertical_thickness_m']['min']>0.000002 for q in frames)
    result['actual_36frame_summary']={'normal_threshold_pass':normals_pass,'fixed_vertices_pass':fixed_pass,
        'sampled_face_interior_no_new_inside_pass':collisions_pass,'sampled_local_thickness_pass':thickness_pass,
        'topology_closed_manifold_pass':result['geometry']['basis_nonmanifold_edges']==0,
        'new_near_contact_samples_max':max(q['face_collision']['new_near_samples'] for q in frames),
        'vertical_minimum_over_all_frames_m':min(q['vertical_thickness_m']['min'] for q in frames),
        'elapsed_seconds':time.perf_counter()-started}
    result['status']='PASS_BOUNDED_GEOMETRY_DIAGNOSTIC_NOT_PRODUCTION' if normals_pass and fixed_pass and collisions_pass and thickness_pass else 'FAIL_OR_UNRESOLVED_LOCAL_GEOMETRY_KEEP_DIAGNOSTIC'
    result['source_unchanged_after_checks']=digest(SOURCE)==SOURCE_SHA
    result['candidate_unchanged_after_checks']=digest(OUTPUT)==result['candidate_sha256']
    result['limitations']=['No bake, render, visual evaluation, or installation performed',
        'Unresolved 07 motion hydraulic head and glass ribbon/opaque foam visual failures remain',
        'Integer frames 1–36 only; subframes and animation longer than 1.5 seconds untested',
        'Fixed patch and animation transition visibility cannot be judged without a later authorized render',
        'Finite collision and thickness samples do not prove continuous global self-intersection absence']
    write(result)
    print('FREEZE08_RESULT',json.dumps({'status':result['status'],**result['actual_36frame_summary']}),flush=True)

if __name__=='__main__':
    mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'check'
    if mode=='build':build()
    elif mode=='check':inspect()
    else:raise ValueError(mode)
