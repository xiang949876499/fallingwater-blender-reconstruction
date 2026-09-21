"""Frozen09 context + existing native48 cache only. Never simulate or render."""
import sys,json,math,importlib.util
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
spec=importlib.util.spec_from_file_location('natural48',Path(__file__).with_name('water10-natural48.py'))
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
P=w.P;r=json.loads(w.REPORT.read_text(encoding='utf8'));BASE=w.SOURCE;NATIVE=Path(r['baked_scene'])
OUT=w.ROOT/'scene/Fallingwater_water10_native48_display.blend';assert not OUT.exists()
assert w.sha(BASE)==w.CONFIG['source_sha256'] and w.sha(NATIVE)==r['baked_scene_sha256']
before=[{'path':str(p.relative_to(w.CACHE)),'bytes':p.stat().st_size,'sha256':w.sha(p)} for p in sorted(w.CACHE.rglob('*')) if p.is_file()]
assert len(before)==192
bpy.ops.wm.open_mainfile(filepath=str(BASE));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.frame_set(1)
oldwater=s.objects['WATER_BearRun_Continuous_Upstream_Downstream'];water=oldwater.data.materials[0]
hidden=[]
for ob in s.objects:
    watermat=ob.type=='MESH' and any(m and ('Water' in m.name or 'water' in m.name or 'Foam' in m.name) for m in ob.data.materials)
    if ob.name.startswith(('WATER','HYBRID07_Impact','HYBRID07_Foam','HYBRID07_Spray','SITE_Remote_Upstream_Creek_Continuation')) or watermat or any(m.type=='FLUID' for m in ob.modifiers):
        hidden.append({'name':ob.name,'hide_render_before':ob.hide_render,'hide_render_after':True});ob.hide_render=True
core=s.objects['SITE_Core_Continuous_Fractured_Sandstone'];assert w.h.shape_hash(core)==w.CONFIG['frozen_core_sha256']
with bpy.data.libraries.load(str(NATIVE),link=False) as (src,dst):dst.objects=[w.DOMAIN]
domain=dst.objects[0];s.collection.objects.link(domain)
domain.hide_render=False;domain.hide_set(False)
d=next(m.domain_settings for m in domain.modifiers if m.type=='FLUID')
assert Path(bpy.path.abspath(d.cache_directory)).resolve()==w.CACHE.resolve()
physical=[]
for group in (d.fluid_group,d.effector_group):
    # Linked collections must belong to the saved scene; merely importing an
    # object leaves its physics collection dependencies orphaned on save/reopen.
    if group.name not in s.collection.children:s.collection.children.link(group)
    for ob in group.objects:
        physical.append({'name':ob.name,'hide_render_before':ob.hide_render,'hide_render_after':True,
                         'hide_viewport_unchanged':ob.hide_viewport,'geometry_sha256':w.h.shape_hash(ob)})
        # Render visibility only. Do not set hide_viewport/use_inflow/use_effector.
        ob.hide_render=True
domain_material_before=[m.name if m else None for m in domain.data.materials]
domain.data.materials.clear();domain.data.materials.append(water)
for face in domain.data.polygons:face.use_smooth=True
foam=bpy.data.materials.new('WATER10_Display_Millimeter_Bubbles_C');foam.use_nodes=True;bs=foam.node_tree.nodes.get('Principled BSDF')
bs.inputs['Base Color'].default_value=(.72,.78,.74,1);bs.inputs['Roughness'].default_value=.22;bs.inputs['Transmission Weight'].default_value=.25;bs.inputs['IOR'].default_value=1.333
protos={}
for kind,mat,size in [('FOAM',foam,.0015),('SPRAY',water,.0025)]:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(0,0,-1000));proto=bpy.context.object;proto.name='WATER10_Display_'+kind+'_UnitSphere';proto.data.materials.append(mat)
    for p in proto.data.polygons:p.use_smooth=True
    protos[kind]=(proto,size)
particle_settings=[]
for ps in domain.particle_systems:
    before_setting={'type':ps.settings.type,'render_type':ps.settings.render_type,'size':ps.settings.particle_size}
    if ps.settings.type=='FLIP':ps.settings.render_type='NONE'
    elif ps.settings.type in protos:
        proto,size=protos[ps.settings.type];ps.settings.render_type='OBJECT';ps.settings.instance_object=proto;ps.settings.particle_size=size;ps.settings.size_random=.35
    particle_settings.append({'before':before_setting,'after':{'type':ps.settings.type,'render_type':ps.settings.render_type,'instance':ps.settings.instance_object.name if ps.settings.instance_object else None,'particle_size':ps.settings.particle_size,'random':ps.settings.size_random}})
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=32;s.render.threads_mode='FIXED';s.render.threads=8
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1;s.frame_end=48;s.view_settings.exposure=.8
def camera(name,pos,target,lens):
    me=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,me);s.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();me.lens=lens;me.clip_start=.03;me.clip_end=5000;return ob
target=Vector((-4,-5.5,-6.325));axis=Vector((-1,-1.4,1)).normalized();overview=camera('CAM_WATER10_NATIVE_OVERVIEW',target+axis*45,target,40)
corners=[Vector((x,y,z)) for x in [-16,8] for y in [-17,6] for z in [-7.7,-4.95]]
for distance in np.arange(45,80,1):
    overview.location=target+axis*float(distance);bpy.context.view_layer.update();uv=[world_to_camera_view(s,overview,p) for p in corners]
    if all(.04<p.x<.96 and .04<p.y<.96 and p.z>0 for p in uv):break
assert all(.04<p.x<.96 and .04<p.y<.96 and p.z>0 for p in uv)
foot=camera('CAM_WATER10_NATIVE_FOOT',(-5.8,-10.5,-2.2),(.4,-2.7,-5.6),46)
s.camera=overview;s.frame_set(1);s['water10_display_status']='NATIVE48_ONLY_DIAGNOSTIC_RAW_VOLUME_DRAIN_AND_FLOATING_SOURCE_JOIN_NOT_ACCEPTED'
s['water10_display_scope']='Frozen09 architecture/geology; all original procedural water hidden. Actual existing native48 cache. C millimeter foam/spray instances. X+ cuts geometric cavity; no outer join or production installation.'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
after=[{'path':str(p.relative_to(w.CACHE)),'bytes':p.stat().st_size,'sha256':w.sha(p)} for p in sorted(w.CACHE.rglob('*')) if p.is_file()]
assert before==after and w.sha(BASE)==w.CONFIG['source_sha256'] and w.sha(NATIVE)==r['baked_scene_sha256']
report={'status':'DISPLAY_ONLY_SAVED_REOPEN_REQUIRED_NOT_RENDERED','output':str(OUT),'output_sha256':w.sha(OUT),
 'full_context_source':str(BASE),'full_context_source_sha256':w.CONFIG['source_sha256'],'native_source':str(NATIVE),'native_source_sha256':r['baked_scene_sha256'],
 'native_domain':domain.name,'camera_primary':overview.name,'camera_optional_foot':foot.name,'suggested_frames':[1,24,48],
 'cameras':[{'name':c.name,'position':list(c.location),'matrix_world':[list(row) for row in c.matrix_world],'lens_mm':c.data.lens} for c in [overview,foot]],
 'overview_domain_corner_projection':[[p.x,p.y,p.z] for p in uv],'frustum_coverage_not_line_of_sight_pass':True,
 'hidden_original_water':hidden,'physics_group_render_visibility_only':physical,'domain_material_before':domain_material_before,'domain_material_after':water.name,
 'display_particle_changes':particle_settings,'display_geometry_changes':'Only C prototype spheres placed outside scene atZ-1000, cameras, and domain smooth shading/material; original simulation vertices/faces/cache unchanged.',
 'suggested_render':{'engine':'CYCLES','CPU_threads':8,'resolution':[1280,720],'samples':32,'exposure':.8,'persistent_data_recommended':True},
 'cache_hashes_unchanged':True,'source_scene_hashes_unchanged':True,'native_cache_manifest':before,
 'native_upstream_join':'NOT_ASSEMBLED_FLOATING_PARTIAL_FALL_INFLOW','procedural_outer_water_join':'NOT_ATTEMPTED_ALL_OLD_WATER_HIDDEN','renders':0,'bakes':0,'production_installed':False}
dump=P/'water10-native-display.json';dump.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('WATER10_NATIVE_DISPLAY_READY',str(OUT),report['output_sha256'],overview.name,foot.name,flush=True)
