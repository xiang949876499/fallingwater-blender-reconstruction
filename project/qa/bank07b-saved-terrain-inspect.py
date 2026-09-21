"""Read-only actual frozen07c terrain profiles and active ground material."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'scene/Fallingwater_geology_candidate07c.blend'
sha=hashlib.sha256(path.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(path))
bpy.context.scene.frame_set(48)
obj=bpy.data.objects['SITE_Continuous_BearRun_Terrain']
bvh=BVHTree.FromObject(obj,bpy.context.evaluated_depsgraph_get())
formula=json.loads((ROOT/'qa/bank07b-terrain-cause-probe.json').read_text(encoding='utf8'))
profiles={}
for name,points in formula['profiles'].items():
    rows=[]
    for p in points:
        x,y=p['xy'];hit,n,i,d=bvh.ray_cast(Vector((x,y,50)),Vector((0,0,-1)),100)
        rows.append({'xy':p['xy'],'actual_z':hit.z if hit else None,'normal':list(n) if n else None,'current_formula_minus_saved':p['final']-hit.z if hit else None,'current_mesh_formula_minus_saved':p['mesh_z']-hit.z if hit else None})
    profiles[name]=rows
mat=obj.data.materials[0]
nodes=[]
for node in mat.node_tree.nodes:
    r={'name':node.name,'type':node.bl_idname,'inputs':{}}
    for s in node.inputs:
        if hasattr(s,'default_value'):
            v=s.default_value
            try:r['inputs'][s.name]=float(v) if isinstance(v,(int,float,bool)) else str(v) if isinstance(v,str) else list(v)
            except (TypeError,ValueError):pass
    if getattr(node,'image',None):r.update(image=node.image.name,path=node.image.filepath,packed=bool(node.image.packed_file),projection=node.projection)
    nodes.append(r)
out={'status':'READ_ONLY_ACTUAL_SAVED_TERRAIN','source_sha256':sha,'terrain_vertices':len(obj.data.vertices),'terrain_faces':len(obj.data.polygons),'smooth_faces':sum(p.use_smooth for p in obj.data.polygons),'material':mat.name,'profiles':profiles,'nodes':nodes,'links':[[l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name] for l in mat.node_tree.links]}
(ROOT/'qa/bank07b-saved-terrain-inspect.json').write_text(json.dumps(out,indent=2),encoding='utf8')
assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
for name,points in profiles.items():
    print(name,'saved heights:',[(p['xy'],round(p['actual_z'],3)) for p in points[::2]])
print('SOURCE_UNCHANGED',sha,flush=True)
