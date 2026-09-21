"""Read-only frame48 baseline equivalence and evaluated rock material/normal audit."""
import bpy, json, hashlib, struct
from pathlib import Path
from collections import Counter
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]

def sha(value):return hashlib.sha256(value).hexdigest()
def serial(value):
    if isinstance(value,(str,int,float,bool)) or value is None:return value
    try:return list(value)
    except TypeError:return str(value)
def material(m):
    if not m:return None
    out={'name':m.name,'diffuse':list(m.diffuse_color),'use_nodes':m.use_nodes}
    if m.use_nodes:
        out['nodes']=[{'name':n.name,'type':n.bl_idname,
                       'inputs':[(x.name,serial(x.default_value)) for x in n.inputs if hasattr(x,'default_value')],
                       'image':n.image.name if getattr(n,'image',None) else None,
                       'image_packed_sha256':sha(n.image.packed_file.data) if getattr(n,'image',None) and n.image.packed_file else None,
                       'projection':getattr(n,'projection',None)} for n in m.node_tree.nodes]
        out['links']=sorted((x.from_node.name,x.from_socket.name,x.to_node.name,x.to_socket.name) for x in m.node_tree.links)
    return out
def mesh_hash(m):
    h=hashlib.sha256()
    for v in m.vertices:h.update(struct.pack('<3f',*v.co))
    for p in m.polygons:
        h.update(struct.pack('<III',len(p.vertices),p.material_index,int(p.use_smooth)))
        for j in p.vertices:h.update(struct.pack('<I',j))
    if m.shape_keys:
        for key in m.shape_keys.key_blocks:
            h.update(key.name.encode())
            for v in key.data:h.update(struct.pack('<3f',*v.co))
    return h.hexdigest()
def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene;scene.frame_set(48);bpy.context.view_layer.update()
    meshes={m.name:mesh_hash(m) for m in bpy.data.meshes if m.users}
    mats={m.name:sha(json.dumps(material(m),sort_keys=True).encode()) for m in bpy.data.materials if m.users}
    out={}
    for o in scene.objects:
        d={'type':o.type,'matrix':[list(row) for row in o.matrix_world],'hide_render':o.hide_render,
           'hide_viewport':o.hide_viewport,'collections':sorted(c.name for c in o.users_collection)}
        if o.type=='MESH':d.update(mesh=meshes[o.data.name],mats=[mats[m.name] if m else None for m in o.data.materials])
        if o.type=='CAMERA':d['camera']={k:getattr(o.data,k) for k in ('lens','shift_x','shift_y','clip_start','clip_end','sensor_width','sensor_height','type')}
        if o.type=='LIGHT':d['light']={'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color)}
        out[o.name]=d
    return out

old_path=ROOT/'scene/Fallingwater_geology_baseline06_no_water.blend'
new_path=ROOT/'scene/Fallingwater_geology_baseline06b_frame48_no_water.blend'
old=snapshot(old_path);new=snapshot(new_path)
changes=[k for k in sorted(set(old)|set(new)) if old.get(k)!=new.get(k)]
baseline={'status':'PASS_FRAME48_RENDER_TARGET_EQUIVALENT' if not changes else 'FAIL',
          'old_file_sha256':sha(old_path.read_bytes()),'new_file_sha256':sha(new_path.read_bytes()),
          'object_count_old':len(old),'object_count_new':len(new),'changed_objects':changes,
          'scope':'Frame48 object transforms/visibility, mesh vertices/faces/material indices/smooth flags/shape keys, full material nodes/socket defaults/links/packed image bytes, lights and camera projection properties. No save or render.'}
path=ROOT/'scene/Fallingwater_geology_candidate07b.blend'
bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.scene.frame_set(48);bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get();cfg=json.loads((ROOT/'data/site.json').read_text(encoding='utf-8'))
lip=Vector(cfg['river_path'][8][:2]);down=(Vector(cfg['river_path'][9][:2])-lip).normalized()
front=Vector((down.x,down.y,0));records=[]
for name in ['SITE_Core_Continuous_Fractured_Sandstone','SITE_Cascade_Shoulder_Continuous_0','SITE_Cascade_Shoulder_Continuous_1']:
    ob=bpy.data.objects[name];ev=ob.evaluated_get(deps);mesh=ev.to_mesh()
    counts=Counter(p.material_index for p in mesh.polygons)
    visible=[p for p in mesh.polygons if p.normal.dot(front)>.35 and p.normal.z<.85]
    records.append({'object':name,'slots':[m.name if m else None for m in mesh.materials],
                    'actual_polygon_material_index_counts':dict(counts),'front_surface_polygons':len(visible),
                    'front_surface_material_index_counts':dict(Counter(p.material_index for p in visible)),
                    'front_surface_dot_flow_range':[min(p.normal.dot(front) for p in visible),max(p.normal.dot(front) for p in visible)] if visible else None,
                    'front_sample_normals':[list(p.normal) for p in visible[::max(1,len(visible)//8)][:8]],
                    'evaluated_polygons':len(mesh.polygons),'flat_polygons':sum(not p.use_smooth for p in mesh.polygons),
                    'materials':[material(m) for m in mesh.materials]})
    ev.to_mesh_clear()
report={'baseline_equivalence':baseline,'candidate_scene_sha256':sha(path.read_bytes()),'evaluated_rock':records}
(ROOT/'qa/geology-baseline-material-inspect07c.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'baseline':baseline,'slots':[{'object':r['object'],'slots':r['slots'],'material_counts':r['actual_polygon_material_index_counts'],'front_material_counts':r['front_surface_material_index_counts'],'front_normals':r['front_sample_normals']} for r in records]},indent=2),flush=True)
assert not changes,'Baselines differ; inspect report before reusing old renders'
