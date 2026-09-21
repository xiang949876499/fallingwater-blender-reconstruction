"""One camera/noncamera World + window AREA approximation; isolated candidate."""
import ast, hashlib, json, sys, time
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import eevee_glass
import render_views
SOURCE = ROOT / 'qa/eevee-iteration07-diffuse-world/Fallingwater_preview_diffuse_world_candidate07.blend'
SOURCE_SHA = '4c26a2667e8697282357688cfb7f580a49e01a7b9f9c88c2dee4a60febb02059'
PHYSICAL = ROOT / 'scene/Fallingwater_iteration07.blend'
PHYSICAL_SHA = 'bf50530009e4a93315915815473188c91d891272ef2d8e9e0169b704bd2e2f16'
OUT = ROOT / 'qa/eevee-iteration08-window-preview'
TOKEN = 'FW_PREVIEW_APPROXIMATION_WINDOW08'
BLEND = OUT / 'Fallingwater_preview_window_candidate08.blend'
REPORT = OUT / 'report.json'
tree = ast.parse((ROOT / 'qa/eevee-iteration06-coverage.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in
    {'sha', 'properties', 'light_state', 'object_state'}], type_ignores=[]), 'inspection_helpers', 'exec'))

def canonical_lights(scene):
    result = light_state(scene)
    for value in result.values():
        value['properties'].pop('session_uid', None)
    return result

def value_data(value):
    if isinstance(value, (bool, int, float, str)) or value is None:
        return value
    try:
        return list(value)
    except TypeError:
        return str(value)

def node_data(node):
    excluded = {'name', 'label', 'location', 'dimensions', 'width', 'width_hidden', 'height',
        'select', 'show_options', 'show_preview', 'show_texture', 'hide', 'color',
        'use_custom_color', 'parent', 'warning_propagation'}
    params = {}
    for p in node.bl_rna.properties:
        if p.identifier in excluded or p.identifier.startswith('bl_') or p.type not in {'BOOLEAN', 'INT', 'FLOAT', 'STRING', 'ENUM'}:
            continue
        params[p.identifier] = value_data(getattr(node, p.identifier))
    return {'type': node.bl_idname, 'parameters': params,
        'inputs': [{'name': socket.name, 'identifier': socket.identifier,
            'default': value_data(socket.default_value) if hasattr(socket, 'default_value') else None}
            for socket in node.inputs]}

def world_graph(world):
    return {'nodes': {n.name: node_data(n) for n in world.node_tree.nodes},
        'links': sorted([l.from_node.name, l.from_socket.identifier, l.to_node.name, l.to_socket.identifier]
            for l in world.node_tree.links),
        'use_nodes': world.use_nodes, 'color': list(world.color)}

def digest(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

def surface_branch(world, engine='CYCLES'):
    outputs = [n for n in world.node_tree.nodes if n.type == 'OUTPUT_WORLD' and n.target == engine]
    if not outputs:
        outputs = [n for n in world.node_tree.nodes if n.type == 'OUTPUT_WORLD' and n.target == 'ALL']
    assert len(outputs) == 1
    output = outputs[0]
    assert len(output.inputs['Surface'].links) == 1
    def walk(node):
        data = node_data(node)
        data['links'] = {socket.identifier: {'output': socket.links[0].from_socket.identifier,
            'node': walk(socket.links[0].from_node)} for socket in node.inputs if socket.is_linked}
        return data
    return walk(output.inputs['Surface'].links[0].from_node)

def restore_preview_for_cycles(scene):
    """Candidate-local explicit restore; not integrated in production renderer."""
    info = json.loads(scene['fw_preview_window_restore_json'])
    assert info['token'] == TOKEN
    physical_world = bpy.data.worlds[info['world']]
    assert digest(world_graph(physical_world)) == info['world_graph_sha256']
    removed = []
    for name in info['added_lights']:
        obj = bpy.data.objects.get(name)
        if obj is not None:
            assert obj.type == 'LIGHT' and obj.get('preview_owner') == TOKEN
            data = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if data.users == 0:
                bpy.data.lights.remove(data)
            removed.append(name)
    collection = bpy.data.collections.get(info['collection'])
    if collection is not None:
        assert collection.get('preview_owner') == TOKEN and len(collection.objects) == 0
        bpy.data.collections.remove(collection)
    scene.world = physical_world
    selected = render_views.configure_engine(scene, 'CYCLES', 32, 'CPU')
    scene['fw_preview_window_active'] = False
    return {'removed_lights': removed, 'restored_world': physical_world.name,
        'world_graph_sha256': digest(world_graph(physical_world)), 'engine': scene.render.engine,
        'device': selected, 'production_renderer_integration': False}

def restore_check():
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    assert sha(BLEND) == report['candidate_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    s = bpy.context.scene
    s.frame_set(48)
    s.render.threads_mode = 'FIXED'
    s.render.threads = 4
    bpy.context.view_layer.update()
    assert s.world.get('preview_owner') == TOKEN
    before = canonical_lights(s)
    assert set(before) - set(report['original_lights']) == set(report['restore_spec']['added_lights'])
    result = restore_preview_for_cycles(s)
    bpy.context.view_layer.update()
    assert set(result['removed_lights']) == set(report['restore_spec']['added_lights'])
    assert canonical_lights(s) == report['original_lights']
    assert world_graph(s.world) == report['physical_world_graph']
    assert digest(surface_branch(s.world)) == report['original_cycles_world_branch_sha256']
    assert eevee_glass.cycles_signature() == report['cycles_glass_hash']
    assert eevee_glass.geometry_signature(s) == report['glazing_geometry_hash']
    assert not any(o.get('preview_owner') == TOKEN for o in s.objects)
    assert sha(SOURCE) == SOURCE_SHA and sha(PHYSICAL) == PHYSICAL_SHA
    assert sha(BLEND) == report['candidate_sha256']
    result.update(status='PASS', fresh_reopen=True, original_lights_and_shadow_links_restored=True,
        complete_physical_world_graph_restored=True, cycles_glass_branch_preserved=True,
        glazing_geometry_preserved=True, added_light_count_after=0, renders=0, bakes=0, saves=0,
        source_and_candidate_files_unchanged=True)
    (OUT / 'cycles-restore-check.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print('WINDOW08_RESTORE ' + json.dumps(result), flush=True)

def build():
    OUT.mkdir(exist_ok=True)
    assert sha(SOURCE) == SOURCE_SHA and sha(PHYSICAL) == PHYSICAL_SHA
    assert not BLEND.exists() and not (OUT / 'CAM_MAIN_L3_STUDY_B_EV2p4.png').exists()
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    s = bpy.context.scene
    s.frame_set(48)
    s.render.threads_mode = 'FIXED'
    s.render.threads = 4
    bpy.context.view_layer.update()
    assert s.render.engine == 'BLENDER_EEVEE' and s.eevee.use_raytracing
    assert s.eevee.use_fast_gi and s.eevee.fast_gi_method == 'AMBIENT_OCCLUSION_ONLY'
    assert abs(s.eevee.fast_gi_distance - .6) < 1e-6
    assert not any(o.type == 'LIGHT_PROBE' and o.data.type == 'VOLUME' for o in bpy.data.objects)
    original_lights = canonical_lights(s)
    original_objects = object_state(s)
    original_cycles = eevee_glass.cycles_signature()
    original_geometry = eevee_glass.geometry_signature(s)
    original_ao = {p.identifier: value_data(getattr(s.eevee, p.identifier)) for p in s.eevee.bl_rna.properties if 'fast_gi' in p.identifier}
    original_world = s.world
    inherited_world_branch = digest(surface_branch(original_world))
    # Load only the physical World datablock, never its scene or objects.
    with bpy.data.libraries.load(str(PHYSICAL), link=False) as (available, requested):
        assert 'FW_Lighting_Daylight' in available.worlds
        requested.worlds = ['FW_Lighting_Daylight']
    physical_world = requested.worlds[0]
    physical_world.name = 'FW_WINDOW08_PHYSICAL_WORLD_RESTORE'
    physical_world.use_fake_user = True
    physical_graph = world_graph(physical_world)
    assert digest(surface_branch(physical_world)) == inherited_world_branch
    world = original_world.copy()
    world.name = 'FW_PREVIEW_CAMERA_WORLD_WINDOW08'
    world['preview_owner'] = TOKEN
    s.world = world
    n, links = world.node_tree.nodes, world.node_tree.links
    ee = next(x for x in n if x.type == 'OUTPUT_WORLD' and x.target == 'EEVEE')
    physical_output = next(x for x in n if x.type == 'OUTPUT_WORLD' and x.target == 'CYCLES')
    physical_socket = physical_output.inputs['Surface'].links[0].from_socket
    weak = n['EEVEE weak diffuse ambient']
    assert abs(weak.inputs['Strength'].default_value - .006) < 1e-8
    assert abs(physical_socket.node.inputs['Strength'].default_value - .36) < 1e-6
    camera_path = n.new('ShaderNodeLightPath')
    camera_path.name = 'PREVIEW Is Camera Ray'
    assert 'Is Camera Ray' in camera_path.outputs
    mix = n.new('ShaderNodeMixShader')
    mix.name = 'PREVIEW camera .36 noncamera .006'
    links.new(camera_path.outputs['Is Camera Ray'], mix.inputs[0])
    links.new(weak.outputs[0], mix.inputs[1])
    links.new(physical_socket, mix.inputs[2])
    links.new(mix.outputs[0], ee.inputs['Surface'])
    assert digest(surface_branch(world)) == inherited_world_branch
    collection = bpy.data.collections.new('PREVIEW_APPROXIMATION_WINDOW08')
    collection['preview_owner'] = TOKEN
    s.collection.children.link(collection)
    data = bpy.data.lights.new('FW_PREVIEW_WINDOW08_AREA', 'AREA')
    data.shape = 'RECTANGLE'
    data.size, data.size_y = .75, 1.6
    data.energy = 20.
    data.color = (1., 1., 1.)
    data.normalize = True
    data.use_shadow = True
    light = bpy.data.objects.new('FW_PREVIEW_WINDOW08_AREA', data)
    collection.objects.link(light)
    light.location = (-3.93, (14.0184 + 14.9211) / 2, (5.7 + 7.46) / 2)
    light.rotation_euler = Vector((1, 0, 0)).to_track_quat('-Z', 'Y').to_euler()
    light['preview_owner'] = TOKEN
    light['scope'] = 'PREVIEW_APPROXIMATION: 20 W daylight AREA inside west Study window; not a physical fixture.'
    bpy.context.view_layer.update()
    direction = light.matrix_world.to_3x3() @ Vector((0, 0, -1))
    assert (direction - Vector((1, 0, 0))).length < 1e-5
    deps = bpy.context.evaluated_depsgraph_get()
    rays = []
    for axis in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
        hit, position, normal, face, obj, matrix = s.ray_cast(deps, light.location, Vector(axis), distance=40)
        rays.append({'direction': list(axis), 'object': obj.name if hit else None,
            'distance': (position-light.location).length if hit else None,
            'normal': list(normal) if hit else None, 'face': face if hit else None})
    assert rays[0]['distance'] is None or rays[0]['distance'] > .05
    after_lights = canonical_lights(s)
    assert set(after_lights) - set(original_lights) == {light.name}
    assert all(after_lights[name] == value for name, value in original_lights.items())
    after_objects = object_state(s)
    assert all(after_objects[name] == value for name, value in original_objects.items())
    assert eevee_glass.cycles_signature() == original_cycles
    assert eevee_glass.geometry_signature(s) == original_geometry
    current_ao = {p.identifier: value_data(getattr(s.eevee, p.identifier)) for p in s.eevee.bl_rna.properties if 'fast_gi' in p.identifier}
    assert current_ao == original_ao
    restore = {'token': TOKEN, 'world': physical_world.name, 'world_graph_sha256': digest(physical_graph),
        'added_lights': [light.name], 'collection': collection.name}
    s['fw_preview_window_restore_json'] = json.dumps(restore)
    s['fw_preview_window_active'] = True
    s['fw_eevee_use_fast_gi'] = bool(s.eevee.use_fast_gi)
    s['fw_preview_approximation'] = 'PREVIEW_APPROXIMATION: camera World .36 / all noncamera World .006 and one 20 W window AREA. Requires candidate-local restore before Cycles.'
    s['fw_preview_restore_script'] = str(Path(__file__).resolve())
    s['fw_preview_restore_integration'] = 'NOT_INTEGRATED in production renderer. Explicit restore_preview_for_cycles(scene) required.'
    s.camera = s.objects['CAM_MAIN_L3_STUDY_B']
    s.view_settings.exposure = 2.4
    s.render.resolution_x, s.render.resolution_y, s.render.resolution_percentage = 960, 540, 100
    s.eevee.taa_render_samples = 32
    s.render.image_settings.file_format = 'PNG'
    s.render.image_settings.color_mode = 'RGBA'
    s.render.image_settings.color_depth = '8'
    report = {'status': 'READY_TO_RENDER', 'source_scene': str(SOURCE), 'source_sha256': SOURCE_SHA,
        'physical_source': str(PHYSICAL), 'physical_source_sha256': PHYSICAL_SHA,
        'original_lights': original_lights, 'original_cycles_world_branch_sha256': inherited_world_branch,
        'physical_world_graph': physical_graph, 'restore_spec': restore,
        'cycles_glass_hash': original_cycles, 'glazing_geometry_hash': original_geometry,
        'fast_gi_profile_preserved': current_ao, 'raytracing': s.eevee.use_raytracing,
        'camera_world_strength': .36, 'noncamera_world_strength': .006,
        'light_path_socket': 'Is Camera Ray', 'light_path_socket_exists_and_linked': camera_path.outputs['Is Camera Ray'].is_linked,
        'scope': 'PREVIEW_APPROXIMATION, combined World routing and one AREA candidate, not a single-variable attribution.',
        'area': {'name': light.name, 'location': list(light.location), 'direction': list(direction),
            'local_x_axis': list(light.matrix_world.to_3x3() @ Vector((1,0,0))),
            'local_y_axis': list(light.matrix_world.to_3x3() @ Vector((0,1,0))),
            'shape': data.shape, 'size_m': [.75, 1.6], 'energy_W': data.energy, 'normalize': data.normalize,
            'color_linear_rgb': list(data.color), 'use_shadow': data.use_shadow, 'placement_rays': rays},
        'frame': 48, 'camera': s.camera.name, 'camera_location': list(s.camera.location),
        'camera_rotation': list(s.camera.rotation_euler), 'lens': s.camera.data.lens,
        'resolution': [960,540], 'samples': 32, 'exposure': 2.4, 'view_transform': s.view_settings.view_transform,
        'look': s.view_settings.look, 'gamma': s.view_settings.gamma, 'threads': 4,
        'render_count': 1, 'bake_count': 0, 'production_changed': False, 'production_renderer_restore_integrated': False,
        'original_objects_and_lights_unchanged': True,
        'helper_hashes': {p: sha(ROOT/'scripts'/p) for p in ('eevee_preview.py','eevee_glass.py')}}
    REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
    png = OUT / 'CAM_MAIN_L3_STUDY_B_EV2p4.png'
    s.render.filepath = str(png)
    print('WINDOW08_RENDER_START ' + json.dumps(report['area']), flush=True)
    start = time.perf_counter()
    bpy.ops.render.render(write_still=True)
    report['render_seconds'] = time.perf_counter() - start
    report['png'] = str(png)
    report['png_sha256'] = sha(png)
    report['same_linear_exposure_exports'] = []
    for ev in (1.6, 3.2):
        s.view_settings.exposure = ev
        export = OUT / ('CAM_MAIN_L3_STUDY_B_EV' + str(ev).replace('.', 'p') + '.png')
        bpy.data.images['Render Result'].save_render(str(export), scene=s)
        report['same_linear_exposure_exports'].append({'exposure': ev, 'path': str(export), 'sha256': sha(export), 'same_linear_render': True})
    s.view_settings.exposure = 2.4
    assert {p: sha(ROOT/'scripts'/p) for p in report['helper_hashes']} == report['helper_hashes']
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    report.update(status='RENDERED_SAVED', visual_acceptance='NOT_REVIEWED', candidate_blend=str(BLEND),
        candidate_sha256=sha(BLEND), source_unchanged=sha(SOURCE)==SOURCE_SHA, physical_source_unchanged=sha(PHYSICAL)==PHYSICAL_SHA)
    REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('WINDOW08_COMPLETE ' + json.dumps({k: report[k] for k in ('render_seconds','png_sha256','candidate_sha256')}), flush=True)

if __name__ == '__main__':
    if '--restore-check' in sys.argv:
        restore_check()
    else:
        build()
