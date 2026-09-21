"""Display-only full-context copy of existing native diagnostic, never bake/render/install."""
import sys,json,hashlib,math,importlib.util
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'qa';spec=importlib.util.spec_from_file_location('impact09',P/'water09-impact36.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
BASE=ROOT/'scene/Fallingwater_water_hybrid07_motion36.blend';BASE_SHA='3c7638bd5866f48eca88a2c184cc958cae3bdfb578892e7e58a59e9c967f55d7'
OUT=ROOT/'scene/Fallingwater_water09_impact36_display.blend';assert not OUT.exists();assert w.sha(BASE)==BASE_SHA
r=json.loads(w.REPORT.read_text(encoding='utf-8'));assert w.sha(w.PILOT)==r['baked_sha256'];manifest=w.manifest()
bpy.ops.wm.open_mainfile(filepath=str(BASE));s=bpy.context.scene;s.frame_set(1);hidden=[]
for obj in list(s.objects):
 water_material=obj.type=='MESH' and any(m and 'Water' in m.name for m in obj.data.materials)
 if obj.name.startswith(('WATER','HYBRID07_Impact','HYBRID07_Foam','HYBRID07_Spray')) or water_material or any(m.type=='FLUID' for m in obj.modifiers):
  obj.hide_render=True;hidden.append(obj.name)
with bpy.data.libraries.load(str(w.PILOT),link=False) as (src,dst):dst.objects=[w.DOMAIN]
domain=dst.objects[0];s.collection.objects.link(domain);domain.name='WATER09_Native_Impact36_DIAGNOSTIC';domain.hide_render=False;domain.hide_set(False)
d=next(m.domain_settings for m in domain.modifiers if m.type=='FLUID');assert Path(bpy.path.abspath(d.cache_directory)).resolve()==w.CACHE.resolve()
# Collection dependencies are physics-only. The frozen full scene already displays its actual rock surfaces.
for group in (d.fluid_group,d.effector_group):
 for obj in group.objects:obj.hide_render=True
cam=s.objects.get('CAM_WATER_FOOT')
assert cam is not None,'Existing actually rendered foot camera must be present'
s.camera=cam;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=24;s.render.threads_mode='FIXED';s.render.threads=8;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1;s.frame_end=36;s.view_settings.exposure=.8
water=domain.data.materials[0];foam=bpy.data.materials.new('WATER09_Display_Individual_Bubble_C');foam.use_nodes=True;bs=foam.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.72,.78,.74,1);bs.inputs['Roughness'].default_value=.22;bs.inputs['Transmission Weight'].default_value=.25;bs.inputs['IOR'].default_value=1.333
protos={}
for kind,material,radius in [('FOAM',foam,.0015),('SPRAY',water,.0025)]:
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(0,0,-1000));proto=bpy.context.object;proto.name='WATER09_Display_'+kind+'_UnitSphere';proto.data.materials.append(material)
 for face in proto.data.polygons:face.use_smooth=True
 protos[kind]={'object':proto,'radius_m':radius}
settings=[]
for ps in domain.particle_systems:
 if ps.settings.type=='FLIP':ps.settings.render_type='NONE'
 elif ps.settings.type in protos:
  pp=protos[ps.settings.type];ps.settings.render_type='OBJECT';ps.settings.instance_object=pp['object'];ps.settings.particle_size=pp['radius_m'];ps.settings.size_random=.35
 settings.append({'type':ps.settings.type,'render_type':ps.settings.render_type,'particle_size':ps.settings.particle_size,'size_random':ps.settings.size_random,'instance':ps.settings.instance_object.name if ps.settings.instance_object else None})
s.frame_set(1);s['water09_display_status']='RAW_NATIVE_DIAGNOSTIC_PHYSICS_FLOW_RATE_FAIL_NO_OUTER_JOIN';s['water09_display_scope']='Frozen07 full context, all old river/water hidden. Native pool only; no exterior water join. C sphere instancing sizes, actual cached particle positions.'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));assert w.sha(BASE)==BASE_SHA and w.sha(w.PILOT)==r['baked_sha256'];assert w.manifest()==manifest
report={'status':'DISPLAY_ONLY_READY_NOT_RENDERED_FLOW_RATE_FAIL','output':str(OUT),'output_sha256':w.sha(OUT),'full_context_source':str(BASE),'full_context_source_sha256':BASE_SHA,'native_source':str(w.PILOT),'native_source_sha256':r['baked_sha256'],'camera':{'name':cam.name,'matrix_world':[list(row) for row in cam.matrix_world],'lens_mm':cam.data.lens,'source':'Existing root-rendered CAM_WATER_FOOT in hybrid07_motion36; unchanged'},'frame_range':[1,36],'requested_review_frames':[1,18,36],'render_suggestion':{'resolution':[960,540],'samples':24,'engine':'CYCLES','device':'CPU','threads':8,'exposure':.8},'hidden_previous_water_or_sim_objects':hidden,'native_domain':domain.name,'display_particle_settings':settings,'display_particle_geometry':'C millimeter sphere instances at actual cachedFOAM/SPRAY positions; no flat foam disc, no hidden-gap surface','old_cache_hashes_unchanged':True,'candidate_and_base_hashes_unchanged':True,'outer_water_join':'NOT_ATTEMPTED_ALL_OLD_WATER_HIDDEN','bakes':0,'renders':0,'production_install':False,'frozen07_context_not_current_architecture_delivery':True}
(P/'water09-impact36-display.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('WATER09_DISPLAY_READY',json.dumps({k:report[k] for k in ['status','output','output_sha256','camera','native_domain']}),flush=True)
