"""One unsaved stone shading-normal ablation, preserving the existing GI cache."""
import ast,hashlib,itertools,json,sys,time
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import eevee_glass
SOURCE=ROOT/'qa/eevee-iteration06-practical/Fallingwater_main_l3_coverage_candidate.blend'
EXPECTED='cee741ac1c25c84f487c4967158a4c29bb3552871102338442f9b9fc85488ebf'
PNG=ROOT/'qa/eevee-iteration06-stone-normal-zero.png';REPORT=PNG.with_suffix('.json')
tree=ast.parse((ROOT/'qa/eevee-iteration06-coverage.py').read_text(encoding='utf-8'))
names={'sha','properties','light_state','probe_state','object_state'}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'inspection_helpers','exec'))

def socket_value(socket):
    if not hasattr(socket,'default_value'):return None
    value=socket.default_value
    if isinstance(value,(str,int,float,bool)) or value is None:return value
    if hasattr(value,'name'):return {'data_block':value.name}
    try:return list(value)
    except TypeError:return str(value)

def material_state(material):
    result={'diffuse_color':list(material.diffuse_color),'use_nodes':material.use_nodes}
    if not material.use_nodes:return result
    result['nodes']={n.name:{'type':n.bl_idname,'inputs':[(s.identifier,socket_value(s)) for s in n.inputs],
        'outputs':[(s.identifier,socket_value(s)) for s in n.outputs],
        'image':n.image.name if hasattr(n,'image') and n.image else None,
        'target':getattr(n,'target',None),'projection':getattr(n,'projection',None),
        'invert':getattr(n,'invert',None),'mute':n.mute}
        for n in material.node_tree.nodes}
    result['links']=sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier)
        for l in material.node_tree.links)
    return result

def materials_state():return {m.name:material_state(m) for m in bpy.data.materials}
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()

assert sha(SOURCE)==EXPECTED and not PNG.exists(),'Preserve source and existing evidence'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s=bpy.context.scene;s.frame_set(1)
assert s.render.engine=='BLENDER_EEVEE' and s.eevee.use_raytracing and not s.eevee.use_fast_gi
s.camera=s.objects['CAM_MAIN_L3_STUDY_B'];s.view_settings.exposure=2.4
s.eevee.taa_render_samples=32;s.render.threads_mode='FIXED';s.render.threads=4
s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage=960,540,100
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
bpy.context.view_layer.update()
before_lights=light_state(s);before_probes=probe_state(s);before_objects=object_state(s);before_mats=materials_state()
before_glass=eevee_glass.cycles_signature();before_glazing=eevee_glass.geometry_signature(s)
stone=bpy.data.materials['FW_stone'];nodes=stone.node_tree.nodes;links=stone.node_tree.links
outputs=[n for n in nodes if n.bl_idname=='ShaderNodeOutputMaterial' and n.is_active_output and n.target in {'ALL','EEVEE'}]
assert outputs,'Missing active EEVEE stone output'
reachable=set(outputs);pending=list(outputs)
while pending:
    node=pending.pop()
    for link in links:
        if link.to_node==node and link.from_node not in reachable:
            reachable.add(link.from_node);pending.append(link.from_node)
bumps=[n for n in reachable if n.bl_idname=='ShaderNodeBump' and n.outputs['Normal'].is_linked
    and abs(n.inputs['Strength'].default_value-.5)<1e-6 and abs(n.inputs['Distance'].default_value-.022)<1e-6]
assert len(bumps)==1,[{'name':n.name,'strength':n.inputs['Strength'].default_value,'distance':n.inputs['Distance'].default_value} for n in reachable if n.bl_idname=='ShaderNodeBump']
bump=bumps[0];assert not bump.inputs['Strength'].is_linked
linked_before=[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in links if l.to_node==bump or l.from_node==bump]
bump.inputs['Strength'].default_value=0.0
after_mats=materials_state()
changed=[name for name,value in before_mats.items() if after_mats[name]!=value]
assert changed==['FW_stone'],changed
expected=json.loads(json.dumps(before_mats['FW_stone']))
# Normalize tuple records through JSON before asserting exactly one input change.
after=json.loads(json.dumps(after_mats['FW_stone']))
for item in expected['nodes'][bump.name]['inputs']:
    if item[0]==bump.inputs['Strength'].identifier:item[1]=0.0
assert expected==after,'Stone graph changed beyond the single Strength input'
assert light_state(s)==before_lights and probe_state(s)==before_probes and object_state(s)==before_objects
assert eevee_glass.cycles_signature()==before_glass and eevee_glass.geometry_signature(s)==before_glazing
report={'status':'RUNNING','source_sha256':EXPECTED,'source':str(SOURCE),
    'camera':s.camera.name,'camera_location':list(s.camera.location),'camera_rotation':list(s.camera.rotation_euler),
    'lens':s.camera.data.lens,'frame':1,'exposure':2.4,'resolution':[960,540],'samples':32,'cpu_preparation_threads':4,
    'raytracing':True,'fast_gi':False,'material':'FW_stone','node':bump.name,
    'only_change':{'input':'Strength','before':.5,'after':0.0},'distance_unchanged':bump.inputs['Distance'].default_value,
    'relevant_links':linked_before,'before_stone_graph':before_mats['FW_stone'],
    'before_all_material_graph_hashes':{k:digest(v) for k,v in before_mats.items()},
    'after_all_material_graph_hashes':{k:digest(v) for k,v in after_mats.items()},
    'changed_materials':changed,'lights_and_links_unchanged':True,'all_probe_settings_and_transforms_unchanged':True,
    'all_object_transforms_and_render_visibility_unchanged':True,'cycles_glass_signature':before_glass,
    'glazing_geometry_signature':before_glazing,'gi_rebaked':False,'production_saved':False,
    'scope':'Unsaved shading-normal ablation only. Existing captured GI retained; not a capture-normal experiment. Stone surface edit is engine-independent in memory; original source and physical Cycles files not changed.'}
REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
s.render.filepath=str(PNG);print('STONE_NORMAL_ZERO_START '+bump.name,flush=True)
start=time.perf_counter();bpy.ops.render.render(write_still=True)
report.update(status='RENDERED',render_seconds=time.perf_counter()-start,png=str(PNG),png_sha256=sha(PNG),visual_acceptance='NOT_REVIEWED')
assert sha(SOURCE)==EXPECTED;report['source_unchanged']=True
REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('STONE_NORMAL_ZERO_COMPLETE '+json.dumps({k:report[k] for k in ['render_seconds','png_sha256']}),flush=True)
