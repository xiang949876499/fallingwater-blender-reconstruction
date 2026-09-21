"""Read-only global material protection check against frozen09 and actual cabinet inputs."""
from pathlib import Path
import bpy,json,hashlib
R=Path(__file__).resolve().parents[1]
out=R/'qa/master-bath-detail10-independent-d-materials.json'
assert not out.exists()
def val(x):
    if isinstance(x,(str,int,float,bool)) or x is None:return x
    try:return [float(i) for i in x]
    except Exception:return str(x)
def snap():
    result={}
    for m in bpy.data.materials:
        nodes=[];links=[]
        if m.node_tree:
            for n in m.node_tree.nodes:
                row={'name':n.name,'type':n.bl_idname,'inputs':{s.identifier:val(s.default_value) for s in n.inputs if hasattr(s,'default_value')}}
                for key in ('operation','rotation_type','blend_type','projection','interpolation','extension','space','vector_type','distribution','subsurface_method'):
                    if hasattr(n,key):row[key]=val(getattr(n,key))
                for key in ('image','object'):
                    if hasattr(n,key):row[key]=getattr(n,key).name if getattr(n,key) else None
                nodes.append(row)
            links=sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links)
        result[m.name]={'diffuse_color':list(m.diffuse_color),'nodes':sorted(nodes,key=lambda n:n['name']),'links':links}
    return result
src=R/'scene/Fallingwater_iteration09.blend';d=R/'scene/Fallingwater_master_bath_candidate10d.blend'
bpy.ops.wm.open_mainfile(filepath=str(src));before=snap()
bpy.ops.wm.open_mainfile(filepath=str(d));bpy.context.scene.render.threads_mode='FIXED';bpy.context.scene.render.threads=4;after=snap()
changed=[k for k in before if k not in after or before[k]!=after[k]]
new=sorted(set(after)-set(before))
walnut=after['FW_MasterBath_Walnut10']
anchor=bpy.data.objects['MASTER_BATH10_cabinet_texture_anchor']
record={'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(d.read_bytes()).hexdigest(),
 'common_source_materials':len(before),'changed_or_missing_global_materials':changed,'new_materials':new,
 'cabinet_material':walnut,'cabinet_anchor_world_matrix':[list(r) for r in anchor.matrix_world],
 'cabinet_actual_slots':{o.name:[m.name if m else None for m in o.data.materials] for o in bpy.context.scene.objects if o.type=='MESH' and o.name in ('MASTER_BATH10_cabinet_case','MASTER_BATH10_cabinet_door_0','MASTER_BATH10_cabinet_door_1')},
 'status':'PASS' if not changed else 'FAIL','no_save_no_render':True}
out.write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({k:record[k] for k in ('status','common_source_materials','changed_or_missing_global_materials','new_materials')}))
