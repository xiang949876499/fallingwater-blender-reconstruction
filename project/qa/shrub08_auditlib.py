"""Saved-scene fingerprints and physical checks for isolated shrub08 only."""
import bpy
import json
import hashlib
import math
import struct
import re
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def plain(value):
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, bpy.types.ID):
        return [value.bl_rna.identifier, value.name_full]
    if isinstance(value, set):
        return sorted(plain(v) for v in value)
    if hasattr(value, 'to_dict'):
        return {k: plain(v) for k, v in value.to_dict().items()}
    try:
        return [plain(v) for v in value]
    except TypeError:
        return str(value)


def props(owner):
    result = {}
    for prop in owner.bl_rna.properties:
        key = prop.identifier
        if prop.is_readonly or key in ('rna_type', 'name', 'name_full'):
            continue
        if prop.type == 'COLLECTION':
            continue
        value = getattr(owner, key)
        if prop.type == 'POINTER' and value is not None and not isinstance(value, bpy.types.ID):
            continue
        result[key] = plain(value)
    if hasattr(owner, 'items'):
        try:
            result['custom_properties'] = {k: plain(v) for k, v in owner.items()}
        except TypeError:
            # Some RNA structs expose items() without supporting IDProperties.
            pass
    return result


def block_hash(collection, property_name, components, dtype):
    array = np.empty(len(collection)*components, dtype=dtype)
    if len(array):
        collection.foreach_get(property_name, array)
    return hashlib.sha256(array.tobytes()).hexdigest()


def mesh_fingerprint(mesh):
    attrs = []
    mapping = {'FLOAT': ('value', 1, np.float32), 'INT': ('value', 1, np.int32),
               'INT8': ('value', 1, np.int32), 'INT32_2D': ('value', 2, np.int32),
               'BOOLEAN': ('value', 1, np.bool_), 'FLOAT_VECTOR': ('vector', 3, np.float32),
               'FLOAT2': ('vector', 2, np.float32), 'FLOAT_COLOR': ('color', 4, np.float32),
               'BYTE_COLOR': ('color', 4, np.float32), 'QUATERNION': ('value', 4, np.float32),
               'FLOAT4X4': ('value', 16, np.float32)}
    for attribute in mesh.attributes:
        assert attribute.data_type in mapping, (mesh.name, attribute.name, attribute.data_type)
        attrs.append((attribute.name, attribute.domain, attribute.data_type,
                      block_hash(attribute.data, *mapping[attribute.data_type])))
    keys = None
    if mesh.shape_keys:
        keys = [(k.name, props(k), block_hash(k.data, 'co', 3, np.float32)) for k in mesh.shape_keys.key_blocks]
    return digest({'settings': props(mesh),
                   'vertices': block_hash(mesh.vertices, 'co', 3, np.float32),
                   'edges': block_hash(mesh.edges, 'vertices', 2, np.int32),
                   'loops': block_hash(mesh.loops, 'vertex_index', 1, np.int32),
                   'polygon_start': block_hash(mesh.polygons, 'loop_start', 1, np.int32),
                   'polygon_size': block_hash(mesh.polygons, 'loop_total', 1, np.int32),
                   'polygon_material': block_hash(mesh.polygons, 'material_index', 1, np.int32),
                   'polygon_smooth': block_hash(mesh.polygons, 'use_smooth', 1, np.bool_),
                   'attributes': attrs, 'shape_keys': keys,
                   'materials': [m.name if m else None for m in mesh.materials]})


def node_tree_state(tree):
    if tree is None:
        return None
    nodes = []
    for node in tree.nodes:
        node_state = {'name': node.name, 'properties': props(node),
                      'inputs': [(s.identifier, plain(s.default_value)) for s in node.inputs if hasattr(s, 'default_value')]}
        if hasattr(node, 'color_ramp'):
            node_state['ramp'] = {'properties': props(node.color_ramp),
                                  'elements': [(e.position, list(e.color)) for e in node.color_ramp.elements]}
        nodes.append(node_state)
    return {'nodes': nodes, 'links': [(l.from_node.name, l.from_socket.identifier, l.to_node.name, l.to_socket.identifier) for l in tree.links]}


def snapshot():
    scene = bpy.context.scene
    mesh_states = {mesh.name: mesh_fingerprint(mesh) for mesh in bpy.data.meshes if mesh.users}
    data_states = {}
    for obj in scene.objects:
        if obj.data and obj.type != 'MESH' and obj.data.name not in data_states:
            state = props(obj.data)
            if obj.type == 'CAMERA':
                state['dof'] = props(obj.data.dof)
            if obj.type in ('FONT', 'CURVE', 'SURFACE'):
                state['splines'] = [(props(s), [props(p) for p in s.bezier_points], [props(p) for p in s.points]) for s in obj.data.splines]
            data_states[obj.data.name] = digest(state)
    objects = {}
    for obj in scene.objects:
        objects[obj.name] = {'properties': props(obj),
            'world_matrix': [list(row) for row in obj.matrix_world],
            'data_hash': mesh_states.get(obj.data.name) if obj.type == 'MESH' else data_states.get(obj.data.name) if obj.data else None,
            'material_slots': [(slot.link, slot.material.name if slot.material else None) for slot in obj.material_slots],
            'collections': sorted(c.name for c in obj.users_collection),
            'modifiers': [(m.name, m.type, props(m)) for m in obj.modifiers],
            'constraints': [(c.name, c.type, props(c)) for c in obj.constraints],
            'animation': props(obj.animation_data) if obj.animation_data else None,
            'vertex_groups': [(v.name, v.index, v.lock_weight) for v in obj.vertex_groups]}
    materials = {m.name: digest([props(m), node_tree_state(m.node_tree)]) for m in bpy.data.materials}
    worlds = {w.name: digest([props(w), node_tree_state(w.node_tree)]) for w in bpy.data.worlds}
    image_states = {i.name: [i.filepath, i.source, i.colorspace_settings.name, i.alpha_mode] for i in bpy.data.images}
    actions = {}
    for action in bpy.data.actions:
        curves = []
        for layer in action.layers:
            for strip in layer.strips:
                for slot in action.slots:
                    bag = strip.channelbag(slot)
                    if bag:
                        curves.extend((f.data_path, f.array_index, [(list(k.co), k.interpolation, list(k.handle_left), list(k.handle_right)) for k in f.keyframe_points]) for f in bag.fcurves)
        actions[action.name] = digest([props(action), curves])
    global_state = {'scene': props(scene), 'render': props(scene.render), 'cycles': props(scene.cycles),
                    'view': props(scene.view_settings), 'worlds': worlds,
                    'materials': materials, 'images': image_states, 'actions': actions,
                    'collections': {c.name: props(c) for c in bpy.data.collections},
                    'texts': {t.name: hashlib.sha256(t.as_string().encode()).hexdigest() for t in bpy.data.texts}}
    return {'objects': objects, 'meshes': mesh_states, 'global': global_state}


def compare_snapshots(before, after, targets):
    assert set(before['objects']) == set(after['objects']), 'Scene object set changed'
    changed = []
    for name in before['objects']:
        a, b = before['objects'][name], after['objects'][name]
        if a == b:
            continue
        changed.append(name)
        assert name in targets, ('Non-target object changed', name)
        stripped = []
        for value in (a, b):
            value = json.loads(json.dumps(value))
            value.pop('data_hash')
            value['properties'].pop('data', None)
            # RNA dimensions is writable but is derived from the new mesh
            # bounds and unchanged matrix. Replacing data necessarily changes it.
            value['properties'].pop('dimensions', None)
            stripped.append(value)
        assert stripped[0] == stripped[1], ('Target property other than data changed', name,
            [k for k in stripped[0] if stripped[0][k] != stripped[1].get(k)])
    assert before['global'] == after['global'], 'Scene/material/image/camera/lighting/animation/config state changed'
    assert all(after['meshes'].get(k) == v for k, v in before['meshes'].items()), 'Existing shared mesh changed'
    return changed


def world_geometry(objects, evaluated=False):
    verts, faces, owners = [], [], []
    deps = bpy.context.evaluated_depsgraph_get() if evaluated else None
    for obj in objects:
        if obj.type != 'MESH':
            continue
        actual = obj.evaluated_get(deps) if evaluated else obj
        mesh = actual.to_mesh() if evaluated else actual.data
        offset = len(verts)
        verts.extend(actual.matrix_world@v.co for v in mesh.vertices)
        faces.extend([offset+i for i in poly.vertices] for poly in mesh.polygons)
        owners.extend([obj.name]*len(mesh.polygons))
        if evaluated:
            actual.to_mesh_clear()
    return verts, faces, owners


def world_bvh(objects, evaluated=False):
    verts, faces, owners = world_geometry(objects, evaluated)
    return BVHTree.FromPolygons(verts, faces), owners


def physical_hash(obj):
    actual = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = actual.to_mesh()
    mesh.calc_loop_triangles()
    h = hashlib.sha256()
    for tri in mesh.loop_triangles:
        for index in tri.vertices:
            h.update(struct.pack('<3f', *(actual.matrix_world@mesh.vertices[index].co)))
    result = {'sha256': h.hexdigest(), 'triangles': len(mesh.loop_triangles)}
    actual.to_mesh_clear()
    return result


def bounds(obj):
    points = [obj.matrix_world@Vector(v) for v in obj.bound_box]
    return [f(p[i] for p in points) for i in range(3) for f in (min, max)]


def box_overlap(a, b, expand=0):
    return all(a[2*i] <= b[2*i+1]+expand and a[2*i+1] >= b[2*i]-expand for i in range(3))


def path_boundary_distance(root, path_objects):
    nearest = []
    for path in path_objects:
        points = [path.matrix_world@v.co for v in path.data.vertices]
        counts = Counter(tuple(sorted((a,b))) for p in path.data.polygons for a,b in zip(list(p.vertices), list(p.vertices)[1:]+list(p.vertices)[:1]))
        best = math.inf
        for (i,j), count in counts.items():
            if count != 1:
                continue
            a,b = points[i],points[j]
            dx,dy=b.x-a.x,b.y-a.y
            t=max(0,min(1,((root.x-a.x)*dx+(root.y-a.y)*dy)/max(1e-12,dx*dx+dy*dy)))
            best=min(best,math.hypot(root.x-a.x-t*dx,root.y-a.y-t*dy))
        if math.isfinite(best):
            nearest.append((path.name,best))
    return sorted(nearest,key=lambda x:x[1])


def contact_checks(selection, reports, exclusion):
    scene=bpy.context.scene
    terrain=scene.objects['SITE_Continuous_BearRun_Terrain']
    tbvh,_=world_bvh([terrain],True)
    paths=[o for o in scene.objects if o.type=='MESH' and o.name.startswith(('SITE_Path_','SITE_Bridge_'))]
    pathbvh,_=world_bvh(paths,True)
    hard=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and o.name.startswith(('MAIN_','GUEST_','SITE_Core_','SITE_Cascade_Shoulder_Continuous','SITE_Bridge_','WATER_'))]
    hard_bounds={o.name:bounds(o) for o in hard}
    records=[]
    def ground_gap(point):
        hit=tbvh.ray_cast(Vector((point.x,point.y,100)),Vector((0,0,-1)),250)[0]
        return point.z-hit.z if hit is not None else None
    for row in selection:
        leaf=scene.objects[row['leaf_object']];branch=scene.objects[row['branch_object']]
        root=leaf.matrix_world.translation;scale=row['scale'][0]
        record={'object':leaf.name,'root':list(root),'failures':[]}
        record['root_anchor_gap_m']=ground_gap(root)
        if abs(record['root_anchor_gap_m']+.012)>.00005:record['failures'].append('ROOT_ANCHOR_CHANGED')
        vertices=[o.matrix_world@v.co for o in (branch,leaf) for v in o.data.vertices]
        leaf_gaps=[ground_gap(leaf.matrix_world@v.co) for v in leaf.data.vertices]
        leaf_gaps.extend(ground_gap(leaf.matrix_world@poly.center) for poly in leaf.data.polygons)
        record['leaf_ground_sample_count']=len(leaf_gaps)
        record['leaf_ground_gap_minmax_m']=[min(leaf_gaps),max(leaf_gaps)]
        if min(leaf_gaps)<.012:record['failures'].append('LEAF_TERRAIN_GAP_UNDER_12MM')
        branch_samples=[(v.co,ground_gap(branch.matrix_world@v.co)) for v in branch.data.vertices]
        branch_samples.extend((poly.center,ground_gap(branch.matrix_world@poly.center)) for poly in branch.data.polygons)
        above=[gap for co,gap in branch_samples if co.z>.080]
        basal=[gap for co,gap in branch_samples if co.z<=.080]
        record['above_basal_branch_ground_gap_min_m']=min(above)
        record['basal_branch_ground_gap_minmax_m']=[min(basal),max(basal)]
        if min(above)<.002:record['failures'].append('ABOVE_BASAL_BRANCH_BURIED')
        if min(basal)<-.060 or min(basal)>.002:record['failures'].append('ROOT_BASE_CONTACT_FAILURE')
        leaf_bvh,_=world_bvh([leaf]);branch_bvh,_=world_bvh([branch])
        leaf_overlap=tbvh.overlap(leaf_bvh)
        branch_overlap=tbvh.overlap(branch_bvh)
        nonbasal_overlap=[pair for pair in branch_overlap if min(branch.data.vertices[i].co.z for i in branch.data.polygons[pair[1]].vertices)>.080]
        record['terrain_triangle_intersections']={'leaf':len(leaf_overlap),'branch_basal_allowed':len(branch_overlap)-len(nonbasal_overlap),'branch_above_basal':len(nonbasal_overlap)}
        if leaf_overlap or nonbasal_overlap:record['failures'].append('ABOVE_GROUND_MESH_TERRAIN_INTERSECTION')
        bb=[f(v[i] for v in vertices) for i in range(3) for f in (min,max)]
        overlaps=[];tested=[]
        candidate_bvh,_=world_bvh([branch,leaf])
        for obj in hard:
            if not box_overlap(bb,hard_bounds[obj.name]):continue
            hbvh,_=world_bvh([obj],True);pairs=hbvh.overlap(candidate_bvh)
            tested.append(obj.name)
            if pairs:overlaps.append([obj.name,len(pairs)])
        record['hard_objects_aabb_candidates']=tested;record['hard_triangle_overlaps']=overlaps
        if overlaps:record['failures'].append('HARD_OBJECT_INTERSECTION')
        radial=max(math.hypot(v.x-root.x,v.y-root.y) for v in vertices)
        edge=path_boundary_distance(root,paths)
        record['nearest_path_boundary']=edge[:2]
        record['actual_max_crown_radius_m']=radial
        record['conservative_path_xy_clearance_m']=edge[0][1]-radial
        record['actual_mesh_to_path_3d_min_m']=min(pathbvh.find_nearest(v)[3] for v in vertices)
        hit=pathbvh.ray_cast(Vector((root.x,root.y,100)),Vector((0,0,-1)),250)[0]
        record['root_inside_path_projection']=hit is not None
        if hit is not None or record['conservative_path_xy_clearance_m']<.15 or record['actual_mesh_to_path_3d_min_m']<.15:record['failures'].append('PATH_CLEARANCE')
        camera=[(c.name,min((v-c.matrix_world.translation).length for v in vertices)) for c in scene.objects if c.type=='CAMERA']
        record['nearest_camera_actual_vertex_m']=sorted(camera,key=lambda x:x[1])[0]
        camera_bound=min(math.hypot(root.x-c.matrix_world.translation.x,root.y-c.matrix_world.translation.y)-radial for c in scene.objects if c.type=='CAMERA')
        record['conservative_camera_xy_clearance_m']=camera_bound
        if camera_bound<.5:record['failures'].append('CAMERA_CLEARANCE')
        x0,x1,y0,y1=exclusion['bbox']
        excluded=bb[0]<=x1 and bb[1]>=x0 and bb[2]<=y1 and bb[3]>=y0
        record['main_plunge_and_stair_xy_overlap']=excluded
        if excluded:record['failures'].append('PLUNGE_STAIR_EXCLUSION')
        btree,_=world_bvh([branch]);r=reports[str(row['asset'])]
        contacts=[btree.find_nearest(leaf.matrix_world@leaf.data.vertices[l['first_vertex']].co)[3] for l in r['leaves']]
        record['leaf_petiole_contact_max_m']=max(contacts)
        if max(contacts)>.00001:record['failures'].append('PETIOLE_NOT_ON_FINAL_BRANCH')
        records.append(record)
    return records


def route_regression(route, old_bvh, old_owners, new_bvh, new_owners):
    new_hits=[];before_hits=0;after_hits=0;count=0;segments=[]
    def compare(p,d,length,label):
        nonlocal count,before_hits,after_hits
        count+=1
        a,_,ia,da=old_bvh.ray_cast(Vector(p),Vector(d),length)
        b,_,ib,db=new_bvh.ray_cast(Vector(p),Vector(d),length)
        before_hits+=a is not None;after_hits+=b is not None
        if b is not None and (a is None or db<da-.008):
            new_hits.append({'segment':label,'before':old_owners[ia] if a is not None else None,'after':new_owners[ib],'world':list(b)})
    for seg in route['main_segments']+route['supplemental_segments']:
        start_count=len(new_hits)
        walk=bool(seg.get('body_clearance_tested',seg['mode'].startswith('NORMAL')))
        for aa,bb in zip(seg['points'],seg['points'][1:]):
            a,b=Vector(aa),Vector(bb);delta=b-a;steps=max(1,math.ceil(delta.length/.25))
            for j in range(steps+1):
                p=a+delta*j/steps
                for d in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):compare(p,d,.13,seg['id'])
                if walk:
                    bottom=.24 if 'STAIRS' in seg['mode'] else .09
                    for dx,dy in ((0,0),(-.18,0),(.18,0),(0,-.18),(0,.18)):
                        compare((p.x+dx,p.y+dy,p.z-1.6+bottom),(0,0,1),1.71-bottom,seg['id'])
            if delta.length>.001:
                d=delta.normalized();cross=Vector((-d.y,d.x,0))
                if cross.length>.001:cross.normalize()
                offsets=[cross*s+Vector((0,0,h-1.6)) for s in (-.18,0,.18) for h in (.3,.72,1.13,1.6)] if walk else [Vector(),cross*.12,-cross*.12]
                for off in offsets:compare(a+off,d,delta.length,seg['id'])
        segments.append({'id':seg['id'],'mode':seg['mode'],'new_obstacles':len(new_hits)-start_count})
    return {'ray_count':count,'baseline_target_hits':before_hits,'candidate_target_hits':after_hits,
            'new_obstacles':new_hits,'segments':segments,
            'scope':'Full frozen08 segmented route against every modified object; all unmodified objects fingerprinted. Does not claim new room adjacency or GUI acceptance.'}
