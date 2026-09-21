"""CPU-only offline read of authored tree library and isolated CC0 fern candidate."""
import bpy
import hashlib
import json
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parents[1]
qa = root / 'qa'
bpy.context.scene.render.threads_mode = 'FIXED'
bpy.context.scene.render.threads = 4

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def mesh_stats(mesh):
    mesh.calc_loop_triangles()
    result = {'name': mesh.name, 'vertices': len(mesh.vertices), 'edges': len(mesh.edges),
            'polygons': len(mesh.polygons), 'triangles': len(mesh.loop_triangles),
            'uv_layers': [u.name for u in mesh.uv_layers],
            'materials': [m.name if m else None for m in mesh.materials],
            'bounds_local': [[min(v.co[i] for v in mesh.vertices), max(v.co[i] for v in mesh.vertices)] for i in range(3)] if mesh.vertices else None}
    if 'Individual_Leaves' in mesh.name and len(mesh.vertices) % 7 == 0:
        lengths = [(mesh.vertices[i+3].co-mesh.vertices[i].co).length for i in range(0, len(mesh.vertices), 7)]
        widths = [(mesh.vertices[i+5].co-mesh.vertices[i+1].co).length for i in range(0, len(mesh.vertices), 7)]
        ratios = [w/l for w, l in zip(widths, lengths)]
        result['leaf_measurement_method'] = 'Stored seven-vertex leaf construction: vertices 0-3 blade length; 1-5 shoulder width.'
        result['leaf_count'] = len(lengths)
        result['leaf_length_m_min_mean_max'] = [min(lengths), sum(lengths)/len(lengths), max(lengths)]
        result['leaf_width_m_min_mean_max'] = [min(widths), sum(widths)/len(widths), max(widths)]
        result['leaf_width_length_ratio_min_mean_max'] = [min(ratios), sum(ratios)/len(ratios), max(ratios)]
    return result

library = root / 'assets/models/site_near_trees.blend'
with bpy.data.libraries.load(str(library), link=False) as (src, dst):
    dst.meshes = [n for n in src.meshes if n.startswith('TREE_Asset_')]
authored = [mesh_stats(m) for m in dst.meshes if m]
cfg = json.loads((root / 'data/site.json').read_text())
trees = cfg.get('preserved_vegetation', [])
authored_report = {'source': str(library.relative_to(root)), 'sha256': digest(library),
                  'size_bytes': library.stat().st_size, 'meshes': authored,
                  'preserved_instances': len(trees), 'asset_use_counts': dict(Counter(t['asset'] for t in trees)),
                  'forest_config': cfg['forest'], 'landmark_positions': [t for t in trees if 'Landmark' in t['name']]}

candidate = root / 'assets/candidates/fern_02_2k/fern_02_2k.blend'
bpy.ops.wm.open_mainfile(filepath=str(candidate), load_ui=False, use_scripts=False)
bpy.context.scene.render.threads_mode = 'FIXED'
bpy.context.scene.render.threads = 4
meshes = [mesh_stats(m) for m in bpy.data.meshes]
objects = []
for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    objects.append({'name': obj.name, 'data': obj.data.name, 'dimensions': list(obj.dimensions),
                    'location': list(obj.location), 'scale': list(obj.scale),
                    'modifiers': [{'name': m.name, 'type': m.type, 'show_viewport': m.show_viewport,
                                   'show_render': m.show_render} for m in obj.modifiers],
                    'hide_render': obj.hide_render})
images = []
for img in bpy.data.images:
    p = Path(bpy.path.abspath(img.filepath))
    images.append({'name': img.name, 'filepath': str(p), 'exists': p.exists(),
                   'packed': bool(img.packed_file), 'size': list(img.size), 'channels': img.channels,
                   'depth': img.depth, 'is_float': img.is_float, 'colorspace': img.colorspace_settings.name})
materials = []
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    materials.append({'name': mat.name, 'nodes': [{'name': n.name, 'type': n.type,
                        'image': n.image.name if n.type == 'TEX_IMAGE' and n.image else None} for n in mat.node_tree.nodes],
                      'links': [{'from_node': l.from_node.name, 'from_socket': l.from_socket.name,
                                 'to_node': l.to_node.name, 'to_socket': l.to_socket.name} for l in mat.node_tree.links]})
report = {'status': 'OFFLINE_READ_PASS_NOT_VISUAL_ACCEPTANCE', 'blender': bpy.app.version_string,
          'threads': 4, 'rendered': False, 'baked': False, 'source_sha256': digest(candidate),
          'source_bytes': candidate.stat().st_size, 'unit_scale': bpy.context.scene.unit_settings.scale_length,
          'meshes': meshes, 'objects': objects, 'images': images, 'materials': materials,
          'total_unique_mesh_triangles': sum(m['triangles'] for m in meshes),
          'total_unique_vertices': sum(m['vertices'] for m in meshes),
          'native_lod_groups': [c.name for c in bpy.data.collections if 'lod' in c.name.lower()],
          'text_blocks': [t.name for t in bpy.data.texts], 'authored_baseline': authored_report}
(qa / 'near-tree-asset07-offline-audit.json').write_text(json.dumps(report, indent=2))
print(json.dumps({'candidate_triangles': report['total_unique_mesh_triangles'], 'objects': objects,
                  'images': images, 'authored_mesh_count': len(authored),
                  'authored_mesh_triangles': sum(m['triangles'] for m in authored)}, indent=2))
