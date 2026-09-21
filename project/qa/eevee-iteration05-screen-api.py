"""Installed RNA definitions for independent screen-ray/Fast-GI controls."""
import json
from pathlib import Path
import bpy
e=bpy.context.scene.eevee
result={}
for name in ['use_raytracing','use_fast_gi','fast_gi_method','fast_gi_distance','fast_gi_thickness_near','fast_gi_bias']:
    p=e.bl_rna.properties[name]
    result[name]={'value':str(getattr(e,name)),'name':p.name,'description':p.description,
        'enum':[{'identifier':x.identifier,'description':x.description} for x in p.enum_items] if p.type=='ENUM' else []}
for name in ['trace_max_roughness','screen_trace_quality','screen_trace_thickness']:
    p=e.ray_tracing_options.bl_rna.properties[name]
    result['ray_tracing_options.'+name]={'value':str(getattr(e.ray_tracing_options,name)),
        'name':p.name,'description':p.description}
path=Path(__file__).with_suffix('.json')
path.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result),flush=True)
