"""Factory-only parameter audit; existing failed files are opened read-only.
No simulation, render, or scene save. Does not import any project modeling helper.
"""
import bpy,json,hashlib,math,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'scene/Fallingwater_water08_static_head24.blend'
OUT=ROOT/'qa/water09-default-audit.json'
assert bpy.app.background

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cube(name,lo,hi):
 pts=[(lo[0],lo[1],lo[2]),(hi[0],lo[1],lo[2]),(hi[0],hi[1],lo[2]),(lo[0],hi[1],lo[2]),
      (lo[0],lo[1],hi[2]),(hi[0],lo[1],hi[2]),(hi[0],hi[1],hi[2]),(lo[0],hi[1],hi[2])]
 me=bpy.data.meshes.new(name);me.from_pydata(pts,[],[(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]);me.update()
 o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);return o
def value(v):
 if isinstance(v,(str,bool,int,float)) or v is None:return v
 if isinstance(v,bpy.types.ID):return {'id_type':v.bl_rna.identifier,'name':v.name}
 if hasattr(v,'__len__') and hasattr(v,'__getitem__'):
  try:return [value(v[i]) for i in range(len(v))]
  except:pass
 return {'rna_type':getattr(getattr(v,'bl_rna',None),'identifier',type(v).__name__)}
def snapshot(settings):
 props={};meta={};skip=[]
 for p in settings.bl_rna.properties:
  k=p.identifier
  if k=='rna_type' or p.is_readonly or p.type=='COLLECTION':skip.append(k);continue
  try:
   props[k]=value(getattr(settings,k))
   meta[k]={'type':p.type,'description':p.description,'rna_default':value(p.default_array if getattr(p,'is_array',False) else getattr(p,'default',None))}
  except Exception as e:meta[k]={'error':repr(e)}
 readonly={k:value(getattr(settings,k)) for k in ['domain_resolution','start_point','cell_size'] if hasattr(settings,k)}
 weights=snapshot(settings.effector_weights) if hasattr(settings,'effector_weights') else None
 return {'properties':props,'metadata':meta,'readonly_small_diagnostics':readonly,'effector_weights':weights,'skipped_readonly_or_collections':skip}
def scene_info():
 s=bpy.context.scene
 return {'fps':s.render.fps,'fps_base':s.render.fps_base,'use_gravity':s.use_gravity,'gravity':list(s.gravity),'unit_scale_length':s.unit_settings.scale_length,'unit_system':s.unit_settings.system,'frame_range':[s.frame_start,s.frame_end]}
def object_info(o):
 pts=[o.matrix_world@v.co for v in o.data.vertices]
 return {'name':o.name,'location':list(o.location),'rotation_euler':list(o.rotation_euler),'scale':list(o.scale),'matrix_world':[list(x) for x in o.matrix_world],
  'basis_world_bounds':[[min(v[k] for v in pts),max(v[k] for v in pts)] for k in range(3)],'parent':o.parent.name if o.parent else None,'object_animation':bool(o.animation_data),'mesh_shape_keys':bool(o.data.shape_keys),
  'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'dimensions':list(o.dimensions),'modifiers':[{'name':m.name,'type':m.type,'show_viewport':m.show_viewport,'show_render':m.show_render} for m in o.modifiers]}
def diff(a,b):
 out=[]
 for k in sorted(set(a)|set(b)):
  if a.get(k)!=b.get(k):out.append({'property':k,'factory':a.get(k),'static24':b.get(k)})
 return out

# The command starts with --factory-startup. Reset only this isolated background memory.
bpy.ops.wm.read_factory_settings(use_empty=True)
domain=cube('WATER09_Factory_Cube_Domain',(-1,-1,-1),(1,1,1));m=domain.modifiers.new('Factory fluid domain','FLUID');m.fluid_type='DOMAIN';d=m.domain_settings;d.domain_type='LIQUID'
liquid=cube('WATER09_Factory_Geometry_Liquid',(-1,-1,-1),(1,1,0));m=liquid.modifiers.new('Factory geometry liquid','FLUID');m.fluid_type='FLOW';f=m.flow_settings;f.flow_type='LIQUID';f.flow_behavior='GEOMETRY'
bpy.context.view_layer.update()
factory={'scene':scene_info(),'domain':snapshot(d),'flow':snapshot(f),'objects':[object_info(domain),object_info(liquid)],
 'explicit_setup_only':['Create unit-scale closed2m cube DOMAIN','Set domain_type=LIQUID once','Create unit-scale lower-half cube FLOW','Set flow_type=LIQUID once','Set flow_behavior=GEOMETRY once'],
 'simulation_bake_render_save_run':False}
log=[]
def set_secondary_if_differs(attr,target):
 before=bool(getattr(d,attr));assigned=before!=target
 if assigned:setattr(d,attr,target)
 bpy.context.view_layer.update();after=bool(getattr(d,attr))
 types=[ps.settings.type for ps in domain.particle_systems]
 log.append({'property':attr,'before':before,'target':target,'assignment_executed':assigned,'after':after,'systems':types})
 assert after==target,('Non-idempotent secondary setter mismatch',log[-1])
for attr in ('use_foam_particles','use_spray_particles','use_bubble_particles'):
 set_secondary_if_differs(attr,False);set_secondary_if_differs(attr,False)
# Exercise false->true->true->false->false only in the unsaved factory process.
for attr in ('use_foam_particles','use_spray_particles','use_bubble_particles'):
 for target in (True,True,False,False):set_secondary_if_differs(attr,target)
factory['secondary_idempotent_setter_probe']=log
factory['final_secondary_flags']={k:bool(getattr(d,k)) for k in ('use_foam_particles','use_spray_particles','use_bubble_particles')}
factory['final_particle_systems']=[ps.settings.type for ps in domain.particle_systems]
# Outside cube exists briefly only to inspect default collision RNA; never a proposed simulation object.
eff=cube('WATER09_Default_Effector_RNA_Probe',(10,10,10),(11,11,11));m=eff.modifiers.new('Factory default effector','FLUID');m.fluid_type='EFFECTOR';factory['effector_default']=snapshot(m.effector_settings)
bpy.data.objects.remove(eff,do_unlink=True)
factory['remaining_object_names']=[o.name for o in bpy.context.scene.objects]

before=sha(OLD);bpy.ops.wm.open_mainfile(filepath=str(OLD));s=bpy.context.scene
domain=s.objects['WATER08_Static_Head_Control_Domain'];d=next(m.domain_settings for m in domain.modifiers if m.type=='FLUID')
liquid=s.objects['WATER08_Complete_Connected_Initial_Pool'];f=next(m.flow_settings for m in liquid.modifiers if m.type=='FLUID')
actual={'scene':scene_info(),'domain':snapshot(d),'flow':snapshot(f),'objects':[object_info(domain),object_info(liquid)],'effectors':[]}
for o in d.effector_group.objects:
 e=next(m.effector_settings for m in o.modifiers if m.type=='FLUID')
 actual['effectors'].append({'object':object_info(o),'settings':snapshot(e)})
comparison={'scene':diff(factory['scene'],actual['scene']),'domain':diff(factory['domain']['properties'],actual['domain']['properties']),
 'effector_weights':diff(factory['domain']['effector_weights']['properties'],actual['domain']['effector_weights']['properties']),
 'flow':diff(factory['flow']['properties'],actual['flow']['properties']),
 'effectors':[{'object':e['object']['name'],'differences':diff(factory['effector_default']['properties'],e['settings']['properties'])} for e in actual['effectors']]}
r={'status':'FACTORY_DEFAULT_COMPARISON_ONLY_NO_SIMULATION','blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'file':str(OLD),'file_sha256_before':before,'file_sha256_after':sha(OLD),
 'factory':factory,'static24':actual,'differences':comparison,'new_bakes':0,'renders':0,'scene_files_written':0,'production_or_failed_cache_modified':False}
assert r['file_sha256_before']==r['file_sha256_after']
OUT.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print('WATER09_DIFFERENCES',json.dumps(comparison),flush=True)
print('WATER09_FACTORY_KEY',json.dumps({k:factory['domain']['properties'].get(k) for k in ['use_adaptive_timesteps','use_fractions','particle_radius','delete_in_obstacle','simulation_method','flip_ratio','timesteps_min','timesteps_max','cfl_condition']}),flush=True)
print('WATER09_ACTUAL_KEY',json.dumps({k:actual['domain']['properties'].get(k) for k in ['use_adaptive_timesteps','use_fractions','particle_radius','delete_in_obstacle','simulation_method','flip_ratio','timesteps_min','timesteps_max','cfl_condition']}),flush=True)
